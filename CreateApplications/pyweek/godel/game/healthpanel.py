"""Shows the health of individuals"""

from pgzero import actor
from pgzero import clock
from pgzero.loaders import sounds
from game import group
from game import gauge
from game import button
from game import text
from game.settings import SETTINGS as S


# Drinking states
S_OFF = 'blue_light_off'
S_DRINKING = 'blue_light'
S_NOT_DRINKING = 'red_light'
S_TALKING = 'white_light'


class HealthPanel(group.Group):
    """A panel showing the health of a person"""

    def __init__(self, name, state):
        """Initialise the panel"""
        super(HealthPanel, self).__init__(name)
        #
        self.state = state
        #
        self.water_gauge = gauge.Gauge(
            '{0}-water-gauge'.format(name),
            foreground=None,
            back_colour=(0, 0, 0, 255),
            front_colour=S['panel-water-colour'],
            size=S['panel-water-size'],
            orientation=gauge.Gauge.VERTICAL,
            value=50,
        )
        self.water_gauge.pos = S['panel-water-pos']
        self.append(self.water_gauge)
        #
        self.health_gauge = gauge.Gauge(
            '{0}-health-gauge'.format(name),
            foreground=None,
            back_colour=(0, 0, 0, 255),
            front_colour=S['panel-health-colour'],
            size=S['panel-health-size'],
            orientation=gauge.Gauge.HORIZONTAL,
            value=50,
        )
        self.health_gauge.pos = S['panel-health-pos']
        self.append(self.health_gauge)
        #
        # The panel foreground
        self.append(actor.Actor('{0}_panel'.format(name)))
        #
        # The button to give water
        self.button = button.Button('{0}-give'.format(self.name), 'give_button', self.give_click)
        self.button.pos = S['panel-button-pos']
        self.button.tag = 'give'
        self.button.person = name
        self.append(self.button)
        #
        # The name of the person
        self.person_name = text.Text(S['names']['person_{0}'.format(name)])
        self.person_name.center = S['panel-name-pos']
        self.append(self.person_name)
        #
        # The talking light
        self.talking_light = actor.Actor('green_light')
        self.talking_light.pos = S['panel-talking-light-pos']
        self.append(self.talking_light)
        self.wants_to_talk = False
        #
        # The drinking light
        self.drinking_light = actor.Actor('blue_light_off')
        self.drinking_light.pos = S['panel-drinking-pos']
        self.append(self.drinking_light)
        #
        # The talking button
        self.talking_button = button.Button('{0}-talk'.format(self.name), 'talk_button', self.talk_click)
        self.talking_button.pos = S['panel-talking-button-pos']
        self.talking_button.visible = False
        self.append(self.talking_button)
        #
        # The blackout to hide the actor
        self.blackout = actor.Actor('panel_blackout')
        self.append(self.blackout)
        #
        self.conversation_item = None
        self.is_dead = False

    def give_click(self, button, mouse_button):
        """The button was clicked"""

    def talk_click(self, button, mouse_button):
        """The talk button was clicked"""
        self.log.info('Button {0} clicked'.format(self.name))
        sounds.talk.play()
        self.state.show_conversation(self.conversation_item)
        self.clear_wants_to_talk()

    def set_health(self, new_health):
        """Set the health"""
        self.health_gauge.new_value = new_health

    def set_water(self, new_water):
        """Set the health"""
        self.water_gauge.new_value = new_water

    def hide_button(self):
        """Hide the button"""
        self.button.visible = False

    def show_button(self):
        """Show the button"""
        if not self.is_dead:
            self.button.visible = True

    def set_wants_to_talk(self, conversation_item):
        """Set flag for wants to talk"""
        if not self.wants_to_talk:
            self.wants_to_talk = True
            self.talking_button.visible = True
            clock.schedule_interval(self.flash_talk_light, S['panel-light-flash'])
        #
        self.conversation_item = conversation_item

    def clear_wants_to_talk(self):
        """Clear the wants to talk flag"""
        self.wants_to_talk = False
        self.talking_button.visible = False
        self.talking_light.image = 'green_light'
        clock.unschedule(self.flash_talk_light)

    def flash_talk_light(self):
        """Flash the talking light"""
        if self.talking_light.image == 'green_light':
            self.talking_light.image = 'green_light_on'
        else:
            self.talking_light.image = 'green_light'

    def show_person(self):
        """Show the person"""
        if not self.is_dead:
            self.blackout.visible = False

    def hide_person(self):
        """Hide the person"""
        self.blackout.visible = True

    def set_drinking_state(self, drinking_state):
        """Set the drinking light state"""
        if not self.is_dead:
            self.drinking_light.image = drinking_state

    def set_dead(self):
        """Set this person as dead"""
        self.blackout.image = 'panel_redout'
        self.blackout.visible = True
        self.set_drinking_state(S_OFF)
        self.clear_wants_to_talk()
        self.hide_button()
        #
        self.is_dead = True
