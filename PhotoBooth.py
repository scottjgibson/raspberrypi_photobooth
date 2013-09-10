import piggyphoto
from fysom import Fysom
from ConfigParser import SafeConfigParser 
from Lighting import Lighting
import threading
import pygame
import time
import schnapphoto		
try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print("Error importing RPi.GPIO!  This is probably because you need superuser privileges.  You can achieve this by using 'sudo' to run your script")



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

# Transitions:
def onbeforeinitialize(e):
    print "---- INITIALIZE ----"
    print "Initialize Lighting"
    photo_booth.lighting.setLightingIdle();

    #print "Power Up Camera"
    #set camera power GPIO
    #wait a while

    photo_booth.photosRemaining = 3
    
    #print "Sanity check (disk space)"
    return True


def onbeforesnap_button(e):
    print "---- Photo Button Press ----"
    photo_booth.photosRemaining -= 1
    return True

def oncountdown(e):
    print "---- Photo Countdown ----"
    #3
    photo_booth.lighting.setLightingThree();
    print "Play Tick Noise"
    pygame.mixer.music.load("countdown_tick.wav")
    pygame.mixer.music.play()
    time.sleep(1)

    #2
    photo_booth.lighting.setLightingTwo();
    print "Play Tick Noise"
    pygame.mixer.music.load("countdown_tick.wav")
    pygame.mixer.music.play()
    time.sleep(1)

    #1
    photo_booth.lighting.setLightingOne();
    print "Play Tick Noise"
    pygame.mixer.music.load("countdown_tick.wav")
    pygame.mixer.music.play()
    time.sleep(1)

    photo_booth.lighting.setLightingFlash();
    print "Take Photo"
    try:
        if photo_booth.cameraError == False:
            photo_booth.camera.capture_image('file.jpg')
        else:
            print "no photo - camera error"
    except:
        print "Camera Error"
        photo_booth.cameraError = True;
        photo_booth.lighting.flash_light.brightness = 10;
        photo_booth.lighting.setLighting();

    if photo_booth.cameraError == True:
        photo_booth.stateMachine.camera_error()
    else:
        photo_booth.stateMachine.photo_complete()
    

    return True

def oncamera_error(e):
    print "---- CAMERA ERROR ----"
    photo_booth.lighting.setLightingError()
    while photo_booth.cameraError == True:
        print "Cycle Camera Power"
        print "wait a while"
        try:
            self.camera = piggyphoto.camera()
            self.cfile = piggyphoto.cameraFile()
            self.cameraError = False
        except:
            print "camera init failed"
            self.cameraError = True
        
    


def onbeforephoto_complete(e):
    print "---- PHOTO COMPLETE ----"
    photo_booth.photosRemaining = 3
    photo_booth.lighting.setLightingIdle()
    return True



class PhotoBooth:
    def __init__(self, config_file):
        try:
            self.camera = piggyphoto.camera()
            self.cfile = piggyphoto.cameraFile()
            self.cameraError = False
        except:
            print "camera init failed"
            self.cameraError = True
        self.photosRemaining = 3
        self.lighting_config = LightingConfig()
        self.parseConfigFile(config_file)
        GPIO.setmode(GPIO.BOARD)
        pygame.mixer.init()
        self.lighting = Lighting(self.lighting_config)
        self.verbose = False
        GPIO.setup(self.shutter_switch_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(self.shutter_switch_pin, GPIO.FALLING, callback=self.shutter_switch_callback)
        pygame.mixer.music.set_volume(1)
        pygame.mixer.music.load("startup.wav")
        pygame.mixer.music.play()
        self.stateMachine = Fysom({
            'initial': 'uninitialized',
            'events':[
                {'name': 'initialize', 'src':['uninitialized', 'idle', 'countdown'], 'dst':'idle'},
                {'name': 'photo_complete', 'src':['uninitialized', 'idle', 'countdown'], 'dst':'idle'},
                {'name': 'camera_error', 'src':['uninitialized', 'idle', 'countdown'], 'dst':'idle'},
                {'name': 'snap_button', 'src':'idle', 'dst':'countdown'}],
            'callbacks':{
                'onbeforephoto_complete': onbeforephoto_complete,
                'onbeforeinitialize': onbeforeinitialize,
                'onbeforesnap_button': onbeforesnap_button,
                'oncountdown': oncountdown}})

    #callback used when a button is pressed (tied to GPIO pin)
    def shutter_switch_callback(self, e="no arg"):
        if self.stateMachine.current == 'idle':
            self.stateMachine.snap_button()


    def parseConfigFile(self, configFile):
        config = SafeConfigParser()
        config.read(configFile)
        self.vebose = config.getboolean('general_config', 'verbose')
        self.shutter_switch_pin  = config.getint('general_config', 'shutter_switch_pin')
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
        if self.stateMachine.current == "idle":
            print "---- PERIODIC TASK ---- : SANITY CHECK"
            print "---- PERIODIC TASK ---- : CHANGE MARQEE PIC"
        else:
            print "---- PERIODIC TASK ---- : SKIPPING - Not Idle"
        threading.Timer(10, self.periodicTask).start()

    def run(self):
        self.stateMachine.initialize()
        self.periodicTask()


photo_booth = PhotoBooth('config.ini')





if __name__ == '__main__':
    photo_booth.run()
    time.sleep(3)
    photo_booth.shutter_switch_callback();
    time.sleep(15)
    photo_booth.shutter_switch_callback();
    time.sleep(300)

