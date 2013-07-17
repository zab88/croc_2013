import gpio
import time
import sys

led_pin = "gpio18"
led_pin17 = "gpio17"
led_pin16 = "gpio16"
led_pin15 = "gpio15"
led_pin14 = "gpio14"

def moveCommand(direction):
    #if windows, let's go out of here
    is_windows = sys.platform.startswith('win')
    if is_windows:
        return
    #switch off
    gpio.pinMode(led_pin17, gpio.OUTPUT)
    gpio.pinMode(led_pin16, gpio.OUTPUT)
    gpio.pinMode(led_pin15, gpio.OUTPUT)
    gpio.pinMode(led_pin14, gpio.OUTPUT)
    gpio.digitalWrite(led_pin17, gpio.LOW)
    gpio.digitalWrite(led_pin16, gpio.LOW)
    gpio.digitalWrite(led_pin15, gpio.LOW)
    gpio.digitalWrite(led_pin14, gpio.LOW)

    '''
    pins: 14, 15, 16, 17
    none - 0000
    centered - 1111
    forward  - 0001
    right    - 0010
    back     - 0100
    left     - 1000
    '''

    if direction == 'centered':
        gpio.digitalWrite(led_pin14, gpio.HIGH)
        gpio.digitalWrite(led_pin15, gpio.HIGH)
        gpio.digitalWrite(led_pin16, gpio.HIGH)
        gpio.digitalWrite(led_pin17, gpio.HIGH)
    elif direction == 'forward':
        gpio.digitalWrite(led_pin17, gpio.HIGH)
    elif direction == 'right':
        gpio.digitalWrite(led_pin16, gpio.HIGH)
    elif direction == 'back':
        gpio.digitalWrite(led_pin15, gpio.HIGH)
    elif direction == 'left':
        gpio.digitalWrite(led_pin14, gpio.HIGH)
    elif direction == 'none':
        gpio.digitalWrite(led_pin17, gpio.LOW)
        gpio.digitalWrite(led_pin16, gpio.LOW)
        gpio.digitalWrite(led_pin15, gpio.LOW)
        gpio.digitalWrite(led_pin14, gpio.LOW)
    return

'''
def delay(ms):
    time.sleep(1.0*ms/1000)

def setup():
    gpio.pinMode(led_pin, gpio.OUTPUT)

def loop():
    while(1):
        gpio.digitalWrite(led_pin, gpio.HIGH)
        delay(200)
        gpio.digitalWrite(led_pin, gpio.LOW)
        delay(100)

def main():
    setup()
    loop()

main()
'''