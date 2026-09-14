# -*- coding: utf-8 -*-
"""
driver.py — teddy/synspec driver: synthesize spectra with the Python SYNSPEC.

Work in a directory holding same-named .5 and .7 files; give the prefix and path:
  - <name>.5  TLUSTY-format setup file (same as TLUSTY input; its third
            line, the nst filename, is rewritten per nst; original untouched)
  - <name>.7  model atmosphere (TLUSTY output model)
  - .5/.7 prefixes must match (same model); the prefix is just a filename

nst=None -> no non-standard params (.5 line 3 set to ''); nst=dict ->
generate an nst file (KEY=VALUE) and point the .5 at it.

Outputs (conventions of the original RSynspec script):
  <name>.spec  synthetic spectrum (fort.7)  <name>.cont  continuum flux (fort.17)
  <name>.id  line identification (fort.12)  <name>.eqw  equivalent widths (fort.16)
  <name>.log  run log (unit 6)  pyerr.log  Python errors (should be empty)
  The full fort.* set is kept (incl. fort.5 = patched input actually used);
  the data link is not kept (created temporarily, removed after the run).
"""
import os
import shutil
import subprocess
import sys

PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))
SYNSPEC_PY = os.path.join(PACKAGE_DIR, "synspec54.py")
DATA_DIR = os.path.normpath(os.path.join(PACKAGE_DIR, os.pardir,
                                         "tlusty", "data"))


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


def write_fort55(path, imode=0, idstd=0, iprin=1,
                 inmod=1, intrpl=0, ichang=0, ichemc=0,
                 iophli=0, nunalp=0, nunbet=0, nungam=0, nunbal=0,
                 ifreq=0, inlte=1, icontl=1, inlist=0, ifhe2=0,
                 ihydpr=0, ihe1pr=0, ihe2pr=0,
                 alam0=4000., alast=7000., cutof0=10., cutofs=0.,
                 relop=1.e-4, space=2.,
                 nmlist=0, iunitm=20):
    """Generate the SYNSPEC auxiliary input fort.55 (same format as create_fort55_lin in ivan.py).

    imode  0=normal synthetic spectrum / 1=detailed line profile / 2=pure
           continuum (no lines, no line list) / -1=line ID list only / -2=iron-curtain opacity
    inmod  1=input model is a TLUSTY model (fort.8); the default is fine
    inlist line list format: 0=text (official example convention, ibin=mod(inlist,10)=0) /
           1=binary unformatted; text line lists must use 0
    alam0/alast  synthesis wavelength range [Å] (alast<0 means all vacuum wavelengths)
    """
    with open(path, 'w') as f:
        f.write(f"{imode:8d} {idstd:7d} {iprin:7d}                                \n")
        f.write(f"{inmod:8d} {intrpl:7d} {ichang:7d} {ichemc:7d}                        \n")
        f.write(f"{iophli:8d} {nunalp:7d} {nunbet:7d} {nungam:7d} {nunbal:7d}                \n")
        f.write(f"{ifreq:8d} {inlte:7d} {icontl:7d} {inlist:7d} {ifhe2:7d}                \n")
        f.write(f"{ihydpr:8d} {ihe1pr:7d} {ihe2pr:7d}                                \n")
        f.write(f"    {alam0:.0f}    {alast:.0f}       {cutof0:.0f}       {cutofs:.0f}  {relop:g}    {space:g}\n")
        f.write(f"{nmlist:8d}{iunitm:8d}                                        ! nnlist\n")


def _patched_fort5(src5, dst, nst_name):
    """Copy <name>.5 to fort.5, rewriting the third line (nst filename) per the nst setting."""
    with open(src5) as f:
        lines = f.readlines()
    if len(lines) < 3:
        raise ValueError(f"{src5} has too few lines; not a valid TLUSTY-format .5 file")
    if nst_name:
        lines[2] = f" '{nst_name}'                  ! non-standard parameter file ('' = none)\n"
    else:
        lines[2] = " ''                  ! no change of general optional parameters\n"
    with open(dst, 'w') as f:
        f.writelines(lines)


