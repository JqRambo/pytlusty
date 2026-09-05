# -*- coding: utf-8 -*-
"""
params.py — SYNSPEC 全部 PARAMETER 常量。

来源：PARAMS.FOR / LINDAT.FOR / WINCOM.FOR 中的 PARAMETER 语句
（注释掉的 PARAMETER 不纳入）。注释保留英文原文。

表达式型参数（如 MOPAC = MFRQ、MI1 = MION0-1）直接写成 Python 表达式。
有依赖关系的常量按依赖顺序定义；Fortran 大小写不敏感，此处统一用规范大写拼写
（源码中小写的 mfhtab/mtabth/mtabeh 在此记为 MFHTAB/MTABTH/MTABEH）。
"""

# ======================================================================
# PARAMS.FOR
# ======================================================================

# Parameters that specify dimensions of arrays
MATEX    =       30
MIOEX    =       90
MLEVEL   =     1650
MDEPTH   =      100
MDEPF    =      500
MFREQ    =     2000
MFREQC   =     2000
MFRQ     =     2000
MOPAC    = MFRQ
MMU      =       20
MCROSS   = MLEVEL
MFIT     =     1650
MFCRA    =     1200
MTRAD    =        3
MATOM    =       99
MATOMBIG =       99
MION     =       90
MION0    =        9
MMOLEC   =      500
MPHOT    =       10
MZZ      =        2
MMER     =        2
NLMX     =       80
MI1      = MION0 - 1
MLINH    =       78
MHT      =        7
MHE      =       20
MHWL     =       55
MFGRID   =   100000
MTTAB    =       21
MRTAB    =       20
MSFTAB   =  6000000
MFHTAB   =     1000  # 源码小写 mfhtab
MTABTH   =       10  # 源码小写 mtabth
MTABEH   =       10  # 源码小写 mtabeh

# Basic physical constants
H     = 6.6256e-27       # Planck constant     h
CL    = 2.997925e10      # light speed c (cm/s)
BOLK  = 1.38054e-16      # Boltzmann constant  k
HK    = 4.79928144e-11   # h/k
EH    = 2.17853041e-11   # ionizaton energy of hydrogen
BN    = 1.4743e-2        # 2*h/c**3, c -light speed
SIGE  = 6.6516e-25       # Thomson scattering c-s
PI4H  = 1.8966e27        # 4pi/h
HMASS = 1.67333e-24      # mass of hydrogen atom

# Unit number
IBUFF = 95

# ======================================================================
# LINDAT.FOR
# ======================================================================

MLIN0   =  1200000
MGRIEM  =       10
MNLT    =     2000
MSPHE2  =       20
MLIN    =   190000
MPRF    = MLIN0
MLINM0  =  9000000
MLINM   =  1000000
MMLIST  =        3

# ======================================================================
# WINCOM.FOR
# ======================================================================

MRCORE = 20
MKU    = MDEPTH + MRCORE
MEXT   = MKU
