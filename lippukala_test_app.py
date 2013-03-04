# -*- coding: utf-8 -*-

# This file uses a fairly vile hack to allow it to run as a
# single-file Django app, for testing Lippukala.
# Please excuse me.

import os, sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "__main__")

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

LIPPUKALA_PREFIXES = {
    "0":    u"mat",
    "1":    u"nom",
    "2":    u"dog-jono",
    "3":    u"cat-jono",
}

LIPPUKALA_LITERATE_KEYSPACES = {
    "0":    u"hopea kulta kumi lanka muovi nahka naru pahvi rauta teräs".split(),
    "1":    u"Aino Anna Armas Eino Elisabet Helmi Hilja Ilmari Johanna Johannes Juho Lauri Maria Martta Sofia Toivo Tyyne Vilho Väinö Yrjö".split(),
    "2":    u"Murre Rekku Haukku yksi pallo".split(),
    "3":    u"Miuku Mauku Kitler kaksi neliö".split(),
}

LIPPUKALA_CODE_MIN_N_DIGITS = 6
LIPPUKALA_CODE_MAX_N_DIGITS = 10

INSTALLED_APPS = ("lippukala", )

from django.core.management import execute_from_command_line
execute_from_command_line(sys.argv)