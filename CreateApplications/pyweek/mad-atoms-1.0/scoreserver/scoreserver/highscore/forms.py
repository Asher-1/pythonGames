from django.forms import ModelForm

from scoreserver.highscore.models import HighScore


class HighScoreForm(ModelForm):
    class Meta:
        model = HighScore
