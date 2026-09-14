# -*- coding: utf-8 -*-
"""
fortran.py — Fortran runtime helper functions.

Emulates Fortran 77 intrinsic semantics (integer division, MOD, DINT, DNINT,
DSIGN, string comparison), file units, and unformatted scratch files (SCRATCH).
"""

import math
import sys

import numpy as np

# ------------------------------------------------------------- intrinsics

def idiv(a, b):
    """Fortran integer division I/J: truncation toward zero (unlike Python //)."""
    q = abs(a) // abs(b)
    if (a < 0) != (b < 0):
        q = -q
    return q


def imod(a, b):
    """Fortran MOD(I,J): remainder has the sign of the dividend (truncation semantics)."""
    return a - idiv(a, b) * b


def dint(x):
    """Fortran DINT(X): truncation toward zero, returns a float."""
    return float(math.trunc(x))


def dnint(x):
    """Fortran DNINT(X): round to nearest integer, halves away from zero, float."""
    if x >= 0:
        return float(math.floor(x + 0.5))
    return float(math.ceil(x - 0.5))


def dsign(a, b):
    """Fortran DSIGN(A,B): take |a| with the sign of b (positive if b>=0)."""
    return abs(a) if b >= 0 else -abs(a)


def feq(a, b):
    """Fortran string equality: ignores trailing blanks (compare after rstrip)."""
    return str(a).rstrip() == str(b).rstrip()


def flog(x):
    """Fortran-semantics LOG: log(0)=-inf, log(negative)=nan (IEEE, no trap).

    Python's math.log raises ValueError, whereas Fortran continues by default.
    """
    if x > 0.0:
        return math.log(x)
    if x == 0.0:
        return float("-inf")
    return float("nan")


# -------------------------------------------------------------- file units

funits = {}


def open_unit(unit, filename=None, mode='r', scratch=False):
    """Corresponds to Fortran OPEN(UNIT=unit, FILE=filename, ...).

    scratch=True corresponds to STATUS='SCRATCH' (unformatted scratch file).
    """
    if scratch:
        fh = ScratchFile()
    else:
        fh = open(filename, mode)
    funits[unit] = fh
    return fh


def _implicit_open(unit, mode):
    """Fortran implicit open: first I/O on an unopened unit connects fort.<unit>.

    In read mode a missing file raises EOFError: a failed implicit OPEN is an
    ERR=/END= error condition in Fortran, here handled as the EOF branch.
    """
    try:
        fh = open("fort.%d" % unit, mode)
    except FileNotFoundError:
        if "r" in mode:
            raise EOFError("unit %d: fort.%d does not exist (implicit OPEN failed)"
                           % (unit, unit))
        raise
    funits[unit] = fh
    return fh


def read_line(unit):
    """Read one line from a file unit; return str without newline; EOFError at EOF."""
    fh = funits.get(unit)
    if fh is None:
        fh = _implicit_open(unit, "r")
    line = fh.readline()
    if line == "":
        raise EOFError("unit %d: end of file" % unit)
    return line.rstrip("\n")


def write_line(unit, s):
    """Write one line to a file unit (newline appended), like Fortran formatted WRITE."""
    fh = funits.get(unit)
    if fh is None:
        fh = _implicit_open(unit, "w")
    fh.write(str(s) + "\n")


def close_unit(unit):
    """Corresponds to Fortran CLOSE(UNIT=unit): close and remove from funits."""
    fh = funits.pop(unit)
    if hasattr(fh, "close"):
        fh.close()


def read_stdin_line():
    """Corresponds to Fortran READ(5,...) / READ(*,...): read a line from stdin;
    raise SystemExit on EOF (mimicking a Fortran program aborting with no input)."""
    line = sys.stdin.readline()
    if line == "":
        raise SystemExit("stdin EOF")
    return line.rstrip("\n")


# ----------------------------------------------------------- scratch files

class ScratchFile:
    """Emulates a Fortran unformatted sequential scratch file (STATUS='SCRATCH').

    Each WRITE stores one record; numpy arrays are snapshotted with np.copy on
    write, and reads return the write-time snapshot itself (Fortran semantics).
    """

    def __init__(self):
        self._records = []
        self._pos = 0

    def write(self, *vals):
        """Write one record: WRITE(u) A,B,... ; arrays are snapshotted automatically.

        If the read/write pointer is not at the end of the records, truncate the
        old records after it before appending — Fortran sequential-write semantics.
        """
        snap = tuple(np.copy(v) if isinstance(v, np.ndarray) else v
                     for v in vals)
        if self._pos < len(self._records):
            del self._records[self._pos:]
        self._records.append(snap)
        self._pos += 1

    def read(self):
        """Read the next record: single value returned as-is, multiple as a tuple; arrays return the snapshot itself."""
        if self._pos >= len(self._records):
            raise EOFError("scratch file: read past end of records")
        rec = self._records[self._pos]
        self._pos += 1
        return rec[0] if len(rec) == 1 else rec

    def rewind(self):
        """Corresponds to Fortran REWIND: move the read pointer to the start."""
        self._pos = 0

    def backspace(self):
        """Corresponds to Fortran BACKSPACE: move the read/write pointer back one record (no-op at the start)."""
        if self._pos > 0:
            self._pos -= 1

    def endfile(self):
        """Corresponds to Fortran ENDFILE: truncate all records after the current position.

        Approximate semantics: Fortran's ENDFILE writes an end-of-file mark at
        the current position; BACKSPACE/REWIND can still read earlier records.
        Here we drop trailing records, enough for fill → REWIND → read usage.
        """
        del self._records[self._pos:]


def rewind_unit(unit):
    """Corresponds to Fortran REWIND unit: seek(0) for plain files, rewind() for scratch.

    Unopened unit: Fortran would implicitly connect fort.<unit>; here it is
    opened as w+ (truncating the old file; a later write rewrites from the start).
    """
    fh = funits.get(unit)
    if isinstance(fh, ScratchFile):
        fh.rewind()
    elif fh is not None:
        fh.flush()
        fh.seek(0)
    elif unit in scratch:
        scratch[unit].rewind()
    else:
        _implicit_open(unit, "w+")


def endfile_unit(unit):
    """Corresponds to Fortran ENDFILE unit.

    Plain files: truncate at the current position (file.truncate()); scratch:
    truncate the record list. See ScratchFile.endfile for the semantics.
    """
    fh = funits.get(unit)
    if isinstance(fh, ScratchFile):
        fh.endfile()
    elif fh is not None:
        # in r+ mode a read must be followed by flush before truncate, else truncation has no effect
        fh.flush()
        fh.truncate(fh.tell())
    elif unit in scratch:
        scratch[unit].endfile()
    else:
        raise KeyError("unit %d not open" % unit)


# units 91/92/93 are unformatted scratch files (STATUS='SCRATCH')
scratch = {91: ScratchFile(), 92: ScratchFile(), 93: ScratchFile()}
