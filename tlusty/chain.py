# -*- coding: utf-8 -*-
"""
chain.py — teddy: TT -> TF -> FF 完整链式计算
=============================================

设置好下面的参数后运行:   python3 chain.py

自动完成三步(模式与能级设置已固定, 无需设置):
  TT (LTE 灰大气, 从零开始算)      -> TT.7
  TF (NLTE/C, 以 TT.7 为起始模型)  -> TF.7
  FF (NLTE/L, 以 TF.7 为起始模型)  -> FF.7   最终模型

每个元素的离子能级表(nlevs/ilast/ilvlin 等)按 TLUSTY 官方标准算例
自动配置并随模式自动调整, 不需要作为输入。

所有输入输出都在 OUTPUT_DIR 中, 文件名按模式命名为 TT.5/TT.7、
TF.5/TF.7、FF.5/FF.7 等, 输出目录不保留 data 链接。
"""

from driver import run_chain

# ------------------------- 基本参数(只设一次) -------------------------
TEFF = 22000.0          # 有效温度 [K]
LOGG = 4.0              # 表面重力 log g [cgs]

# ------------------------- 元素与丰度(只设一次) -------------------------
# mode: 2=显式 NLTE(能级表自动配置) / 1=隐式 LTE / 0=不考虑
# abn : 丰度(相对氢数密度比, 如 1.000000e-01); 0 = TLUSTY 内置太阳丰度
ELEMENTS = {
    'H':  {'mode': 2, 'abn': 0.000000e+00, 'modpf': 0},
    'He': {'mode': 2, 'abn': 1.000000e-01, 'modpf': 0},
    'C':  {'mode': 1, 'abn': 0.000000e+00, 'modpf': 0},
    'N':  {'mode': 1, 'abn': 0.000000e+00, 'modpf': 0},
    'O':  {'mode': 1, 'abn': 0.000000e+00, 'modpf': 0},
}

# ------------------------- 三段各自的频率点数 -------------------------
NFREAD = {'TT': 50, 'TF': 50, 'FF': 2000}

# ------------------------- 三段各自的 nst 设置 -------------------------
# 每一步单独设置自己的 nst 参数(光深层数 ND 也在这里设置);
# 某一步不需要 nst 就写 None 或删掉该键
NST = {
    'TT': {'ND': 50},
    'TF': {'ND': 50},
    'FF': {'ND': 50, 'NLAMBD': 6, 'ITEK': 40, 'IACC': 40, 'NITER': 31},
}

# ------------------------- 输出路径 -------------------------
OUTPUT_DIR = './output/chain'

# ------------------------- 执行 -------------------------
if __name__ == '__main__':
    ok, outdir = run_chain(
        teff=TEFF, logg=LOGG, elements=ELEMENTS,
        nfread=NFREAD, nst=NST, output_dir=OUTPUT_DIR)
    if ok:
        print(f"[teddy] 链式计算全部完成, 最终模型: {outdir}/FF.7")
    raise SystemExit(0 if ok else 1)
