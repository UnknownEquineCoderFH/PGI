from __future__ import annotations

from itertools import product
from typing import Iterator, Never, Protocol, Sequence, TypeGuard, Callable, Self
import random

from attrs import define, Factory, field
from isla.language import Grammar as ISLaGrammar
from isla.language import parse_bnf

from functools import partial as Partial


_ = Partial

# from tatsu import parse, compile


def todo(message: str) -> Never:
    raise NotImplementedError(message)


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
        return self.internal


@define(frozen=True)
class Symbol:
    """
    A symbol in a grammar.

    Ex. `<start>` ::= ...
          ^^^^^^ -- This is a symbol

    NOTE: This is effectively a wrapper around a string
    """

    internal: str

    def __repr__(self) -> str:
        return self.internal


@define
class Alt:
    """
    An alternative expansion of a non-terminal.

    Ex. "a" | <prefix> "b" | <prefix> "c" <suffix> etc... Are all Alts
    """

    elements: list[Terminal | Symbol]
    _internal: str | None = field(init=False, default=None)

    def __repr__(self) -> str:
        return "".join(repr(e) for e in self.elements)

    def __iter__(self) -> Iterator[Terminal | Symbol]:
        return iter(self.elements)

    def collapse(self) -> str:
        """
        Collapses the Alt into a single string
        """
        if self._internal is None:
            self._internal = "".join(self.tokens())

        return self._internal

    def __len__(self) -> int:
        return len(self.collapse())

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Alt):
            return self.collapse() == other

        return self.collapse() == other.collapse()

    def __hash__(self) -> int:
        return hash(self.collapse())

    def __index__(self) -> int:
        try:
            return int(self.collapse())
        except ValueError:
            raise ValueError(f"{self.collapse()} is not an integer") from None

    def __contains__(self, element: object) -> bool:
        if not isinstance(element, (Terminal, Symbol)):
            return False

        return element in self.elements

    def contains_any(self, els: Sequence[str]) -> bool:
        return any(element in self for element in els)

    def contains_all(self, els: Sequence[str]) -> bool:
        return all(element in self.collapse() for element in els)

    def pick(self, chance: int) -> bool:
        if chance == 0:
            return False

        if chance == 100:
            return True

        if chance < 0 or chance > 100:
            raise ValueError("Chance must be between 0 and 100")

        return (random.random() * 100) > chance

    def check_child(self, target: Symbol, predicate: Callable[[str], bool]) -> bool:
        for child in self:
            if isinstance(child, Symbol) and child == target:
                ...

        raise ValueError(f"{target} is not found in {self}")

    def tokens(self) -> Iterator[str]:
        """
        Iterates over the inner string representation of all
        erminals and symbols in the Alt
        """
        for element in self.elements:
            yield element.internal

    def add(self, element: Terminal | Symbol, /) -> None:
        """
        Adds an element to the Alt
        """
        self.elements.append(element)

    def extend(self, elements: Sequence[Terminal | Symbol], /) -> None:
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
            if isinstance(element, Symbol):
                return True

        return False

    def expand_one(self, grammar: Grammar) -> list[Alt]:
        """
        Expands a single ALt into a list of Alts

        **1** step only!
        """

        elements: list[list[Alt] | list[Terminal]] = [
            list() for _ in range(len(self.elements))
        ]

        for idx, element in enumerate(self.elements):
            if isinstance(element, Symbol):
                elements[idx] = grammar.rules[element].expansions
            else:
                elements[idx] = [element]

        # Product is typed wrong when you pass *args into it,
        # maybe in the future they will use TypeVarTuples
        # Until then, we have to do this
        partial: product[list[Alt] | list[Terminal]] = product(*elements)  # type: ignore

        return Alt._expand_into_alts(partial)

    @staticmethod
    def _expand_into_alts(
        partial: Iterator[list[Alt] | list[Terminal]], /
    ) -> list[Alt]:
        """
        Expands any iterator over a list of alts an terminals into a list of alts,
        effectively flattening it.
        """
        tmp_alts = list[Alt]()

        for alts in partial:
            tmp = Alt([])
            for alt in alts:
                if isinstance(alt, Alt):
                    tmp.extend(alt.elements)
                else:
                    tmp.add(alt)
            tmp_alts.append(tmp)

        return tmp_alts


@define
class NonTerminal:
    """
    A non-terminal symbol in a grammar.
    """

    expansions: list[Alt]

    def __repr__(self) -> str:
        return " | ".join(repr(e) for e in self.expansions)

    def __iter__(self) -> Iterator[Alt]:
        return iter(self.expansions)

    def can_expand(self) -> bool:
        """
        Checks if the current instance of the class contains
        any symbol (and thus can be instantiated).

        Returns:
            bool: True if the current instance can be expanded, False otherwise.
        """
        return any(
            isinstance(element, Symbol) for alt in self.expansions for element in alt
        )


