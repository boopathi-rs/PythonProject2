"""
Ball Counting Game for Raspberry Pi Pico
Requires: LCD1602 I2C module, HX711 load cell amplifier
"""

import time
import random
from machine import Pin, I2C
from hx711 import HX711
from lcd_api import LcdApi
from pico_i2c_lcd import I2cLcd

# ============== CONFIGURATION ==============
# LCD Configuration
I2C_ADDR = 0x27  # Common I2C address for LCD1602, try 0x3F if this doesn't work
I2C_NUM_ROWS = 2
I2C_NUM_COLS = 16

# HX711 Configuration
HX711_DT_PIN = 19
HX711_SCK_PIN = 18

# Game Configuration
GAME_TIME_SECONDS = 10
BALL_WEIGHT_GRAMS = 10.0  # Adjust this to match your actual ball weight
WEIGHT_TOLERANCE = 2.0  # Allow ±2g tolerance per ball


# ============== HARDWARE SETUP ==============
def setup_hardware():
    """Initialize LCD and HX711"""
    # Setup I2C for LCD
    i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)
    lcd = I2cLcd(i2c, I2C_ADDR, I2C_NUM_ROWS, I2C_NUM_COLS)

    # Setup HX711
    hx = HX711(HX711_DT_PIN, HX711_SCK_PIN)

    return lcd, hx


# ============== CALIBRATION ==============
def calibrate_scale(lcd, hx):
    """
    Calibrate the scale. Run this once to get your calibration value.
    Comment out after first calibration.
    """
    lcd.clear()
    lcd.putstr("Calibrating...")
    lcd.move_to(0, 1)
    lcd.putstr("Remove weight")
    time.sleep(3)

    # Tare (zero) the scale
    hx.tare()

    lcd.clear()
    lcd.putstr("Place known")
    lcd.move_to(0, 1)
    lcd.putstr("weight (100g)")
    time.sleep(5)

    # Read value with known weight
    raw_value = hx.read()
    calibration_factor = raw_value / 100.0  # Assuming 100g known weight

    lcd.clear()
    lcd.putstr(f"Factor:{calibration_factor}")
    time.sleep(3)

    return calibration_factor


# ============== GAME FUNCTIONS ==============
def display_question(lcd, num_balls):
    """Display the question on LCD"""
    lcd.clear()
    lcd.putstr(f"Drop {num_balls} ball")
    lcd.move_to(0, 1)
    if num_balls == 1:
        lcd.putstr("on the scale!")
    else:
        lcd.putstr("s on the scale!")


def read_weight(hx, calibration_factor):
    """Read weight from load cell in grams"""
    try:
        raw_value = hx.read()
        weight_grams = raw_value / calibration_factor
        return max(0, weight_grams)  # Don't return negative weights
    except:
        return 0


def calculate_balls(weight, ball_weight):
    """Calculate number of balls based on weight"""
    if weight < ball_weight / 2:  # Less than half a ball weight
        return 0
    return round(weight / ball_weight)


def display_countdown(lcd, seconds_left):
    """Update countdown on LCD"""
    lcd.move_to(0, 1)
    lcd.putstr(f"Time: {seconds_left:2d}s      ")


def display_result(lcd, is_correct, actual_balls, expected_balls):
    """Display the result on LCD"""
    lcd.clear()
    if is_correct:
        lcd.putstr("   CORRECT!   ")
        lcd.move_to(0, 1)
        lcd.putstr(f"  {actual_balls} balls!  ")
    else:
        lcd.putstr("Wrong. Try again")
        lcd.move_to(0, 1)
        lcd.putstr(f"Got {actual_balls}, need {expected_balls}")


def play_round(lcd, hx, calibration_factor):
    """Play one round of the game"""
    # Generate random number of balls
    num_balls = random.randint(1, 10)

    # Display question
    display_question(lcd, num_balls)
    time.sleep(2)  # Give child time to read

    # Tare the scale
    hx.tare()

    # Start countdown
    start_time = time.time()
    last_second = GAME_TIME_SECONDS

    lcd.clear()
    lcd.putstr(f"Drop {num_balls} ball{'s' if num_balls > 1 else ''}!")

    # Game loop - 10 seconds
    while True:
        elapsed = time.time() - start_time
        seconds_left = GAME_TIME_SECONDS - int(elapsed)

        if seconds_left != last_second:
            display_countdown(lcd, seconds_left)
            last_second = seconds_left

        if elapsed >= GAME_TIME_SECONDS:
            break

        time.sleep(0.1)  # Small delay to prevent too rapid updates

    # Time's up! Calculate result
    lcd.clear()
    lcd.putstr("Calculating...")
    time.sleep(0.5)

    # Read final weight
    final_weight = read_weight(hx, calibration_factor)
    balls_placed = calculate_balls(final_weight, BALL_WEIGHT_GRAMS)

    # Check if correct
    is_correct = balls_placed == num_balls

    # Display result
    display_result(lcd, is_correct, balls_placed, num_balls)
    time.sleep(4)  # Show result for 4 seconds

    return is_correct


# ============== MAIN GAME LOOP ==============
def main():
    """Main game function"""
    # Setup hardware
    lcd, hx = setup_hardware()

    # Welcome message
    lcd.clear()
    lcd.putstr("Ball Counting")
    lcd.move_to(0, 1)
    lcd.putstr("Game!")
    time.sleep(2)

    # Calibration factor (you need to determine this for your setup)
    # Option 1: Run calibration once and note the value
    # calibration_factor = calibrate_scale(lcd, hx)

    # Option 2: Use pre-determined calibration factor
    calibration_factor = 1000.0  # REPLACE with your calibrated value

    lcd.clear()
    lcd.putstr("Get ready...")
    time.sleep(2)

    # Game loop
    round_num = 1
    while True:
        lcd.clear()
        lcd.putstr(f"Round {round_num}")
        time.sleep(1)

        play_round(lcd, hx, calibration_factor)

        round_num += 1

        # Brief pause between rounds
        lcd.clear()
        lcd.putstr("Next round...")
        time.sleep(2)


# ============== ENTRY POINT ==============
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Game stopped by user")
    except Exception as e:
        print(f"Error: {e}")