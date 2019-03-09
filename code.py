# CircuitPlayground Testing code for Accelerometer Logging
# Without using CPX libraries.
# Done for porting to M4 Feather at some point
# Only use NeoPixel[0] for that reason

# Version 1.0 which includes
# Updating Filename variable with time
# Button to Pause/Unpause logging & Button to change Filename
# Writing to file: Time, XYZ Accel, Temp, Noise
# Auto Pause Logging after time delay
# Version 1.1 Add File writing code in Comments for eventual testing
# Version 1.2 with different logic to write the files
# Version 1.3 with IR Signals decoded
# Version 1.4 with IR Signals removed and Logic changed
# Version 1.5 with File Writing enabled again, works very well.
# Version 1.6 Clears out Microphone code for time saving
# Version 1.7 Uploaded to GIT

# Instructions
# Reboot with Reset button pressed and slide switch to right (USB at top)
# Press Right Button to start/pause physics logging
# Press Left button to increment file name

import board                            #Board Library
import adafruit_lis3dh                  #accelerometer
import time                             #time calculations
import digitalio                        #Digital Input and Output for board
import random                           #Used to create data for output if sensor not connected
import neopixel                         #NeoPixel Ring 10 pixels on Playground
import os


from digitalio import DigitalInOut, Direction, Pull

# Hardware I2C setup on CircuitPlayground Express for Accelerometer:
import busio
i2c = busio.I2C(board.ACCELEROMETER_SCL, board.ACCELEROMETER_SDA)
int1 = digitalio.DigitalInOut(board.ACCELEROMETER_INTERRUPT)
lis3dh = adafruit_lis3dh.LIS3DH_I2C(i2c, address=0x19, int1=int1)
lis3dh.range = adafruit_lis3dh.RANGE_8_G

#CircuitPlayground has 10 Neopixels
pixels = neopixel.NeoPixel(board.NEOPIXEL, 10, brightness=0.2, auto_write=True)

#CircuitPlayground Buttons & Switch Digital 4 Left / Digital 5 Right / D21 Switch
#Switch returns TRUE if Left (Print to Serial Position) and FALSE (Write to File Position)
buttonA = DigitalInOut(board.D4)
buttonB = DigitalInOut(board.D5)
switchA = DigitalInOut(board.D7)
buttonA.direction = Direction.INPUT
buttonB.direction = Direction.INPUT
switchA.direction = Direction.INPUT
buttonA.pull = Pull.DOWN
buttonB.pull = Pull.DOWN
switchA.pull = Pull.UP

#Variables for NeoPixel Colors
RED = (50,0,0)
GREEN = (0,50,0)
BLACK = (0,0,0)
BLUE = (0,0,50)
YELLOW = (50,50,0)
CYAN = (0,50,50)
WHITE = (50,50,50)
VIOLET = (50,0,50)

# This routine logs the accelerometer data to the log file --------------------------------------:
def logphysics():
    # global logging_paused (Global Scope unnecessary I think?)
    try:
        with open("/"+log_fn, "a") as fp:
            # Read accelerometer values (in m / s ^ 2).  Returns a 3-tuple of x, y,z axis values.
            x, y, z = lis3dh.acceleration
            x = x / 9.806           #Convert to G forces and Calibrate
            y = y / 9.806
            z = z / 9.806
            
            t = time.monotonic()      # Get a timestamp

            if buttonA.value:           # Right Button Unpauses/Pauses Logging
                fp.flush
                return -10
            if buttonB.value:           # Left Button increments filename
                fp.flush
                return -20
            if int(t) % 2 == 0:         #Flash Green if Logging, Violet if paused
                if not logging_paused:
                    pixels[0] = GREEN
                elif logging_paused:
                    pixels[0] = VIOLET
            else:
                pixels[0] = BLACK
            if not logging_paused:
                fp.write('{:f},{:f},{:f},{:f} \n' .format(t, x, y, z))
    except OSError as e:            #If Can't Write (read Only) then flash RED NeoPixel on PIXEL 1
        pixels[1] = WHITE
        if e.args[0] == 28:         #Error 28 flashes WHITE
            pixels[0] = WHITE
            return -99
        else:                       #Can't write to storage, so print to serial
            print("Can't write to File: " + log_fn)
            print(log_fn + " " + '{:f},{:f},{:f},{:f}' .format(t, x, y, z))
            print(buttonA.value, buttonB.value, switchA.value)
            pixels[0] = RED
            return -99

# Get a new Log Filename which is an increment of existing files in the directory -------------:
def get_log_filename():
    i=0
    log_fn = "log" + str(int(i)) +".txt"
    while log_fn in os.listdir(""):
        i +=1
        log_fn = "log" + str(int(i)) +".txt"
    return log_fn


# Main Routine just before writing data - Setting up variables etc.
pixels[0] = YELLOW              # Present solid YELLOW to show startup
time.sleep(1)                   # Hold for 1 second at startup
logging_paused = True           # Start with logging paused
buttonpress = -1                # Flag for return value
log_fn = get_log_filename()     # Check storage and get new filename

# Main Loop - Log file as subroutine ----------------------------------------------------------:
while True:
    # Check switch postion - if left, then no logging.  If right, then call sub
    # If not logging, then flash yellow quickly and reflect on serial monitor
    # Also communicate file name change via CYAN
    # And communicate paused logging via VIOLET
    if not switchA.value:       # If Switch to RIGHT, then log data
        buttonpress = logphysics()
    else:
        print(str(time.monotonic()) + " Not writing to file " + log_fn)
        pixels[0] = YELLOW
        time.sleep(0.5)
        pixels[0] = BLACK
        time.sleep(1)
    if buttonpress == -10:      # Update file name if LEFT button pressed
        # Update file name based on time
        log_fn = get_log_filename()
        pixels[0] = CYAN
        logging_paused = True
        time.sleep(0.5)   # Debounce
    if buttonpress == -20:      #Pause Logging if RIGHT button pressed
        # Pause/Unpause logging
        logging_paused = not logging_paused
        pixels[0] = VIOLET
        time.sleep(0.5) # Debounce
    if buttonpress == -99:
        # Error must have occured in logging routine, present WHITE for error
        pixels[0] = WHITE
        time.sleep(5)