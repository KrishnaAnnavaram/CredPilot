"""The CredPilot web application: the page, and the API mounted behind it.

The HTTP endpoints live in :mod:`src.api` — this module is what turns them into
something a browser can open. It creates the FastAPI application, includes the
API router, serves ``index.html`` and mounts the static assets.

``python -m src.web`` runs it.

The two were one module until the API was separated from the page it happens to
be served with. Nothing about the endpoints changed in the move; the names the
tests import are re-exported below so a caller that reached for them here still
finds them.
"""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from src.api.routes import (  # noqa: F401 - re-exported for callers and tests
    AssessRequest,
    ChatRequest,
    ResumeRequest,
    _state_from_packet,
    get_graph,
    router,
)

STATIC_DIR = Path(__file__).resolve().parent / "static"


def create_app() -> FastAPI:
    """The application: the API router, the page, and the static assets."""
    app = FastAPI(
        title="CredPilot",
        description=(
            "Loan origination and underwriting copilot. Mortgage and private "
            "education lending, kept strictly separate."
        ),
        version="1.0.0",
    )

    app.include_router(router)

    @app.get("/")
    def index() -> FileResponse:
        return FileResponse(STATIC_DIR / "index.html")

    if STATIC_DIR.exists():
        app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

    return app


app = create_app()


def main() -> int:
    """Run the development server."""
    import argparse

    import uvicorn

    parser = argparse.ArgumentParser(description="Run the CredPilot web application")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--reload", action="store_true")
    args = parser.parse_args()

    print(f"CredPilot  ->  http://{args.host}:{args.port}")
    uvicorn.run(
        "src.web.app:app" if args.reload else app,
        host=args.host, port=args.port, reload=args.reload,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
