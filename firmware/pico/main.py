import time
import machine
import json
import network

print("\n====================================")
print("       CIVY NODE BOOT SEQUENCE      ")
print("====================================")

# 1. Onboard LED Diagnostic Flash
led = machine.Pin("LED", machine.Pin.OUT)
for _ in range(3):
    led.on()
    time.sleep_ms(60)
    led.off()
    time.sleep_ms(60)

try:
    import node_engine
    import button
    import ota_updater

    # 2. Start Core Engine
    engine = node_engine.CivyNodeEngine("config.json")
    
    # 3. Attach Doorbell Interrupt on GP14
    doorbell = button.DoorbellButton(pin_num=14, engine=engine)

    # 4. Handle Optional Wi-Fi & OTA Check
    if engine.config.get("wifi_enabled", False):
        print(f"[NET] Connecting to {engine.config['wifi_ssid']}...")
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        wlan.connect(engine.config["wifi_ssid"], engine.config["wifi_pass"])
        
        # Non-blocking wait (up to 5s)
        wait_count = 0
        while not wlan.isconnected() and wait_count < 5:
            time.sleep(1)
            wait_count += 1
            
        if wlan.isconnected():
            print(f"[NET] Online. IP: {wlan.ifconfig()[0]}")
            updater = ota_updater.OTAUpdater("config.json")
            updater.check_and_update()
        else:
            print("[NET] Connection timed out. Falling back to offline mesh mode.")
    else:
        print("[NET] Wi-Fi disabled in config. Running 100% offline.")

    print("\n[CIVY NODE] Engine active and listening. Standby mode...")

    # 5. Non-Blocking Event Loop
    heartbeat_timer = time.ticks_ms()
    while True:
        # Flash heartbeat LED briefly every 10 seconds
        if time.ticks_diff(time.ticks_ms(), heartbeat_timer) > 10000:
            led.on()
            time.sleep_ms(15)
            led.off()
            heartbeat_timer = time.ticks_ms()
            
        time.sleep_ms(100)

except Exception as err:
    print(f"[CRITICAL ERROR] Boot loop failed: {err}")
    while True:
        led.toggle()
        time.sleep_ms(300)