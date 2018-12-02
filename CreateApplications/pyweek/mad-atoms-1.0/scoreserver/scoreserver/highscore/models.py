from django.db import models


class HighScore(models.Model):
    playername = models.CharField(max_length=512)
    score = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u'{0}: {1}'.format(self.playername, self.score)
