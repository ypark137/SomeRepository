import threading
from time import sleep

from pymba import *
import numpy as np
import cv2
import time
import labrad
from labrad.units import WithUnit as U

from subprocess import Popen



class Test(object):

    def __init__(self):
        self.threads=[]
        self.running=True
        cxn=labrad.connect()
        self.pulser=cxn.pulser

    def hardwareTrigger(self):



            vimba=Vimba()

            vimba.startup()

            system = vimba.getSystem()
            system.runFeatureCommand("GeVDiscoveryAllOnce")

            cameraIds = vimba.getCameraIds()

            camera = vimba.getCamera(cameraIds[0])

            camera.openCamera()

            camera.AcquisitionMode = 'Continuous'
            camera.TriggerMode = 'On'
            camera.TriggerSource='Line2'

            frame = camera.getFrame()
            frame2= camera.getFrame()

            frame.announceFrame()
            frame2.announceFrame()

            camera.startCapture()

            frame.queueFrameCapture()
            frame2.queueFrameCapture()

            frame.waitFrameCapture(5000)

            print 'frame 1 captured or timed out '

            frame2.waitFrameCapture(5000)

            print 'frame 2 captured or timed out'

            imgData1=frame.getBufferByteData()
            imgData2=frame2.getBufferByteData()

            camera.endCapture()

            moreUsefulImgData = np.ndarray(buffer = frame.getBufferByteData(),
                                           dtype = np.uint8,
                                           shape = (frame.height,
                                                    frame.width,
                                                    1))

            rgb = cv2.cvtColor(moreUsefulImgData, cv2.COLOR_BAYER_RG2RGB)

            cv2.imwrite('waitYouna5.png'.format(1), rgb)


            moreUsefulImgData2 = np.ndarray(buffer = frame2.getBufferByteData(),
                                            dtype = np.uint8,
                                            shape = (frame2.height,

                                                     frame2.width,
                                                     1))

            rgb2 = cv2.cvtColor(moreUsefulImgData2, cv2.COLOR_BAYER_RG2RGB)

            cv2.imwrite('waitYouna6.png'.format(1), rgb2)

            print 'images saved'

            camera.revokeAllFrames()

            self.pulser.stop_sequence()

    def sequence(self):
            pulser=self.pulser

           # pulser.switchAuto=('TTL2',True)

            time.sleep(2)
            pulser.new_sequence()

            #second image not saved
            pulser.add_ttl_pulse('TTL2',U(100,'ms'),U(5,'ms'))
            pulser.add_ttl_pulse('TTL2',U(135,'ms'), U(5,'ms'))
            pulser.add_ttl_pulse('TTL3',U(110,'ms'), U(10,'ms'))
            pulser.add_ttl_pulse('TTL3',U(125,'ms'), U(10,'ms'))
            # pulser.add_ttl_pulse('TTL4', U(350, 'ms'), U(100, 'ms'))
            # pulser.add_ttl_pulse('TTL5', U(350, 'ms'), U(100, 'ms'))
            # pulser.add_ttl_pulse('TTL6', U(350, 'ms'), U(100, 'ms'))
            # pulser.add_ttl_pulse('TTL7', U(350, 'ms'), U(100, 'ms'))

            pulser.program_sequence()

            pulser.start_number(1)


    def go(self):
        t1=threading.Thread(target=self.hardwareTrigger)
        t1.start()
        t2=threading.Thread(target=self.sequence)

        t2.start()
        self.threads.append(t1)
        self.threads.append(t2)


def join_threads(threads):
    for t in threads:
        while t.isAlive():
            t.join(5)


def main():
    t=Test()
    t.go()
    join_threads(t.threads)

if __name__ == "__main__":
    main()