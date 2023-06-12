# -*- coding: UTF-8 -*-
import json
from configparser import ConfigParser

config = ConfigParser()
config.read('mirror.conf', encoding='UTF-8')

v2ray_config = {
    'reverse': {'portals': []}, 
    'inbounds': [{
        'tag': 'nessus', 
        'port': config.get('v2ray', 'port', fallback='8835'),
        'protocol': 'vmess',
        'settings': {'clients': [{'id': config.get('v2ray', 'id', fallback='')}]}
    }], 
    'outbounds': [{'protocol': 'freedom', 'tag': 'direct'}],
    'routing': {'rules': []}
}
for key, value in config['user'].items():
    v2ray_config['reverse']['portals'].append(
        {'tag': f"portal-{key}", 'domain': f"{key}.nessus-tunnel"}
    )
    v2ray_config['inbounds'].append({
        'tag': f"reverse-{key}",
        'port': value,
        'listen': '127.0.0.1',
        'protocol': 'dokodemo-door',
        'settings': {'address': 'nessus.local', 'port': 8834}
    })
    v2ray_config['routing']['rules'].append({
        'type': 'field',
        'inboundTag': [f"reverse-{key}"],
        'outboundTag': f"portal-{key}"
    })
    v2ray_config['routing']['rules'].append({
        'type': 'field',
        'inboundTag': ['nessus'],
        'domain': [f"full:{key}.nessus-tunnel"],
        'outboundTag': f"portal-{key}"
    })

with open('storage/config.json', 'w') as f:
    json.dump(v2ray_config, f)
with open('storage/users.conf', 'w') as f:
    f.writelines([f"{key}.{config.get('nginx', 'domain', fallback='')} {value};\n" for key, value in config['user'].items()])
