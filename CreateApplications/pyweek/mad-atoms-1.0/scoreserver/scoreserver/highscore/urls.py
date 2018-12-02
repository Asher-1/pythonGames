from django.conf.urls import patterns, url


urlpatterns = patterns('scoreserver.highscore.views',
    url(r'^top-10/$', 'top10'),
    url(r'^submit/$', 'submit'),
)
