#!/usr/bin/python

import piggyphoto
from Adafruit_PWM_Servo_Driver import PWM
from ConfigParser import SafeConfigParser 
from Lighting import Lighting
import threading
import pygame
import time
# import schnapphoto        
import datetime
import os
import logging
import sys
import os
from collections import namedtuple
import traceback
import pygame

try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print("Error importing RPi.GPIO!  This is probably because you need superuser privileges.  You can achieve this by using 'sudo' to run your script")

_ntuple_diskusage = namedtuple('usage', 'total used free')

def disk_usage(path):
    """Return disk usage statistics about the given path.

    Returned valus is a named tuple with attributes 'total', 'used' and
    'free', which are the amount of total, used and free space, in bytes.
    """
    st = os.statvfs(path)
    free = st.f_bavail * st.f_frsize
    total = st.f_blocks * st.f_frsize
    used = (st.f_blocks - st.f_bfree) * st.f_frsize
    return _ntuple_diskusage(total, used, free)


button_pressed = False


class LightingConfig():
    def __init__(self):
        self.ready_pwm_support = False
        self.flash_light_pin = 0
        self.flash_pwm_support = False
        self.three_light_pin = 0
        self.three_pwm_support = False
        self.two_light_pin = 0
        self.two_pwm_support = False
        self.one_light_pin = 0
        self.one_pwm_support = False


