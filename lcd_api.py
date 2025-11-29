"""
LCD API Base Class
Save as: lcd_api.py
"""

import time


class LcdApi:
    # Commands
    LCD_CLR = 0x01
    LCD_HOME = 0x02
    LCD_ENTRY_MODE = 0x04
    LCD_DISPLAY_CTRL = 0x08
    LCD_CURSOR_SHIFT = 0x10
    LCD_FUNCTION_SET = 0x20
    LCD_SET_CGRAM = 0x40
    LCD_SET_DDRAM = 0x80

    # Flags for display on/off control
    LCD_DISPLAY_ON = 0x04
    LCD_CURSOR_ON = 0x02
    LCD_BLINK_ON = 0x01

    # Flags for display entry mode
    LCD_ENTRY_LEFT = 0x02
    LCD_ENTRY_SHIFT_DECREMENT = 0x00

    # Flags for function set
    LCD_4BIT_MODE = 0x00
    LCD_2LINE = 0x08
    LCD_5x8_DOTS = 0x00

    def __init__(self, num_lines, num_columns):
        self.num_lines = num_lines
        self.num_columns = num_columns
        self.cursor_x = 0
        self.cursor_y = 0
        self.backlight = True
        self.display_on()
        self.clear()

    def clear(self):
        """Clear the display"""
        self.hal_write_command(self.LCD_CLR)
        time.sleep_ms(2)
        self.cursor_x = 0
        self.cursor_y = 0

    def home(self):
        """Return cursor to home position"""
        self.hal_write_command(self.LCD_HOME)
        time.sleep_ms(2)
        self.cursor_x = 0
        self.cursor_y = 0

    def move_to(self, cursor_x, cursor_y):
        """Move cursor to specified position"""
        self.cursor_x = cursor_x
        self.cursor_y = cursor_y
        addr = cursor_x + (0x40 * cursor_y)
        self.hal_write_command(self.LCD_SET_DDRAM | addr)

    def putchar(self, char):
        """Write a single character"""
        if char == '\n':
            self.cursor_y += 1
            self.cursor_x = 0
            if self.cursor_y >= self.num_lines:
                self.cursor_y = 0
            self.move_to(self.cursor_x, self.cursor_y)
        else:
            self.hal_write_data(ord(char))
            self.cursor_x += 1

    def putstr(self, string):
        """Write a string"""
        for char in string:
            self.putchar(char)

    def display_on(self):
        """Turn display on"""
        self.hal_write_command(self.LCD_DISPLAY_CTRL | self.LCD_DISPLAY_ON)

    def display_off(self):
        """Turn display off"""
        self.hal_write_command(self.LCD_DISPLAY_CTRL)

    def backlight_on(self):
        """Turn backlight on"""
        self.backlight = True
        self.hal_backlight_on()

    def backlight_off(self):
        """Turn backlight off"""
        self.backlight = False
        self.hal_backlight_off()

    def hal_backlight_on(self):
        """Override in subclass"""
        pass

    def hal_backlight_off(self):
        """Override in subclass"""
        pass

    def hal_write_command(self, cmd):
        """Override in subclass"""
        raise NotImplementedError

    def hal_write_data(self, data):
        """Override in subclass"""
        raise NotImplementedError


"""
I2C LCD Driver for Raspberry Pi Pico
Save as: pico_i2c_lcd.py
"""

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