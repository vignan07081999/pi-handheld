import os
import sys
import importlib
import time
from core.ui import Menu
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
        items = []
        
        # Apps Section
        for app in self.apps:
            items.append({
                'label': app['name'],
                'action': lambda a=app: self.launch_app(a)
            })
            
        # Games Section
        for game in self.games:
            items.append({
                'label': f"Game: {game['name']}",
                'action': lambda g=game: self.launch_app(g)
            })
            
        # Settings (Built-in)
        # items.append({'label': 'Settings', 'action': self.launch_settings})
        
        self.main_menu = Menu(items, title="Main Menu")

    def launch_app(self, app_info):
        print(f"Launching {app_info['name']}...")
        try:
            module = importlib.import_module(app_info['module_path'])
            importlib.reload(module)
            
            if hasattr(module, 'App'):
                app_instance = module.App(self.display, self.input)
                self.current_app = app_instance
                
                # Clear Input Callbacks for the App
                self.input.clear_callbacks()
                
                # Register App Inputs
                # The AppManager will now route inputs to the App's handle_input method
                # So we don't need to register callbacks here unless the App uses them directly.
                # But for compatibility, let's allow apps to register callbacks if they want,
                # OR we enforce handle_input.
                # Let's enforce handle_input for cleaner architecture.
                
                # Register Global Back to Exit
                self.input.on('back', self.close_current_app)
                
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
        self.input.clear_callbacks()
        
        # Restore Menu Controls
        self.input.on('left', lambda: self.main_menu.move_selection(-1))
        self.input.on('right', lambda: self.main_menu.move_selection(1))
        self.input.on('select', self.main_menu.select_current)

    def run(self):
        # Initial Control Setup
        self.close_current_app() 
        
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
            else:
                self.main_menu.update()
                self.main_menu.draw(self.display.get_draw())
            
            self.display.show()
            time.sleep(0.03)

    def _route_input(self, event_name):
        if self.current_app:
            handled = False
            if hasattr(self.current_app, 'handle_input'):
                handled = self.current_app.handle_input(event_name)
            
            if event_name == 'back' and not handled:
                # Global Back Handler (only if app didn't consume it)
                self.close_current_app()
        else:
            # Menu Navigation (Handled by callbacks registered in close_current_app)
            # Wait, if we register callbacks in close_current_app, they will be called TWICE
            # because we also registered global handlers above.
            # FIX: Only use global handlers.
            if event_name == 'left':
                self.main_menu.move_selection(-1)
            elif event_name == 'right':
                self.main_menu.move_selection(1)
            elif event_name == 'select':
                self.main_menu.select_current()

