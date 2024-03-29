from Adafruit_PWM_Servo_Driver import PWM
from Light import Light


class Lighting:
    def __init__(self, config, pwm=False):
        # Initialise the PWM device using the default address
        if (pwm != False):
            self.pwm = pwm
        else:
            self.pwm = PWM(0x40, debug=True)
            self.pwm.setPWMFreq(1000)                        # Set frequency to 60 Hz
        self.flash_light = Light("flash", config.flash_light_pin, self.pwm)
        self.ready_light = Light("ready", config.ready_light_pin, self.pwm)
        self.three_light = Light("three", config.three_light_pin, self.pwm)
        self.two_light = Light("two", config.two_light_pin, self.pwm)
        self.one_light = Light("one", config.one_light_pin, self.pwm)
        self.all_lights = [self.flash_light, self.ready_light, self.three_light, self.two_light, self.one_light];
        self.flash_light.brightness = 2;
        self.ready_light.brightness = 0;
        self.three_light.brightness = 0;
        self.two_light.brightness = 0;
        self.one_light.brightness = 0;
        self.setLighting();

    def __str__(self):
        ret = "\nLighting"
        for light in self.all_lights:
            ret += str(light)
        return ret

    def setLightingThree(self):
        self.flash_light.brightness = 2;
        self.ready_light.brightness = 0;
        self.three_light.brightness = 100;
        self.two_light.brightness = 0;
        self.one_light.brightness = 0;
        self.setLighting();

    def setLightingTwo(self):
        self.flash_light.brightness = 2;
        self.ready_light.brightness = 0;
        self.three_light.brightness = 0;
        self.two_light.brightness = 100;
        self.one_light.brightness = 0;
        self.setLighting();

    def setLightingOne(self):
        self.flash_light.brightness = 2;
        self.ready_light.brightness = 0;
        self.three_light.brightness = 0;
        self.two_light.brightness = 0;
        self.one_light.brightness = 100;
        self.setLighting();

    def setLightingFlash(self):
        self.flash_light.brightness = 100;
        self.ready_light.brightness = 0;
        self.three_light.brightness = 0;
        self.two_light.brightness = 0;
        self.one_light.brightness = 0;
        self.setLighting();

    def setLightingError(self):
        self.flash_light.brightness = 2;
        self.ready_light.brightness = 0;
        self.three_light.brightness = 0;
        self.two_light.brightness = 0;
        self.one_light.brightness = 0;
        self.setLighting();

    def setLightingIdle(self):
        self.flash_light.brightness = 2;
        self.ready_light.brightness = 100;
        self.three_light.brightness = 0;
        self.two_light.brightness = 0;
        self.one_light.brightness = 0;
        self.setLighting();

    def setLighting(self):
         for light in self.all_lights:
            light.update();


