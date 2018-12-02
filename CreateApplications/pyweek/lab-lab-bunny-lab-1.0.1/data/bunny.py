from run_game import *

def Repeat(s, n):
  if s is BALL_ROTATE_CW or s is BALL_ROTATE_CCW:
    n /= 5
  return 'A'.join(random.choice(list(s)) for i in range(n))

def Find(s, m, n):
  return random.choice([g.string for g in s if g.meaning == m]) * n

def GetSingleDNA():
  dna = ''
  # Body:
  dna += Repeat(BALL_ROTATE_CCW, 35)
  dna += Repeat(BALL_INFLATE, 25)
  # Hind leg:
  dna += Repeat(BALL_START, 1)
  dna += Repeat(BALL_ROTATE_CW, 110)
  dna += Repeat(BALL_CONTRACT, 5)
  dna += Repeat(BALL_INFLATE, 15)
  dna += Find(GENES, 'dark', 1)
  # Hind knee:
  dna += Repeat(BALL_START, 1)
  dna += Repeat(BALL_ROTATE_CW, 10)
  dna += Repeat(BALL_INFLATE, 6)
  # Hind foot:
  dna += Repeat(BALL_START, 1)
  dna += Repeat(BALL_ROTATE_CW, 95)
  dna += Repeat(BALL_INFLATE, 20)
  dna += Repeat(BALL_CONTRACT, 15)
  dna += Repeat(BALL_END, 1) # Hind foot.
  dna += Repeat(BALL_ROTATE_CCW, 10)
  dna += Repeat(BALL_INFLATE, 6)
  dna += Repeat(BALL_END, 1) # Hind knee.
  dna += Repeat(BALL_INFLATE, 15)
  dna += Repeat(BALL_END, 1) # Hind leg.
  dna += Repeat(BALL_ROTATE_CW, 160)
  # Front leg:
  dna += Repeat(BALL_START, 1)
  dna += Repeat(BALL_CONTRACT, 8)
  dna += Repeat(BALL_INFLATE, 12)
  dna += Find(GENES, 'dark', 1)
  # Front foot:
  dna += Repeat(BALL_START, 1)
  dna += Repeat(BALL_ROTATE_CW, 50)
  dna += Repeat(BALL_INFLATE, 12)
  dna += Repeat(BALL_CONTRACT, 8)
  dna += Repeat(BALL_END, 1) # Front foot.
  dna += Repeat(BALL_INFLATE, 3)
  dna += Repeat(BALL_END, 1) # Front leg.
  dna += Repeat(BALL_INFLATE, 15)
  dna += Repeat(BALL_ROTATE_CW, 100)
  dna += Repeat(BALL_CONTRACT, 17)
  # Head:
  dna += Repeat(BALL_START, 1)
  dna += Repeat(BALL_WIDEN, 10)
  dna += Repeat(BALL_ROTATE_CW, 90)
  # Eye:
  dna += Repeat(BALL_START, 1)
  dna += Repeat(BALL_INFLATE, 7)
  dna += Find(GENES, 'green', 6)
  dna += Find(GENES, 'dark', 2)
  dna += Find(GENES, 'eye', 3)
  dna += Repeat(BALL_END, 1) # Eye.
  dna += Repeat(BALL_INFLATE, 15)
  # Ear 1:
  dna += Repeat(BALL_START, 1)
#  dna += Find(GENES, 'leaf', 3)
#  dna += Find(GENES, 'green', 3)
  dna += Repeat(BALL_ROTATE_CCW, 15)
  dna += Repeat(BALL_CONTRACT, 15)
  dna += Repeat(BALL_INFLATE, 25)
  dna += Repeat(BALL_END, 1) # Ear 1.
  dna += Repeat(BALL_ROTATE_CCW, 30)
  # Ear 2:
  dna += Repeat(BALL_START, 1)
#  dna += Find(GENES, 'leaf', 3)
#  dna += Find(GENES, 'green', 3)
  dna += Repeat(BALL_ROTATE_CCW, 15)
  dna += Repeat(BALL_CONTRACT, 15)
  dna += Repeat(BALL_INFLATE, 25)
  dna += Find(GENES, 'dark', 1)
  dna += Repeat(BALL_END, 1) # Ear 2.
  dna += Repeat(BALL_ROTATE_CCW, 150)
  dna += Repeat(BALL_INFLATE, 5)
  # Face:
  dna += Repeat(BALL_START, 1)
  dna += Repeat(BALL_ROTATE_CW, 90)
  dna += Repeat(BALL_WIDEN, 2)
  # Nose:
  dna += Repeat(BALL_START, 1)
  dna += Repeat(BALL_INFLATE, 5)
  dna += Find(GENES, 'dark', 4)
  dna += Find(GENES, 'scaled', 3)
  dna += Repeat(BALL_END, 1) # Nose.
  dna += Repeat(BALL_ROTATE_CCW, 70)
  dna += Repeat(BALL_INFLATE, 8)
  dna += Repeat(BALL_END, 1) # Face.
  dna += Repeat(BALL_ROTATE_CW, 100)
  dna += Repeat(BALL_END, 1) # Head.
  dna += Repeat(BALL_ROTATE_CW, 180)
  dna += Repeat(BALL_INFLATE, 15)
  # Tail:
  dna += Repeat(BALL_START, 1)
  dna += Repeat(BALL_INFLATE, 12)
  dna += Repeat(BALL_CONTRACT, 3)
  dna += Repeat(BALL_ROTATE_CCW, 40)
  dna += Repeat(BALL_END, 1) # Tail.
  dna += Repeat(BALL_INFLATE, 5)
  dna += Repeat(BALL_ROTATE_CCW, 30)
  dna += Repeat(BALL_END, 1) # Body.
  dna += Find(GENES, 'furry', 1)
  dna += Find(GENES, 'bright', 1)
  dna += Find(GENES, 'red', 2)
  dna += Find(GENES, 'green', 1)
  return dna

def GetDNA():
  dna = GetSingleDNA(), GetSingleDNA()
#  print 'Bunny generated with', len(dna[0]), 'bases.'
  return dna
