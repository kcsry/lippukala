# -*- coding: utf-8 -*-
from string import digits
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


def get_setting(name, default=None):
    return getattr(settings, "LIPPUKALA_%s" % name, default)

def get_integer_setting(name, default=0):
    try:
        value = get_setting(name, default)
        return int(value)
    except ValueError:
        raise ImproperlyConfigured("LIPPUKALA_%s must be an integer (got %r)" % (name, value))

PREFIXES = get_setting("PREFIXES", {})
LITERATE_KEYSPACES = get_setting("LITERATE_KEYSPACES", {})
CODE_MIN_N_DIGITS = get_integer_setting("CODE_MIN_N_DIGITS", 10)
CODE_MAX_N_DIGITS = get_integer_setting("CODE_MAX_N_DIGITS", 10)
CODE_ALLOW_LEADING_ZEROES = bool(get_setting("CODE_ALLOW_LEADING_ZEROES", True))

def validate_settings():
    key_lengths = [len(k) for k in PREFIXES]
    if key_lengths and not all(k == key_lengths[0] for k in key_lengths):
        raise ImproperlyConfigured("All LIPPUKALA_PREFIXES keys must be the same length!")

    if CODE_MIN_N_DIGITS <= 5 or CODE_MAX_N_DIGITS < CODE_MIN_N_DIGITS:
        raise ImproperlyConfigured("The range (%d .. %d) for Lippukala code digits is invalid" % (CODE_MIN_N_DIGITS, CODE_MAX_N_DIGITS))

    for prefix in PREFIXES:
        if not all(c in digits for c in prefix):
            raise ImproperlyConfigured("The prefix %r has invalid characters. Only digits are allowed." % prefix)

    for prefix, literate_keyspace in LITERATE_KEYSPACES.iteritems():
        if isinstance(literate_keyspace, basestring):
            raise ImproperlyConfigured("A string (%r) was passed as the literate keyspace for prefix %r" % (literate_keyspace, prefix))
        if any(len(key) <= 1 for key in literate_keyspace) or len(set(literate_keyspace)) != len(literate_keyspace):
            raise ImproperlyConfigured("The literate keyspace for prefix %r has invalid or duplicate entries." % prefix)


validate_settings()
del validate_settings  # aaaand it's gone