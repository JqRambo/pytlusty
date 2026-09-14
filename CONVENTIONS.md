# Translation Conventions: Fortran → Python

This document records the conventions that were followed in the line-by-line
translation of `tlusty208.f` (TLUSTY 208) and `synspec54.f` (SYNSPEC 54) into
Python. The goal of the translation was strict functional identity: no
paraphrasing, no restructuring for style, no omission of any executable
statement. Every physical formula and every numerical algorithm of the
Fortran source is preserved exactly.

## Source layout

Each package contains:

```
  params.py        # all PARAMETER constants
  commons.py       # all COMMON-block variables (lazily allocated; use: import commons as C)
  fortran.py       # Fortran runtime-semantics helpers (from fortran import *)
  tlusty208.py     # TLUSTY main module (single file, as the Fortran original)
  synspec54.py     # SYNSPEC main module (single file, as the Fortran original)
```

## Naming

- Subroutine/function names become lowercase Python function names, e.g.
  `SUBROUTINE RESOLV` → `def resolv():`.
- Fortran identifiers are case-insensitive, Python is not. Rules:
  - COMMON variables are always accessed through the canonical spelling
    declared in `commons.py` (`C.TEFF`, `C.POPUL`, ...); any case variant in
    the source (`Teff`, `tEfF`) is normalized to the canonical spelling.
  - PARAMETERs use the canonical spelling of `params.py`.
  - Local variables keep the spelling of their first occurrence,
    consistently within the function.
- A local variable must not shadow a `params.py` constant; on a clash the
  local gets an `_l` suffix and a comment.

## Types and arrays (1-based indexing retained)

- `IMPLICIT REAL*8 (A-H,O-Z), LOGICAL*1 (L)`:
  initial letter I–N → `int`; A–H, O–Z → `float`; L... → `bool`; explicit
  declarations take precedence.
- Arrays keep Fortran's 1-based indexing: every dimension is allocated one
  element larger and index 0 is unused.
  Local 1-D: `a = np.zeros(n + 1)`; 2-D: `a = np.zeros((n1 + 1, n2 + 1))`,
  accessed as `a[i, j]`.
- COMMON arrays are pre-allocated by `commons.py` at their declared
  dimensions +1; use `C.XXX[i, j]` directly, never reallocate.
- Integer local arrays: `np.zeros(n+1, dtype=np.int64)`; logical arrays
  `dtype=bool`; character arrays use a list or
  `np.empty(n+1, dtype=object)` filled with `''`.
- Integer division: Fortran `I/J` truncates toward zero → always
  `idiv(i, j)` (provided by fortran.py); never `//` or `/`.
- `MOD(I,J)` → `imod(i, j)`; `DINT(X)` → `dint(x)`; `DNINT(X)` → `dnint(x)`;
  `DSIGN(A,B)` → `dsign(a, b)`; `DABS`→`abs`, `DFLOAT`→`float`,
  `SNGL`→`float`, `IABS`→`abs`.
- Math functions use `math.`: `DEXP`→`math.exp`, `DLOG`→`math.log`,
  `DLOG10`→`math.log10`, `DSQRT`→`math.sqrt`,
  `DSIN/DCOS/DTAN/DATAN/DATAN2`→`math.sin/cos/tan/atan/atan2`.
- `DMAX1/DMIN1/MAX0/MIN0/AMAX1...` → `max`/`min`.
- Literals: `1.D0`→`1.0`, `2.3D-15`→`2.3e-15`, `.TRUE.`→`True`,
  `.FALSE.`→`False`.
- Operators: `.EQ.`→`==`, `.NE.`→`!=`, `.LT.`→`<`, `.LE.`→`<=`, `.GT.`→`>`,
  `.GE.`→`>=`, `.AND.`→`and`, `.OR.`→`or`, `.NOT.`→`not`, `.EQV.`→`==`,
  `.NEQV.`→`!=`, `**`→`**`.
- String comparisons ignore trailing blanks: use `feq(a, b)` (fortran.py).

## Dummy-argument and return-value convention

Fortran dummies are passed by reference. The Python rules are:

- Array dummies: numpy arrays are shared by reference; modify in place and
  do NOT return them.
- Scalar dummies: if the body assigns to any scalar dummy, the function
  returns ALL scalar dummies (in declaration order, whether modified or
  not), and every call site re-receives them:
  ```python
  # Fortran: CALL STATE(MODE,ID,T,ANE), with T and ANE modified inside STATE
  mode, id, t, ane = state(mode, id, t, ane)
  ```
