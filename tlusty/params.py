# -*- coding: utf-8 -*-
"""
params.py — TLUSTY 全部 PARAMETER 常量。

来源：BASICS.FOR / ATOMIC.FOR / ITERAT.FOR / MODELQ.FOR / ODFPAR.FOR 中的
PARAMETER 语句（注释掉的 PARAMETER 不纳入）。注释保留英文原文。

注意：Fortran 整数除法为向零截断，如 MPAG = MLEVEL/6+1 = 1134//6+1 = 190。
有依赖关系的常量按依赖顺序定义。
"""

# ======================================================================
# BASICS.FOR
# ======================================================================

# Parameters that specify dimensions of arrays
MATOM   =    99  # max.num. of explicit atoms
MION    =   170  # max.num. of explicit ions
MLEVEL  =  1134  # max.num. of explicit levels
MLVEXP  =   233  # max.num. of explicit linearized levels
MTRANS  = 21000  # max.num. of all transitions
MDEPTH  =   100  # max.num. of depth points
MFREQ   = 135000 # max.num. of frequency points
MFREQP  = 220000 # working arrays of frequency
MFREQC  = 125000 # max.num. of freq.points in continuum
MFREX   =    54  # max.num. of linearized frequencies
MFREQL  = 25798  # max.num. of frequencies per line
MTOT    =   280  # max.num. of linearized parameters
MMU     =     6  # max.num. of angle points
MFIT    =   357  # max.num. of fit points (OP b-f c.s)
MITJ    =   380  # max.num. of overlapping transitions
MMCDW   =    26  # max.num. of levels with pseudocont.
MMER    =    12  # max.num. of merged levels
MVOIGT  =  8080  # max.num. of lines with Voigt profile
MZZ     =    10  # maximum charge for occup.prob. ions
NLMX    =    80  # highest hydrogenic level considered
MSMX    =     1  # size of matrix kept in memory in SOLVE
MFREQ1  = MFREQ  # =1 for ISPLIN<5; =MFREQ otherwise
MFRTAB  = 125000 # max.num. of freqeuncies in opac.table
MTABT   =    21  # max.number of temps in opac.table
MTABR   =    19  # max.number of densities in opac.table
MDEPTC  =     2  # max.num. of depth points (Compton)
MMUC    =     2  # max.num. of angle points (Compton)
MLEVE3  =     1  # =1 for diag.prec; =MLEVEL for trid.prec.
MLVEX3  =     1  # =1 for diag.oper.; =MLVEXP for tridiag.   .
MTRAN3  =     1  # =1 for diag.oper; =MTRANS for tridiag.
MCROSS  = MLEVEL + 5  # max.num. of b-f cross.secs.
MBF     = MLEVEL      # max.num. of b-f transitions
#  NEW VARIABLES YFMO Jun 2017
MCFIT   =    10  # max.num. of collision fit points
MXTCOL  =     3  # max.num. of collision types (CE, CP, CH)
MCORAT  = MTRANS # max.num. of col excitation transitions

# Basic physical constants
H     = 6.6256e-27       # Planck constant     h
BOLK  = 1.38054e-16      # Boltzmann constant  k
HK    = 4.79928144e-11   # h/k
CAS   = 2.997925e18      # light speed c (A/s)
EH    = 2.17853041e-11   # ionizaton energy of hydrogen
BN    = 1.4743e-2        # 2*h/c**3, c -light speed
SIGE  = 6.6516e-25       # Thomson scattering c-s
SIG4P = 4.5114062e-6     # Stefan-Boltzmann const/4pi
PI4H  = 1.8966e27        # 4pi/h
PCK   = 4.19168946e-10   # 4pi/c
HMASS = 1.67333e-24      # mass of hydrogen atom

# Basic mathematical constants
UN    = 1.0
HALF  = 0.5
TWO   = 2.0

# Unit number
IBUFF = 95

# ======================================================================
# ATOMIC.FOR
# ======================================================================

MPAG = MLEVEL // 6 + 1  # Fortran 整数除法：MLEVEL/6+1 = 1134//6+1 = 190
MTRPRD = 5

# ======================================================================
# ITERAT.FOR
# ======================================================================

MITER  = 200
MLAMBD = 100

# ======================================================================
# MODELQ.FOR
# ======================================================================

MLINH  = 78
MHT    = 7
MHE    = 20
MHWL   = 90
mfhtab = 1000
mtabth = 10
mtabeh = 10

# ======================================================================
# ODFPAR.FOR
# ======================================================================

MFODF  =     180
MHOD   =       3
MFRO   =  MFREQL
MDODF  =       3
MKULEV =    7000
MLINE  = 1140000
MCFE   = 7824000
