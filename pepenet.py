#!/usr/bin/env python3
from kad import DHT
import shelve
from flask import Flask

app = Flask(__name__)
host1, port1 = 'localhost', 3000
host2, port2 = 'localhost', 3001


def get_saved_peers(filename):
    peer_list = []
    with open(filename, 'r') as peers:
        for line in peers:
            peer = line.split(" ")
            peer[1] = int(peer[1])
            peer_list.append(tuple(peer))

    return peer_list


@app.route("/")
def hello():

    print(remoteDHT["my_key"])	 # blocking get
    remoteDHT.get("my_key", lambda data: print(data))  # threaded get

    return "Shadilay! fellow kekistani enjoy your"\
           " pepes {}".format(remoteDHT["my_key"])


# the storage parameter allows us to cache the keys locally and persistently
localDHT = DHT(host1, port1)

# seeds is a list of tuples (host, port), which contains the bootstrap
# nodes for our dht, we should load them from a file and update the at
# every once in while
remoteDHT = DHT(host2, port2, seeds=[(host1, port1)])

localDHT["my_key"] = [u"Timestap",
                      u"hash",
                      u"Object"]
# Returns your peers
peers = localDHT.peers()

if __name__ == "__main__":
    app.run(port=8080, debug=True)
