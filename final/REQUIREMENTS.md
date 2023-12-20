# ISLa/ISLearn Requirements

If you plan to use ISLa and ISLearn based on our Docker images (see README.md),
you need to **have Docker installed**. It is unlikely that you will be able to
reproduce the same numbers (performance data) that we obtained in our ISLa
experiments. You can expect the closest results if you run the experiments in a
similar hardware environment. We used a MacBook Pro 2019 with a 2,4 GHz 8-core
Intel Core i9 processor and 32 GB RAM. 

ISLa and ISLearn have been tested on Linux and macOS machines.

## Basic Requirements

For installing ISLa/ISLearn on your machine, you need **Python 3.10**. The
concrete Python requirements for the tools (that should be automatically
installed when you run `pip install isla` or `pip install islearn`) are
documented in our Python requirements.txt files on GitHub:

- https://github.com/rindPHI/isla/blob/main/requirements.txt
- https://github.com/rindPHI/islearn/blob/main/requirements.txt

In the Docker image based on Alpine Linux, we also had to install `python3-dev`
(for the Python header files), `gcc`, `g++`, `make`, and `cmake` to be able to
build and install the Python requirements.

## Requirements for Testing and Evaluation

When running the tests and evaluations, you need the extended requirements in
the `requirements_test.txt` files:

- https://github.com/rindPHI/isla/blob/main/requirements_test.txt
- https://github.com/rindPHI/islearn/blob/main/requirements_test.txt
 
Those are automatically installed when locally installing ISLa/ISLearn as
described in README.md and INSTALL.md, i.e., by running `pip install -e
.[dev,test]`.

### Testing and Evaluating ISLa

For the ISLa tests and evaluations, you need clang and csvlint. The latter
executable can be obtained from
`https://github.com/Clever/csvlint/releases/download/v0.3.0/csvlint-v0.3.0-linux-amd64.tar.gz`;
both are already installed in the Docker image for ISLa. 

### Testing and Evaluating ISLearn

For evaluating the ISLearn, a Racket installation and GraphViz is required (in
Alpine: `apk add racket graphviz`). As usual, the ISLearn Docker image contains
all requirements.
