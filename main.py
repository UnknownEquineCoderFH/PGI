from __future__ import annotations

from pig.utils import load_bnf
from pig.non_terminal import NonTerminal
from pig.grammar import Grammar


grammar = load_bnf("grammars/numbers.bnf")

parsed = (
    Grammar.from_isla(grammar)
    .load_constraints("grammars/constraints.pig")
    .partial_expand(NonTerminal.symbol("start"))
)

print(parsed)
