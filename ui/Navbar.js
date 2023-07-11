import m from "mithril";

export default function NavBar() {
  return {
    view() {
      return m(".topnav", [
        m(m.route.Link, { href: "/" }, "Lobby"),
        m(m.route.Link, { href: "/about" }, "About"),
      ]);
    },
  };
}
