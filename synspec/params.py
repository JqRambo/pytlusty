# -*- coding: utf-8 -*-
"""
params.py — All PARAMETER constants of SYNSPEC.

Source: PARAMETER statements in PARAMS.FOR / LINDAT.FOR / WINCOM.FOR
(commented-out PARAMETERs are not included). Comments keep the original English.

Expression-type parameters (e.g. MOPAC = MFRQ, MI1 = MION0-1) are written directly as Python expressions.
Constants with dependencies are defined in dependency order; Fortran is case-insensitive, so canonical
uppercase spelling is used here (lowercase mfhtab/mtabth/mtabeh in the source are MFHTAB/MTABTH/MTABEH here).
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
MFHTAB   =     1000  # lowercase mfhtab in the source
MTABTH   =       10  # lowercase mtabth in the source
MTABEH   =       10  # lowercase mtabeh in the source

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
