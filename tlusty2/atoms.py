# -*- coding: utf-8 -*-
"""
atoms.py — 元素周期表、太阳丰度与显式离子标准配置

数据来源（保证与 TLUSTY 程序本身的丰度原理完全一致）:
- 元素符号与太阳丰度: TLUSTY 内置表 (tlusty208.f 中 STATE 的 DATA D / DYP,
  前 30 个元素取自 Grevesse & Sauval 1998, 其余为程序自带值,
  丰度为数密度比 N(E)/N(H))。
- 显式离子标准配置: TLUSTY 官方测试算例
  tests/tlusty/bstar/BGA20000g400v2a.5 (bstar2006 网格的标准设置)。
"""

# Z=1..99 元素符号(与 TLUSTY DYP 一致)
SYMBOLS = [
    'H', 'He', 'Li', 'Be', 'B', 'C', 'N', 'O', 'F', 'Ne',
    'Na', 'Mg', 'Al', 'Si', 'P', 'S', 'Cl', 'Ar', 'K', 'Ca',
    'Sc', 'Ti', 'V', 'Cr', 'Mn', 'Fe', 'Co', 'Ni', 'Cu', 'Zn',
    'Ga', 'Ge', 'As', 'Se', 'Br', 'Kr', 'Rb', 'Sr', 'Y', 'Zr',
    'Nb', 'Mo', 'Tc', 'Ru', 'Rh', 'Pd', 'Ag', 'Cd', 'In', 'Sn',
    'Sb', 'Te', 'I', 'Xe', 'Cs', 'Ba', 'La', 'Ce', 'Pr', 'Nd',
    'Pm', 'Sm', 'Eu', 'Gd', 'Tb', 'Dy', 'Ho', 'Er', 'Tm', 'Yb',
    'Lu', 'Hf', 'Ta', 'W', 'Re', 'Os', 'Ir', 'Pt', 'Au', 'Hg',
    'Tl', 'Pb', 'Bi', 'Po', 'At', 'Rn', 'Fr', 'Ra', 'Ac', 'Th',
    'Pa', 'U', 'Np', 'Pu', 'Am', 'Cm', 'Bk', 'Cf', 'Es',
]

# 符号 -> 原子序数
Z_OF = {sym: z + 1 for z, sym in enumerate(SYMBOLS)}

# Z -> 太阳丰度(数密度比 N(E)/N(H), 与 TLUSTY 内置 DATA D 一致)
# 注: TLUSTY 中 .5 文件某元素 ABN=0 时即自动使用此太阳丰度。
SOLAR_ABUNDANCE = [
    1.0,          1.00e-1,      1.26e-11,     2.51e-11,     5.0e-10,
    3.31e-4,      8.32e-5,      6.76e-4,      3.16e-8,      1.20e-4,
    2.14e-6,      3.80e-5,      2.95e-6,      3.55e-5,      2.82e-7,
    2.14e-5,      3.16e-7,      2.52e-6,      1.32e-7,      2.29e-6,
    1.48e-9,      1.05e-7,      1.00e-8,      4.68e-7,      2.45e-7,
    3.16e-5,      8.32e-8,      1.78e-6,      1.62e-8,      3.98e-8,
    1.34896324e-09, 4.26579633e-09, 2.34422821e-10, 2.23872066e-09, 4.26579633e-10,
    1.69824373e-09, 2.51188699e-10, 8.51138173e-10, 1.65958702e-10, 4.07380181e-10,
    2.51188630e-11, 9.12010923e-11, 1.0e-24,  6.60693531e-11, 1.23026887e-11,
    5.01187291e-11, 1.73780087e-11, 5.75439927e-11, 6.60693440e-12, 1.38038460e-10,
    1.09647810e-11, 1.73780087e-10, 3.23593651e-11, 1.69824373e-10, 1.31825676e-11,
    1.62181025e-10, 1.58489337e-11, 4.07380293e-11, 6.02559549e-12, 2.95120943e-11,
    1.0e-24,      9.33254366e-12, 3.46736869e-12, 1.17489770e-11, 2.13796216e-12,
    1.41253747e-11, 3.16227767e-12, 8.91250917e-12, 1.34896287e-12, 8.91250917e-12,
    1.31825674e-12, 5.37031822e-12, 1.34896287e-12, 4.78630102e-12, 1.86208719e-12,
    2.39883290e-11, 2.34422885e-11, 4.78630036e-11, 6.76082952e-12, 1.23026887e-11,
    6.60693440e-12, 1.12201834e-10, 5.12861361e-12, 1.0e-24,      1.0e-24,
    1.0e-24,      1.0e-24,      1.0e-24,      1.0e-24,      1.20226443e-12,
    1.0e-24,      3.23593651e-13, 1.0e-24,      1.0e-24,      1.0e-24,
    1.0e-24,      1.0e-24,      1.0e-24,      1.0e-24,
]


