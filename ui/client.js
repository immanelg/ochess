//@ts-check
/**
 * @property {string} baseurl
 * @property {WebSocket} ws
 */
export class OchessWebSocket {
  /**
   * @param {string} url
   */
  constructor(url) {
    this.baseurl = `ws://${window.location.host}/ws/`;
    this.url = this.baseurl + url;
    window["ochessSocket"] = this;
  }

  connect() {
    this.ws = new WebSocket(this.url);

    this.ws.onopen = event => {
      console.log("Open connection", this.url);
      this.onConnect(event);
    };

    this.ws.onmessage = event => {
      const text = event.data;
      const msg = JSON.parse(text);
      this.onMsg(msg);
    };

    this.ws.onclose = event => {
      this.onClose(event);
      this.reconnect(10);
    };

    this.ws.onerror = event => {
      this.onError(event);
      this.ws.close();
    };
  }

  /**
   * @param sec {number}
   **/
  reconnect = sec => {
    console.log(`Reconnecting after ${sec}s...`);
    setTimeout(() => {
      this.connect();
    }, 1000 * sec);
  };

  close() {
    this.ws.close();
  }

  /**
   * @param msg {Object}
   */
  sendMsg(msg) {
    const json = JSON.stringify(msg);
    console.log(`Sending msg ${json}`);
    this.ws.send(json);
  }

  /**
   * @param msg {Object}
   */
  onMsg(msg) {}

  /**
   * @param {any} event
   */
  onConnect(event) {}

  /**
   * @param {any} event
   */
  onClose(event) {}

  /**
   * @param {any} event
   */
  onError(event) {}
}
