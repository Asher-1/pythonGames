"""Various timers"""

import random
import serge.actor


class BadSequence(Exception):
    """Data was in a bad range"""


class TimerStopped(Exception):
    """A timer needs to stop"""


class BadRange(Exception):
    """Data was in a bad range"""


class BaseTimer(serge.actor.Actor):
    """A base class for timer types"""

    def __init__(self, tag, name, callback=None, one_shot=False, started=True):
        """Initialise the timer"""
        super(BaseTimer, self).__init__(tag, name)
        self.callback = callback
        #
        self._running = started
        self.setTimeToGo()
        self._time_passed = 0
        self.number_times = 0
        self.one_shot = one_shot

    def setTimeToGo(self):
        """Set the time to go"""
        try:
            self._time_to_go = self._getTimeToGo()
        except TimerStopped:
            self.stopTimer()
            self.log.debug('Timer %s stopped' % self.getNiceName())
        else:
            self.log.debug('Timer %s new time to go is %s' % (self.getNiceName(), self._time_to_go))

    def _getTimeToGo(self):
        """Get the time to go until the next firing - override this in real classes"""
        raise NotImplementedError

    def updateActor(self, interval, world):
        """Update the timer"""
        if self._running:
            self._time_passed += interval / 1000.0
            #
            # Timer gone off?
            while self._time_passed >= self._time_to_go:
                self.log.debug('Timer %s has gone off' % self.getNiceName())
                self._time_passed -= self._time_to_go
                self.number_times += 1
                self.callback()
                #
                # One shots should just stop now
                if self.one_shot:
                    self.stopTimer()
                    break
                #
                # Get a new time to go
                try:
                    self._time_to_go = self._getTimeToGo()
                except TimerStopped:
                    self.stopTimer()
                    break

    def startTimer(self):
        """Start the timer"""
        self._running = True

    def stopTimer(self):
        """Stop the timer"""
        self._running = False

    def resetTimer(self):
        """Reset the timer back to zero

        If running then the timer continues to run. The time
        to go is recalculated

        """
        self._time_passed = 0
        self._time_to_go = self._getTimeToGo()
        self.number_times = 0

    def resetAndStopTimer(self):
        """Reset and stop the timer"""
        self.resetTimer()
        self.stopTimer()

    def resetAndStartTimer(self):
        """Reset and start the timer"""
        self.resetTimer()
        self.startTimer()

    def isRunning(self):
        """Return True if we are running"""
        return self._running


class Timer(BaseTimer):
    """A timer that goes off and calls a callback - time is in seconds"""

    def __init__(self, tag, name, least_time, most_time=None, callback=None, one_shot=False, started=True):
        """Initialise the timer"""
        self.least_time = least_time
        self.most_time = most_time
        #
        # Super call must be here because it will call the _getTimeToGo method
        super(Timer, self).__init__(tag, name, callback=callback, one_shot=one_shot, started=started)
        #
        # Sanity check
        if most_time is not None and least_time > most_time:
            raise BadRange('Most time (%s) must be greater than least time (%s)' % (
                most_time, least_time
            ))

    def _getTimeToGo(self):
        """Return the time to go"""
        if self.most_time is None or self.least_time == self.most_time:
            return self.least_time
        else:
            return random.uniform(self.least_time, self.most_time)


class SequenceIntervalTimer(BaseTimer):
    """A timer that uses a sequence of intervals as the gaps"""

    def __init__(self, tag, name, intervals, callback=None, repeat=False, started=True):
        """Initialise the timer"""
        #
        if intervals and min(intervals) <= 0:
            raise BadSequence('Sequence contains values <= 0 (%s)' % (intervals, ))
        #
        self.intervals = intervals
        self._index = -1
        self.repeat = repeat
        #
        # Super call must be here because it will call the _getTimeToGo method
        super(SequenceIntervalTimer, self).__init__(tag, name, callback=callback, started=started)

    def _getTimeToGo(self):
        """Return the next time interval"""
        if not self.intervals:
            raise TimerStopped
        #
        self._index += 1
        if self._index == len(self.intervals):
            if self.repeat:
                self._index = 0
            else:
                raise TimerStopped
        #
        return self.intervals[self._index]

    def resetTimer(self):
        """Reset the timer"""
        self._index = -1
        super(SequenceIntervalTimer, self).resetTimer()


class SequenceTimer(SequenceIntervalTimer):
    """A sequential timer specified by a series of absolute times"""

    def __init__(self, tag, name, sequence, callback=None, repeat=False, started=True):
        """Initialise the timer"""
        current = 0
        intervals = []
        for t in sequence:
            intervals.append(t - current)
            current = t
        #
        super(SequenceTimer, self).__init__(tag, name, intervals, callback=callback, repeat=repeat, started=started)

