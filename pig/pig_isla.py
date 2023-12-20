from __future__ import annotations

from isla.solver import ISLaSolver
from isla.type_defs import Grammar
from isla.derivation_tree import DerivationTree
from isla.helpers import crange
from typing import Callable
import re
from graphviz import Digraph
import string


def dot_escape(s: str, show_ascii=None) -> str:
    """Return s in a form suitable for dot.
    If `show_ascii` is True or length of `s` is 1, also append ascii value."""
    escaped_s = ""
    if show_ascii is None:
        show_ascii = len(s) == 1  # Default: Single chars only

    if show_ascii and s == "\n":
        return "\\\\n (10)"

    s = s.replace("\n", "\\n")
    for c in s:
        if re.match('[,<>\\\\"]', c):
            escaped_s += "\\" + c
        elif c in string.printable and 31 < ord(c) < 127:
            escaped_s += c
        else:
            escaped_s += "\\\\x" + format(ord(c), "02x")

        if show_ascii:
            escaped_s += f" ({ord(c)})"

    return escaped_s


def extract_node(
    node: DerivationTree, id: int
) -> tuple[str, list[DerivationTree], str]:
    symbol, children, *annotation = node
    return symbol, children, "".join(str(a) for a in annotation)  # type: ignore


def default_node_attr(dot: Digraph, nid: int, symbol: str, ann: str):
    dot.node(repr(nid), dot_escape(symbol))


def default_edge_attr(dot: Digraph, start_node: int, stop_node: int):
    dot.edge(repr(start_node), repr(stop_node))


def default_graph_attr(dot: Digraph):
    dot.attr("node", shape="plain")


def display_tree(
    derivation_tree: DerivationTree,
    log: bool = False,
    extract_node: Callable[
        [DerivationTree, int], tuple[str, list[DerivationTree], str]
    ] = extract_node,
    node_attr: Callable[[Digraph, int, str, str], None] = default_node_attr,
    edge_attr: Callable[[Digraph, int, int], None] = default_edge_attr,
    graph_attr: Callable[[Digraph], None] = default_graph_attr,
) -> Digraph:
    counter = 0

    def traverse_tree(dot: Digraph, tree: DerivationTree, id: int = 0):
        (symbol, children, annotation) = extract_node(tree, id)
        node_attr(dot, id, symbol, annotation)

        if children:
            for child in children:
                nonlocal counter
                counter += 1
                child_id = counter
                edge_attr(dot, id, child_id)
                traverse_tree(dot, child, child_id)

    dot = Digraph(comment="Derivation Tree")
    graph_attr(dot)
    traverse_tree(dot, derivation_tree)
    if log:
        print(dot)
    return dot


XML_GRAMMAR: Grammar = {
    "<start>": ["<xml-tree>"],
    "<xml-tree>": ["<open-tag><xml-content><close-tag>"],
    "<open-tag>": ["<<id>>"],
    "<close-tag>": ["</<id>>"],
    "<xml-content>": ["<text>", "<xml-tree>"],
    "<id>": ["<letter>", "<id><letter>"],
    "<text>": ["<letter><text>", "<letter>"],
    "<letter>": crange("a", "z"),
}

solver = ISLaSolver(
    XML_GRAMMAR,
    """
    <xml-tree>.<open-tag>.<id> = <xml-tree>.<close-tag>.<id>
    """,
    max_number_smt_instantiations=5,
)


def navigate(tree: DerivationTree, father_id: str = "<start>"):
    # print(f'Examining {father_id}')
    value, id, children = tree.value, tree.id, tree.children
    if len(children):
        for child in children:
            child_id = f"{father_id}.{child.value}"
            navigate(child, child_id)
    else:
        print(f"No child for {id}")


def main() -> int:
    for _ in range(1):
        solution = solver.solve()
        print(solution)
        navigate(solution)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
