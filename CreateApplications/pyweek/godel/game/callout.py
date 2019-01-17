"""A call-out - a window that appears with text and a dismiss button"""

from pgzero import actor
from pgzero import animation
from pgzero.loaders import sounds
from game import text
from game import group
from game import button
from game import textentry
from game import scrolling
from game.settings import SETTINGS as S


class Callout(group.Group):
    """A window that appears"""

    def __init__(self, name, display_text, background, button_names, config, auto_remove=True, title=None):
        """Initialise the call-out"""
        super(Callout, self).__init__(name)
        #
        self.log.info('Created callout {0}'.format(name))
        #
        self.config = C = config
        self.auto_remove = auto_remove
        self.background = actor.Actor(background, center=(0, 0))
        self.append(self.background)
        w, h = (self.background.width, self.background.height)
        #
        self.text = text.Text(display_text, center=(0, 0),
                              fontname=config['callout-font'],
                              color=config['callout-colour'],
                              width=config['callout-width'])
        self.append(self.text)
        self.text.pos = config['callout-text-pos']
        self.dismiss_button = None
        #
        if title:
            self.title = text.Text(
                title,
                center=(0, 0),
                fontname=config['callout-title-font'],
                color=config['callout-title-colour'],
            )
            self.title.pos = config['callout-title-pos']
            self.append(self.title)
        #
        for idx, button_name in enumerate(button_names):
            this_button = button.Button(
                button_name,
                button_name,
                center=(0, 0),
                callback=self.button_click,
            )
            this_button.pos = (
                ((idx - (len(button_names) / 2 - 1)) - 0.5) * this_button.width + config['callout-button-x'],
                h / 2 + config['callout-button-y']
            )
            self.append(this_button)

    def show(self):
        """Show the callout"""
        C = self.config
        self.pos = (C['callout-initial-x'], C['callout-initial-y'])
        animation.Animation(
            self,
            pos=(C['callout-final-x'], C['callout-final-y']),
            duration=C['callout-animation-time'],
            tween=C['callout-animation-tween-in'],
        )
        self.dismiss_button = None

    def button_click(self, the_button, mouse_button):
        """A button was clicked"""
        self.log.debug('Dismissing callout with button {0}'.format(the_button.name))
        sounds.talk.play()
        self.dismiss_button = the_button.name
        if self.auto_remove:
            self.dismiss(the_button, mouse_button)

    def dismiss(self, the_button=None, mouse_button=None):
        """Dismiss the callout"""
        #
        C = self.config
        animation.Animation(
            self,
            pos=(C['callout-initial-x'], C['callout-initial-y']),
            duration=C['callout-animation-time'],
            tween=C['callout-animation-tween-out'],
            on_finished=self.remove_from_group,
        )

    def remove_from_group(self):
        """Remove this callout from the groups it is in"""
        self.ready_for_removal = True


class FinishCallout(Callout):
    """A callout for the end result of the game"""

    def __init__(self, name, background, button_names, config, deaths):
        """Initialise the callout"""
        super(FinishCallout, self).__init__(name, 'text', background, button_names, config)
        self.remove(self.text)
        #
        container = scrolling.ScrolledEntries(
            'vdu-text',
            width=S['end-vdu-size'][0],
            height=S['end-vdu-size'][1],
            background=None,
        )
        container.pos = (0, 30)
        self.append(container)
        #
        for name in 'abcde':
            if name in deaths:
                text = 'Died after {0} days'.format(deaths[name])
            else:
                text = 'Survived'
            #
            entry = textentry.TextEntry(
                'person_{0}'.format(name),
                text,
                width=S['text-entry-width'],
                fontname='computerfont',
                color=S['end-vdu-colour'],
            )
            container.append(entry)