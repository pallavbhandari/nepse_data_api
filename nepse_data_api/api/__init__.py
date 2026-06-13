"""REST interface for the nepse-data-api library.

Exposes the synchronous :class:`nepse_data_api.market.Nepse` client over HTTP
using FastAPI so it can be consumed from Postman, curl, or any HTTP client.

Run with::

    uvicorn nepse_data_api.api.app:app --reload --port 8000

Interactive docs are then available at ``/docs`` and the OpenAPI schema at
``/openapi.json`` (import that URL into Postman to scaffold a collection).
"""

from .app import app

__all__ = ["app"]
