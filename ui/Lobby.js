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
  // debug
  // invites.push({
  //   gameId: 1,
  //   whiteId: 2,
  //   blackId: 3,
  // });
  // invites.push({
  //   gameId: 1,
  //   whiteId: 2,
  //   blackId: 3,
  // });
  // invites.push({
  //   gameId: 1,
  //   whiteId: 2,
  //   blackId: 3,
  // });

  const client = new OchessWebSocket("lobby");

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
        break;
      case "accept_game":
        // did someone just accept our invite 👉👈?
        if (
          userId === parseInt(msg["whiteId"]) ||
          userId === parseInt(msg["blackId"])
        ) {
          console.log("Our game was accepted", msg);
          client.close();
          m.route.set(`/game/${msg["gameId"]}`);
        }
        invites = invites.filter(inv => inv.gameId !== msg["gameId"]);
        console.log("Someone accepted an invite!");
        console.table(invites);
        break;
      case "cancel_game":
        invites = invites.filter(inv => inv.gameId !== msg["gameId"]);
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

  return {
    oncreate: () => client.connect(),
    view: () => [
      m(NavBar),
      m(
        "table.invites",
        m(
          "thead",
          m("tr", m("th", "Color"), m("th", "Player ID"), m("th", "Game ID")),
        ),
        m(
          "tbody",
          invites.map(game =>
            m(
              "tr",
              {
                onclick: () =>
                  clickInvite(game.whiteId ?? game.blackId, game.gameId),
                key: game.gameId,
              },

              m("td", game.whiteId ? "white" : "black"),
              m("td", game.whiteId ?? game.blackId),
              m("td", game.gameId),
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
          "Create Game",
        ),
        m(
          "button",
          {
            onclick: () => alert("todo!"),
          },
          "Play with friend",
        ),
      ),
    ],
  };
}
