import time
import requests
import threading
import config
from PIL import Image, ImageDraw

class App:
    def __init__(self, display, input_manager):
        self.display = display
        self.input = input_manager
        self.entities = []
        self.loading = True
        self.error = None
        
        # Grid State
        self.selected_index = 0
        self.cols = 2
        self.rows = 3 # Visible rows
        self.scroll_row = 0
        
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
                
                if config.HA_ENTITIES:
                    # Filter by selected list
                    self.entities = [
                        e for e in all_states 
                        if e['entity_id'] in config.HA_ENTITIES
                    ]
                else:
                    # Default behavior
                    self.entities = [
                        e for e in all_states 
                        if e['entity_id'].startswith('light.') or e['entity_id'].startswith('switch.')
                    ]
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
            
            # Optimistic update
            for e in self.entities:
                if e['entity_id'] == entity_id:
                    e['state'] = 'off' if current_state == 'on' else 'on'
                    break
            
            # Full Refresh later?
            # self.fetch_entities() 
            
        except Exception as e:
            print(f"Toggle Error: {e}")

    def update(self):
        pass

    def draw(self):
        draw = self.display.get_draw()
        draw.rectangle((0, 0, config.DISPLAY_WIDTH, config.DISPLAY_HEIGHT), fill=config.COLOR_BG)
        
        if self.loading:
            draw.text((80, 140), "Loading...", fill=config.COLOR_TEXT)
            return
        elif self.error:
            draw.text((20, 140), self.error, fill=config.COLOR_WARNING)
            draw.text((20, 160), "Check config.py", fill=config.COLOR_TEXT)
            return
            
        if not self.entities:
            draw.text((50, 140), "No Entities", fill="gray")
            return

        # Draw Grid
        margin = 10
        spacing = 10
        
        # Calculate cell size
        cell_w = (config.DISPLAY_WIDTH - (margin * 2) - (spacing * (self.cols - 1))) // self.cols
        cell_h = 90
        
        start_y = 10
        
        # Adjust scroll
        current_row = self.selected_index // self.cols
        if current_row < self.scroll_row:
            self.scroll_row = current_row
        elif current_row >= self.scroll_row + self.rows:
            self.scroll_row = current_row - self.rows + 1
            
        visible_start_idx = self.scroll_row * self.cols
        
        for i, entity in enumerate(self.entities):
            if i < visible_start_idx: continue
            if i >= visible_start_idx + (self.rows * self.cols): break
            
            # Grid Position
            grid_idx = i - visible_start_idx
            r = grid_idx // self.cols
            c = grid_idx % self.cols
            
            x = margin + c * (cell_w + spacing)
            y = start_y + r * (cell_h + spacing)
            
            is_selected = (i == self.selected_index)
            is_on = (entity['state'] == 'on')
            
            # Card Background
            bg_color = (40, 40, 40)
            if is_selected:
                outline_color = config.COLOR_ACCENT
            else:
                outline_color = (60, 60, 60)
                
            draw.rectangle((x, y, x + cell_w, y + cell_h), fill=bg_color, outline=outline_color, width=2 if is_selected else 1)
            
            # Icon / Indicator
            icon_color = "yellow" if is_on else "gray"
            cx = x + cell_w // 2
            cy = y + 35
            
            # Simple Bulb Icon
            draw.ellipse((cx-15, cy-15, cx+15, cy+15), fill=icon_color)
            draw.rectangle((cx-8, cy+15, cx+8, cy+25), fill="gray")
            
            # Name
            name = entity['attributes'].get('friendly_name', entity['entity_id'])
            # Truncate
            if len(name) > 12: name = name[:10] + ".."
            
            # Center text
            bbox = draw.textbbox((0, 0), name)
            tw = bbox[2] - bbox[0]
            draw.text((cx - tw // 2, y + cell_h - 25), name, fill="white")

    def handle_input(self, event):
        if self.loading or self.error:
            if event == 'back': return False
            return True
            
        if event == 'left':
            self.selected_index = max(0, self.selected_index - 1)
        elif event == 'right':
            self.selected_index = min(len(self.entities) - 1, self.selected_index + 1)
        elif event == 'select':
            if self.entities:
                e = self.entities[self.selected_index]
                self.toggle_entity(e['entity_id'], e['state'])
        elif event == 'back':
            return False
            
        return True
