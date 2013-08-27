import light

class Lighting:
    def __init__(self):
        self.flash_light = Light("flash", 1, True)
        self.ready_light = Light("ready", 2, True)
        self.three_light = Light("three", 3, True)
        self.two_light = Light("two", 4, True)
        self.one_light = Light("one", 5, True)
        self.all_lights[self.flash_light, self.ready_light, self.three_light, self.two_light, self.one_light];
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


