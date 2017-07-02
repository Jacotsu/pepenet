#!/usr/bin/env python3
import ipfsapi
import ipfs_pubsub
from flask import Flask

ipfs_host = "localhost"
ipfs_port = "5001"

app = Flask(__name__)
ipfs = ipfsapi.connect(ipfs_host, ipfs_port)


@app.route("/")
def hello():
    return "Shadilay! fellow kekistani enjoy your"\
           " pepes {}".format(ipfs.id())


if __name__ == "__main__":
    app.run(port=8080, debug=True)
