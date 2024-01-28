import m from "mithril";

export default function NavBar() {
  return {
    view() {
      return m(
        "nav",
        m("h1", "ochess"),
        m("ul", [
          m("li", m(m.route.Link, { href: "/" }, "Lobby")),
          m("li", m(m.route.Link, { href: "/watch" }, "Watch")),
          m("li", m(m.route.Link, { href: "/about" }, "About")),
        ]),
      );
    },
  };
}
