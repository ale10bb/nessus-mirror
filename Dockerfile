FROM registry.cn-shanghai.aliyuncs.com/ale10bb/python:3.11-web-flask

# directory structure for nessus-mirror
WORKDIR /nessus-mirror
VOLUME /nessus-mirror/storage
COPY app.py .

ENTRYPOINT [ "gunicorn", "app:app" ]
CMD [ "--worker-class", "gevent", "--capture-output", "--bind", ":9090"]