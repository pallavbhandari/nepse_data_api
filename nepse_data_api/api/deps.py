"""Shared client management and error handling for the REST layer.

The underlying :class:`Nepse` client wraps a synchronous ``requests.Session``
and performs a network authentication call in its constructor. We therefore
build a single shared instance at application startup and serialise access to
it with a lock, since FastAPI dispatches synchronous path operations across a
thread pool.
"""

import threading
from typing import Any, Callable

import requests
from fastapi import HTTPException

from nepse_data_api.market import Nepse

# Module-level singleton, populated by the app lifespan handler.
_client: Nepse | None = None
_lock = threading.Lock()


def init_client(**kwargs: Any) -> Nepse:
    """Instantiate the shared Nepse client (called once on startup)."""
    global _client
    _client = Nepse(**kwargs)
    return _client


def get_client() -> Nepse:
    """Return the shared client, raising 503 if it failed to initialise."""
    if _client is None:
        raise HTTPException(
            status_code=503,
            detail="NEPSE client is not initialised (authentication failed).",
        )
    return _client


def call_nepse(method: str, *args: Any, **kwargs: Any) -> Any:
    """Invoke a Nepse method under the shared lock and normalise errors.

    Upstream NEPSE/network failures become 502s, missing methods become 500s,
    and everything else surfaces as a clean JSON error rather than a stack
    trace.
    """
    client = get_client()
    fn: Callable[..., Any] | None = getattr(client, method, None)
    if fn is None or not callable(fn):
        raise HTTPException(status_code=500, detail=f"Unknown operation: {method}")

    with _lock:
        try:
            return fn(*args, **kwargs)
        except HTTPException:
            raise
        except requests.HTTPError as exc:  # upstream returned a non-2xx
            status = getattr(exc.response, "status_code", 502)
            raise HTTPException(
                status_code=502,
                detail=f"NEPSE upstream error ({status}) for {method}.",
            ) from exc
        except requests.RequestException as exc:  # connection/timeout
            raise HTTPException(
                status_code=502,
                detail=f"Could not reach NEPSE upstream for {method}: {exc}",
            ) from exc
        except Exception as exc:  # noqa: BLE001 - last-resort guard
            raise HTTPException(
                status_code=500, detail=f"Error in {method}: {exc}"
            ) from exc
