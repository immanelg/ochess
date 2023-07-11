from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app import environment
from app.database import service
from app.database.database import get_session


class UserIdMiddleware(BaseHTTPMiddleware):
    # PLACEHOLDER for actual authentication
    # Just sets cookie with user id on response
    async def dispatch(self, request, call_next):
        user_id = request.cookies.get("user_id", None)
        response = await call_next(request)
        if user_id is None:
            async with get_session() as session:
                user = await service.UserRepository(session).create()
            response.set_cookie("user_id", str(user.id))

        return response


middleware: list[Middleware] = [
    Middleware(SessionMiddleware, secret_key=environment.SECRET_KEY),
    Middleware(UserIdMiddleware),
]
