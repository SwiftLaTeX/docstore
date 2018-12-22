from flask import Flask, request, jsonify, send_file
import io
import os
import mimetypes
from flask_pymongo import PyMongo
from mongofs import MongoDBFileSystem
import config
import string_utils
import time
app = Flask(__name__)
app.config.from_object(__name__)
app.config["MONGO_URI"] = config.DB_URL
mongo = PyMongo(app)
filesystem = MongoDBFileSystem(mongo)

def verify_access_key():
    s_token = request.headers.get('S-TOKEN', "00000000000000000000000000000000")
    if isinstance(s_token, str) and s_token == config.ACCESS_KEY:
        return True
    return False


@app.route('/')
def index():
    return "Docstore v0.1. Happily storing %d files." % filesystem.file_count()

@app.route('/<path:path>', methods=["GET", "POST", "DELETE", "PUT"])
def main_entry(path):

    if not string_utils.is_valid_pidurl(path):
        return jsonify({'result': 'failed', 'reason': 'unsupported url'}), 500

    pid, url = string_utils.split_pidurl(path)

    if request.method == "GET":
        return download_file(pid, url)
    else:
        if not verify_access_key():
            return jsonify({'result': 'failed', 'reason': 'access denied'}), 500
        if request.method == "POST":
            return access_file(pid, url)
        elif request.method == "DELETE":
            return delete_file(pid, url)
        elif request.method == "PUT":
            return upload_file(pid, url)

    return jsonify({'result':'failed', 'reason':'unsupported operation'}), 500


def download_file(pid, url):
    expire_time = request.args.get("expire", "")
    signed = request.args.get("signed", "")
    if expire_time == "":
        return jsonify({'result': 'failed', 'reason': 'incorrect expire time'}), 500

    if string_utils.hash_with_prefix(expire_time, config.HMAC_KEY) != signed:
        return jsonify(
            {'result': 'failed', 'reason': 'unable to verify signature'}), 500

    if abs(int(expire_time) - time.time()) > 3600:
        if expire_time == "":
            return jsonify({'result': 'failed',
                            'reason': 'file expired'}), 500

    data = filesystem.read(pid, url)
    if data is None:
        return jsonify({'result': 'failed',
                            'reason': 'no such file'}), 500

    return send_file(
        io.BytesIO(data),
        attachment_filename=os.path.basename(url),
        mimetype=mimetypes.guess_type(url)[0]
    )


def access_file(pid, url):
    operation = request.form.get('op', "")
    if not isinstance(operation, str) or (operation != "list" and operation != "rename"):
        return jsonify({'result': 'failed', 'reason': 'unsupported operation'}), 500

    if operation == "list":
        items = filesystem.readtree(pid, url)
        return jsonify({'result': 'ok', 'data':items, 'pid': pid, 'url': url})
    else:
        newpath = request.form.get('newpath', "")
        if not isinstance(newpath, str) or newpath == "":
            return jsonify({'result': 'failed', 'reason': 'no name provided'}), 500
        if not filesystem.rename(pid, url, newpath):
            return jsonify({'result': 'failed', 'reason': 'rename failed'}), 500
        return jsonify({'result': 'ok', 'pid': pid, 'url': newpath})



def delete_file(pid, url):
    if not filesystem.delete(pid, url):
        return jsonify({'result': 'failed', 'reason': 'unable to delete the selected file'}), 500
    return jsonify({'result': 'ok', 'pid':  pid, 'url': url})


def upload_file(pid, url):

    is_dir = False
    if 'file' not in request.files:
        is_dir = True

    if not is_dir:
        file = request.files['file']
        if file.filename == '':
            return jsonify({'result': 'failed', 'reason': 'no file provided'}), 500
        if not filesystem.write(pid, url, file.read()):
            return jsonify({'result': 'failed', 'reason': 'unable to write file'}), 500
    else:
        if not filesystem.mkdir(pid, url):
            return jsonify({'result': 'failed', 'reason': 'unable to mkdir dir'}), 500

    return jsonify({'result': 'ok', 'pid': pid, 'url': url})

if __name__ == '__main__':
    app.run(debug=True)
