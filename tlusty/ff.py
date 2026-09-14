# -*- coding: utf-8 -*-
"""
ff.py — teddy: direct computation of an FF (NLTE/L) model
=========================================================

Set the parameters below, then run:   python3 ff.py

FF is a full non-LTE model and must start from a starting model (a
TLUSTY requirement): give the starting model name (without suffix) in
START_MODEL, e.g. START_MODEL = 'old' uses old.7 as the initial model
(searched first in the current directory, then in OUTPUT_DIR).

The ion level tables are configured automatically from the ELEMENTS
settings (nlevs/ilast/ilvlin etc., per official TLUSTY examples).

Output goes to OUTPUT_DIR: FF.5, FF.6 (log), FF.7 (model), FF.9
(convergence history), FF.14, FF.69, nst and all fort.* files; no data links.
"""

from driver import run_model

# ------------------------- Basic parameters -------------------------
TEFF = 22000.0          # effective temperature [K]
LOGG = 4.0              # surface gravity log g [cgs]
NFREAD = 2000           # number of frequency points

# ------------------------- Elements and abundances -------------------------
# mode: 2=explicit NLTE (level table auto-detected) / 1=implicit LTE / 0=not considered
# abn : abundance (number density relative to hydrogen, e.g. 1.000000e-01); 0 = TLUSTY built-in solar abundance
ELEMENTS = {
    'H':  {'mode': 2, 'abn': 0.000000e+00, 'modpf': 0},
    'He': {'mode': 2, 'abn': 1.000000e-01, 'modpf': 0},
    'C':  {'mode': 1, 'abn': 0.000000e+00, 'modpf': 0},
    'N':  {'mode': 1, 'abn': 0.000000e+00, 'modpf': 0},
    'O':  {'mode': 1, 'abn': 0.000000e+00, 'modpf': 0},
}

# ------------------------- nst non-standard parameters -------------------------
# The number of optical depth points ND is also set here; write NST = None if nst is not needed
NST = {'ND': 50, 'NLAMBD': 6, 'ITEK': 40, 'IACC': 40, 'NITER': 31}

# ------------------------- Starting model and output -------------------------
START_MODEL = 'old'             # starting model name (without the .7 suffix)
OUTPUT_DIR = './output/FF'

# ------------------------- Run -------------------------
if __name__ == '__main__':
    ok, outdir = run_model(
        teff=TEFF, logg=LOGG, elements=ELEMENTS,
        nfread=NFREAD, model_type='FF', nst=NST,
        model='FF', output_dir=OUTPUT_DIR, start_model=START_MODEL,
        run=True)
    raise SystemExit(0 if ok else 1)
