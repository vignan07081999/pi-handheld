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
            # Reload to ensure fresh state if re-opened
            importlib.reload(module)
            
            if hasattr(module, 'App'):
                app_instance = module.App(self.display, self.input)
                self.current_app = app_instance
                
                # Transfer control to App
                # The App is responsible for its own loop or we call a run method?
                # Better: We call a run method that blocks until exit, 
                # OR we switch the 'update' and 'draw' calls to the app.
                # Let's go with the "App has its own loop" approach for simplicity in porting games,
                # BUT for a unified OS, it's better if the App implements update() and draw() 
                # and the Main Loop calls them.
                # However, the user asked for "Apps that can be used...".
                # Let's assume App has a run() method that takes control and returns when done.
                
                # Clear inputs before starting
                self.input.callbacks['left'] = []
                self.input.callbacks['right'] = []
                self.input.callbacks['select'] = []
                self.input.callbacks['back'] = []
                
                # Register global back to exit app
                # We let the App handle 'back' to stop its run() loop.
                # When run() returns, we call close_current_app() below.
                # self.input.on('back', self.close_current_app)
                
                app_instance.run()
                
                # When run() returns, we are back
                self.close_current_app()
                
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
        # Restore Menu Controls
        self.input.callbacks['left'] = []
        self.input.callbacks['right'] = []
        self.input.callbacks['select'] = []
        self.input.callbacks['back'] = []
        
        self.input.on('left', lambda: self.main_menu.move_selection(-1))
        self.input.on('right', lambda: self.main_menu.move_selection(1))
        self.input.on('select', self.main_menu.select_current)
        # Back on menu could show shutdown option?

    def run(self):
        # Initial Control Setup
        self.close_current_app() # Sets up menu controls
        
        while self.running:
            # Main System Loop
            
            # Update Inputs
            # In simulation, we need to pump events
            if self.input.simulate and self.display.simulate:
                import pygame
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                    self.input.handle_pygame_event(event)
            
            # Logic
            if self.current_app:
                # If app is running in non-blocking mode (update/draw), do it here.
                # But we decided on blocking run(). 
                # If run() is blocking, we won't reach here until it returns.
                # So this loop is mainly for the Menu.
                pass
            else:
                self.main_menu.update()
                self.main_menu.draw(self.display.get_draw())
                self.display.show()
            
            time.sleep(0.01)

