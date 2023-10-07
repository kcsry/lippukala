import pytest

from lippukala.adapter import LippukalaAdapter, get_adapter
from lippukala.models import Order
from lippukala_tests.utils import create_test_order


@pytest.fixture
def adapter(rf) -> LippukalaAdapter:
    return get_adapter(rf.get("/"))


@pytest.fixture
def test_order(adapter) -> Order:
    return create_test_order(adapter)
