# IMPROVEMENTS — tlusty205-fork physics ported into TLUSTY 208

This document describes the physics and numerical-robustness improvements
ported from Matti Dorsch's
[tlusty205 fork](https://github.com/mattidorsch/tlusty205_fork) into
TLUSTY 208, before the code was translated to Python. All three code
bodies in this repository carry the identical changes:

- `fortran/tlusty208_fixed.f` — improved Fortran twin (reference)
- `tlusty/tlusty208.py` — serial Python version
- `tlusty2/tlusty208.py` — parallel Python version (physics functions
  byte-identical to the serial version; only the multiprocess driver
  differs)

All credit for the original fixes goes to **M. Dorsch**; they were
developed against TLUSTY 205 and mapped onto TLUSTY 208 here (stock 205
and 208 are line-identical in the affected routines, so the mapping is
nearly mechanical). Line numbers below refer to the Fortran 208 source.

---

## 1. Occupation probabilities exact for non-hydrogenic ions (DWNFR2)

Core physics. Reference: Hummer & Mihalas 1988, ApJ, 331, 794.

- Original: the dissolved-fraction routine `DWNFR1` used an approximate
  effective quantum number and an incomplete Hummer–Mihalas `K_n` factor,
  and was multiplied by the empirical `BERGFC` parameter.
- Improved: a new routine `DWNFR2` (transcribed line by line from the
  fork) replaces `DWNFR1` at all 10 call sites. It uses the exact
  effective quantum number `n* = Z sqrt(nu_H / dE)`, the complete
  Hummer–Mihalas `K_n` factor, normalizes the Holtsmark microfield by
  the charged-perturber density, and does **not** multiply by `BERGFC`.
  `DWNFR1` is retained as dead code, as in the fork.
- Routines touched: new `DWNFR2`; call sites in `OPACF1` (2), `BPOPE`,
  `OPACFD` (2), `OPACF0`, `OPACFL` (2), `OPACFA` (2).

## 2. Effective quantum number from binding energy (WNSTOR)

Core physics.

- Original: `WNSTOR` used a hydrogenic interpolation table for H and the
  principal quantum number `NQUANT` for all other ions when computing
  occupation probabilities.
- Improved: for every ion the effective quantum number is derived from
  the level binding energy, `n* = Z sqrt(E_H / E_ion)`; levels with
  `E_ion <= 0` (above-threshold / autoionizing levels) are not dissolved
  (`wop = 1`). For hydrogenic ions the new and old schemes are strictly
  equivalent. The `wn()` function itself (which retains `BERGFC`) is
  unchanged.
- Routine touched: `WNSTOR`.

## 3. Pseudo-continuum opacity below metal bound-free edges (SIGK)

Core physics.

- Original: cross sections from Opacity-Project-style tables were tapered
  to zero below the edge, so pseudo-continuum opacity vanished below
  metal bound-free thresholds.
- Improved: in pseudo-continuum mode (`MODE > 0`) the table cross section
  is extrapolated below threshold along the slope of the first segment —
  a one-line change: `IF(X.GE.XTOP(1,IC))` becomes
  `IF(X.GE.XTOP(1,IC) .OR. MODE.GT.0)`. The 208-specific sub-threshold
  tapers for `IB = 1` and hydrogen are left untouched.
- Routine touched: `SIGK`.

## 4. Iron-group photoionization fits (VERNER family)

Core physics. References: Verner et al. 1995; Verner & Yakovlev 1996.

- Original: `VERNER` provided inner-shell photoionization cross sections
  only for selected species; for Fe the inner-shell contribution replaced
  the outer-shell fit above the inner-edge energy.
- Improved:
  a) `VERNER` dispatches Z = 22–30 (except Fe) to a new routine `VERNTI`;
  b) `VERNTI` (new, ~260 lines, transcribed line by line from the fork)
     carries the full coefficient tables for 8 elements (Ti, V, Cr, Mn,
     Co, Ni, Cu, Zn) x 8 ionization stages — outer-shell 1995-style fits
     plus inner-shell contributions added beyond the inner-edge energy;
  c) `VERN26` (Fe) gains a complete 1995 **outer-shell** coefficient
     table; for energies above the inner edge the outer-shell 1995 fit is
     continued and the inner shell is changed from "replace" to "add":
     `VERN26 = VERN26 + S95*T18*FY`, guarded by `IF(E.GE.EMX)`.
- Routines touched: `VERNER`, new `VERNTI`, `VERN26`.

## 5. Level-dissolution counter timing and dimension (NNCDW / MMCDW)

- Original: the `nncdw` counter block ran **before** `CALL TRAINI`, but
  `MCDW` is only assigned inside `TRAINI` — so `nncdw` was always 0 and
  the guard based on it never triggered (a genuine bug in 208).
- Improved: the counter block is moved after `CALL TRAINI`. The
  dimension `MMCDW` is raised 26 → 100 (as in the fork; memory cost of
  `DWF1` is negligible).
- Routines touched: main program initialization sequence; `BASICS.FOR`
  / `params.py` (`MMCDW`).

