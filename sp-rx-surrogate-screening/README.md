# SP → RX Surrogate-Based Bayesian Optimization Screening

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
   regression (MAE = 0.105 eV, R² = 0.78).
3. Train a Gaussian Process (RBF + White kernel, standardized input) mapping
   SP → RX on the 50 known structures.
4. Apply the trained GP to a pool of 10,000 candidates (SP-only, from cheap
   single-point calculations) to predict RX and its uncertainty.
5. Flag candidates whose SP values fall outside the training range
   (extrapolation risk) and exclude them from the ranking.
6. Rank remaining in-domain candidates by predicted uncertainty (variance-
   based exploration) and select the top 20 for the next round of RX
   (relaxed) DFT calculations.
7. Export the selected candidates to `results/top20_BO_candidates.xlsx`.

## Files

```
sp-rx-surrogate-screening/
├── sp_rx_surrogate_bo.ipynb        # main notebook
├── requirements.txt
├── data/
│   ├── dataset.xlsx                # 50 known structures (SP + RX, ground truth)
│   └── dataset10000.xlsx           # candidate pool (SP only, + outside_training_range flag, + structure_file names)
└── results/
    └── top20_BO_candidates.xlsx    # top 20 candidates selected for the next DFT round
```

## Requirements

See `requirements.txt`. Install with:

```bash
pip install -r requirements.txt
```

## Notes

- This notebook runs a single BO iteration (uncertainty sampling round), not
  a full retraining loop. Candidates selected here are meant to be relaxed
  via DFT, folded back into the training set, and used to retrain the GP for
  a subsequent round.
- Ranking currently uses pure uncertainty sampling (max variance), not an
  acquisition function like Expected Improvement or UCB — see the note in
  the main README's "Why two approaches" section for how this fits into the
  broader screening strategy.

## Author

Sahar Bayat — PhD Candidate, [Risko Lab](https://www.riskolab.org/), University of Kentucky
