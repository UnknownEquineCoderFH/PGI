from __future__ import annotations

from typing import Self
from attrs import define


@define(frozen=True)
class NonTerminal:
    """
    A symbol in a grammar.

    Ex. `<start>` ::= ...
          ^^^^^^ -- This is a symbol

    NOTE: This is effectively a wrapper around a string
    """

    internal: str

    def __repr__(self) -> str:
        return self.internal

    @classmethod
    def symbol(cls, name: str) -> Self:
        return cls(f"<{name}>")
