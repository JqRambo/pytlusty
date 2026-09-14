# -*- coding: utf-8 -*-
"""
ff.py — teddy: directly compute an FF (NLTE/L) model
=====================================================

After setting the parameters below, run:   python3 ff.py

FF is a full non-LTE model and must start from a starting model (TLUSTY
requirement): START_MODEL gives the starting model name (no suffix); for
file old.7 write START_MODEL = 'old'; old.7 is the initial model (found
first in the current directory, then in OUTPUT_DIR).

Ion level tables are configured automatically from the ELEMENTS settings
(nlevs/ilast/ilvlin etc., per TLUSTY standard cases); no manual input.

Output goes to OUTPUT_DIR: FF.5, FF.6 (log), FF.7 (model), FF.9
(convergence history), FF.14, FF.69, nst, all fort.* files; no data links.

Parallelism: NPAR = worker count for the frequency loop (the hot spot);
NPAR=None is serial, bit-identical to original TLUSTY; parallel only
reorders float sums (~1e-16); recommend NPAR = os.cpu_count().
"""

from driver import run_model

# ------------------------- Basic parameters -------------------------
TEFF = 22000.0          # effective temperature [K]
LOGG = 4.0              # surface gravity log g [cgs]
NFREAD = 2000           # number of frequency points

# ------------------------- Elements and abundances -------------------------
# mode: 2=explicit NLTE (level tables auto-detected) / 1=implicit LTE / 0=not considered
# abn : abundance (number-density ratio relative to hydrogen, e.g. 1.000000e-01); 0 = TLUSTY built-in solar abundance
ELEMENTS = {
    'H':  {'mode': 2, 'abn': 0.000000e+00, 'modpf': 0},
    'He': {'mode': 2, 'abn': 1.000000e-01, 'modpf': 0},
    'C':  {'mode': 1, 'abn': 0.000000e+00, 'modpf': 0},
    'N':  {'mode': 1, 'abn': 0.000000e+00, 'modpf': 0},
    'O':  {'mode': 1, 'abn': 0.000000e+00, 'modpf': 0},
}

# ------------------------- nst non-standard parameters -------------------------
# the number of depth points ND is also set here; write NST = None if nst is not needed
NST = {'ND': 50, 'NLAMBD': 6, 'ITEK': 40, 'IACC': 40, 'NITER': 31}

# ------------------------- Starting model and output -------------------------
START_MODEL = 'old'             # starting model name (without the .7 suffix)
OUTPUT_DIR = './output/FF'

# ------------------------- Parallel settings -------------------------
NPAR = None  # number of parallel processes; None=serial (bit-identical to the original), recommend os.cpu_count()

# ------------------------- Execute -------------------------
if __name__ == '__main__':
    ok, outdir = run_model(
        teff=TEFF, logg=LOGG, elements=ELEMENTS,
        nfread=NFREAD, model_type='FF', nst=NST,
        model='FF', output_dir=OUTPUT_DIR, start_model=START_MODEL,
        run=True, npar=NPAR)
    raise SystemExit(0 if ok else 1)
