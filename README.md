# Complex Polynomial Solving
Tool for showing that a system of complex polynomials is satisfiable.

## System
A system of $m$ complex polynomials is defined as:

$$f_1(x_1,x_2,...,x_n) = 0$$

$$f_2(x_1,x_2,...,x_n) = 0$$

$$\vdots$$

$$f_m(x_1,x_2,...,x_n) = 0$$

where $x_1,x_2,...,x_n \in \mathbb{C}$

The polynomial $f_i$ is defined as:

$$f_i(x_1,x_2,...,x_n) = \sum_{j=1}^{p}(c_j\prod_{k=1}^{n}x_k^{e_k})$$

where $c_j \in \mathbb{R}$ and $e_k \in \mathbb{Z}^+$

## Installing

```bash
conda env create -f environment.yml
```

## TODOs
- [ ] Refactor SAT code and make it more readable.
- [ ] Add bitvector based solver for z3.
- [ ] Fix the main.py file so that it can read polynomials from files
- [ ] Find benchmark for testing the solver
- [ ] Compare performance of integer based solver, SAT solver and bitvector solver.
- [ ] Find a value for number of primes `NUM_PRIMES_TO_SAMPLE` that gives good enough results for benchmarks

