from run_game import *

def Repeat(s, n):
  if s is BALL_ROTATE_CW or s is BALL_ROTATE_CCW:
    n /= 5
  return 'A'.join(random.choice(list(s)) for i in range(n))

def Find(s, m, n):
  return random.choice([g.string for g in s if g.meaning == m]) * n

def Finger(length, width, flip):
  if flip:
    rot = BALL_ROTATE_CCW
  else:
    rot = BALL_ROTATE_CW
  dna = ''
  # Bone:
  dna += Repeat(BALL_START, 1)
  dna += Repeat(BALL_INFLATE, length)
  # Bone:
  dna += Repeat(BALL_START, 1)
  dna += Repeat(rot, 30)
  dna += Repeat(BALL_INFLATE, length * 2)
  dna += Repeat(BALL_CONTRACT, length * 2 - width * 2)
  dna += Find(GENES, 'dark', 1)
  dna += Repeat(BALL_END, 1) # Bone.
  dna += Repeat(BALL_INFLATE, length)
  dna += Repeat(BALL_CONTRACT, length * 2 - width * 2)
  dna += Find(GENES, 'dark', 1)
  dna += Repeat(BALL_END, 1) # Bone.
  return dna

def Hand(flip):
  if flip:
    rot1 = BALL_ROTATE_CW
    rot2 = BALL_ROTATE_CCW
  else:
    rot1 = BALL_ROTATE_CCW
    rot2 = BALL_ROTATE_CW
  dna = ''
  # Palm:
  dna += Repeat(BALL_START, 1)
  dna += Repeat(BALL_INFLATE, 3)
  dna += Repeat(rot1, 60)
  dna += Finger(2, 1, flip)
  dna += Repeat(rot2, 20)
  dna += Finger(3, 1, flip)
  dna += Repeat(rot2, 20)
  dna += Finger(3, 1, flip)
  dna += Repeat(rot2, 20)
  dna += Finger(3, 1, flip)
  dna += Repeat(rot2, 80)
  dna += Finger(2, 2, not flip)
  dna += Repeat(rot1, 50)
  dna += Repeat(BALL_INFLATE, 4)
  dna += Find(GENES, 'dark', 1)
  dna += Repeat(BALL_END, 1) # Palm.
  return dna

def Limb(size, flip, elbow=30):
  if flip:
    rot = BALL_ROTATE_CCW
  else:
    rot = BALL_ROTATE_CW
  dna = ''
  # Upper part:
  dna += Repeat(BALL_START, 1)
  dna += Repeat(BALL_CONTRACT, size)
  dna += Repeat(BALL_INFLATE, size * 2)
  dna += Find(GENES, 'dark', 1)
  # Lower part:
  dna += Repeat(BALL_START, 1)
  dna += Repeat(rot, elbow)
  dna += Repeat(BALL_INFLATE, size)
  dna += Hand(flip)
  dna += Repeat(BALL_INFLATE, size)
  dna += Repeat(BALL_CONTRACT, size)
  dna += Find(GENES, 'dark', 1)
  dna += Repeat(BALL_END, 1) # Lower part.
  dna += Repeat(BALL_INFLATE, size)
  dna += Repeat(BALL_END, 1) # Upper part.
  return dna
  
def Ear():
  dna = ''
  # Outside:
  dna += Repeat(BALL_START, 1)
  dna += Repeat(BALL_INFLATE, 7)
  dna += Repeat(BALL_WIDEN, 2)
  dna += Find(GENES, 'dark', 2)
  dna += Repeat(BALL_END, 1) # Ear.
  # Inside:
  dna += Repeat(BALL_START, 1)
  dna += Repeat(BALL_INFLATE, 5)
  dna += Repeat(BALL_WIDEN, 2)
  dna += Find(GENES, 'dark', 1)
  dna += Repeat(BALL_END, 1) # Ear.
  return dna

