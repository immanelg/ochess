from starlette.routing import Mount, Route, WebSocketRoute

from app import views
from app.resources import static
from app.websocket import websocket

routes = [
    Route("/", views.home, name="home"),
    # Route("/lobby", views.lobby_view, name="lobby"),
    # Route("/game/{game_id:int}", views.game_view, name="game"),
    WebSocketRoute(
        "/ws/game/{game_id:int}", websocket.websocket_listener, name="ws_game"
    ),
    WebSocketRoute("/ws/lobby", websocket.websocket_listener, name="ws_lobby"),
    Mount("/static", static, name="static"),
]
