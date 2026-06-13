"""FastAPI application exposing the NEPSE client over REST."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from nepse_data_api.version import __version__
from . import deps
from .routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Build the shared Nepse client once when the server starts."""
    try:
        deps.init_client()
    except Exception as exc:  # noqa: BLE001 - keep the server up, surface via /health
        # Leave the client unset; get_client() will return 503 until a
        # successful refresh. This avoids the whole server failing to boot
        # just because NEPSE was briefly unreachable at startup.
        print(f"[startup] NEPSE authentication failed: {exc}")
    yield


app = FastAPI(
    title="NEPSE Data API",
    description=(
        "REST interface over the nepse-data-api library for the Nepal Stock "
        "Exchange. Import /openapi.json into Postman to scaffold a collection."
    ),
    version=__version__,
    lifespan=lifespan,
)

app.include_router(router)


@app.get("/health", tags=["admin"])
def health() -> dict:
    """Liveness/readiness check. Reports whether the client authenticated."""
    return {"status": "ok", "authenticated": deps._client is not None}
