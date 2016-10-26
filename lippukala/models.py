# -*- coding: utf-8 -*-
from random import choice, randint
from string import digits

from django.db import models
from django.utils.six.moves import xrange
from django.utils.timezone import now

from .settings import CODE_ALLOW_LEADING_ZEROES, CODE_MAX_N_DIGITS, CODE_MIN_N_DIGITS, LITERATE_KEYSPACES, PREFIXES

###
# --- Constants ---
###

UNUSED = 0
USED = 1
MANUAL_INTERVENTION_REQUIRED = 2
BEYOND_LOGIC = 3

CODE_STATUS_CHOICES = (
    (UNUSED, "Unused"),
    (USED, "Used"),
    (MANUAL_INTERVENTION_REQUIRED, "Manual intervention required"),
    (BEYOND_LOGIC, "Beyond logic")
)

if PREFIXES:
    PREFIX_CHOICES = [(p, "%s [%s]" % (p, t)) for (p, t) in sorted(PREFIXES.items())]
    PREFIX_MAY_BE_BLANK = False
else:
    PREFIX_CHOICES = [("", "---")]
    PREFIX_MAY_BE_BLANK = True

###
# --- Models ---
###


class CantUseException(ValueError):
    pass


class Order(models.Model):

    """ Encapsulates an order, which may contain zero or more codes.

    :var event: An (optional) event identifier for this order. May be used at the client app's discretion.
    """
    event = models.CharField(max_length=32, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)
    reference_number = models.CharField(blank=True, null=True, max_length=64, unique=True, help_text="Reference number, unique")
    address_text = models.TextField(blank=True, help_text="Text printed in the PDF address area")
    free_text = models.TextField(blank=True, help_text="Text printed on PDF")
    comment = models.TextField(blank=True, help_text="Administrative comment")

    def __unicode__(self):
        return "LK-%08d (ref %s)" % (self.pk, self.reference_number)


class Code(models.Model):

    """ Encapsulates a single code, belonging to an order, that may be used to claim one or more products, as described in product_text. """
    order = models.ForeignKey(Order)
    created_on = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(choices=CODE_STATUS_CHOICES, default=UNUSED)
    used_on = models.DateTimeField(blank=True, null=True)
    used_at = models.CharField(max_length=64, blank=True, help_text="Station at which code was used")
    prefix = models.CharField(max_length=16, blank=True, editable=False)
    code = models.CharField(max_length=64, unique=True, editable=False)
    literate_code = models.CharField(max_length=256, blank=True, editable=False)
    product_text = models.CharField(max_length=512, blank=True, editable=False)

    full_code = property(lambda self: "%s%s" % (self.prefix, self.code))
    is_used = property(lambda self: self.status == USED)

    def __unicode__(self):
        return "Code %s (%s) (%s)" % (self.full_code, self.literate_code, self.get_status_display())

    def _generate_code(self):
        qs = self.__class__.objects
        for attempt in range(500):  # 500 attempts really REALLY should be enough.
            n_digits = randint(CODE_MIN_N_DIGITS, CODE_MAX_N_DIGITS + 1)
            code = ("".join(choice(digits) for x in range(n_digits)))
            if not CODE_ALLOW_LEADING_ZEROES:
                code = code.lstrip("0")
            # Leading zeroes could have dropped digits off the code, so recheck that.
            if CODE_MIN_N_DIGITS <= len(code) <= CODE_MAX_N_DIGITS:
                if not qs.filter(code=code).exists():
                    return code

        raise ValueError("Unable to find an unused code! Is the keyspace exhausted?")

    def _generate_literate_code(self):
        keyspace = (LITERATE_KEYSPACES.get(self.prefix) or LITERATE_KEYSPACES.get(None))

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
            bits.insert(0, PREFIXES[self.prefix])

        return " ".join(bits).strip()

    def _check_sanity(self):
        if self.used_on and self.status != USED:
            raise ValueError("Un-sane situation detected: saving Code with used status and no usage date")
        if self.status != UNUSED and not self.pk:
            raise ValueError("Un-sane situation detected: initial save of code with non-virgin status!")
        if not all(c in digits for c in self.full_code):
            raise ValueError("Un-sane situation detected: full_code contains non-digits. (This might mean a contaminated prefix configuration.)")
        if not PREFIX_MAY_BE_BLANK and not self.prefix:
            raise ValueError("Un-sane situation detected: prefix may not be blank")
        if self.prefix and self.prefix not in PREFIXES:
            raise ValueError("Un-sane situation detected: prefix %r is not in PREFIXES" % self.prefix)

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self._generate_code()

        if not self.literate_code:
            self.literate_code = self._generate_literate_code()

        self._check_sanity()

        return super(Code, self).save(*args, **kwargs)

    def set_used(self, save=True, used_at=""):
        if self.status != UNUSED:
            raise CantUseException("Can't use a code in %s status!" % self.get_status_display())
        self.status = USED
        self.used_on = now()
        self.used_at = used_at
        if save:
            return self.save()
