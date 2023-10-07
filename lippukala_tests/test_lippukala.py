from io import BytesIO

import pytest
from django.conf import settings

from lippukala.models import Code, Order
from lippukala.reports import CodeReportWriter, get_code_report

from .utils import create_test_order

pytestmark = pytest.mark.django_db


def test_creating_order(adapter, test_order):
    prefixes = adapter.get_prefixes()
    assert test_order.code_set.count() == 25, "orders don't hold their codes"
    for code in test_order.code_set.all():
        assert code.literate_code.startswith(prefixes[code.prefix]), "prefixes don't work"


def test_cant_create_invalid_prefix():
    order = Order.objects.create(comment="Dummy")

    with pytest.raises(ValueError):
        Code.objects.create(order=order, prefix="HQ")

    with pytest.raises(ValueError):
        Code.objects.create(order=order, prefix="69")

    order.delete()


def test_double_use_code(test_order):
    code = test_order.code_set.all()[:1][0]
    assert not code.is_used, "code is not used"
    code.set_used(save=True)
    assert code.is_used, "code is used"
    code = Code.objects.get(pk=code.pk)  # reload it to see if saving worked
    assert code.is_used, "code is used (even from the db)"

    with pytest.raises(ValueError):
        code.set_used()


def test_csv_reports_have_good_stuff(test_order):
    csv_report_data = get_code_report("csv", False).decode(settings.DEFAULT_CHARSET)
    # We don't particularly care if we have extra orders/codes at this point, just as long
    # as the ones we just created are found
    for code in test_order.code_set.all():
        assert code.literate_code in csv_report_data, f"code {code!r} was missing"


def test_all_report_formats_seem_to_work(test_order):
    formats = [n.split("_")[1] for n in dir(CodeReportWriter) if n.startswith("format_")]
    for format in formats:
        assert get_code_report(format, False, True)
        assert get_code_report(format, True, False)


@pytest.mark.parametrize("one_per_page", (False, True))
def test_printing(one_per_page, adapter):
    from lippukala.printing import OrderPrinter

    prefix = next(iter(adapter.get_prefixes()))

    printer = OrderPrinter(
        print_logo_path=adapter.get_print_logo_path(prefix),
        print_logo_size_cm=adapter.get_print_logo_size_cm(prefix),
    )
    printer.ONE_TICKET_PER_PAGE = one_per_page
    for x in range(3):
        order = create_test_order(adapter)
        printer.process_order(order)

    outf = BytesIO()
    outf.write(printer.finish())
    assert outf.getvalue().startswith(b"%PDF")
