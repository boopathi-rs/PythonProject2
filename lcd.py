import time
from liquidcrystal_i2c import LiquidCrystal_I2C

# The default I2C address for most 16x2 LCD modules is 0x27 or 0x3F.
# You may need to change this if your module uses a different address.
LCD_ADDRESS = 0x27

# Initialize the LCD object:
# The parameters are (I2C Address, Backlight Enable Pin, LCD columns, LCD rows)
# 16 is for 16 columns, 2 is for 2 rows (16x2 LCD)
lcd = LiquidCrystal_I2C(LCD_ADDRESS, 0, 16, 2)

# --- Start LCD Communication ---
print("Initializing LCD...")
# Turn on the backlight (if it's not on by default)
lcd.backlight()

# Clear any previous content on the display
lcd.clear()

# Display "Hello World!" on the first row (row index 0)
# setCursor(column, row)
lcd.setCursor(0, 0)
lcd.print("Hello World!")

# Display a supplementary message on the second row (row index 1)
lcd.setCursor(0, 1)
lcd.print("I2C Pi Project")

# Optional: Keep the display active for 5 seconds, then clear it.
time.sleep(5)
lcd.clear()
print("LCD cleared. Program finished.")