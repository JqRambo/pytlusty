# fortran — the improved Fortran twin

`tlusty208_fixed.f` is **TLUSTY 208 with the physics improvements of the
[tlusty205 fork](https://github.com/mattidorsch/tlusty205_fork)
(M. Dorsch) ported in** — occupation probabilities exact for
non-hydrogenic ions, pseudo-continuum opacity below metal bound-free
edges, extended iron-group photoionization fits, NaN-aware convergence
diagnostics, and updated atomic data (see
[../IMPROVEMENTS.md](../IMPROVEMENTS.md) for the full list).

This is the **reference implementation against which the Python
translation was validated**: `tlusty/tlusty208.py` and
`tlusty2/tlusty208.py` are line-by-line translations of this source, and
the benchmark in `test/` shows bit-level agreement of the convergence
history.

## Build

```
gfortran -O2 -w -std=legacy -mcmodel=medium -fno-automatic -o tlusty208_fixed.exe tlusty208_fixed.f
```

**`-fno-automatic` is REQUIRED.** The code relies on SAVE semantics of
local variables (e.g. the `itrx` counter in `RDATAX` must retain its
value between calls). With gfortran's default stack allocation the
executable segfaults immediately. This is a property of the original
TLUSTY 208 code — a pristine stock 208 built without `-fno-automatic`
crashes the same way — not something introduced by the port.

## Run

As with stock TLUSTY, the program reads the standard input file on
stdin:

```
./tlusty208_fixed.exe < FF.5
```

and produces the usual `fort.*` output files (`fort.7` model, `fort.9`
convergence log, etc.). The `data/` directory with the atomic data (from
`../tlusty/data/`) must be reachable from the working directory, e.g. via
a symlink.
