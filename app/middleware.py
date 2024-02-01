from starlette.middleware import Middleware

middleware: list[Middleware] = [
    # Middleware(SessionMiddleware, secret_key=settings.SECRET_KEY),
]
