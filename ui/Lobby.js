//@ts-check
import m from "mithril";
import { OchessWebSocket } from "./client";
import { userId } from "./user";
import NavBar from "./Navbar";

/**
 * @typedef Invite
 * @property {number} gameId
 * @property {number?} whiteId
 * @property {number?} blackId
*/


export default function Lobby() {

  /** @type {Invite[]} */
  let invites = [];

  const client = new OchessWebSocket("lobby");

  client.onConnect = _ => {
    client.sendMsg({ type: "auth", user_id: userId });
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
          gameId: parseInt(msg["game_id"]),
          whiteId: parseInt(msg["white_id"]),
          blackId: parseInt(msg["black_id"]),
        });
        console.table(invites);
        break;
      case "accept_game":
        // did someone just accept our invite 👉👈?
        if (userId === parseInt(msg["white_id"]) || userId === parseInt(msg["black_id"])) {
          console.log("Our game was accepted", msg);
          client.close();
          m.route.set(`/game/${msg["game_id"]}`);
        }
        invites = invites.filter(inv => inv.gameId !== msg["game_id"]);
        console.log("Someone accepted an invite!");
        console.table(invites);
        break;
      case "cancel_game":
        invites = invites.filter(inv => inv.gameId !== msg["game_id"]);
        console.log("Invite is cancelled");
        console.table(invites);
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
    m.redraw();
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

  /**
   * @param gameId {number}
   */
  function accept(gameId) {
    console.log("Accepted invite");
    client.sendMsg({
      type: "accept_game",
      game_id: gameId,
    });
  }

  /**
   * @param gameId {number}
   */
  function cancel(gameId) {
    console.log("Cancelling invite");
    client.sendMsg({
      type: "cancel_game",
      game_id: gameId,
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

  return {
    oncreate: () => client.connect(),
    view: () => [
      m(NavBar),
      m(
        "table.invites",
        m(
          "thead",
          m("tr", m("th", "color"), m("th", "player"), m("th", "game")),
        ),
        m(
          "tbody",
          invites.map(row =>
            m(
              "tr",
              {
                onclick: () =>
                  clickInvite(row.whiteId ?? row.blackId, row.gameId),
                key: row.gameId,
              },

              m("td", row.whiteId ? "white" : "black"),
              m("td", row.whiteId ?? row.blackId),
              m("td", row.gameId),
            ),
          ),
        ),
      ),
      m(
        ".center",
        m(
          "button",
          {
            onclick: () => create(null),
          },
          "New Game",
        ),
      ),
    ],
  };
}
