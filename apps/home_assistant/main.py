import time
import requests
import config
from core.ui import Menu

class App:
    def __init__(self, display, input_manager):
        self.display = display
        self.input = input_manager
        self.running = True
        self.entities = []
        self.menu = None
        self.loading = True
        self.error = None

    def fetch_entities(self):
        try:
            headers = {
                "Authorization": f"Bearer {config.HA_TOKEN}",
                "content-type": "application/json",
            }
            url = f"{config.HA_URL}/api/states"
            response = requests.get(url, headers=headers, timeout=5)
            
            if response.status_code == 200:
                all_states = response.json()
                # Filter for lights and switches
                self.entities = [
                    e for e in all_states 
                    if e['entity_id'].startswith('light.') or e['entity_id'].startswith('switch.')
                ]
                self.create_menu()
                self.loading = False
            else:
                self.error = f"Error: {response.status_code}"
                self.loading = False
        except Exception as e:
            self.error = f"Conn Error: {str(e)[:15]}"
            self.loading = False

    def toggle_entity(self, entity_id, current_state):
        domain = entity_id.split('.')[0]
        service = "turn_off" if current_state == 'on' else "turn_on"
        
        try:
            headers = {
                "Authorization": f"Bearer {config.HA_TOKEN}",
                "content-type": "application/json",
            }
            url = f"{config.HA_URL}/api/services/{domain}/{service}"
            data = {"entity_id": entity_id}
            requests.post(url, headers=headers, json=data)
            
            # Optimistic update
            # Re-fetch or just update local state?
            # Let's re-fetch after a short delay or just update UI
            time.sleep(0.5)
            self.fetch_entities() # Refresh
            
        except Exception as e:
            print(f"Toggle Error: {e}")

    def create_menu(self):
        items = []
        for entity in self.entities:
            name = entity['attributes'].get('friendly_name', entity['entity_id'])
            state = entity['state']
            icon = "[X]" if state == 'on' else "[ ]"
            
            items.append({
                'label': f"{icon} {name}",
                'action': lambda e=entity: self.toggle_entity(e['entity_id'], e['state'])
            })
            
        if not items:
            items.append({'label': "No Devices Found", 'action': None})
            
        self.menu = Menu(items, title="Smart Home")

    def stop(self):
        self.running = False

    def run(self):
        # Initial Fetch
        self.fetch_entities()
        
        # Controls
        self.input.on('back', self.stop)
        
        while self.running:
            draw = self.display.get_draw()
            draw.rectangle((0, 0, config.DISPLAY_WIDTH, config.DISPLAY_HEIGHT), fill=config.COLOR_BG)
            
            if self.loading:
                draw.text((80, 140), "Loading...", fill=config.COLOR_TEXT)
            elif self.error:
                draw.text((20, 140), self.error, fill=config.COLOR_WARNING)
                draw.text((20, 160), "Check config.py", fill=config.COLOR_TEXT)
            elif self.menu:
                # Update menu controls if not set (lazy init)
                if not self.input.callbacks['left']:
                    self.input.on('left', lambda: self.menu.move_selection(-1))
                    self.input.on('right', lambda: self.menu.move_selection(1))
                    self.input.on('select', self.menu.select_current)
                
                self.menu.update()
                self.menu.draw(draw)
            
            self.display.show()
            
            if self.input.simulate:
                import pygame
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                    self.input.handle_pygame_event(event)
            
            time.sleep(0.05)
