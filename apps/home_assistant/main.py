import time
import requests
import threading
import config
from core.ui import Menu

class App:
    def __init__(self, display, input_manager):
        self.display = display
        self.input = input_manager
        self.entities = []
        self.menu = None
        self.loading = True
        self.error = None
        
        # Start fetching in background
        threading.Thread(target=self.fetch_entities, daemon=True).start()

    def fetch_entities(self):
        self.loading = True
        self.error = None
        try:
            headers = {
                "Authorization": f"Bearer {config.HA_TOKEN}",
                "content-type": "application/json",
            }
            url = f"{config.HA_URL}/api/states"
            response = requests.get(url, headers=headers, timeout=5)
            
            if response.status_code == 200:
                all_states = response.json()
                self.entities = [
                    e for e in all_states 
                    if e['entity_id'].startswith('light.') or e['entity_id'].startswith('switch.')
                ]
                self.create_menu()
            else:
                self.error = f"Error: {response.status_code}"
        except Exception as e:
            self.error = f"Conn Error: {str(e)[:15]}"
        finally:
            self.loading = False

    def toggle_entity(self, entity_id, current_state):
        # Run in thread to not block UI
        threading.Thread(target=self._toggle_thread, args=(entity_id, current_state), daemon=True).start()

    def _toggle_thread(self, entity_id, current_state):
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
            
            # Refresh
            self.fetch_entities()
            
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

    def update(self):
        if self.menu and not self.loading:
            self.menu.update()

    def draw(self):
        draw = self.display.get_draw()
        draw.rectangle((0, 0, config.DISPLAY_WIDTH, config.DISPLAY_HEIGHT), fill=config.COLOR_BG)
        
        if self.loading:
            draw.text((80, 140), "Loading...", fill=config.COLOR_TEXT)
        elif self.error:
            draw.text((20, 140), self.error, fill=config.COLOR_WARNING)
            draw.text((20, 160), "Check config.py", fill=config.COLOR_TEXT)
        elif self.menu:
            self.menu.draw(draw, self.display.get_image())

    def handle_input(self, event):
        if self.loading:
            if event == 'back': return False
            return True
            
        if self.menu:
            if event == 'left': self.menu.move_selection(-1)
            elif event == 'right': self.menu.move_selection(1)
            elif event == 'select': self.menu.select_current()
            elif event == 'back': return False
            
        elif self.error:
             if event == 'back': return False
             
        return True
