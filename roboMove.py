import serial
import time

ser = serial.Serial('COM12', 115200, timeout=1)
print( ser.readline().decode('utf-8').strip() )

elbowPos = 250
shoulderPos = 250
penUp = 1
penDown = 2

xPos = 0
yPos = 0

def move_arm(shoulder, elbow, pen):
    # Construct the string: e.g., "{250,250,1}"
    command = f"{{{shoulder},{elbow},{pen}}}\n"
    
    # Send it to the serial port
    ser.write(command.encode('utf-8'))
    elbowPos = elbow
    shoulderPos = shoulder
    
    # Read the response
    feedback = ser.readline().decode('utf-8').strip()
    return feedback

def pen_up():
    print(move_arm(shoulderPos, elbowPos, penUp))

def pen_down():
    print(move_arm(shoulderPos, elbowPos, penDown))

def return_home():
    print(move_arm(250, 250, penUp))

return_home()
pen_down()
