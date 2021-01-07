# This is a sample Python script.
import os
import json
from pathlib import Path
from flask import Flask, request, render_template
import paho.mqtt.client as mqtt

config_path = os.getenv('CONFIG_PATH')
if not config_path:
    base_path = Path(__file__).parent
    if os.path.isfile(base_path / 'config.json'):
        config_path = base_path / 'config.json'
    elif os.path.isfile(base_path / 'config.default.json'):
        config_path = base_path / 'config.default.json'
    else:
        print('Couldn\'t find config file.')
        exit(1)

config = None
if os.path.isfile(config_path):
    with open(config_path, 'r') as file:
        config = json.load(file)

app = Flask(__name__)

for endpoint in config['endpoints']:
    def view_func():
        result = render_template(endpoint['template'], **{**(request.json or {}), **endpoint['variables']})
        client.publish(endpoint['topic'], result)
        return 'OK'

    app.add_url_rule(endpoint['rule'], None, view_func)


client = mqtt.Client(config['mqtt']['client_id'])


def on_connect(client: mqtt.Client, userdata, flags, rc):
    print('Connected with result code '+str(rc))


client.on_connect = on_connect
client.loop_start()
if 'username' in config['mqtt']:
    client.username_pw_set(config['mqtt']['username'], config['mqtt']['password'])
if config['mqtt']['tls']:
    client.tls_set()
client.connect(config['mqtt']['host'], config['mqtt']['port'] or 1883, 60)

print('Good morning! \\(^o^)/')
