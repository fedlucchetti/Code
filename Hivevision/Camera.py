import numpy as np
import picamera

from picamera import PiCamera
import time, pathlib, os
from shutil import copyfile


class Camera():
    def __init__(self):
        print("Initializing Pi Camera Class with default parameters")
        self.outfolder = "../data/raw/"
        self.serverfolder = "/var/www/html/"
        self.xRes = 1280
        self.yRes = 720
        # self.camobj = PiCamera()
        # self.camobj.resolution = (self.xRes,self.yRes)
        return None

    def capture(self,path=None,upload=False,exposure_time=0.1):
        # self.camobj.resolution = self.camobj.MAX_IMAGE_RESOLUTION
        if path!=None:
            pass
        else:
            count = 0
            for path in pathlib.Path(self.outfolder).iterdir():
                if path.is_file():
                    count+=1
            path = self.outfolder + 'sample_' + str(count) + '.npy'
        import picamera.array
        with picamera.PiCamera() as camera:
            camera.iso=0
            camera.framerate    = 24
            camera.exposure_mode = 'snow'
            with picamera.array.PiBayerArray(camera) as stream:
                time.sleep(exposure_time)
                camera.capture(stream, 'jpeg',bayer=True)
                output = stream.demosaic()
                # camera.capture(path)
        if upload:
            print("Uploading to server...")
            # tail = os.path.split(path)
            # copyfile(path, self.serverfolder +"raw/"+ tail[1])
            np.save(path,output)
            print("Saved to ",path)
            input("Click enter to continue ")
        return 1

    def capture_custom1(self,folderpath,upload=False):
        self.check_create_folder(folderpath)
        with picamera.PiCamera() as camera:
            camera.resolution = (self.xRes, self.yRes)
            camera.framerate = 30
            time.sleep(2)
            camera.shutter_speed = camera.exposure_speed
            camera.exposure_mode = 'off'
            g = camera.awb_gains
            camera.awb_mode = 'off'
            camera.awb_gains = g
            # Finally, take several photos with the fixed settings
            camera.capture_sequence([folderpath + 'image%02d.data' % i for i in range(10)],'yuv')

        # print("Picture saved to", path)
        if upload:
            print("Uploading to server...")
            tail = os.path.split(path)
            copyfile(path, self.serverfolder +"raw/"+ tail[1])
            print("Done uploading")
        return 1

    def check_create_folder(self,folderpath):
        if not os.path.isdir(folderpath):
            os.makedirs(folderpath)
            print("created new output folder : ", folderpath)
        return 1


if __name__ == "__main__":
    picam      = Camera()
    picam.capture(upload=True)
