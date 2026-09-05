#!/bin/bash
# 把 fragments/chunkNN.py 按序拼接为 synspec54.py(改了分片后重新组装用)
cd "$(dirname "$0")"
{
cat <<'EOF'
# -*- coding: utf-8 -*-
"""
synspec54.py — SYNSPEC54 的 Python 逐行直译(物理公式、数值方法完全不变)

由 fragments/chunk01..17.py 按序拼接而成; 源文件: tlusty/synspec/synspec54.f
(23917 行固定格式 F77)。翻译约定见 CONVENTIONS.md。

运行方式: python3 -u synspec54.py < fort.5 > 日志
(unit 5=stdin 与 TLUSTY 相同的 .5; unit 55=fort.55 附加输入;
 unit 8=fort.8 模型大气; unit 19=fort.19 线列表)
"""
import math, sys
import numpy as np
from params import *
import commons as C
from fortran import *

EOF
cat fragments/chunk01.py fragments/chunk02.py fragments/chunk03.py fragments/chunk04.py fragments/chunk05.py fragments/chunk06.py fragments/chunk07.py fragments/chunk08.py fragments/chunk09.py fragments/chunk10.py fragments/chunk11.py fragments/chunk12.py fragments/chunk13.py fragments/chunk14.py fragments/chunk15.py fragments/chunk16.py fragments/chunk17.py
cat <<'EOF'


if __name__ == '__main__':
    main()
EOF
} > synspec54.py
python3 -m py_compile synspec54.py && echo ASSEMBLED_OK
