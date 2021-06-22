import random
import time

from lippukala.models import Order, Code
from django.utils.encoding import force_str


def _create_test_order():
    fname = random.choice(["Teppo", "Tatu", "Tauno", "Tintti", "Taika"])
    order = Order.objects.create(
        address_text="%s Testinen\nTestikatu %d\n%05d Turku\nFinland" % (fname, random.randint(1, 50), random.randint(0, 99999)),
        free_text="Tervetuloa Testiconiin!",
        comment=f"{fname} on kiva jätkä.",
        reference_number=str(int(time.time() * 10000 + random.randint(0, 35474500))),
    )
    assert order.pk
    assert str(order.pk) in force_str(order)
    for x in range(25):
        prefix = str(x % 4)
        code = Code.objects.create(
            order=order,
            prefix=prefix,
            product_text="Lippu %d" % (x + 1)
        )
        assert code.full_code in force_str(code)
        assert code.literate_code in force_str(code)
    return order
