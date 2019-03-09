# Write your code here :-)
import board
import digitalio
import storage
import time

switch = digitalio.DigitalInOut(board.D7)  # For Circuit Playground Express
switch.direction = digitalio.Direction.INPUT
switch.pull = digitalio.Pull.UP

led = digitalio.DigitalInOut(board.D13)
led.direction = digitalio.Direction.OUTPUT

#led = DigitalInOut(board.D13)           #create led which is D13
#led.direction = Direction.OUTPUT        #D7 is output digital

# If the switch pin is connected to ground CircuitPython can write to the drive
# If Switch is LEFT then can write to drive from MU, switch.value is True
# If Switch is RIGHT then CAN'T write to drive from MU,
# yet can write from Python, switch.value is False

storage.remount("/", switch.value)

#Now Put on Red LED to show if WRITEABLE from Mu, swich.value is True
led.value = not switch.value
time.sleep(1)   #Pause for a second to show light before loading code.py
#print(switch.value)