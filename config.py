# Configuration for Raspberry Pi Handheld OS
import json
import os

# ==========================================
# GPIO PIN CONFIGURATION
# ==========================================
PIN_DISPLAY_CS = 8
PIN_DISPLAY_DC = 25
PIN_DISPLAY_RST = 27
PIN_DISPLAY_BL = 18
PIN_ENCODER_CLK = 5
PIN_ENCODER_DT = 6
PIN_ENCODER_SW = 13
PIN_HAPTIC = 26

# ==========================================
# DISPLAY SETTINGS
# ==========================================
DISPLAY_WIDTH = 240
DISPLAY_HEIGHT = 320
DISPLAY_ROTATION = 90
DISPLAY_BAUDRATE = 24000000

# ==========================================
# UI THEME
# ==========================================
COLOR_BG = (0, 0, 0)
COLOR_TEXT = (255, 255, 255)
COLOR_ACCENT = (0, 255, 213)
COLOR_HIGHLIGHT = (40, 40, 40)
COLOR_WARNING = (255, 50, 50)

FONT_SIZE_SMALL = 14
FONT_SIZE_NORMAL = 18
FONT_SIZE_LARGE = 24
FONT_SIZE_TITLE = 32

# ==========================================
# SYSTEM SETTINGS
# ==========================================
ANIMATION_SPEED = 0.1
LONG_PRESS_TIME = 1.0
HAPTIC_DURATION_SHORT = 0.05
HAPTIC_DURATION_LONG = 0.2

# ==========================================
# DYNAMIC CONFIGURATION (Load from JSON)
# ==========================================
CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'config.json')

def load_config():
    defaults = {
        "ha_url": "http://homeassistant.local:8123",
        "ha_token": "",
        "ha_entities": [],
        "owm_api_key": "",
        "owm_lat": "0",
        "owm_lon": "0",
        "owm_units": "metric",
        "wifi_ssid": "",
        "wifi_password": ""
    }
    
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                data = json.load(f)
                defaults.update(data)
        except Exception as e:
            print(f"Error loading config.json: {e}")
            
    return defaults

_config_data = load_config()

HA_URL = _config_data['ha_url']
HA_TOKEN = _config_data['ha_token']
HA_ENTITIES = _config_data['ha_entities']

OWM_API_KEY = _config_data['owm_api_key']
OWM_LAT = _config_data['owm_lat']
OWM_LON = _config_data['owm_lon']
OWM_UNITS = _config_data['owm_units']

WIFI_SSID = _config_data['wifi_ssid']
WIFI_PASSWORD = _config_data['wifi_password']

SHORTCUT_APP = _config_data.get('shortcut_app', 'torch')

def save_config(data):
    # Update global vars (for current session if needed, though restart is better)
    # Actually, apps should reload config or we should use a config object.
    # For now, we just save to file.
    current = load_config()
    current.update(data)
    with open(CONFIG_FILE, 'w') as f:
        json.dump(current, f, indent=4)
