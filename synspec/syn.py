# -*- coding: utf-8 -*-
"""
syn.py — teddy/synspec: spectrum synthesis setup and entry point
================================================================

Set the parameters below, then run:   python3 syn.py

Prerequisite: WORK_DIR already contains the setup file and model atmosphere
(NAME.5 and NAME.7, computed by teddy/tlusty or Fortran TLUSTY).
The prefix is purely a file name, independent of the model kind (TT/TF/FF);
the two files must share it, representing the same model.

Output in WORK_DIR: NAME.spec (synthetic spectrum), NAME.cont (continuum),
NAME.id (line identification table), NAME.eqw (equivalent widths),
NAME.log (log) and all fort.* files; the data link is not kept.
"""

from driver import run_synspec

# ------------------------- model and working path -------------------------
NAME = 'FF'                     # file-name prefix: synthesize with FF.5 + FF.7
WORK_DIR = '/home/ubuntu/transform/teddy/test/synspec_python'

# ------------------------- wavelength range and mode -------------------------
IMODE = 0               # 0=normal synthesis / 1=line profiles / 2=continuum only (no line list needed)
IDSTD = 0               # standard depth index (fort.55 first row, second column): at this
                        # deep layer print ionization fractions and take the standard Doppler
                        # width; 0=auto 2*ND/3, or give depth index directly (ND=50 model: 50=deepest)
IPRIN = 1               # output verbosity; >=1 required for the line ID table (NAME.id)
ALAM0 = 3000.0          # starting wavelength [Å]
ALAST = 9000.0          # ending wavelength [Å] (negative = all vacuum wavelengths)
CUTOF0 = 10.0           # line cutoff parameter [Å], recommended 5-10
RELOP = 1.0e-4          # lower limit of line-center/continuum opacity ratio
SPACE = 0.5             # maximum spacing between adjacent frequency points [Å]

# ------------------------- other switches -------------------------
IFREQ = 1               # 0=SPACE in Å; >0=as frequency spacing (1 in the standard test case)
INLTE = 1               # 0=treat all lines in LTE; 1=allow NLTE lines
ICONTL = 0              # line-opacity handling at continuum frequency points (0 in the standard test case)

# ------------------------- line list -------------------------
# 'gfATO'/'gfMOL'/'gfTiO' select a built-in line list, or give a file path;
# use None for IMODE=2 (continuum only)
LINELIST = 'gfATO'
# LINELIST = '/home/ubuntu/transform/tlusty/linelist/lines.dat'

# ------------------------- nst non-standard parameters -------------------------
# None if not needed; otherwise give KEY=VALUE pairs (e.g. VTB=2. for turbulent velocity [km/s])
NST = None
# NST = {'VTB': 2.}

# ------------------------- run -------------------------
if __name__ == '__main__':
    ok, outdir = run_synspec(
        NAME, workdir=WORK_DIR, nst=NST, linelist=LINELIST,
        imode=IMODE, idstd=IDSTD, iprin=IPRIN,
        ifreq=IFREQ, inlte=INLTE, icontl=ICONTL,
        alam0=ALAM0, alast=ALAST,
        cutof0=CUTOF0, relop=RELOP, space=SPACE,
        run=True)
    raise SystemExit(0 if ok else 1)
