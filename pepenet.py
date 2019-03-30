#!/usr/bin/env python3
import ipfsapi
import os
import pepe
import socket
from flask import Flask, request, redirect, render_template
from werkzeug.utils import secure_filename
from argparse import ArgumentParser
import logging
from threading import Thread
from time import sleep

parser = ArgumentParser()
parser.add_argument('-H', default='localhost')
args = parser.parse_args()

ipfs_host = socket.gethostbyname(args.H)
ipfs_port = 5001
ipfs_web_port = 8080

flask_port = 8000

UPLOAD_FOLDER = 'tmp'
ALLOWED_EXTENSIONS = ('.txt', '.png', '.jpg', '.jpeg')

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ipfs = ipfsapi.connect(ipfs_host, ipfs_port)
pman = pepe.PepeMan(ipfs, ipfs_host)


def get_pepes():
    result = []
    for pepe_hash in pman.get_all_pepes():
        logging.debug("Showing: {}".format(pepe_hash))
        pepe = {"url": "http://{}:{}/ipfs/{}".format(ipfs_host,
                                                     ipfs_web_port,
                                                     pepe_hash),
                "normieness": "Calculating...",
                "hash": pepe_hash
                }
        result.append(pepe)
    return result


@app.route("/calc_normieness/<pepe_hash>")
def normieness_calc(pepe_hash):
    result = pman.calc_normieness(pepe_hash)
    return "{} ({})".format(*result)


@app.route("/")
def home_page():
    return render_template("main.html",
                           ipfs_info=ipfs.id(),
                           rare_pepes=get_pepes(),
                           peer_n=pman.get_peer_number(),
                           server=ipfs_host,
                           port=ipfs_port)


@app.route("/download/<pepe_hash>")
def download_file(pepe_hash):
    pman.pin_pepe(pepe_hash)
    return redirect('/')


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part', 400

    form_file = request.files['file']

    if form_file.filename == '':
        return 'No selected file', 400

    if form_file.filename.lower().endswith(ALLOWED_EXTENSIONS):
        filename = secure_filename(form_file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        form_file.save(file_path)
        pman.upload_pepe(file_path)

        # We delete the file because ipfs has copied it into its repository
        os.remove(file_path)
        return redirect('/')
    else:
        return 'Bad extension', 400


def save_pepes():
    while True:
        pman.save_pepes_lists()
        sleep(30)


if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s -'
                        '%(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    data_saver_thread = Thread(target=save_pepes)
    data_saver_thread.start()
    logging.debug("Flask path: {}".format(app.instance_path))
    app.run(port=flask_port, debug=True)
