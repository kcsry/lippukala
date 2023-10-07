import pytest

from lippukala.adapter import LippukalaAdapter, get_adapter


@pytest.fixture
def adapter(rf) -> LippukalaAdapter:
    return get_adapter(rf.get("/"))
