import csv
import json
import re
import sys

import requests


def get(url):
    '''Request dataworld URL with authorization token.'''
    return requests.get(url, headers={
        'Authorization': 'Bearer ' + data_world_config['token']
    })


# Reading config file
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

data_world_config = config['data_world']
try:
    files = get(data_world_config['data_url']).json().get('files')
except Exception as e:
    sys.exit(e)

for file in files:
    if not (bool(file.get('name') and re.search("\.csv$", file['name']))):
        print('WARN: Expect a csv file from data world, receive ' + json.dumps(file))
        continue

    print('Asking for ' + file['name'])
    response = get(data_world_config['file_prefix'] + 'full_data.csv').content
    open('files/' + file['name'], 'w').write(response.decode('utf-8'))

print('Finished')
sys.exit(0)
