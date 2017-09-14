#!/usr/bin/env python3
import ipfsapi
import ipfs_pubsub
from os import walk
import pepe
from flask import Flask
from flask import render_template
import logging

ipfs_host = "localhost"
ipfs_port = "5001"

app = Flask(__name__)
ipfs = ipfsapi.connect(ipfs_host, ipfs_port)

theme = "default"

html = {}

pepe1 = {"url": "https://media4.s-nbcnews.com/j/msnbc/components/video/201609/a_ov_pepe_160928.nbcnews-ux-1080-600.jpg",
        "normieness": 1,
        "hash": ""
        }


def generate_pepes():
    "Used for debugging"
    result = []
    for i in range(100):
        result.append(pepe1)
    return result


@app.route('/pepe/fetch/<id_hash>')
def fetch_pepe(id_hash):
    pass


@app.route("/")
def home_page():
    return render_template("default/main.html",
                           ipfs_info=ipfs.id(),
                           rare_pepes=generate_pepes())


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    logging.debug("Flask path: {}".format(app.instance_path))
    app.run(port=8000, debug=True)
