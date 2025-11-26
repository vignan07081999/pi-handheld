import time
import config

# Try to import hardware libraries
try:
    from gpiozero import RotaryEncoder, Button
    HARDWARE_AVAILABLE = True
except ImportError:
    HARDWARE_AVAILABLE = False

class InputManager:
    def __init__(self, simulate=False):
        self.simulate = simulate or not HARDWARE_AVAILABLE
        self.callbacks = {
            'left': [],
            'right': [],
            'select': [],
            'back': []
        }
        self.on_any_event = None
        
        if not self.simulate:
            try:
                self._init_hardware()
            except Exception as e:
                print(f"Input Init Failed: {e}")
                self.simulate = True
        else:
            print("Input Manager running in Simulation Mode")

    def _init_hardware(self):
        # Rotary Encoder (wrap=False to track direction manually or use steps)
        # gpiozero RotaryEncoder: 
        # when_rotated is called. steps increases/decreases.
        self.encoder = RotaryEncoder(config.PIN_ENCODER_CLK, config.PIN_ENCODER_DT, wrap=False)
        self.encoder.when_rotated = self._on_rotate
        
        # Button
        self.btn = Button(config.PIN_ENCODER_SW, pull_up=True)
        self.btn.when_released = self._on_release
        self.btn.when_held = self._on_hold
        self.btn.hold_time = config.LONG_PRESS_TIME

    def _on_rotate(self):
        # We need to determine direction.
        # gpiozero doesn't pass direction to callback directly, but we can check steps change?
        # Actually, RotaryEncoder has 'steps' property.
        # But for simple left/right events, we might want to track last steps.
        # Or use the internal value.
        # Wait, if we use wrap=False, steps goes up and down.
        # We can just compare to last value?
        # But simpler: gpiozero 2.0 has when_rotated_clockwise and when_rotated_counter_clockwise?
        # Let's check docs or assume standard behavior.
        # Standard RotaryEncoder has when_rotated.
        # Let's track steps.
        pass

    # Re-implementing _on_rotate with logic to detect direction
    # We need to store last_steps
        self.last_steps = 0
        
    def _on_rotate(self):
        current_steps = self.encoder.steps
        delta = current_steps - self.last_steps
        self.last_steps = current_steps
        
        if delta > 0:
            self._trigger('right')
        elif delta < 0:
            self._trigger('left')

    def _on_release(self):
        # If it was held, when_held fired. Does when_released also fire?
        # Usually yes. We need to distinguish.
        # gpiozero: when_held fires after hold_time. 
        # We can set a flag in when_held?
        if not hasattr(self, 'was_held'):
            self.was_held = False
            
        if self.was_held:
            self.was_held = False # Reset
            # Do nothing, handled by hold
        else:
            self._trigger('select')

    def _on_hold(self):
        self.was_held = True
        self._trigger('back')

    def on(self, event_name, callback):
        if event_name in self.callbacks:
            self.callbacks[event_name].append(callback)

    def _trigger(self, event_name):
        if self.on_any_event:
            self.on_any_event(event_name)
            
        for callback in self.callbacks[event_name]:
            callback()

    def handle_pygame_event(self, event):
        import pygame
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self._trigger('left')
            elif event.key == pygame.K_RIGHT:
                self._trigger('right')
            elif event.key == pygame.K_RETURN:
                self._trigger('select')
            elif event.key == pygame.K_ESCAPE or event.key == pygame.K_BACKSPACE:
                self._trigger('back')
