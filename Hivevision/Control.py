from __future__ import division
import time, sys, os, json
import numpy as np
import picamera
import picamera.array
from colorsys import hls_to_rgb
from datetime import datetime


class Control():
    def __init__(self):
        self.ledconfig     = {'w'    : {'channel':10,'imax':14000,'frate':11,'exptime':1},\
                              'g'    : {'channel':11,'imax':12300,'frate':6, 'exptime':0.5},\
                              'b'    : {'channel':12,'imax':8700 ,'frate':1, 'exptime':0.1},\
                              'r'    : {'channel':13,'imax':8350 ,'frate':1 ,'exptime':0.2},\
                              'fr'   : {'channel':15,'imax':17000,'frate':6,'exptime':0.5},\
                              'noise': {'channel':1,'imax':0    ,'frate':21,'exptime':0.05}}
        self.psy_delay     = 0.1
        MAXDUTY            = 16*4095-1
        self.x1,self.x2    = 400,2100
        self.y1,self.y2    = 800, 2500
        self.framerate     = 1
        self.exposure_time = 0.2
        self.Navg          = 10

        try:
            from board import SCL, SDA
            import busio
            from adafruit_pca9685 import PCA9685
            i2c_bus = busio.I2C(SCL, SDA)
            self.pwm = PCA9685(i2c_bus)
            #pwm = Adafruit_PCA9685.PCA9685()
            self.pwm.frequency = 2000
            print("Adafruit_PCA9685 loaded")
            time.sleep(1)
        except Exception as e:
            self.pwm = None
            print("Adafruit_PCA9685 not found")
            print(e)
            time.sleep(1)

    def monitor(self):
        print('white','\t','green','\t','blue','\t','red','\t','farred')
        print(self.pwm.channels[7].duty_cycle,'\t',\
              self.pwm.channels[6].duty_cycle,'\t',\
              self.pwm.channels[5].duty_cycle,'\t',\
              self.pwm.channels[4].duty_cycle,'\t',\
              self.pwm.channels[2].duty_cycle)
        os.system('clear')

    def set_duty(self,color,newpwm):
        channel=self.ledconfig[color]["channel"]
        startpwm=self.pwm.channels[channel].duty_cycle
        delta=newpwm-startpwm
        step=np.sign(delta)
        if step == -1 or step == 1:
            for id in range(startpwm,newpwm,10*step):
                try:
                    self.pwm.channels[channel].duty_cycle = id
                    if channel==13:self.pwm.channels[14].duty_cycle = id
                    # self.monitor()
                except Exception as e:
                    print(e)
            self.pwm.channels[channel].duty_cycle = newpwm
                # time.sleep(1/np.abs(newpwm-startpwm))
        else:
            pass

        return 1

    def turn_all_off(self):
        for color in self.ledconfig.keys():
            self.set_duty(color,0)
        return 1

    def psychedelia(self):
        while True:
            for idx in range(0,360,1):
                rgb = hls_to_rgb(idx/360, 0.5, 1)
                self.pwm.channels[4].duty_cycle = round(rgb[0]*MAXDUTY)
                self.pwm.channels[6].duty_cycle = round(rgb[1]*MAXDUTY)
                self.pwm.channels[5].duty_cycle = round(rgb[2]*MAXDUTY)
                time.sleep(self.psy_delay)
            for idx in range(360,0,-1):
                rgb = hls_to_rgb(idx/360, 0.5, 1)
                self.pwm.channels[4].duty_cycle = round(rgb[0]*MAXDUTY)
                self.pwm.channels[6].duty_cycle = round(rgb[1]*MAXDUTY)
                self.pwm.channels[5].duty_cycle = round(rgb[2]*MAXDUTY)
                time.sleep(self.psy_delay)

    def _led_status_channel(self,color):
        channel=int(self.ledconfig[color]["channel"])
        return self.pwm.channels[channel].duty_cycle

    def led_status(self):
        print("color",'\t',"duty")
        for color in self.ledconfig.keys():
            print(color,'\t',self._led_status_channel(color))
        return None

    def get_suffix(self):
        suffix=""
        for color in self.ledconfig.keys():
            suffix+=color+str(self._led_status_channel(color))+"_"
        return suffix

    def measure_reflectance(self,color,img):
        if color=='w':id=[0,1,2]
        elif color=='r' or color=='fr':id=[0]
        elif color=='g': id=[1]
        elif color=='b': id=[2]
        reflectance = np.percentile(img, 95)/2**10
        return reflectance

    def CalibrateImax(self):
        import picamera
        import picamera.array
        outfolder="Radiometric/Imax/"
        if not os.path.isdir("Radiometric/"):os.makedirs("Radiometric/")
        if not os.path.isdir(outfolder):os.makedirs(outfolder)
        colors   = ['w','g','b','r','fr']
        colors   = ['g','b','r','fr']
        IMAXduty=[]
        for idx, color in enumerate(colors):
            step=0
            print('color = ',color )
            self.turn_all_off()
            while step<50:
                if color=='noise':self.turn_all_off()
                else:
                    ch   = self.ledconfig[color]["channel"]
                    imax = self.ledconfig[color]["imax"]+200*step
                    self.set_duty(color,imax)
                with picamera.PiCamera() as camera:
                    camera.framerate    = 24
                    time.sleep(0.05)
                    camera.exposure_mode = 'off'
                    with picamera.array.PiBayerArray(camera) as stream:
                        camera.capture(stream, 'jpeg',bayer=True)
                        output = stream.demosaic()
                if   color=="r" or color=="fr":id=[0]
                elif color=="g":               id=[1]
                elif color=="b":               id=[2]
                elif color=="w":               id=[0,1,2]
                r=self.measure_reflectance(color,output)
                print(color,'r = ',r,'max =',np.max(output),'imax=',imax)
                if r>0.80:
                    IMAXduty.append(imax)
                    break
                else:
                    step=step+1
                    continue
        np.save('imax_dutys.npy',IMAXduty)
        return 1

    def pic_tile(self):
        outfolder="Tiles/"
        if not os.path.isdir(outfolder):os.makedirs(outfolder)
        fr = input('Framerate: ')
        et = input("Expoisure time ")
        Navg = input("Number of averages ")
        self.framerate = int(fr)
        self.exposure_time = float(et)
        # output=self.read_bayer()
        output=self.average_capture(Navg=int(Navg))
        suffix=self.get_suffix()
        outpath = outfolder + suffix + "_frate" +fr + "_exptime" + et + "_Navg" + Navg + ".npy"
        print("saving sample img to ", outpath)
        np.save(outpath,output)
        time.sleep(2)

    def measure(self,crop=False):
        outfolder="Samples/"
        color=input("Select color channel: ")
        crop=input("crop image y/n?")
        if not os.path.isdir(outfolder):os.makedirs(outfolder)
        output=self.read_bayer()
        if crop=='y': output=output[self.x1:self.x2,self.y1:self.y2,:]
        r=self.measure_reflectance(color,output)
        suffix=self.get_suffix()
        outpath = outfolder + suffix + ".npy"
        print('r = ',r,'max =',np.max(output))
        print("saving sample img to ", outpath)
        np.save(outpath,output)
        time.sleep(2)

    def read_bayer(self):
        with picamera.PiCamera() as camera:
            camera.framerate    = self.framerate
            time.sleep(self.exposure_time)
            camera.exposure_mode = 'off'
            print("Frame rate = ", camera.framerate,"  exposure time = ", self.exposure_time)
            with picamera.array.PiBayerArray(camera) as output:
                camera.capture(output, 'jpeg', bayer=True)
                bayer=output.demosaic()
                # bayer=output.array
            del output
        del camera
        return bayer

    def multiple_shots(self,Navg):
        outfolder="MultipleAVG/"
        if not os.path.isdir(outfolder):os.makedirs(outfolder)
        for idx in range(Navg):
            output=self.read_bayer()
            suffix=self.get_suffix()
            outpath = outfolder + suffix + "_frate" +str(self.framerate) + "_exptime" + str(self.exposure_time) + "shot"+str(idx)+".npy"
            print("saving sample img to ", outpath)
            np.save(outpath,output)

    def average_capture(self,Navg=5):
        for idx in range(Navg):
            output=self.read_bayer()
            if idx==0:avg=output
            else:     avg+=output
        avg=avg/Navg
        avg = avg.astype(np.int)
        return avg

    def loop_params(self):
        outfolder="Tiles/"
        if not os.path.isdir(outfolder):os.makedirs(outfolder)
        exptimes  =  [0.01,0.02,0.05,0.07,0.1,0.15,0.2,0.3,0.5,1]
        framerates = [1,2,3,4,5]
        for exptime in exptimes:
            for framerate in framerates:
                self.framerate     = framerate
                self.exposure_time = exptime
                output=self.read_bayer()
                suffix=self.get_suffix()
                outpath = outfolder + suffix + "_frate" +str(framerate) + "_exptime" + str(exptime) + ".npy"
                print("saving sample img to ", outpath)
                np.save(outpath,output)

    def cal_tile(self):
        input("Start capturing white calibration tile?")
        colors   = ['w','g','b','r','fr']
        outfolder="Tiles/"
        if not os.path.isdir(outfolder):os.makedirs(outfolder)
        for idx, color in enumerate(colors):
            print('color = ',color )
            self.turn_all_off()
            if color=='noise':self.turn_all_off()
            else:
                ch   = self.ledconfig[color]["channel"]
                imax = self.ledconfig[color]["imax"]
                print(color,imax)
                self.set_duty(color,imax)
            self.framerate     = self.ledconfig[color]["frate"]
            self.exposure_time = self.ledconfig[color]["exptime"]
            output=self.read_bayer()
            print("saving sample img to ", outpath)
            np.save(outpath,output)
            time.sleep(2)
        return None

    def MultiSpectralPic(self,mode="signal",crop=False):
        if mode=="signal" : outfolder="Radiometric/Signal/"
        elif mode=="tile"  : outfolder="Radiometric/Tile/"
        if not os.path.isdir("Radiometric/"):os.makedirs("Radiometric/")
        if not os.path.isdir(outfolder):     os.makedirs(outfolder)
        colors   = ['w','g','b','r','fr','noise']
        for idx, color in enumerate(colors):
            print('color = ',color )
            self.turn_all_off()
            if color=='noise':self.turn_all_off()
            else:
                ch   = self.ledconfig[color]["channel"]
                imax = self.ledconfig[color]["imax"]
                print(color,imax)
                self.set_duty(color,imax)
            self.framerate     = int(self.ledconfig[color]["frate"])
            self.exposure_time = float(self.ledconfig[color]["exptime"])
            # output=self.read_bayer()
            output=self.average_capture(Navg=self.Navg)
            if crop: output=output[self.x1:self.x2,self.y1:self.y2,:]
            if mode=="signal" : suffix = mode+"_"+color+"_"+datetime.now().strftime("%d_%m_%Y_%H_%M")
            elif mode=="tile"  : suffix = mode+"_"+color
            outpath = outfolder + suffix + ".npy"
            print("saving image to ",outpath)
            np.save(outpath,output)
        return 1
