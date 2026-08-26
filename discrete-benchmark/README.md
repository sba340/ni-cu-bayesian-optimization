# Discrete Bayesian Optimization for Ni-Cu Catalyst Screening

Adapts the Bayesian optimization workflow from [Kayode, Hill & Montemore (2023), *J. Mater. Chem. A*, 11, 19128](https://doi.org/10.1039/D3TA02830E) to a Ni-Cu bimetallic coking-susceptibility dataset. Reproduces the paper's discrete-candidate-pool BO loop exactly — no ML potentials, relaxations, or continuous optimizers in the search itself.

## What this does

Given a fixed set of pre-computed DFT adsorption energies (one value per candidate configuration), the notebook:

1. Fits a Gaussian process regressor (GPR) on a small initial seed of known candidates
2. Uses expected improvement (adapted for target-value seeking, via Monte Carlo estimation) to recommend which untested candidate to "run DFT on" next
3. Pulls that candidate's energy from the lookup table (standing in for an actual DFT calculation)
4. Repeats until the recommendation lands within ±2% of a target adsorption energy, or 14 additional calculations are used — both stopping criteria taken directly from the paper

Includes a validation section benchmarking BO against random search across randomized targets, and a feature ablation testing whether a cheap ML-predicted energy descriptor improves search efficiency — mirroring Figs. 3c and 3d of the paper.

## Data

Two catalyst states, each with 50 candidate site/configuration combinations at fixed composition:

- `fresh_catalyst` — Ni84:Cu16
- `regenerated_catalyst` — Ni77:Cu23

Each candidate has: adsorption site type (top/bridge/hollow), an ML-predicted adsorption energy, and a full-relaxation DFT adsorption energy (used as ground truth).

`dataset.xlsx` is not included in this repo (raw/unpublished data). Supply your own file with matching structure to run the notebook.

## Usage

```
pip install numpy pandas scikit-learn matplotlib openpyxl
```

Place `dataset.xlsx` alongside the notebook, set `TARGET_EADS` and `CATALYST` in the single-target example cell, and run top to bottom.

## Reference

Kayode, G. O.; Hill, A. F.; Montemore, M. M. Bayesian optimization of single-atom alloys and other bimetallics: efficient screening for alkane transformations, CO₂ reduction, and hydrogen evolution. *J. Mater. Chem. A* **2023**, *11*, 19128–19137.
