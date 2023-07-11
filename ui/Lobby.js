import m from "mithril";
import { WSClient } from "./client";
import NavBar from "./Navbar";

const dataset = document.getElementById("data")?.dataset;
const userId = parseInt(dataset.userId);

export default function Lobby() {
  let invites = [];

  const client = new WSClient("lobby");
  window.client = client;

  client.onMsg = (action, data) => {
    switch (action) {
      case "ping":
        console.log("pong!");
        break;
      case "create-invite":
        invites.push({
          user_id: data.user_id,
          game_id: data.game_id,
          color: data.white === true ? "white" : "black",
        });
        console.table(invites);
        break;
      case "accept-invite":
        // we are in this game, meaning it's either us who accepted it
        // or someone else accepted our invite.
        if (data.white_id === userId || data.black_id === userId)
          m.route.set(`/game/${data.game_id}`);
        invites = invites.filter(inv => inv.game_id !== data.game_id);
        console.log("Someone accepted an invite!");
        console.table(invites);
        break;
      case "cancel-invite":
        invites = invites.filter(inv => inv.game_id !== data.game_id);
        console.log("Invite is cancelled");
        console.table(invites);
        break;
      case "error":
        console.error(`Server sent error ${data}`);
        break;
      default:
        console.error(
          `Server sent unknown action in message to lobby: ${{ action, data }}`,
        );
        break;
    }
    m.redraw();
  };

  function onMyCreateInvite() {
    client.sendMsg({
      action: "create-invite",
      data: {
        white: Math.random() < 0.5,
      },
    });
    console.log("Creating invite");
  }

  function onMyAcceptInvite(gameId) {
    client.sendMsg({
      action: "accept-invite",
      data: {
        game_id: gameId,
      },
    });
    console.log("Accepting invite");
  }

  function onMyCancelInvite(gameId) {
    client.sendMsg({
      action: "cancel-invite",
      data: {
        game_id: gameId,
      },
    });
    console.log("Cancelling invite");
  }

  function onMyCreateInvite() {
    client.sendMsg({
      action: "create-invite",
      data: {
        white: Math.random() < 0.5,
      },
    });
    console.log("Creating invite");
  }

  function onClickInvite(inviteUserId, gameId) {
    if (userId === inviteUserId) onMyCancelInvite(gameId);
    else onMyAcceptInvite(gameId);
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
                onclick: () => onClickInvite(row.user_id, row.game_id),
                key: row.game_id,
              },
              ["color", "user_id", "game_id"].map(col => m("td", row[col])),
            ),
          ),
        ),
      ),
      m(
        ".center",
        m("button", { onclick: event => onMyCreateInvite() }, "New game"),
      ),
    ],
  };
}
