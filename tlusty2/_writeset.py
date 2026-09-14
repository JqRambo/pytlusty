# -*- coding: utf-8 -*-
"""
_writeset.py — empirical write-set verification tool (invoked by parmap when TLUSTY_WSET=1)
==================================================================

Purpose: snapshot/compare all numpy arrays and scalars in vars(C) before and after a
kernel's ij loop, and append the names of variables actually written (accumulated per
kernel, deduplicated) to wset.log in the working directory, to cross-check the accum/slots lists in the parmap.KERNELS registry.

Note: snapshots are taken once at the entry and once at the exit of one kernel call (the
whole ij loop), yielding the union of that call's write set — exactly the information
needed to check the registry; per-ij comparison yields the same union at much higher
cost, so entry/exit comparison is used. Writes restored to net zero inside the function
(e.g. the temporary modification of POPUL/ABTRA in the iprcrs branch of opacf1, or the
save/restore of ISPLIN in rtefr1) do not appear in the results — this matches the "no net effect on the worker" criterion.
"""

import os

import numpy as np

import commons as C

LOG = os.path.abspath('wset.log')

# {kernel: set of already-logged written variable names} (deduplicated accumulation; in a worker it is
# the parent-process copy at fork time; newly found names in a worker are appended directly to wset.log)
_logged = {}
_switches_logged = set()

_SWITCHES = ['IFPREC', 'ifprec', 'IRDER', 'IFALI', 'IOPTAB', 'IDISK', 'icompt',
             'ILMCOR', 'ILASCT', 'ISPODF', 'iprcrs', 'IFDIEL', 'IFRYB',
             'IFPRAD', 'IFPRD', 'ISPLIN', 'ILPSCT', 'NDRE', 'IOPADD', 'INMOD',
             'IFPOPR', 'ITER', 'ILAM', 'NFREQ', 'NFREQE', 'ND', 'NTRANS']


def append_log(lines):
    """Append lines to wset.log (workers call this directly; short lines with O_APPEND are safe enough)."""
    if not lines:
        return
    with open(LOG, 'a') as f:
        for line in lines:
            f.write(line + '\n')


def log_switches(kernel):
    """On the first call of each kernel, write the runtime values of key switches into wset.log."""
    if kernel in _switches_logged:
        return
    _switches_logged.add(kernel)
    kv = ' '.join(f'{s}={getattr(C, s, "?")}' for s in _SWITCHES)
    append_log([f'# switches {kernel}: {kv}'])


def take_snap(kernel):
    """Snapshot arrays/scalars in vars(C) not yet logged as written."""
    logged = _logged.setdefault(kernel, set())
    snap = {}
    for name, val in vars(C).items():
        if name.startswith('__') or name in logged:
            continue
        if isinstance(val, np.ndarray):
            snap[name] = val.copy()
        elif isinstance(val, (bool, int, float, np.generic)):
            snap[name] = val
    return snap


def collect_news(kernel, snap):
    """Compare against the snapshot and return newly found written variable names (also accumulating them into the dedup set)."""
    logged = _logged.setdefault(kernel, set())
    news = []
    cur_vars = vars(C)
    for name, old in snap.items():
        if name not in cur_vars:
            continue
        val = cur_vars[name]
        if isinstance(old, np.ndarray):
            if not np.array_equal(val, old):
                news.append(name)
        elif val != old:
            news.append(name)
    # arrays newly lazily allocated during the loop: compare against the "just-allocated value"
    # (all zeros / empty strings); a difference counts as written (excludes false positives from read-only-triggered lazy allocation, e.g. DABM1/DEMM1)
    for name, val in cur_vars.items():
        if name.startswith('__') or name in logged or name in snap:
            continue
        if isinstance(val, np.ndarray):
            if val.dtype == object:
                written = bool(np.any(val != ''))
            else:
                written = bool(np.any(val != 0))
            if written:
                news.append(name)
    for name in news:
        logged.add(name)
    return sorted(set(news))
