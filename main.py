
from servos import servo_update
from hbridge import update_fan
import utime

  
dx = 180  # center x of 320px image
dy = -120  # center y of 240px image

fan=0

# Simulate a loop where dx and dy update from image analysis
while True:

    dy+=1
    dy=dy if dy<120 else -120
    
    dx-=1
    dx=dx if dx>-180 else 180
    
    servo_update(dx,dy)
    
    fan+=1
    fan%=101
    
    update_fan(fan)
    utime.sleep(0.1)