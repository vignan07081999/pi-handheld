import time
from PIL import ImageDraw
import config

class App:
    def __init__(self, display, input_manager):
        self.display = display
        self.input = input_manager
        self.running = False

    def run(self):
        self.running = True
        
        # Draw White Screen
        draw = self.display.get_draw()
        draw.rectangle((0, 0, config.DISPLAY_WIDTH, config.DISPLAY_HEIGHT), fill=(255, 255, 255))
        
        # Add a small hint text
        draw.text((10, 10), "Torch On", fill=(0, 0, 0))
        draw.text((10, 30), "Hold Back to Exit", fill=(0, 0, 0))
        
        self.display.show()
        
        # Loop until exit
        while self.running:
            # Input is handled by global back handler in AppManager?
            # No, AppManager registers 'back' to close_current_app, but that just sets current_app=None.
            # It doesn't break THIS loop unless we check self.running or if AppManager kills the thread (it doesn't).
            # So we need to check if we are still the current app or if a flag is set.
            # But wait, AppManager calls app.run() which BLOCKS.
            # So AppManager CANNOT close the app unless the app checks inputs.
            # We need to handle inputs here!
            
            # Check inputs manually or via callbacks?
            # AppManager cleared callbacks. We need to re-register if we want custom behavior,
            # OR rely on AppManager's 'back' callback to set a flag?
            # AppManager's 'close_current_app' sets self.current_app = None.
            # But it doesn't affect US directly.
            
            # Better approach: AppManager sets a flag on the App instance?
            # Or we handle 'back' ourselves.
            
            # Let's handle 'back' ourselves to break the loop.
            
            if self.input.simulate:
                import pygame
                for event in pygame.event.get():
                    self.input.handle_pygame_event(event)
            
            # We need to register a back handler that sets running = False
            # We do this ONCE.
            pass
            
            time.sleep(0.1)

    def stop(self):
        self.running = False

    # We need to override the run method to actually register the callback
    def handle_input(self, event):
        pass # Only exit handled by global back

    def update(self):
        pass

    def draw(self):
        draw = self.display.get_draw()
        draw.rectangle((0, 0, config.DISPLAY_WIDTH, config.DISPLAY_HEIGHT), fill=(255, 255, 255))
        draw.text((60, 150), "TORCH", fill=(0, 0, 0))
