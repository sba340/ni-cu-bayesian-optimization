# Ni–Cu Bayesian Optimization for Catalyst Screening

Three complementary Bayesian optimization (BO) workflows for screening Ni–Cu bimetallic catalyst
configurations, developed as part of ongoing DFT/ML-driven catalyst discovery research.

## Contents

### [`discrete-benchmark/`](./discrete-benchmark)
A discrete-candidate-pool BO workflow for Ni–Cu catalyst screening, guided by the approach in
([Kayode, Hill & Montemore, 2023, *J. Mater. Chem. A*](https://doi.org/10.1039/D3TA02830E)) and
adapted to a fixed lookup table of pre-computed DFT adsorption energies. No relaxations run live —
this validates the BO search strategy against a known dataset and benchmarks it against random
search.

### [`active-learning-screening/`](./active-learning-screening)
A live BO loop coupling BoTorch/GPyTorch to on-the-fly relaxations with Meta FAIR's FAIRChem
(Open Catalyst Project) ML-potential, screening Ni–Cu composition × adsorption-site space for
low-energy ethylidyne (–CCH₃) binding configurations — a coking-precursor surrogate relevant to
renewable diesel / hydrodeoxygenation catalysis.

### [`sp-rx-surrogate-screening/`](./sp-rx-surrogate-screening)
A single-fidelity surrogate screening workflow that uses a cheap single-point (SP) adsorption
energy as a proxy descriptor for the more expensive relaxed (RX) adsorption energy. A Gaussian
Process trained on 50 structures with known SP and RX values is used to predict RX and its
uncertainty across a pool of 10,000 candidates, which are then ranked by predictive uncertainty to
select the next batch for DFT relaxation.

## Why three approaches

The `discrete-benchmark` establishes that the BO strategy reliably finds target adsorption
energies against ground-truth data. The `active-learning-screening` workflow then applies that
same BO-driven search logic to a real, continuous discovery setting — proposing and relaxing new
structures on the fly rather than picking from a pre-computed table. The `sp-rx-surrogate-screening`
workflow sits between the two: it uses a physically motivated cheap descriptor (SP) to screen a
much larger candidate pool before committing to expensive RX relaxations, prioritizing which
structures are worth relaxing next.

## Requirements

Each subfolder has its own `requirements.txt` — install within the subfolder you're running.

## Author

Sahar Bayat — PhD Candidate, [Risko Lab](https://www.riskolab.org/), University of Kentucky
