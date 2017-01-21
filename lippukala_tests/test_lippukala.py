# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pytest
from django.conf import settings
from django.test import TestCase
from django.utils.six import BytesIO

from lippukala.models import Code, Order
from lippukala.reports import CodeReportWriter, get_code_report
from lippukala.settings import PREFIXES
from .utils import _create_test_order


class OrderCreationTest(TestCase):

    def test_creating_order(self):
        order = _create_test_order()
        self.assertTrue(order.code_set.count() == 25, "orders don't hold their codes")
        for code in order.code_set.all():
            self.assertTrue(code.literate_code.startswith(PREFIXES[code.prefix]), "prefixes don't work")

    def test_cant_create_invalid_prefix(self):
        order = Order.objects.create(comment="Dummy")

        def t1():
            Code.objects.create(order=order, prefix="HQ")
        self.assertRaises(ValueError, t1)

        def t2():
            Code.objects.create(order=order, prefix="69")
        self.assertRaises(ValueError, t2)
        order.delete()


class CodeUseTest(TestCase):

    def test_double_use_code(self):
        order = _create_test_order()
        code = order.code_set.all()[:1][0]
        self.assertFalse(code.is_used, "code is not used")
        code.set_used(save=True)
        self.assertTrue(code.is_used, "code is used")
        code = Code.objects.get(pk=code.pk)  # reload it to see if saving worked
        self.assertTrue(code.is_used, "code is used (even from the db)")

        def t():
            code.set_used()
        self.assertRaises(ValueError, t)


class ReportTest(TestCase):

    def test_csv_reports_have_good_stuff(self):
        order = _create_test_order()
        csv_report_data = get_code_report("csv", False).decode(settings.DEFAULT_CHARSET)
        # We don't particularly care if we have extra orders/codes at this point, just as long
        # as the ones we just created are found
        for code in order.code_set.all():
            assert (code.literate_code in csv_report_data), "code %r was missing" % code

    def test_all_report_formats_seem_to_work(self):
        _create_test_order()
        formats = [n.split("_")[1] for n in dir(CodeReportWriter) if n.startswith("format_")]
        for format in formats:
            self.assertTrue(get_code_report(format, False, True))
            self.assertTrue(get_code_report(format, True, False))


@pytest.mark.parametrize("one_per_page", (False, True))
@pytest.mark.django_db
def test_printing(one_per_page):
    from lippukala.printing import OrderPrinter
    printer = OrderPrinter()
    printer.ONE_TICKET_PER_PAGE = one_per_page
    for x in range(3):
        order = _create_test_order()
        printer.process_order(order)

    outf = BytesIO()
    outf.write(printer.finish())
    assert outf.getvalue().startswith(b"%PDF")
