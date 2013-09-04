from Light import Light

class Lighting:
    def __init__(self, config):
        self.flash_light = Light("flash", config.flash_light_pin, True)
        self.ready_light = Light("ready", config.ready_light_pin, True)
        self.three_light = Light("three", config.three_light_pin, True)
        self.two_light = Light("two", config.two_light_pin, True)
        self.one_light = Light("one", config.one_light_pin, True)
        self.all_lights = [self.flash_light, self.ready_light, self.three_light, self.two_light, self.one_light];
        self.flash_light.brightness = 10;
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

    def setLighting(self):
         for light in self.all_lights:
            light.update();