def GetSingleDNA():
  dna = ''
  # Body:
  dna += Repeat(BALL_INFLATE, 10)
  dna += Repeat(BALL_ROTATE_CCW, 90)
  # Upper body:
  dna += Repeat(BALL_START, 1)
  dna += Repeat(BALL_INFLATE, 10)
  dna += Repeat(BALL_ROTATE_CW, 60)
  # Shoulder:
  dna += Repeat(BALL_START, 1)
  dna += Repeat(BALL_INFLATE, 5)
  dna += Repeat(BALL_ROTATE_CW, 90)
  dna += Limb(6, False)
  dna += Repeat(BALL_ROTATE_CCW, 90)
  dna += Repeat(BALL_INFLATE, 15)
  dna += Repeat(BALL_END, 1) # Shoulder.
  dna += Repeat(BALL_ROTATE_CCW, 120)
  # Shoulder:
  dna += Repeat(BALL_START, 1)
  dna += Repeat(BALL_INFLATE, 5)
  dna += Repeat(BALL_ROTATE_CW, 30)
  dna += Limb(6, False, 80)
  dna += Repeat(BALL_ROTATE_CCW, 30)
  dna += Repeat(BALL_INFLATE, 15)
  dna += Repeat(BALL_END, 1) # Shoulder.
  dna += Repeat(BALL_ROTATE_CW, 60)
  dna += Repeat(BALL_INFLATE, 10)
  # Head:
  dna += Repeat(BALL_START, 1)
  # Eye:
  dna += Repeat(BALL_START, 1)
  dna += Repeat(BALL_ROTATE_CW, 60)
  dna += Repeat(BALL_INFLATE, 5)
  dna += Find(GENES, 'green', 6)
  dna += Find(GENES, 'dark', 2)
  dna += Find(GENES, 'eye', 3)
  dna += Repeat(BALL_END, 1) # Eye.
  # Eye:
  dna += Repeat(BALL_START, 1)
  dna += Repeat(BALL_ROTATE_CCW, 60)
  dna += Repeat(BALL_INFLATE, 5)
  dna += Find(GENES, 'green', 6)
  dna += Find(GENES, 'dark', 2)
  dna += Find(GENES, 'eye', 3)
  dna += Repeat(BALL_END, 1) # Eye.
  # Nose:
  dna += Repeat(BALL_START, 1)
  dna += Repeat(BALL_ROTATE_CCW, 180)
  dna += Repeat(BALL_INFLATE, 6)
  dna += Repeat(BALL_CONTRACT, 2)
  dna += Find(GENES, 'dark', 2)
  dna += Repeat(BALL_END, 1) # Nose.
  dna += Repeat(BALL_INFLATE, 15)
  dna += Repeat(BALL_ROTATE_CW, 60)
  dna += Ear()
  dna += Repeat(BALL_ROTATE_CCW, 120)
  dna += Ear()
  dna += Repeat(BALL_ROTATE_CW, 60)
  dna += Repeat(BALL_INFLATE, 5)
  dna += Repeat(BALL_END, 1) # Head.
  dna += Repeat(BALL_INFLATE, 10)
  dna += Repeat(BALL_END, 1) # Upper body.
  dna += Repeat(BALL_INFLATE, 10)
  dna += Repeat(BALL_ROTATE_CW, 120)
  dna += Limb(5, False, elbow=100)
  dna += Repeat(BALL_ROTATE_CW, 150)
  dna += Limb(5, True, elbow=60)
  dna += Repeat(BALL_ROTATE_CCW, 120)
  dna += Repeat(BALL_INFLATE, 5)
  dna += Repeat(BALL_END, 1) # Body.
  dna += Find(GENES, 'furry', 1)
  dna += Find(GENES, 'bright', 1)
  dna += Find(GENES, 'red', 2)
  dna += Find(GENES, 'green', 1)
  return dna

def GetDNA():
  dna = GetSingleDNA(), GetSingleDNA()
#  print 'Monkey generated with', len(dna[0]), 'bases.'
  return dna
