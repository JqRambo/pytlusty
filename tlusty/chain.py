# -*- coding: utf-8 -*-
"""
chain.py — teddy: TT -> TF -> FF full chained calculation
=============================================

After setting the parameters below, run:   python3 chain.py

Automatically performs three steps (mode and level settings are fixed, no setup needed):
  TT (LTE gray atmosphere, from scratch)        -> TT.7
  TF (NLTE/C, starting from TT.7)               -> TF.7
  FF (NLTE/L, starting from TF.7)               -> FF.7   final model

The ion level table for each element (nlevs/ilast/ilvlin etc.) follows the
official TLUSTY standard example, is auto-configured and adjusted per mode, no input needed.

All input/output lives in OUTPUT_DIR; files are named per mode as TT.5/TT.7,
TF.5/TF.7, FF.5/FF.7 etc.; the output directory keeps no data symlinks.
"""

from driver import run_chain

# ------------------------- Basic parameters (set once) -------------------------
TEFF = 22000.0          # effective temperature [K]
LOGG = 4.0              # surface gravity log g [cgs]

# ------------------------- Elements and abundances (set once) -------------------------
# mode: 2=explicit NLTE (level table auto-configured) / 1=implicit LTE / 0=not considered
# abn : abundance (number-density ratio relative to H, e.g. 1.000000e-01); 0 = TLUSTY built-in solar abundance
ELEMENTS = {
    'H':  {'mode': 2, 'abn': 0.000000e+00, 'modpf': 0},
    'He': {'mode': 2, 'abn': 1.000000e-01, 'modpf': 0},
    'C':  {'mode': 1, 'abn': 0.000000e+00, 'modpf': 0},
    'N':  {'mode': 1, 'abn': 0.000000e+00, 'modpf': 0},
    'O':  {'mode': 1, 'abn': 0.000000e+00, 'modpf': 0},
}

# ------------------------- Number of frequency points per stage -------------------------
NFREAD = {'TT': 50, 'TF': 50, 'FF': 2000}

# ------------------------- nst settings per stage -------------------------
# Each step sets its own nst parameters (number of depth points ND is also set here);
# if a step needs no nst, write None or delete that key
NST = {
    'TT': {'ND': 50},
    'TF': {'ND': 50},
    'FF': {'ND': 50, 'NLAMBD': 6, 'ITEK': 40, 'IACC': 40, 'NITER': 31},
}

# ------------------------- Output path -------------------------
OUTPUT_DIR = './output/chain'

# ------------------------- Run -------------------------
if __name__ == '__main__':
    ok, outdir = run_chain(
        teff=TEFF, logg=LOGG, elements=ELEMENTS,
        nfread=NFREAD, nst=NST, output_dir=OUTPUT_DIR)
    if ok:
        print(f"[teddy] chained calculation finished, final model: {outdir}/FF.7")
    raise SystemExit(0 if ok else 1)
