from __future__ import annotations

from typing import Protocol, Iterator
from .non_terminal import NonTerminal
from .filter import Filter
from .expansion import Expansion
from .grammar import Grammar


class Generator(Protocol):
    filter: Filter
    grammar: Grammar

    def __call__(self, symbol: NonTerminal) -> Iterator[Expansion]:
        ...
