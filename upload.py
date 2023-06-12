# -*- coding: UTF-8 -*-
from configparser import ConfigParser
import os
import tarfile
from qiniu import Auth, BucketManager, CdnManager, put_file
import base64
import requests

file_path = 'storage/all-2.0.tar.gz'
assert os.path.exists(file_path)

# 尝试获取bucket的绑定域名
config = ConfigParser()
config.read('mirror.conf', encoding='UTF-8')
auth = Auth(config.get('qiniu', 'ak', fallback=''), config.get('qiniu', 'sk', fallback=''))
bucket = config.get('qiniu', 'bucket', fallback='')
bucket_domain = config.get('qiniu', 'bucket_domain', fallback='')
key = 'nessus/all-2.0.tar.gz'
try:
    ret, info = BucketManager(auth).stat(bucket, key)
    remote_plugin_set = ret['x-qn-meta']['Plugin-Set']
except:
    remote_plugin_set = '197001010000'
print(f"remote plugin_set: {remote_plugin_set}")

# 目前(2021.09.14)完整包大概在300MB左右，按照阿里云5Mbps的上传速度，大约需要上传500秒
print('reading all-2.0.tar.gz...')
# 检测完整包是否较新，是则覆盖上传七牛云
with tarfile.open(file_path, 'r:gz') as f:
    with f.extractfile('plugin_feed_info.inc') as info:
        local_plugin_set = ''
        while True:
            line = info.readline().decode('utf-8')
            if not line:
                break
            if 'PLUGIN_SET' in line:
                local_plugin_set = line.split('"')[1]
                break
assert local_plugin_set, 'failed to read plugin_set'
print(f"local plugin_set: {local_plugin_set}")

assert local_plugin_set > remote_plugin_set, 'local plugin_set outdated'

token = auth.upload_token(bucket, key)
print('qiniu.put_file() start')
ret, info = put_file(token, key, file_path)
print('qiniu.put_file() complete')
print(f"ret: {ret}")
# SDK未提供修改元数据的API，在此手动设置Plugin-Set
print('setting x-qn-meta...')
path = '/chgm/{}/x-qn-meta-Plugin-Set/{}'.format(
    base64.b64encode(f"{bucket}:{key}".encode('utf-8')).decode('utf-8'),
    base64.b64encode(local_plugin_set.encode('utf-8')).decode('utf-8')
)
accessToken = auth.token(f"POST {path}\nHost: rs.qbox.me\nContent-Type: application/x-www-form-urlencoded\n\n")
r = requests.post(f"https://rs.qbox.me{path}", 
    headers={
        'Content-Type': 'application/x-www-form-urlencoded', 
        'Authorization': f"Qiniu {accessToken}",
    }
)
print(f"ret: {r.text}")
if remote_plugin_set != '197001010000':
    # 主动刷新CDN的缓存，否则gzip文件将被缓存30天
    print('refreshing cdn...')
    urls = [f"http://{bucket_domain}/{key}"]
    ret, info = CdnManager(auth).refresh_urls(urls)
    print(f"ret: {ret}")

os.remove(file_path)
