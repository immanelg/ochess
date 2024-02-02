//@ts-check
import { StrongSocket } from "./client.js";
import { userId } from "./user.js";

/**
 * @typedef Invite
 * @property {number} gameId
 * @property {number?} whiteId
 * @property {number?} blackId
 */

/** @type {Invite[]} */
let invites = [];

const client = new StrongSocket("lobby");

client.onConnect = _ => {
  client.sendMsg({ type: "auth", userId: userId });
  // client.sendMsg({
  //   type: "get_waiting_games",
  // });
};

client.onMsg = msg => {
  switch (msg["type"]) {
    case "pong":
      console.log("Pong!");
      client.sendMsg({ type: "ping" });
      break;
    case "create_game":
      invites.push({
        gameId: parseInt(msg["gameId"]),
        whiteId: parseInt(msg["whiteId"]) || null,
        blackId: parseInt(msg["blackId"]) || null,
      });
      console.table(invites);
      refreshTable();
      break;
    case "accept_game":
      // did someone just accept our invite 👉👈?
      if (
        userId === parseInt(msg["whiteId"]) ||
        userId === parseInt(msg["blackId"])
      ) {
        console.log("Our game was accepted", msg);
        client.close();
        window.location.assign(`/game/${msg["gameId"]}`);
      }
      invites = invites.filter(inv => inv.gameId !== msg["gameId"]);
      console.log("Someone accepted an invite!");
      console.table(invites);
      refreshTable();
      break;
    case "cancel_game":
      invites = invites.filter(inv => inv.gameId !== msg["gameId"]);
      console.log("Invite is cancelled");
      console.table(invites);
      refreshTable();
      break;
    case "error":
      console.log("Server sent error", msg);
      break;
    case "auth_ok":
      console.log("Authenticated", msg);
      break;
    default:
      console.log("Unknown message", msg);
      break;
  }
};

/**
 * @param white {boolean?}
 */
function create(white) {
  console.log("Create invite");
  client.sendMsg({
    type: "create_game",
    white,
  });
}

function createChallenge() {
  alert("todo");
}

/**
 * @param gameId {number}
 */
function accept(gameId) {
  console.log("Accepted invite");
  client.sendMsg({
    type: "accept_game",
    gameId: gameId,
  });
}

/**
 * @param gameId {number}
 */
function cancel(gameId) {
  console.log("Cancelling invite");
  client.sendMsg({
    type: "cancel_game",
    gameId: gameId,
  });
}

/**
 * @param creatorId {number}
 * @param gameId {number}
 */
function clickInvite(creatorId, gameId) {
  if (userId === creatorId) cancel(gameId);
  else accept(gameId);
}

function refreshTable() {
  const table = document
    .querySelector("table.invites")
    .getElementsByTagName("tbody")[0];
  table.innerHTML = "";

  invites.forEach(({ blackId, whiteId, gameId }) => {
    const row = table.insertRow();
    const creatorId = whiteId ?? blackId;
    row.addEventListener("click", event => {
      clickInvite(creatorId, gameId);
      refreshTable();
    });
    row
      .insertCell()
      .appendChild(document.createTextNode(whiteId ? "white" : "black"));
    row.insertCell().appendChild(document.createTextNode(creatorId));
    row.insertCell().appendChild(document.createTextNode(gameId));
  });
}

window.addEventListener("DOMContentLoaded", event => {
  document
    .getElementById("create-game")
    .addEventListener("click", event => create(null));
  document
    .getElementById("create-challenge")
    .addEventListener("click", event => createChallenge());
  client.connect();
});
