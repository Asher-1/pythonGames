from django.http import HttpResponse
from django.core import serializers

from scoreserver.highscore.models import HighScore
from scoreserver.highscore.forms import HighScoreForm


def top10(request):
    top = HighScore.objects.order_by('-score')[:10]
    return HttpResponse(serializers.serialize('json', top))


def submit(request):
    form = HighScoreForm(request.POST)
    if request.POST and form.is_valid():
        form.save()
    return top10(request)
