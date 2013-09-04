import RPi.GPIO as GPIO

class Light:
    def __init__(self, name, gpio_pin, pwm_support):
        self.name = name;
        self.brightness = 0;
        self.gpio_pin = gpio_pin;
        self.pwm_support = pwm_support;
        GPIO.setup(self.gpio_pin, GPIO.OUT, pull_up_down=GPIO.PUD_DOWN)
        if pwm_support:
            # 60Hz PWM frequency
            self.p = GPIO.PWM(self.gpio_pin, 60)
            self.p.start(0)
            self.p.ChangeDutyCycle(0)
        else:
            GPIO.output(self.gpio_pin, GPIO.LOW)
    def __str__(self):
        ret = "\nName: %s\n" %  self.name 
        ret += "Brightness: %s\n" % self.brightness
        ret += "PWM Supported: %s\n" % self.pwm_support
        ret += "GPIO Pin: %s\n" % self.gpio_pin
        ret += "status: %s\n" % GPIO.input(self.gpio_pin)
        return ret
    def update(self):
        if (self.brightness > 0):
            if (self.pwm_support):
                self.p.ChangeDutyCycle(self.brightness)
                print "%s (Pin: %d) ON (%d%%)" % (self.name, self.gpio_pin, self.brightness)

            else:
                GPIO.output(self.gpio_pin, GPIO.HIGH)
                print "%s (Pin: %d) ON" % (self.name, self.gpio_pin)
    
        else:
            GPIO.output(self.gpio_pin, GPIO.LOW)
            print "%s (Pin: %d) OFF" % (self.name, self.gpio_pin)

