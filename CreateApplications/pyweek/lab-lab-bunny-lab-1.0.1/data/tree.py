from run_game import *

def Repeat(s, n):
  if s is BALL_ROTATE_CW or s is BALL_ROTATE_CCW:
    n /= 5
  return 'A'.join(random.choice(list(s)) for i in range(n))

def Find(s, m, n):
  return random.choice([g.string for g in s if g.meaning == m]) * n

def Blank(s):
  return 'A' * len(s)

def Leaf():
  dna = ''
  dna += Repeat(BALL_START, 1)
  i = random.randint(0, 4)
  dna += Find(GENES, 'dark', i)
  dna += Find(GENES, 'green', 8 - i)
  i = random.randint(0, 4)
  dna += Repeat(BALL_INFLATE, 25 - i)
  dna += Repeat(BALL_CONTRACT, 5 + i)
  dna += 'A' * i  # CONTRACT is 1 shorter than INFLATE.
  dna += Repeat(BALL_END, 1) # Leaf.
  return dna

def ThreeLeaves():
  dna = ''
  # Leaves:
  dna += Repeat(BALL_START, 1)
  dna += Repeat(BALL_INFLATE, 5)
  dna += Find(GENES, 'leaf', 5)
  dna += Leaf()
  dna += Repeat(BALL_ROTATE_CCW, 40)
  dna += Leaf()
  dna += Repeat(BALL_ROTATE_CW, 80)
  dna += Leaf()
  dna += Repeat(BALL_SHRINK, 5)
  dna += Repeat(BALL_END, 1) # Leaves.
  return dna

def MaybeDarken():
  if random.random() < 0.1:
    return Find(GENES, 'dark', 1)
  else:
    return Blank(Find(GENES, 'dark', 1))

def GetSingleDNA():
  dna = ''
  # Trunk:
  dna += Repeat(BALL_ROTATE_CCW, 90)
  dna += Repeat(BALL_START, 1)
  dna += Repeat(BALL_START, 1)
  # Branch:
  dna += Repeat(BALL_START, 1)
  dna += Repeat(BALL_INFLATE, 11)
  dna += ThreeLeaves()
  dna += Repeat(BALL_INFLATE, 11)
  dna += Repeat(BALL_CONTRACT, 14)
  dna += MaybeDarken()
  dna += Repeat(BALL_END, 1) # Branch.
  dna += Repeat(BALL_ROTATE_CCW, 70)
  # Branch:
  dna += Repeat(BALL_START, 1)
  dna += Repeat(BALL_INFLATE, 7)
  dna += Repeat(BALL_START, 1)
  dna += Repeat(BALL_ROTATE_CW, 20)
  dna += Repeat(BALL_INFLATE, 3)
  dna += ThreeLeaves()
  dna += Repeat(BALL_INFLATE, 11)
  dna += Repeat(BALL_CONTRACT, 9)
  dna += MaybeDarken()
  dna += Repeat(BALL_END, 1) # Branch.
  dna += Repeat(BALL_INFLATE, 11)
  dna += Repeat(BALL_CONTRACT, 11)
  dna += MaybeDarken()
  dna += Repeat(BALL_END, 1) # Branch.
  dna += Repeat(BALL_ROTATE_CW, 140)
  # Branch:
  dna += Repeat(BALL_START, 1)
  dna += Repeat(BALL_INFLATE, 11)
  dna += ThreeLeaves()
  dna += Repeat(BALL_INFLATE, 11)
  dna += Repeat(BALL_CONTRACT, 14)
  dna += MaybeDarken()
  dna += Repeat(BALL_END, 1) # Branch.
  dna += Repeat(BALL_ROTATE_CCW, 70)
  dna += Repeat(BALL_INFLATE, 23)
  dna += Repeat(BALL_CONTRACT, 14)
  dna += MaybeDarken()
  dna += Repeat(BALL_END, 1) # Trunk.
  dna += Repeat(BALL_INFLATE, 24)
  dna += Repeat(BALL_CONTRACT, 14)
  dna += MaybeDarken()
  dna += Repeat(BALL_END, 1) # Trunk.
  dna += Repeat(BALL_CONTRACT, 14)
  dna += Repeat(BALL_INFLATE, 24)
  dna += MaybeDarken()
  dna += Repeat(BALL_END, 1) # Trunk.
  dna += Find(GENES, 'scaled', 3)
  dna += Find(GENES, 'dark', 5)
  dna += Find(GENES, 'red', 6)
  dna += Find(GENES, 'green', 5)
  return dna

def GetDNA():
  dna = GetSingleDNA(), GetSingleDNA()
#  print 'Tree generated with', len(dna[0]), 'bases.'
  return dna
