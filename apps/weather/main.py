import time
import threading
import requests
import config
from PIL import ImageDraw

class App:
    def __init__(self, display, input_manager):
        self.display = display
        self.input = input_manager
        self.running = True
        
        self.weather_data = None
        self.loading = True
        self.error = None
        self.last_update = 0
        
        # Start fetch in background
        self.fetch_thread = threading.Thread(target=self.fetch_weather)
        self.fetch_thread.daemon = True
        self.fetch_thread.start()

    def fetch_weather(self):
        self.loading = True
        self.error = None
        
        if config.OWM_API_KEY == "YOUR_OWM_API_KEY":
            self.error = "API Key Missing"
            self.loading = False
            return

        try:
            url = f"https://api.openweathermap.org/data/2.5/weather?lat={config.OWM_LAT}&lon={config.OWM_LON}&appid={config.OWM_API_KEY}&units={config.OWM_UNITS}"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                self.weather_data = response.json()
                self.last_update = time.time()
                
                # Update Global Config for Status Bar
                temp = self.weather_data['main']['temp']
                unit = "C" if config.OWM_UNITS == "metric" else "F"
                config.WEATHER_TEMP = f"{int(temp)}°{unit}"
            else:
                self.error = f"Error: {response.status_code}"
        except Exception as e:
            self.error = "Network Error"
            print(f"Weather Fetch Error: {e}")
        
        self.loading = False

    def update(self):
        # Auto-refresh every 30 minutes
        if time.time() - self.last_update > 1800 and not self.loading and not self.error:
            self.fetch_thread = threading.Thread(target=self.fetch_weather)
            self.fetch_thread.daemon = True
            self.fetch_thread.start()

    def draw(self):
        draw = self.display.get_draw()
        draw.rectangle((0, 0, config.DISPLAY_WIDTH, config.DISPLAY_HEIGHT), fill=config.COLOR_BG)
        
        if self.loading:
            draw.text((80, 140), "Loading...", fill=config.COLOR_TEXT)
            return
            
        if self.error:
            draw.text((20, 100), "Weather Error", fill=config.COLOR_WARNING)
            draw.text((20, 130), self.error, fill=config.COLOR_TEXT)
            if "API Key" in self.error:
                draw.text((20, 160), "Check config.py", fill="gray")
            draw.text((50, 240), "Press Select to Retry", fill="gray")
            return

        if self.weather_data:
            # Parse Data
            temp = self.weather_data['main']['temp']
            desc = self.weather_data['weather'][0]['description'].title()
            humidity = self.weather_data['main']['humidity']
            wind = self.weather_data['wind']['speed']
            city = self.weather_data['name']
            
            # Draw
            # City
            draw.text((20, 20), city, fill=config.COLOR_ACCENT)
            
            # Temp (Large)
            unit = "C" if config.OWM_UNITS == "metric" else "F"
            temp_str = f"{int(temp)}°{unit}"
            # Use a large font if possible, or scale up
            # We don't have a huge font loaded in UI, but we can try default large
            # Or draw it manually/pixelated?
            # Let's just use the standard large font for now.
            draw.text((20, 60), temp_str, fill="white", font=None) # Default font is small
            # To make it bigger without loading a new font file (which might fail), 
            # we can't easily do it with default PIL font.
            # But we have `core.ui.load_font`. We can't access it easily here without importing UI.
            # Let's import it.
            from core.ui import load_font
            font_huge = load_font(60, bold=True)
            font_large = load_font(24)
            
            draw.text((20, 50), temp_str, font=font_huge, fill="white")
            
            # Condition
            draw.text((20, 130), desc, font=font_large, fill=config.COLOR_ACCENT)
            
            # Details
            draw.text((20, 180), f"Humidity: {humidity}%", fill="gray")
            draw.text((20, 210), f"Wind: {wind} m/s", fill="gray")
            
            # Last Update
            t_str = time.strftime("%H:%M", time.localtime(self.last_update))
            draw.text((20, 280), f"Updated: {t_str}", fill="gray")

    def handle_input(self, event):
        if event == 'back':
            return False
        elif event == 'select':
            if not self.loading:
                self.fetch_thread = threading.Thread(target=self.fetch_weather)
                self.fetch_thread.daemon = True
                self.fetch_thread.start()
        return True
