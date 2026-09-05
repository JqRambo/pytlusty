# -*- coding: utf-8 -*-
"""
fortran.py — Fortran 运行时辅助函数。

提供 Fortran 77 内建函数语义（整数除法、MOD、DINT、DNINT、DSIGN、字符串比较）
以及文件单元（OPEN/READ/WRITE/CLOSE）和无格式顺序临时文件（SCRATCH）的模拟。
"""

import math
import sys

import numpy as np

# ---------------------------------------------------------------- 内建函数

def idiv(a, b):
    """Fortran 整数除法 I/J：向零截断（与 Python // 的向下取整不同）。"""
    q = abs(a) // abs(b)
    if (a < 0) != (b < 0):
        q = -q
    return q


def imod(a, b):
    """Fortran MOD(I,J)：余数符号与被除数一致（向零截断语义）。"""
    return a - idiv(a, b) * b


def dint(x):
    """Fortran DINT(X)：截断取整（向零），返回浮点数。"""
    return float(math.trunc(x))


def dnint(x):
    """Fortran DNINT(X)：四舍五入到最近整数，半进时远离零，返回浮点数。"""
    if x >= 0:
        return float(math.floor(x + 0.5))
    return float(math.ceil(x - 0.5))


def dsign(a, b):
    """Fortran DSIGN(A,B)：取 |a| 并赋予 b 的符号（b>=0 为正）。"""
    return abs(a) if b >= 0 else -abs(a)


def feq(a, b):
    """Fortran 字符串相等比较：忽略尾部空格（rstrip 后比较）。"""
    return str(a).rstrip() == str(b).rstrip()


def flog(x):
    """Fortran 语义的 LOG：log(0)=-inf、log(负数)=nan（IEEE，不 trap）。

    Python 的 math.log 会抛 ValueError，而 Fortran 默认继续执行。
    """
    if x > 0.0:
        return math.log(x)
    if x == 0.0:
        return float("-inf")
    return float("nan")


# ---------------------------------------------------------------- 文件单元

funits = {}


def open_unit(unit, filename=None, mode='r', scratch=False):
    """对应 Fortran OPEN(UNIT=unit, FILE=filename, ...)。

    scratch=True 对应 STATUS='SCRATCH'（用 ScratchFile 模拟无格式临时文件）。
    """
    if scratch:
        fh = ScratchFile()
    else:
        fh = open(filename, mode)
    funits[unit] = fh
    return fh


def _implicit_open(unit, mode):
    """Fortran 隐式打开：未 OPEN 的单元首次 I/O 时连接 fort.<unit> 文件。

    读模式下文件不存在时抛 EOFError：Fortran 中隐式 OPEN 失败属于
    ERR=/END= 可捕获的错误条件，这里统一按 EOF 分支处理。
    """
    try:
        fh = open("fort.%d" % unit, mode)
    except FileNotFoundError:
        if "r" in mode:
            raise EOFError("unit %d: fort.%d 不存在（隐式 OPEN 失败）"
                           % (unit, unit))
        raise
    funits[unit] = fh
    return fh


def read_line(unit):
    """从文件单元读一行，返回不含换行符的 str；EOF 时抛 EOFError。"""
    fh = funits.get(unit)
    if fh is None:
        fh = _implicit_open(unit, "r")
    line = fh.readline()
    if line == "":
        raise EOFError("unit %d: end of file" % unit)
    return line.rstrip("\n")


def write_line(unit, s):
    """向文件单元写一行（自动追加换行符），对应 Fortran 格式 WRITE。"""
    fh = funits.get(unit)
    if fh is None:
        fh = _implicit_open(unit, "w")
    fh.write(str(s) + "\n")


def close_unit(unit):
    """对应 Fortran CLOSE(UNIT=unit)：关闭并从 funits 中移除。"""
    fh = funits.pop(unit)
    if hasattr(fh, "close"):
        fh.close()


def read_stdin_line():
    """对应 Fortran READ(5,...) / READ(*,...)：从标准输入读一行；
    遇到 EOF 时抛 SystemExit（模拟 Fortran 程序读不到输入而终止）。"""
    line = sys.stdin.readline()
    if line == "":
        raise SystemExit("stdin EOF")
    return line.rstrip("\n")


# ---------------------------------------------------------------- 临时文件

class ScratchFile:
    """模拟 Fortran 无格式顺序临时文件（STATUS='SCRATCH'）。

    每条 WRITE 存一个记录；numpy 数组在写入时用 np.copy 做快照，
    读出时返回写时的快照本身（与 Fortran 无格式读语义一致）。
    """

    def __init__(self):
        self._records = []
        self._pos = 0

    def write(self, *vals):
        """写一条记录：WRITE(u) A,B,... ；数组自动快照。

        若读/写指针不在记录末尾，先截断其后旧记录再追加——模拟 Fortran
        顺序写的覆盖语义（在当前位置写入会使原文件中其后的内容失效）。
        """
        snap = tuple(np.copy(v) if isinstance(v, np.ndarray) else v
                     for v in vals)
        if self._pos < len(self._records):
            del self._records[self._pos:]
        self._records.append(snap)
        self._pos += 1

    def read(self):
        """读下一条记录：单值返回该值，多值返回元组；数组返回快照本身。"""
        if self._pos >= len(self._records):
            raise EOFError("scratch file: read past end of records")
        rec = self._records[self._pos]
        self._pos += 1
        return rec[0] if len(rec) == 1 else rec

    def rewind(self):
        """对应 Fortran REWIND：读指针回到开头。"""
        self._pos = 0

    def backspace(self):
        """对应 Fortran BACKSPACE：读/写指针后退一条记录（开头处则不动）。"""
        if self._pos > 0:
            self._pos -= 1

    def endfile(self):
        """对应 Fortran ENDFILE：截断当前位置之后的所有记录。

        近似语义：Fortran 的 ENDFILE 是在当前位置写一个文件结束标记，
        之后再 BACKSPACE/REWIND 仍可读前面的记录；这里直接丢弃尾部记录，
        对本程序的 scratch 用法（写满→REWIND→读）足够。
        """
        del self._records[self._pos:]


def rewind_unit(unit):
    """对应 Fortran REWIND unit：普通文件 seek(0)，scratch 调 rewind()。

    未打开的单元：Fortran 会隐式连接 fort.<unit>；这里以 w+ 打开
    （截断旧文件，因为随后的写就是从文件开头重写全部内容）。
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
    """对应 Fortran ENDFILE unit。

    普通文件：截断到当前位置（file.truncate()）；scratch：截断记录列表。
    近似语义见 ScratchFile.endfile 的注释。
    """
    fh = funits.get(unit)
    if isinstance(fh, ScratchFile):
        fh.endfile()
    elif fh is not None:
        # r+ 模式下读操作后必须先 flush 再 truncate，否则截断不生效
        fh.flush()
        fh.truncate(fh.tell())
    elif unit in scratch:
        scratch[unit].endfile()
    else:
        raise KeyError("unit %d 未打开" % unit)


# 单元 91/92/93 是无格式临时文件（STATUS='SCRATCH'）
scratch = {91: ScratchFile(), 92: ScratchFile(), 93: ScratchFile()}
