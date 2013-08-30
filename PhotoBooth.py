import piggyphoto
from fysom import Fysom
from ConfigParser import SafeConfigParser 
from Lighting import Lighting
import pygame
import time

#callback used when a button is pressed (tied to GPIO pin)
def button_pressed():
    if photo_booth.stateMachine.current == 'idle':
        photo_booth.stateMachine.snap_photo()

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
    print "Initialize Lighting"
    photo_booth.lighting.flash_light.brightness = 10;
    photo_booth.lighting.ready_light.brightness = 0;
    photo_booth.lighting.three_light.brightness = 0;
    photo_booth.lighting.two_light.brightness = 0;
    photo_booth.lighting.one_light.brightness = 0;
    photo_booth.lighting.one_light.brightness = 0;
    photo_booth.lighting.setLighting();

    print "Power Up Camera"
    #set camera power GPIO
    #wait a while

    #see if camera is available
    try: 
        photo_booth.camera = piggyphoto.camera()
        photo_booth.camera.init()
    finally:
        print "Camera can not be initialized"
        time.sleep(2)
        photo_booth.stateMachine.initialize()
        return False

    photo_booth.photosRemaining = 3

    
    print "Sanity check (disk space)"
    return True

def onbeforesnap_button(e):
    print "Button Pressed"
    photo_booth.photosRemaining -= 1
    return True

def oncountdown(e):
    #3
    print "Turn Off Ready Lamp"
    photo_booth.lighting.ready_light.brightness = 0;
    print "Turn On Three Lamp"
    photo_booth.lighting.three_light.brightness = 100;
    photo_booth.lighting.setLighting();
    print "Play Tick Noise"
    pygame.mixer.music.load("countdown_tick.wav")
    pygame.mixer.music.play()
    time.sleep(1)

    #2
    print "Turn Off Three Lamp"
    photo_booth.lighting.three_light.brightness = 0;
    print "Turn On Two Lamp"
    photo_booth.lighting.two_light.brightness = 100;
    photo_booth.lighting.setLighting();
    print "Play Tick Noise"
    pygame.mixer.music.load("countdown_tick.wav")
    pygame.mixer.music.play()
    time.sleep(1)

    #1
    print "Turn Off Two Lamp"
    photo_booth.lighting.two_light.brightness = 0;
    print "Turn On One Lamp"
    photo_booth.lighting.one_light.brightness = 100;
    photo_booth.lighting.setLighting();
    print "Play Tick Noise"
    pygame.mixer.music.load("countdown_tick.wav")
    pygame.mixer.music.play()
    time.sleep(1)

    print "Turn Off One Lamp"
    photo_booth.lighting.one_light.brightness = 0;
    print "Turn On Flash Lamp"
    photo_booth.lighting.flash_light.brightness = 100;
    photo_booth.lighting.setLighting();
    print "Take Photo"
    try:
        camera.capture_image('file.jpg')
    finally:
        print "Camera Error"
    photo_booth.lighting.flash_light.brightness = 0;
    photo_booth.lighting.setLighting();

    return True


def onidle(e):
    photo_booth.photosRemaining = 3
    photo_booth.lighting.flash_light.brightness = 10;
    photo_booth.lighting.ready_light.brightness = 100;
    photo_booth.lighting.three_light.brightness = 0;
    photo_booth.lighting.two_light.brightness = 0;
    photo_booth.lighting.one_light.brightness = 0;
    photo_booth.lighting.setLighting();
    print "Update Marqee Display"
    return True



class PhotoBooth:
    def __init__(self, config_file):
        self.photosRemaining = 3
        self.lighting_config = LightingConfig()
        self.parseConfigFile(config_file)
        self.lighting = Lighting(self.lighting_config)
        self.verbose = False
        pygame.mixer.init()
        pygame.mixer.music.set_volume(1)
        pygame.mixer.music.load("startup.wav")
        pygame.mixer.music.play()
        self.stateMachine = Fysom({
            'initial': 'uninitialized',
            'events':[
                {'name': 'initialize', 'src':['uninitialized', 'idle', 'coundown', 'take_photo'], 'dst':'idle'},
                {'name': 'snap_button', 'src':'idle', 'dst':'countdown'}],
            'callbacks':{
                'onbeforeinitialize': onbeforeinitialize,
                'onbeforesnap_button': onbeforesnap_button,
                'oncountdown': oncountdown}})



    def parseConfigFile(self, configFile):
        config = SafeConfigParser()
        config.read(configFile)
        self.vebose = config.getboolean('general_config', 'verbose')
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

    def run(self):
        self.stateMachine.initialize()
        #start periodic timer


photo_booth = PhotoBooth('config.ini')





if __name__ == '__main__':
    photo_booth.run()
    time.sleep(1)
    button_pressed();
    time.sleep(1)

