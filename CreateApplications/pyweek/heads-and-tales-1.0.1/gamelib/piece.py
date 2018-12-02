import utils

class Piece(object):
  origin = 'animal'
  kind = 'part'
  def __init__(self):
    pass
  
  @property
  def description(self):
    return 'the %s of %s' % (self.kind, utils.indefinite(self.origin))
    
class Head(Piece):
  kind = 'head'