"""
This file controls the L293 H bridge that controls the fan's power.
The interface is the function "update_fan"

hbridge L293 IC datasheet:
https://www.ti.com/lit/ds/symlink/l293.pdf

Module used: 4
Used pinout:
4,5,12 or 13: GND
16: VCC1 logic gates power source (5V)
8: Vcc2 fan power supply input
9: EN modules 4 and 3 (if L makes output high impedance)
15: A module 4 (control pulse)
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