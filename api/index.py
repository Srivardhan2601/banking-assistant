import sys
from pathlib import Path
from fastapi import FastAPI

# Add project root to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.main import app as main_app


class VercelFastAPIBridge(FastAPI):
    """FastAPI subclass that resolves Vercel dynamic rewrite path queries to exact FastAPI routes."""
    def __init__(self, target_app):
        super().__init__()
        self.target = target_app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            qs = scope.get("query_string", b"").decode("utf-8")
            if "path=" in qs:
                for part in qs.split("&"):
                    if part.startswith("path="):
                        val = part.split("=", 1)[1]
                        scope["path"] = f"/api/{val}" if not val.startswith("/") else val
                        break
        await self.target(scope, receive, send)


app = VercelFastAPIBridge(main_app)
del main_app
