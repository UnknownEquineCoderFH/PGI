from __future__ import annotations

from typing import Iterator, TYPE_CHECKING

from isla.language import Grammar as ISLaGrammar, parse_bnf

if TYPE_CHECKING:
    from .predicate import Predicate
    from .expansion import Expansion


def load_bnf(path: str) -> ISLaGrammar:
    with open(path, "rt") as f:
        source = f.read()

    return parse_bnf(source)


def break_sequence(inp: str) -> Iterator[str]:
    skips = 0

    for idx, char in enumerate(inp):
        if skips:
            skips -= 1
            continue

        if char == "<":
            closing_tag = inp.find(">", idx)

            if closing_tag == -1:
                raise ValueError("Unclosed tag")

            skips += closing_tag - idx

            yield inp[idx : closing_tag + 1]
        else:
            yield char


def is_symbol(inp: str) -> bool:
    return inp.startswith("<") and inp.endswith(">")


def chain(first: Predicate[()], *predicates: Predicate[()]) -> Predicate[()]:
    """
    Returns a new predicate that combines multiple predicates into a single predicate.

    Args:
        predicates: A variable number of predicates to be combined.

    Returns:
        A new predicate that returns True if all of the given
        predicates return True, and False otherwise.
    """

    def inner(symbol: Expansion) -> bool:
        if not first(symbol):
            return False

        for predicate in predicates:
            if not predicate(symbol):
                return False

        return True

    return inner


def monomorphize[*Args](predicate: Predicate[*Args], *args: *Args) -> Predicate[()]:
    """
    Returns a new predicate that takes no extra arguments.

    Args:
        predicate: A predicate that takes arguments.
        args: The arguments to be passed to the predicate.

    """

    def inner(symbol: Expansion) -> bool:
        return predicate(symbol, *args)

    return inner
