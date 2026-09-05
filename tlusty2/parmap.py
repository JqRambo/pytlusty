# -*- coding: utf-8 -*-
"""
parmap.py — TLUSTY 频率(ij)循环的多进程并行框架
================================================

设计要点：
- NPAR 取自环境变量 TLUSTY_NPAR（缺省 1）；NPAR<=1 时纯串行，与原版逐位一致。
- 每次并行调用用 fork 上下文新建 Pool（worker 经 COW 看到父进程当前全部
  COMMON 状态），调用结束立即关闭。
- 活跃 ij 列表切成 NPAR 个连续块，pool.map 到模块级 worker `_par_worker`。
- kernel 注册表 KERNELS 由 tlusty208 在定义循环体函数后调用 register() 注入
  （parmap 不 import tlusty208，避免循环 import）。
- worker 返回两类结果，父进程按块序应用：
    accum —— 累加器（数组/标量）。worker 在块首对它们做快照，块尾返回
             delta = 当前值 - 快照；父进程 C.X += delta。
             （用 delta 而非全量拷贝，这样对"父进程未清零"的累加器也正确，
             例如 REIM/REDM/HEIM/REDMM/HEIMM 在 Fortran/Python 中都从不清零，
             以及 rosstd 的模块级 SAVE 数组 _save_rosstd_pld/_save_rosstd_abpld；
             对父进程已清零的累加器，delta 与全量拷贝等价。）
             名字前缀 'M:' 表示 body 所在模块的模块级变量（而非 C 的属性）。
    slots —— 槽位数组。worker 在块首快照，块尾用 np.flatnonzero(cur != snap)
             找出被写过的元素，返回 (flat_index, values)；父进程按块序
             C.X.flat[idx] = vals。没被写的元素不出现在结果里，自带正确性；
             恰好写成与旧值相同的元素不写也不错。支持非 float dtype（如 bool）。
             对"每个 ij 全量重写"的临时数组，块按升序应用后父进程最终值即
             串行最后一个活跃 ij 的值，因此临时数组也可放入 slots 以保持
             循环后状态与串行一致。
- worker 内 try/except BaseException：traceback 文本返回，父进程原样抛出。
- worker 把 fd 1 重定向到 /dev/null，防止多个进程往 FF.6 乱写。
- TLUSTY_WSET=1 时做写集合实证核验（见 _writeset.py）。
"""

import multiprocessing
import os
import sys
import traceback

import numpy as np

import commons as C

NPAR = int(os.environ.get('TLUSTY_NPAR', '1') or '1')
WSET = bool(os.environ.get('TLUSTY_WSET', ''))

# kernel 注册表：{名字: {'body': 循环体函数, 'accum': [...], 'slots': [...]}}
KERNELS = {}


def register(name, body, accum=(), slots=()):
    """注册一个可并行的 ij 循环体（由 tlusty208 在定义 body 后调用）。"""
    KERNELS[name] = {'body': body, 'accum': list(accum), 'slots': list(slots)}


def _resolve(name, body):
    """把注册表名字解析为 (对象, 属性名)；'M:xxx' 表示 body 模块的模块级变量。"""
    if name.startswith('M:'):
        return sys.modules[body.__module__], name[2:]
    return C, name


def _chunks(ijs, n):
    """把 ij 列表切成 n 个连续块（长度尽量均匀，降序余数分给前面的块）。"""
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
    """对 accum/slots 做块首快照；返回 {名字: 拷贝 或 标量 或 None}。"""
    snap = {}
    body = kern['body']
    for name in kern['accum'] + kern['slots']:
        obj, attr = _resolve(name, body)
        val = getattr(obj, attr, None)
        if isinstance(val, np.ndarray):
            snap[name] = val.copy()
        elif val is None:
            snap[name] = None      # 模块级 SAVE 数组可能尚未分配
        else:
            snap[name] = val       # 标量（int/float/bool）
    return snap


def _collect(kern, snap):
    """块尾收集：accum 的 delta 与 slots 的 (flat_index, values)。"""
    body = kern['body']
    deltas = []
    for name in kern['accum']:
        obj, attr = _resolve(name, body)
        cur = getattr(obj, attr, None)
        old = snap[name]
        if cur is None:
            deltas.append((name, None))          # 本块从未触碰
        elif old is None:
            deltas.append((name, cur.copy()))    # 起点相当于全零
        elif isinstance(cur, np.ndarray):
            deltas.append((name, cur - old))
        else:
            deltas.append((name, cur - old))     # 标量
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
    """父进程按块序应用一个块的 accum delta 和 slots diff。"""
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
            setattr(obj, attr, cur + delta)      # 标量
    for name, idx, vals in diffs:
        obj, attr = _resolve(name, body)
        getattr(obj, attr).flat[idx] = vals


def _par_worker(task):
    """worker：对块内每个 ij 按序调用注册的循环体，返回 delta/diff。"""
    kernel_name, ijs, args = task
    try:
        # worker 的 stdout 定向到 /dev/null，防止多进程往 FF.6 乱写
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
        # 错误不静默：traceback 文本返回，父进程原样抛出
        return (kernel_name, traceback.format_exc(), None, None)


def par_foreach(kernel_name, ijs, *args):
    """对活跃 ij 列表按序执行 kernel 循环体；NPAR>1 时多进程并行。"""
    kern = KERNELS[kernel_name]
    body = kern['body']
    if NPAR <= 1 or len(ijs) < 2:
        # 纯串行路径：不建 Pool，与提取前的逐 ij 循环逐位一致
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
    # pool.map 保持输入顺序 → 按块序（ij 升序）应用
    for kernel_name, err, deltas, diffs in results:
        if err is not None:
            raise RuntimeError(
                f'并行 worker 在 kernel {kernel_name!r} 中出错:\n{err}')
        _apply(kern, deltas, diffs)
