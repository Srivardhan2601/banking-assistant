import sys
from pathlib import Path

# Add project root to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.main import app as fastapi_app


class VercelPathFixMiddleware:
    """Restores the original client URL path from Vercel query params or headers."""
    def __init__(self, asgi_app):
        self.app = asgi_app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            query_string = scope.get("query_string", b"").decode("utf-8")
            path_restored = False

            if "path=" in query_string:
                for param in query_string.split("&"):
                    if param.startswith("path="):
                        val = param.split("=", 1)[1]
                        scope["path"] = f"/api/{val}" if not val.startswith("/") else val
                        path_restored = True
                        break

            if not path_restored:
                headers = dict(scope.get("headers", []))
                matched_header = (
                    headers.get(b"x-matched-path")
                    or headers.get(b"x-forwarded-uri")
                    or headers.get(b"x-vercel-matched-path")
                )
                if matched_header:
                    orig_path = matched_header.decode("utf-8").split("?")[0]
                    if orig_path and not orig_path.startswith("/api/index"):
                        scope["path"] = orig_path

        await self.app(scope, receive, send)


app = VercelPathFixMiddleware(fastapi_app)
