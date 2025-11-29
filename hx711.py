"""
HX711 Load Cell Amplifier Driver for Raspberry Pi Pico
Save as: hx711.py
"""

import time
from machine import Pin


class HX711:
    def __init__(self, dt_pin, sck_pin):
        """
        Initialize HX711
        dt_pin: Data pin number
        sck_pin: Clock pin number
        """
        self.dt = Pin(dt_pin, Pin.IN)
        self.sck = Pin(sck_pin, Pin.OUT, value=0)
        self.tare_value = 0

    def is_ready(self):
        """Check if HX711 is ready to send data"""
        return self.dt.value() == 0

    def wait_ready(self, timeout=1.0):
        """Wait for HX711 to be ready"""
        start = time.time()
        while not self.is_ready():
            if time.time() - start > timeout:
                return False
            time.sleep(0.001)
        return True

    def read_raw(self):
        """Read raw 24-bit value from HX711"""
        if not self.wait_ready():
            return 0

        # Read 24 bits
        value = 0
        for _ in range(24):
            self.sck.value(1)
            time.sleep_us(1)
            value = (value << 1) | self.dt.value()
            self.sck.value(0)
            time.sleep_us(1)

        # Pulse SCK one more time to set gain to 128 for next reading
        self.sck.value(1)
        time.sleep_us(1)
        self.sck.value(0)

        # Convert from 24-bit two's complement to signed integer
        if value & 0x800000:
            value -= 0x1000000

        return value

    def read(self, samples=5):
        """
        Read average value over multiple samples
        samples: number of samples to average
        """
        values = []
        for _ in range(samples):
            val = self.read_raw()
            if val != 0:  # Only include valid readings
                values.append(val)
            time.sleep(0.01)

        if not values:
            return 0

        # Remove outliers (simple approach: remove min and max if we have enough samples)
        if len(values) >= 5:
            values.remove(min(values))
            values.remove(max(values))

        return sum(values) / len(values) - self.tare_value

    def tare(self, samples=10):
        """
        Zero the scale by setting current reading as baseline
        samples: number of samples to average for tare
        """
        values = []
        for _ in range(samples):
            val = self.read_raw()
            if val != 0:
                values.append(val)
            time.sleep(0.05)

        if values:
            self.tare_value = sum(values) / len(values)
        else:
            self.tare_value = 0

    def power_down(self):
        """Put HX711 in power-down mode"""
        self.sck.value(0)
        self.sck.value(1)
        time.sleep_us(60)

    def power_up(self):
        """Wake HX711 from power-down mode"""
        self.sck.value(0)
        time.sleep_us(1)