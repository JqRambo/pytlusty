# -*- coding: utf-8 -*-
"""
driver.py — driver logic of the teddy package: generate TLUSTY input and run the Python version of TLUSTY

The user gives the configuration in basic.py (elements/abundances/mode/modpf/
TEFF/LOGG/NFREAD/NST/output paths, etc.); this module is responsible for:
  1. Automatically generating the .5 standard input file (including the full ion table for explicit ions)
  2. Optionally generating the nst non-standard parameter file
  3. Running the Python version of TLUSTY in the output directory
  4. Temporarily creating the data symlink during the run, removed afterwards
     (no data symlink is kept in the output directory; all other fort.* and MOD.* files are kept)
"""
import os
import shutil
import subprocess
import sys

import atoms

PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))
TLUSTY_PY = os.path.join(PACKAGE_DIR, "tlusty208.py")
DATA_DIR = os.path.join(PACKAGE_DIR, "data")

# Three calculation modes (consistent with ivan.py / the TLUSTY documentation):
#   'TT'  LTE       : LTE=T, LTGRAY=T, all lines in detailed radiative equilibrium (ilvlin=100)
#   'TF'  NLTE/C    : NLTE for continua only, lines in detailed radiative equilibrium (ilvlin=100)
#   'FF'  NLTE/L    : full NLTE, explicit lines (ilvlin=0)
MODEL_TYPES = {
    'TT': {'lte': True,  'ltgray': True,  'ilvlin': 100},
    'TF': {'lte': False, 'ltgray': False, 'ilvlin': 100},
    'FF': {'lte': False, 'ltgray': False, 'ilvlin': 0},
    # Aliases
    'LTE':    {'lte': True,  'ltgray': True,  'ilvlin': 100},
    'NLTEC':  {'lte': False, 'ltgray': False, 'ilvlin': 100},
    'NLTEL':  {'lte': False, 'ltgray': False, 'ilvlin': 0},
}


# ---------------------------------------------------------------------------
# .5 input file generation
# ---------------------------------------------------------------------------

def _fmt_abn(abn):
    """Format an abundance in Fortran floating-point notation, 8 decimals zero-padded, e.g. 1.00000000e-01
    (consistent with format_abundance in create.py; all values have a fixed
    length of 14 characters, keeping the second column of the .5 file aligned)."""
    if isinstance(abn, str):
        return abn                      # allow passing a string directly (special notation)
    if abn == 0:
        return "0.00000000e+00"
    return f"{abn:.8e}"


def atoms_section(elements, model_type='FF'):
    """Generate the NATOMS record and the ion records from the user element settings.

    elements: {symbol: {'mode': m, 'abn': a, 'modpf': p}}, elements H..Es (Z<=99) supported
    model_type: 'TT'/'TF'/'FF' (or the aliases 'LTE'/'NLTEC'/'NLTEL')

    The ion table depends on the mode (consistent with ivan.py):
      FF (NLTE/L): all explicit ions ilvlin=0, full level sets
      TT/TF:       the first ion of each element with a data file keeps its full levels,
                   subsequent ordinary ions are compressed to one level (ilast=1, data file kept),
                   ODF ions (e.g. Fe) stay complete; ions with a file get ilvlin=100,
                   one-level bare-nucleus ions get ilvlin=0
    Returns (natoms, atom_lines, ion_lines)
    """
    mt = MODEL_TYPES[model_type]
    for sym in elements:
        if sym not in atoms.Z_OF:
            raise ValueError(f"unknown element symbol: {sym!r} (H through Es supported)")
    natoms = max(atoms.Z_OF[sym] for sym in elements)

    atom_lines = []
    for z in range(1, natoms + 1):
        sym = atoms.SYMBOLS[z - 1]
        cfg = elements.get(sym)
        if cfg is None:
            atom_lines.append((0, 0.0, 0))
        else:
            atom_lines.append((int(cfg.get('mode', 0)),
                               cfg.get('abn', 0.0),
                               int(cfg.get('modpf', 0))))

    ion_lines = []
    for sym, cfg in sorted(elements.items(),
                           key=lambda kv: atoms.Z_OF[kv[0]]):
        if int(cfg.get('mode', 0)) != 2:
            continue
        if sym not in atoms.EXPLICIT_IONS:
            raise ValueError(
                f"element {sym} has no ready-made explicit atom data configuration, "
                f"use mode=1 (implicit) instead, or add it to EXPLICIT_IONS in atoms.py")
        z = atoms.Z_OF[sym]
        ions = cfg.get('ions') or atoms.EXPLICIT_IONS[sym]
        first_file_ion_done = False
        for iz, nlevs, filei, odf in ions:
            ilast = 1 if filei is None else 0
            ilvlin = 0
            nonstd = -1 if odf else 0
            if model_type in ('TT', 'TF', 'LTE', 'NLTEC'):
                if filei is not None:
                    ilvlin = mt['ilvlin']
                    if first_file_ion_done and odf is None:
                        # subsequent ordinary ions compressed to one level (consistent with TT/TF in ivan.py)
                        nlevs = 1
                        ilast = 1
                    first_file_ion_done = True
            typion = f"{sym:>2s} {iz + 1}"
            ion_lines.append((z, iz, nlevs, ilast, ilvlin, nonstd,
                              typion, filei or ' ', odf))
    return natoms, atom_lines, ion_lines


