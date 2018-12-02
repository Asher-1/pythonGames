import csv
from cocos.sprite import Sprite
from cocos.cocosnode import CocosNode
from util import Vector
import options
import os.path

class Game():
    def __init__ (self):
        self.score = float(options.getopt('score'))
        self.levelTree = LevelTree(os.path.join('data','levels.txt'))
        self.currentLevel = None

    def setCurrentLevel(self, level):
        """ Che que prolijidad mira escribi un setter y todo"""
        self.currentLevel = level

    def completeCurrentLevel(self, position):
        assert not self.currentLevel is None
        if position == 1:
            self.levelTree.completeLevel(self.currentLevel.levelId)
            self.levelUpdater()
        if position <= len(self.currentLevel.prizes):
            self.score += self.currentLevel.prizes[position-1]
            options.setopt ('score', self.score)
        self.currentLevel = None
        # TODO: Assign other prizes even if we didn't end up first

class Level(CocosNode):
    def __init__(self, levelId, name, filename, x, y, difficulty, prizes, unlocks):
        super(Level, self).__init__()
        self.unlockedSprite = Sprite('level.png')
        self.add (self.unlockedSprite)
        self.completedSprite = Sprite('level_completed.png')
        self.completedSprite.visible = False
        self.add (self.completedSprite)
        self.levelId = levelId
        self.name = name
        self.levelFilename = filename
        self.position = int(x), int(y)
        self.difficulty = difficulty
        self.prizes = [float(x) for x in prizes.split('/')]
        self.unlocks = unlocks.split()
        self.completed = False
    def pos(self):
        return Vector(*self.position)

    def setCompleted(self):
        self.completedSprite.visible = True
        self.unlockedSprite.visible = False
        self.completed = True

class LevelTree():
    def __init__(self, filename):
        f = open(filename)
        rows = csv.reader(f)
        self.completed = {}
        self.unlocked = {}
        self.all = {}
        first = Level(*rows.next())
        self.all[first.levelId] = self.unlocked[first.levelId] = first
        for row in rows:
            if len(row) > 0: # Skip blank lines
                level = Level(*row)
                self.all[level.levelId] = level
        for l in str(options.getopt('unlocked')).split(','):
            if len(l) > 0:
                self.unlocked[l] = self.all[l]
        for l in str(options.getopt('completed')).split(','):
            if len(l) > 0:
                self.completed[l] = self.all[l]
                self.completed[l].setCompleted()

    def completeLevel(self, levelId):
        assert levelId in self.unlocked
        level = self.unlocked[levelId]
        level.setCompleted()
        for lId in level.unlocks:
            self.unlocked[lId] = self.all[lId]
        self.completed[levelId] = level
        options.setopt('unlocked', ','.join(self.unlocked.keys()))
        options.setopt('completed', ','.join(self.completed.keys()))

