import levels
__all__ = [ 'state' ]


class State( object ):

    STATE_PAUSE, STATE_PLAY, STATE_WIN, STATE_OVER = range(4)

    def __init__( self ):

        # current score
        self.score = 0

        # current level
        self.level = None

        # touched goals
        self.touched_goals = 0

        # current level idx
        self.level_idx = None

        # time
        self.time = 0

        # state
        self.state = self.STATE_PAUSE

        self.start_level = 0

    def reset( self ):
        self.score = 0
        self.level = None
        self.level_idx = None
        self.state = self.STATE_PAUSE

    def set_level( self, l ):
        self.level_idx = l
        self.level = levels.levels[l]
        self.touched_goals = 0
        self.time = self.level.time

state = State()
