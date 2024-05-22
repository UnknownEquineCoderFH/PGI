from __future__ import annotations

from typing import Self, Iterator, Sequence

from isla.language import Grammar as ISLaGrammar
from attrs import define, Factory

from .utils import chain, monomorphize, break_sequence, is_symbol
from .non_terminal import NonTerminal
from .terminal import Terminal
from .expression import Expression
from .expansion import Expansion
from .predicate import Predicate


@define
class Grammar:
    rules: dict[NonTerminal, Expression]
    allow_recursive: bool = False
    recursion_limit: int = 5
    predicates: dict[NonTerminal, Predicate[()]] = Factory(dict)

    def __attrs_post_init__(self) -> None:
        if not self.allow_recursive:
            recursive: set[NonTerminal] = {
                symbol for symbol in self.rules if self.is_recursive_rule(symbol)
            }

            if recursive:
                raise ValueError(f"Some recursive rules were detected {recursive}") from None

    def export(self, file: str) -> None:
        with open(file, "w") as f:
            for line in self.expand():
                f.write(f"{line}\n")

    def load_constraints(self, file: str) -> Self:
        preds: tuple[Predicate[()], ...] = (
            lambda symbol: len(symbol) > 2,
            lambda symbol: symbol.contains_all("ab"),
            lambda symbol: symbol.sample(20),
        )

        for pred in preds:
            self.add_predicate(NonTerminal("<id>"), pred)

        return self

    def add_predicate[*Args](self, symbol: NonTerminal, predicate: Predicate[*Args], *args: *Args):
        if (fn := self.predicates.get(symbol)) is None:
            self.predicates[symbol] = monomorphize(predicate, *args)
        else:
            self.predicates[symbol] = chain(monomorphize(predicate, *args), fn)

    def __iter__(self) -> Iterator[tuple[NonTerminal, Expression]]:
        return iter(self.rules.items())

    def __repr__(self) -> str:
        return "\n".join(f"{k} ::= {v}" for k, v in self.rules.items())

    def is_recursive_rule(self, symbol: NonTerminal, /) -> bool:
        expr = self.rules[symbol]

        for alt in expr.expansions:
            for element in alt:
                if isinstance(element, NonTerminal) and (
                    element == symbol or (self.is_recursive_rule(element))
                ):
                    return True

        return False

    def expansions_count(self, symbol: NonTerminal = NonTerminal("<start>"), /) -> int:
        expr = self.rules[symbol]
        n_alts = [1 for _ in expr.expansions]

        for idx, alt in enumerate(expr.expansions):
            for element in alt:
                if isinstance(element, NonTerminal):
                    n_alts[idx] *= self.expansions_count(element)

        return sum(n_alts)

    def expand_one(self, symbol: NonTerminal = NonTerminal("<start>"), /) -> tuple[Expansion, ...]:
        partial = (rule.expand_one(self) for rule in self.rules[symbol].expansions)

        return tuple(item for sublist in partial for item in sublist)

    def expand_one_from_alts(self, alts: Sequence[Expansion], /) -> tuple[Expansion, ...]:
        partial = (alt.expand_one(self) for alt in alts)

        return tuple(item for sublist in partial for item in sublist)

    def _rules_can_expand(self, alts: Sequence[Expansion], /) -> bool:
        return all(rule.can_expand() for rule in alts)

    def expand(self, symbol: NonTerminal = NonTerminal("<start>"), /) -> Iterator[Expansion]:
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

    def apply_expansion(self, symbol: NonTerminal = NonTerminal("<start>"), /) -> Self:
        expansions = self.expand(symbol)
        alts = list(expansions)
        self.rules[symbol] = Expression(alts)

        return self

    def next_rule(self) -> Iterator[NonTerminal]:
        complexities = dict[NonTerminal, int]()

        for symbol, nt in self:
            complexities[symbol] = nt.complexity()

        occurrences = sorted(complexities.items(), key=lambda x: x[1], reverse=True)

        for symbol, _ in occurrences:
            yield symbol

    def partial_expand(self, symbol: NonTerminal | str = NonTerminal("<start>"), /) -> Self:
        if isinstance(symbol, str):
            symbol = NonTerminal.symbol(symbol)

        for rule in self.next_rule():
            self.apply_expansion(rule)

            if rule == symbol:
                break

        return self

    @classmethod
    def from_isla(cls, isla_grammar: ISLaGrammar, /) -> Grammar:
        rules = dict[NonTerminal, Expression]()

        for tag, val in isla_grammar.items():
            alts = list[Expansion]()

            for alt in val:
                components = break_sequence(alt)

                transformed = [NonTerminal(c) if is_symbol(c) else Terminal(c) for c in components]

                alts.append(Expansion(transformed))

            rules[NonTerminal(tag)] = Expression(alts)

        return cls(rules)
