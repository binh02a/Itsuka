import csv
import json
import os
import re
import sys
from urllib.parse import quote_plus as url_encode

import requests


def get(url):
    '''Request dataworld URL with authorization token.'''
    return requests.get(url, headers={
        'Authorization': f'Bearer {token}'
    })


# Reading config file
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

# create data directory
category = 'suicide_by_age'
if not os.path.isdir(f'files/{category}'):
    os.makedirs(f'files/{category}')

token = config['data_world']['token']
data_world_config = config['data_world'][category]
try:
    files = get(data_world_config['data_url']).json().get('files')
except Exception as e:
    sys.exit(e)

for file in files:
    name = file.get('name')
    if not (bool(name) and re.search("\.csv$", name)):
        print('WARN: Expect a csv file from data world, receive %s' % json.dumps(file))
        continue

    # encode filename to escape spaces
    print('Asking for %s' % name)
    response = get(data_world_config['file_prefix'] + url_encode(name)).content
    open(f'files/{category}/{name}', 'w').write(response.decode('utf-8'))

print('Finished')
sys.exit(0)
