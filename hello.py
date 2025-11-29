import machine
import time

# The onboard LED on the Pico is connected to pin 25
LED_PIN = 25

# Set up the LED pin as an output
led = machine.Pin(LED_PIN, machine.Pin.OUT)

print("Starting LED flash sequence...")
# Start an infinite loop to flash the LED
while True:
    # Turn the LED on (set pin voltage to HIGH)
    led.value(1)
    # Wait for 0.5 seconds
    time.sleep(5)

    # Turn the LED off (set pin voltage to LOW)
    led.value(0)
    # Wait for 0.5 seconds
    time.sleep(5)