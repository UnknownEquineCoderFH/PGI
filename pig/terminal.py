from __future__ import annotations

from typing import Self
from attrs import define


@define(frozen=True)
class Terminal:
    """
    A terminal in a grammar.

    Ex. "a" | "b"
           ^ -- This is a Terminal

    NOTE: This is effectively a wrapper around a string
    """

    internal: str

    def __repr__(self) -> str:
        return f'"{self.internal}"'

    def __add__(self, other: object) -> Self:
        if not isinstance(other, Terminal):
            return NotImplemented

        return type(self)(f"{self.internal}{other.internal}")
