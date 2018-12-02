import data

from constants import *

class BestTimes(object):

    def __init__(self, filename="persistency.duck"):
        self.filename = filename
        self.times = {}
        self.won = set()
        self.load()

    def save(self):
        file = data.save(self.filename)
        for level in self.times.keys():
            values = ["%d:%s" % (ticks, name) for ticks, name in self.times[level]]
            winstr = ['', '!'][level in self.won]
            file.write("%s=%s%s\n" % (level, winstr, ",".join(values)))
        file.close()
        
    def load(self):
        try:
            file = data.load(self.filename)
        except:
            pass
        else:
            input = file.readlines()
            for line in input:
                chomped = line[:-1]
                level, values = chomped.split("=", 1)
                leveltimes = []
                if values != "":
                    if values[0] == '!':
                        self.won.add(level)
                        values = values[1:]
                    for value in values.split(","):
                        ticks, name = value.split(":", 1)
                        leveltimes.append((int(ticks),name))
                self.times[level] = leveltimes
            file.close()

    def get_best_times(self, levelname):
        ln = self._clean_levelname(levelname)
        if self.times.has_key(ln):
            return self.times[ln]
        return []

    def is_qualifying_time(self, levelname, ticks):
        ln = self._clean_levelname(levelname)
        t = self.get_best_times(ln)
        return len(t) < SCORES_PER_LEVEL or t[-1][0] > ticks
 
    def add_time(self, levelname, ticks, playername):
        ln = self._clean_levelname(levelname)
        t = self.get_best_times(ln)
        index = 0
        while index < len(t) and ticks > t[index][0]:
            index += 1
        t.insert(index, (ticks, playername))
        self.times[ln] = t[:SCORES_PER_LEVEL]
        self.won.add(ln)

    def level_completed(self, levelname):
        ln = self._clean_levelname(levelname)
        return ln in self.won

    def _clean_levelname(self, levelname):
        return levelname.replace("=", "")
        
    def _clean_playername(self, playername):
        return playername.replace(",", "")
        
    def format_time(self, ticks, rate):
        msec = ticks * rate
        min, msec = divmod(msec, 60000)
        sec, msec = divmod(msec, 1000)
        csec = msec // 10
        return "%d'%02d\"%02d" % (min, sec, csec)
