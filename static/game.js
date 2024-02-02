//@ts-check
import { Chessground } from "./chessground.min.js";
import { StrongSocket } from "./client.js";
import { userId } from "./user.js";

// TODO:
// offer draw
// online status, spectators

/**
 *  @typedef Move
 *  @property {string} src
 *  @property {string} dest
 *  @property {string} promo
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
 *  @property {Move[]} moves,
 */

/**
 *  @typedef {"white" | "black"} Color
 */

const gameId = parseInt(document.getElementById("data")?.dataset?.gameid);

/** @type Game */
let game = {};
game.id = gameId;

/** @type {string[]} */
let keystack = [];

let cg;

const client = new StrongSocket(`game/${gameId}`);

client.onConnect = () => {
  client.sendMsg({
    type: "auth",
    userId,
  });
  client.sendMsg({
    type: "reconnect",
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
    case "auth_ok":
      console.log("Authenticated", msg);
      break;
    case "reconnect":
      console.log("User reconnected", msg);
      break;
    case "game":
      updateGame(msg.game);
      refreshGameInfo();
      maybeMove(); // premove
      break;
    case "error":
      console.log("Server sent error", msg);
      break;
    default:
      console.log("Unknown message", msg);
      break;
  }
};

/**
   * @param {string[]} keystack
   * @return {Move}

  */
function keystackIntoUci(keystack) {
  const src = keystack.slice(0, 2).join("");
  const dest = keystack.slice(2, 4).join("");
  const promo = "";
  return {
    src: src.length === 2 ? src : "",
    dest: dest.length === 2 ? dest : "",
    promo,
  };
}

function maybeMove() {
  const { src, dest, promo } = keystackIntoUci(keystack);

  if (dest !== "") {
    if (myColor() !== whichTurn()) {
      return;
    } else {
      sendMove(src, dest, promo);
      keystack = [];
      refreshKeys();
    }
  }
}

function makeMove(src, dest) {
  sendMove(src, dest);
}

window.addEventListener("keydown", event => {
  const key = event.key;
  if (key == "Escape") {
    keystack = [];
    refreshKeys();
    return;
  }

  // prettier-ignore
  const squares = [
      "a", "b", "c", "d", "e", "f", "g", "h",
      "1", "2", "3", "4", "5", "6", "7", "8",
    ];
  if (!squares.includes(key)) return;

  if (keystack.length < 4) {
    keystack.push(key);
  }
  refreshKeys();

  maybeMove();
});

function whichTurn() {
  if (!game?.moves) return undefined;
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
function canMove() {
    const mycolor = myColor();
    const turn = whichTurn();
    return mycolor && turn && mycolor === turn;
}

/**
 * @param {any} gameUpdated
 */
function updateGame(gameUpdated) {
  game.id = parseInt(gameUpdated["id"]);
  game.whiteId = parseInt(gameUpdated["whiteId"]);
  game.blackId = parseInt(gameUpdated["blackId"]);
  game.stage = gameUpdated["stage"];
  game.result = gameUpdated["result"];
  game.winner = gameUpdated["winner"];
  game.fen = gameUpdated["fen"];
  game.moves = gameUpdated["moves"];

  if (cg === null) throw new Error("cg === null");
  const move = game.moves[game.moves.length - 1];

  cg.set({
    orientation: myColor() ?? "white",
    turnColor: canMove(),
    lastMove: move ? [move.src, move.dest] : undefined,
    fen: game.fen,
    movable: {
      color: canMove(), 
    },
  });
  if (!["playing", "waiting"].includes(game.stage)) cg.stop();
}

/**
 * @param {string} src
 * @param {string} dest
 * @param {string} promo
 * */
function sendMove(src, dest, promo = "") {
  client.sendMsg({
    type: "make_move",
    src,
    dest,
    promo,
  });
}

function resign() {
  client.sendMsg({
    type: "resign",
  });
}

function initChessground() {
  const el = /** @type {HTMLInputElement} */ (
    document.querySelector(".cg-wrap")
  );

  const cgConfig = {
    movable: {
      free: true,
      events: {
        after: (src, dest, _) => makeMove(src, dest),
      },
    },
  };
  cg = Chessground(el, cgConfig);
}

function refreshGameInfo() {
  const info = document.querySelector("#game-info");
  info.innerText = `Game: ${JSON.stringify(game)}`;
}

function refreshKeys() {
  const keys = document.querySelector("#keystack");
  keys.innerText = `Pressed keys (UCI): ${keystack.join("")}`;
}

document.addEventListener("DOMContentLoaded", event => {
  initChessground();
  document.querySelector("button#resign")?.addEventListener("click", event => {
    resign();
  });
  client.connect();
});

