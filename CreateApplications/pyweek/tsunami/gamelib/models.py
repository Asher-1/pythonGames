import options

class SubModel():
    """ Configures a submarine """
    RANGE = 200 # Rope range
    power = 100.0 # Acceleration force
    rotspeed = 1.0 # Max angular velocity (radians/s)
    rotpower = 400.0 # Max momentum applied by maneuver jets
    name = 'Default'
    price = 300
    moment_i = 500

    def morph(self, sub):
        sub.RANGE = self.RANGE
        sub.power = self.power
        sub.rotspeed = self.rotspeed
        sub.rotpower = self.rotpower
        sub.name = self.name
        sub.moment_i = self.moment_i

class Dolphin(SubModel):
    name = 'Dolphin'

class Piranha (SubModel):
    power = 150.0
    rotspeed = 1.1
    rotpower = 500.0
    name = 'Piranha'
    price = 1000
    moment_i = 400

class Barracuda (SubModel):
    RANGE = 220
    power = 200.0
    rotspeed = 1.4
    rotpower = 600.0
    name = 'Barracuda'
    price = 5000
    moment_i = 300

class Stingray (SubModel):
    RANGE = 250
    power = 260.0
    rotspeed = 1.8
    rotpower = 700.0
    name = 'Stingray'
    price = 8000
    moment_i = 250

class Tsunami (SubModel):
    RANGE = 300
    power = 350.0
    rotspeed = 2.5
    rotpower = 1000.0
    name = 'Tsunami'
    price = 15000
    moment_i = 100

models = [Dolphin(), Piranha(), Barracuda(), Stingray(), Tsunami()]

def currentModel():
    for m in models:
        if m.name == options.getopt('model'):
            return m
    print "Current model not found!!"

