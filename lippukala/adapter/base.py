from __future__ import annotations

from abc import ABCMeta, abstractmethod

from django.http import HttpRequest

IMPLEMENT_IN_A_SUBCLASS = "Implement in a subclass"


class LippukalaAdapter(metaclass=ABCMeta):
    def __init__(self, request: HttpRequest | None) -> None:
        self.request = request

    @abstractmethod
    def get_prefixes(self) -> dict[str, str]:
        raise NotImplementedError(IMPLEMENT_IN_A_SUBCLASS)

    @abstractmethod
    def get_literate_keyspace(self, prefix: str | None) -> list[str] | None:
        raise NotImplementedError(IMPLEMENT_IN_A_SUBCLASS)

    @abstractmethod
    def get_code_digit_range(self, prefix: str) -> range:
        raise NotImplementedError(IMPLEMENT_IN_A_SUBCLASS)

    @abstractmethod
    def get_code_allow_leading_zeroes(self, prefix: str) -> bool:
        raise NotImplementedError(IMPLEMENT_IN_A_SUBCLASS)

    @abstractmethod
    def get_print_logo_path(self, prefix: str) -> str | None:
        raise NotImplementedError(IMPLEMENT_IN_A_SUBCLASS)

    @abstractmethod
    def get_print_logo_size_cm(self, prefix: str) -> tuple[float, float]:
        raise NotImplementedError(IMPLEMENT_IN_A_SUBCLASS)

    def get_prefix_may_be_blank(self) -> bool:
        return not self.get_prefixes()
