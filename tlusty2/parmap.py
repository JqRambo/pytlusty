# -*- coding: utf-8 -*-
"""
parmap.py — Multiprocess parallel framework for the TLUSTY frequency (ij) loops
===============================================================================

Design notes:
- NPAR from env var TLUSTY_NPAR (default 1); NPAR<=1 is purely serial, bit-identical.
- Each parallel call builds a fresh Pool with the fork context (workers see
  the parent's full COMMON state via COW) and closes it right after the call.
- Active ij list split into NPAR contiguous chunks, pool.map'ed to `_par_worker`.
- KERNELS registry injected by tlusty208 via register() after defining the
  loop bodies (parmap does not import tlusty208, avoiding circular imports).
- Workers return two kinds of results, applied by the parent in chunk order:
    accum — accumulators (arrays/scalars). Worker snapshots them at chunk
             start, returns delta = current - snapshot at end; parent C.X += delta.
             (Delta, not full copy, also works for never-zeroed accumulators,
             e.g. REIM/REDM/HEIM/REDMM/HEIMM — never cleared in Fortran or
             Python — and rosstd's module SAVE arrays _save_rosstd_pld and
             _save_rosstd_abpld; for zeroed ones delta equals a full copy.)
             'M:' prefix = module-level variable of body's module, not of C.
    slots — slot arrays. Worker snapshots at chunk start; at chunk end
             np.flatnonzero(cur != snap) finds written elements, returned as
             (flat_index, values); parent applies C.X.flat[idx] = vals in chunk
             order. Unwritten elements never appear — self-consistent; elements
             rewritten with the same value are safely skipped. Non-float dtypes
             (e.g. bool) supported. Scratch arrays rewritten each ij may go in
             slots too: ascending chunk application leaves the serial last-ij value.
- Worker try/except BaseException: traceback returned, parent re-raises it.
- Worker redirects fd 1 to /dev/null so processes cannot garble FF.6.
- TLUSTY_WSET=1 enables empirical write-set verification (see _writeset.py).
"""

import multiprocessing
import os
import sys
import traceback

import numpy as np

import commons as C

NPAR = int(os.environ.get('TLUSTY_NPAR', '1') or '1')
WSET = bool(os.environ.get('TLUSTY_WSET', ''))

# kernel registry: {name: {'body': loop-body function, 'accum': [...], 'slots': [...]}}
KERNELS = {}


def register(name, body, accum=(), slots=()):
    """Register a parallelizable ij loop body (called by tlusty208 after defining body)."""
    KERNELS[name] = {'body': body, 'accum': list(accum), 'slots': list(slots)}


def _resolve(name, body):
    """Resolve a registry name to (object, attribute name); 'M:xxx' means a module-level variable of body's module."""
    if name.startswith('M:'):
        return sys.modules[body.__module__], name[2:]
    return C, name


def _chunks(ijs, n):
    """Split the ij list into n contiguous chunks (as even as possible; the remainder goes to the earlier chunks)."""
    n = max(1, min(n, len(ijs)))
    q, r = divmod(len(ijs), n)
    out = []
    i = 0
    for k in range(n):
        m = q + (1 if k < r else 0)
        out.append(ijs[i:i + m])
        i += m
    return [c for c in out if c]


def _snapshot(kern):
    """Snapshot accum/slots at chunk start; returns {name: copy or scalar or None}."""
    snap = {}
    body = kern['body']
    for name in kern['accum'] + kern['slots']:
        obj, attr = _resolve(name, body)
        val = getattr(obj, attr, None)
        if isinstance(val, np.ndarray):
            snap[name] = val.copy()
        elif val is None:
            snap[name] = None      # a module-level SAVE array may not be allocated yet
        else:
            snap[name] = val       # scalar (int/float/bool)
    return snap


