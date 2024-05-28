from __future__ import annotations

import random
import time

from django.utils.encoding import force_str

from lippukala.adapter import LippukalaAdapter
from lippukala.models import Code, Order


def create_test_order(adapter: LippukalaAdapter | None) -> Order:
    fname = random.choice(["Teppo", "Tatu", "Tauno", "Tintti", "Taika"])
    address_text = "\n".join(
        (
            f"{fname} Testinen",
            f"Testikatu {random.randint(1, 50):d}",
            f"{random.randint(0, 99999):05d} Turku",
            "Finland",
        )
    )
    order = Order.objects.create(
        adapter=adapter,
        address_text=address_text,
        free_text="Tervetuloa Testiconiin!",
        comment=f"{fname} on kiva jätkä.",
        reference_number=str(int(time.time() * 10000 + random.randint(0, 35474500))),
    )
    assert order.pk
    assert str(order.pk) in force_str(order)
    for x in range(25):
        prefix = str(x % 4)
        code = Code.objects.create(order=order, prefix=prefix, product_text="Lippu %d" % (x + 1))
        assert code.full_code in force_str(code)
        assert code.literate_code in force_str(code)
    return order
