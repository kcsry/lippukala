import os
import sys
import collections

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lippukala_test_app.settings")


def seed():
    from lippukala.tests import _create_test_order
    for x in range(20):
        print(_create_test_order().pk)


def manage():
    from django.core.management import execute_from_command_line
    try:
        func = globals().get(sys.argv[1])
    except:
        func = None
    if func and isinstance(func, collections.Callable):
        func()
    else:
        execute_from_command_line(sys.argv)


if __name__ == "__main__":
    manage()
