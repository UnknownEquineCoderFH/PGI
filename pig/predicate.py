from __future__ import annotations

from typing import Protocol
from .expansion import Expansion


class Predicate[*Args](Protocol):
    def __call__(self, symbol: Expansion, *args: *Args) -> bool:
        ...
