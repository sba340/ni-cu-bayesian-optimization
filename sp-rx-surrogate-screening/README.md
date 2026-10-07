# SP to RX Surrogate-Based Bayesian Optimization Screening

## Overview

This workflow uses a cheap single-point (SP) adsorption energy as a surrogate
descriptor for the more expensive relaxed (RX) adsorption energy, then applies
Gaussian Process regression and uncertainty-based ranking to prioritize the
next round of DFT relaxations from a pool of 10,000 candidate structures.

It complements the other two workflows in this repo:
- `discrete-benchmark/` validates BO search strategy against a fixed,
  precomputed lookup table.
- `active-learning-screening/` runs a live BO loop with on-the-fly FAIRChem
  relaxations.
- `sp-rx-surrogate-screening/` (this folder) sits between the two: it uses a
  physically motivated cheap proxy (SP) to screen a much larger candidate
  pool before committing to expensive RX relaxations.

## Method

1. Load 50 structures with both SP and RX adsorption energies (ground truth).
2. Confirm SP is predictive of RX via 5-fold cross-validated linear
   regression (MAE = 0.105 eV, R2 = 0.78).
3. Train a Gaussian Process (RBF + White kernel, standardized input) mapping
   SP to RX on the 50 known structures.
4. Apply the trained GP to a pool of 10,000 candidates (SP-only, from cheap
   single-point calculations) to predict RX and its uncertainty.
5. Flag candidates whose SP values fall outside the training range
   (extrapolation risk) and exclude them from the ranking.
6. Rank remaining in-domain candidates by predicted uncertainty (variance
   based exploration) and select the top 20 for the next round of RX
   (relaxed) DFT calculations.
7. Export the selected candidates to `results/top20_BO_candidates.xlsx`.

## Round 2 results and an open question

The 20 round 1 candidates were relaxed via DFT and folded into the training
set (50 to 70 structures). Retraining the GP on the expanded set made
performance worse, not better: MAE went from 0.105 eV to 0.24 eV, and R2
dropped from 0.78 to 0.38.

The likely cause: round 1's pure uncertainty sampling concentrated almost
all 20 selections in a narrow SP window (about -4.71 to -4.72 eV), where
SP turned out to be a poor predictor of RX. Points at nearly identical SP
had RX values spanning roughly 2 eV, which pulls the GP's fit toward an
unstable compromise in that region rather than improving it.

`ni_cu_distribution_report.py` was added to investigate this. It compares
the Ni/Cu layer distribution, local composition around the bound carbon,
and Cu clustering for structures with SP outside the training range
(`too_strong` and `too_weak` groups) against a random sample of in-domain,
low-uncertainty structures. The goal is to check whether some structural
feature other than SP (for example adsorption site, Cu clustering near the
adsorbate, or which layer the Cu atoms sit in) explains the SP-RX
breakdown, which would suggest SP alone is not sufficient as a descriptor
in that part of the composition space.

## Files

```
sp-rx-surrogate-screening/
├── sp_rx_surrogate_bo.ipynb          # main notebook
├── ni_cu_distribution_report.py      # investigates the round 2 SP-RX breakdown
├── requirements.txt
├── data/
│   ├── dataset.xlsx                  # known structures (SP + RX, ground truth)
│   │                                 # you need to provide your own known structures
│   │                                 # with identified SP and RX energies
│   └── dataset10000.xlsx             # candidate pool (SP only, + outside_training_range
│                                     # flag, + structure_file names) you need to provide
│                                     # your own large dataset with identified SP energies
└── results/
    └── top20_BO_candidates.xlsx      # top 20 candidates selected in round 1
```

## Requirements

See `requirements.txt`. Install with:

```bash
pip install -r requirements.txt
```

`ni_cu_distribution_report.py` additionally requires `ase` and expects
`pool_all` and `file_map` to already exist in the session (see its header
comment for details).

## Notes

- This notebook runs a single BO iteration (uncertainty sampling round), not
  a full retraining loop. Candidates selected here are meant to be relaxed
  via DFT, folded back into the training set, and used to retrain the GP for
  a subsequent round.
- Ranking currently uses pure uncertainty sampling (max variance), not an
  acquisition function like Expected Improvement or UCB. See the note in the
  main README's "Why three approaches" section for how this fits into the
  broader screening strategy.
- Round 2 showed that uncertainty sampling alone can over-concentrate
  selections in one narrow region. A next step worth considering is mixing
  in some exploration across the full SP range, or switching to an
  acquisition function that balances uncertainty against predicted RX.

## Author

Sahar Bayat, PhD Candidate, [Risko Lab](https://www.riskolab.org/), University of Kentucky
