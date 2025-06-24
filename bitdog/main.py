"""
This section controls the servo motors based on two inputs dx and dy
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
IMG_WIDTH=100
IMG_HEIGHT=100

# module of max angle (negative in other direction)
X_MAX_ANGLE=90
Y_MAX_ANGLE=90

# Setup PWM for servos (adjust pins as needed)
servo_h = PWM(Pin(8)) # GPIO8 for horizontal 
servo_v = PWM(Pin(9)) # GPIO9 for vertical

# Set frequency to 50Hz for servos
servo_h.freq(50)
servo_v.freq(50)

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
    servo_h.duty_u16(angle_to_duty(angle_x))
    servo_v.duty_u16(angle_to_duty(angle_y))

"""
This section controls the L293 H bridge that controls the fan's power.
The interface is the function "update_fan"

hbridge L293 IC datasheet:
https://www.ti.com/lit/ds/symlink/l293.pdf

Module used: 4
Used pinout:
4,5,12 or 13: GND
16: VCC1 logic gates power source (5V)
8: Vcc2 fan power supply input
9: EN modules 4 and 3 (if L makes output high impedance)
15: A module 4 (control pulse from GPIO4)
14: output module 4 to connect on device
"""
from machine import Pin, PWM

# Set up PWM on GPIO4 at 25 kHz
fan_pwm = PWM(Pin(4))
fan_pwm.freq(50)

# Function to set fan speed (0–100%)
def update_fan(percent):
    percent = max(0, min(100, percent))  # clamp
    duty = int((percent / 100) * 65535)
    fan_pwm.duty_u16(duty)

"""
Main section

It polls waiting for udp packets at port 12345
and updates the servos with the new position
if no packages are received a timer turns off
the fan.
"""
import socket
import network
import struct

from machine import Timer

import utime

def send_udp_broadcast(message):
    # send a broadcast with the message
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.sendto(message, ("255.255.255.255", 12347))
    sock.settimeout(3)  # Optional: avoid blocking forever
    
    #send ACK and return value or return none
    try:
        response, _ = sock.recvfrom(1024)
        sock.close()
        print("registered IP")
        return response.decode()
    except OSError:
        sock.close()
        return None


#from servos import servo_update
#from hbridge import update_fan

# timer that turns off the pwm of the fan each 15s
fan_timer=Timer()
def fan_timeout(timer):
    update_fan(0)
    print("fan timeout")
    # period=[ms]
    fan_timer.init(mode=Timer.ONE_SHOT, period=15000, callback=fan_timeout)

# Setup Wi-Fi
ssid = 'DLEA801'
password = 'fanrobot'


network.hostname("bitdog")



sta = network.WLAN(network.STA_IF)
sta.active(True)
sta.connect(ssid, password)

while not sta.isconnected():
    utime.sleep(0.5)

print('Connected to Wi-Fi:', sta.ifconfig())

# Wait until ipaddress is registered on mock dns server
resp=None
while( resp is None):
    resp=send_udp_broadcast(b"REGISTER bitdog")

# Create TCP socket server
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('0.0.0.0', 12345))




fan_timeout(0)
try:
    while True:
        # receives two 1 byte elements from the udp connection
        data, addr = sock.recvfrom(2)
        
        # if data is received turns on the fan each 100ms cycle
        # if it's waiting at the previous code line, the timer fan_timeout
        # will make sure the fan is off after a wait period
        update_fan(100)
        
        # bb = signed 2 byte int
        dx, dy = struct.unpack('bb', data)
        print(f"dx={dx}, dy={dy}")

        # update servos position
        servo_update(dx,-dy)
        
        utime.sleep(0.1)
        
# when the program is interrupted turns off all pwm signals
except KeyboardInterrupt:
    print("User interrupt")
finally:
     servo_h.deinit()
     servo_v.deinit()
     fan_pwm.deinit()

