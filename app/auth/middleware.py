from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.auth.jwt import decode_token


# Routes that don't require a token
PUBLIC_ROUTES = ["/auth/login", "/auth/register", "/docs", "/openapi.json", "/products", ]

class JWTMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if any(request.url.path.startswith(route) for route in PUBLIC_ROUTES):
            return await call_next(request)

        token = request.headers.get("Authorization", "")
        if not token.startswith("Bearer "):
            return JSONResponse({"detail": "Missing token"}, status_code=401)

        payload = decode_token(token.split(" ")[1])
        if not payload:
            return JSONResponse({"detail": "Invalid or expired token"}, status_code=401)

        # Attach user id to request state for use in routes
        request.state.user_id = payload.get("sub")
        return await call_next(request)