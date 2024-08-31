import time
import orangepi.zero2w
from OPi import GPIO

# Define your GPIO pins
RESET_PIN = 11  
DC_PIN = 22  
CS_PIN = 13  
BUSY_PIN = 18  
PWR_PIN = 12  
MOSI_PIN = 19 
SCLK_PIN = 23
# Setup GPIO
GPIO.setmode(orangepi.zero2w.BOARD)
GPIO.setup(RESET_PIN, GPIO.OUT)
GPIO.setup(BUSY_PIN, GPIO.IN, GPIO.LOW)
GPIO.setup(PWR_PIN, GPIO.OUT)
GPIO.setup(DC_PIN, GPIO.OUT)

def reset_display():
    GPIO.output(PWR_PIN, GPIO.LOW)
    time.sleep(0.2)
    GPIO.output(PWR_PIN, GPIO.HIGH)
    time.sleep(0.2)
    GPIO.output(RESET_PIN, GPIO.HIGH)
    time.sleep(0.2)
    GPIO.output(RESET_PIN, GPIO.LOW)
    time.sleep(0.002)
    GPIO.output(RESET_PIN, GPIO.HIGH)
    time.sleep(0.2)

def read_busy():
    start_time = time.time()
    while GPIO.input(BUSY_PIN) == GPIO.HIGH:
        print("Busy pin is HIGH, waiting...")
        time.sleep(0.02)
        if time.time() - start_time > 30:  # Timeout after 30 seconds
            print("Timeout waiting for busy pin to go LOW")
            break
    print("Busy pin is LOW")

try:
    reset_display()
    read_busy()
finally:
    GPIO.cleanup()
