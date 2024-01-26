from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app import environment
from app.database import service
from app.database.database import get_session



middleware: list[Middleware] = [
    Middleware(SessionMiddleware, secret_key=environment.SECRET_KEY),
]
