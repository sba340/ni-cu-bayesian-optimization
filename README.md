# Ni–Cu Bayesian Optimization for Catalyst Screening

Two complementary Bayesian optimization (BO) workflows for screening Ni–Cu bimetallic catalyst
configurations, developed as part of ongoing DFT/ML-driven catalyst discovery research.

## Contents

### [`discrete-benchmark/`](./discrete-benchmark)
Reproduces a published discrete-candidate-pool BO method
([Kayode, Hill & Montemore, 2023, *J. Mater. Chem. A*](https://doi.org/10.1039/D3TA02830E)) on a
fixed lookup table of pre-computed DFT adsorption energies. No relaxations run live — this
validates the BO search strategy itself against a known dataset and benchmarks it against random
search.

### [`active-learning-screening/`](./active-learning-screening)
A live BO loop coupling BoTorch/GPyTorch to on-the-fly relaxations with Meta FAIR's FAIRChem
(Open Catalyst Project) ML-potential, screening Ni–Cu composition × adsorption-site space for
low-energy ethylidyne (–CCH₃) binding configurations — a coking-precursor surrogate relevant to
renewable diesel / hydrodeoxygenation catalysis.

## Why two approaches

The `discrete-benchmark` establishes that the BO strategy reliably finds target adsorption
energies against ground-truth data. The `active-learning-screening` workflow then applies that
same BO-driven search logic to a real, continuous discovery setting — proposing and relaxing new
structures on the fly rather than picking from a pre-computed table.

## Requirements

Each subfolder has its own `requirements.txt` — install within the subfolder you're running.

## Author

Sahar Bayat — PhD Candidate, [Risko Lab]([https://cbirt.as.uky.edu/](https://www.riskolab.org/)), University of Kentucky
