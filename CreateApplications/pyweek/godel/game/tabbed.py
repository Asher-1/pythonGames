"""Tabbed display for the vdu"""

from pgzero import actor
from pgzero.loaders import sounds
from game import group
from game import button
from game import scrolling
from game.settings import SETTINGS as S


class Tabbed(group.Group):
    """A tabbed display"""

    def __init__(self):
        """Initialise the tab display"""
        super(Tabbed, self).__init__('tab')
        #
        self.buttons = []
        for idx, button_name in enumerate(S['tabbed-buttons']):
            new_button = button.Button('button', '{0}_button'.format(button_name), callback=self.change_tab)
            new_button.idx = idx
            new_button.midleft = (S['tabbed-initial-x'] + idx * S['tabbed-delta-x'], S['tabbed-initial-y'])
            self.append(new_button)
            self.buttons.append(new_button)
            new_button.base_name = '{0}_button'.format(button_name)
        #
        self.select_tab_button(self.buttons[0])
        #
        # The visual display unit
        self.vdu_text = scrolling.ScrolledEntries(
            'vdu-text',
            width=S['vdu-size'][0],
            height=S['vdu-size'][1],
            background=None,
        )
        self.vdu_text.pos = S['vdu-position']
        self.append(self.vdu_text)
        self.tabs = [self.vdu_text]
        #
        for tab_name in ['people_panel', 'health_tab_empty', 'water_tab_empty', 'food_tab_empty']:
            new_tab = actor.Actor(tab_name)
            new_tab.pos = S['vdu-position']
            self.tabs.append(new_tab)
        #
        self.current_tab = self.vdu_text

    def add_dialog_item(self, item):
        """Add an item of dialog"""
        self.vdu_text.insert(0, item)
        #
        # Make sure we go to the first tab
        if self.current_tab != self.tabs[0]:
            self.change_tab(self.buttons[0], None)

    def change_tab(self, pressed_button, mouse_button):
        """Change the tab"""
        self.log.info('Changing to tab {0}'.format(pressed_button.idx))
        sounds.talk.play()
        #
        self.remove(self.current_tab)
        self.current_tab = self.tabs[pressed_button.idx]
        self.append(self.current_tab)
        #
        self.select_tab_button(pressed_button)

    def select_tab_button(self, the_button):
        """Select a particular tab button"""
        #
        for button in self.buttons:
            button.off_image = button.base_name
            button.on_image = '{0}_highlight'.format(button.base_name)
            button.image = button.off_image
        #
        the_button.on_image = '{0}_on'.format(the_button.base_name)
        the_button.off_image = '{0}_on'.format(the_button.base_name)
        the_button.image = the_button.on_image
