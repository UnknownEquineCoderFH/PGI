from __future__ import annotations

from .predicate import Predicate
from .expansion import Expansion


class Filter:
    predicates: list[Predicate[()]]

    def __call__(self, symbol: Expansion) -> bool:
        for predicate in self.predicates:
            if not predicate(symbol):
                return False

        return True

    def extend[
        *Args
    ](self, predicate: Predicate[*Args], *args: *Args,) -> None:
        def inner(symbol: Expansion) -> bool:
            return predicate(symbol, *args)

        self.predicates.append(inner)
