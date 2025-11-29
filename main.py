# works fine with hx711.py
from hx711 import HX711
import time

# Adjust pins according to your wiring
DATA_PIN = 19   # GPIO2
CLOCK_PIN = 18  # GPIO3

hx = HX711(dout=DATA_PIN, pd_sck=CLOCK_PIN, gain=128)

print("Taring... Remove any weight from the scale.")
hx.tare()
print("Tare complete.")

# Set your calibration factor after testing with a known weight
hx.set_scale(1000)  # Adjust this value after calibration

while True:
    try:
        weight = hx.get_units(5)  # Average over 5 readings
        print("Weight: {:.2f} g".format(weight))
        time.sleep(0.5)
    except KeyboardInterrupt:
        print("Exiting...")
        break
