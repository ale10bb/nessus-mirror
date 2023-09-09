# -*- coding: UTF-8 -*-
import os
from configparser import ConfigParser
from flask import Flask, request, g
import requests

config = ConfigParser()
config.read(os.path.join("conf", "mirror.conf"), encoding="UTF-8")
wxwork_url = config.get("wxwork", "url", fallback="http://127.0.0.1:9080")

app = Flask("mirror")
app.logger.setLevel("INFO")


@app.before_request
def before_request():
    g.user = request.host.split(".")[0]
    app.logger.debug('%s: "%s %s"', g.user, request.method, request.path)


@app.post("/login")
def login():
    app.logger.info(
        '%s: "%s %s" %s', g.user, request.method, request.path, dict(request.values)
    )
    return ""


@app.post("/plugins/process")
def plugins_process():
    app.logger.info(
        '%s: "%s %s" %s', g.user, request.method, request.path, dict(request.values)
    )
    msg = f"====== Info ======\n\nPath: /plugins/process\nFile: {request.form['filename']}\nComment: 已开始本地更新，可关闭工具并等待Nessus自动重启"
    requests.post(
        f"{wxwork_url}/message/send/nessus", json={"to": g.user, "content": msg}
    )
    return ""


@app.post("/file/upload")
def file_upload():
    app.logger.info(
        '%s: "%s %s" %s', g.user, request.method, request.path, dict(request.values)
    )
    msg = f"====== Info ======\n\nPath: /file/upload\nFile: {request.files['Filedata'].filename}\nSize: {request.content_length/1048576:.2f}MB\nComment: 开始上传"
    app.logger.info('filename: "{}"'.format(request.files["Filedata"].filename))
    if not os.path.exists("storage"):
        os.mkdir("storage")
    if (
        not os.path.exists(os.path.join("storage", "all-2.0.tar.gz"))
        and request.files["Filedata"].filename == "all-2.0.tar.gz"
    ):
        app.logger.info('saving "all-2.0.tar.gz"')
        request.files["Filedata"].save(os.path.join("storage", "all-2.0.tar.gz"))
    requests.post(
        f"{wxwork_url}/message/send/nessus", json={"to": g.user, "content": msg}
    )
    return ""


if __name__ == "__main__":
    app.run(debug=True)
