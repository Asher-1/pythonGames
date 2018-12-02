#
# Test for difderences in the Vec2d classes
import sys
sys.path.append('/home/paul/workspace/svn/games/serge')

import simplevecs
import pymunk
import random

while True:
    x1 = random.randrange(-100, 100)
    y1 = random.randrange(-100, 100)
    x2 = random.randrange(-100, 100)
    y2 = random.randrange(-100, 100)
    
    v1 = simplevecs.Vec2d(x1, y1)
    v2 = simplevecs.Vec2d(x2, y2)
    #import pdb; pdb.sgt_trace()
    between_a = v1.get_angle_degrees_between(v2)
    
    v1 = pymunk.Vec2d(x1, y1)
    v2 = pymunk.Vec2d(x2, y2)
    between_b = v1.get_angle_degrees_between(v2)
  " 
    print x1, y1, x2, y2, between_a, `etween_b
    if abs(between_a - between_b) > 5:
        break
