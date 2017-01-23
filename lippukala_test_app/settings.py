# -*- coding: utf-8 -*-

import os
import tempfile

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(tempfile.gettempdir(), "lippukala_test.sqlite3"),
    }
}

SECRET_KEY = 'secret'

LIPPUKALA_PREFIXES = {
    "0": u"mat",
    "1": u"nom",
    "2": u"dog-jono",
    "3": u"cat-jono",
}

LIPPUKALA_LITERATE_KEYSPACES = {
    "0": u"hopea kulta kumi lanka muovi nahka naru pahvi rauta teräs".split(),
    "1": u"Aino Anna Armas Eino Elisabet Helmi Hilja Ilmari Johanna Johannes Juho Lauri Maria Martta Sofia Toivo Tyyne Vilho Väinö Yrjö".split(),
    "2": u"Murre Rekku Haukku yksi pallo".split(),
    "3": u"Miuku Mauku Kitler kaksi neliö".split(),
}

LIPPUKALA_CODE_MIN_N_DIGITS = 6
LIPPUKALA_CODE_MAX_N_DIGITS = 10

LIPPUKALA_PRINT_LOGO_PATH = "./fictitious_con.jpg"
LIPPUKALA_PRINT_LOGO_SIZE_CM = (5.84, 1.5)

INSTALLED_APPS = (
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "lippukala",
)

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": True,
        "OPTIONS": {},
    },
]

ROOT_URLCONF = "lippukala_test_app.urls"
DEBUG = True
