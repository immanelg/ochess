from starlette.applications import Starlette

from app.environment import settings
from app.lifespan import lifespan
from app.middleware import middleware
from app.routes import routes

app = Starlette(
    debug=settings.DEBUG,
    routes=routes,
    lifespan=lifespan,
    middleware=middleware,
)
