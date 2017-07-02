from urllib import request
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

    def __subscription_fetch_data(self):
        "Fetches the data for every subscribed topic and saves it"
        while True:
            for topic, packed_topic in self.subscriptions.items():
               # packed_topic["data"].append(packed_topic["socket"].
               #                             read(512).decode("utf-8"))
               pass
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
        if not self.update_thread:
            self.update_thread = Thread(target=self.__subscription_fetch_data)
            self.update_thread.start()
            pass

        if topic not in self.subscriptions:
            try:
                self.subscriptions[topic] = {"socket": request.urlopen(url),
                                             "data": []
                                             }
            except Exception as exc:
                logging.error(exc)

            self.__subscription_fetch_data()
            return True
