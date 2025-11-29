import utime

import machine
from machine import I2C
from lcd_api import LcdApi
from pico_i2c_lcd import I2cLcd
# from hx711 import HX711
from hx711_pio import HX711
from machine import Pin


I2C_ADDR     = 0x27
I2C_NUM_ROWS = 4
I2C_NUM_COLS = 20

def test_main():
    #Test function for verifying basic functionality
    print("Running test_main")
    rtc = machine.RTC()
    rtc.datetime((2025, 11, 27, 3, 21, 53, 0, 0))

    # Initialize HX711 (DT=Pin 15, SCK=Pin 14)
    # hx = HX711(pd_sck=14, dout=15)
    # hx.set_scale(1) # Update this with your calibration factor
    # hx.tare()

    pin_OUT = Pin(19, Pin.IN, pull=Pin.PULL_DOWN)
    pin_SCK = Pin(18, Pin.OUT)

    hx = HX711(pin_SCK, pin_OUT, state_machine=0)
    i2c = I2C(0, sda=machine.Pin(0), scl=machine.Pin(1), freq=400000)
    lcd = I2cLcd(i2c, I2C_ADDR, I2C_NUM_ROWS, I2C_NUM_COLS)    
    lcd.putstr("Navshikha has \n big bum!")
    utime.sleep(2)
    lcd.clear()

    count = 0

    while True:
        lcd.clear()
        time = utime.localtime()

        # Read weight
        val = hx.get_units()
        print("Value: ", hx.get_value())
        print("Filtered: ", hx.get_value_filtered())

        lcd.putstr("{year:>04d}/{month:>02d}/{day:>02d} {HH:>02d}:{MM:>02d}:{SS:>02d}\nWeight: {:.2f}".format(
            val,
            year=time[0], month=time[1], day=time[2],
            HH=time[3], MM=time[4], SS=time[5]))
        if count % 10 == 0:
            print("Turning cursor on")
            lcd.show_cursor()
        if count % 10 == 1:
            print("Turning cursor off")
            lcd.hide_cursor()
        if count % 10 == 2:
            print("Turning blink cursor on")
            lcd.blink_cursor_on()
        if count % 10 == 3:
            print("Turning blink cursor off")
            lcd.blink_cursor_off()                    
        if count % 10 == 4:
            print("Turning backlight off")
            lcd.backlight_off()
        if count % 10 == 5:
            print("Turning backlight on")
            lcd.backlight_on()
        if count % 10 == 6:
            print("Turning display off")
            lcd.display_off()
        if count % 10 == 7:
            print("Turning display on")
            lcd.display_on()
        if count % 10 == 8:
            print("Filling display")
            lcd.clear()
            string = ""
            for x in range(32, 32+I2C_NUM_ROWS*I2C_NUM_COLS):
                string += chr(x)
            lcd.putstr(string)
        count += 1
        utime.sleep(2)

#if __name__ == "__main__":
test_main()
