from fysom import Fysom
from ConfigParser import SafeConfigParser 
from Lighting import Lighting



photosRemaining = 3

# Transitions:
def oninitialize(e):
    photosRemaining = 3
    print "Power Up Camera"
    print "Initialize Lighting"
    print "Sanity check (disk space)"
    print "Lock Camera"
    print "Test Camera"
    return True

def countownThree():
    print "Turn Off Ready Lamp"
    print "Turn On Three Lamp"
    print "Play Tick Noise"
    return True

def countownToTwo():
    print "Turn Off Three Lamp"
    print "Turn On Two Lamp"
    print "Play Tick Noise"
    return True

def countownToOne():
    print "Turn Off Two Lamp"
    print "Turn On One Lamp"
    print "Play Tick Noise"
    return True

def onsnap_button(e):
    photosRemaining -= 1
    print "Turn Off One Lamp"
    print "Turn On Flash Lamp"
    print "Turn Off Two Lamp"
    print "Turn On One Lamp"
    print "Play Tick Noise"
    return True

def imageAquired():
    print "Turn off flash"
    return True

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
        self.lighting_config = LightingConfig()
        self.parseConfigFile(config_file)
        self.lighting = Lighting(self.lighting_config)
        self.verbose = False
        self.stateMachine = Fysom({
            'initial': 'uninitialized',
            'events':[
                {'name': 'initialize', 'src':'uninitialized', 'dst':'idle'},
                {'name': 'snap_button', 'src':'idle', 'dst':'countdown_three'}],
            'callbacks':{
                'oninitialize': oninitialize,
                'onsnap_button': onsnap_button }})



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



if __name__ == '__main__':
    photo_booth  = PhotoBooth('config.ini')
    photo_booth.run()