- If no scalar dummy is modified, the function returns None implicitly and
  call sites simply write `sub(...)`.
- A `FUNCTION` returns its value; if it also modifies scalar dummies (rare),
  it returns `(value, *scalars)`, noted in the docstring.
- Passing an array element as an array base (`CALL X(A(5))` with the callee
  using `B(1)` ...) → pass the slice `a[5:]` with a comment.
- A literal actual argument for a dummy the callee modifies → receive into a
  temporary, with a comment.

## Control flow

- `DO 10 I=1,N` → `for i in range(1, n + 1):`; step `,2` →
  `range(1, n + 1, 2)`; reverse `DO I=N,1,-1` → `range(n, 0, -1)`.
  Note the ±1 adjustment of the terminal value.
- A loop variable used after the loop (in Fortran it retains terminal
  value + step) → assign it explicitly after the loop, with a comment.
- `DO WHILE (...)` → `while ...:`.
- `GO TO`: preferably refactored minimally into while/if/break/continue;
  where no clean refactoring exists, a `_label` state variable with a
  `while True` dispatcher is used, keeping the original label comments:
  ```python
  _label = 10                    # corresponds to Fortran label 10
  while True:
      if _label == 10:
          ...
          _label = 20            # GO TO 20
          continue
      if _label == 20:
          ...
          break                  # end of subroutine / RETURN
  ```
  Either way, the original labels and the GO TO destinations are noted in
  nearby comments.
- Arithmetic `IF (X) 10,20,30` → `if x < 0: ... elif x == 0: ... else: ...`.
- `RETURN` → `return` (with the scalar-dummy convention where applicable);
  `STOP` → `raise SystemExit`; `PAUSE` → comment + `pass`.

## DATA / SAVE / EQUIVALENCE

- `DATA`-initialized local arrays that are never modified afterwards →
  plain assignment at the top of the function, with a `# DATA ...` comment.
- `DATA` arrays that ARE modified (implicit SAVE in Fortran) → promoted to
  module-level `_save_<routine>_<name>` variables, with a comment.
- `BLOCK DATA` → `def block_data():` assigning to `C.XXX`; called first in
  main.
- `EQUIVALENCE`: conforming arrays → simple alias `a = b` with a comment;
  different shapes → numpy views (mind `reshape(..., order='F')`); where
  inexpressible, both variables are kept and the assumption is documented.

## I/O

- `WRITE(6,...)` / `WRITE(*,...)` → `print(...)`; FORMATs are translated
  into f-strings, with the original FORMAT statement kept as a comment.
  `1H0`/`/` → blank line; `X` → space.
- Files: `OPEN(UNIT=n,FILE='...',...)` → `open_unit(n, '...', mode)`
  (fortran.py); `WRITE(n, fmt)` → `write_line(n, f"...")`; `READ(n, fmt)`
  is parsed per context with `read_line(n)`.
- Unformatted scratch files (`STATUS='SCRATCH'`, units 91/92/93): the
  `scratch[91]` ScratchFile object; `WRITE(91) A,B` →
  `scratch[91].write(a, b)`; `READ(91) A,B` → `a, b = scratch[91].read()`;
  `REWIND 91` → `scratch[91].rewind()`. Array records are snapshotted
  automatically, matching Fortran semantics; the scratch data reside in
  memory rather than on disk.
- `READ(5,...)`/`READ(*,...)` → `read_stdin_line()` followed by parsing
  translated literally from the original FORMAT/list-directed form.
- `CLOSE(n)` → `close_unit(n)`; `ENDFILE n` / `BACKSPACE n` → comment plus
  the corresponding helper call.

## Comment policy

- Every function opens with a docstring: the original Fortran header
  comment (kept in English) plus `Corresponds to tlusty208.f/synspec54.f
  lines X–Y`.
- Original `C`/`!` comments are kept (English original).
- Translation decisions are annotated: `# GO TO 100 -> break out of the
  loop`, `# Fortran integer division`, `# DATA statement, implicit SAVE`,
  and similar.
- Physics fixes ported from the tlusty205 fork are marked `FIX(fork):`;
  Python-side additions are marked `Python addition:`.
- Any semantic uncertainty was translated in the most reasonable way and
  flagged with a `# TODO(port):` comment; no code was ever omitted.
