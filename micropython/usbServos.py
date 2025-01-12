import sys
import time
import math
from pimoroni import Button
from plasma import WS2812
from servo import Servo, servo2040

"""
Demonstrates how to create multiple Servo objects and control them together via serial commands from PC.
It uses code from pimoroni servo 2040 examples to move servos smoothly
"""
# Create the LED bar, using PIO 1 and State Machine 0
led_bar = WS2812(servo2040.NUM_LEDS, 1, 0, servo2040.LED_DATA)

# Create a list of servos for pins 0 to 3. Up to 16 servos can be created
START_PIN = servo2040.SERVO_1
END_PIN = servo2040.SERVO_9
servos = [Servo(i) for i in range(START_PIN, END_PIN + 1)]

# Enable all servos (this puts them at the middle)
for s in servos:
    s.enable()
time.sleep(1)

UPDATES = 50            # How many times to update Servos per second
TIME_FOR_EACH_MOVE = 0.25  # The time to travel between each values
UPDATES_PER_MOVE = TIME_FOR_EACH_MOVE * UPDATES
USE_COSINE = True       # Whether or not to use a cosine path between values

servoValues = [0.0] * 9 # servo values for the current posture
nextServoValues = [0.0] * 9 # servo values for the next posture provided by SAS command

# Create the user button
user_sw = Button(servo2040.USER_SW)

# Start updating the LED bar
led_bar.start()

# receive command "servoNumber servoValue"
while not user_sw.raw():
    
    # read a command from the host
    inCommand = sys.stdin.readline().strip()
    
    # if you received a command, show via led0
    if len(inCommand) > 0:
        led_bar.set_hsv(0, 1.0, 1.0, 0.5)     

        print(inCommand)
        inCommandSplit = inCommand.split()
        cmdString = inCommandSplit[0]
        
        if cmdString == "sss":
            servoNumber = int(inCommandSplit[1])
            servoValue = float(inCommandSplit[2])
        
            # set servo value
            servos[servoNumber].value(servoValue)
            
            # give servo time to react
            time.sleep(0.1)
            
        elif cmdString == "sas":
            # parse the servo values into a new array
            for arrayNumber in range(1, len(inCommandSplit)):
                #print("servoNumber: " + str(arrayNumber-1) + " " + inCommandSplit[arrayNumber])
                # servos are addressed zero-based
                #servos[arrayNumber-1].value(float(inCommandSplit[arrayNumber]))
                
                nextServoValues[arrayNumber-1] = float(inCommandSplit[arrayNumber])
                
            for update in range(0, UPDATES_PER_MOVE):
                # Calculate how far along this movement to be
                percent_along = update / UPDATES_PER_MOVE

                if USE_COSINE:
                    # Move the servo between values using cosine
                    for eachServoNumber in range(0,9):
                        servos[eachServoNumber].to_percent(math.cos(percent_along * math.pi), 1.0, -1.0, servoValues[eachServoNumber], nextServoValues[eachServoNumber])
                else:
                    # Move the servo linearly between values
                    for eachServoNumber in range(0,9):
                        servos[eachServoNumber].to_percent(percent_along, 0.0, 1.0, servoValues[eachServoNumber], nextServoValues[eachServoNumber])                
                
                time.sleep(1.0 / UPDATES)
                
            # now copy the new values to the old state    
            for eachServoNumber in range(0,9):
                servoValues[eachServoNumber] = nextServoValues[eachServoNumber]
            
        # indicate that you received a cmd
        led_bar.set_hsv(0, 0.0, 0.0, 0.0)
    
# Disable the servos
for s in servos:
    s.disable()

# Turn off the LED bar
led_bar.clear()
