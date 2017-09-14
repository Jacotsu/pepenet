#!/usr/bin/env python3
import ipfsapi
import os
import pepe
from flask import Flask, request, redirect, render_template, flash
from werkzeug.utils import secure_filename
import logging
import atexit

ipfs_host = "localhost"
ipfs_port = "5001"

UPLOAD_FOLDER = 'static/rare_pepes'
ALLOWED_EXTENSIONS = set(['txt', 'png', 'jpg', 'jpeg'])

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ipfs = ipfsapi.connect(ipfs_host, ipfs_port)
pman = pepe.PepeMan(ipfs)

theme = "default"

html = {}

pepe1 = {"url": "https://media4.s-nbcnews.com/j/msnbc/components/video/201609"
         "/a_ov_pepe_160928.nbcnews-ux-1080-600.jpg",
         "normieness": 1,
         "hash": ""
         }


def generate_pepes():
    "Used for debugging"
    result = []
    for i in range(100):
        result.append(pepe1)
    return result


def get_pepes():
    result = []
    for i in pman.get_all_pepes():
        logging.debug("Showing: {}".format(i))
        pepe = {"url": "http://{}:{}/ipfs/{}".format(ipfs_host, 8080, i),
                "normieness": 1,
                "hash": i
                }
        result.append(pepe)
    return result


@app.route('/pepe/fetch/<id_hash>')
def fetch_pepe(id_hash):
    pass


@app.route("/555")
def home_page():
    return render_template("default/main.html",
                           ipfs_info=ipfs.id(),
                           rare_pepes=generate_pepes(),
                           peer_n=pman.get_peer_number())


@app.route("/")
def home_page_deb():
    return render_template("default/main.html",
                           ipfs_info=ipfs.id(),
                           rare_pepes=get_pepes(),
                           peer_n=pman.get_peer_number(),
                           server=ipfs_host,
                           port=ipfs_port)


def get_pinned_pepes(hash_list):
    pepes = []
    for pepe_hash in hash_list:
        pman.get_pepe(pepe_hash)
        pepe = {"url": "./{}".format(pepe_hash),
                "normieness": 1,
                "hash": ""
                }
        pepes.append(pepe)

    return pepes


@app.route("/pinned_pepes")
def pinned_pepes_page():
    return render_template("default/main.html",
                           ipfs_info=ipfs.id(),
                           rare_pepes=get_pinned_pepes(pman.ls_pinned_pepes()))


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/pepe_upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            pman.upload_pepe(os.path.join(app.config['UPLOAD_FOLDER'],
                                          filename))
            return "File uploaded"

    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    '''


def close_running_threads():
    pman.save_pepes_lists()


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    atexit.register(close_running_threads)
    logging.debug("Flask path: {}".format(app.instance_path))
    app.run(port=8000, debug=True)
