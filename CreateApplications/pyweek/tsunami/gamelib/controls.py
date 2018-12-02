from pyglet.window import key, mouse
from cocos.layer import Layer

rope_map_1 = {
    key.W: (0, 90),
    key.E: (1, 45),
    key.D: (2, 0),
    key.C: (3, -45),
    key.X: (4, -90),
    key.Z: (5, -135),
    key.A: (6, 180),
    key.Q: (7, 135),
}

rope_map_2 = {
    key.NUM_8: (0, 90),
    key.NUM_9: (1, 45),
    key.NUM_6: (2, 0),
    key.NUM_3: (3, -45),
    key.NUM_2: (4, -90),
    key.NUM_1: (5, -135),
    key.NUM_4: (6, 180),
    key.NUM_7: (7, 135),
}

arrow_map_1 = dict(left=key.LEFT, up=key.UP, right=key.RIGHT, down=key.DOWN)
arrow_map_2 = dict(left=key.A, up=key.W, right=key.D, down=key.S)
arrow_map_3 = dict(left=None, up=None, right=None, down=None)

class Bindings:
    rope_map = rope_map_1
    arrow_map = arrow_map_1

STEER_THRESHOLD = 0
STEER_TIME = 1.0
MOUSE_SENSITIVITY = 0.5

class ControlLayer (Layer):

    is_event_handler = True
    
    def __init__ (self, hero):
        super (ControlLayer, self).__init__ ()
        self.hero = hero
        self.target_angle = hero.rotation
        self.steering = False
        self.mouse_w = 0

    #def on_mouse_drag (self, x, y, dx, dy, buttons, modifiers):
    #    # No special case for drag:
    #    self.on_mouse_motion (x,y,dx,dy)
        
    #def on_mouse_motion (self, x, y, dx, dy):
    #    if not self.steering and abs(dx) >= STEER_THRESHOLD:
    #        self.steering = True
    #        self.target_angle = int(self.hero.rotation)
    #        self.schedule (self.timer)
    #    if self.steering:
    #        self.time = STEER_TIME
    #        self.target_angle += dx*MOUSE_SENSITIVITY

    def timer (self, dt):
        self.time -= dt
        if self.time <= 0:
            self.steering = False
            self.hero.desired_w -= self.mouse_w
            self.unschedule (self.timer)
            self.mouse_w = 0
        else:
            self.hero.desired_w -= self.mouse_w
            current = int(self.hero.rotation) % 360
            desired = int(self.target_angle) % 360
            if current == desired:
                pass
            elif current < desired <= current + 180 or current < desired+360 <= current + 180: # left!
                self.mouse_w = -self.hero.rotspeed
            else:
                self.mouse_w = self.hero.rotspeed
            self.hero.desired_w += self.mouse_w

    def on_mouse_press (self, x, y, buttons, modifiers):
        if buttons & mouse.LEFT:
            self.hero.engine_on()

    def on_mouse_release (self, x, y, buttons, modifiers):
        if buttons & mouse.LEFT:
            self.hero.engine_off()

    def on_key_press (self, symbol, modifiers):
        speed = 5.0
        if symbol in Bindings.arrow_map.values():
            if symbol==Bindings.arrow_map['up']:
                self.hero.engine_on()
            elif symbol==Bindings.arrow_map['down']:
                pass # no action here
            elif symbol==Bindings.arrow_map['left']:
                self.hero.start_left()
            elif symbol==Bindings.arrow_map['right']:
                self.hero.start_right()
            return True # event was handled
        elif symbol in Bindings.rope_map:
            i, dir = Bindings.rope_map[symbol]
            self.hero.throw_rope (i, dir)
            return True
        else:
            return False

    def on_key_release (self, symbol, modifiers):
        if symbol in Bindings.arrow_map.values():
            if symbol==Bindings.arrow_map['up']:
                self.hero.engine_off()
            elif symbol==Bindings.arrow_map['left']:
                self.hero.stop_left()
            elif symbol==Bindings.arrow_map['right']:
                self.hero.stop_right()
            return True
        elif symbol in Bindings.rope_map:
            i, dir = Bindings.rope_map[symbol]
            self.hero.detach_rope (i)
            return True

        return False
    
