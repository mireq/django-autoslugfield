# -*- coding: utf-8 -*-
from pathlib import Path

BASE_DIR = Path(__file__).parent

INSTALLED_APPS = ['tests', 'django_autoslugfield']
SECRET_KEY = 'secret'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
USE_TZ = False

DATABASES = {
	'default': {
		'ENGINE': 'django.db.backends.sqlite3',
		'NAME': ':memory:',
	}
}
