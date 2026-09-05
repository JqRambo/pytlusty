# -*- coding: utf-8 -*-
"""
ff.py — teddy: 直接计算 FF (NLTE/L) 模型
=========================================

设置好下面的参数后运行:   python3 ff.py

FF 是完整非 LTE 模型, 必须从起始模型出发(TLUSTY 本身的要求):
在 START_MODEL 中给出起始模型名(不带后缀), 例如起始大气模型文件为
old.7, 就写 START_MODEL = 'old', 程序自动把 old.7 作为初始模型
(先在当前目录找, 再在 OUTPUT_DIR 中找)。

元素的离子能级表根据 ELEMENTS 的设置自动识别配置
(nlevs/ilast/ilvlin 等, 按 TLUSTY 官方标准算例), 不需要手工输入。

输出在 OUTPUT_DIR 中: FF.5, FF.6(日志), FF.7(模型), FF.9(收敛历史),
FF.14, FF.69, nst 以及全部 fort.* 文件; 不保留 data 链接。

并行: NPAR 设置频率循环(程序最热点)的多进程并行进程数;
NPAR=None 为串行, 与原版 TLUSTY 逐位一致; 并行只改变浮点求和顺序,
数值差异在 1e-16 量级, 建议 NPAR = os.cpu_count()。
"""

from driver import run_model

# ------------------------- 基本参数 -------------------------
TEFF = 22000.0          # 有效温度 [K]
LOGG = 4.0              # 表面重力 log g [cgs]
NFREAD = 2000           # 频率点数

# ------------------------- 元素与丰度 -------------------------
# mode: 2=显式 NLTE(能级表自动识别) / 1=隐式 LTE / 0=不考虑
# abn : 丰度(相对氢数密度比, 如 1.000000e-01); 0 = TLUSTY 内置太阳丰度
ELEMENTS = {
    'H':  {'mode': 2, 'abn': 0.000000e+00, 'modpf': 0},
    'He': {'mode': 2, 'abn': 1.000000e-01, 'modpf': 0},
    'C':  {'mode': 1, 'abn': 0.000000e+00, 'modpf': 0},
    'N':  {'mode': 1, 'abn': 0.000000e+00, 'modpf': 0},
    'O':  {'mode': 1, 'abn': 0.000000e+00, 'modpf': 0},
}

# ------------------------- nst 非标准参数 -------------------------
# 光深层数 ND 也在这里设置; 不需要 nst 就写 NST = None
NST = {'ND': 50, 'NLAMBD': 6, 'ITEK': 40, 'IACC': 40, 'NITER': 31}

# ------------------------- 起始模型与输出 -------------------------
START_MODEL = 'old'             # 起始模型名(不带 .7 后缀)
OUTPUT_DIR = './output/FF'

# ------------------------- 并行设置 -------------------------
NPAR = None  # 并行进程数; None=串行(与原版逐位一致), 建议 os.cpu_count()

# ------------------------- 执行 -------------------------
if __name__ == '__main__':
    ok, outdir = run_model(
        teff=TEFF, logg=LOGG, elements=ELEMENTS,
        nfread=NFREAD, model_type='FF', nst=NST,
        model='FF', output_dir=OUTPUT_DIR, start_model=START_MODEL,
        run=True, npar=NPAR)
    raise SystemExit(0 if ok else 1)
