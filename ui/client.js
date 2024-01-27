export class WSClient {
  constructor(url) {
    this.baseurl = "ws://127.0.0.1:8000/ws/";
    this.url = this.baseurl + url;
  }

  reconnect = sec => {
    setTimeout(() => {
      console.log("Reconnecting");
      this.connect();
    }, 1000*sec);
  };

  connect() {
    this.ws = new WebSocket(this.url);

    this.ws.onopen = event => {
      console.log("Opened connection");
      this.onOpen(event);
    };

    this.ws.onmessage = event => {
      const text = event.data;
      const msg = JSON.parse(text);
      console.log(`Got message ${msg}`);
      this.onMsg(msg);
    };

    this.ws.onclose = event => {
      console.log("Closing", event);
      this.onClose(event);
      this.reconnect(10);
    };

    this.ws.onerror = event => {
      console.log("Error", event);
      this.onError(event);
      this.ws.close();
    };
  }

  onOpen(event) {
    // ...
  }

  onClose(event) {
    // ...
  }

  onError(event) {
    // ...
  }

  onMsg(msg) {
    // ...
  }

  sendMsg(obj) {
    this.ws.send(JSON.stringify(obj));
  }
}
