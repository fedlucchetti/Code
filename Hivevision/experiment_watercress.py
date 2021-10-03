import time, sys, os, json
import numpy as np
from datetime import datetime
import Control
control=Control.Control()

#####################################################
ledconfig = control.ledconfig
control.turn_all_off()
#####################################################
#####################################################
hour_on,hour_off = 8,8+14
h_period         = 2
duty_r           = 1500
duty_b           = int(duty_r*2)
#####################################################
timeout=61
#####################################################
try:
    while True:
        hour = int(datetime.now().strftime("%H"))
        min  = int(datetime.now().strftime("%M"))
        if hour > hour_on and hour < hour_off and timeout >60:
            print(hour,min)
            # print('r',control._led_status_channel("r"),'target = ',duty_r,'b',control._led_status_channel("b"),'target = ',duty_b)
            if control._led_status_channel("r") not in range(duty_r-20,duty_r+20):
                print("Setting duty red")
                control.set_duty('r',duty_r)
                timeout=0
            if control._led_status_channel("b") not in range(duty_b-20,duty_b+20):
                print("Setting duty blue")
                control.set_duty('b',duty_b)
                timeout=0
        elif  hour%h_period==0 and min==0:
            print("executing multispectral pic")
            control.MultiSpectralPic()
            time.sleep(30)
        elif hour < hour_on and hour > hour_off:
            control.turn_all_off()
        else:
            pass
        timeout+=1
        time.sleep(1)
except Exception as e:
    control.turn_all_off()
    print(e)
