import time
import config

# Try to import hardware libraries
try:
    import RPi.GPIO as GPIO
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
        self.on_any_event = None # Callback(event_name)
        
        self.last_button_press_time = 0
        self.button_pressed = False
        
        if not self.simulate:
            self._init_hardware()
        else:
            print("Input Manager running in Simulation Mode (Use Left/Right Arrows, Enter, Esc)")

    def _init_hardware(self):
        try:
            GPIO.setmode(GPIO.BCM)
            
            # Encoder Pins
            GPIO.setup(config.PIN_ENCODER_CLK, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.setup(config.PIN_ENCODER_DT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.setup(config.PIN_ENCODER_SW, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            
            # Add interrupts
            GPIO.add_event_detect(config.PIN_ENCODER_CLK, GPIO.BOTH, callback=self._encoder_callback)
            GPIO.add_event_detect(config.PIN_ENCODER_SW, GPIO.BOTH, callback=self._button_callback, bouncetime=50)
            
            self.clk_last_state = GPIO.input(config.PIN_ENCODER_CLK)
        except Exception as e:
            print(f"Input Hardware Init Failed: {e}")
            self.simulate = True

    def _encoder_callback(self, channel):
        clk_state = GPIO.input(config.PIN_ENCODER_CLK)
        dt_state = GPIO.input(config.PIN_ENCODER_DT)
        
        if clk_state != self.clk_last_state:
            if dt_state != clk_state:
                self._trigger('right')
            else:
                self._trigger('left')
        self.clk_last_state = clk_state

    def _button_callback(self, channel):
        # Logic for Short Press vs Long Press
        if GPIO.input(config.PIN_ENCODER_SW) == 0: # Pressed (Active Low)
            self.button_pressed = True
            self.last_button_press_time = time.time()
        else: # Released
            if self.button_pressed:
                duration = time.time() - self.last_button_press_time
                if duration >= config.LONG_PRESS_TIME:
                    self._trigger('back')
                else:
                    self._trigger('select')
                self.button_pressed = False

    def on(self, event_name, callback):
        """Register a callback for an event ('left', 'right', 'select', 'back')."""
        if event_name in self.callbacks:
            self.callbacks[event_name].append(callback)

    def _trigger(self, event_name):
        if self.on_any_event:
            self.on_any_event(event_name)
            
        for callback in self.callbacks[event_name]:
            callback()

    def update(self):
        """Call this in the main loop to handle simulation events."""
        if self.simulate:
            import pygame
            # We assume pygame is initialized by DisplayManager
            keys = pygame.key.get_pressed()
            # We need to handle single key presses, not continuous holding for navigation usually
            # But pygame.key.get_pressed() is for state. 
            # Better to rely on the event loop in DisplayManager or handle events here if passed.
            # Ideally, main loop passes events here.
            pass

    def handle_pygame_event(self, event):
        """Process a pygame event for simulation."""
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
