from starlette.routing import Mount, Route, WebSocketRoute

from app import views
from app.resources import static
from app.websocket.endpoint import websocket_listener

routes = [
    Route("/", views.index),
    Route("/lobby", views.lobby),
    Route("/about", views.about),
    Route("/watch", views.watch),
    Route("/players", views.players),
    Route("/game/{game_id:int}", views.game),
    WebSocketRoute("/ws/game/{game_id:int}", websocket_listener),
    WebSocketRoute("/ws/lobby", websocket_listener),
    Mount("/static", static, name="static"),
]
