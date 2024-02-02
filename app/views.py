from typing import Any

from starlette.requests import Request
from starlette.responses import RedirectResponse

from app.resources import templates


async def index(_request: Request) -> Any:
    return RedirectResponse(url="/lobby")


async def lobby(request: Request) -> Any:
    context = {"request": request}
    return templates.TemplateResponse("lobby.html", context)


async def game(request: Request) -> Any:
    context = {"request": request, "gameid": request.path_params["game_id"]}
    return templates.TemplateResponse("game.html", context)


async def watch(request: Request) -> Any:
    context = {"request": request}
    return templates.TemplateResponse("watch.html", context)


async def players(request: Request) -> Any:
    context = {"request": request}
    return templates.TemplateResponse("players.html", context)


async def about(request: Request) -> Any:
    context = {"request": request}
    return templates.TemplateResponse("about.html", context)
