"""
This file controls the servo motors based on two inputs dx and dy
that represent the distance from the center of the image in the camera
using the interface function "servo_update" 

Board GPIO for project
GPIO8 for horizontal PWM
GPIO9 for vertical PWM

0° is when the fan is pointing to the center

Tower pro micro Servo 9g SG90 pinout
Pin Configuration and Descriptions
Pin Number 	Color 	Description
1 	Brown 	Ground (GND)
2 	Red 	Power Supply (VCC)
3 	Orange 	Control Signal (PWM)
"""
from machine import Pin, PWM
#Constants

#image specs
IMG_WIDTH=320
IMG_HEIGHT=240

# module of max angle (negative in other direction)
X_MAX_ANGLE=90
Y_MAX_ANGLE=90

# Setup PWM for servos (adjust pins as needed)
servo_horizontal = PWM(Pin(8)) # GPIO8 for horizontal 
servo_vertical = PWM(Pin(9)) # GPIO9 for vertical

# Set frequency to 50Hz for servos
servo_horizontal.freq(50)
servo_vertical.freq(50)

# Helper: Map angle (-90–90) to duty_u16 for 0.5ms–2.5ms pulse width at 50Hz
def angle_to_duty(angle):
    # Duty cycle range for -90° to 90° is approx. 1638 (0.5ms) to 8192 (2.5ms)
    return int(1638 + ((angle+90) / 180.0) * (8192 - 1638))

# Map dx, dy (image coordinates) to angles (-90°–90°)
def position_to_angle(dx, dy):
    angle_x = int(2*(dx / IMG_WIDTH) * X_MAX_ANGLE)
    angle_y = int(2*(dy / IMG_HEIGHT) * Y_MAX_ANGLE)
    return angle_x, angle_y

# interface function for the servo motors
def servo_update(dx, dy):
    angle_x, angle_y = position_to_angle(dx, dy)

    # Send angles to servos
    servo_horizontal.duty_u16(angle_to_duty(angle_x))
    servo_vertical.duty_u16(angle_to_duty(angle_y))
 