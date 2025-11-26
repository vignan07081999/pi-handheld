from flask import Flask, render_template, request, jsonify
import json
import os
import requests

app = Flask(__name__)

CONFIG_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.json')

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_config(data):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(data, f, indent=4)

@app.route('/', methods=['GET', 'POST'])
def index():
    config = load_config()
    
    if request.method == 'POST':
        config['ha_url'] = request.form.get('ha_url')
        config['ha_token'] = request.form.get('ha_token')
        config['owm_api_key'] = request.form.get('owm_api_key')
        config['owm_lat'] = request.form.get('owm_lat')
        config['owm_lon'] = request.form.get('owm_lon')
        config['wifi_ssid'] = request.form.get('wifi_ssid')
        config['wifi_password'] = request.form.get('wifi_password')
        config['shortcut_app'] = request.form.get('shortcut_app')
        
        # Selected Entities
        selected_entities = request.form.getlist('entities')
        config['ha_entities'] = selected_entities
        
        save_config(config)
        return render_template('index.html', config=config, message="Configuration Saved! Restart Pi to apply.")

    return render_template('index.html', config=config)

@app.route('/fetch_entities', methods=['POST'])
def fetch_entities():
    url = request.json.get('url')
    token = request.json.get('token')
    
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "content-type": "application/json",
        }
        response = requests.get(f"{url}/api/states", headers=headers, timeout=5)
        if response.status_code == 200:
            entities = response.json()
            # Filter useful ones
            filtered = [
                {'id': e['entity_id'], 'name': e['attributes'].get('friendly_name', e['entity_id'])}
                for e in entities 
                if e['entity_id'].split('.')[0] in ['light', 'switch', 'sensor', 'media_player', 'climate']
            ]
            return jsonify({'success': True, 'entities': filtered})
        else:
            return jsonify({'success': False, 'error': f"Status {response.status_code}"})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
