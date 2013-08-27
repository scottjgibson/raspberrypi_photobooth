class Light:
    def __init__(self, name, gpio_pin, pwm_support):
        self.name = name;
        self.brightness = 0;
        self.gpio_pin = gpio_pin;
        self.pwm_support = pwm_support;
    def __str__(self):
        ret = "\nName: %s\n" %  self.name 
        ret += "Brightness: %s\n" % self.brightness
        ret += "PWM Supported: %s\n" % self.pwm_support
        ret += "GPIO Pin: %s\n" % self.gpio_pin
        return ret
    def update(self):
        if (self.pwm_support):
            #Update GPIO output
        else:
            if (brightness > 0):
                #set pin on
            else:
                #turn pin off

