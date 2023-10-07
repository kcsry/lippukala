from __future__ import annotations

from django.conf import settings
from django.http import HttpRequest
from django.utils.module_loading import import_string

from lippukala.adapter.base import LippukalaAdapter

try:
    from functools import cache
except ImportError:  # Remove this when deprecating Python 3.9 support
    from functools import lru_cache

    cache = lru_cache(maxsize=None)

DEFAULT_ADAPTER_REFERENCE = "lippukala.adapter.default.DefaultLippukalaAdapter"


@cache
def get_adapter_class() -> type[LippukalaAdapter]:
    adapter_class_name = getattr(settings, "LIPPUKALA_ADAPTER_CLASS", DEFAULT_ADAPTER_REFERENCE)
    return import_string(adapter_class_name)


def get_adapter(request: HttpRequest) -> LippukalaAdapter:
    return get_adapter_class()(request)
