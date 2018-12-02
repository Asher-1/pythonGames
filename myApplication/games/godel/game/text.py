"""Class to handle text"""

import pgzero.actor
import pgzero.ptext


class Text(pgzero.actor.Actor):
    """Class to show text"""

    def __init__(self, text, *args, **kw):
        """Initialise the text"""
        self.init_args = (args, kw)
        surface = pgzero.ptext.draw(text, (0, 0), *args, get_surface=True, **kw)
        super(Text, self).__init__(surface, *args, **kw)
        #
        self.text = text

    def set_text(self, text):
        """Set some text"""
        p = self.pos
        surface = pgzero.ptext.draw(text, (0, 0), *self.init_args[0],
                                    get_surface=True, **self.init_args[1])
        super(Text, self).__init__(surface, *self.init_args[0], **self.init_args[1])
        self.pos = p
        #
        self.text = text