@define
class Grammar:
    rules: dict[Symbol, NonTerminal]
    allow_recursive: bool = False
    predicates: dict[Symbol, Predicate[()]] = Factory(dict)

    def __attrs_post_init__(self) -> None:
        if not self.allow_recursive:
            recursive: set[Symbol] = {
                symbol for symbol in self.rules if self.is_recursive_rule(symbol)
            }

            if recursive:
                raise ValueError(
                    f"Some recursive rules were detected {recursive}"
                ) from None

    def export(self, file: str) -> None:
        with open(file, "w") as f:
            for line in self.expand():
                f.write(f"{line}\n")

    def load_constraints(self, file: str) -> Self:
        preds: tuple[Predicate, ...] = (
            lambda symbol: len(symbol) > 4,
            lambda symbol: symbol.contains_all("abc"),
            lambda symbol: symbol.pick(20),
        )

        for pred in preds:
            self.add_predicate(Symbol("<start>"), pred)

        return self

    def add_predicate[
        *Args
    ](self, symbol: Symbol, predicate: Predicate[*Args], *args: *Args):
        if (fn := self.predicates.get(symbol)) is None:
            self.predicates[symbol] = monomorphize(predicate, *args)
        else:
            self.predicates[symbol] = chain(monomorphize(predicate, *args), fn)

    def __iter__(self) -> Iterator[tuple[Symbol, NonTerminal]]:
        return iter(self.rules.items())

    def __repr__(self) -> str:
        return "\n".join(f"{k} ::= {v}" for k, v in self.rules.items())

    def is_recursive_rule(self, symbol: Symbol, /) -> bool:
        nt = self.rules[symbol]

        for alt in nt.expansions:
            for element in alt:
                if isinstance(element, Symbol):
                    if element == symbol:
                        return True

                    if self.is_recursive_rule(element):
                        return True

        return False

    def expansions_count(self, symbol: Symbol = Symbol("<start>"), /) -> int:
        nt = self.rules[symbol]
        n_alts = [1 for _ in nt.expansions]

        for idx, alt in enumerate(nt.expansions):
            for element in alt:
                if isinstance(element, Symbol):
                    n_alts[idx] *= self.expansions_count(element)

        return sum(n_alts)

    def expand_one(self, symbol: Symbol = Symbol("<start>"), /) -> tuple[Alt, ...]:
        partial = (rule.expand_one(self) for rule in self.rules[symbol].expansions)

        return tuple(item for sublist in partial for item in sublist)

    def expand_one_from_alts(self, alts: Sequence[Alt], /) -> tuple[Alt, ...]:
        partial = (alt.expand_one(self) for alt in alts)

        return tuple(item for sublist in partial for item in sublist)

    def _rules_can_expand(self, alts: Sequence[Alt], /) -> bool:
        return all(rule.can_expand() for rule in alts)

    def expand(self, symbol: Symbol = Symbol("<start>"), /) -> Iterator[Alt]:
        alts = self.expand_one(symbol)

        while self._rules_can_expand(alts):
            alts = self.expand_one_from_alts(alts)

        predicate = self.predicates.get(symbol)

        if predicate:
            for alt in alts:
                if predicate(alt):
                    yield alt
        else:
            yield from alts

    @classmethod
    def from_isla(cls, isla_grammar: ISLaGrammar, /) -> Grammar:
        rules = dict[Symbol, NonTerminal]()

        for tag, val in isla_grammar.items():
            alts = list[Alt]()

            for alt in val:
                components = break_sequence(alt)

                transformed = [
                    Symbol(c) if is_symbol(c) else Terminal(c) for c in components
                ]

                alts.append(Alt(transformed))

            rules[Symbol(tag)] = NonTerminal(alts)

        return cls(rules)


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


def all_terminal(rules: list[Terminal | Symbol], /) -> TypeGuard[list[Terminal]]:
    return all(not is_symbol(rule.internal) for rule in rules)


class Predicate[*Args](Protocol):
    def __call__(self, symbol: Alt, *args: *Args) -> bool:
        ...


def chain(first: Predicate, *predicates: Predicate) -> Predicate:
    """
    Returns a new predicate that combines multiple predicates into a single predicate.

    Args:
        *predicates: A variable number of predicates to be combined.

    Returns:
        A new predicate that returns True if all of the given
        predicates return True, and False otherwise.
    """

    def inner(symbol: Alt) -> bool:
        if not first(symbol):
            return False

        for predicate in predicates:
            if not predicate(symbol):
                return False

        return True

    return inner


def monomorphize[*Args](predicate: Predicate[*Args], *args: *Args) -> Predicate[()]:
    def inner(symbol: Alt) -> bool:
        return predicate(symbol, *args)

    return inner


grammar = load_bnf("grammars/numbers.bnf")

parsed = Grammar.from_isla(grammar).load_constraints("grammars/constraints.pig")

expansions = parsed.export("./instantiated.txt")
