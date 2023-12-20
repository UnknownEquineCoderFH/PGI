# Artifact Submission for "Input Invariants"

This artifact describes how to 

* *obtain* the ISLa and ISLearn tools for the paper "Input Invariants" accepted
  for ESEC/FSE'22,
* *reproduce* the results reported in the paper, and
* *apply* the tools to your examples.
 
We describe these aspects separately for the ISLa and ISLearn systems.

## The ISLa Solver

ISLa is publicly available on GitHub and the Python Package Index (PyPI). The
following URLs are relevant for ISLa:

* DOI for the ISLa version corresponding to this artifact: https://doi.org/10.5281/zenodo.7034971
* GitHub repository: https://github.com/rindPHI/isla
* ISLa web page: https://rindphi.github.io/isla/
* ISLa on PyPI: https://pypi.org/project/isla-solver/

The following pages are also linked from the ISLa README and the web page:

* ISLa tutorial: https://www.fuzzingbook.org/beta/html/FuzzingWithConstraints.html
* ISLa language specification: https://rindphi.github.io/isla/islaspec/

The web page describes how ISLa is installed as a library or for testing
and development. To use it as a library, a simple `pip install isla-solver`
suffices; the only requirement is a Python 3.10 installation with `pip`
available.

### Reproducing the Results from the Paper

The easiest way to reproduce our results is using our provided Docker image.
With Docker installed and its daemon running, copy the following instructions
into a terminal:

```shell
docker pull dsteinhoefel/isla:0.10.6
docker run -it --name isla dsteinhoefel/isla:0.10.6
```

**NOTE:** If you get a message "The container name "/isla" is already in use..."
(this happens, e.g., if you use `docker run` multiple times), you have a choice:

- You can delete the existing container by running `docker rm /isla`,
- You can rename the existing container, e.g., into "isla_other," using `docker
  rename /isla /isla_other`,
- You start and enter the existing container (which you should only do if it is
  a container of the same image, e.g., resulting from an earlier `docker run`):

  ```shell
  docker start /isla
  docker exec -it isla fish
  ```

