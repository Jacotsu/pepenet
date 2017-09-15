from urllib import request
import requests
from threading import Thread
from time import sleep
from time import time
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

    def topic_peer_number(self, topic):
        peers = self.topic_peers(topic)
        if peers:
            return len(peers)
        return 0

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
                        if "data" not in decoded_msg:
                            continue
                        # Here we get the actual data in base 64
                        data = {"content":
                                decoded_msg.split(",")[1].split(":")[1],
                                "sender": decoded_msg.split(",")[0].
                                split(":")[1],
                                "timestamp": time()
                                }

                        logging.debug("Received data: ".format(data))

                        if data:
                            for callback in self.\
                                            subscriptions[topic]["on_receive"]:
                                callback(data)

                            self.subscriptions[topic]["msg"].append(data)
            sleep(self.sub_update_interval)

    def topic_data(self, topic):
        return self.subscriptions[topic]["msg"]

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
                # on_receive should be a list of callbacks
                self.subscriptions[topic] = {"socket": [socket, iterator],
                                             "thread": update_thread,
                                             "msg": [],
                                             "on_receive": []
                                             }
                update_thread.start()
            except Exception as exc:
                logging.error(exc)

            return True

    def topic_set_callback(self, topic, func):
        """
        Sets func as callback for topic update, func is called as follow
        func(data)
        where data is a dict with the following keys:
        ['hash', 'timestamp', 'sender']
        """
        if self.subscriptions[topic]:
            self.subscriptions[topic]["on_receive"].append(func)

    def topic_pop_message(self, topic):
        # FIFO data stack
        if self.subscriptions[topic]["msg"]:
            return self.subscriptions[topic]["msg"].pop(0)

    def topic_pop_messages_from_sender(self, topic, sender):
        # FIFO data stack
        messages = set()
        removable = []
        if self.subscriptions[topic]["msg"]:
            for msg in self.subscriptions[topic]["msg"]:
                if msg["sender"] == sender:
                    messages.update((msg["content"],))
                    removable.append((msg,))

            for msg in removable:
                try:
                    self.subscriptions[topic]["msg"].remove(msg)
                except:
                    pass

        return messages


if __name__ == "__main__":
    logging.error("Don't execute this module")