def solar_abundance(symbol):
    """返回某元素的太阳丰度(数密度比 N(E)/N(H))。"""
    return SOLAR_ABUNDANCE[Z_OF[symbol] - 1]


# ---------------------------------------------------------------------------
# 显式离子标准配置(mode=2 元素用)
#
# 每个元素给出一个离子列表, 每条:
#   (iz, nlevs, filei, odf)
#     iz      电离度(0=中性)
#     nlevs   该离子在模型中用的能级数(与数据文件一致,
#             取自 bstar2006 标准算例或由数据文件数出)
#     filei   原子数据文件路径(相对运行目录, 即 'data/xxx');
#             最后一个一能级离子为 None(无文件, ilast=1)
#     odf     仅 Fe 这类用 ODF 的离子: (gam文件, lin文件, rap文件),
#             对应 .5 中 nonstd=-1 的三行附加记录; 其余为 None
#
# 最后一个离子自动按 ilast=1, nlevs=1 处理(裸核一能级离子)。
# ---------------------------------------------------------------------------
EXPLICIT_IONS = {
    'H':  [(0, 9,  'data/h1.dat', None),
           (1, 1,  None, None)],
    'He': [(0, 24, 'data/he1.dat', None),
           (1, 20, 'data/he2.dat', None),
           (2, 1,  None, None)],
    'C':  [(0, 40, 'data/c1.dat', None),
           (1, 22, 'data/c2.dat', None),
           (2, 46, 'data/c3_34+12lev.dat', None),
           (3, 25, 'data/c4.dat', None),
           (4, 1,  None, None)],
    'N':  [(0, 34, 'data/n1.dat', None),
           (1, 42, 'data/n2_32+10lev.dat', None),
           (2, 32, 'data/n3.dat', None),
           (3, 48, 'data/n4_34+14lev.dat', None),
           (4, 16, 'data/n5.dat', None),
           (5, 1,  None, None)],
    'O':  [(0, 33, 'data/o1_23+10lev.dat', None),
           (1, 48, 'data/o2_36+12lev.dat', None),
           (2, 41, 'data/o3_28+13lev.dat', None),
           (3, 39, 'data/o4.dat', None),
           (4, 6,  'data/o5.dat', None),
           (5, 1,  None, None)],
    'Ne': [(0, 35, 'data/ne1_23+12lev.dat', None),
           (1, 32, 'data/ne2_23+9lev.dat', None),
           (2, 34, 'data/ne3_22+12lev.dat', None),
           (3, 12, 'data/ne4.dat', None),
           (4, 1,  None, None)],
    'Mg': [(1, 25, 'data/mg2.dat', None),
           (2, 1,  None, None)],
    'Al': [(1, 29, 'data/al2_20+9lev.dat', None),
           (2, 23, 'data/al3_19+4lev.dat', None),
           (3, 1,  None, None)],
    'Si': [(1, 40, 'data/si2_36+4lev.dat', None),
           (2, 30, 'data/si3.dat', None),
           (3, 23, 'data/si4.dat', None),
           (4, 1,  None, None)],
    'P':  [(3, 14, 'data/p4.dat', None),
           (4, 17, 'data/p5.dat', None),
           (5, 1,  None, None)],
    'S':  [(1, 33, 'data/s2_23+10lev.dat', None),
           (2, 41, 'data/s3_29+12lev.dat', None),
           (3, 38, 'data/s4_33+5lev.dat', None),
           (4, 25, 'data/s5_20+5lev.dat', None),
           (5, 1,  None, None)],
    'Ar': [(0, 71, 'data/ar1_71lev-jK.dat', None),
           (1, 54, 'data/ar2_42+12lev.dat', None),
           (2, 44, 'data/ar3_27+17lev.dat', None),
           (3, 36, 'data/ar4_25+11lev.dat', None),
           (4, 1,  None, None)],
    # Fe 使用 ODF(非标准离子记录 nonstd=-1), 与 bstar2006 一致;
    # 注意: 使用 Fe 显式时建议在 NST 中设 ISPODF=1
    'Fe': [(1, 36, 'data/fe2va.dat',
            ('data/gf2601.gam', 'data/gf2601.lin', 'data/fe2p_14+11lev.rap')),
           (2, 50, 'data/fe3va.dat',
            ('data/gf2602.gam', 'data/gf2602.lin', 'data/fe3p_22+7lev.rap')),
           (3, 43, 'data/fe4va.dat',
            ('data/gf2603.gam', 'data/gf2603.lin', 'data/fe4p_21+11lev.rap')),
           (4, 42, 'data/fe5va.dat',
            ('data/gf2604.gam', 'data/gf2604.lin', 'data/fe5p_19+11lev.rap')),
           (5, 1,  None, None)],
}


def has_explicit(symbol):
    """该元素是否有现成的显式(mode=2)原子数据配置。"""
    return symbol in EXPLICIT_IONS