Now, you should have entered a [fish
shell](https://fishshell.com/docs/current/fish_for_bash_users.html#fish-for-bash-users)
inside the Docker container. Next, change into the `isla/` directory by typing
`cd isla/`. If you wish to upgrade to the newest ISLa version (optional,
regressions possible), change to the main branch (`git checkout main`) and pull
the last changes (`git pull`).

Optionally, you can now test the ISLa installation:

```shell
python3 -m pytest -n 16 tests
```

The parameter `-n 16` specifies that the tests should run in 16 parallel
processes. You can adapt this to your needs if necessary.

Then, run evaluation scripts for the input languages we studied in the paper:

* CSV: `fish run_eval_csv.fish`
* reST: `fish run_eval_rest.fish`
* Scriptsize-C: `fish run_eval_scriptsize_c.fish`
* TAR: `fish run_eval_tar.fish`
* XML: `fish run_eval_xml.fish`

The scripts perform two ISLa runs of one hour each. In the end, they print
information on the obtained efficiency (inputs/min), precision (valid
inputs/min), diversity (percentage of covered k-paths), and mean/median input
length (numbers of characters) directly to the terminal. You can run all five
scripts in parallel, which might, however, degrade performance.

An example output for CSV after only one (demo) run of 20 sec is

```
+--------------------+------------+------------------+------------+--------------------------+
| Job                | Efficiency |    Precision     | Diversity  | Mean/Median Input Length |
+--------------------+------------+------------------+------------+--------------------------+
| CSV Grammar Fuzzer |    1056.00 | 568.00 ( 53.79%) |     79.78% |            9.63 /   8.00 |
| CSV Cnt-Columns    |     934.00 | 934.00 (100.00%) |     99.47% |          289.18 / 288.50 |
+--------------------+------------+------------------+------------+--------------------------+
```

If you wish to adapt the evaluation scripts, you can ask the case study-specific
evaluator classes for information about the available parameters, for example:

```
> python3 evaluations/evaluate_csv.py -h
usage: evaluate_csv.py [-h] [--db DB] [-n NUMSESSIONS] [-l] [-g] [-v] [-p] [-a] [-c | -d] [-j JOBS] [-t TIMEOUT] [-k KVALUES]

Evaluating the ISLa producer with case study CSV.

options:
  -h, --help            show this help message and exit
  --db DB               Path to the sqlite database file. (default: /home/isla/isla/src/isla_evaluation.sqlite)
  -n NUMSESSIONS, --numsessions NUMSESSIONS
                        The number of sessions to generate or analyze. For analysis, this can be set to -1; in this case, all sessions are analyzed. (default: 1)
  -l, --listjobs        Shows all jobs for this evaluator. (default: False)
  -g, --generate        Generate inputs with a timeout of [timeout] seconds, [numsessions] times. (default: False)
  -v, --validity        Compute validity of the inputs of the previous [numsessions] sessions. (default: False)
  -p, --kpaths          Compute k-paths for the inputs of the previous [numsessions] sessions. (default: False)
  -a, --analyze         Analyze the accumulated results of the previous [numsessions] sessions. (default: False)
  -c, --clean           Removes all data related to the given job(s) from the database. WARNING: This cannot be undone! (default: False)
  -d, --dryrun          Does not write results to database when *generating* (-g). Does not affect -v and -p. (default: False)
  -j JOBS, --jobs JOBS  Comma-separated list of jobs to run / evaluate. (default: Grammar Fuzzer, Cnt-Columns)
  -t TIMEOUT, --timeout TIMEOUT
                        The timeout for test input generation. Useful with the '-g' option. (default: 3600)
  -k KVALUES, --kvalues KVALUES
                        Comma-separated list of the values 'k' for which to compute k-path coverage. Useful with the '-p' option. (default: 3,4)
```

### Applying ISLa to Your Examples

If you wish to use ISLa for different languages, we highly recommend our
[interactive Jupyter notebook
tutorial](https://www.fuzzingbook.org/beta/html/FuzzingWithConstraints.html).
The tutorial can be opened as an editable Jupyter notebook using the Binder
service, which enables you to adapt the existing examples to your needs or
create new ones. Alternatively, we provide instructions on running the example
from the README file on the ISLa web page/GitHub.

First, install ISLa using `pip install isla-solver`. To minimize package
conflicts, we recommend using a virtual environment:

```shell
python3.10 -m venv venv
source venv/bin/activate  # activate.fish in fish, etc.
pip install isla-solver
```

Alternatively, you can use our Docker image following the instructions above.

Then, create a file named `example.py` (adapt as you like) and fill it with the
following content:

```python
import string

from isla.solver import ISLaSolver
from isla.isla_predicates import BEFORE_PREDICATE

LANG_GRAMMAR = {
    "<start>":
        ["<stmt>"],
    "<stmt>":
        ["<assgn>", "<assgn> ; <stmt>"],
    "<assgn>":
        ["<var> := <rhs>"],
    "<rhs>":
        ["<var>", "<digit>"],
    "<var>": list(string.ascii_lowercase),
    "<digit>": list(string.digits)
}

concrete_syntax_formula = '''
  forall <assgn> assgn_1:
    exists <assgn> assgn_2:
      (before(assgn_2, assgn_1) and assgn_1.<rhs>.<var> = assgn_2.<var>)'''

solver = ISLaSolver(
    grammar=LANG_GRAMMAR,
    formula=concrete_syntax_formula,
    structural_predicates={BEFORE_PREDICATE},
    max_number_free_instantiations=10,
    max_number_smt_instantiations=10)

it = solver.solve()
while True:
    try:
        print(next(it))
    except StopIteration:
        break
```

This produces a series of assignments of the form `x := 1 ; y := x`, where
variables occurring as right-hand sides are declared in a previous assignment
(which is a context-sensitive property). You need to press Ctrl-C to interrupt
the input generation.

The format for specifying context-free grammars is inspired by the [Fuzzing
Book](https://www.fuzzingbook.org/html/Grammars.html). To adapt this example to
your use case, we recommend studying our
[tutorial](https://www.fuzzingbook.org/beta/html/FuzzingWithConstraints.html).
The [ISLa language specification](https://rindphi.github.io/isla/islaspec/)
provides additional information on the ISLa specification language.

## The ISLearn Input Invariants Learner

ISLearn is publicly available on GitHub and the Python Package Index (PyPI). The
following URLs are relevant for ISLearn:

* DOI for the ISLearn version corresponding to this artifact: https://doi.org/10.5281/zenodo.7035007
* GitHub repository: https://github.com/rindPHI/islearn
* ISLearn on PyPI: https://pypi.org/project/islearn/

### Reproducing the Results from the Paper

The easiest way to reproduce our results is using our provided Docker image.
With Docker installed and its daemon running, copy the following instructions
into a terminal:

```shell
docker pull dsteinhoefel/islearn:0.2.13
docker run -it --name islearn dsteinhoefel/islearn:0.2.13
```

**NOTE:** If you get a message "The container name "/islearn" is already in
use..." (this happens, e.g., if you use `docker run` multiple times), you have a
choice:

- You can delete the existing container by running `docker rm /islearn`, 
- You can rename the existing container, e.g., into "islearn_other," using
  `docker rename /islearn /islearn_other`,
- You start and enter the existing container (which you should only do if it is
  a container of the same image, e.g., resulting from an earlier `docker run`):

  ```shell
  docker start /islearn
  docker exec -it islearn fish
  ```

Now, you should have entered a [fish
shell](https://fishshell.com/docs/current/fish_for_bash_users.html#fish-for-bash-users)
inside the Docker container. Next, change into the `islearn/` directory by
typing `cd islearn/`. If you wish to upgrade to the newest ISLearn version
(optional, regressions possible), change to the main branch (`git checkout
main`) and pull the last changes (`git pull`).

Optionally, you can now test the ISLearn installation:

```shell
python3 -m pytest -n 16 tests
```

The parameter `-n 16` specifies that the tests should run in 16 parallel
processes. You can adapt this to your needs if necessary.

Next, run the Python scripts for learning invariants for our case studies DOT,
Racket, and ICMP:

```shell
python3 evaluations/dot/evaluate_dot.py
python3 evaluations/icmp/evaluate_icmp.py
python3 evaluations/racket/evaluate_racket.py
```

The ICMP example does not include the Internet checksum, since we had to add
this primitive especially for that use case. To include the checksum into the
instantiated patterns, uncomment the line `# "Checksums",` in
`evaluate_icmp.py`.

### Applying ISLearn to Your Examples

Alternatively, we provide instructions on running the example from the README
file on the ISLearn GitHub repository.

First, install ISLearn using `pip install islearn`. To minimize package
conflicts, we recommend using a virtual environment:

```shell
python3.10 -m venv venv
source venv/bin/activate  # activate.fish in fish, etc.
pip install islearn
```

Alternatively, you can use our Docker image following the instructions above.

Then, create a file named `example.py` (adapt as you like) and fill it with the
following content:

```python
import string
from typing import Dict, Tuple

from isla.solver import ISLaSolver
from isla.isla_predicates import BEFORE_PREDICATE
from isla.language import DerivationTree, Formula, ISLaUnparser 
from isla.parser import EarleyParser
from isla.type_defs import ParseTree

from islearn.learner import InvariantLearner
from islearn.parse_tree_utils import dfs, get_subtree, tree_to_string


LANG_GRAMMAR = {
    "<start>":
        ["<stmt>"],
    "<stmt>":
        ["<assgn>", "<assgn> ; <stmt>"],
    "<assgn>":
        ["<var> := <rhs>"],
    "<rhs>":
        ["<var>", "<digit>"],
    "<var>": list(string.ascii_lowercase),
    "<digit>": list(string.digits)
}


def eval_lang(inp: str) -> Dict[str, int]:
    def assgnlhs(assgn: ParseTree):
        return tree_to_string(get_subtree(assgn, (0,)))

    def assgnrhs(assgn: ParseTree):
        return tree_to_string(get_subtree(assgn, (2,)))

    valueMap: Dict[str, int] = {}
    tree = list(EarleyParser(LANG_GRAMMAR).parse(inp))[0]

    def evalAssignments(tree):
        node, children = tree
        if node == "<assgn>":
            lhs = assgnlhs(tree)
            rhs = assgnrhs(tree)
            if rhs.isdigit():
                valueMap[lhs] = int(rhs)
            else:
                valueMap[lhs] = valueMap[rhs]

    dfs(tree, evalAssignments)

    return valueMap

def validate_lang(inp: DerivationTree) -> bool:
    try:
        eval_lang(str(inp))
        return True
    except Exception:
        return False

result: Dict[Formula, Tuple[float, float]] = InvariantLearner(
    LANG_GRAMMAR,
    prop=validate_lang,
    activated_patterns={  # Optional; leads to quicker results
        "Def-Use (reST Strict)",
    },
).learn_invariants()

print("\n".join(map(
    lambda p: f"{p[1]}: " + ISLaUnparser(p[0]).unparse(),
    {f: p for f, p in result.items() if p[0] > .0}.items())))
```

This produces the single invariant with full recall and specificity for the
assignment language, specifying that each right-hand side variable has to be
declared in a previous assignment (sometimes, you get an empty output; run again
in that case). The corresponding pattern has been derived from the reST case
study conducted in the ISLa part of the evaluation. The assignment language and
learned constraint are the same as those provided in the ISLa example earlier in
this document.

Information about the parameters accepted by the `InvariantLearner` class is
provided in the [ISLearn
README](https://github.com/rindPHI/islearn/blob/main/README.md).
In particular, `InvariantLearner` accepts a parameter `patter_file` where you
can provide your own patterns (schematic ISLa formulas). The default pattern
catalog can be found in the source distribution (from the GitHub repository)
under `src/islearn/patterns.toml`. An example pattern is

```
[[Existential]]

name = "String Existence"
constraint = '''
forall <?NONTERMINAL> container in start:
  exists <?NONTERMINAL> elem in container:
    (= elem <?STRING>)
'''
```

The placeholder `<?NONTERMINAL>` can represent any nonterminal from the
reference grammar; `<?STRING>` is some string constant. A third type of
placeholder occurs in the following pattern:

```
[[Misc]]

name = "Balance"
constraint = '''
forall <?NONTERMINAL> container="{<?MATCHEXPR(opid, clid)>}" in start:
  (= opid clid)
'''
```

The placeholder variable `<?MATCHEXPR(opid, clid)>` represents some match
expression containing two bound elements `opid` and `clid` that can be used
inside the quantified formula.

Apart from the pattern catalog, you must supply a grammar and a property as
above. The property is a function from an `isla.derivation_tree.DerivationTree`
object to `bool`. The learner tries to find an ISLa formula describing exactly
the inputs satisfying the given property.
