"""CredPilot's web application.

A FastAPI backend and a single static page. The CLI remains the reproducible
execution path and is unchanged; this is the same graph reached over HTTP, not a
second implementation of anything.

    python -m src.web            # http://127.0.0.1:8000
"""

from src.web.app import app, create_app

__all__ = ["app", "create_app"]
