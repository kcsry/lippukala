from __future__ import annotations

from lippukala.adapter import LippukalaAdapter


class AdapterMixin:
    _adapter: LippukalaAdapter | None = None

    def get_adapter(self) -> LippukalaAdapter:
        if not self._adapter:
            raise ValueError(f"An adapter needs to be set on {self.__class__.__name__}")
        return self._adapter
