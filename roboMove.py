import serial
import time
import math

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

class position_setter:
    def __init__(self):
        self.x = 0 # Max is 100
        self.y = 100 # starts at max y
        # Position is 
        self.elbowPos = 250 # around 90 degrees in respect to x axis
        self.shoulderPos = 250 # around 60 degrees form x axis
        self.pen = 1 # pen down 2, pen up 1
        self.L1 = 100  # shoulder arm length
        self.L2 = 100  # elbow arm length
        return_home()
    def move_line(self, x_start, y_start, x_end, y_end, steps=20):
        """
        Moves the arm in a straight line from (x_start, y_start) to (x_end, y_end)
        using small incremental steps.
        """
        for i in range(steps + 1):
            xi = x_start + (x_end - x_start) * i / steps
            yi = y_start + (y_end - y_start) * i / steps
            self.move(xi, yi)
            time.sleep(0.05)  # small delay for smooth motion

    def move(self, x,y):
        '''
        Will translate position of x,y to elbow and arm
        '''
        # translate positions code here
        min_x, max_x = 0, self.L1 + self.L2
        min_y, max_y = 0, self.L1 + self.L2
        self.x = max(min_x, min(max_x, x))
        self.y = max(min_y, min(max_y, y))
        # Use inverse kinematics
        t1,t2 = self.inverse_kinematics()
        d1 = math.degrees(t1)
        d2 = math.degrees(t2)
        self.shoulderPos = self.map_range(d1, -90, 90, 75, 375)
        self.elbowPos = self.map_range(d2, 0, 180, 75, 430)
        print("Target:", self.x, self.y)
        print("Servo:", self.shoulderPos, self.elbowPos)
        move_arm(self.shoulderPos, self.elbowPos,  self.pen)
        
    def t_pen(self):
        self.pen = 1 if self.pen == 2 else 2
    def inverse_kinematics(self):

        d = math.sqrt(self.x**2 + self.y**2)

        # Prevent impossible positions
        if d > (self.L1 + self.L2):
            raise ValueError("Target out of reach")

        # elbow angle
        cos_theta2 = (self.x**2 + self.y**2 - self.L1**2 - self.L2**2) / (2*self.L1*self.L2)
        theta2 = math.acos(cos_theta2)

        # shoulder angle
        theta1 = math.atan2(self.y, self.x) - math.atan2(self.L2*math.sin(theta2),
                                               self.L1 + self.L2*math.cos(theta2))

        return theta1, theta2
    def map_range(self, value, in_min, in_max, out_min, out_max):
        return out_min + (value - in_min) * (out_max - out_min) / (in_max - in_min)
time.sleep(1)
robot = position_setter()
robot.t_pen()
# Start at current position
x_start, y_start = 0, 100
x_end, y_end = 0,50

# Move in a straight line
# result 
robot.move_line(x_start, y_start, x_end, y_end, steps=50)
