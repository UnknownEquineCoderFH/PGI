from __future__ import annotations

import random
from typing import Iterator, Sequence, Callable, TYPE_CHECKING
from itertools import product

from attrs import define, field

from .non_terminal import NonTerminal
from .terminal import Terminal

if TYPE_CHECKING:
    from .grammar import Grammar


@define
class Expansion:
    """
    An alternative expansion of a non-terminal.

    Ex. "a" | <prefix> "b" | <prefix> "c" <suffix> etc... Are all Alts
    """

    elements: list[Terminal | NonTerminal]
    _repr: str = field(init=False)

    def __attrs_post_init__(self) -> None:
        elements = list[Terminal | NonTerminal]()
        acc = ""

        for element in self.elements:
            if isinstance(element, Terminal):
                acc += element.internal
            else:
                elements.append(Terminal(acc))
                elements.append(element)

                acc = ""

        if acc:
            elements.append(Terminal(acc))

        internal = "".join(element.internal for element in elements)

        self._repr = f'"{internal}"'

    def __repr__(self) -> str:
        return self._repr

    def __iter__(self) -> Iterator[Terminal | NonTerminal]:
        return iter(self.elements)

    @property
    def collapsed(self) -> str:
        """
        Collapses the Alt into a single string
        """
        return self._repr

    def __len__(self) -> int:
        return len(self.collapsed)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Expansion):
            return self.collapsed == other

        return self.collapsed == other.collapsed

    def __hash__(self) -> int:
        return hash(self.collapsed)

    def __index__(self) -> int:
        try:
            return int(self.collapsed)
        except ValueError:
            raise ValueError(f"{self.collapsed} is not an integer") from None

    def __contains__(self, element: object) -> bool:
        if not isinstance(element, (Terminal, NonTerminal)):
            return False

        return element in self.elements

    def contains_any(self, els: Sequence[str]) -> bool:
        return any(element in self.collapsed for element in els)

    def contains_all(self, els: Sequence[str]) -> bool:
        return all(element in self.collapsed for element in els)

    def sample(self, chance: int) -> bool:
        if chance == 0:
            return False

        if chance == 100:
            return True

        if chance < 0 or chance > 100:
            raise ValueError("Chance must be between 0 and 100")

        return (random.random() * 100) > chance

    def check_child(
        self, target: NonTerminal, predicate: Callable[[str], bool]
    ) -> bool:
        for child in self:
            if isinstance(child, NonTerminal) and child == target:
                ...

        raise ValueError(f"{target} is not found in {self}")

    def tokens(self) -> Iterator[str]:
        """
        Iterates over the inner string representation of all
        erminals and symbols in the Alt
        """
        for element in self.elements:
            yield element.internal

    def add(self, element: Terminal | NonTerminal, /) -> None:
        """
        Adds an element to the Alt
        """
        self.elements.append(element)

    def extend(self, elements: Sequence[Terminal | NonTerminal], /) -> None:
        """
        Adds multiple elements to the Alt
        """
        self.elements.extend(elements)

    def can_expand(self) -> bool:
        """
        Returns whether the Alt can be expanded into a list of Alts
        starting from non terminals in it.
        """
        for element in self.elements:
            if isinstance(element, NonTerminal):
                return True

        return False

    def expand_one(self, grammar: Grammar) -> list[Expansion]:
        """
        Expands a single ALt into a list of Alts

        **1** step only!
        """

        elements: list[list[Expansion] | list[Terminal]] = [
            list() for _ in range(len(self.elements))
        ]

        for idx, element in enumerate(self.elements):
            if isinstance(element, NonTerminal):
                elements[idx] = grammar.rules[element].expansions
            else:
                elements[idx] = [element]

        # Product is typed wrong when you pass *args into it,
        # maybe in the future they will use TypeVarTuples
        # Until then, we have to do this
        partial: product[list[Expansion] | list[Terminal]] = product(*elements)  # type: ignore

        return Expansion._expand_into_alts(partial)

    @staticmethod
    def _expand_into_alts(
        partial: Iterator[list[Expansion] | list[Terminal]], /
    ) -> list[Expansion]:
        """
        Expands any iterator over a list of alts an terminals into a list of alts,
        effectively flattening it.
        """
        tmp_alts = list[Expansion]()

        for alts in partial:
            tmp = list[Terminal | NonTerminal]()

            for alt in alts:
                if isinstance(alt, Expansion):
                    tmp.extend(alt.elements)
                else:
                    tmp.append(alt)
            tmp_alts.append(Expansion(tmp))

        return tmp_alts
