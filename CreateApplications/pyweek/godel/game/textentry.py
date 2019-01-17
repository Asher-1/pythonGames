"""A text entry for the screen"""

from pgzero import actor
from game import group
from game import text
from game.settings import SETTINGS as S


class TextEntry(group.Group):
    """The visual representation of some text entry"""

    def __init__(self, name, entry_text, *args, **kw):
        """Initialise the entry"""
        super(TextEntry, self).__init__('text-entry')
        #
        self.icon = actor.Actor(name, center=S['text-entry-icon-pos'])
        self.icon.scale(S['text-entry-icon-scale'])
        self.name = text.Text(S['names'][name], center=S['text-entry-name-pos'])
        self.entry_text = text.Text(entry_text, midleft=S['text-entry-text-pos'], *args, **kw)
        #
        self.append(self.icon)
        self.append(self.name)
        self.append(self.entry_text)
        #
        self.height = S['text-entry-height']
        self.width = S['text-entry-width']
