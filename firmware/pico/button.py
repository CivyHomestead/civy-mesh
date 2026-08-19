import time
from machine import Pin

class DoorbellButton:
    def __init__(self, pin_num=14, engine=None):
        self.pin = Pin(pin_num, Pin.IN, Pin.PULL_UP)
        self.engine = engine
        self.last_press_time = 0
        self.debounce_ms = 50
        
        # Attach hardware interrupt for falling edge (button pressed to GND)
        self.pin.irq(trigger=Pin.IRQ_FALLING, handler=self._handle_irq)
        print(f"[BUTTON] Listening on GP{pin_num} (Internal Pull-Up Active)")

    def _handle_irq(self, pin):
        current_time = time.ticks_ms()
        
        # Debounce filter
        if time.ticks_diff(current_time, self.last_press_time) < self.debounce_ms:
            return
            
        self.last_press_time = current_time
        
        # Measure hold duration
        start_hold = time.ticks_ms()
        while self.pin.value() == 0:
            time.sleep_ms(10)
            
        hold_duration = time.ticks_diff(time.ticks_ms(), start_hold)
        
        # Determine press type
        if hold_duration >= 3000:
            press_type = "LONG"   # Emergency SOS
        elif hold_duration >= 50:
            press_type = "SHORT"  # Diner Bell / Poke
        else:
            return  # Ignore noise spikes
            
        print(f"\n[BUTTON INTERRUPT] Detected {press_type} press ({hold_duration}ms)")
        
        # Dispatch to Node Engine if linked
        if self.engine:
            self.engine.trigger_button_action(press_type)