def write_model5(path, teff, logg, model_type, nst_name, nfread, elements):
    """Write the TLUSTY standard input file MODEL.5.

    model_type: 'TT'/'TF'/'FF' (or the aliases 'LTE'/'NLTEC'/'NLTEL')
    """
    mt = MODEL_TYPES[model_type]
    natoms, atom_lines, ion_lines = atoms_section(elements, model_type)

    with open(path, 'w') as f:
        f.write(f" {teff:.0f}  {logg}      ! TEFF, GRAV\n")
        f.write(f" {'T' if mt['lte'] else 'F'}  "
                f"{'T' if mt['ltgray'] else 'F'}"
                f"                ! LTE,  LTGRAY\n")
        f.write(f" '{nst_name or ''}'                  ! non-standard "
                f"parameter file ('' = none)\n")
        f.write("*" + "-" * 64 + "\n")
        f.write("* frequencies\n*\n")
        f.write(f" {nfread:3d}                  ! NFREAD\n")
        f.write("*" + "-" * 64 + "\n")
        f.write("* data for atoms\n*\n")
        f.write(f" {natoms:2d}                   ! NATOMS\n")
        f.write("* mode abn modpf\n")
        for mode, abn, modpf in atom_lines:
            f.write(f"   {mode:2d}  {_fmt_abn(abn):>14s}      {modpf:2d}\n")
        f.write("*" + "-" * 64 + "\n")
        f.write("* data for ions\n*\n")
        f.write("*iat   iz   nlevs  ilast ilvlin  nonstd typion  filei\n*\n")
        for z, iz, nlevs, ilast, ilvlin, nonstd, typion, filei, odf \
                in ion_lines:
            f.write(f" {z:3d} {iz:4d} {nlevs:5d} {ilast:6d} {ilvlin:6d}"
                    f" {nonstd:6d}    '{typion}' '{filei}'\n")
            if odf:
                gam, lin, rap = odf
                f.write(f"   0    0                                      "
                        f"'{gam}'\n")
                f.write(f"                                               "
                        f"'{lin}'\n")
                f.write(f"                                               "
                        f"'{rap}'\n")
        f.write("   0    0     0     -1      0      0    '    ' ' '\n")
        f.write("*\n* end\n")
    return natoms


def write_nst(path, nst):
    """Write the nst non-standard parameter file (KEY=VALUE, comma-separated, wrapped at 70 columns)."""
    def fmt(v):
        if isinstance(v, bool):
            return 'T' if v else 'F'
        return str(v)
    line = ""
    with open(path, 'w') as f:
        for key, value in nst.items():
            item = f"{key}={fmt(value)},"
            if len(line) + len(item) > 70:
                f.write(line.rstrip().rstrip(',') + "\n")
                line = item
            else:
                line += item
        if line:
            f.write(line.rstrip(','))


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------

