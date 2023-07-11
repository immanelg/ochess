from typing import Any

from starlette.requests import Request

from app.resources import templates


async def home(request: Request) -> Any:
    context = {"request": request, "user_id": request.cookies.get("user_id", "<unset>")}
    return templates.TemplateResponse("index.html", context)


async def lobby_view(request: Request) -> Any:
    context = {"request": request, "user_id": request.cookies.get("user_id", "<unset>")}
    return templates.TemplateResponse("lobby.html", context)


async def game_view(request: Request) -> Any:
    context = {
        "request": request,
        "user_id": request.cookies.get("user_id"),
        "game_id": request.path_params.get("game_id"),
    }
    return templates.TemplateResponse("game.html", context)
