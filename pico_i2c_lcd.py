from lcd_api import LcdApi
from machine import I2C
import time

# PCF8574 I2C LCD Backpack pin mapping
MASK_RS = 0x01
MASK_RW = 0x02
MASK_E = 0x04
SHIFT_BACKLIGHT = 3
SHIFT_DATA = 4


class I2cLcd(LcdApi):
    def __init__(self, i2c, i2c_addr, num_lines, num_columns):
        self.i2c = i2c
        self.i2c_addr = i2c_addr
        self.i2c.writeto(self.i2c_addr, bytes([0]))
        time.sleep_ms(20)

        # Initialize in 4-bit mode
        self.hal_write_init_nibble(0x03)
        time.sleep_ms(5)
        self.hal_write_init_nibble(0x03)
        time.sleep_ms(5)
        self.hal_write_init_nibble(0x03)
        time.sleep_ms(1)
        self.hal_write_init_nibble(0x02)

        # Initialize display
        LcdApi.__init__(self, num_lines, num_columns)

        cmd = self.LCD_FUNCTION_SET | self.LCD_4BIT_MODE | self.LCD_2LINE | self.LCD_5x8_DOTS
        self.hal_write_command(cmd)

    def hal_write_init_nibble(self, nibble):
        """Write initialization nibble"""
        byte = ((nibble & 0x0F) << SHIFT_DATA) | (1 << SHIFT_BACKLIGHT)
        self.i2c.writeto(self.i2c_addr, bytes([byte]))
        time.sleep_us(1)
        self.i2c.writeto(self.i2c_addr, bytes([byte | MASK_E]))
        time.sleep_us(1)
        self.i2c.writeto(self.i2c_addr, bytes([byte]))
        time.sleep_us(100)

    def hal_backlight_on(self):
        """Turn backlight on"""
        self.i2c.writeto(self.i2c_addr, bytes([1 << SHIFT_BACKLIGHT]))

    def hal_backlight_off(self):
        """Turn backlight off"""
        self.i2c.writeto(self.i2c_addr, bytes([0]))

    def hal_write_command(self, cmd):
        """Write command to LCD"""
        byte = (1 << SHIFT_BACKLIGHT) if self.backlight else 0
        self.hal_write_byte(byte | ((cmd & 0xF0)))
        self.hal_write_byte(byte | ((cmd << 4) & 0xF0))

        if cmd <= 3:
            time.sleep_ms(5)

    def hal_write_data(self, data):
        """Write data to LCD"""
        byte = (1 << SHIFT_BACKLIGHT) if self.backlight else 0
        self.hal_write_byte(byte | MASK_RS | (data & 0xF0))
        self.hal_write_byte(byte | MASK_RS | ((data << 4) & 0xF0))

    def hal_write_byte(self, data):
        """Write a byte using I2C"""
        self.i2c.writeto(self.i2c_addr, bytes([data]))
        time.sleep_us(1)
        self.i2c.writeto(self.i2c_addr, bytes([data | MASK_E]))
        time.sleep_us(1)
        self.i2c.writeto(self.i2c_addr, bytes([data]))
        time.sleep_us(100)