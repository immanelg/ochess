from broadcaster import Broadcast
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from app import config

templates = Jinja2Templates(directory=str(config.TEMPLATES_DIR))
static = StaticFiles(directory=str(config.STATIC_DIR))
broadcast = Broadcast("memory:///")
