# test — benchmark and validation

Benchmark case: a **H–He solar-composition model atmosphere**, Teff =
22500 K, log g = 4.0, ND = 50 depth points, NFREAD ≈ 2000 frequency
points, FF stage (NLTE/L mode), nst parameters `NLAMBD=6, ITEK=40,
IACC=40, NITER=31`. The same starting model is used for all runs.

## Implementations compared

| label | implementation |
|---|---|
| F-orig | original Fortran TLUSTY 208 (stock, no fork fixes) |
| F-imp | improved Fortran twin `fortran/tlusty208_fixed.f` |
| Python serial | `tlusty/` (improved, single process) |
| Python parallel | `tlusty2/` (improved, `TLUSTY_NPAR` processes) |

## Directory layout

```
run_fortran_fixed/   F-imp run (converged: 23 iterations)
run_py_serial/       Python serial run (converged: 23 iterations)
run_py_parallel/     Python parallel run (converged: 23 iterations)
syn_*                spectrum runs (see below)
```

Each `run_*` directory contains the standard TLUSTY input/output files:
`FF.5` (input), `FF.6` (log), `FF.7` (model), `FF.9` (convergence
history), `nst`, and the remaining `fort.*` files; the serial run
directory also holds the common starting model (`old.5`/`old.7`).

## Comparison scripts

- `compare_struct.py out.pdf label:path.7 label:path.7 [...]` —
  atmospheric-structure comparison: upper panel T / ne / rho vs. column
  mass M, lower panel relative differences.
- `compare_spec_fixed.py out.pdf label:ref.spec label:test.spec` —
  spectrum comparison with spline continuum normalization (same
  normalization scheme as the publication figures): upper panel spectra,
  lower panel residuals.

## Expected results

**Convergence.** The three improved implementations (F-imp, Python
serial, Python parallel) all converge in **23 iterations** with an
identical iteration-by-iteration convergence history (same maximum
relative change at every iteration, down to the final value); no NaN in
any model.

**Atmospheric structure (translation fidelity).** Comparing the converged
models of the improved Python versions against the improved Fortran
twin: median relative difference 0, **maximum relative difference 7e-7**
in T, ne, and rho.

**Spectra.** Spectrum synthesis is run with the **Fortran SYNSPEC** on
identical input for each model (3000–9000 Å, `gfATO.dat` line list,
20200 wavelength points, same `fort.55` parameters). Comparing the
spline-normalized spectra computed from the improved Python models
against the one from the improved Fortran model: **bit-identical at
93.6% of the 20200 wavelength points**, maximum relative difference
**2.1e-3** (in the H-beta wing).

Note: the line lists are not shipped with the repository. To reproduce
the synthesis runs, download `gfATO.dat` (and optionally `gfMOL.dat`,
`gfTiO.dat`) from the TLUSTY website
(https://tlusty.oca.eu/tlusty/) into `synspec/data/` and link it into
the run directory as `fort.19` (the `data` symlinks in `syn_*/` already
point to `synspec/data/`).

**Effect of the physics fixes (F-imp vs. F-orig).** The fork
improvements change the converged structure at the few-1e-3 level
(median relative differences: T ≈ 1.4e-3, ne ≈ 1.8e-3, rho ≈ 2.0e-3) and
the normalized spectrum by a median of ~2e-5, with the largest effect at
the He I lines (up to ~9e-2 near 5740 Å).

## Timings

On a 24-core Threadripper 3960X, full convergence of the benchmark:

- improved Fortran twin: ~30 s
- serial Python: ~7 hr
- 10-process Python (`tlusty2/`, `TLUSTY_NPAR=10`): ~45 min
