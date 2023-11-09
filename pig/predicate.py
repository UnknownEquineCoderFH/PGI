from __future__ import annotations

from typing import Protocol
from .alt import Alt


class Predicate[*Args](Protocol):
    def __call__(self, symbol: Alt, *args: *Args) -> bool:
        ...
