import m from "mithril";
import NavBar from "./Navbar";
import { Chessground } from "chessground";
import { WSClient } from "./client";

const dataset = document.getElementById("data")?.dataset;
const userId = parseInt(dataset.userId);

// TODO:
// restrict moves on board to only legal.
// check for game state for end of game.
// resign button and event.
// refactor this potentially huge function.

export default function Game() {
  let state = {
    game: {
      id: m.route.param("gameId"),
    },
    color: "white",
    /** @type {import("chessground/api").Api | null} */
    cg: null,
  };

  const client = new WSClient(`game/${state.game.id}`);

  window.state = state;
  window.client = client;

  client.onOpen = () => {
    client.sendMsg({
      action: "connect-to-game",
      data: {},
    });
  };

  client.onMsg = (action, data) => {
    const handler =
      {
        game: onGameUpdate,
        error: () => console.error(`Server sent error ${data}`);
      }[action] ??
      function() {
        console.error(
          `Server sent unknown action in message to lobby: ${{ action, data }}`,
        );
      };
    handler(data);
    m.redraw();
  };

  function turn(game) {
    return game.position.moves.length % 2 === 0 ? "white" : "black";
  }

  function onGameUpdate(data) {
    // we might have connected after opponent played a move, btw
    // so we need to set full state
    state.game = { ...state.game, ...data.game };
    state.color ??= state.game.black_id === userId ? "black" : "white";
    state.cg.set({
      orientation: state.color,
      turnColor: turn(state.game),
      fen: state.game.position.fen,
      movable: {
        free: true, // TODO: request dests and set them
        color: turn(state.game),
      },
    });
    if (state.game.status !== "playing") {
      state.cg.set({
        movable: {
          free: false,
        }
      })
    }
  }

  function onMyMove(orig, dest) {
    state.cg.set({
      movable: {
        // set it immediatly
        color: state.cg.state.turnColor === "white" ? "black" : "white",
      },
    });
    client.sendMsg({
      action: "make-move",
      data: {
        move: orig + dest,
      },
    });
  }

  function init() {
    const el = document.querySelector(".cg-wrap");
    state.cg = Chessground(el, { movable: false });
    state.cg.set({
      movable: {
        events: {
          after: (orig, dest, _) => onMyMove(orig, dest),
        },
      },
    });
    client.connect();
  }

  return {
    view: () => [
      m(NavBar),
      m("section.blue.merida", m("div.cg-wrap", { oncreate: init })),
      m("p", "White: ", state.game.white_id),
      m("p", "Black: ", state.game.black_id),
      m("p", "Status: ", state.game.status),
      m("p", "Moves: ", state.game.position.moves),
    ],
  };
}
