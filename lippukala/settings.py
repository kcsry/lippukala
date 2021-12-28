import os
from string import digits

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


def get_setting(name, default=None):
    return getattr(settings, f"LIPPUKALA_{name}", default)


def get_integer_setting(name, default=0):
    try:
        value = get_setting(name, default)
        return int(value)
    except ValueError:  # pragma: no cover
        raise ImproperlyConfigured(f"LIPPUKALA_{name} must be an integer (got {value!r})")


PREFIXES = get_setting("PREFIXES", {})
LITERATE_KEYSPACES = get_setting("LITERATE_KEYSPACES", {})
CODE_MIN_N_DIGITS = get_integer_setting("CODE_MIN_N_DIGITS", 10)
CODE_MAX_N_DIGITS = get_integer_setting("CODE_MAX_N_DIGITS", 10)
CODE_ALLOW_LEADING_ZEROES = bool(get_setting("CODE_ALLOW_LEADING_ZEROES", True))
PRINT_LOGO_PATH = get_setting("PRINT_LOGO_PATH")
PRINT_LOGO_SIZE_CM = get_setting("PRINT_LOGO_SIZE_CM")

if PREFIXES:
    PREFIX_CHOICES = [(p, f"{p} [{t}]") for (p, t) in sorted(PREFIXES.items())]
    PREFIX_MAY_BE_BLANK = False
else:
    PREFIX_CHOICES = [("", "---")]
    PREFIX_MAY_BE_BLANK = True


def validate_settings():  # pragma: no cover
    _validate_code()
    _validate_prefixes()
    _validate_print()


def _validate_code():
    if CODE_MIN_N_DIGITS <= 5 or CODE_MAX_N_DIGITS < CODE_MIN_N_DIGITS:
        raise ImproperlyConfigured(
            "The range (%d .. %d) for Lippukala code digits is invalid"
            % (CODE_MIN_N_DIGITS, CODE_MAX_N_DIGITS)
        )


def _validate_prefixes():
    key_lengths = [len(k) for k in PREFIXES]
    if key_lengths and not all(k == key_lengths[0] for k in key_lengths):
        raise ImproperlyConfigured("All LIPPUKALA_PREFIXES keys must be the same length!")
    for prefix in PREFIXES:
        if not all(c in digits for c in prefix):
            raise ImproperlyConfigured(
                f"The prefix {prefix!r} has invalid characters. Only digits are allowed."
            )
    for prefix, literate_keyspace in list(LITERATE_KEYSPACES.items()):
        if isinstance(literate_keyspace, str):
            raise ImproperlyConfigured(
                f"A string ({literate_keyspace!r}) was passed as the literate keyspace for prefix {prefix!r}"
            )
        too_short_keys = any(len(key) <= 1 for key in literate_keyspace)
        maybe_duplicate = len(set(literate_keyspace)) != len(literate_keyspace)
        if too_short_keys or maybe_duplicate:
            raise ImproperlyConfigured(
                f"The literate keyspace for prefix {prefix!r} has invalid or duplicate entries."
            )


def _validate_print():
    if PRINT_LOGO_PATH:
        if not os.path.isfile(PRINT_LOGO_PATH):
            raise ImproperlyConfigured(
                f"PRINT_LOGO_PATH was defined, but does not exist ({PRINT_LOGO_PATH!r})"
            )
        if not all(float(s) > 0 for s in PRINT_LOGO_SIZE_CM):
            raise ImproperlyConfigured(
                f"PRINT_LOGO_SIZE_CM values not valid: {PRINT_LOGO_SIZE_CM!r}"
            )


validate_settings()
del validate_settings  # aaaand it's gone
