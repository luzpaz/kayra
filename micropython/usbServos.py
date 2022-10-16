import sys
import time
from pimoroni import Button
from plasma import WS2812
from servo import Servo, servo2040

"""
Demonstrates how to create multiple Servo objects and control them together via serial commands from PC.
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
            #print("sas cmd")
            for arrayNumber in range(1, len(inCommandSplit)):
                #print("servoNumber: " + str(arrayNumber-1) + " " + inCommandSplit[arrayNumber])
                # servos are addressed zero-based
                servos[arrayNumber-1].value(float(inCommandSplit[arrayNumber]))
            
        
        # indicate that you received a cmd
        led_bar.set_hsv(0, 0.0, 0.0, 0.0)
    
# Disable the servos
for s in servos:
    s.disable()

# Turn off the LED bar
led_bar.clear()
