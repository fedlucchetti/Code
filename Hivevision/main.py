from __future__ import division
import time, sys, os, json
import numpy as np
import Camera
from colorsys import hls_to_rgb
from datetime import datetime
cam = Camera.Camera()
import Control
control=Control.Control()

#####################################################
MAXDUTY     = 16*4095
SMOOTHDELAY = 0.1
DIMDELAY    = 1 # in sec
colors      = ["w","g","b","r","fr"]
#####################################################

while True:
    os.system('clear')
    print('                                                             ')
    print('_____________________________________________________________')
    print('current color intensities')
    print('white','\t','green','\t','blue','\t','red','\t','farred')
    print(control.pwm.channels[7].duty_cycle,'\t',\
          control.pwm.channels[6].duty_cycle,'\t',\
          control.pwm.channels[5].duty_cycle,'\t',\
          control.pwm.channels[4].duty_cycle+control.pwm.channels[3].duty_cycle,'\t',\
          control.pwm.channels[2].duty_cycle)
    print("Select color:")
    print("             [ w:white , g:green , b:blue , r:red , fr:farred]")
    print("Options:")
    print("         pic      : take picture")
    print("         testtile : test tile")
    print("         loopparams : loop framerate and exposure time params")
    print("         live     : live stream port 8081")
    print("         multi    : Multispectral capture")
    print("         cal      : Color Imax calbration")
    print("         off      : Switch all off")
    print("         avg      : Multiple shots")


    # print("         start: start live stream")
    # print("         stop : start live stream")
    print("         q    : quit")
    select = input("Enter:  ")
    if select=='q': break
    if select=='off': control.turn_all_off()
    if select=='cal':
        control.CalibrateImax()
    if select=='multi':
        mode = input("signal or tile: ")
        control.MultiSpectralPic(mode)
    if select=='psy': psychedelia()
    if select == "live":
        os.system("sudo service motion start")
        print("Start live stream")
        time.sleep(1)
        continue
    if select=="stop":
        os.system("sudo service motion stop")
        print("Stop live stream")
        time.sleep(1)
        continue
    if select=='avg':
        os.system("sudo service motion stop")
        N=input("Number of captures :")
        control.framerate     = int(input("framerate "))
        control.exposure_time = float(input("exposure time "))
        control.multiple_shots(int(N))
        time.sleep(1)
        continue
    if select=='loopparams':
        os.system("sudo service motion stop")
        control.loop_params()
        time.sleep(1)
        continue
    if select=='pic':
        os.system("sudo service motion stop")
        control.measure()
        time.sleep(1)
        continue
    if select=='testtile':
        os.system("sudo service motion stop")
        control.pic_tile()
        time.sleep(1)
        continue
    if select in colors:
        val_in = int(input("Enter intensity value [0 " + str(MAXDUTY) + "] for color " + select + ":"))
        control.set_duty(select,val_in)
        time.sleep(1)
        continue
    else:
        # print("Not valid")
        time.sleep(2)
        continue
