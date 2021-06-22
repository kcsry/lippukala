from random import randint, choice
from string import digits

from django.db import models
from django.utils.timezone import now

from lippukala.consts import CODE_STATUS_CHOICES, UNUSED, USED
from lippukala.excs import CantUseException
from lippukala.models import Order
import lippukala.settings as settings


class Code(models.Model):

    """ Encapsulates a single code, belonging to an order, that may be used to claim one or more products, as described in product_text. """
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(choices=CODE_STATUS_CHOICES, default=UNUSED)
    used_on = models.DateTimeField(blank=True, null=True)
    used_at = models.CharField(max_length=64, blank=True, help_text="Station at which code was used")
    prefix = models.CharField(max_length=16, blank=True, editable=False)
    code = models.CharField(max_length=64, unique=True, editable=False)
    literate_code = models.CharField(max_length=256, blank=True, editable=False)
    product_text = models.CharField(max_length=512, blank=True, editable=False)

    full_code = property(lambda self: f"{self.prefix}{self.code}")
    is_used = property(lambda self: self.status == USED)

    def __str__(self):
        return f"Code {self.full_code} ({self.literate_code}) ({self.get_status_display()})"

    def _generate_code(self):
        qs = self.__class__.objects
        for attempt in range(500):  # 500 attempts really REALLY should be enough.
            n_digits = randint(settings.CODE_MIN_N_DIGITS, settings.CODE_MAX_N_DIGITS + 1)
            code = ("".join(choice(digits) for x in range(n_digits)))
            if not settings.CODE_ALLOW_LEADING_ZEROES:
                code = code.lstrip("0")
            # Leading zeroes could have dropped digits off the code, so recheck that.
            if settings.CODE_MIN_N_DIGITS <= len(code) <= settings.CODE_MAX_N_DIGITS:
                if not qs.filter(code=code).exists():
                    return code

        raise ValueError("Unable to find an unused code! Is the keyspace exhausted?")

    def _generate_literate_code(self):
        keyspace = (settings.LITERATE_KEYSPACES.get(self.prefix) or settings.LITERATE_KEYSPACES.get(None))

        if not keyspace:  # When absolutely no keyspaces can be found, assume (prefix+code) will do
            return self.full_code

        bits = []
        val = int(self.code, 10)
        n = len(keyspace)
        assert val > 0
        while val > 0:
            val, digit = divmod(val, n)
            bits.append(keyspace[digit])

        bits = bits[::-1]  # We have to reverse `bits` to get the least significant digit to be the first word.

        if self.prefix:  # Oh -- and if we had a prefix, add its literate counterpart now.
            bits.insert(0, settings.PREFIXES[self.prefix])

        return " ".join(bits).strip()

    def _check_sanity(self):
        if self.used_on and self.status != USED:
            raise ValueError("Un-sane situation detected: saving Code with used status and no usage date")
        if self.status != UNUSED and not self.pk:
            raise ValueError("Un-sane situation detected: initial save of code with non-virgin status!")
        if not all(c in digits for c in self.full_code):
            raise ValueError("Un-sane situation detected: full_code contains non-digits. (This might mean a contaminated prefix configuration.)")
        if not settings.PREFIX_MAY_BE_BLANK and not self.prefix:
            raise ValueError("Un-sane situation detected: prefix may not be blank")
        if self.prefix and self.prefix not in settings.PREFIXES:
            raise ValueError(f"Un-sane situation detected: prefix {self.prefix!r} is not in PREFIXES")

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self._generate_code()

        if not self.literate_code:
            self.literate_code = self._generate_literate_code()

        self._check_sanity()

        return super().save(*args, **kwargs)

    def set_used(self, save=True, used_at=""):
        if self.status != UNUSED:
            raise CantUseException(f"Can't use a code in {self.get_status_display()} status!")
        self.status = USED
        self.used_on = now()
        self.used_at = used_at
        if save:
            return self.save()
