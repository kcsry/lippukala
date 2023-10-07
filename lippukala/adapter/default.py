from __future__ import annotations

import os
from string import digits

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from lippukala.adapter.base import LippukalaAdapter


def get_setting(name, default=None):
    return getattr(settings, f"LIPPUKALA_{name}", default)


def get_integer_setting(name, default=0):
    try:
        value = get_setting(name, default)
        return int(value)
    except ValueError:  # pragma: no cover
        raise ImproperlyConfigured(f"LIPPUKALA_{name} must be an integer (got {value!r})")


class LippukalaSettings:
    def __init__(self) -> None:
        self.prefixes = get_setting("PREFIXES", {})
        self.literate_keyspaces = get_setting("LITERATE_KEYSPACES", {})
        self.code_min_n_digits = get_integer_setting("CODE_MIN_N_DIGITS", 10)
        self.code_max_n_digits = get_integer_setting("CODE_MAX_N_DIGITS", 10)
        self.code_allow_leading_zeroes = bool(get_setting("CODE_ALLOW_LEADING_ZEROES", True))
        self.print_logo_path = get_setting("PRINT_LOGO_PATH")
        self.print_logo_size_cm = get_setting("PRINT_LOGO_SIZE_CM")

        if self.prefixes:
            self.prefix_choices = [(p, f"{p} [{t}]") for (p, t) in sorted(self.prefixes.items())]
            self.prefix_may_be_blank = False
        else:
            self.prefix_choices = [("", "---")]
            self.prefix_may_be_blank = True

    def validate(self) -> None:  # pragma: no cover
        self._validate_code()
        self._validate_prefixes()
        self._validate_print()

    def _validate_code(self) -> None:
        if self.code_min_n_digits <= 5 or self.code_max_n_digits < self.code_min_n_digits:
            raise ImproperlyConfigured(
                f"The range ({self.code_min_n_digits} .. {self.code_max_n_digits}) for "
                f"Lippukala code digits is invalid"
            )

    def _validate_prefixes(self):
        key_lengths = [len(k) for k in self.prefixes]
        if key_lengths and not all(k == key_lengths[0] for k in key_lengths):
            raise ImproperlyConfigured("All LIPPUKALA_PREFIXES keys must be the same length!")
        for prefix in self.prefixes:
            if not all(c in digits for c in prefix):
                raise ImproperlyConfigured(
                    f"The prefix {prefix!r} has invalid characters. Only digits are allowed."
                )
        for prefix, literate_keyspace in list(self.literate_keyspaces.items()):
            if isinstance(literate_keyspace, str):
                raise ImproperlyConfigured(
                    f"A string ({literate_keyspace!r}) was passed as the "
                    f"literate keyspace for prefix {prefix!r}"
                )
            too_short_keys = any(len(key) <= 1 for key in literate_keyspace)
            maybe_duplicate = len(set(literate_keyspace)) != len(literate_keyspace)
            if too_short_keys or maybe_duplicate:
                raise ImproperlyConfigured(
                    f"The literate keyspace for prefix {prefix!r} has invalid or duplicate entries."
                )

    def _validate_print(self):
        if not self.print_logo_path:
            return
        if not os.path.isfile(self.print_logo_path):
            raise ImproperlyConfigured(
                f"PRINT_LOGO_PATH was defined, but does not exist ({self.print_logo_path!r})"
            )
        if not all(float(s) > 0 for s in self.print_logo_size_cm):
            raise ImproperlyConfigured(f"PRINT_LOGO_SIZE_CM values not valid: {self.print_logo_size_cm!r}")


class DefaultLippukalaAdapter(LippukalaAdapter):
    _settings: LippukalaSettings | None = None

    @classmethod
    def get_settings(cls) -> LippukalaSettings:
        if not cls._settings:
            cls._settings = LippukalaSettings()
            cls._settings.validate()
        return cls._settings

    def get_prefixes(self) -> dict[str, str]:
        return self.get_settings().prefixes

    def get_literate_keyspace(self, prefix: str | None) -> list[str] | None:
        literate_keyspaces = self.get_settings().literate_keyspaces
        return literate_keyspaces.get(prefix)

    def get_code_digit_range(self, prefix: str) -> range:
        s = self.get_settings()
        return range(s.code_min_n_digits, s.code_max_n_digits + 1)

    def get_code_allow_leading_zeroes(self, prefix: str) -> bool:
        return self.get_settings().code_allow_leading_zeroes

    def get_print_logo_path(self, prefix: str) -> str | None:
        return self.get_settings().print_logo_path

    def get_print_logo_size_cm(self, prefix: str) -> tuple[float, float]:
        return self.get_settings().print_logo_size_cm
