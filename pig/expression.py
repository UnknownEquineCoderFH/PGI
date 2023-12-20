from __future__ import annotations

from attrs import define

from typing import Iterator

from .non_terminal import NonTerminal
from .expansion import Expansion


@define
class Expression:
    """
    A non-terminal symbol in a grammar.
    """

    expansions: list[Expansion]

    def __repr__(self) -> str:
        return " | ".join(repr(e) for e in self.expansions)

    def __iter__(self) -> Iterator[Expansion]:
        return iter(self.expansions)

    def can_expand(self) -> bool:
        """
        Checks if the current instance of the class contains
        any symbol (and thus can be instantiated).

        Returns:
            bool: True if the current instance can be expanded, False otherwise.
        """
        return any(
            isinstance(element, NonTerminal)
            for alt in self.expansions
            for element in alt
        )

    def complexity(self) -> int:
        """
        Count the number of symbols in each Alt
        """

        acc = 0

        for alt in self.expansions:
            for element in alt:
                if isinstance(element, NonTerminal):
                    acc += 1

        return acc