def _collect(kern, snap):
    """Chunk-end collection: deltas for accum and (flat_index, values) for slots."""
    body = kern['body']
    deltas = []
    for name in kern['accum']:
        obj, attr = _resolve(name, body)
        cur = getattr(obj, attr, None)
        old = snap[name]
        if cur is None:
            deltas.append((name, None))          # never touched by this chunk
        elif old is None:
            deltas.append((name, cur.copy()))    # starting point is effectively all zeros
        elif isinstance(cur, np.ndarray):
            deltas.append((name, cur - old))
        else:
            deltas.append((name, cur - old))     # scalar
    diffs = []
    for name in kern['slots']:
        obj, attr = _resolve(name, body)
        cur = getattr(obj, attr, None)
        old = snap[name]
        if cur is None or old is None:
            continue
        idx = np.flatnonzero(cur != old)
        if idx.size:
            diffs.append((name, idx, cur.flat[idx].copy()))
    return deltas, diffs


def _apply(kern, deltas, diffs):
    """The parent applies one chunk's accum deltas and slots diffs in chunk order."""
    body = kern['body']
    for name, delta in deltas:
        if delta is None:
            continue
        obj, attr = _resolve(name, body)
        cur = getattr(obj, attr, None)
        if cur is None:
            setattr(obj, attr, delta)
        elif isinstance(cur, np.ndarray):
            cur += delta
        else:
            setattr(obj, attr, cur + delta)      # scalar
    for name, idx, vals in diffs:
        obj, attr = _resolve(name, body)
        getattr(obj, attr).flat[idx] = vals


def _par_worker(task):
    """Worker: calls the registered loop body for each ij of the chunk in order, returns delta/diff."""
    kernel_name, ijs, args = task
    try:
        # redirect the worker's stdout to /dev/null so processes cannot garble FF.6
        devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull, 1)
        os.close(devnull)
        kern = KERNELS[kernel_name]
        body = kern['body']
        snap = _snapshot(kern)
        wset_snap = None
        if WSET:
            import _writeset
            wset_snap = _writeset.take_snap(kernel_name)
        for ij in ijs:
            body(ij, *args)
        deltas, diffs = _collect(kern, snap)
        if WSET:
            names = _writeset.collect_news(kernel_name, wset_snap)
            _writeset.append_log(
                [f'{kernel_name} {n} (worker{os.getpid()})' for n in names])
        return (kernel_name, None, deltas, diffs)
    except BaseException:
        # errors are not silenced: the traceback text is returned and the parent re-raises it verbatim
        return (kernel_name, traceback.format_exc(), None, None)


def par_foreach(kernel_name, ijs, *args):
    """Run the kernel loop body over the active ij list in order; multiprocess-parallel when NPAR>1."""
    kern = KERNELS[kernel_name]
    body = kern['body']
    if NPAR <= 1 or len(ijs) < 2:
        # pure serial path: no Pool, bit-identical to the per-ij loop before extraction
        wset_snap = None
        if WSET:
            import _writeset
            _writeset.log_switches(kernel_name)
            wset_snap = _writeset.take_snap(kernel_name)
        for ij in ijs:
            body(ij, *args)
        if WSET:
            names = _writeset.collect_news(kernel_name, wset_snap)
            _writeset.append_log([f'{kernel_name} {n}' for n in names])
        return

    chunks = _chunks(list(ijs), NPAR)
    if WSET:
        import _writeset
        _writeset.log_switches(kernel_name)
    ctx = multiprocessing.get_context('fork')
    pool = ctx.Pool(len(chunks))
    try:
        results = pool.map(
            _par_worker, [(kernel_name, ch, args) for ch in chunks])
    finally:
        pool.close()
        pool.join()
    # pool.map preserves input order → apply in chunk order (ascending ij)
    for kernel_name, err, deltas, diffs in results:
        if err is not None:
            raise RuntimeError(
                f'parallel worker failed in kernel {kernel_name!r}:\n{err}')
        _apply(kern, deltas, diffs)
