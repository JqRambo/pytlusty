# -*- coding: utf-8 -*-
"""
chain.py — teddy: full chained calculation TT -> TF -> FF
=============================================

Set the parameters below, then run:   python3 chain.py

Automatically performs three steps (mode and level settings are fixed, no setup needed):
  TT (LTE gray atmosphere, computed from scratch)      -> TT.7
  TF (NLTE/C, starting from TT.7 as initial model)     -> TF.7
  FF (NLTE/L, starting from TF.7 as initial model)     -> FF.7   final model

The ion level table of each element (nlevs/ilast/ilvlin etc.) is auto-configured
per the TLUSTY official standard test case and per mode; not needed as input.

All inputs and outputs reside in OUTPUT_DIR, files named per mode as
TT.5/TT.7, TF.5/TF.7, FF.5/FF.7 etc.; no data links kept.
"""

from driver import run_chain

# ------------------------- basic parameters (set once) -------------------------
TEFF = 22000.0          # effective temperature [K]
LOGG = 4.0              # surface gravity log g [cgs]

# ------------------------- elements and abundances (set once) -------------------------
# mode: 2=explicit NLTE (level table auto-configured) / 1=implicit LTE / 0=not considered
# abn : abundance (number-density ratio relative to hydrogen, e.g. 1.000000e-01); 0 = TLUSTY built-in solar abundance
ELEMENTS = {
    'H':  {'mode': 2, 'abn': 0.000000e+00, 'modpf': 0},
    'He': {'mode': 2, 'abn': 1.000000e-01, 'modpf': 0},
    'C':  {'mode': 1, 'abn': 0.000000e+00, 'modpf': 0},
    'N':  {'mode': 1, 'abn': 0.000000e+00, 'modpf': 0},
    'O':  {'mode': 1, 'abn': 0.000000e+00, 'modpf': 0},
}

# ------------------------- frequency points for each of the three steps -------------------------
NFREAD = {'TT': 50, 'TF': 50, 'FF': 2000}

# ------------------------- nst settings for each of the three steps -------------------------
# each step sets its own nst parameters (the number of optical-depth layers ND is also set here);
# write None or delete the key for a step that needs no nst
NST = {
    'TT': {'ND': 50},
    'TF': {'ND': 50},
    'FF': {'ND': 50, 'NLAMBD': 6, 'ITEK': 40, 'IACC': 40, 'NITER': 31},
}

# ------------------------- output path -------------------------
OUTPUT_DIR = './output/chain'

# ------------------------- parallelization -------------------------
NPAR = None  # number of parallel processes; None=serial (bit-identical to the original), recommend os.cpu_count()

# ------------------------- run -------------------------
if __name__ == '__main__':
    ok, outdir = run_chain(
        teff=TEFF, logg=LOGG, elements=ELEMENTS,
        nfread=NFREAD, nst=NST, output_dir=OUTPUT_DIR, npar=NPAR)
    if ok:
        print(f"[teddy] chained calculation complete, final model: {outdir}/FF.7")
    raise SystemExit(0 if ok else 1)
