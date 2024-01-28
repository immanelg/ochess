//@ts-check
import m from "mithril";
import NavBar from "./Navbar";
import { Chessground } from "chessground";
import { OchessWebSocket } from "./client";
import { userId } from "./user";

// TODO:
// offer draw
// player online, spectators, etc

// TODO: keyboard input!

/**
 * @typedef {import("chessground/types").Key} Key
 */

/**
 *  @typedef Game
 *  @property {number} id
 *  @property {number?} whiteId
 *  @property {number?} blackId,
 *  @property {"waiting" | "playing" | "ended"} stage,
 *  @property {"checkmate" | "draw" | "resign" | "abandoned" | null} result,
 *  @property {Color?} winner,
 *  @property {string} fen,
 *  @property {Array<{move: string}>} moves,
 */

/**
 *  @typedef {"white" | "black"} Color
 */

export default function Game() {
  const gameId = parseInt(m.route.param("gameId"));

  /** @type Game */
  let game = {};
  game.id = gameId;

  /** @type {string[]} */
  let keystack = [];

  /** @type {import("chessground/api").Api | null} */
  let cg;

  const client = new OchessWebSocket(`game/${gameId}`);

  client.onConnect = () => {
    client.sendMsg({
      type: "auth",
      userId: userId,
    });
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

  window.addEventListener("keydown", event => {
    const key = event.key;
    if (key == "Escape") {
      keystack = [];
      m.redraw();
      return;
    }

    // prettier-ignore
    const moveKeys = [
      "a", "b", "c", "d", "e", "f", "g", "h",
      "1", "2", "3", "4", "5", "6", "7", "8"
    ];
    if (!moveKeys.includes(key)) return;

    if (keystack.length < 4) {
      keystack.push(key);
    }

    if (keystack.length === 4 && myColor() === whichTurn()) {
      makeMove(keystack.slice(0, 2).join(""), keystack.slice(2, 4).join(""));
      keystack = [];
    }
    m.redraw();
  });

  function whichTurn() {
    if (!game.moves) return undefined;
    return game.moves.length % 2 === 0 ? "white" : "black";
  }

  function myColor() {
    switch (userId) {
      case game.whiteId:
        return "white";
      case game.blackId:
        return "black";
    }
  }

  /**
   * @param {any} gameUpdated
   */
  function updateGame(gameUpdated) {
    // update full state of the game, so even if we reconnected, we get valid state
    game.id = parseInt(gameUpdated["id"]);
    game.whiteId = parseInt(gameUpdated["whiteId"]);
    game.blackId = parseInt(gameUpdated["blackId"]);
    game.stage = gameUpdated["stage"];
    game.result = gameUpdated["result"];
    game.winner = gameUpdated["winner"];
    game.fen = gameUpdated["fen"];
    game.moves = gameUpdated["moves"];

    if (cg === null) throw new Error("cg === null");

    const lastMove = game.moves[game.moves.length - 1]?.move;
    const lastMoveKeys = lastMove
      ? /** @type {Key[] | undefined} */ ([
          lastMove.slice(0, 2),
          lastMove.slice(2, 4),
        ])
      : undefined;
    cg.set({
      orientation: myColor() ?? "white",
      lastMove: lastMoveKeys,
      fen: game.fen,
      movable: {
        free: false,
      },
    });
  }

  /**
   * @param {string} orig
   * @param {string} dest
   * @param {string?} promo
   * */
  function makeMove(orig, dest, promo = null) {
    client.sendMsg({
      type: "make_move",
      move: orig + dest,
    });
  }

  function resign() {
    client.sendMsg({
      type: "resign",
    });
  }

  function init() {
    const el = /** @type {HTMLInputElement} */ (
      document.querySelector(".cg-wrap")
    );
    cg = Chessground(el, {
      movable: {
        free: false,
      },
    });
    client.connect();
  }

  return {
    view: () => [
      m(NavBar),
      m(
        ".center",
        m(
          "section.blue.merida",
          m("div.cg-wrap", {
            oncreate: init,
          }),
        ),
      ),
      m("p", keystack),
      m("p", "Game: ", JSON.stringify(game)),
      m("p", "My color: ", myColor()),
      m("p", "My ID: ", userId),
      m("button", { onclick: () => resign() }, "Resign"),
    ],
  };
}
