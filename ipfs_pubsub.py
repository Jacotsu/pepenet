from urllib import request
from urllib.parse import urlencode
import json

api_urls = {"ls": "/api/v0/pubsub/ls",
            "peers": "/api/v0/pubsub/peers",
            "pub": "/api/v0/pubsub/pub",
            "sub": "/api/v0/pubsub/sub"
            }


class PubSub:
    def __init__(self, host="localhost", port=5001):
        self.host = host
        self.port = port

    def topic_ls(self):
        "Lists topics by name, returns a list of strings"
        url = "http://{}:{}{}".format(self.host, self.port, api_urls["ls"])
        with request.urlopen(url) as response:
            return json.loads(response.read().decode("utf-8"))["Strings"]

    def topic_peers(self, topic=None):
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
           # Should check that the return code is 200
           pass

#    def topic_sub(self, topic, discover_peers=False):
#        """
#        Subscribes to topic, This is a blocking synchronous function.
#        Should be an async non blocking function
#        """
#        url = "http://{}:{}{}?arg={}&discover={}".format(self.host,
#                                                         self.port,
#                                                         api_urls["sub"],
#                                                         topic,
#                                                         discover_peers)
#        with request.urlopen(url) as response:
#            return json.loads(response.read().decode("utf-8"))["Message"]
