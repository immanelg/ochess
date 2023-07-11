import m from "mithril";
import NavBar from "./Navbar";

export default function About() {
  return {
    view() {
      return [
        m(NavBar),
        m(
          "p",
          "Source code: ",
          m("a", { href: "http://github.com/immanelg/ochess" }, "GitHub"),
        ),
      ];
    },
  };
}
