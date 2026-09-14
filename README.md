# PyTLUSTY / PySYNSPEC

A faithful, line-by-line Python translation of the Fortran NLTE
stellar-atmosphere codes **TLUSTY 208** and **SYNSPEC 54** (Hubeny & Lanz).
Before translation, the physics improvements of the community
[tlusty205 fork](https://github.com/mattidorsch/tlusty205_fork) (M. Dorsch)
were ported into TLUSTY 208 — in short: occupation probabilities exact for
non-hydrogenic ions, restored pseudo-continuum opacity below metal
bound-free edges, improved iron-group photoionization fits, and NaN-aware
convergence diagnostics. The physics, numerical methods, and arithmetic of
the (improved) original codes are preserved line by line; no Fortran
compiler, shell driver scripts, or hand-typed input files are needed any
more. The repository ships three implementations of the improved TLUSTY
208: the Fortran twin, the serial Python version, and the multiprocess
Python version.

- `tlusty/chain.py` — full chained calculation TT → TF → FF
- `tlusty/ff.py` — direct FF (NLTE/L) model calculation from a start model
- `tlusty2/` — same code as `tlusty/`, plus multiprocess parallelism over
  the frequency loop
- `synspec/syn.py` — synthetic spectra from an existing model (`<name>.5` +
  `<name>.7`)
- `fortran/` — the improved Fortran twin `tlusty208_fixed.f` (reference
  implementation)

## Layout

```
tlusty/          TLUSTY model atmospheres (serial Python version)
  chain.py       chained calculation setup and entry point (TT -> TF -> FF)
  ff.py          single FF model setup and entry point
  driver.py      driver: builds the .5 input, ion level tables, nst, runs
  atoms.py       element table (H..Es), TLUSTY solar abundances,
                 standard explicit-ion setups
  tlusty208.py   Python TLUSTY main program (translated from the improved
                 tlusty208_fixed.f)
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
  synspec54.py   Python SYNSPEC main program (translated from synspec54.f)
  data/          place line lists here (gfATO.dat / gfMOL.dat / gfTiO.dat)
fortran/         improved Fortran twin tlusty208_fixed.f (fortran/README.md)
test/            benchmark runs and comparisons (test/README.md)
IMPROVEMENTS.md  the tlusty205-fork physics improvements ported into 208
```

## Requirements

Python 3 + NumPy. Optional: tqdm (live iteration/region progress bar when
running in a terminal; without it, one progress line per iteration/region
is printed to the run log instead).

Usage:

```python
import sys
sys.path.insert(0, '.../tlusty')    # or '.../tlusty2', '.../synspec'
import driver
```

or run `chain.py` / `ff.py` / `syn.py` directly in the respective
directory.

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
  processes in `ff.py`/`chain.py`; `NPAR <= 1` (or unset) falls back to the
  serial path, bitwise identical to `tlusty/`
- parallelism only changes floating-point summation order; differences are
  at the 1e-16 level, physics and arithmetic unchanged

## The tlusty205 physics improvements

The translated code is not stock TLUSTY 208: the physics and numerical
robustness fixes of the [tlusty205
fork](https://github.com/mattidorsch/tlusty205_fork) (occupation
probabilities exact for non-hydrogenic ions, pseudo-continuum opacity
below metal bound-free edges, extended iron-group photoionization fits,
NaN-aware convergence diagnostics, updated ionization-energy data, and
more) were first ported into the Fortran 208 source, and the Python code
was translated from the improved source. See
[IMPROVEMENTS.md](IMPROVEMENTS.md) for the complete list.

## The improved Fortran twin

`fortran/tlusty208_fixed.f` is TLUSTY 208 with the fork improvements
ported in; it is the reference implementation against which the Python
translation was validated. Build instructions are in
[fortran/README.md](fortran/README.md) — note that **`-fno-automatic` is
REQUIRED** (the code relies on SAVE semantics of local variables; without
it the executable segfaults).

## Benchmark / validation

See [test/README.md](test/README.md). Headline numbers for the benchmark
H–He solar-composition model (Teff = 22500 K, log g = 4.0, ND = 50,
~2000 frequency points, NLTE/L mode):

- the improved Fortran twin, serial Python, and parallel Python all
  converge in **23 iterations** with an identical iteration-by-iteration
  convergence history
- atmospheric structure (T, ne, rho): maximum relative difference
  **7e-7** between the Python and Fortran improved versions
- timings on a 24-core Threadripper 3960X: Fortran ~30 s, serial Python
  ~7 hr, 10-process Python ~45 min

The Python translation is about two orders of magnitude slower than the
Fortran original; use `tlusty2/` (parallel) for production models.

## References

- TLUSTY website: https://tlusty.oca.eu/tlusty/
- tlusty205 fork: https://github.com/mattidorsch/tlusty205_fork
- Hubeny I., Lanz T., 1995, ApJ, 439, 875
- Hubeny I., Lanz T., 2017, arXiv:1706.01859
- Hummer D. G., Mihalas D., 1988, ApJ, 331, 794
- A paper describing this package is in preparation.

## License

TLUSTY and SYNSPEC are distributed by Hubeny & Lanz via the [TLUSTY
website](https://tlusty.oca.eu/tlusty/). This translation preserves their
licensing and terms of use; the same terms apply to the Python code here.
