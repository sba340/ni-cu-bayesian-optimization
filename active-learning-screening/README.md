# BO-Guided ML Screening of Ethylidyne Adsorption on Ni–Cu Alloy Surfaces

Bayesian Optimization (BoTorch/GPyTorch) coupled to Meta FAIR's **FAIRChem (Open Catalyst Project) UMA**
machine-learned interatomic potential to efficiently search Ni–Cu alloy composition × adsorption-site space
for low-energy binding configurations of ethylidyne (–CCH₃), a coking-precursor surrogate relevant to
renewable diesel / hydrodeoxygenation catalysis.

Instead of brute-force enumeration of every Cu-substitution pattern and site type, a Gaussian Process
surrogate model proposes the next configuration to evaluate, targeting low-energy motifs in a small number
of ML-potential relaxations.

## Workflow
1. Randomly substitute a subset of Ni atoms with Cu on a fixed slab (seed-controlled).
2. Place the adsorbate at a randomly selected on-top / bridge / hollow site.
3. Relax with the FAIRChem UMA potential (ASE + LBFGS).
4. Reject unphysical outcomes (dissociation, desorption).
5. Feed the resulting adsorption energy into a BoTorch GP model.
6. Repeat for a fixed step budget, checkpointing after every iteration so runs can resume.

## Contents
- `BO_Ni_Cu_ethylidyne_screening.ipynb` — main notebook (Colab-ready)
- `data/` — example slab and adsorbate POSCAR files (replace with your own system)
- `requirements.txt` — pinned-free dependency list for local use

## Running in Google Colab
Click the badge at the top of the notebook (or open it directly via
`File > Open notebook > GitHub` and paste this repo's URL). You will need:
- A free Hugging Face account with access to the FAIRChem UMA checkpoints
  (accept the model license on the model page, then generate a **read** token at
  https://huggingface.co/settings/tokens)
- A GPU runtime is recommended (Runtime > Change runtime type > GPU) but not required

## Running locally
```bash
pip install -r requirements.txt
jupyter notebook BO_Ni_Cu_ethylidyne_screening.ipynb
```

## Outputs
- `bo_results.csv` — energy/site/pass-fail log for every BO step
- `BEST_STRUCTURE.vasp` — lowest-energy configuration found
- `bo_structures/` — all accepted relaxed structures (VASP POSCAR format)
- `bo_trajectories/` — LBFGS relaxation trajectories
- `bo_checkpoint.pt`, `bo_checkpoint_meta.json` — resumable run state

## Attribution
Built on models and tools from the Open Catalyst Project / FAIR Chemistry team at Meta AI
([FAIRChem](https://github.com/FAIR-Chem/fairchem)) and [BoTorch](https://botorch.org/).
Please cite the OC20/UMA papers if you reuse this workflow.