class PhotoBooth:
    def __init__(self, config_file):
        self.storage_path = []
        self.display_image_files = []
        self.display_image_index = 0
        main_log_file = datetime.datetime.now().strftime("logs/%I%M%p_%B_%d_%Y.log")
        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                            datefmt='%m-%d %H:%M',
                            filename='logs/photo_booth.log',
                            filemode='w')

        console = logging.StreamHandler()
        console.setLevel(logging.INFO)        
        # set a format which is simpler for console use
        formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
        # tell the handler to use this format
        console.setFormatter(formatter)
        # add the handler to the root logger
        logging.getLogger('').addHandler(console)

        self.main_logger = logging.getLogger("Main")
        self.maintenance_logger = logging.getLogger("Maintenance")
        self.lighting_logger = logging.getLogger("Lighting")
        self.camera_logger = logging.getLogger("Camera")
        self.lighting_logger.info("Setup Lighting")
        self.pwm = PWM(0x40, debug=True)
        self.pwm.setPWMFreq(1000)                        # Set frequency to 60 Hz
        self.lighting_config = LightingConfig()
        self.parseConfigFile(config_file)
        self.lighting = Lighting(self.lighting_config, self.pwm)
        self.lighting_logger.debug(self.lighting)
        self.lighting_logger.info("Setup Lighting - OK")
        GPIO.setmode(GPIO.BOARD)
        pygame.mixer.init()
        self.lighting_logger.info("Setup Lighting - OK")
        self.camera_logger.info("Setup Camera")
        self.cameraError = True
        while self.cameraError == True:
            self.powerDownCamera()
            time.sleep(1)
            self.powerUpCamera()
            time.sleep(5)
            os.system("sudo lsusb | grep Canon | sed 's/Bus\ /sudo\ \/home\/pi\/usbreset\ \/dev\/bus\/usb\//' | sed 's/\ Device\ /\//' | sed 's/:.*//' > /home/pi/resetcmd")
            os.system("sh /home/pi/resetcmd")
            time.sleep(1)
            try:
                self.camera = piggyphoto.camera()
                self.cfile = piggyphoto.cameraFile()
                self.cameraError = False
                self.camera_logger.info("Setup Camera - OK")
            except:
                self.camera_logger.error("Setup Camera - Error")
                self.cameraError = True

        self.photosRemaining = 3
        self.main_logger.info("Setup Button Input")
        self.verbose = False
        GPIO.setup(self.shutter_switch_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(self.shutter_switch_pin, GPIO.FALLING, callback=self.shutter_switch_callback)
        self.main_logger.info("Setup Button Input - OK")
        self.main_logger.info("Setup Video Display")
#        pygame.mixer.music.set_volume(1)
#        pygame.mixer.music.load("startup.wav")
#        pygame.mixer.music.play()
#        pygame.init()
#        self.screen = pygame.display.set_mode((0, 0))
#        self.clock = pygame.time.Clock()
        self.main_logger.info("Setup Video Display - OK")

    def powerUpCamera(self):
        self.main_logger.info("Power Up Camera")
        self.pwm.setPWM(self.camera_power_pin, 0, 4095)

    def powerDownCamera(self):
        self.main_logger.info("Power Down Camera")
        self.pwm.setPWM(self.camera_power_pin, 0, 0)

    #callback used when a button is pressed (tied to GPIO pin)
    def shutter_switch_callback(self, e="no arg"):
        global button_pressed
        if (button_pressed == False):
            self.main_logger.info("Shutter Button Pressed")
            button_pressed = True


    def parseConfigFile(self, configFile):
        config = SafeConfigParser()
        config.read(configFile)
        self.vebose = config.getboolean('general_config', 'verbose')
        self.shutter_switch_pin  = config.getint('general_config', 'shutter_switch_pin')
        self.camera_power_pin  = config.getint('general_config', 'camera_power_pin')
        self.lighting_config.ready_light_pin = config.getint('lighting_config', 'ready_light_pin')
        self.lighting_config.ready_pwm_support = config.getboolean('lighting_config', 'ready_light_pwm_support')
        self.lighting_config.flash_light_pin = config.getint('lighting_config', 'flash_light_pin')
        self.lighting_config.flash_pwm_support = config.getboolean('lighting_config', 'flash_light_pwm_support')
        self.lighting_config.three_light_pin = config.getint('lighting_config', 'three_light_pin')
        self.lighting_config.three_pwm_support = config.getboolean('lighting_config', 'three_light_pwm_support')
        self.lighting_config.two_light_pin = config.getint('lighting_config', 'two_light_pin')
        self.lighting_config.two_pwm_support = config.getboolean('lighting_config', 'two_light_pwm_support')
        self.lighting_config.one_light_pin = config.getint('lighting_config', 'one_light_pin')
        self.lighting_config.one_pwm_support = config.getboolean('lighting_config', 'one_light_pwm_support')

    def periodicTask(self):
        if len(self.display_image_files) > self.display_image_index:
            print self.display_image_files
            print "displaying image index: %d" % self.display_image_index
            print "Display Image %s/%s" % (self.storage_path, self.display_image_files[self.display_image_index])
            if os.path.isfile("%s/%s" % (self.storage_path, self.display_image_files[self.display_image_index])):
                image = pygame.image.load("%s/%s" % (self.storage_path, self.display_image_files[self.display_image_index]))
                image = pygame.transform.scale(image,(720,480))
                self.screen.fill((255,255,255))
                self.screen.blit(image,(0,0))
                self.clock.tick(1)
                pygame.display.flip()   
            self.display_image_index += 1
        else:
            self.display_image_index = 0

        threading.Timer(10, self.periodicTask).start()

    def maintenanceTask(self):
        #if self.stateMachine.current == "idle":
        root_usage = disk_usage("/")
        self.maintenance_logger.info("Root Disk Free Space: %d MB" % (int(root_usage.free) / (1024 * 1024)))
        if (root_usage.free < 10*1024*1024):
            self.maintenance_logger.error("Low Disk Space: %d MB Free" % (int(usb_usage.free) / (1024 * 1024)))
        usb_usage = disk_usage("/mnt/usb_drive")
        self.maintenance_logger.info("USB Disk Free Space: %d MB" % (int(usb_usage.free) / (1024 * 1024)))
        if (usb_usage.free < 10*1024*1024):
            self.maintenance_logger.error("Low Disk Space: Change USB Drive - %d MB Free" % (int(usb_usage.free) / (1024 * 1024)))
        self.maintenance_logger.info("Update Marqee Picture")
        threading.Timer(30, self.maintenanceTask).start()

    def run(self):
#        self.maintenanceTask()
#        self.periodicTask()
        self.main_loop()

    def main_loop(self):
        global button_pressed
        self.main_logger.info("Initializing")

        usb_drive_path = "/mnt/usb_drive"
        if (os.path.ismount(usb_drive_path) == False):
            self.main_logger.error("USB Drive not mounted - try mounting")
            os.system("mount /mnt/usb_drive")
            time.sleep(0.5)
            if (os.path.ismount(usb_drive_path) == False):
                self.main_logger.error("Unable to mount USB drive")
                sys.exit(0)
            else:
                self.main_logger.info("Successfully mounted USB Drive")

        self.storage_path = datetime.datetime.now().strftime("/mnt/usb_drive/%I%M%p_%B_%d_%Y")

        image_index = 0


        self.main_logger.info("make directory for photos: %s" % self.storage_path)
        if not os.path.exists(self.storage_path):
            os.makedirs(self.storage_path)    
        

        log_file = "%s/log.txt" % self.storage_path

        root_usage = disk_usage("/")
        self.main_logger.info(root_usage)
        self.main_logger.info("Root Disk Free Space: %d MB" % (int(root_usage.free) / (1024 * 1024)))
        if (root_usage.free < 10*1024*1024):
            self.main_logger.error("Low Disk Space: %d MB Free" % (int(usb_usage.free) / (1024 * 1024)))
        usb_usage = disk_usage(usb_drive_path)
        self.main_logger.info(usb_usage)
        self.main_logger.info("USB Disk Free Space: %d MB" % (int(usb_usage.free) / (1024 * 1024)))
        if (usb_usage.free < 10*1024*1024):
            self.main_logger.error("Low Disk Space: Change USB Drive - %d MB Free" % (int(usb_usage.free) / (1024 * 1024)))


        #Button was pressed
        while (True):
            self.lighting.setLightingIdle();
            button_pressed = False
            self.photosRemaining = 3
            self.display_image_files = sorted(os.listdir(self.storage_path), reverse=True)
            
            all_files = ''
            for fn in self.display_image_files:
                all_files += " %s/%s" % (self.storage_path, fn)
            if len(self.display_image_files):
                _cmd = "sudo /usr/bin/nice -n 18 fbi -a --noverbose -T 2 -t 5 %s &" % all_files
                print _cmd
                os.system("sudo pkill fbi")
                os.system(_cmd)
            else:
                _cmd = "sudo /usr/bin/nice -n 18 fbi -a --noverbose -T 2 /home/pi/git/raspberrypi_photobooth/logo.jpg"
                print _cmd
                os.system("sudo pkill fbi")
                os.system(_cmd)

            self.display_image_index = 0
            GPIO.setup(self.shutter_switch_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.remove_event_detect(self.shutter_switch_pin)
            GPIO.add_event_detect(self.shutter_switch_pin, GPIO.FALLING, callback=self.shutter_switch_callback)

            self.main_logger.info("Waiting for button press")
            while not (button_pressed):
                time.sleep(1)
            os.system("sudo pkill fbi")
	    _cmd = "sudo /usr/bin/nice -n 18 fbi -a --noverbose -T 2 /home/pi/git/raspberrypi_photobooth/logo.jpg"
	    os.system("sudo pkill fbi")
	    os.system(_cmd)

            self.main_logger.info("got button press")

            while (self.photosRemaining):
                self.main_logger.info("Countdown")
                #3
                self.lighting.setLightingThree();
                pygame.mixer.music.load("countdown_tick.wav")
                pygame.mixer.music.play()
                time.sleep(1.5)

                #2
                self.lighting.setLightingTwo();
                pygame.mixer.music.load("countdown_tick.wav")
                pygame.mixer.music.play()
                time.sleep(1.5)

                #1
                self.lighting.setLightingOne();
                pygame.mixer.music.load("countdown_tick.wav")
                pygame.mixer.music.play()
                time.sleep(1.5)

                self.lighting.setLightingFlash();
                self.main_logger.info("Take Photo")
                try:
                    if self.cameraError == False:
                        self.camera_logger.info("capturing %s/%05d.jpg" % (self.storage_path, image_index))
                        self.camera.capture_image("%s/%04d.jpg" %(self.storage_path, image_index))
                    else:
                        self.camera_logger.error("Camera Error 1 - can't run capture_image")
                        self.cameraError = True;
                        self.lighting.flash_light.brightness = 10;
                        self.lighting.setLighting();
                except:
                    self.camera_logger.error("Camera Error 2 - can't run capture_image")
                    self.cameraError = True;
                    self.lighting.flash_light.brightness = 10;
                    self.lighting.setLighting();

                image_index += 1

                if self.cameraError == True:
                    self.camera_logger.error("Starting Camera Error Recovery")
                    self.lighting.setLightingError()
                    while self.cameraError == True:
                        self.powerDownCamera()
                        time.sleep(1)
                        self.powerUpCamera()
                        time.sleep(5)
                        os.system("sudo lsusb | grep Canon | sed 's/Bus\ /sudo\ \/home\/pi\/usbreset\ \/dev\/bus\/usb\//' | sed 's/\ Device\ /\//' | sed 's/:.*//' > /home/pi/resetcmd")
                        os.system("sh /home/pi/resetcmd")
                        time.sleep(1)
                        try:
                            self.camera = piggyphoto.camera()
                            self.cfile = piggyphoto.cameraFile()
                            self.cameraError = False
                            self.camera_logger.error("Camera Recovered")
                        except:
                            self.camera_logger.error("Camera Recovery Failed")
                            self.cameraError = True


                self.main_logger.info("Photo Complete %d" % self.photosRemaining)
                print "---- PHOTO COMPLETE ----"
                self.photosRemaining -= 1
                self.lighting.setLightingIdle()



photo_booth = PhotoBooth('config.ini')

if __name__ == '__main__':
    try:
        photo_booth.run()
    except KeyboardInterrupt:
        print "Shutdown requested...exiting"
    except Exception:
        traceback.print_exc(file=sys.stdout)
    sys.exit(0)

