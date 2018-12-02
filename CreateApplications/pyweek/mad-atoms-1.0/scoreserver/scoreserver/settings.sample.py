import os

PROJECT_PATH = os.path.abspath(os.path.join(__file__, '..', '..'))
print PROJECT_PATH


DEBUG = True
TEMPLATE_DEBUG = DEBUG

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(PROJECT_PATH, 'var', 'data.db')
    }
}

TIME_ZONE = 'Europe/Vilnius'
LANGUAGE_CODE = 'en-us'
SITE_ID = 1
USE_I18N = True
USE_L10N = True
USE_TZ = True

SECRET_KEY = '61aqt((6i%6f2om%=9f477nbbux2356qu#p@qk8a!6+%1_f7wb'

TEMPLATE_LOADERS = (
)

MIDDLEWARE_CLASSES = (
)

ROOT_URLCONF = 'scoreserver.urls'

WSGI_APPLICATION = 'scoreserver.wsgi.application'

TEMPLATE_DIRS = (
)

INSTALLED_APPS = (
    'scoreserver.highscore'
)
