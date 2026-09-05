# -*- coding: utf-8 -*-
"""
_writeset.py — 写集合实证核验工具（TLUSTY_WSET=1 时由 parmap 调用）
==================================================================

用途：在 kernel 的 ij 循环前后对 vars(C) 中所有 numpy 数组和标量做
快照/对比，把实际被写过的变量名（按 kernel 去重累积）追加写到工作目录
wset.log，用来交叉核对 parmap.KERNELS 注册表的 accum/slots 名单。

说明：快照在 kernel 一次调用（整个 ij 循环）的入口/出口各做一次，
得到该次调用写集的并集——这正是核对注册表所需的信息；逐 ij 对比
得到的是同一个并集，但开销大得多，故采用入口/出口对比。
函数内恢复净零的写入（如 opacf1 的 iprcrs 分支对 POPUL/ABTRA 的
临时修改、rtefr1 对 ISPLIN 的保存/恢复）不会出现在结果里——
这正符合"对 worker 无净效应"的判定。
"""

import os

import numpy as np

import commons as C

LOG = os.path.abspath('wset.log')

# {kernel: 已记录的写变量名集合}（去重累积；worker 里是 fork 时的父进程副本，
# worker 新发现的直接追加到 wset.log）
_logged = {}
_switches_logged = set()

_SWITCHES = ['IFPREC', 'ifprec', 'IRDER', 'IFALI', 'IOPTAB', 'IDISK', 'icompt',
             'ILMCOR', 'ILASCT', 'ISPODF', 'iprcrs', 'IFDIEL', 'IFRYB',
             'IFPRAD', 'IFPRD', 'ISPLIN', 'ILPSCT', 'NDRE', 'IOPADD', 'INMOD',
             'IFPOPR', 'ITER', 'ILAM', 'NFREQ', 'NFREQE', 'ND', 'NTRANS']


def append_log(lines):
    """把若干行追加到 wset.log（worker 也直接调用，O_APPEND 短行足够安全）。"""
    if not lines:
        return
    with open(LOG, 'a') as f:
        for line in lines:
            f.write(line + '\n')


def log_switches(kernel):
    """每个 kernel 首次调用时把关键开关的运行时值写进 wset.log。"""
    if kernel in _switches_logged:
        return
    _switches_logged.add(kernel)
    kv = ' '.join(f'{s}={getattr(C, s, "?")}' for s in _SWITCHES)
    append_log([f'# switches {kernel}: {kv}'])


def take_snap(kernel):
    """对 vars(C) 中尚未记录为已写的数组/标量做快照。"""
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
    """对比快照，返回新发现的被写变量名列表（并累积进去重集合）。"""
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
    # 循环中新懒分配出来的数组：与"刚分配的值"（全零/空串）对比，
    # 不同才算被写（排除只读触发懒分配的误报，如 DABM1/DEMM1）
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
