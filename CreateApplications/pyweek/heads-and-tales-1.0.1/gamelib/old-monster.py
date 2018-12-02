import piece
import utils

class Monster(piece.Piece):
  def __init__(self):
    self.pieces = []
    self.name = 'rabbit'
  
  @property
  def description(self):
    if self.pieces: 
      desc = utils.conjunction(p.description for p in self.pieces)
    else:
      desc = 'no body parts'
    return "%s with %s" % (utils.indefinite(self.name).capitalize(), desc)

if __name__ == '__main__':
  m = Monster()
  print m.description
  m.pieces.append(piece.Piece())
  print m.description
  m.pieces.append(piece.Head())
  print m.description
  m.pieces.append(piece.Head())
  print m.description