def run_synspec(name, workdir='.', nst=None, linelist=None,
                run=True, verbose=True, **kw):
    """Synthesize a spectrum in workdir from <name>.5 + <name>.7.

    name      filename prefix (e.g. 'FF'; requires FF.5 and FF.7 to both exist in workdir)
    workdir   working directory
    nst       None=no non-standard parameters; dict=write an nst file and enable it
    linelist  line list: 'gfATO'/'gfMOL'/'gfTiO' selects a built-in line list
              (teddy/synspec/data/<name>.dat, copied to fort.19);
              a direct file path may also be given; may be None for imode=2 pure continuum
    **kw      all fort.55 parameters, see write_fort55(imode/alam0/alast/...)
    Returns (ok, workdir)
    """
    workdir = os.path.abspath(workdir)
    src5 = os.path.join(workdir, name + '.5')
    src7 = os.path.join(workdir, name + '.7')
    for src in (src5, src7):
        if not os.path.exists(src):
            raise FileNotFoundError(
                f"missing input file: {src}(.5 and .7 must exist with the same prefix)")

    # built-in line list name -> teddy/synspec/data/<name>.dat
    if linelist and not os.path.sep in linelist and not os.path.exists(linelist):
        builtin = os.path.join(PACKAGE_DIR, 'data', linelist + '.dat')
        if not os.path.exists(builtin):
            raise FileNotFoundError(
                f"unknown built-in line list: {linelist}(choose gfATO/gfMOL/gfTiO, or give a file path)")
        linelist = builtin

    if nst:
        write_nst(os.path.join(workdir, 'nst'), nst)
    _patched_fort5(src5, os.path.join(workdir, 'fort.5'),
                   'nst' if nst else None)
    write_fort55(os.path.join(workdir, 'fort.55'), **kw)
    shutil.copy(src7, os.path.join(workdir, 'fort.8'))
    if linelist:
        shutil.copy(linelist, os.path.join(workdir, 'fort.19'))

    if verbose:
        print(f"[teddy/synspec] model {name}  workdir {workdir}")
        print(f"[teddy/synspec]   input: {name}.5 + {name}.7"
              f"  nst: {'yes ' + str(nst) if nst else 'none'}"
              f"  line list: {linelist if linelist else 'none'}")
        print(f"[teddy/synspec]   fort.55: imode={kw.get('imode', 0)} "
              f"range {kw.get('alam0', 4000.):.0f}-{kw.get('alast', 7000.):.0f} Å")

    if not run:
        return True, workdir

    # data link: created before the run, removed afterwards
    link = os.path.join(workdir, 'data')
    made_link = False
    if not os.path.exists(link):
        os.symlink(DATA_DIR, link)
        made_link = True

    log = os.path.join(workdir, name + '.log')
    errlog = os.path.join(workdir, 'pyerr.log')
    try:
        with open(os.path.join(workdir, 'fort.5')) as fin, \
                open(log, 'w') as fout, open(errlog, 'w') as ferr:
            proc = subprocess.run(
                [sys.executable, '-u', SYNSPEC_PY],
                stdin=fin, stdout=fout, stderr=ferr,
                cwd=workdir)
        ok = proc.returncode == 0
        for unit, ext in ((7, 'spec'), (17, 'cont'), (12, 'id'), (16, 'eqw')):
            src = os.path.join(workdir, f'fort.{unit}')
            if os.path.exists(src):
                shutil.copy(src, os.path.join(workdir, f'{name}.{ext}'))
    finally:
        if made_link and os.path.islink(link):
            os.unlink(link)

    if verbose:
        if ok:
            print(f"[teddy/synspec] {name} synthesis done, output in {workdir}")
            print(f"[teddy/synspec]   {name}.spec synthetic spectrum   {name}.cont continuum")
            print(f"[teddy/synspec]   {name}.id line identification list   {name}.log run log")
        else:
            print(f"[teddy/synspec] {name} synthesis failed, see {log} and {errlog}")
    return ok, workdir
