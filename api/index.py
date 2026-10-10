import sys
from pathlib import Path

# Add project root to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.main import app as fastapi_app


class VercelPathFixMiddleware:
    """Restores the original client URL path from Vercel's x-matched-path header."""
    def __init__(self, asgi_app):
        self.app = asgi_app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            headers = dict(scope.get("headers", []))
            matched_path = headers.get(b"x-matched-path")
            if matched_path:
                orig_path = matched_path.decode("utf-8")
                orig_path = orig_path.split("?")[0]
                if orig_path and not orig_path.startswith("/api/index"):
                    scope["path"] = orig_path
        await self.app(scope, receive, send)


app = VercelPathFixMiddleware(fastapi_app)
