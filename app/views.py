from typing import Any

from starlette.requests import Request

from app.resources import templates


async def home(request: Request) -> Any:
    context = {"request": request}
    return templates.TemplateResponse("index.html", context)
