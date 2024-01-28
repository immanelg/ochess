// @ts-check
// TODO: refactor fat components.
// I didn't care because writing good browser front-end wasn't my goal.
// It is just for "proof of concept".

import m from "mithril";
import About from "./About";
import Game from "./Game";
import Lobby from "./Lobby";
import Watch from "./Watch";

const root = document.querySelector("#app");

m.route(root, "/", {
  "/": Lobby,
  "/game/:gameId": Game,
  "/watch": Watch,
  "/about": About,
});
