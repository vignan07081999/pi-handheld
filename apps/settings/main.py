import time
import subprocess
import os
import config
from core.ui import Menu, Keyboard
from core import highscore

class App:
    def __init__(self, display, input_manager):
        self.display = display
        self.input = input_manager
        self.running = True
        self.mode = "menu"
        self.wifi_networks = []
        self.selected_ssid = ""
        
        self.main_menu = Menu([
            {'label': 'WiFi', 'action': lambda: self.set_mode('wifi_scan')},
            {'label': 'Highscores', 'action': lambda: self.set_mode('highscores')},
            {'label': 'About', 'action': lambda: self.set_mode('about')},
            {'label': 'Reboot', 'action': self.reboot},
            {'label': 'Shutdown', 'action': self.shutdown}
        ], title="Settings")
        
        self.keyboard = Keyboard(self.on_keyboard_done)

    def set_mode(self, mode):
        self.mode = mode
        # No need to register callbacks anymore!
        
        if mode == 'wifi_scan':
            self.scan_wifi()
        elif mode == 'wifi_password':
            self.keyboard.activate()

    def scan_wifi(self):
        # Simulate or Real Scan
        self.wifi_networks = []
        if self.input.simulate:
            self.wifi_networks = ["Home WiFi", "Guest WiFi", "Neighbor"]
        else:
            try:
                # Use nmcli
                cmd = "nmcli -t -f SSID dev wifi list"
                output = subprocess.check_output(cmd, shell=True).decode('utf-8')
                self.wifi_networks = [line for line in output.split('\n') if line]
                self.wifi_networks = list(set(self.wifi_networks)) # Dedup
            except:
                self.wifi_networks = ["Scan Failed"]

        # Create Menu for Networks
        items = []
        for ssid in self.wifi_networks:
            items.append({
                'label': ssid,
                'action': lambda s=ssid: self.select_wifi(s)
            })
        self.wifi_menu = Menu(items, title="Select WiFi")

    def select_wifi(self, ssid):
        self.selected_ssid = ssid
        self.set_mode('wifi_password')

    def on_keyboard_done(self, text):
        password = text
        print(f"Connecting to {self.selected_ssid} with {password}")
        # Connect logic here (nmcli)
        if not self.input.simulate:
            try:
                subprocess.run(f"nmcli dev wifi connect '{self.selected_ssid}' password '{password}'", shell=True)
            except:
                pass
        self.set_mode('menu')

    def reboot(self):
        if not self.input.simulate:
            os.system("sudo reboot")
        else:
            print("Simulated Reboot")

    def shutdown(self):
        if not self.input.simulate:
            os.system("sudo shutdown now")
        else:
            print("Simulated Shutdown")

    def handle_input(self, event):
        if self.mode == 'menu':
            if event == 'left': self.main_menu.move_selection(-1)
            elif event == 'right': self.main_menu.move_selection(1)
            elif event == 'select': self.main_menu.select_current()
            elif event == 'back': return False # Exit App
            
        elif self.mode == 'wifi_scan':
            if hasattr(self, 'wifi_menu'):
                if event == 'left': self.wifi_menu.move_selection(-1)
                elif event == 'right': self.wifi_menu.move_selection(1)
                elif event == 'select': self.wifi_menu.select_current()
            if event == 'back': 
                self.set_mode('menu')
                return True # Consumed
            
        elif self.mode == 'wifi_password':
            if event == 'left': self.keyboard.move_selection(-1)
            elif event == 'right': self.keyboard.move_selection(1)
            elif event == 'select': self.keyboard.select_current()
            elif event == 'back': 
                self.keyboard.backspace()
                # If empty and back pressed? Go back?
                if len(self.keyboard.text) == 0:
                    self.set_mode('wifi_scan')
                return True
            
        elif self.mode == 'highscores' or self.mode == 'about':
            if event == 'back': 
                self.set_mode('menu')
                return True

        return False # Default: Not handled

    def update(self):
        if self.mode == 'menu':
            self.main_menu.update()
        elif self.mode == 'wifi_scan' and hasattr(self, 'wifi_menu'):
            self.wifi_menu.update()

    def draw(self):
        draw = self.display.get_draw()
        draw.rectangle((0, 0, config.DISPLAY_WIDTH, config.DISPLAY_HEIGHT), fill=config.COLOR_BG)
        
        if self.mode == 'menu':
            self.main_menu.draw(draw)
            
        elif self.mode == 'wifi_scan':
            if hasattr(self, 'wifi_menu'):
                self.wifi_menu.draw(draw)
            else:
                draw.text((80, 140), "Scanning...", fill=config.COLOR_TEXT)
                
        elif self.mode == 'wifi_password':
            self.keyboard.draw(draw)
            draw.text((20, 40), f"Pass for {self.selected_ssid}", fill=config.COLOR_TEXT)
            draw.text((20, 280), "Hold Select to OK", fill=(100, 100, 100)) # Hint
            
        elif self.mode == 'highscores':
            scores = highscore.load_highscores()
            y = 40
            draw.text((80, 10), "HIGHSCORES", font=self.main_menu.title_font, fill=config.COLOR_ACCENT)
            for game, score in scores.items():
                draw.text((40, y), f"{game.title()}: {score}", font=self.main_menu.font, fill=config.COLOR_TEXT)
                y += 30
            draw.text((60, 280), "Back to Return", fill=(100, 100, 100))

        elif self.mode == 'about':
            draw.text((80, 20), "ABOUT", font=self.main_menu.title_font, fill=config.COLOR_ACCENT)
            draw.text((20, 60), "Pi Handheld OS v1.0", fill=config.COLOR_TEXT)
            draw.text((20, 90), "Python Based OS", fill=config.COLOR_TEXT)
            draw.text((20, 120), "Created by Gemini", fill=config.COLOR_TEXT)
