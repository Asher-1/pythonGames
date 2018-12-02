from run_game import *

def Repeat(s, n):
  if s is BALL_ROTATE_CW or s is BALL_ROTATE_CCW:
    n /= 5
  return 'A'.join(random.choice(list(s)) for i in range(n))

def Find(s, m, n):
  return random.choice([g.string for g in s if g.meaning == m]) * n

def GetSingleDNA():
  dna = ''
  # Leg:
  dna += Repeat(BALL_ROTATE_CCW, 90)
  dna += Repeat(BALL_INFLATE, 6)
  # Body:
  dna += Repeat(BALL_START, 1)
  dna += Repeat(BALL_INFLATE, 15)
  dna += Repeat(BALL_ROTATE_CW, 90)
  # Tail:
  dna += Repeat(BALL_START, 1)
  dna += Find(GENES, 'wing', 4)
  dna += Repeat(BALL_INFLATE, 17)
  dna += Repeat(BALL_END, 1) # Tail.
  dna += Repeat(BALL_ROTATE_CCW, 180)
  # Wing:
  # Multiple starts to emphasize motion.
  dna += Repeat(BALL_START, 1)
  dna += Repeat(BALL_START, 1)
  dna += Repeat(BALL_START, 1)
  dna += Repeat(BALL_START, 1)
  dna += Repeat(BALL_START, 1)
  dna += Repeat(BALL_START, 1)
  dna += Repeat(BALL_START, 1)
  dna += Repeat(BALL_START, 1)
  dna += Repeat(BALL_ROTATE_CW, 180)
  dna += Repeat(BALL_INFLATE, 25)
  dna += Find(GENES, 'wing', 3)
  dna += Repeat(BALL_END, 1) # Wing.
  dna += Repeat(BALL_END, 1) # Wing.
  dna += Repeat(BALL_END, 1) # Wing.
  dna += Repeat(BALL_END, 1) # Wing.
  dna += Repeat(BALL_END, 1) # Wing.
  dna += Repeat(BALL_END, 1) # Wing.
  dna += Repeat(BALL_END, 1) # Wing.
  dna += Repeat(BALL_END, 1) # Wing.
  # Neck:
  dna += Repeat(BALL_START, 1)
  dna += Repeat(BALL_ROTATE_CW, 50)
  dna += Repeat(BALL_INFLATE, 10)
  dna += Repeat(BALL_CONTRACT, 7)
  # Head:
  dna += Repeat(BALL_START, 1)
  dna += Repeat(BALL_ROTATE_CCW, 60)
  # Eye:
  dna += Repeat(BALL_START, 1)
  dna += Repeat(BALL_INFLATE, 3)
  dna += Find(GENES, 'red', 6)
  dna += Find(GENES, 'dark', 4)
  dna += Find(GENES, 'eye', 3)
  dna += Repeat(BALL_END, 1) # Eye.
  dna += Repeat(BALL_INFLATE, 8)
  # Beak:
  dna += Repeat(BALL_START, 1)
  dna += Find(GENES, 'red', 3)
  dna += Find(GENES, 'green', 1)
  dna += Find(GENES, 'dark', 4)
  dna += Find(GENES, 'tooth', 3)
  dna += Repeat(BALL_INFLATE, 8)
  dna += Repeat(BALL_END, 1) # Beak.
  dna += Repeat(BALL_ROTATE_CW, 60)
  # Comb:
  dna += Repeat(BALL_START, 1)
  dna += Repeat(BALL_INFLATE, 6)
  dna += Find(GENES, 'wing', 2)
  dna += Find(GENES, 'dark', 5)
  dna += Find(GENES, 'red', 6)
  dna += Repeat(BALL_END, 1) # Comb.
  dna += Repeat(BALL_INFLATE, 5)
  dna += Repeat(BALL_END, 1) # Head.
  dna += Repeat(BALL_INFLATE, 10)
  dna += Repeat(BALL_END, 1) # Neck.
  dna += Repeat(BALL_ROTATE_CW, 90)
  dna += Repeat(BALL_INFLATE, 15)
  dna += Repeat(BALL_END, 1) # Body.
  dna += Repeat(BALL_ROTATE_CW, 180)
  dna += Find(GENES, 'dark', 4)
  dna += Find(GENES, 'red', 2)
  dna += Find(GENES, 'green', 1)
  dna += Find(GENES, 'scaled', 3)
  dna += Repeat(BALL_CONTRACT, 14)
  dna += Repeat(BALL_INFLATE, 3)
  # Finger:
  dna += Repeat(BALL_START, 1)
  dna += Repeat(BALL_ROTATE_CW, 20)
  dna += Repeat(BALL_INFLATE, 4)
  dna += Repeat(BALL_CONTRACT, 2)
  dna += Repeat(BALL_END, 1) # Finger.
  # Finger:
  dna += Repeat(BALL_START, 1)
  dna += Repeat(BALL_ROTATE_CW, 60)
  dna += Repeat(BALL_INFLATE, 7)
  dna += Repeat(BALL_CONTRACT, 5)
  dna += Repeat(BALL_END, 1) # Finger.
  # Finger:
  dna += Repeat(BALL_START, 1)
  dna += Repeat(BALL_ROTATE_CCW, 60)
  dna += Repeat(BALL_INFLATE, 7)
  dna += Repeat(BALL_CONTRACT, 5)
  dna += Repeat(BALL_END, 1) # Finger.
  dna += Repeat(BALL_INFLATE, 5)
  dna += Repeat(BALL_END, 1) # Leg.
  dna += Find(GENES, 'furry', 1)
  dna += Find(GENES, 'bright', 3)
  dna += Find(GENES, 'red', 1)
  dna += Find(GENES, 'green', 1)
  return dna

def GetDNA():
  dna = GetSingleDNA(), GetSingleDNA()
#  print 'Chicken generated with', len(dna[0]), 'bases.'
  return dna
