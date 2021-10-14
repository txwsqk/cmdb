from linkedme_devops.settings.base import *

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'ysx',
        'USER': 'root',
        'PASSWORD': 'root',
        'HOST': '172.10.31.7',
        'PORT': '3306',
    }
}
