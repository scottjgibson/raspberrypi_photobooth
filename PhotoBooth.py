import StateMachine

class State:
    def __init__(self, name): self.name = name
    def __str__(self): return self.name

State.uninitialized = State("Uninitialize")
State.idle = State("Idle")
State.countdown_three = State("Countdown_Three")
State.countdown_two = State("Countdown_Two")
State.countdown_one = State("Countdown_One")
State.snap_photo = State("Snap Photo")
State.wait_photo = State("Waiting For Photo")

class Action:
    def __init__(self,name):
        self.name = name;
    def __str__(self): return self.name

Action.Initialize = Action("Triggered Initialization")
Action.ButtonPress = Action("Button Press")
Action.TimerExpired = Action("Timer Expired")
Action.ImageAquired = Action("Image Successfuly Aquired")
Action.ImageAquiryFailed = Action("Image Failed To Be Aquired")


class Quit:
    def __str__(self): return "Quit"
Quit.quit = Quit()


class PhotoBoothStateMachine(StateMachine):
    photosRemaining = 3

    # Conditions:
    def photosRemaining(self):
        return photosRemaining > 3

    # Transitions:
    def initialize(self, input):
        photosRemaining = 3
        print "Power Up Camera"
        print "Initialize Lighting"
        print "Sanity check (disk space)"
        print "Lock Camera"
        print "Test Camera"

    def countownStart(self, input):
        print "Turn Off Ready Lamp"
        print "Turn On Three Lamp"
        print "Play Tick Noise"

    def countownToTwo(self, input):
        print "Turn Off Three Lamp"
        print "Turn On Two Lamp"
        print "Play Tick Noise"

    def countownToOne(self, input):
        print "Turn Off Two Lamp"
        print "Turn On One Lamp"
        print "Play Tick Noise"

    def triggerCamera(self, input):
        photosRemaining -= 1
        print "Turn Off One Lamp"
        print "Turn On Flash Lamp"
        print "Turn Off Two Lamp"
        print "Turn On One Lamp"
        print "Play Tick Noise"

    def imageAquired(self,input):
        print "Turn off flash"

    def __init__(self):
        StateMachine.__init__(self, State.uninitialized)

        """
        buildTable(Object[][][]{
         ::State.uninitialized, # Current state
            # Input, test, transition, next state:
           :Initialize.class, null,
             initialize, State.idle,
         ::State.idle, # Current state
            # Input, test, transition, next state:
           :ButtonPress.class, null,
             countdownStart, State.countdown_three,
         ::State.countdown_three, # Current state
            # Input, test, transition, next state:
           :TimerExpired, null,
             countdownToTwo, State.countdown_two,
         ::State.countdown_two, # Current state
            # Input, test, transition, next state:
           :TimerExpired, null,
             countdownToOne, State.countdown_one,
         ::State.countdown_one, # Current state
            # Input, test, transition, next state:
           :TimerExpired, null,
             countdownToOne, State.countdown_one,
         ::State.countdown_one, # Current state
            # Input, test, transition, next state:
           :TimerExpired, null,
             triggerCamera, State.snap_photo,
         ::State.snap_photo, # Current state
            # Input, test, transition, next state:
           :Quit.quit, null,
             returnChange, State.idle,
           :TimerExpired.class, null,
             null, State.wait_photo,
           :ImageAquired.class, photosRemaining(),
             countdownStart, State.countdown_three,
           :ImageAquired.class, photosRemaining(),
             showDigit, State.idle,
           :ImageAquiredFailed.class, null,
             initialize, State.idle,
        )
        """

class PhotoBooth:
    def __init__(self, config_file):
        self.parseConfigFile(config_file)
        self.lighting = Lighting(self.lighting_config)
        self.verbose = False
        self.stateMachine = PhotoBoothStateMachine()

    def parseConfigFile(self, configFile):
        config = SafeConfigParser()
        config.read(configFile)
        self.vebose = config.getint('general_config', 'verbose')
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
        for input in [
                Action.Initialize,
                Action.ButtonPress,
                Action.TimerExpired,
                Action.TimerExpired,
                Action.TimerExpired,
                Action.TimerExpired,
                Action.TimerExpired,
                Action.ImageAquired]:
            self.stateMachine.nextState(input)


if __name__ == '__main__':
    photo_booth  = PhotoBooth('config.ini')
    photo_booth.run()