def run_model(teff, logg, elements, nfread=2000,
              model_type='FF', nst=None,
              model='FF', output_dir='.', start_model=None,
              run=True, verbose=True, npar=None):
    """Generate the input and (optionally) run the Python version of TLUSTY.

    model_type  'TT'(LTE) / 'TF'(NLTE/C) / 'FF'(NLTE/L)
    npar        number of parallel processes for the frequency loop; None=serial
                (bit-identical to the original), os.cpu_count() recommended. Parallelism only
                changes the floating-point summation order; differences vs. serial are at the 1e-16 level.
    Output directory contents: MODEL.5, MODEL.6 (log), nst (if set), the full fort.* set,
                  MODEL.7/.9/.69/.14; no data symlink is kept.
    Returns (ok, output_dir)
    """
    if model_type not in MODEL_TYPES:
        raise ValueError(f"model_type must be one of {sorted(MODEL_TYPES)}")
    if not model:
        model = model_type           # file name defaults to the mode: TT/TF/FF
    output_dir = os.path.abspath(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    nst_name = None
    if nst:
        nst_name = 'nst'
        write_nst(os.path.join(output_dir, 'nst'), nst)

    mod5 = os.path.join(output_dir, model + '.5')
    natoms = write_model5(mod5, teff, logg, model_type, nst_name,
                          nfread, elements)
    if verbose:
        nexp = sum(1 for c in elements.values()
                   if int(c.get('mode', 0)) == 2)
        print(f"[teddy] generated {mod5}")
        print(f"[teddy] {model_type} mode  TEFF={teff:.0f} logg={logg}  "
              f"NATOMS={natoms}  explicit elements={nexp}  NFREAD={nfread}")
        if nst:
            print(f"[teddy] nst parameters: {nst}")

    # Starting model -> fort.8
    if start_model:
        # Try in order: direct path / path+.7 / under OUTPUT_DIR / under OUTPUT_DIR+.7
        cands = [start_model, start_model + '.7',
                 os.path.join(output_dir, start_model),
                 os.path.join(output_dir, start_model + '.7')]
        src = next((c for c in cands if os.path.exists(c)), None)
        if src is None:
            raise FileNotFoundError(
                f"starting model not found: tried {cands}")
        shutil.copy(src, os.path.join(output_dir, 'fort.8'))
        if verbose:
            print(f"[teddy] starting model: {src} -> fort.8")

    if not run:
        return True, output_dir

    # data symlink: created before the run, removed afterwards
    link = os.path.join(output_dir, 'data')
    made_link = False
    if not os.path.exists(link):
        os.symlink(DATA_DIR, link)
        made_link = True

    log6 = os.path.join(output_dir, model + '.6')
    errlog = os.path.join(output_dir, 'pyerr.log')
    env = None
    if npar is not None:
        env = dict(os.environ, TLUSTY_NPAR=str(int(npar)))
        if verbose:
            print(f"[teddy] parallel processes for frequency loop TLUSTY_NPAR={int(npar)}"
                  " (only the floating-point summation order differs, differences at the 1e-16 level)")
    try:
        with open(mod5) as fin, open(log6, 'w') as fout, \
                open(errlog, 'w') as ferr:
            proc = subprocess.run(
                [sys.executable, '-u', TLUSTY_PY],
                stdin=fin, stdout=fout, stderr=ferr,
                cwd=output_dir, env=env)
        ok = proc.returncode == 0
        for unit in (7, 9, 69, 14):
            src = os.path.join(output_dir, f'fort.{unit}')
            if os.path.exists(src):
                shutil.copy(src, os.path.join(output_dir,
                                              f'{model}.{unit}'))
    finally:
        if made_link and os.path.islink(link):
            os.unlink(link)

    if verbose:
        if ok:
            print(f"[teddy] model {model} finished, output in {output_dir}")
            print(f"[teddy]   {model}.7  model atmosphere   {model}.9  convergence history")
            print(f"[teddy]   {model}.6  run log            {model}.14 model summary")
        else:
            print(f"[teddy] model {model} failed, see {log6} and {errlog}")
    return ok, output_dir


def run_chain(teff, logg, elements, nfread=2000, nst=None,
              output_dir='.', verbose=True, npar=None):
    """Full TT -> TF -> FF three-step chained calculation (consistent with the ivan.py workflow):

      TT (LTE)     computed from scratch -> TT.7
      TF (NLTE/C)  starting from TT.7 -> TF.7
      FF (NLTE/L)  starting from TF.7 -> FF.7  (final model)

    nfread can be:
      - an integer: the same NFREAD shared by all three steps
      - {'TT': n1, 'TF': n2, 'FF': n3}: per-step number of frequency points
    nst can be:
      - a plain dict: the same set of nst parameters shared by all three steps
      - {'TT': {...}, 'TF': {...}, 'FF': {...}}: per-step nst parameters
        (a step missing from the dict runs without nst)
    npar is the number of parallel processes for the frequency loop (None=serial), shared by the three steps and passed through to run_model.
    Returns (ok, output_dir); ok means all three steps succeeded.
    """
    def per_stage(x):
        if isinstance(x, dict) and all(k in ('TT', 'TF', 'FF') for k in x):
            return lambda stage: x.get(stage)
        return lambda stage: x

    nfr = per_stage(nfread)
    nstf = per_stage(nst)

    ok, _ = run_model(teff, logg, elements, nfread=nfr('TT'),
                      model_type='TT', nst=nstf('TT'), model='TT',
                      output_dir=output_dir, verbose=verbose, npar=npar)
    if not ok:
        return False, output_dir
    ok, _ = run_model(teff, logg, elements, nfread=nfr('TF'),
                      model_type='TF', nst=nstf('TF'), model='TF',
                      output_dir=output_dir, start_model='TT',
                      verbose=verbose, npar=npar)
    if not ok:
        return False, output_dir
    ok, outdir = run_model(teff, logg, elements, nfread=nfr('FF'),
                           model_type='FF', nst=nstf('FF'), model='FF',
                           output_dir=output_dir, start_model='TF',
                           verbose=verbose, npar=npar)
    return ok, outdir
