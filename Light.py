from numpy import interp
import RPi.GPIO as GPIO
from Adafruit_PWM_Servo_Driver import PWM

# Initialise the PWM device using the default address
class Light:
    def __init__(self, name, gpio_pin, pwm):
        self.name = name;
        self.brightness = 0;
        self.gpio_pin = gpio_pin;
        self.pwm = pwm;
        print "Light Init"
        self.pwm.setPWM(self.gpio_pin, 0, int(round(interp(self.brightness, [0, 100], [0, 4095]))))

    def __str__(self):
        ret = "\nName: %s\n" %  self.name 
        ret += "Brightness: %s\n" % self.brightness
        ret += "GPIO Pin: %s\n" % self.gpio_pin
        return ret
    def update(self):
        print "%s (Pin: %d):%d" % (self.name, self.gpio_pin, self.brightness)
        self.pwm.setPWM(self.gpio_pin, 0, int(round(interp(self.brightness, [0, 100], [0, 4095]))))

