//@ts-check
import m from "mithril";
import NavBar from "./Navbar";
import { Chessground } from "chessground";
import { OchessWebSocket } from "./client";
import { userId } from "./user";

// TODO:
// fetch legal moves from the server
// fix funky chessground (im lazy to understand its API)
// resign (I mean in chess)
// player online, spectator count, etc

/**
 *  @typedef Game
 *  @property {number} id
 *  @property {number?} whiteId
 *  @property {number?} blackId,
 *  @property {"waiting" | "playing" | "ended"} stage,
 *  @property {"checkmate" | "draw" | "resign" | "abandoned"} result,
 *  @property {"white" | "black"} winner,
 *  @property {string} fen,
 *  @property {Array<{move: string}>} moves,
 */

export default function Game() {
  const gameId = parseInt(m.route.param("gameId"));

  /** @type Game */
  let game = {};
  game.id = gameId;

  /** @type {"white" | "black" | null} */
  let myColor = null;

  /** @type {import("chessground/api").Api | null} */
  let cg;

  const client = new OchessWebSocket(`game/${gameId}`);

  client.onConnect = () => {
    client.sendMsg({
      type: "auth",
      userId: userId,
    })
    client.sendMsg({
      type: "fetch_game",
    });
  };

  client.onMsg = msg => {
    switch (msg["type"]) {
      case "pong":
        console.log("Pong!");
        client.sendMsg({ type: "ping" });
        break;
      case "error":
        console.log("Server sent error", msg);
        break;
      case "game":
        updateGame(msg.game);
        break;
      case "auth_ok":
        console.log("Authenticated", msg);
        break;
      default:
        console.log("Unknown message", msg);
        break;
    }
    m.redraw();
  };

  function getTurn() {
    if (!game.moves) return undefined;
    return game.moves.length % 2 === 0 ? "white" : "black" ;
  }

  /** 
    * @param {Game} gameUpdated
    */
  function updateGame(gameUpdated) {
    // update full state of the game, so even if we reconnected, we get valid state
    game.id = gameUpdated["id"];
    game.whiteId = gameUpdated["whiteId"];
    game.blackId = gameUpdated["blackId"];
    game.stage = gameUpdated["stage"];
    game.result = gameUpdated["result"];
    game.winner = gameUpdated["winner"];
    game.fen = gameUpdated["fen"];
    game.moves = gameUpdated["moves"];

    switch (userId) {
      case game.whiteId:
        myColor = "white";
        break;
      case game.blackId:
        myColor = "black";
        break;
      default:
        myColor = null;
    }
    console.assert(cg !== null);
    cg.set({
      orientation: myColor ?? "white",
      turnColor: getTurn(),
      fen: game.fen,
      movable: {
        free: true, // TODO: request dests and set them
        color: getTurn(),
      },
    });
    if (game.stage !== "playing" && game.stage !== "waiting") {
      cg.set({
        movable: {
          free: false,
        },
      });
    }
  }

  function makeMove(orig, dest) {
    cg.set({
      movable: {
        color: undefined, // lock right after our move
      },
    });
    client.sendMsg({
      type: "make_move",
        move: orig + dest,
    });
  }

  function init() {
    const el = document.querySelector(".cg-wrap");
    cg = Chessground(el, { movable: false });
    cg.set({
      movable: {
        events: {
          after: (orig, dest, _) => makeMove(orig, dest),
        },
      },
    });
    client.connect();
  }

  return {
    view: () => [
      m(NavBar),
      m("section.blue.merida", m("div.cg-wrap", { oncreate: init })),
      m("p", "Game: ", JSON.stringify(game)),
      m("p", "My color: ", myColor),
      m("p", "My ID: ", userId),
      m("p", "Game ID: ", gameId),
      m("p", "White: ", game.whiteId),
      m("p", "Black: ", game.blackId),
      game.moves ? m("p", "Moves: ", game.moves.map(m => m.move).join(", ")) : '',
    ],
  };
}
