FROM registry.cn-shanghai.aliyuncs.com/ale10bb/python:3.12-web-flask

# requirements for mirror
RUN pip install --no-cache-dir qiniu
# directory structure for nessus-mirror
WORKDIR /nessus-mirror
VOLUME /nessus-mirror/conf
COPY app.py .
COPY utils utils

ENTRYPOINT [ "gunicorn", "app:app" ]
CMD [ "--worker-class", "gevent", "--capture-output", "--bind", ":9090"]