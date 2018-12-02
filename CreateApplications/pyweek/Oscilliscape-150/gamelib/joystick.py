from pyglet import event
import sys

if sys.platform == 'linux2':
    import struct
    from select import select

    class JoystickEventDispatcher(event.EventDispatcher):
        JS_EVENT_BUTTON = 0x01 #/* button pressed/released */
        JS_EVENT_AXIS = 0x02  #/* joystick moved */
        JS_EVENT_INIT = 0x80  #/* initial state of device */
        JS_EVENT = "IhBB"
        JS_EVENT_SIZE = struct.calcsize(JS_EVENT)

        def __init__(self, device_number=0):
            device = '/dev/input/js%s' % device_number
            event.EventDispatcher.__init__(self)
            self.dev = open(device)

        def dispatch_events(self):
            r,w,e = select([self.dev],[],[], 0)
            if self.dev not in r: return
            evt = self.dev.read(self.JS_EVENT_SIZE)
            time, value, type, number = struct.unpack(self.JS_EVENT, evt)
            evt = type & ~self.JS_EVENT_INIT
            if evt == self.JS_EVENT_AXIS:
                self.dispatch_event('on_axis', number, value)
            elif evt == self.JS_EVENT_BUTTON:
                self.dispatch_event('on_button', number, value==1)

        def on_axis(self, axis, value):
            pass

        def on_button(self, button, pressed):
            pass
else:
    # not supported so just create a do nothing dummy class
    class JoystickEventDispatcher(event.EventDispatcher):
        def __init__(self, device_number=0):
            pass

        def dispatch_events(self):
            pass

        def on_axis(self, axis, value):
            pass

        def on_button(self, button, pressed):
            pass

JoystickEventDispatcher.register_event_type('on_axis')
JoystickEventDispatcher.register_event_type('on_button')

    
class DPad(object):
    def __init__(self, device_number=0):
        self.joystick_event_dispatcher = JoystickEventDispatcher(device_number)
        self.joystick_event_dispatcher.push_handlers(self)
        self.axis0 = 0
        self.axis1 = 0

    def update(self):
        self.joystick_event_dispatcher.dispatch_events()

    def on_axis(self, axis, value):
        if axis == 0:
            self.axis0 = value
        elif axis == 1:
            self.axis1 = value

if __name__ == "__main__":
    j = JoystickEventDispatcher(0)
    @j.event
    def on_button(button, pressed):
        print 'button', button, pressed

    @j.event
    def on_axis(axis, value):
        print 'axis', axis, value

    while True:
        j.dispatch_events()

