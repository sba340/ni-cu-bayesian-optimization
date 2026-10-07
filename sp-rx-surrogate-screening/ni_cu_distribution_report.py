# ============================================================
# Ni/Cu distribution report: worst-certainty vs best-certainty structures
#
# Purpose: investigate whether structures with extreme GP uncertainty
# (SP values outside the training range, split into "too_strong" and
# "too_weak" groups) differ systematically in their Ni/Cu arrangement
# from a random sample of low-uncertainty, in-domain structures.
#
# Prerequisites (must exist in the notebook before running this cell):
#   pool_all  : the candidate pool DataFrame with a "group" column
#               already set to one of "too_strong", "too_weak", or
#               "low_uncertainty" for each row, plus "SP", "pred_RX",
#               and "pred_std" columns from the trained GP.
#   file_map  : a dict mapping config_id -> path to that structure's
#               POSCAR file.
#
# Requires: ase (atomic simulation environment), pandas, numpy, openpyxl
# ============================================================
import os, shutil
import numpy as np
import pandas as pd
from ase.io import read
from ase.geometry import find_mic

N_BEST       = 200     # number of low-uncertainty structures to sample
BOUND_CUTOFF = 2.5     # Angstrom, bound carbon to metal
LOCAL_RADIUS = 4.0     # Angstrom, sideways radius around the adsorbate in the top layer
CUCU_CUTOFF  = 3.0     # Angstrom, Cu-Cu nearest-neighbour distance
OUT_XLSX     = "/content/NiCu_distribution_report.xlsx"
OUT_DIR      = "/content/selected_POSCARs"


def split_layers(z, gap=0.8):
    """Split metal atoms into layers by z-coordinate. Returns top layer first."""
    order = np.argsort(-z)
    layers = [[order[0]]]
    for prev, cur in zip(order[:-1], order[1:]):
        if z[prev] - z[cur] > gap:
            layers.append([])
        layers[-1].append(cur)
    return layers


def ni_cu_features(path):
    """Compute Ni/Cu composition features for one structure's POSCAR."""
    atoms = read(path, format="vasp")
    sym = np.array(atoms.get_chemical_symbols())
    metal = np.where(np.isin(sym, ["Ni", "Cu"]))[0]
    is_cu = sym == "Cu"
    out = {}

    # Ni and Cu counts in each layer (layer 1 = top)
    layers = split_layers(atoms.positions[metal, 2])
    for i, l in enumerate(layers, start=1):
        idx = metal[l]
        out[f"Cu_L{i}"] = int(is_cu[idx].sum())
        out[f"Ni_L{i}"] = int(len(idx) - is_cu[idx].sum())
    out["Cu_total"] = int(is_cu[metal].sum())

    # surface-bound carbon = carbon closest to any metal atom
    c_all = np.where(sym == "C")[0]
    dmin = [atoms.get_distances(c, metal, mic=True).min() for c in c_all]
    c_b = c_all[int(np.argmin(dmin))]

    d = atoms.get_distances(c_b, metal, mic=True)
    bound = metal[d < BOUND_CUTOFF]
    out["Cu_bound"] = int(is_cu[bound].sum())
    out["Ni_bound"] = int(len(bound) - is_cu[bound].sum())

    # top-layer atoms around the adsorbate (sideways distance)
    top = metal[layers[0]]
    vec = atoms.positions[top] - atoms.positions[c_b]
    vec, _ = find_mic(vec, atoms.cell, atoms.pbc)
    local = top[np.linalg.norm(vec[:, :2], axis=1) < LOCAL_RADIUS]
    out["Cu_local_top"] = int(is_cu[local].sum())
    out["Ni_local_top"] = int(len(local) - is_cu[local].sum())
    out["Cu_frac_local_top"] = out["Cu_local_top"] / len(local) if len(local) else np.nan

    # Cu-Cu nearest-neighbour pairs in the top layer (clustered vs isolated Cu)
    top_cu = top[is_cu[top]]
    pairs = 0
    for k in range(len(top_cu) - 1):
        dd = atoms.get_distances(top_cu[k], top_cu[k + 1:], mic=True)
        pairs += int((dd < CUCU_CUTOFF).sum())
    out["CuCu_pairs_top"] = pairs
    return out


def build(df_in, label):
    rows = []
    for _, r in df_in.iterrows():
        path = file_map[int(r["config_id"])]
        rows.append({
            "config_id": int(r["config_id"]), "group": label,
            "SP": r["SP"], "pred_RX": r["pred_RX"], "pred_std": r["pred_std"],
            "POSCAR": os.path.basename(path), **ni_cu_features(path)
        })
    return pd.DataFrame(rows)


# ---------- choose structures ----------
strong = pool_all[pool_all["group"] == "too_strong"].sort_values("pred_std", ascending=False)
weak   = pool_all[pool_all["group"] == "too_weak"].sort_values("pred_std", ascending=False)
low    = pool_all[pool_all["group"] == "low_uncertainty"]
best   = low.sample(n=min(N_BEST, len(low)), random_state=0).sort_values("pred_std")

