# -*- coding: utf-8 -*-

# This file uses a fairly vile hack to allow it to run as a
# single-file Django app, for testing Lippukala.
# Please excuse me.

import os, sys, tempfile

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "__main__")

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(tempfile.gettempdir(), "lippukala_test.sqlite3"),
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

LIPPUKALA_PRINT_LOGO_PATH = "./fictitious_con.jpg"
LIPPUKALA_PRINT_LOGO_SIZE_CM = (5.84, 1.5)

INSTALLED_APPS = ("lippukala", )
ROOT_URLCONF = "__main__"
DEBUG = True

from django.conf.urls import patterns, url
from lippukala.views import POSView
from django.views.decorators.csrf import csrf_exempt

urlpatterns = patterns("",
   url("^pos/$", csrf_exempt(POSView.as_view())),
)

def seed():
    from lippukala.tests import _create_test_order
    for x in xrange(20):
        print _create_test_order().pk


if __name__ == "__main__":
    from django.core.management import execute_from_command_line
    try:
        func = globals().get(sys.argv[1])
    except:
        func = None
    if func and callable(func):
        func()
    else:
        execute_from_command_line(sys.argv)