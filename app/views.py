from typing import Any

from starlette.requests import Request

from app.resources import templates


async def home(request: Request) -> Any:
    context = {"request": request, "user_id": request.cookies.get("user_id", "<unset>")}
    return templates.TemplateResponse("index.html", context)
