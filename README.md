# PyTLUSTY / PySYNSPEC

A faithful Python translation of the Fortran stellar-atmosphere codes
**TLUSTY208** and **SYNSPEC54** (Hubeny & Lanz), with a multiprocessing
parallel driver on top. The physics, numerical methods, and arithmetic of
the original codes are preserved line by line; no Fortran compiler, shell
driver scripts, or hand-written input files are needed any more.

- `tlusty/chain.py` — full chained calculation TT → TF → FF
- `tlusty/ff.py` — direct FF (NLTE/L) model calculation from a start model
- `tlusty2/` — same code as `tlusty/`, plus multiprocess parallelism over
  the frequency loop
- `synspec/syn.py` — synthetic spectra from an existing model (`<name>.5` +
  `<name>.7`)

## Layout

```
tlusty/          TLUSTY model atmospheres (serial version)
  chain.py       chained calculation setup and entry point (TT -> TF -> FF)
  ff.py          single FF model setup and entry point
  driver.py      driver: builds the .5 input, ion level tables, nst, runs
  atoms.py       element table (H..Es), TLUSTY solar abundances,
                 standard explicit-ion setups
  tlusty208.py   Python TLUSTY main program (translated from tlusty208.f)
  commons.py     TLUSTY COMMON-block state
  params.py      TLUSTY PARAMETER constants
  fortran.py     Fortran runtime-semantics helpers
  data/          full atomic data (incl. Fe ODF data gf*.gam/.lin)
tlusty2/         parallel TLUSTY (adds on top of tlusty/)
  parmap.py      multiprocess framework for the frequency loops
  _writeset.py   empirical verifier of parallel write sets (TLUSTY_WSET=1)
synspec/         SYNSPEC spectral synthesis
  syn.py         synthesis setup and entry point
  driver.py      driver: builds fort.55/fort.5, optional nst, runs
  synspec54.py   Python SYNSPEC main program (translated from synspec54.f,
                 assembled from fragments/chunkNN.py by assemble.sh)
  data/          place line lists here (gfATO.dat / gfMOL.dat / gfTiO.dat)
test/            benchmark runs and three-way comparisons (test/README.md)
```

Requirements: Python 3 + NumPy. Usage:

```python
import sys
sys.path.insert(0, '.../tlusty')    # or '.../tlusty2', '.../synspec'
import driver
```

or run `chain.py` / `ff.py` / `syn.py` directly in the respective directory.

## Quick start

See the in-code configuration blocks:

- `tlusty/chain.py` — set `TEFF`, `LOGG`, `ELEMENTS` (element/mode/abundance),
  per-stage `NFREAD` and `NST` (incl. `ND`), and `OUTPUT_DIR`; then
  `python3 chain.py` runs TT (LTE) → TF (NLTE/C, from TT.7) → FF (NLTE/L,
  from TF.7). The final model is `FF.7`.
- `tlusty/ff.py` — same settings plus `START_MODEL` (prefix without suffix,
  e.g. `'old'` for `old.7`).
- `synspec/syn.py` — set `NAME`, `WORK_DIR` (holding `NAME.5` + `NAME.7`),
  `IMODE` (0 = full spectrum, 1 = line profiles, 2 = continuum),
  `ALAM0`/`ALAST` [Å], and `LINELIST` (`'gfATO'`/`'gfMOL'`/`'gfTiO'` from
  `synspec/data/`, or any file path; `None` for IMODE=2).

Line lists are not shipped with the repository; place `gfATO.dat`,
`gfMOL.dat`, or `gfTiO.dat` into `synspec/data/` before synthesis.

## Parallel version (tlusty2)

`tlusty2` is identical to `tlusty` except that the two hottest per-frequency
loops of the formal solution (radiative rates and the ALI operator, ~90% of
the runtime) are evaluated with multiprocessing:

- set `NPAR` (or the environment variable `TLUSTY_NPAR`) to the number of
  processes in `ff.py`/`chain.py`; `NPAR = None` falls back to the serial
  path, bitwise identical to `tlusty/`
- parallelism only changes floating-point summation order; differences are
  at the 1e-16 level, physics and arithmetic unchanged
- benchmark (H–He model, Teff = 22500 K, log g = 4.0): serial ≈ 6.2 h →
  48 processes ≈ 1.9 h on a shared machine

## Verification

The main programs are line-by-line translations: `tlusty208.py` from
`tlusty208.f`, `synspec54.py` from `synspec54.f`, keeping Fortran 1-based
indexing and all numerical algorithms. Verified against the Fortran
reference (runs in `test/`):

- TLUSTY: H–He solar-abundance models (Teff = 22000 and 22500 K, log g =
  4.0); median relative differences vs. Fortran ≈ 1e-3 in temperature,
  electron density, and density (within each run's convergence accuracy)
- SYNSPEC: 3000–9000 Å synthesis of the same model; identical wavelength
  grids (20200 points), median relative flux difference 1.3e-7, maximum
  7.4e-4 in deep line cores

Note: the Python translation is about two orders of magnitude slower than
the Fortran original; use `tlusty2/` (parallel) for production models.

## Reference

If you use this code, please cite the accompanying paper (Jia & Li, in
preparation) and the original TLUSTY/SYNSPEC papers:

- Hubeny I., 1988, Comput. Phys. Commun., 52, 103
- Hubeny I., Lanz T., 1995, ApJ, 439, 875
- Hubeny I., Lanz T., 2017, arXiv:1706.01859
