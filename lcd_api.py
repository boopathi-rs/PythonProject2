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