t_strong = build(strong, "too_strong")
t_weak   = build(weak, "too_weak")
t_best   = build(best, "low_uncertainty")
allt = pd.concat([t_strong, t_weak, t_best], ignore_index=True)

# ---------- summary table ----------
layer_cols = [c for c in allt.columns if c.startswith("Cu_L")]
summary_cols = layer_cols + ["Cu_bound", "Ni_bound", "Cu_local_top",
                             "Cu_frac_local_top", "CuCu_pairs_top"]
summary = allt.groupby("group")[summary_cols].mean().round(3)
summary.insert(0, "n_structures", allt.groupby("group").size())

# reference row: Cu spread evenly over all layers
n_layers = len(layer_cols)
n_metal = allt[[c for c in allt.columns if c.startswith(("Cu_L", "Ni_L"))]].sum(axis=1).mean()
ref = {c: round(allt["Cu_total"].mean() / n_layers, 3) for c in layer_cols}
ref["Cu_frac_local_top"] = round(allt["Cu_total"].mean() / n_metal, 3)
summary.loc["uniform_mixing_reference"] = pd.Series(ref)
summary = summary.reindex(["too_strong", "low_uncertainty", "too_weak",
                           "uniform_mixing_reference"])

# ---------- percent of structures with k Cu atoms ----------
dist_bound = (pd.crosstab(allt["group"], allt["Cu_bound"], normalize="index") * 100).round(1)
dist_bound.columns = [f"{c} Cu bonded to C" for c in dist_bound.columns]
dist_top = (pd.crosstab(allt["group"], allt["Cu_L1"], normalize="index") * 100).round(1)
dist_top.columns = [f"{c} Cu in top layer" for c in dist_top.columns]

readme = pd.DataFrame({
    "column": ["group", "SP, pred_RX, pred_std", "POSCAR", "Cu_L1 ... Cu_L5",
               "Ni_L1 ... Ni_L5", "Cu_total", "Cu_bound, Ni_bound",
               "Cu_local_top, Ni_local_top", "Cu_frac_local_top",
               "CuCu_pairs_top", "Note"],
    "meaning": [
        "too_strong: SP below the training range. too_weak: SP above it. low_uncertainty: random sample from the dark purple region of the plot.",
        "SP energy of the structure, GP predicted RX energy, GP uncertainty.",
        "Name of the POSCAR file for that structure.",
        "Number of Cu atoms in each metal layer. Layer 1 is the top (surface) layer, layer 5 is the bottom. Each layer has 16 metal atoms.",
        "Number of Ni atoms in each metal layer.",
        "Total Cu atoms in the slab.",
        "Cu and Ni atoms within 2.5 angstrom of the carbon attached to the surface.",
        "Cu and Ni atoms in the top layer within 4.0 angstrom (sideways) of that carbon.",
        "Cu_local_top divided by the number of top-layer atoms counted.",
        "Nearest-neighbour Cu-Cu pairs in the top layer. 0 means every surface Cu is isolated, larger means Cu is clustered.",
        "Geometry comes from the generated POSCARs, which appear to be the starting structures before relaxation."
    ]
})

# ---------- write Excel ----------
with pd.ExcelWriter(OUT_XLSX, engine="openpyxl") as xw:
    readme.to_excel(xw, sheet_name="README", index=False)
    summary.to_excel(xw, sheet_name="Summary")
    dist_bound.to_excel(xw, sheet_name="Cu_bonded_to_C_pct")
    dist_top.to_excel(xw, sheet_name="Cu_in_top_layer_pct")
    t_strong.to_excel(xw, sheet_name="too_strong", index=False)
    t_weak.to_excel(xw, sheet_name="too_weak", index=False)
    t_best.to_excel(xw, sheet_name="low_uncertainty_sample", index=False)
    for ws in xw.book.worksheets:
        ws.freeze_panes = "B2"
        for col in ws.columns:
            width = max(len(str(c.value)) if c.value is not None else 0 for c in col)
            ws.column_dimensions[col[0].column_letter].width = min(max(width + 2, 10), 90)

# ---------- copy the selected POSCARs into folders and zip them ----------
shutil.rmtree(OUT_DIR, ignore_errors=True)
for label, tdf in [("too_strong", t_strong), ("too_weak", t_weak),
                   ("low_uncertainty_sample", t_best)]:
    folder = os.path.join(OUT_DIR, label)
    os.makedirs(folder, exist_ok=True)
    for cid in tdf["config_id"]:
        shutil.copy(file_map[int(cid)], folder)
shutil.make_archive(OUT_DIR, "zip", OUT_DIR)

print(summary.to_string())
print("\nSaved:", OUT_XLSX, "and", OUT_DIR + ".zip")

try:
    from google.colab import files
    files.download(OUT_XLSX)
    files.download(OUT_DIR + ".zip")
except Exception:
    print("Use the file browser on the left to download the two files from /content.")
