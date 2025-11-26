# Configuration for Raspberry Pi Handheld OS

# ==========================================
# GPIO PIN CONFIGURATION
# ==========================================
# IMPORTANT: Update these pins based on your specific wiring!
# Refer to your "Google Gemini.pdf" for the correct pinout.

# Display (ST7789) - SPI Interface
# Using Standard SPI 0 (DIN=GPIO10, CLK=GPIO11)
PIN_DISPLAY_CS = 8   # SPI CE0
PIN_DISPLAY_DC = 25  # Data/Command
PIN_DISPLAY_RST = 27 # Reset
PIN_DISPLAY_BL = 18  # Backlight (PWM compatible)

# Rotary Encoder
PIN_ENCODER_CLK = 5  # Clock
PIN_ENCODER_DT = 6   # Data
PIN_ENCODER_SW = 13  # Switch (Push button)

# Haptics / Vibration Motor
PIN_HAPTIC = 26      # PWM or simple GPIO

# ==========================================
# DISPLAY SETTINGS
# ==========================================
DISPLAY_WIDTH = 240
DISPLAY_HEIGHT = 320
DISPLAY_ROTATION = 90 # 0, 90, 180, 270
DISPLAY_BAUDRATE = 24000000 # 24 MHz (Safe default)

# ==========================================
# UI THEME (Dark AMOLED Style)
# ==========================================
COLOR_BG = (0, 0, 0)          # Pure Black
COLOR_TEXT = (255, 255, 255)  # White
COLOR_ACCENT = (0, 255, 213)  # Cyan/Teal Neon
COLOR_HIGHLIGHT = (40, 40, 40) # Dark Gray for selection
COLOR_WARNING = (255, 50, 50) # Red

FONT_SIZE_SMALL = 14
FONT_SIZE_NORMAL = 18
FONT_SIZE_LARGE = 24
FONT_SIZE_TITLE = 32

# ==========================================
# SYSTEM SETTINGS
# ==========================================
ANIMATION_SPEED = 0.1 # Seconds
LONG_PRESS_TIME = 1.0 # Seconds for "Back" action
HAPTIC_DURATION_SHORT = 0.05
HAPTIC_DURATION_LONG = 0.2

# ==========================================
# HOME ASSISTANT CONFIGURATION
# ==========================================
HA_URL = "http://192.168.68.87:8123" # or IP address
HA_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiI3NGM5NDVmMDEwYzc0OGMzYmYyYmEwYjFmYWRkZTNhYSIsImlhdCI6MTc2NDE3ODYxMCwiZXhwIjoyMDc5NTM4NjEwfQ.5hrV3Lptc0CV4qtz74zBB28yqtV1RDCLQmgwViC_agk"

# ==========================================
# WEATHER CONFIGURATION (OpenWeatherMap)
# ==========================================
OWM_API_KEY = "2c5d6bd7405d3d0e285a5e7e35741191"
OWM_LAT = "44.184418" # New York (Example)
OWM_LON = "-77.403337"
OWM_UNITS = "metric" # metric or imperial
