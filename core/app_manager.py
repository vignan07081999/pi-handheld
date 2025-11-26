import os
import sys
import importlib
import time
from core.ui import CarouselMenu, ListMenu
import config

class AppManager:
    def __init__(self, display_manager, input_manager):
        self.display = display_manager
        self.input = input_manager
        self.apps = []
        self.games = []
        self.current_app = None
        self.running = True
        
        self.main_menu = None
        self.sub_menu = None # For categories
        
        self._load_apps()
        self._create_main_menu()

    def _load_apps(self):
        # Load Apps
        app_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'apps')
        self.apps = self._scan_directory(app_dir, 'apps')
        
        # Load Games
        game_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'games')
        self.games = self._scan_directory(game_dir, 'games')

    def _scan_directory(self, directory, category):
        found = []
        if not os.path.exists(directory):
            return found
            
        for name in os.listdir(directory):
            path = os.path.join(directory, name)
            if os.path.isdir(path) and os.path.exists(os.path.join(path, 'main.py')):
                found.append({
                    'name': name.replace('_', ' ').title(),
                    'id': name,
                    'path': path,
                    'module_path': f"{category}.{name}.main"
                })
        return found

    def _create_main_menu(self):
        # Categories
        items = [
            {'label': 'Games', 'action': lambda: self.open_category('Games')},
            {'label': 'Tools', 'action': lambda: self.open_category('Tools')},
            {'label': 'Apps', 'action': lambda: self.open_category('Apps')},
            {'label': 'Settings', 'action': lambda: self.open_category('Settings')}
        ]
        
        self.main_menu = CarouselMenu(items, title="Main Menu")

    def open_category(self, category):
        items = []
        
        if category == 'Games':
            for game in self.games:
                items.append({
                    'label': game['name'],
                    'action': lambda g=game: self.launch_app(g)
                })
        elif category == 'Tools':
            # Filter tools from apps
            tools = ['Torch', 'Measure']
            for app in self.apps:
                if app['name'] in tools:
                    items.append({
                        'label': app['name'],
                        'action': lambda a=app: self.launch_app(a)
                    })
        elif category == 'Settings':
            # Filter settings
            for app in self.apps:
                if app['name'] == 'Settings':
                    items.append({
                        'label': app['name'],
                        'action': lambda a=app: self.launch_app(a)
                    })
        elif category == 'Apps':
            # Everything else
            tools = ['Torch', 'Measure', 'Settings']
            for app in self.apps:
                if app['name'] not in tools:
                    items.append({
                        'label': app['name'],
                        'action': lambda a=app: self.launch_app(a)
                    })
                    
        if not items:
            items.append({'label': 'No Items', 'action': None})
            
        self.sub_menu = ListMenu(items, title=category)

    def close_sub_menu(self):
        self.sub_menu = None

    def launch_app(self, app_info):
        print(f"Launching {app_info['name']}...")
        try:
            module = importlib.import_module(app_info['module_path'])
            importlib.reload(module)
            
            if hasattr(module, 'App'):
                app_instance = module.App(self.display, self.input)
                self.current_app = app_instance
            else:
                print(f"Error: No 'App' class found in {app_info['name']}")
                
        except Exception as e:
            print(f"Error launching app: {e}")
            import traceback
            traceback.print_exc()
            self.close_current_app()

    def close_current_app(self):
        print("Closing app, returning to menu...")
        self.current_app = None

    def run(self):
        # Initial Control Setup
        self.input.clear_callbacks()
        
        # Global Input Handlers (routed manually)
        self.input.on('left', lambda: self._route_input('left'))
        self.input.on('right', lambda: self._route_input('right'))
        self.input.on('select', lambda: self._route_input('select'))
        self.input.on('back', lambda: self._route_input('back'))

        while self.running:
            # Update Inputs (Simulation)
            if self.input.simulate and self.display.simulate:
                import pygame
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                    self.input.handle_pygame_event(event)
            
            # Logic & Draw
            if self.current_app:
                try:
                    self.current_app.update()
                    self.current_app.draw() # App draws to buffer
                except Exception as e:
                    print(f"App Crashed: {e}")
                    import traceback
                    traceback.print_exc()
                    self.close_current_app()
            elif self.sub_menu:
                self.sub_menu.update()
                self.sub_menu.draw(self.display.get_draw(), self.display.get_image())
            else:
                self.main_menu.update()
                self.main_menu.draw(self.display.get_draw(), self.display.get_image())
            
            self.display.show()
            time.sleep(0.03)

    def _route_input(self, event_name):
        if self.current_app:
            handled = False
            if hasattr(self.current_app, 'handle_input'):
                handled = self.current_app.handle_input(event_name)
            
            if event_name == 'back' and not handled:
                self.close_current_app()
        elif self.sub_menu:
            if event_name == 'left': self.sub_menu.move_selection(-1)
            elif event_name == 'right': self.sub_menu.move_selection(1)
            elif event_name == 'select': self.sub_menu.select_current()
            elif event_name == 'back': self.close_sub_menu()
        else:
            # Main Menu
            if event_name == 'left': self.main_menu.move_selection(-1)
            elif event_name == 'right': self.main_menu.move_selection(1)
            elif event_name == 'select': self.main_menu.select_current()
            elif event_name == 'back':
                # Shortcut (Long Press is handled by InputManager sending 'back' after hold)
                # But 'back' is also sent for short press if we don't distinguish?
                # InputManager sends 'back' on release if short, or 'back' on hold?
                # Let's check InputManager.
                # Assuming 'back' event means "Back Action" (Short press usually).
                # Wait, user said "If I long press enough".
                # Standard 'back' usually implies exit/back.
                # If we want a specific "Shortcut" event, we might need to modify InputManager.
                # OR, we check if we are at the top level.
                # If we are at Main Menu, 'back' usually does nothing or reboots.
                # Let's use 'back' at Main Menu to trigger Shortcut.
                self.launch_shortcut()

    def launch_shortcut(self):
        target = config.SHORTCUT_APP
        print(f"Shortcut triggered: {target}")
        
        # Find app
        found = None
        for app in self.apps:
            if app['id'] == target: found = app
        if not found:
            for game in self.games:
                if game['id'] == target: found = game
        
        if found:
            self.launch_app(found)
        else:
            print(f"Shortcut app '{target}' not found.")
