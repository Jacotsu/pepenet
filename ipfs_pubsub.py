from urllib import request
import requests
from base64 import b64decode
from urllib.parse import urlencode
from threading import Thread
from time import sleep
import logging
import json

api_urls = {"ls": "/api/v0/pubsub/ls",
            "peers": "/api/v0/pubsub/peers",
            "pub": "/api/v0/pubsub/pub",
            "sub": "/api/v0/pubsub/sub"
            }


class PubSub:
    def __init__(self, host="localhost", port=5001, update_interval=0.5):
        self.host = host
        self.port = port
        # this contains the fetched data and their relative sockets
        # [topic] = {"data": data, "socket": socket}
        self.subscriptions = {}
        self.update_thread = None
        self.sub_update_interval = update_interval

    def topic_ls(self):
        "Lists topics by name, returns a list of strings"
        url = "http://{}:{}{}".format(self.host, self.port, api_urls["ls"])
        with request.urlopen(url) as response:
            return json.loads(response.read().decode("utf-8"))["Strings"]

    def topic_peers(self, topic=""):
        "Lists peers subscribed to topic, returns a list of peers"
        url = "http://{}:{}{}?arg={}".format(self.host,
                                             self.port,
                                             api_urls["peers"],
                                             topic)
        with request.urlopen(url) as response:
            return json.loads(response.read().decode("utf-8"))["Strings"]

    def topic_pub(self, topic, payload):
        "Publishes payload to topic, returns True if successfull"
        url = "http://{}:{}{}?arg={}&arg={}".format(self.host,
                                                    self.port,
                                                    api_urls["pub"],
                                                    topic,
                                                    payload)
        with request.urlopen(url, payload.encode("utf-8")) as response:
            if response.getcode() == 200:
                return True
            else:
                return False

    def _subscription_fetch_data(self, topic):
        "Fetches the data for every subscribed topic and saves it"
        while True:
            # topic_data["socket"][1] is the socket iterator
            for msg in self.subscriptions[topic]["socket"][1]:
                if msg:
                    decoded_msg = msg.decode("utf-8")
                    if decoded_msg != "{}":
                        # Here we get the actual data in base 64
                        data = decoded_msg.split(",")[1].split(":")[1]
                        logging.debug("Received data: ".format(data))
                        if data:
                            self.subscriptions[topic]["data"].append(data)
            sleep(self.sub_update_interval)

    def topic_sub(self, topic, discover_peers=False):
        """
        Subscribes to topic, returns true if successfull
        """
        url = "http://{}:{}{}?arg={}&discover={}".format(self.host,
                                                         self.port,
                                                         api_urls["sub"],
                                                         topic,
                                                         discover_peers)
        if topic not in self.subscriptions:
            try:
                socket = requests.get(url, stream=True)
                iterator = socket.iter_lines()
                update_thread = Thread(target=self._subscription_fetch_data,
                                       args=(topic,))
                self.subscriptions[topic] = {"socket": [socket, iterator],
                                             "thread": update_thread,
                                             "data": []
                                             }
                update_thread.start()
            except Exception as exc:
                logging.error(exc)

            return True

    def topic_pop_message(self, topic):
        # FIFO data stack
        if self.subscriptions[topic]["data"]:
            return b64decode(self.subscriptions[topic]["data"].pop(0))

if __name__ == "__main__":
    logging.error("Don't execute this module")
