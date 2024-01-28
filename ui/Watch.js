import m from "mithril";
import NavBar from "./Navbar";

export default function Watch() {
  return {
    view() {
      return [
        m(NavBar),
        m(
          "p",
          "Not implemented. Maybe we will have a cool grid with live games which you can click.",
        ),
        m("a", { href: "http://github.com/immanelg/ochess" }, "Make a PR!"),
      ];
    },
  };
}
