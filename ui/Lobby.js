//@ts-check
import m from "mithril";
import { WSClient } from "./client";
import { userId } from "./user";
import NavBar from "./Navbar";

export default function Lobby() {
  /**
    * @type {Array<{
          gameId: string,
          whiteId?: string,
          blackId?: string,
    * }>}
    */
  let invites = [];

  const client = new WSClient("lobby");

  client.onOpen = _ => {
    client.sendMsg({type: "auth", user_id: userId});
  }

  client.onMsg = (msg) => {
    switch (msg.type) {
      case "ping":
        console.log("pong!");
        client.sendMsg({type: "ping"});
        break;
      case "create_game":
        invites.push({
          gameId: msg["game_id"],
          whiteId: msg["white_id"],
          blackId: msg["black_id"],
        });
        console.table(invites);
        break;
      case "accept_game":
        // did someone just accept our invite 👉👈?
        if ([msg["white_id"], msg["black_id"]].includes(userId)) {
          m.route.set(`/game/${msg["game_id"]}`);
          return;
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
        console.error(`Server sent error ${msg}`);
        break;
      default:
        console.error(
          `Unknown message: ${msg}`,
        );
        break;
    }
    m.redraw();
  };

  function create(white = null) {
    console.log("Create invite");
    client.sendMsg({
      action: "create_game",
      data: {
        white: white,
      },
    });
  }

  /**
    * @param gameId {string}
    */
  function accept(gameId) {
    console.log("Accepted invite");
    client.sendMsg({
      action: "accept_game",
      data: {
        game_id: gameId,
      },
    });
  }

  /**
    * @param gameId {string}
    */
  function cancel(gameId) {
    console.log("Cancelling invite");
    client.sendMsg({
      action: "cancel_game",
      data: {
        game_id: gameId,
      },
    });
  }


  /**
    * @param creatorId {string}
    * @param gameId {string}
    */
  function clickInvite(creatorId, gameId) {
    if (userId === creatorId)
      cancel(gameId);
    else
      accept(gameId);
  }

  return {
    view: () => [
      m(NavBar),
      m(
        "table.invites",
        { oncreate: () => client.connect() },
        m(
          "thead",
          m("tr", m("th", "color"), m("th", "player id"), m("th", "game id")),
        ),
        m(
          "tbody",
          invites.map(row =>
            m(
              "tr",
              {
                onclick: () => clickInvite(row.whiteId ?? row.blackId, row.gameId),
                key: row.gameId,
              },
              ["color", "userId", "gameId"].map(col => m("td", row[col])),
            ),
          ),
        ),
      ),
      m(
        ".center",
        m("button", { onclick: _event => create() }, "New Game"),
      ),
    ],
  };
}
