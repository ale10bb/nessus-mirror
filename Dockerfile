FROM registry.cn-shanghai.aliyuncs.com/ale10bb/python:3.11-web-flask

# requirements for mirror
RUN set -eux; \
        \
        pip install --no-cache-dir qiniu
# directory structure for nessus-mirror
WORKDIR /nessus-mirror
VOLUME /nessus-mirror/storage
COPY app.py .
COPY init.py .
COPY upload.py .

ENTRYPOINT [ "gunicorn", "app:app" ]
CMD [ "--worker-class", "gevent", "--capture-output", "--bind", ":9090"]