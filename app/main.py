from starlette.applications import Starlette

from app import environment
from app.lifespan import lifespan
from app.middleware import middleware
from app.routes import routes

app = Starlette(
    debug=environment.DEBUG,
    routes=routes,
    lifespan=lifespan,
    middleware=middleware,
)
