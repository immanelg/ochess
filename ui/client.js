export class WSClient {
  constructor(url) {
    this.baseurl = "ws://127.0.0.1:8000/ws/";
    this.url = this.baseurl + url;
  }

  reconnect = ms => {
    setTimeout(() => {
      console.log("Reconnecting");
      this.connect();
    }, ms);
  };

  connect() {
    delete this.ws;
    this.ws = new WebSocket(this.url);

    this.ws.onopen = event => {
      console.log("Opened connection");
      this.onOpen(event);
    };

    this.ws.onmessage = event => {
      const text = event.data;
      const obj = JSON.parse(text);
      console.log("Got data", obj);
      const action = obj.action;
      const data = obj.data;
      this.onMsg(action, data);
    };

    this.ws.onclose = event => {
      console.log("Closing", event);
      this.onClose(event);
      this.reconnect(10_000);
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

  onMsg(action, data) {
    // ...
  }

  sendMsg(obj) {
    this.ws.send(JSON.stringify(obj));
  }
}
