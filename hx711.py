# hx711.py - MicroPython driver for HX711 load cell amplifier
# Works with Raspberry Pi Pico - works as of 29/11/2025
# Author: Adapted for clarity and robustness

from machine import Pin
import time


class HX711:
    def __init__(self, dout, pd_sck, gain=128):
        self.PD_SCK = Pin(pd_sck, Pin.OUT)
        self.DOUT = Pin(dout, Pin.IN, pull=None)

        self.GAIN = 0
        self.OFFSET = 0
        self.SCALE = 1

        self.set_gain(gain)

    def set_gain(self, gain):
        if gain == 128:
            self.GAIN = 1
        elif gain == 64:
            self.GAIN = 3
        elif gain == 32:
            self.GAIN = 2
        else:
            raise ValueError("Gain must be 128, 64, or 32")
        self.read()

    def is_ready(self):
        return self.DOUT.value() == 0

    def read(self):
        # Wait until HX711 is ready
        while not self.is_ready():
            time.sleep_us(10)

        data = 0
        for _ in range(24):
            self.PD_SCK.value(1)
            data = (data << 1) | self.DOUT.value()
            self.PD_SCK.value(0)

        # Set channel and gain factor for next reading
        for _ in range(self.GAIN):
            self.PD_SCK.value(1)
            self.PD_SCK.value(0)

        # Convert from 24-bit two's complement
        if data & 0x800000:
            data |= ~0xffffff
        return data

    def read_average(self, times=3):
        if times <= 0:
            raise ValueError("times must be > 0")
        sum_val = 0
        for _ in range(times):
            sum_val += self.read()
        return sum_val // times

    def tare(self, times=15):
        self.OFFSET = self.read_average(times)

    def set_scale(self, scale):
        self.SCALE = scale

    def get_units(self, times=3):
        value = self.read_average(times) - self.OFFSET
        return value / self.SCALE

    def power_down(self):
        self.PD_SCK.value(0)
        self.PD_SCK.value(1)
        time.sleep_us(70)

    def power_up(self):
        self.PD_SCK.value(0)
