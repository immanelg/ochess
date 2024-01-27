from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware

from app import environment

middleware: list[Middleware] = [
    Middleware(SessionMiddleware, secret_key=environment.SECRET_KEY),
]