## 6. NaN-aware convergence and interpolation guards

Numerical robustness.

- Original: divergence guards of the form `IF(ABS(CHMX).GT.1.D16)` never
  fire for NaN (all comparisons with NaN are false), and maximum-change
  reductions silently overwrite NaN with ordinary values, hiding
  divergence.
- Improved:
  a) `SOLVE`, `SOLVES`, `RYBCHN`: divergence guard recast in negated
     form, `IF(ITER.NE.1 .AND. .NOT.(ABS(CHMX).LE.1.D16))`, which is true
     for NaN (in Python, an explicit `not (abs(chmx) <= 1e16)`);
  b) `PRCHAN`: the three maximum reductions (per-depth `CH`, `CHMT`, and
     global `CHM`) made NaN-dominant — once NaN appears it is kept as the
     maximum;
  c) `PFNI`: the `t < 12000` branch made NaN-safe
     (`if not (t >= 12000)`); temperature clamped `tc = min(t, 350000)`
     before interpolation; the six `t <= 200000` tests rewritten as
     `it < 200`.
- Routines touched: `SOLVE`, `SOLVES`, `RYBCHN`, `PRCHAN`, `PFNI`.

## 7. GN/GP initialization in BHE

- Original: `BHE` used the Jacobian weight factors `GN`/`GP` without
  initializing them (stock code only assigns `BRTE`/`BRE`/`VISINI`),
  leaving missing terms in the Jacobian — in practice zero by accident,
  where the correct value is `GN = 1`.
- Improved: at `BHE` entry, `GP = 0; GN = 1; IF(INMP.GT.0) THEN GP = 1;
  GN = 0`.
- Routine touched: `BHE`.

## 8. `berfc` typo in DWNFR

- Original: line `cb = cb0*berfc` in `DWNFR` references the undeclared
  name `berfc` (implicitly an uninitialized variable) instead of the
  COMMON variable `bergfc` — a genuine 208 bug on the `PRINC` diagnostic
  path.
- Improved: corrected to `cb = cb0*bergfc`, matching the fork.
- Routine touched: `DWNFR`.

## 9. Adaptive lambda iteration (IADLAM)

New feature (ported; default off).

- Original: the lambda-iteration loop always runs the fixed `NLAMBD`
  passes.
- Improved: new namelist keyword `IADLAM`. With `IADLAM = 0` (default)
  behavior is unchanged. With `IADLAM = N > 0` the lambda loop exits
  early once the maximum relative population change over all depths and
  levels is below `10**(-N)` (and at least one iteration has completed;
  upper limit still `NLAMBD`). Levels with populations below 1e-10 of the
  depth maximum are ignored; no early exit on NaN. Requires a
  `POPLAM(MLEVEL,MDEPTH)` population-snapshot array. The fork's `IDSTEP`
  keyword (purely diagnostic output) was not ported.
- Routines touched: `NSTPAR` (keyword table), `RESOLV` (adaptive block).

## 10. Ionization-energy tables and related data

Reference: Rodrigues et al. 2004, ADNDT, 86, 117.

- Original: ionization energies of stages IV–VIII for Z ≈ 19–30 and
  heavier elements were placeholder values (99.99); lead was limited to
  ionization stage III; several auxiliary arrays were dimensioned for 30
  elements.
- Improved: the stage IV–VIII ionization energies are filled with real
  values from Rodrigues et al. 2004 (20 element rows; the Sn stage-IV
  value corrected 72.3 → 40.74 eV); the maximum Pb ionization stage is
  extended 3 → 7; `PFSPEC` gains ground-state statistical weights for
  Pb IV–IX; element-indexed arrays in `CHANGE`, `PARTF`, and `INIFRS`
  (including the mass table) are expanded 30 → 90.
- Routines touched: `NSTPAR` (data tables), `PFSPEC`, `CHANGE`, `PARTF`,
  `INIFRS`.

---

## Not ported (deliberately)

Purely diagnostic or engineering changes with no effect on model results:

- `ARRUSE`/`ARRUS1` array-usage statistics and the `MU*` peak counters
- `IPOPAC`/`ICOOLP` opacity-decomposition output
- `OUTPRI`/`RADPRE` g_rad/g printing
- `QUIT` stop-1 return code (the Python version already exits non-zero)
- `ITRLIN` int2→int4 type promotion and the `ntrans > 32767` guard
  (Python integers have arbitrary precision)
- `COLKUR` table expansion 15000 → 20000 (capacity only)
- `IDSTEP` (diagnostic output step)

## Verification of the port

All coefficient tables transcribed into `VERNTI` (13 tables of 64 values
each, plus `IZTAB`) were compared programmatically against the fork
source and agree exactly; the ionization-energy rows match the fork
character-for-character. The improved Fortran compiles cleanly with
gfortran, and in a smoke test (2 iterations of the 22500 K H–He
benchmark) the improved Python and improved Fortran agree to the printed
precision of the iteration log, with a maximum relative difference of
2.5e-6 in the model file. The full convergence benchmark is documented in
[test/README.md](test/README.md).
