# -*- coding: utf-8 -*-
"""
fortran.py — Fortran runtime helper functions.

Emulates Fortran 77 intrinsics (integer division, MOD, DINT, DNINT, DSIGN,
string comparison), file units (OPEN/READ/WRITE/CLOSE), and scratch files.
"""

import math
import sys

import numpy as np

# ---------------------------------------------------------- intrinsics

def idiv(a, b):
    """Fortran integer division I/J: truncates toward zero (unlike Python //)."""
    q = abs(a) // abs(b)
    if (a < 0) != (b < 0):
        q = -q
    return q


def imod(a, b):
    """Fortran MOD(I,J): remainder takes the sign of the dividend (truncating semantics)."""
    return a - idiv(a, b) * b


def dint(x):
    """Fortran DINT(X): truncate toward zero, returned as a float."""
    return float(math.trunc(x))


def dnint(x):
    """Fortran DNINT(X): round to nearest integer, half away from zero, returned as float."""
    if x >= 0:
        return float(math.floor(x + 0.5))
    return float(math.ceil(x - 0.5))


def dsign(a, b):
    """Fortran DSIGN(A,B): take |a| and give it the sign of b (b>=0 is positive)."""
    return abs(a) if b >= 0 else -abs(a)


def feq(a, b):
    """Fortran string equality: ignore trailing blanks (compare after rstrip)."""
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

    scratch=True is STATUS='SCRATCH' (ScratchFile emulates an unformatted temp file).
    """
    if scratch:
        fh = ScratchFile()
    else:
        fh = open(filename, mode)
    funits[unit] = fh
    return fh


def _implicit_open(unit, mode):
    """Fortran implicit open: a unit never OPENed connects fort.<unit> on first I/O.

    In read mode a missing file raises EOFError: in Fortran a failed implicit
    OPEN is an ERR=/END=-catchable condition, here handled as the EOF branch.
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
    """Read one line from a file unit, returning a str without newline; raises EOFError at EOF."""
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
    """Corresponds to Fortran READ(5,...) / READ(*,...): read one line from stdin;
    raises SystemExit at EOF (mimics a Fortran program terminating on missing input)."""
    line = sys.stdin.readline()
    if line == "":
        raise SystemExit("stdin EOF")
    return line.rstrip("\n")


# ------------------------------------------------------------ scratch files

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

        If the pointer is not at the end, trailing old records are truncated first —
        Fortran sequential-write semantics (writing here invalidates what follows).
        """
        snap = tuple(np.copy(v) if isinstance(v, np.ndarray) else v
                     for v in vals)
        if self._pos < len(self._records):
            del self._records[self._pos:]
        self._records.append(snap)
        self._pos += 1

    def read(self):
        """Read the next record: single value returned as-is, multiple as a tuple; arrays return the write-time snapshot."""
        if self._pos >= len(self._records):
            raise EOFError("scratch file: read past end of records")
        rec = self._records[self._pos]
        self._pos += 1
        return rec[0] if len(rec) == 1 else rec

    def rewind(self):
        """Corresponds to Fortran REWIND: reset the read pointer to the beginning."""
        self._pos = 0

    def backspace(self):
        """Corresponds to Fortran BACKSPACE: move the read/write pointer back one record (no-op at the beginning)."""
        if self._pos > 0:
            self._pos -= 1

    def endfile(self):
        """Corresponds to Fortran ENDFILE: truncate all records after the current position.

        Approximate semantics: Fortran's ENDFILE writes an end-of-file mark at
        the current position; here the trailing records are simply discarded,
        which suffices for this program's scratch usage (write all → REWIND → read).
        """
        del self._records[self._pos:]


def rewind_unit(unit):
    """Corresponds to Fortran REWIND unit: seek(0) for regular files, rewind() for scratch.

    Unopened unit: Fortran would implicitly connect fort.<unit>; here open with
    w+ (truncating the old file, since later writes rewrite it from the start).
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

    Regular files: truncate at the current position (file.truncate()); scratch:
    truncate the record list. See ScratchFile.endfile for the approx. semantics.
    """
    fh = funits.get(unit)
    if isinstance(fh, ScratchFile):
        fh.endfile()
    elif fh is not None:
        # in r+ mode a flush is required after reads before truncate, otherwise the truncation has no effect
        fh.flush()
        fh.truncate(fh.tell())
    elif unit in scratch:
        scratch[unit].endfile()
    else:
        raise KeyError("unit %d not open" % unit)


# Units 91/92/93 are unformatted scratch files (STATUS='SCRATCH')
scratch = {91: ScratchFile(), 92: ScratchFile(), 93: ScratchFile()}
