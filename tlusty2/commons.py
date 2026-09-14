# -*- coding: utf-8 -*-
"""
commons.py — lazy-allocation namespace for all TLUSTY COMMON block variables.

Covers all COMMON blocks from the 7 include files (BASICS.FOR / ATOMIC.FOR /
ARRAY1.FOR / ITERAT.FOR / MODELQ.FOR / ODFPAR.FOR / ALIPAR.FOR),
including the unnamed COMMON in ARRAY1.FOR.

Usage:
    import commons as C
    C.ABSO[i] = 1.0      # array: allocated on first access to the Fortran declared dims (+1 per dim)
    C.NATOM = 5          # scalar: first access returns default 0 / 0.0 / False / ''

Rules:
- Keep Fortran 1-based indexing: each array dimension gets one extra element; index 0 is unused.
- Types follow IMPLIC.FOR: IMPLICIT REAL*8 (A-H,O-Z), LOGICAL*1 (L),
  i.e. leading letter I-N -> int64, A-H/O-Z -> float64, L -> bool; explicit declarations win:
  INTEGER*2 -> np.int16, REAL*4 -> np.float32, CHARACTER*n -> dtype=object (initial value '').
- DECLS records {name: (kind, dimension-expression tuple, dtype)}; the module-level __getattr__ (PEP 562)
  allocates on first access accordingly and caches into module globals(); later accesses are normal attributes.
- PARAMETER names in dimension expressions come from params.py (Fortran is case-insensitive; canonical spelling used here).
"""

import numpy as np

import params as P

# {name: (kind "array"/"scalar", (dimension expression, ...), dtype)}
# Each comment notes the source: file name + COMMON block name + original dimension declaration.
DECLS = {
    # ===== BASICS.FOR : COMMON /BASNUM/ =====
    "NATOM": ("scalar", (), "np.int64"),  # BASICS.FOR /BASNUM/ NATOM
    "NION": ("scalar", (), "np.int64"),  # BASICS.FOR /BASNUM/ NION
    "NLEVEL": ("scalar", (), "np.int64"),  # BASICS.FOR /BASNUM/ NLEVEL
    "NTRANS": ("scalar", (), "np.int64"),  # BASICS.FOR /BASNUM/ NTRANS
    "ND": ("scalar", (), "np.int64"),  # BASICS.FOR /BASNUM/ ND
    "NFREQ": ("scalar", (), "np.int64"),  # BASICS.FOR /BASNUM/ NFREQ
    "NFREQC": ("scalar", (), "np.int64"),  # BASICS.FOR /BASNUM/ NFREQC
    "NFREQE": ("scalar", (), "np.int64"),  # BASICS.FOR /BASNUM/ NFREQE
    "IOPTAB": ("scalar", (), "np.int64"),  # BASICS.FOR /BASNUM/ IOPTAB
    "IDISK": ("scalar", (), "np.int64"),  # BASICS.FOR /BASNUM/ IDISK
    "IZSCAL": ("scalar", (), "np.int64"),  # BASICS.FOR /BASNUM/ IZSCAL
    "IDMFIX": ("scalar", (), "np.int64"),  # BASICS.FOR /BASNUM/ IDMFIX
    "IHESO6": ("scalar", (), "np.int64"),  # BASICS.FOR /BASNUM/ IHESO6
    "IFMOL": ("scalar", (), "np.int64"),  # BASICS.FOR /BASNUM/ IFMOL
    "IFENTR": ("scalar", (), "np.int64"),  # BASICS.FOR /BASNUM/ IFENTR
    "NFREQL": ("scalar", (), "np.int64"),  # BASICS.FOR /BASNUM/ NFREQL
    "NLEV0": ("scalar", (), "np.int64"),  # BASICS.FOR /BASNUM/ NLEV0
    "ICOLHN": ("scalar", (), "np.int64"),  # BASICS.FOR /BASNUM/ ICOLHN
    "IOSCOR": ("scalar", (), "np.int64"),  # BASICS.FOR /BASNUM/ IOSCOR
    "ILGDER": ("scalar", (), "np.int64"),  # BASICS.FOR /BASNUM/ ILGDER
    "IFRYB": ("scalar", (), "np.int64"),  # BASICS.FOR /BASNUM/ IFRYB
    "IFRSET": ("scalar", (), "np.int64"),  # BASICS.FOR /BASNUM/ IFRSET
    "NFREAD": ("scalar", (), "np.int64"),  # BASICS.FOR /BASNUM/ NFREAD
    "NELSC": ("scalar", (), "np.int64"),  # BASICS.FOR /BASNUM/ NELSC
    "NTRANC": ("scalar", (), "np.int64"),  # BASICS.FOR /BASNUM/ NTRANC
    "IOVER": ("scalar", (), "np.int64"),  # BASICS.FOR /BASNUM/ IOVER
    "JALI": ("scalar", (), "np.int64"),  # BASICS.FOR /BASNUM/ JALI
    "IBC": ("scalar", (), "np.int64"),  # BASICS.FOR /BASNUM/ IBC
    "IUBC": ("scalar", (), "np.int64"),  # BASICS.FOR /BASNUM/ IUBC
    "INTENS": ("scalar", (), "np.int64"),  # BASICS.FOR /BASNUM/ INTENS
    "IRDER": ("scalar", (), "np.int64"),  # BASICS.FOR /BASNUM/ IRDER
    "ILMCOR": ("scalar", (), "np.int64"),  # BASICS.FOR /BASNUM/ ILMCOR
    "IFDIEL": ("scalar", (), "np.int64"),  # BASICS.FOR /BASNUM/ IFDIEL
    "IFALIH": ("scalar", (), "np.int64"),  # BASICS.FOR /BASNUM/ IFALIH
    "IFTENE": ("scalar", (), "np.int64"),  # BASICS.FOR /BASNUM/ IFTENE
    "ITNDRE": ("scalar", (), "np.int64"),  # BASICS.FOR /BASNUM/ ITNDRE
    "ILPSCT": ("scalar", (), "np.int64"),  # BASICS.FOR /BASNUM/ ILPSCT
    "ILASCT": ("scalar", (), "np.int64"),  # BASICS.FOR /BASNUM/ ILASCT
    "IRTE": ("scalar", (), "np.int64"),  # BASICS.FOR /BASNUM/ IRTE
    "IDLTE": ("scalar", (), "np.int64"),  # BASICS.FOR /BASNUM/ IDLTE
    "IBFINT": ("scalar", (), "np.int64"),  # BASICS.FOR /BASNUM/ IBFINT
    "INTRPL": ("scalar", (), "np.int64"),  # BASICS.FOR /BASNUM/ INTRPL
    "ICHANG": ("scalar", (), "np.int64"),  # BASICS.FOR /BASNUM/ ICHANG
    "NATOMS": ("scalar", (), "np.int64"),  # BASICS.FOR /BASNUM/ NATOMS
    "IPSLTE": ("scalar", (), "np.int64"),  # BASICS.FOR /BASNUM/ IPSLTE
    "ISPODF": ("scalar", (), "np.int64"),  # BASICS.FOR /BASNUM/ ISPODF
    "ITLUCY": ("scalar", (), "np.int64"),  # BASICS.FOR /BASNUM/ ITLUCY
    "NRETC": ("scalar", (), "np.int64"),  # BASICS.FOR /BASNUM/ NRETC
    "IFRAYL": ("scalar", (), "np.int64"),  # BASICS.FOR /BASNUM/ IFRAYL
    "IFPRAD": ("scalar", (), "np.int64"),  # BASICS.FOR /BASNUM/ IFPRAD

    # ===== BASICS.FOR : COMMON /INPPAR/ =====
    "TEFF": ("scalar", (), "np.float64"),  # BASICS.FOR /INPPAR/ TEFF
    "GRAV": ("scalar", (), "np.float64"),  # BASICS.FOR /INPPAR/ GRAV
    "YTOT": ("array", ("MDEPTH", ), "np.float64"),  # BASICS.FOR /INPPAR/ YTOT(MDEPTH)
    "WMM": ("array", ("MDEPTH", ), "np.float64"),  # BASICS.FOR /INPPAR/ WMM(MDEPTH)
    "WMY": ("array", ("MDEPTH", ), "np.float64"),  # BASICS.FOR /INPPAR/ WMY(MDEPTH)
    "TMOLIM": ("scalar", (), "np.float64"),  # BASICS.FOR /INPPAR/ TMOLIM
    "xmstar": ("scalar", (), "np.float64"),  # BASICS.FOR /INPPAR/ xmstar
    "xmdot": ("scalar", (), "np.float64"),  # BASICS.FOR /INPPAR/ xmdot
    "rstar": ("scalar", (), "np.float64"),  # BASICS.FOR /INPPAR/ rstar
    "alpha0": ("scalar", (), "np.float64"),  # BASICS.FOR /INPPAR/ alpha0
    "reynum": ("scalar", (), "np.float64"),  # BASICS.FOR /INPPAR/ reynum
    "QGRAV": ("scalar", (), "np.float64"),  # BASICS.FOR /INPPAR/ QGRAV
    "EDISC": ("scalar", (), "np.float64"),  # BASICS.FOR /INPPAR/ EDISC
    "DZETA": ("scalar", (), "np.float64"),  # BASICS.FOR /INPPAR/ DZETA
    "RELDST": ("scalar", (), "np.float64"),  # BASICS.FOR /INPPAR/ RELDST
    "visc": ("scalar", (), "np.float64"),  # BASICS.FOR /INPPAR/ visc
    "zeta0": ("scalar", (), "np.float64"),  # BASICS.FOR /INPPAR/ zeta0
    "zeta1": ("scalar", (), "np.float64"),  # BASICS.FOR /INPPAR/ zeta1
    "dmvisc": ("scalar", (), "np.float64"),  # BASICS.FOR /INPPAR/ dmvisc
    "fractv": ("scalar", (), "np.float64"),  # BASICS.FOR /INPPAR/ fractv
    "omeg32": ("scalar", (), "np.float64"),  # BASICS.FOR /INPPAR/ omeg32
    "wbarm": ("scalar", (), "np.float64"),  # BASICS.FOR /INPPAR/ wbarm
    "wbar": ("scalar", (), "np.float64"),  # BASICS.FOR /INPPAR/ wbar
    "alphav": ("scalar", (), "np.float64"),  # BASICS.FOR /INPPAR/ alphav
    "pgas0": ("scalar", (), "np.float64"),  # BASICS.FOR /INPPAR/ pgas0
    "bergfc": ("scalar", (), "np.float64"),  # BASICS.FOR /INPPAR/ bergfc
    "cutlym": ("scalar", (), "np.float64"),  # BASICS.FOR /INPPAR/ cutlym
    "cutbal": ("scalar", (), "np.float64"),  # BASICS.FOR /INPPAR/ cutbal
    "ISPLIN": ("scalar", (), "np.int64"),  # BASICS.FOR /INPPAR/ ISPLIN
    "IRSPLT": ("scalar", (), "np.int64"),  # BASICS.FOR /INPPAR/ IRSPLT
    "ivisc": ("scalar", (), "np.int64"),  # BASICS.FOR /INPPAR/ ivisc
    "ibche": ("scalar", (), "np.int64"),  # BASICS.FOR /INPPAR/ ibche
    "LTE": ("scalar", (), "bool"),  # BASICS.FOR /INPPAR/ LTE
    "LTGREY": ("scalar", (), "bool"),  # BASICS.FOR /INPPAR/ LTGREY
    "LCHC": ("scalar", (), "bool"),  # BASICS.FOR /INPPAR/ LCHC
    "LRESC": ("scalar", (), "bool"),  # BASICS.FOR /INPPAR/ LRESC

    # ===== BASICS.FOR : COMMON /MATKEY/ =====
    "NN": ("scalar", (), "np.int64"),  # BASICS.FOR /MATKEY/ NN
    "NN0": ("scalar", (), "np.int64"),  # BASICS.FOR /MATKEY/ NN0
    "INHE": ("scalar", (), "np.int64"),  # BASICS.FOR /MATKEY/ INHE
    "INRE": ("scalar", (), "np.int64"),  # BASICS.FOR /MATKEY/ INRE
    "INPC": ("scalar", (), "np.int64"),  # BASICS.FOR /MATKEY/ INPC
    "INSE": ("scalar", (), "np.int64"),  # BASICS.FOR /MATKEY/ INSE
    "INZD": ("scalar", (), "np.int64"),  # BASICS.FOR /MATKEY/ INZD
    "INMP": ("scalar", (), "np.int64"),  # BASICS.FOR /MATKEY/ INMP
    "NDRE": ("scalar", (), "np.int64"),  # BASICS.FOR /MATKEY/ NDRE
    "insel": ("scalar", (), "np.int64"),  # BASICS.FOR /MATKEY/ insel

    # ===== BASICS.FOR : COMMON /FIXDEN/ =====
    "IFIXDE": ("scalar", (), "np.int64"),  # BASICS.FOR /FIXDEN/ IFIXDE

    # ===== BASICS.FOR : COMMON /INVINT/ =====
    "XI2": ("array", ("NLMX", ), "np.float64"),  # BASICS.FOR /INVINT/ XI2(NLMX)
    "XI3": ("array", ("NLMX", ), "np.float64"),  # BASICS.FOR /INVINT/ XI3(NLMX)

    # ===== BASICS.FOR : COMMON /RUNKEY/ =====
    "CHMAX": ("scalar", (), "np.float64"),  # BASICS.FOR /RUNKEY/ CHMAX
    "ITER": ("scalar", (), "np.int64"),  # BASICS.FOR /RUNKEY/ ITER
    "NITER": ("scalar", (), "np.int64"),  # BASICS.FOR /RUNKEY/ NITER
    "NITZER": ("scalar", (), "np.int64"),  # BASICS.FOR /RUNKEY/ NITZER
    "INIT": ("scalar", (), "np.int64"),  # BASICS.FOR /RUNKEY/ INIT
    "LAC2": ("scalar", (), "bool"),  # BASICS.FOR /RUNKEY/ LAC2
    "LFIN": ("scalar", (), "bool"),  # BASICS.FOR /RUNKEY/ LFIN
    "CHMX": ("scalar", (), "np.float64"),  # Python addition: max relative change of the current iteration (written by SOLVE/SOLVES/RYBSOL, for main progress display)

    # ===== BASICS.FOR : COMMON /CONKEY/ =====
    "HMIX0": ("scalar", (), "np.float64"),  # BASICS.FOR /CONKEY/ HMIX0
    "crflim": ("scalar", (), "np.float64"),  # BASICS.FOR /CONKEY/ crflim
    "NCONIT": ("scalar", (), "np.int64"),  # BASICS.FOR /CONKEY/ NCONIT
    "ICONV": ("scalar", (), "np.int64"),  # BASICS.FOR /CONKEY/ ICONV
    "INDL": ("scalar", (), "np.int64"),  # BASICS.FOR /CONKEY/ INDL
    "IPRESS": ("scalar", (), "np.int64"),  # BASICS.FOR /CONKEY/ IPRESS
    "ITEMP": ("scalar", (), "np.int64"),  # BASICS.FOR /CONKEY/ ITEMP
    "ICBEG": ("scalar", (), "np.int64"),  # BASICS.FOR /CONKEY/ ICBEG
    "itmcor": ("scalar", (), "np.int64"),  # BASICS.FOR /CONKEY/ itmcor
    "iconre": ("scalar", (), "np.int64"),  # BASICS.FOR /CONKEY/ iconre
    "ideepc": ("scalar", (), "np.int64"),  # BASICS.FOR /CONKEY/ ideepc
    "ndcgap": ("scalar", (), "np.int64"),  # BASICS.FOR /CONKEY/ ndcgap
    "IDCONZ": ("scalar", (), "np.int64"),  # BASICS.FOR /CONKEY/ IDCONZ

    # ===== BASICS.FOR : COMMON /OPCKEY/ =====
    "NCON": ("scalar", (), "np.int64"),  # BASICS.FOR /OPCKEY/ NCON
    "IOPHL1": ("scalar", (), "np.int64"),  # BASICS.FOR /OPCKEY/ IOPHL1
    "IOPHL2": ("scalar", (), "np.int64"),  # BASICS.FOR /OPCKEY/ IOPHL2
    "IPHE2C": ("scalar", (), "np.int64"),  # BASICS.FOR /OPCKEY/ IPHE2C
    "IFMOFF": ("scalar", (), "np.int64"),  # BASICS.FOR /OPCKEY/ IFMOFF

    # ===== BASICS.FOR : COMMON /PRINTS/ =====
    "IPRINT": ("scalar", (), "np.int64"),  # BASICS.FOR /PRINTS/ IPRINT
    "IPRING": ("scalar", (), "np.int64"),  # BASICS.FOR /PRINTS/ IPRING
    "IPRIND": ("scalar", (), "np.int64"),  # BASICS.FOR /PRINTS/ IPRIND
    "IPRINP": ("scalar", (), "np.int64"),  # BASICS.FOR /PRINTS/ IPRINP
    "ICOOLP": ("scalar", (), "np.int64"),  # BASICS.FOR /PRINTS/ ICOOLP
    "ICHCKP": ("scalar", (), "np.int64"),  # BASICS.FOR /PRINTS/ ICHCKP
    "IPOPAC": ("scalar", (), "np.int64"),  # BASICS.FOR /PRINTS/ IPOPAC
    "IPRINI": ("scalar", (), "np.int64"),  # BASICS.FOR /PRINTS/ IPRINI

    # ===== BASICS.FOR : COMMON /PSILIM/ =====
    "DPSILG": ("scalar", (), "np.float64"),  # BASICS.FOR /PSILIM/ DPSILG
    "DPSILT": ("scalar", (), "np.float64"),  # BASICS.FOR /PSILIM/ DPSILT
    "DPSILN": ("scalar", (), "np.float64"),  # BASICS.FOR /PSILIM/ DPSILN
    "DPSILD": ("scalar", (), "np.float64"),  # BASICS.FOR /PSILIM/ DPSILD

    # ===== BASICS.FOR : COMMON /CENTRL/ =====
    "ZND": ("scalar", (), "np.float64"),  # BASICS.FOR /CENTRL/ ZND
    "IFZ0": ("scalar", (), "np.int64"),  # BASICS.FOR /CENTRL/ IFZ0

    # ===== BASICS.FOR : COMMON /OPCPAR/ =====
    "IOPADD": ("scalar", (), "np.int64"),  # BASICS.FOR /OPCPAR/ IOPADD
    "IOPHMI": ("scalar", (), "np.int64"),  # BASICS.FOR /OPCPAR/ IOPHMI
    "IOPH2P": ("scalar", (), "np.int64"),  # BASICS.FOR /OPCPAR/ IOPH2P
    "IOPHEM": ("scalar", (), "np.int64"),  # BASICS.FOR /OPCPAR/ IOPHEM
    "IOPCH": ("scalar", (), "np.int64"),  # BASICS.FOR /OPCPAR/ IOPCH
    "IOPOH": ("scalar", (), "np.int64"),  # BASICS.FOR /OPCPAR/ IOPOH
    "IOPH2M": ("scalar", (), "np.int64"),  # BASICS.FOR /OPCPAR/ IOPH2M
    "IOH2H2": ("scalar", (), "np.int64"),  # BASICS.FOR /OPCPAR/ IOH2H2
    "IOH2HE": ("scalar", (), "np.int64"),  # BASICS.FOR /OPCPAR/ IOH2HE
    "IOH2H": ("scalar", (), "np.int64"),  # BASICS.FOR /OPCPAR/ IOH2H
    "IOHHE": ("scalar", (), "np.int64"),  # BASICS.FOR /OPCPAR/ IOHHE
    "IOPHLI": ("scalar", (), "np.int64"),  # BASICS.FOR /OPCPAR/ IOPHLI
    "IRSCT": ("scalar", (), "np.int64"),  # BASICS.FOR /OPCPAR/ IRSCT
    "IRSCHE": ("scalar", (), "np.int64"),  # BASICS.FOR /OPCPAR/ IRSCHE
    "IRSCH2": ("scalar", (), "np.int64"),  # BASICS.FOR /OPCPAR/ IRSCH2
    "KEEPOP": ("scalar", (), "np.int64"),  # BASICS.FOR /OPCPAR/ KEEPOP
    "IOPOLD": ("scalar", (), "np.int64"),  # BASICS.FOR /OPCPAR/ IOPOLD

    # ===== BASICS.FOR : COMMON /ANGLES/ =====
    "AMU": ("array", ("MMU", ), "np.float64"),  # BASICS.FOR /ANGLES/ AMU(MMU)
    "WTMU": ("array", ("MMU", ), "np.float64"),  # BASICS.FOR /ANGLES/ WTMU(MMU)
    "FMU": ("array", ("MMU", ), "np.float64"),  # BASICS.FOR /ANGLES/ FMU(MMU)
    "NMU": ("scalar", (), "np.int64"),  # BASICS.FOR /ANGLES/ NMU

    # ===== BASICS.FOR : COMMON /comptn/ =====
    "amuc": ("array", ("MMUC", ), "np.float64"),  # BASICS.FOR /comptn/ amuc(mmuc)
    "wtmuc": ("array", ("MMUC", ), "np.float64"),  # BASICS.FOR /comptn/ wtmuc(mmuc)
    "amuc1": ("array", ("MMUC", ), "np.float64"),  # BASICS.FOR /comptn/ amuc1(mmuc)
    "amuc2": ("array", ("MMUC", ), "np.float64"),  # BASICS.FOR /comptn/ amuc2(mmuc)
    "amuc3": ("array", ("MMUC", ), "np.float64"),  # BASICS.FOR /comptn/ amuc3(mmuc)
    "amuj": ("array", ("MMUC", ), "np.float64"),  # BASICS.FOR /comptn/ amuj(mmuc)
    "amuk": ("array", ("MMUC", ), "np.float64"),  # BASICS.FOR /comptn/ amuk(mmuc)
    "amuh": ("array", ("MMUC", ), "np.float64"),  # BASICS.FOR /comptn/ amuh(mmuc)
    "amun": ("array", ("MMUC", ), "np.float64"),  # BASICS.FOR /comptn/ amun(mmuc)
    "calph": ("array", ("MMUC", "MMUC", ), "np.float64"),  # BASICS.FOR /comptn/ calph(mmuc,mmuc)
    "cbeta": ("array", ("MMUC", "MMUC", ), "np.float64"),  # BASICS.FOR /comptn/ cbeta(mmuc,mmuc)
    "cgamm": ("array", ("MMUC", "MMUC", ), "np.float64"),  # BASICS.FOR /comptn/ cgamm(mmuc,mmuc)
    "RADZER": ("scalar", (), "np.float64"),  # BASICS.FOR /comptn/ RADZER
    "FRLCOM": ("scalar", (), "np.float64"),  # BASICS.FOR /comptn/ FRLCOM
    "SIGEC": ("array", ("MFREQ", ), "np.float64"),  # BASICS.FOR /comptn/ SIGEC(MFREQ)
    "ijorig": ("array", ("MFREQ", ), "np.int64"),  # BASICS.FOR /comptn/ ijorig(mfreq)

    # ===== BASICS.FOR : COMMON /angnum/ =====
    "nmuc": ("scalar", (), "np.int64"),  # BASICS.FOR /angnum/ nmuc

    # ===== BASICS.FOR : COMMON /compti/ =====
    "nedd": ("scalar", (), "np.int64"),  # BASICS.FOR /compti/ nedd
    "nsti": ("scalar", (), "np.int64"),  # BASICS.FOR /compti/ nsti
    "islab": ("scalar", (), "np.int64"),  # BASICS.FOR /compti/ islab
    "ilbc": ("scalar", (), "np.int64"),  # BASICS.FOR /compti/ ilbc
    "icompt": ("scalar", (), "np.int64"),  # BASICS.FOR /compti/ icompt
    "icomst": ("scalar", (), "np.int64"),  # BASICS.FOR /compti/ icomst
    "icomde": ("scalar", (), "np.int64"),  # BASICS.FOR /compti/ icomde
    "icombc": ("scalar", (), "np.int64"),  # BASICS.FOR /compti/ icombc
    "icmdra": ("scalar", (), "np.int64"),  # BASICS.FOR /compti/ icmdra
    "knish": ("scalar", (), "np.int64"),  # BASICS.FOR /compti/ knish
    "itcomp": ("scalar", (), "np.int64"),  # BASICS.FOR /compti/ itcomp
    "icomve": ("scalar", (), "np.int64"),  # BASICS.FOR /compti/ icomve
    "icomrt": ("scalar", (), "np.int64"),  # BASICS.FOR /compti/ icomrt
    "ichcoo": ("scalar", (), "np.int64"),  # BASICS.FOR /compti/ ichcoo
    "icomgr": ("scalar", (), "np.int64"),  # BASICS.FOR /compti/ icomgr

    # ===== BASICS.FOR : COMMON /comite/ =====
    "ncfor1": ("scalar", (), "np.int64"),  # BASICS.FOR /comite/ ncfor1
    "ncfor2": ("scalar", (), "np.int64"),  # BASICS.FOR /comite/ ncfor2
    "nccoup": ("scalar", (), "np.int64"),  # BASICS.FOR /comite/ nccoup
    "ncitot": ("scalar", (), "np.int64"),  # BASICS.FOR /comite/ ncitot
    "ncfull": ("scalar", (), "np.int64"),  # BASICS.FOR /comite/ ncfull

    # ===== BASICS.FOR : COMMON /mlcons/ =====
    "aconml": ("scalar", (), "np.float64"),  # BASICS.FOR /mlcons/ aconml
    "bconml": ("scalar", (), "np.float64"),  # BASICS.FOR /mlcons/ bconml
    "cconml": ("scalar", (), "np.float64"),  # BASICS.FOR /mlcons/ cconml

    # ===== BASICS.FOR : COMMON /taursl/ =====
    "taurs": ("array", ("MDEPTH", ), "np.float64"),  # BASICS.FOR /taursl/ taurs(mdepth)

    # ===== BASICS.FOR : COMMON /iprkey/ =====
    "iprybh": ("scalar", (), "np.int64"),  # BASICS.FOR /iprkey/ iprybh
    "ipelch": ("scalar", (), "np.int64"),  # BASICS.FOR /iprkey/ ipelch
    "ipeldo": ("scalar", (), "np.int64"),  # BASICS.FOR /iprkey/ ipeldo
    "ipconf": ("scalar", (), "np.int64"),  # BASICS.FOR /iprkey/ ipconf

    # ===== fork addition : COMMON /ADPLAM/ =====
    "iadlam": ("scalar", (), "np.int64"),  # fork NSTPAR /ADPLAM/ IADLAM (adaptive lambda iteration)

    # ===== ATOMIC.FOR : COMMON /ATOPAR/ =====
    "AMASS": ("array", ("MATOM", ), "np.float64"),  # ATOMIC.FOR /ATOPAR/ AMASS(MATOM)
    "ABUND": ("array", ("MATOM", "MDEPTH", ), "np.float64"),  # ATOMIC.FOR /ATOPAR/ ABUND(MATOM,MDEPTH)
    "NUMAT": ("array", ("MATOM", ), "np.int64"),  # ATOMIC.FOR /ATOPAR/ NUMAT(MATOM)
    "N0A": ("array", ("MATOM", ), "np.int64"),  # ATOMIC.FOR /ATOPAR/ N0A(MATOM)
    "NKA": ("array", ("MATOM", ), "np.int64"),  # ATOMIC.FOR /ATOPAR/ NKA(MATOM)
    "nref": ("array", ("MATOM", ), "np.int64"),  # ATOMIC.FOR /ATOPAR/ nref(matom)
    "iatex": ("array", ("MATOM", ), "np.int64"),  # ATOMIC.FOR /ATOPAR/ iatex(matom)
    "nrefs": ("array", ("MATOM", "MDEPTH", ), "np.int64"),  # ATOMIC.FOR /ATOPAR/ nrefs(matom,mdepth)
    "iadop": ("array", ("MATOM", ), "np.int64"),  # ATOMIC.FOR /ATOPAR/ iadop(matom)
    "iifix": ("array", ("MATOM", ), "np.int64"),  # ATOMIC.FOR /ATOPAR/ iifix(matom)
    "iatref": ("scalar", (), "np.int64"),  # ATOMIC.FOR /ATOPAR/ iatref
    "modref": ("scalar", (), "np.int64"),  # ATOMIC.FOR /ATOPAR/ modref

    # ===== ATOMIC.FOR : COMMON /atomas/ =====
    "amas": ("array", ("100", ), "np.float64"),  # ATOMIC.FOR /atomas/ amas(100)

    # ===== ATOMIC.FOR : COMMON /IONPAR/ =====
    "FF": ("array", ("MION", ), "np.float64"),  # ATOMIC.FOR /IONPAR/ FF(MION)
    "CHARG2": ("array", ("MION", ), "np.float64"),  # ATOMIC.FOR /IONPAR/ CHARG2(MION)
    "NFIRST": ("array", ("MION", ), "np.int64"),  # ATOMIC.FOR /IONPAR/ NFIRST(MION)
    "NLAST": ("array", ("MION", ), "np.int64"),  # ATOMIC.FOR /IONPAR/ NLAST(MION)
    "NNEXT": ("array", ("MION", ), "np.int64"),  # ATOMIC.FOR /IONPAR/ NNEXT(MION)
    "IZ": ("array", ("MION", ), "np.int64"),  # ATOMIC.FOR /IONPAR/ IZ(MION)
    "IUPSUM": ("array", ("MION", ), "np.int64"),  # ATOMIC.FOR /IONPAR/ IUPSUM(MION)
    "ICUP": ("array", ("MION", ), "np.int64"),  # ATOMIC.FOR /IONPAR/ ICUP(MION)
    "ilte": ("array", ("MION", ), "np.int64"),  # ATOMIC.FOR /IONPAR/ ilte(mion)
    "iltion": ("array", ("MION", ), "np.int64"),  # ATOMIC.FOR /IONPAR/ iltion(mion)

    # ===== ATOMIC.FOR : COMMON /LEVPAR/ =====
    "ENION": ("array", ("MLEVEL", ), "np.float64"),  # ATOMIC.FOR /LEVPAR/ ENION(MLEVEL)
    "G": ("array", ("MLEVEL", ), "np.float64"),  # ATOMIC.FOR /LEVPAR/ G(MLEVEL)
    "NQUANT": ("array", ("MLEVEL", ), "np.int64"),  # ATOMIC.FOR /LEVPAR/ NQUANT(MLEVEL)
    "IATM": ("array", ("MLEVEL", ), "np.int64"),  # ATOMIC.FOR /LEVPAR/ IATM(MLEVEL)
    "IEL": ("array", ("MLEVEL", ), "np.int64"),  # ATOMIC.FOR /LEVPAR/ IEL(MLEVEL)
    "ILK": ("array", ("MLEVEL", ), "np.int64"),  # ATOMIC.FOR /LEVPAR/ ILK(MLEVEL)
    "ilin": ("array", ("MLEVEL", ), "np.int64"),  # ATOMIC.FOR /LEVPAR/ ilin(mlevel)
    "iltlev": ("array", ("MLEVEL", ), "np.int64"),  # ATOMIC.FOR /LEVPAR/ iltlev(mlevel)
    "indlev": ("array", ("MLEVEL", ), "np.int64"),  # ATOMIC.FOR /LEVPAR/ indlev(mlevel)
    "imodl": ("array", ("MLEVEL", ), "np.int64"),  # ATOMIC.FOR /LEVPAR/ imodl(mlevel)
    "iiexp": ("array", ("MLEVEL", ), "np.int64"),  # ATOMIC.FOR /LEVPAR/ iiexp(mlevel)
    "iifor": ("array", ("MLEVEL", ), "np.int64"),  # ATOMIC.FOR /LEVPAR/ iifor(mlevel)
    "ipzert": ("array", ("MLEVEL", ), "np.int64"),  # ATOMIC.FOR /LEVPAR/ ipzert(mlevel)
    "igzert": ("array", ("MLEVEL", ), "np.int64"),  # ATOMIC.FOR /LEVPAR/ igzert(mlevel)
    "indlgz": ("array", ("MLEVEL", ), "np.int64"),  # ATOMIC.FOR /LEVPAR/ indlgz(mlevel)
    "iinonz": ("array", ("MLEVEL", ), "np.int64"),  # ATOMIC.FOR /LEVPAR/ iinonz(mlevel)
    "NLVEXP": ("scalar", (), "np.int64"),  # ATOMIC.FOR /LEVPAR/ NLVEXP
    "NLVFOR": ("scalar", (), "np.int64"),  # ATOMIC.FOR /LEVPAR/ NLVFOR
    "NLVEXZ": ("scalar", (), "np.int64"),  # ATOMIC.FOR /LEVPAR/ NLVEXZ
    "LBPFX": ("scalar", (), "bool"),  # ATOMIC.FOR /LEVPAR/ LBPFX

    # ===== ATOMIC.FOR : COMMON /TRAPAR/ =====
    "FR0": ("array", ("MTRANS", ), "np.float64"),  # ATOMIC.FOR /TRAPAR/ FR0(MTRANS)
    "OSC0": ("array", ("MTRANS", ), "np.float64"),  # ATOMIC.FOR /TRAPAR/ OSC0(MTRANS)
    "CPAR": ("array", ("MTRANS", ), "np.float64"),  # ATOMIC.FOR /TRAPAR/ CPAR(MTRANS)
    "FRQMX": ("array", ("MTRANS", ), "np.float64"),  # ATOMIC.FOR /TRAPAR/ FRQMX(MTRANS)
    "FR0PC": ("array", ("MTRANS", ), "np.float64"),  # ATOMIC.FOR /TRAPAR/ FR0PC(MTRANS)
    "OMECOL": ("array", ("MLEVEL", "MLEVEL", ), "np.float64"),  # ATOMIC.FOR /TRAPAR/ OMECOL(MLEVEL,MLEVEL)
    "XGRAD": ("scalar", (), "np.float64"),  # ATOMIC.FOR /TRAPAR/ XGRAD
    "STRL1": ("scalar", (), "np.float64"),  # ATOMIC.FOR /TRAPAR/ STRL1
    "STRL2": ("scalar", (), "np.float64"),  # ATOMIC.FOR /TRAPAR/ STRL2
    "STRLX": ("scalar", (), "np.float64"),  # ATOMIC.FOR /TRAPAR/ STRLX
    "ILOW": ("array", ("MTRANS", ), "np.int64"),  # ATOMIC.FOR /TRAPAR/ ILOW(MTRANS)
    "IUP": ("array", ("MTRANS", ), "np.int64"),  # ATOMIC.FOR /TRAPAR/ IUP(MTRANS)
    "INDEXP": ("array", ("MTRANS", ), "np.int64"),  # ATOMIC.FOR /TRAPAR/ INDEXP(MTRANS)
    "KFR0": ("array", ("MTRANS", ), "np.int64"),  # ATOMIC.FOR /TRAPAR/ KFR0(MTRANS)
    "KFR1": ("array", ("MTRANS", ), "np.int64"),  # ATOMIC.FOR /TRAPAR/ KFR1(MTRANS)
    "ILUCTR": ("array", ("MTRANS", ), "np.int64"),  # ATOMIC.FOR /TRAPAR/ ILUCTR(MTRANS)
    "IFC0": ("array", ("MTRANS", ), "np.int64"),  # ATOMIC.FOR /TRAPAR/ IFC0(MTRANS)
    "IFC1": ("array", ("MTRANS", ), "np.int64"),  # ATOMIC.FOR /TRAPAR/ IFC1(MTRANS)
    "IFR0": ("array", ("MTRANS", ), "np.int64"),  # ATOMIC.FOR /TRAPAR/ IFR0(MTRANS)
    "IFR1": ("array", ("MTRANS", ), "np.int64"),  # ATOMIC.FOR /TRAPAR/ IFR1(MTRANS)
    "ITRA": ("array", ("MLEVEL", "MLEVEL", ), "np.int64"),  # ATOMIC.FOR /TRAPAR/ ITRA(MLEVEL,MLEVEL)
    "IPROF": ("array", ("MTRANS", ), "np.int64"),  # ATOMIC.FOR /TRAPAR/ IPROF(MTRANS)
    "ICOL": ("array", ("MTRANS", ), "np.int64"),  # ATOMIC.FOR /TRAPAR/ ICOL(MTRANS)
    "INTMOD": ("array", ("MTRANS", ), "np.int64"),  # ATOMIC.FOR /TRAPAR/ INTMOD(MTRANS)
    "ITRCON": ("array", ("MTRANS", ), "np.int64"),  # ATOMIC.FOR /TRAPAR/ ITRCON(MTRANS)
    "IDIEL": ("array", ("MTRANS", ), "np.int64"),  # ATOMIC.FOR /TRAPAR/ IDIEL(MTRANS)
    "IJTF": ("array", ("MTRANS", ), "np.int64"),  # ATOMIC.FOR /TRAPAR/ IJTF(MTRANS)
    "LCOMP": ("array", ("MTRANS", ), "bool"),  # ATOMIC.FOR /TRAPAR/ LCOMP(MTRANS)
    "LINE": ("array", ("MTRANS", ), "bool"),  # ATOMIC.FOR /TRAPAR/ LINE(MTRANS)

    # ===== ATOMIC.FOR : COMMON /PHOSET/ =====
    "S0CS": ("array", ("MLEVEL", ), "np.float64"),  # ATOMIC.FOR /PHOSET/ S0CS(MLEVEL)
    "ALFCS": ("array", ("MLEVEL", ), "np.float64"),  # ATOMIC.FOR /PHOSET/ ALFCS(MLEVEL)
    "BETCS": ("array", ("MLEVEL", ), "np.float64"),  # ATOMIC.FOR /PHOSET/ BETCS(MLEVEL)
    "GAMCS": ("array", ("MLEVEL", ), "np.float64"),  # ATOMIC.FOR /PHOSET/ GAMCS(MLEVEL)
    "IBF": ("array", ("MLEVEL", ), "np.int64"),  # ATOMIC.FOR /PHOSET/ IBF(MLEVEL)

    # ===== ATOMIC.FOR : COMMON /TOPCS/ =====
    "CTOP": ("array", ("MFIT", "MCROSS", ), "np.float64"),  # ATOMIC.FOR /TOPCS/ CTOP(MFIT,MCROSS)
    "XTOP": ("array", ("MFIT", "MCROSS", ), "np.float64"),  # ATOMIC.FOR /TOPCS/ XTOP(MFIT,MCROSS)

    # ===== ATOMIC.FOR : COMMON /TABCOL/ =====
    "CTEMP": ("array", ("MXTCOL", "MCFIT", "MCORAT", ), "np.float64"),  # ATOMIC.FOR /TABCOL/ CTEMP(MXTCOL,MCFIT,MCORAT)
    "CRATE": ("array", ("MXTCOL", "MCFIT", "MCORAT", ), "np.float64"),  # ATOMIC.FOR /TABCOL/ CRATE(MXTCOL,MCFIT,MCORAT)

    # ===== ATOMIC.FOR : COMMON /VOIPAR/ =====
    "GAMAR": ("array", ("MVOIGT", ), "np.float64"),  # ATOMIC.FOR /VOIPAR/ GAMAR(MVOIGT)
    "STARK1": ("array", ("MVOIGT", ), "np.float64"),  # ATOMIC.FOR /VOIPAR/ STARK1(MVOIGT)
    "STARK2": ("array", ("MVOIGT", ), "np.float64"),  # ATOMIC.FOR /VOIPAR/ STARK2(MVOIGT)
    "STARK3": ("array", ("MVOIGT", ), "np.float64"),  # ATOMIC.FOR /VOIPAR/ STARK3(MVOIGT)
    "VDWH": ("array", ("MVOIGT", ), "np.float64"),  # ATOMIC.FOR /VOIPAR/ VDWH(MVOIGT)

    # ===== ATOMIC.FOR : COMMON /HECRAT/ =====
    "COLHE1": ("array", ("19", "19", ), "np.float64"),  # ATOMIC.FOR /HECRAT/ COLHE1(19,19)

    # ===== ATOMIC.FOR : COMMON /TRACOR/ =====
    "LEXP": ("array", ("MTRANS", ), "bool"),  # ATOMIC.FOR /TRACOR/ LEXP(MTRANS)
    "LALI": ("array", ("MTRANS", ), "bool"),  # ATOMIC.FOR /TRACOR/ LALI(MTRANS)

    # ===== ATOMIC.FOR : COMMON /TRAALI/ =====
    "NFFIX": ("scalar", (), "np.int64"),  # ATOMIC.FOR /TRAALI/ NFFIX
    "IFSUB": ("scalar", (), "np.int64"),  # ATOMIC.FOR /TRAALI/ IFSUB
    "IFLEV": ("scalar", (), "np.int64"),  # ATOMIC.FOR /TRAALI/ IFLEV

    # ===== ATOMIC.FOR : COMMON /AUXIND/ =====
    "IATH": ("scalar", (), "np.int64"),  # ATOMIC.FOR /AUXIND/ IATH
    "IATHE": ("scalar", (), "np.int64"),  # ATOMIC.FOR /AUXIND/ IATHE
    "IELH": ("scalar", (), "np.int64"),  # ATOMIC.FOR /AUXIND/ IELH
    "IELHM": ("scalar", (), "np.int64"),  # ATOMIC.FOR /AUXIND/ IELHM
    "IELHE1": ("scalar", (), "np.int64"),  # ATOMIC.FOR /AUXIND/ IELHE1
    "IELHE2": ("scalar", (), "np.int64"),  # ATOMIC.FOR /AUXIND/ IELHE2

    # ===== ATOMIC.FOR : COMMON /IONFIL/ =====
    "FIDATA": ("array", ("MION", ), "object"),  # ATOMIC.FOR /IONFIL/ FIDATA
    "FIODF1": ("array", ("MION", ), "object"),  # ATOMIC.FOR /IONFIL/ FIODF1
    "FIODF2": ("array", ("MION", ), "object"),  # ATOMIC.FOR /IONFIL/ FIODF2
    "FIBFCS": ("array", ("MION", ), "object"),  # ATOMIC.FOR /IONFIL/ FIBFCS

    # ===== ATOMIC.FOR : COMMON /IONDAT/ =====
    "IATI": ("array", ("MION", ), "np.int64"),  # ATOMIC.FOR /IONDAT/ IATI(MION)
    "IZI": ("array", ("MION", ), "np.int64"),  # ATOMIC.FOR /IONDAT/ IZI(MION)
    "NLEVS": ("array", ("MION", ), "np.int64"),  # ATOMIC.FOR /IONDAT/ NLEVS(MION)
    "NLLIM": ("array", ("MION", ), "np.int64"),  # ATOMIC.FOR /IONDAT/ NLLIM(MION)

    # ===== ATOMIC.FOR : COMMON /OSCHYD/ =====
    "OSH": ("array", ("20", "20", ), "np.float64"),  # ATOMIC.FOR /OSCHYD/ OSH(20,20)

    # ===== ATOMIC.FOR : COMMON /PRINTP/ =====
    "NPGPOP": ("scalar", (), "np.int64"),  # ATOMIC.FOR /PRINTP/ NPGPOP
    "IIPR": ("array", ("6", "MPAG", ), "np.int64"),  # ATOMIC.FOR /PRINTP/ IIPR(6,MPAG)
    "TYPLEV": ("array", ("MLEVEL", ), "object"),  # ATOMIC.FOR /PRINTP/ TYPLEV
    "TYPION": ("array", ("MION", ), "object"),  # ATOMIC.FOR /PRINTP/ TYPION

    # ===== ATOMIC.FOR : COMMON /tabmax/ =====
    "frtabm": ("scalar", (), "np.float64"),  # ATOMIC.FOR /tabmax/ frtabm

    # ===== ATOMIC.FOR : COMMON /PRDPAR/ =====
    "DOPTR": ("array", ("MTRPRD", "MDEPTH", ), "np.float64"),  # ATOMIC.FOR /PRDPAR/ DOPTR(MTRPRD,MDEPTH)
    "COHER": ("array", ("MTRPRD", "MDEPTH", ), "np.float64"),  # ATOMIC.FOR /PRDPAR/ COHER(MTRPRD,MDEPTH)
    "PJBAR": ("array", ("MTRPRD", "MDEPTH", ), "np.float64"),  # ATOMIC.FOR /PRDPAR/ PJBAR(MTRPRD,MDEPTH)
    "RJBAR": ("array", ("MTRPRD", "MDEPTH", ), "np.float64"),  # ATOMIC.FOR /PRDPAR/ RJBAR(MTRPRD,MDEPTH)
    "XPDIV": ("scalar", (), "np.float64"),  # ATOMIC.FOR /PRDPAR/ XPDIV
    "IPRD": ("array", ("MTRANS", ), "np.int64"),  # ATOMIC.FOR /PRDPAR/ IPRD(MTRANS)
    "ITRTOT": ("array", ("MTRPRD", ), "np.int64"),  # ATOMIC.FOR /PRDPAR/ ITRTOT(MTRPRD)
    "NTRPRD": ("scalar", (), "np.int64"),  # ATOMIC.FOR /PRDPAR/ NTRPRD
    "IFPRD": ("scalar", (), "np.int64"),  # ATOMIC.FOR /PRDPAR/ IFPRD

    # ===== ARRAY1.FOR : COMMON (blank) =====
    "A": ("array", ("MTOT", "MTOT", ), "np.float64"),  # ARRAY1.FOR blank COMMON A(MTOT,MTOT)
    "B": ("array", ("MTOT", "MTOT", ), "np.float64"),  # ARRAY1.FOR blank COMMON B(MTOT,MTOT)
    "C": ("array", ("MTOT", "MTOT", ), "np.float64"),  # ARRAY1.FOR blank COMMON C(MTOT,MTOT)
    "E": ("array", ("MTOT", "MTOT", ), "np.float64"),  # ARRAY1.FOR blank COMMON E(MTOT,MTOT)
    "VECL": ("array", ("MTOT", ), "np.float64"),  # ARRAY1.FOR blank COMMON VECL(MTOT)
    "Y1": ("array", ("MTOT", ), "np.float64"),  # ARRAY1.FOR blank COMMON Y1(MTOT)
    "Y2": ("array", ("MTOT", ), "np.float64"),  # ARRAY1.FOR blank COMMON Y2(MTOT)
    "PSI0": ("array", ("MTOT", ), "np.float64"),  # ARRAY1.FOR blank COMMON PSI0(MTOT)
    "PSIM": ("array", ("MTOT", ), "np.float64"),  # ARRAY1.FOR blank COMMON PSIM(MTOT)
    "PSIP": ("array", ("MTOT", ), "np.float64"),  # ARRAY1.FOR blank COMMON PSIP(MTOT)
    "RAD0": ("array", ("MTOT", ), "np.float64"),  # ARRAY1.FOR blank COMMON RAD0(MTOT)
    "RADM": ("array", ("MTOT", ), "np.float64"),  # ARRAY1.FOR blank COMMON RADM(MTOT)
    "RADP": ("array", ("MTOT", ), "np.float64"),  # ARRAY1.FOR blank COMMON RADP(MTOT)
    "FKM": ("array", ("MFREX", ), "np.float64"),  # ARRAY1.FOR blank COMMON FKM(MFREX)
    "FK0": ("array", ("MFREX", ), "np.float64"),  # ARRAY1.FOR blank COMMON FK0(MFREX)
    "FKP": ("array", ("MFREX", ), "np.float64"),  # ARRAY1.FOR blank COMMON FKP(MFREX)
    "ABSOM": ("array", ("MFREX", ), "np.float64"),  # ARRAY1.FOR blank COMMON ABSOM(MFREX)
    "ABSO0": ("array", ("MFREX", ), "np.float64"),  # ARRAY1.FOR blank COMMON ABSO0(MFREX)
    "ABSOP": ("array", ("MFREX", ), "np.float64"),  # ARRAY1.FOR blank COMMON ABSOP(MFREX)
    "EMISM": ("array", ("MFREX", ), "np.float64"),  # ARRAY1.FOR blank COMMON EMISM(MFREX)
    "EMIS0": ("array", ("MFREX", ), "np.float64"),  # ARRAY1.FOR blank COMMON EMIS0(MFREX)
    "EMISP": ("array", ("MFREX", ), "np.float64"),  # ARRAY1.FOR blank COMMON EMISP(MFREX)
    "SCATM": ("array", ("MFREX", ), "np.float64"),  # ARRAY1.FOR blank COMMON SCATM(MFREX)
    "SCAT0": ("array", ("MFREX", ), "np.float64"),  # ARRAY1.FOR blank COMMON SCAT0(MFREX)
    "SCATP": ("array", ("MFREX", ), "np.float64"),  # ARRAY1.FOR blank COMMON SCATP(MFREX)
    "DABTM": ("array", ("MFREX", ), "np.float64"),  # ARRAY1.FOR blank COMMON DABTM(MFREX)
    "DABT0": ("array", ("MFREX", ), "np.float64"),  # ARRAY1.FOR blank COMMON DABT0(MFREX)
    "DABTP": ("array", ("MFREX", ), "np.float64"),  # ARRAY1.FOR blank COMMON DABTP(MFREX)
    "DEMTM": ("array", ("MFREX", ), "np.float64"),  # ARRAY1.FOR blank COMMON DEMTM(MFREX)
    "DEMT0": ("array", ("MFREX", ), "np.float64"),  # ARRAY1.FOR blank COMMON DEMT0(MFREX)
    "DEMTP": ("array", ("MFREX", ), "np.float64"),  # ARRAY1.FOR blank COMMON DEMTP(MFREX)
    "DABNM": ("array", ("MFREX", ), "np.float64"),  # ARRAY1.FOR blank COMMON DABNM(MFREX)
    "DABN0": ("array", ("MFREX", ), "np.float64"),  # ARRAY1.FOR blank COMMON DABN0(MFREX)
    "DABNP": ("array", ("MFREX", ), "np.float64"),  # ARRAY1.FOR blank COMMON DABNP(MFREX)
    "DEMNM": ("array", ("MFREX", ), "np.float64"),  # ARRAY1.FOR blank COMMON DEMNM(MFREX)
    "DEMN0": ("array", ("MFREX", ), "np.float64"),  # ARRAY1.FOR blank COMMON DEMN0(MFREX)
    "DEMNP": ("array", ("MFREX", ), "np.float64"),  # ARRAY1.FOR blank COMMON DEMNP(MFREX)
    "DABMM": ("array", ("MFREX", ), "np.float64"),  # ARRAY1.FOR blank COMMON DABMM(MFREX)
    "DABM0": ("array", ("MFREX", ), "np.float64"),  # ARRAY1.FOR blank COMMON DABM0(MFREX)
    "DABMP": ("array", ("MFREX", ), "np.float64"),  # ARRAY1.FOR blank COMMON DABMP(MFREX)
    "DEMMM": ("array", ("MFREX", ), "np.float64"),  # ARRAY1.FOR blank COMMON DEMMM(MFREX)
    "DEMM0": ("array", ("MFREX", ), "np.float64"),  # ARRAY1.FOR blank COMMON DEMM0(MFREX)
    "DEMMP": ("array", ("MFREX", ), "np.float64"),  # ARRAY1.FOR blank COMMON DEMMP(MFREX)
    "WDEPM": ("array", ("MFREX", ), "np.float64"),  # ARRAY1.FOR blank COMMON WDEPM(MFREX)
    "WDEP0": ("array", ("MFREX", ), "np.float64"),  # ARRAY1.FOR blank COMMON WDEP0(MFREX)
    "WDEPP": ("array", ("MFREX", ), "np.float64"),  # ARRAY1.FOR blank COMMON WDEPP(MFREX)
    "SBFM": ("array", ("MLEVEL", ), "np.float64"),  # ARRAY1.FOR blank COMMON SBFM(MLEVEL)
    "SBF0": ("array", ("MLEVEL", ), "np.float64"),  # ARRAY1.FOR blank COMMON SBF0(MLEVEL)
    "SBFP": ("array", ("MLEVEL", ), "np.float64"),  # ARRAY1.FOR blank COMMON SBFP(MLEVEL)
    "HEX": ("array", ("MLEVEL", ), "np.float64"),  # ARRAY1.FOR blank COMMON HEX(MLEVEL)
    "REX": ("array", ("MLEVEL", ), "np.float64"),  # ARRAY1.FOR blank COMMON REX(MLEVEL)
    "REXA": ("array", ("MLEVEL", ), "np.float64"),  # ARRAY1.FOR blank COMMON REXA(MLEVEL)
    "DSBFM": ("array", ("MLEVEL", ), "np.float64"),  # ARRAY1.FOR blank COMMON DSBFM(MLEVEL)
    "DSBF0": ("array", ("MLEVEL", ), "np.float64"),  # ARRAY1.FOR blank COMMON DSBF0(MLEVEL)
    "DSBFP": ("array", ("MLEVEL", ), "np.float64"),  # ARRAY1.FOR blank COMMON DSBFP(MLEVEL)
    "SUMDCH": ("array", ("MLEVEL", ), "np.float64"),  # ARRAY1.FOR blank COMMON SUMDCH(MLEVEL)
    "DRCHM": ("array", ("MLEVEL", "MFREX", ), "np.float64"),  # ARRAY1.FOR blank COMMON DRCHM(MLEVEL,MFREX)
    "DRETM": ("array", ("MLEVEL", "MFREX", ), "np.float64"),  # ARRAY1.FOR blank COMMON DRETM(MLEVEL,MFREX)
    "DRCH0": ("array", ("MLEVEL", "MFREX", ), "np.float64"),  # ARRAY1.FOR blank COMMON DRCH0(MLEVEL,MFREX)
    "DRET0": ("array", ("MLEVEL", "MFREX", ), "np.float64"),  # ARRAY1.FOR blank COMMON DRET0(MLEVEL,MFREX)
    "DRCHP": ("array", ("MLEVEL", "MFREX", ), "np.float64"),  # ARRAY1.FOR blank COMMON DRCHP(MLEVEL,MFREX)
    "DRETP": ("array", ("MLEVEL", "MFREX", ), "np.float64"),  # ARRAY1.FOR blank COMMON DRETP(MLEVEL,MFREX)

    # ===== ARRAY1.FOR : COMMON /EXPRAD/ =====
    "ABSOEX": ("array", ("MFREX", "MDEPTH", ), "np.float64"),  # ARRAY1.FOR /EXPRAD/ ABSOEX(MFREX,MDEPTH)
    "EMISEX": ("array", ("MFREX", "MDEPTH", ), "np.float64"),  # ARRAY1.FOR /EXPRAD/ EMISEX(MFREX,MDEPTH)
    "SCATEX": ("array", ("MFREX", "MDEPTH", ), "np.float64"),  # ARRAY1.FOR /EXPRAD/ SCATEX(MFREX,MDEPTH)
    "DABTEX": ("array", ("MFREX", "MDEPTH", ), "np.float64"),  # ARRAY1.FOR /EXPRAD/ DABTEX(MFREX,MDEPTH)
    "DEMTEX": ("array", ("MFREX", "MDEPTH", ), "np.float64"),  # ARRAY1.FOR /EXPRAD/ DEMTEX(MFREX,MDEPTH)
    "DABNEX": ("array", ("MFREX", "MDEPTH", ), "np.float64"),  # ARRAY1.FOR /EXPRAD/ DABNEX(MFREX,MDEPTH)
    "DEMNEX": ("array", ("MFREX", "MDEPTH", ), "np.float64"),  # ARRAY1.FOR /EXPRAD/ DEMNEX(MFREX,MDEPTH)
    "DABMEX": ("array", ("MFREX", "MDEPTH", ), "np.float64"),  # ARRAY1.FOR /EXPRAD/ DABMEX(MFREX,MDEPTH)
    "DEMMEX": ("array", ("MFREX", "MDEPTH", ), "np.float64"),  # ARRAY1.FOR /EXPRAD/ DEMMEX(MFREX,MDEPTH)
    "DRCHEX": ("array", ("MLVEXP", "MFREX", "MDEPTH", ), "np.float64"),  # ARRAY1.FOR /EXPRAD/ DRCHEX(MLVEXP,MFREX,MDEPTH)
    "DRETEX": ("array", ("MLVEXP", "MFREX", "MDEPTH", ), "np.float64"),  # ARRAY1.FOR /EXPRAD/ DRETEX(MLVEXP,MFREX,MDEPTH)

    # ===== ARRAY1.FOR : COMMON /BPOCOM/ =====
    "ESEMAT": ("array", ("MLEVEL", "MLEVEL", ), "np.float64"),  # ARRAY1.FOR /BPOCOM/ ESEMAT(MLEVEL,MLEVEL)
    "BESE": ("array", ("MLEVEL", ), "np.float64"),  # ARRAY1.FOR /BPOCOM/ BESE(MLEVEL)
    "ATT": ("array", ("MLEVEL", ), "np.float64"),  # ARRAY1.FOR /BPOCOM/ ATT(MLEVEL)
    "ANN": ("array", ("MLEVEL", ), "np.float64"),  # ARRAY1.FOR /BPOCOM/ ANN(MLEVEL)

    # ===== ITERAT.FOR : COMMON /LAMBDA/ =====
    "NLAMBD": ("scalar", (), "np.int64"),  # ITERAT.FOR /LAMBDA/ NLAMBD
    "IFFIX": ("array", ("MITER", ), "np.int64"),  # ITERAT.FOR /LAMBDA/ IFFIX(MITER)
    "NETEXP": ("array", ("MITER", ), "np.int64"),  # ITERAT.FOR /LAMBDA/ NETEXP(MITER)
    "NETFIX": ("array", ("MITER", ), "np.int64"),  # ITERAT.FOR /LAMBDA/ NETFIX(MITER)
    "IETEXP": ("array", ("MITER", "MLAMBD", ), "np.int64"),  # ITERAT.FOR /LAMBDA/ IETEXP(MITER,MLAMBD)
    "IETFIX": ("array", ("MITER", "MLAMBD", ), "np.int64"),  # ITERAT.FOR /LAMBDA/ IETFIX(MITER,MLAMBD)
    "NITLAM": ("array", ("MITER+1", ), "np.int64"),  # ITERAT.FOR /LAMBDA/ NITLAM(MITER+1)
    "IELCOR": ("scalar", (), "np.int64"),  # ITERAT.FOR /LAMBDA/ IELCOR

    # ===== ITERAT.FOR : COMMON /CHNMAT/ =====
    "INHE0": ("array", ("MITER", ), "np.int64"),  # ITERAT.FOR /CHNMAT/ INHE0(MITER)
    "INRE0": ("array", ("MITER", ), "np.int64"),  # ITERAT.FOR /CHNMAT/ INRE0(MITER)
    "INPC0": ("array", ("MITER", ), "np.int64"),  # ITERAT.FOR /CHNMAT/ INPC0(MITER)
    "INDL0": ("array", ("MITER", ), "np.int64"),  # ITERAT.FOR /CHNMAT/ INDL0(MITER)
    "INSE0": ("array", ("MITER", ), "np.int64"),  # ITERAT.FOR /CHNMAT/ INSE0(MITER)
    "INMP0": ("array", ("MITER", ), "np.int64"),  # ITERAT.FOR /CHNMAT/ INMP0(MITER)
    "NN00": ("array", ("MITER", ), "np.int64"),  # ITERAT.FOR /CHNMAT/ NN00(MITER)
    "NDRE0": ("array", ("MITER", ), "np.int64"),  # ITERAT.FOR /CHNMAT/ NDRE0(MITER)
    "LCHMAT": ("scalar", (), "bool"),  # ITERAT.FOR /CHNMAT/ LCHMAT
    "LIROST": ("scalar", (), "bool"),  # ITERAT.FOR /CHNMAT/ LIROST

    # ===== ITERAT.FOR : COMMON /ACCEL/ =====
    "ORELAX": ("scalar", (), "np.float64"),  # ITERAT.FOR /ACCEL/ ORELAX
    "ITEK": ("scalar", (), "np.int64"),  # ITERAT.FOR /ACCEL/ ITEK
    "IACC": ("scalar", (), "np.int64"),  # ITERAT.FOR /ACCEL/ IACC
    "IACC0": ("scalar", (), "np.int64"),  # ITERAT.FOR /ACCEL/ IACC0
    "IACD": ("scalar", (), "np.int64"),  # ITERAT.FOR /ACCEL/ IACD
    "KANT": ("array", ("MITER", ), "np.int64"),  # ITERAT.FOR /ACCEL/ KANT(MITER)
    "KSNG": ("scalar", (), "np.int64"),  # ITERAT.FOR /ACCEL/ KSNG
    "LSNG": ("array", ("MTOT", ), "bool"),  # ITERAT.FOR /ACCEL/ LSNG(MTOT)
    "LASO": ("scalar", (), "bool"),  # ITERAT.FOR /ACCEL/ LASO
    "LRES2": ("scalar", (), "bool"),  # ITERAT.FOR /ACCEL/ LRES2

    # ===== ITERAT.FOR : COMMON /ACCLP/ =====
    "ILAM": ("scalar", (), "np.int64"),  # ITERAT.FOR /ACCLP/ ILAM
    "IACPP": ("scalar", (), "np.int64"),  # ITERAT.FOR /ACCLP/ IACPP
    "IACC0P": ("scalar", (), "np.int64"),  # ITERAT.FOR /ACCLP/ IACC0P
    "IACDP": ("scalar", (), "np.int64"),  # ITERAT.FOR /ACCLP/ IACDP
    "LAC2P": ("scalar", (), "bool"),  # ITERAT.FOR /ACCLP/ LAC2P

    # ===== ITERAT.FOR : COMMON /ACCLT/ =====
    "IACLT": ("scalar", (), "np.int64"),  # ITERAT.FOR /ACCLT/ IACLT
    "IACLDT": ("scalar", (), "np.int64"),  # ITERAT.FOR /ACCLT/ IACLDT

    # ===== ITERAT.FOR : COMMON /CHNAD/ =====
    "CHMAXT": ("scalar", (), "np.float64"),  # ITERAT.FOR /CHNAD/ CHMAXT
    "NLAMT": ("scalar", (), "np.int64"),  # ITERAT.FOR /CHNAD/ NLAMT
    "ILDER": ("scalar", (), "np.int64"),  # ITERAT.FOR /CHNAD/ ILDER
    "IBPOPE": ("scalar", (), "np.int64"),  # ITERAT.FOR /CHNAD/ IBPOPE

    # ===== MODELQ.FOR : COMMON /MODPAR/ =====
    "DM": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /MODPAR/ DM(MDEPTH)
    "TEMP": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /MODPAR/ TEMP(MDEPTH)
    "ELEC": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /MODPAR/ ELEC(MDEPTH)
    "DENS": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /MODPAR/ DENS(MDEPTH)
    "TOTN": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /MODPAR/ TOTN(MDEPTH)
    "ANTO": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /MODPAR/ ANTO(MDEPTH)
    "ANMA": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /MODPAR/ ANMA(MDEPTH)
    "ANH1": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /MODPAR/ ANH1(MDEPTH)
    "ZD": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /MODPAR/ ZD(MDEPTH)
    "HKT1": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /MODPAR/ HKT1(MDEPTH)
    "TK1": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /MODPAR/ TK1(MDEPTH)
    "HKT21": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /MODPAR/ HKT21(MDEPTH)
    "SQT1": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /MODPAR/ SQT1(MDEPTH)
    "TEMP1": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /MODPAR/ TEMP1(MDEPTH)
    "ELEC1": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /MODPAR/ ELEC1(MDEPTH)
    "DENS1": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /MODPAR/ DENS1(MDEPTH)
    "DENSI": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /MODPAR/ DENSI(MDEPTH)
    "DENSIM": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /MODPAR/ DENSIM(MDEPTH)
    "ELSCAT": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /MODPAR/ ELSCAT(MDEPTH)
    "ALAB": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /MODPAR/ ALAB(MDEPTH)
    "DELDM": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /MODPAR/ DELDM(MDEPTH)
    "DEDM1": ("scalar", (), "np.float64"),  # MODELQ.FOR /MODPAR/ DEDM1
    "DELDMZ": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /MODPAR/ DELDMZ(MDEPTH)
    "THETAV": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /MODPAR/ THETAV(MDEPTH)
    "VISCD": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /MODPAR/ VISCD(MDEPTH)
    "DALPMX": ("scalar", (), "np.float64"),  # MODELQ.FOR /MODPAR/ DALPMX
    "XHYD": ("scalar", (), "np.float64"),  # MODELQ.FOR /MODPAR/ XHYD
    "DMTOT": ("scalar", (), "np.float64"),  # MODELQ.FOR /MODPAR/ DMTOT
    "RRDIL": ("scalar", (), "np.float64"),  # MODELQ.FOR /MODPAR/ RRDIL
    "TEMPBD": ("scalar", (), "np.float64"),  # MODELQ.FOR /MODPAR/ TEMPBD
    "ALPTAV": ("scalar", (), "np.float64"),  # MODELQ.FOR /MODPAR/ ALPTAV
    "ALPGAV": ("scalar", (), "np.float64"),  # MODELQ.FOR /MODPAR/ ALPGAV
    "NALP": ("scalar", (), "np.int64"),  # MODELQ.FOR /MODPAR/ NALP
    "IBETA": ("scalar", (), "np.int64"),  # MODELQ.FOR /MODPAR/ IBETA

    # ===== MODELQ.FOR : COMMON /LEVPOP/ =====
    "POPUL": ("array", ("MLEVEL", "MDEPTH", ), "np.float64"),  # MODELQ.FOR /LEVPOP/ POPUL(MLEVEL,MDEPTH)
    "BFAC": ("array", ("MLEVEL", "MDEPTH", ), "np.float64"),  # MODELQ.FOR /LEVPOP/ BFAC(MLEVEL,MDEPTH)
    "POPINV": ("array", ("MLEVEL", "MDEPTH", ), "np.float64"),  # MODELQ.FOR /LEVPOP/ POPINV(MLEVEL,MDEPTH)
    "POPGRP": ("array", ("MLEVEL", ), "np.float64"),  # MODELQ.FOR /LEVPOP/ POPGRP(MLEVEL)
    "POP": ("array", ("MLEVEL", ), "np.float64"),  # MODELQ.FOR /LEVPOP/ POP(MLEVEL)
    "SBF": ("array", ("MLEVEL", ), "np.float64"),  # MODELQ.FOR /LEVPOP/ SBF(MLEVEL)
    "DSBF": ("array", ("MLEVEL", ), "np.float64"),  # MODELQ.FOR /LEVPOP/ DSBF(MLEVEL)
    "USUM": ("array", ("MION", ), "np.float64"),  # MODELQ.FOR /LEVPOP/ USUM(MION)

    # ===== MODELQ.FOR : COMMON /POPZR0/ =====
    "POPZER": ("scalar", (), "np.float64"),  # MODELQ.FOR /POPZR0/ POPZER
    "POPZR2": ("scalar", (), "np.float64"),  # MODELQ.FOR /POPZR0/ POPZR2
    "POPZCH": ("scalar", (), "np.float64"),  # MODELQ.FOR /POPZR0/ POPZCH
    "RPOP0": ("array", ("MLVEXP", "MDEPTH", ), "np.float64"),  # MODELQ.FOR /POPZR0/ RPOP0(MLVEXP,MDEPTH)
    "IPZERO": ("array", ("MLEVEL", "MDEPTH", ), "np.int64"),  # MODELQ.FOR /POPZR0/ IPZERO(MLEVEL,MDEPTH)
    "IGZERO": ("array", ("MLVEXP", "MDEPTH", ), "np.int64"),  # MODELQ.FOR /POPZR0/ IGZERO(MLVEXP,MDEPTH)

    # ===== MODELQ.FOR : COMMON /CRSWPS/ =====
    "CRSW": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /CRSWPS/ CRSW(MDEPTH)
    "SWPFAC": ("scalar", (), "np.float64"),  # MODELQ.FOR /CRSWPS/ SWPFAC
    "SWPLIM": ("scalar", (), "np.float64"),  # MODELQ.FOR /CRSWPS/ SWPLIM
    "SWPINC": ("scalar", (), "np.float64"),  # MODELQ.FOR /CRSWPS/ SWPINC
    "ICRSW": ("scalar", (), "np.int64"),  # MODELQ.FOR /CRSWPS/ ICRSW

    # ===== MODELQ.FOR : COMMON /WMCOMP/ =====
    "WNHINT": ("array", ("NLMX", "MDEPTH", ), "np.float64"),  # MODELQ.FOR /WMCOMP/ WNHINT(NLMX,MDEPTH)
    "WNHEII": ("array", ("NLMX", "MDEPTH", ), "np.float64"),  # MODELQ.FOR /WMCOMP/ WNHEII(NLMX,MDEPTH)
    "wop": ("array", ("MLEVEL", "MDEPTH", ), "np.float64"),  # MODELQ.FOR /WMCOMP/ wop(mlevel,mdepth)
    "ifwop": ("array", ("MLEVEL", ), "np.int64"),  # MODELQ.FOR /WMCOMP/ ifwop(mlevel)

    # ===== MODELQ.FOR : COMMON /REPART/ =====
    "REINT": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /REPART/ REINT(MDEPTH)
    "REDIF": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /REPART/ REDIF(MDEPTH)
    "TAUDIV": ("scalar", (), "np.float64"),  # MODELQ.FOR /REPART/ TAUDIV
    "IDLST": ("scalar", (), "np.int64"),  # MODELQ.FOR /REPART/ IDLST

    # ===== MODELQ.FOR : COMMON /TURBUL/ =====
    "VTURB": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /TURBUL/ VTURB(MDEPTH)
    "VTURBS": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /TURBUL/ VTURBS(MDEPTH)
    "VTB": ("scalar", (), "np.float64"),  # MODELQ.FOR /TURBUL/ VTB
    "IPTURB": ("scalar", (), "np.int64"),  # MODELQ.FOR /TURBUL/ IPTURB

    # ===== MODELQ.FOR : COMMON /LEVREF/ =====
    "SBPSI": ("array", ("MLEVEL", "MDEPTH", ), "np.float64"),  # MODELQ.FOR /LEVREF/ SBPSI(MLEVEL,MDEPTH)
    "SBLPSI": ("array", ("MLEVEL", "MDEPTH", ), "np.float64"),  # MODELQ.FOR /LEVREF/ SBLPSI(MLEVEL,MDEPTH)
    "DSBPST": ("array", ("MLEVEL", "MDEPTH", ), "np.float64"),  # MODELQ.FOR /LEVREF/ DSBPST(MLEVEL,MDEPTH)
    "DSBPSN": ("array", ("MLEVEL", "MDEPTH", ), "np.float64"),  # MODELQ.FOR /LEVREF/ DSBPSN(MLEVEL,MDEPTH)
    "ILTREF": ("array", ("MLEVEL", "MDEPTH", ), "np.int64"),  # MODELQ.FOR /LEVREF/ ILTREF(MLEVEL,MDEPTH)
    "IGUIDE": ("array", ("MLEVEL", ), "np.int64"),  # MODELQ.FOR /LEVREF/ IGUIDE(MLEVEL)
    "ILTERF": ("array", ("MLEVEL", "MDEPTH", ), "np.int64"),  # MODELQ.FOR /LEVREF/ ILTERF(MLEVEL,MDEPTH)

    # ===== MODELQ.FOR : COMMON /LEVFIX/ =====
    "PT": ("array", ("MLEVEL", "MDEPTH", ), "np.float64"),  # MODELQ.FOR /LEVFIX/ PT(MLEVEL,MDEPTH)
    "PN": ("array", ("MLEVEL", "MDEPTH", ), "np.float64"),  # MODELQ.FOR /LEVFIX/ PN(MLEVEL,MDEPTH)
    "PP": ("array", ("MLEVEL", "MDEPTH", ), "np.float64"),  # MODELQ.FOR /LEVFIX/ PP(MLEVEL,MDEPTH)

    # ===== MODELQ.FOR : COMMON /LEVADD/ =====
    "USUMS": ("array", ("MION", "MDEPTH", ), "np.float64"),  # MODELQ.FOR /LEVADD/ USUMS(MION,MDEPTH)
    "DUSMT": ("array", ("MION", "MDEPTH", ), "np.float64"),  # MODELQ.FOR /LEVADD/ DUSMT(MION,MDEPTH)
    "DUSMN": ("array", ("MION", "MDEPTH", ), "np.float64"),  # MODELQ.FOR /LEVADD/ DUSMN(MION,MDEPTH)
    "DIESIG": ("array", ("MION", "MDEPTH", ), "np.float64"),  # MODELQ.FOR /LEVADD/ DIESIG(MION,MDEPTH)

    # ===== MODELQ.FOR : COMMON /MRGPAR/ =====
    "SGM0": ("array", ("MMER", ), "np.float64"),  # MODELQ.FOR /MRGPAR/ SGM0(MMER)
    "FRCH": ("array", ("MMER", ), "np.float64"),  # MODELQ.FOR /MRGPAR/ FRCH(MMER)
    "SGEXT1": ("array", ("MMER", "MDEPTH", ), "np.float64"),  # MODELQ.FOR /MRGPAR/ SGEXT1(MMER,MDEPTH)
    "GMER": ("array", ("MMER", "MDEPTH", ), "np.float64"),  # MODELQ.FOR /MRGPAR/ GMER(MMER,MDEPTH)
    "SGMSUM": ("array", ("NLMX", "MMER", "MDEPTH", ), "np.float64"),  # MODELQ.FOR /MRGPAR/ SGMSUM(NLMX,MMER,MDEPTH)
    "SGMSUD": ("array", ("NLMX", "MMER", "MDEPTH", ), "np.float64"),  # MODELQ.FOR /MRGPAR/ SGMSUD(NLMX,MMER,MDEPTH)
    "SGMG": ("array", ("MMER", "MDEPTH", ), "np.float64"),  # MODELQ.FOR /MRGPAR/ SGMG(MMER,MDEPTH)
    "IMRG": ("array", ("MLEVEL", ), "np.int64"),  # MODELQ.FOR /MRGPAR/ IMRG(MLEVEL)
    "IIMER": ("array", ("MMER", ), "np.int64"),  # MODELQ.FOR /MRGPAR/ IIMER(MMER)

    # ===== MODELQ.FOR : COMMON /UPSUMS/ =====
    "DUSUMT": ("array", ("MION", ), "np.float64"),  # MODELQ.FOR /UPSUMS/ DUSUMT(MION)
    "DUSUMN": ("array", ("MION", ), "np.float64"),  # MODELQ.FOR /UPSUMS/ DUSUMN(MION)

    # ===== MODELQ.FOR : COMMON /DWNPAR/ =====
    "ELEC23": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /DWNPAR/ ELEC23(MDEPTH)
    "ACOR": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /DWNPAR/ ACOR(MDEPTH)
    "Z3": ("array", ("MZZ", ), "np.float64"),  # MODELQ.FOR /DWNPAR/ Z3(MZZ)
    "DWC1": ("array", ("MZZ", "MDEPTH", ), "np.float64"),  # MODELQ.FOR /DWNPAR/ DWC1(MZZ,MDEPTH)
    "DWC2": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /DWNPAR/ DWC2(MDEPTH)
    "DWF1": ("array", ("MMCDW", "MDEPTH", ), "np.float64"),  # MODELQ.FOR /DWNPAR/ DWF1(MMCDW,MDEPTH)
    "MCDW": ("array", ("MTRANS", ), "np.int64"),  # MODELQ.FOR /DWNPAR/ MCDW(MTRANS)
    "ITRCDW": ("array", ("MMCDW", ), "np.int64"),  # MODELQ.FOR /DWNPAR/ ITRCDW(MMCDW)
    "NCDW": ("scalar", (), "np.int64"),  # MODELQ.FOR /DWNPAR/ NCDW

    # ===== MODELQ.FOR : COMMON /OBFPAR/ =====
    "ITRBF": ("array", ("MBF", ), "np.int64"),  # MODELQ.FOR /OBFPAR/ ITRBF(MBF)

    # ===== MODELQ.FOR : COMMON /GFFPAR/ =====
    "GF0": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /GFFPAR/ GF0(MDEPTH)
    "GF1": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /GFFPAR/ GF1(MDEPTH)
    "GF2": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /GFFPAR/ GF2(MDEPTH)
    "GF3": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /GFFPAR/ GF3(MDEPTH)
    "GF4": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /GFFPAR/ GF4(MDEPTH)
    "GF5": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /GFFPAR/ GF5(MDEPTH)
    "GF6": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /GFFPAR/ GF6(MDEPTH)
    "GF0D": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /GFFPAR/ GF0D(MDEPTH)
    "GF1D": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /GFFPAR/ GF1D(MDEPTH)
    "GF2D": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /GFFPAR/ GF2D(MDEPTH)
    "GF3D": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /GFFPAR/ GF3D(MDEPTH)
    "GF4D": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /GFFPAR/ GF4D(MDEPTH)
    "GF5D": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /GFFPAR/ GF5D(MDEPTH)
    "GF6D": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /GFFPAR/ GF6D(MDEPTH)
    "DELTT": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /GFFPAR/ DELTT(MDEPTH)

    # ===== MODELQ.FOR : COMMON /OFFPAR/ =====
    "SFF3": ("array", ("MION", "MDEPTH", ), "np.float64"),  # MODELQ.FOR /OFFPAR/ SFF3(MION,MDEPTH)
    "SFF2": ("array", ("MION", "MDEPTH", ), "np.float64"),  # MODELQ.FOR /OFFPAR/ SFF2(MION,MDEPTH)
    "DSFF": ("array", ("MION", "MDEPTH", ), "np.float64"),  # MODELQ.FOR /OFFPAR/ DSFF(MION,MDEPTH)
    "CFFN": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /OFFPAR/ CFFN(MDEPTH)
    "CFFT": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /OFFPAR/ CFFT(MDEPTH)

    # ===== MODELQ.FOR : COMMON /OTRPAR/ =====
    "ABTRA": ("array", ("MTRANS", "MDEPTH", ), "np.float64"),  # MODELQ.FOR /OTRPAR/ ABTRA(MTRANS,MDEPTH)
    "EMTRA": ("array", ("MTRANS", "MDEPTH", ), "np.float64"),  # MODELQ.FOR /OTRPAR/ EMTRA(MTRANS,MDEPTH)
    "DEMLT": ("array", ("MTRANS", "MDEPTH", ), "np.float64"),  # MODELQ.FOR /OTRPAR/ DEMLT(MTRANS,MDEPTH)

    # ===== MODELQ.FOR : COMMON /CURRNT/ =====
    "XKF": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /CURRNT/ XKF(MDEPTH)
    "XKF1": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /CURRNT/ XKF1(MDEPTH)
    "XKFB": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /CURRNT/ XKFB(MDEPTH)

    # ===== MODELQ.FOR : COMMON /CUROPA/ =====
    "ABSO1": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /CUROPA/ ABSO1(MDEPTH)
    "EMIS1": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /CUROPA/ EMIS1(MDEPTH)
    "SCAT1": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /CUROPA/ SCAT1(MDEPTH)
    "ABSOT": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /CUROPA/ ABSOT(MDEPTH)
    "ABSOE1": ("array", ("MFREX", ), "np.float64"),  # MODELQ.FOR /CUROPA/ ABSOE1(MFREX)
    "EMEL1": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /CUROPA/ EMEL1(MDEPTH)
    "ABSO1L": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /CUROPA/ ABSO1L(MDEPTH)
    "EMIS1L": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /CUROPA/ EMIS1L(MDEPTH)
    "ABSOPR": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /CUROPA/ ABSOPR(MDEPTH)
    "EMISPR": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /CUROPA/ EMISPR(MDEPTH)

    # ===== MODELQ.FOR : COMMON /TOTRAD/ =====
    "RAD": ("array", ("MFREQ1", "MDEPTH", ), "np.float64"),  # MODELQ.FOR /TOTRAD/ RAD(MFREQ1,MDEPTH)
    "FHD": ("array", ("MFREQ", ), "np.float64"),  # MODELQ.FOR /TOTRAD/ FHD(MFREQ)
    "FAK": ("array", ("MFREQ1", "MDEPTH", ), "np.float64"),  # MODELQ.FOR /TOTRAD/ FAK(MFREQ1,MDEPTH)
    "RADK": ("array", ("MFREQ1", "MDEPTH", ), "np.float64"),  # MODELQ.FOR /TOTRAD/ RADK(MFREQ1,MDEPTH)
    "EXTRAD": ("array", ("MFREQ", ), "np.float64"),  # MODELQ.FOR /TOTRAD/ EXTRAD(MFREQ)
    "EXTINT": ("array", ("MFREQ", "MMU", ), "np.float64"),  # MODELQ.FOR /TOTRAD/ EXTINT(MFREQ,MMU)
    "HEXTRD": ("array", ("MFREQ", ), "np.float64"),  # MODELQ.FOR /TOTRAD/ HEXTRD(MFREQ)
    "TRAD": ("scalar", (), "np.float64"),  # MODELQ.FOR /TOTRAD/ TRAD
    "WDIL": ("scalar", (), "np.float64"),  # MODELQ.FOR /TOTRAD/ WDIL
    "EXTOT": ("scalar", (), "np.float64"),  # MODELQ.FOR /TOTRAD/ EXTOT
    "TSTAR": ("scalar", (), "np.float64"),  # MODELQ.FOR /TOTRAD/ TSTAR

    # ===== MODELQ.FOR : COMMON /CURRAD/ =====
    "RAD1": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /CURRAD/ RAD1(MDEPTH)
    "ALI1": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /CURRAD/ ALI1(MDEPTH)
    "FAK1": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /CURRAD/ FAK1(MDEPTH)
    "radcm": ("array", ("MFREQ", "MDEPTH", ), "np.float64"),  # MODELQ.FOR /CURRAD/ radcm(mfreq,mdepth)
    "RADL": ("array", ("MFREQL", "MDEPTH", ), "np.float64"),  # MODELQ.FOR /CURRAD/ RADL(MFREQL,MDEPTH)
    "ABSALI": ("array", ("MFREQL", "MDEPTH", ), "np.float64"),  # MODELQ.FOR /CURRAD/ ABSALI(MFREQL,MDEPTH)
    "alih1": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /CURRAD/ alih1(mdepth)

    # ===== MODELQ.FOR : COMMON /CURDER/ =====
    "DABT1": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /CURDER/ DABT1(MDEPTH)
    "DEMT1": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /CURDER/ DEMT1(MDEPTH)
    "DABN1": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /CURDER/ DABN1(MDEPTH)
    "DEMN1": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /CURDER/ DEMN1(MDEPTH)
    "DABM1": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /CURDER/ DABM1(MDEPTH)
    "DEMM1": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /CURDER/ DEMM1(MDEPTH)
    "DABX1": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /CURDER/ DABX1(MDEPTH)
    "DEMX1": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /CURDER/ DEMX1(MDEPTH)
    "DABP1": ("array", ("MLEVEL", "MDEPTH", ), "np.float64"),  # MODELQ.FOR /CURDER/ DABP1(MLEVEL,MDEPTH)
    "DEMP1": ("array", ("MLEVEL", "MDEPTH", ), "np.float64"),  # MODELQ.FOR /CURDER/ DEMP1(MLEVEL,MDEPTH)
    "DRCH1": ("array", ("MLEVEL", "MDEPTH", ), "np.float64"),  # MODELQ.FOR /CURDER/ DRCH1(MLEVEL,MDEPTH)
    "DRET1": ("array", ("MLEVEL", "MDEPTH", ), "np.float64"),  # MODELQ.FOR /CURDER/ DRET1(MLEVEL,MDEPTH)
    "ABSFF": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /CURDER/ ABSFF(MDEPTH)
    "DABFT": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /CURDER/ DABFT(MDEPTH)
    "DABFN": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /CURDER/ DABFN(MDEPTH)
    "DSFDT": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /CURDER/ DSFDT(MDEPTH)
    "DSFDN": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /CURDER/ DSFDN(MDEPTH)
    "DSFDM": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /CURDER/ DSFDM(MDEPTH)
    "DSFDP": ("array", ("MLVEXP", "MDEPTH", ), "np.float64"),  # MODELQ.FOR /CURDER/ DSFDP(MLVEXP,MDEPTH)
    "DSFDTM": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /CURDER/ DSFDTM(MDEPTH)
    "DSFDNM": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /CURDER/ DSFDNM(MDEPTH)
    "DSFDPM": ("array", ("MLVEXP", "MDEPTH", ), "np.float64"),  # MODELQ.FOR /CURDER/ DSFDPM(MLVEXP,MDEPTH)
    "DSFDTP": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /CURDER/ DSFDTP(MDEPTH)
    "DSFDNP": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /CURDER/ DSFDNP(MDEPTH)
    "DSFDPP": ("array", ("MLVEXP", "MDEPTH", ), "np.float64"),  # MODELQ.FOR /CURDER/ DSFDPP(MLVEXP,MDEPTH)

    # ===== MODELQ.FOR : COMMON /CURTRI/ =====
    "ALIM1": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /CURTRI/ ALIM1(MDEPTH)
    "ALIP1": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /CURTRI/ ALIP1(MDEPTH)

    # ===== MODELQ.FOR : COMMON /EXPRAF/ =====
    "RADEX": ("array", ("MFREX", "MDEPTH", ), "np.float64"),  # MODELQ.FOR /EXPRAF/ RADEX(MFREX,MDEPTH)
    "FAKEX": ("array", ("MFREX", "MDEPTH", ), "np.float64"),  # MODELQ.FOR /EXPRAF/ FAKEX(MFREX,MDEPTH)

    # ===== MODELQ.FOR : COMMON /TOTPRF/ =====
    "PRFLIN": ("array", ("MDEPTH", "MFREQP", ), "np.float32"),  # MODELQ.FOR /TOTPRF/ PRFLIN(MDEPTH,MFREQP)

    # ===== MODELQ.FOR : COMMON /TOTFLX/ =====
    "FLTOT": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /TOTFLX/ FLTOT(MDEPTH)
    "FLFIX": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /TOTFLX/ FLFIX(MDEPTH)
    "FLEXP": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /TOTFLX/ FLEXP(MDEPTH)
    "FCOOL": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /TOTFLX/ FCOOL(MDEPTH)
    "FCOOLI": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /TOTFLX/ FCOOLI(MDEPTH)
    "FLRD": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /TOTFLX/ FLRD(MDEPTH)
    "FPRAD": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /TOTFLX/ FPRAD(MDEPTH)
    "GRAD": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /TOTFLX/ GRAD(MDEPTH)
    "FPRD": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /TOTFLX/ FPRD(MDEPTH)
    "GRADF": ("array", ("MDEPTH", "MFREQ", ), "np.float64"),  # MODELQ.FOR /TOTFLX/ GRADF(MDEPTH,MFREQ)

    # ===== MODELQ.FOR : COMMON /RRATES/ =====
    "RRU": ("array", ("MTRANS", "MDEPTH", ), "np.float64"),  # MODELQ.FOR /RRATES/ RRU(MTRANS,MDEPTH)
    "RRD": ("array", ("MTRANS", "MDEPTH", ), "np.float64"),  # MODELQ.FOR /RRATES/ RRD(MTRANS,MDEPTH)
    "DRDT": ("array", ("MTRANS", "MDEPTH", ), "np.float64"),  # MODELQ.FOR /RRATES/ DRDT(MTRANS,MDEPTH)

    # ===== MODELQ.FOR : COMMON /RRTOFF/ =====
    "RDDP": ("array", ("MTRAN3", "MDEPTH", ), "np.float64"),  # MODELQ.FOR /RRTOFF/ RDDP(MTRAN3,MDEPTH)
    "RDDM": ("array", ("MTRAN3", "MDEPTH", ), "np.float64"),  # MODELQ.FOR /RRTOFF/ RDDM(MTRAN3,MDEPTH)

    # ===== MODELQ.FOR : COMMON /CRATES/ =====
    "COLRAT": ("array", ("MTRANS", "MDEPTH", ), "np.float64"),  # MODELQ.FOR /CRATES/ COLRAT(MTRANS,MDEPTH)
    "COLTAR": ("array", ("MTRANS", "MDEPTH", ), "np.float64"),  # MODELQ.FOR /CRATES/ COLTAR(MTRANS,MDEPTH)

    # ===== MODELQ.FOR : COMMON /FRQALL/ =====
    "FREQ": ("array", ("MFREQ", ), "np.float64"),  # MODELQ.FOR /FRQALL/ FREQ(MFREQ)
    "W": ("array", ("MFREQ", ), "np.float64"),  # MODELQ.FOR /FRQALL/ W(MFREQ)
    "PROF": ("array", ("MFREQP", ), "np.float64"),  # MODELQ.FOR /FRQALL/ PROF(MFREQP)
    "WCH": ("array", ("MFREQ", ), "np.float64"),  # MODELQ.FOR /FRQALL/ WCH(MFREQ)
    "JIK": ("array", ("MFREQ", ), "np.int64"),  # MODELQ.FOR /FRQALL/ JIK(MFREQ)
    "IJX": ("array", ("MFREQ", ), "np.int64"),  # MODELQ.FOR /FRQALL/ IJX(MFREQ)
    "IJBF": ("array", ("MFREQ", ), "np.int64"),  # MODELQ.FOR /FRQALL/ IJBF(MFREQ)
    "IFS0": ("scalar", (), "np.int64"),  # MODELQ.FOR /FRQALL/ IFS0
    "KIJ": ("array", ("MFREQ", ), "np.int64"),  # MODELQ.FOR /FRQALL/ KIJ(MFREQ)
    "LSKIP": ("array", ("MDEPTH", "MFREQ", ), "bool"),  # MODELQ.FOR /FRQALL/ LSKIP(MDEPTH,MFREQ)

    # ===== MODELQ.FOR : COMMON /FRQINT/ =====
    "FRCMAX": ("scalar", (), "np.float64"),  # MODELQ.FOR /FRQINT/ FRCMAX
    "FRCMIN": ("scalar", (), "np.float64"),  # MODELQ.FOR /FRQINT/ FRCMIN
    "FRLMAX": ("scalar", (), "np.float64"),  # MODELQ.FOR /FRQINT/ FRLMAX
    "FRLMIN": ("scalar", (), "np.float64"),  # MODELQ.FOR /FRQINT/ FRLMIN
    "CFRMAX": ("scalar", (), "np.float64"),  # MODELQ.FOR /FRQINT/ CFRMAX
    "DFTAIL": ("scalar", (), "np.float64"),  # MODELQ.FOR /FRQINT/ DFTAIL
    "TSNU": ("scalar", (), "np.float64"),  # MODELQ.FOR /FRQINT/ TSNU
    "VTNU": ("scalar", (), "np.float64"),  # MODELQ.FOR /FRQINT/ VTNU
    "DDNU": ("scalar", (), "np.float64"),  # MODELQ.FOR /FRQINT/ DDNU
    "CNU1": ("scalar", (), "np.float64"),  # MODELQ.FOR /FRQINT/ CNU1
    "CNU2": ("scalar", (), "np.float64"),  # MODELQ.FOR /FRQINT/ CNU2
    "IELNU": ("scalar", (), "np.int64"),  # MODELQ.FOR /FRQINT/ IELNU
    "NFTAIL": ("scalar", (), "np.int64"),  # MODELQ.FOR /FRQINT/ NFTAIL

    # ===== MODELQ.FOR : COMMON /LINOVR/ =====
    "NITJ": ("array", ("MFREQ", ), "np.int64"),  # MODELQ.FOR /LINOVR/ NITJ(MFREQ)
    "IJLIN": ("array", ("MFREQ", ), "np.int64"),  # MODELQ.FOR /LINOVR/ IJLIN(MFREQ)
    "ITRLIN": ("array", ("MITJ", "MFREQ", ), "np.int16"),  # MODELQ.FOR /LINOVR/ ITRLIN(MITJ,MFREQ)

    # ===== MODELQ.FOR : COMMON /LINFRQ/ =====
    "NLINES": ("array", ("MFREQ", ), "np.int64"),  # MODELQ.FOR /LINFRQ/ NLINES(MFREQ)

    # ===== MODELQ.FOR : COMMON /PHOEXP/ =====
    "AIJBF": ("array", ("MFREQ", ), "np.float64"),  # MODELQ.FOR /PHOEXP/ AIJBF(MFREQ)
    "BFCS": ("array", ("MCROSS", "MFREQC", ), "np.float32"),  # MODELQ.FOR /PHOEXP/ BFCS(MCROSS,MFREQC)
    "IFREQB": ("array", ("MFREQC", ), "np.int64"),  # MODELQ.FOR /PHOEXP/ IFREQB(MFREQC)

    # ===== MODELQ.FOR : COMMON /FREAUX/ =====
    "W0E": ("array", ("MFREQ", ), "np.float64"),  # MODELQ.FOR /FREAUX/ W0E(MFREQ)
    "BNUE": ("array", ("MFREQ", ), "np.float64"),  # MODELQ.FOR /FREAUX/ BNUE(MFREQ)
    "WC": ("array", ("MFREQ", ), "np.float64"),  # MODELQ.FOR /FREAUX/ WC(MFREQ)
    "IJTC": ("array", ("MTRANS", ), "np.int64"),  # MODELQ.FOR /FREAUX/ IJTC(MTRANS)
    "IJALI": ("array", ("MFREQ", ), "np.int64"),  # MODELQ.FOR /FREAUX/ IJALI(MFREQ)
    "IJEX": ("array", ("MFREQ", ), "np.int64"),  # MODELQ.FOR /FREAUX/ IJEX(MFREQ)
    "IJFR": ("array", ("MFREQ", ), "np.int64"),  # MODELQ.FOR /FREAUX/ IJFR(MFREQ)

    # ===== MODELQ.FOR : COMMON /COMPIF/ =====
    "LINEXP": ("array", ("MTRANS", ), "bool"),  # MODELQ.FOR /COMPIF/ LINEXP(MTRANS)

    # ===== MODELQ.FOR : COMMON /SURFAC/ =====
    "FLUX": ("array", ("MFREQ", ), "np.float64"),  # MODELQ.FOR /SURFAC/ FLUX(MFREQ)
    "FH": ("array", ("MFREQ", ), "np.float64"),  # MODELQ.FOR /SURFAC/ FH(MFREQ)
    "Q0": ("array", ("MFREQ", ), "np.float64"),  # MODELQ.FOR /SURFAC/ Q0(MFREQ)
    "UU0": ("array", ("MFREQ", ), "np.float64"),  # MODELQ.FOR /SURFAC/ UU0(MFREQ)

    # ===== MODELQ.FOR : COMMON /FILES/ =====
    "PSY0": ("array", ("MTOT", "MDEPTH", ), "np.float64"),  # MODELQ.FOR /FILES/ PSY0(MTOT,MDEPTH)
    "PSY1": ("array", ("MTOT", "MDEPTH", ), "np.float64"),  # MODELQ.FOR /FILES/ PSY1(MTOT,MDEPTH)
    "PSY2": ("array", ("MTOT", "MDEPTH", ), "np.float64"),  # MODELQ.FOR /FILES/ PSY2(MTOT,MDEPTH)
    "PSY3": ("array", ("MTOT", "MDEPTH", ), "np.float64"),  # MODELQ.FOR /FILES/ PSY3(MTOT,MDEPTH)

    # ===== MODELQ.FOR : COMMON /PRESSR/ =====
    "PTOTAL": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /PRESSR/ PTOTAL(MDEPTH)
    "PGS": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /PRESSR/ PGS(MDEPTH)
    "PRADT": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /PRESSR/ PRADT(MDEPTH)
    "PRADA": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /PRESSR/ PRADA(MDEPTH)

    # ===== MODELQ.FOR : COMMON /HEQAUX/ =====
    "PRD0": ("scalar", (), "np.float64"),  # MODELQ.FOR /HEQAUX/ PRD0
    "IHECOR": ("scalar", (), "np.int64"),  # MODELQ.FOR /HEQAUX/ IHECOR

    # ===== MODELQ.FOR : COMMON /OPMEAN/ =====
    "ABROSD": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /OPMEAN/ ABROSD(MDEPTH)
    "SUMDPL": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /OPMEAN/ SUMDPL(MDEPTH)
    "ABPLAD": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /OPMEAN/ ABPLAD(MDEPTH)
    "ABPMIN": ("scalar", (), "np.float64"),  # MODELQ.FOR /OPMEAN/ ABPMIN

    # ===== MODELQ.FOR : COMMON /CHARFX/ =====
    "QFIX": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /CHARFX/ QFIX(MDEPTH)

    # ===== MODELQ.FOR : COMMON /WINDBL/ =====
    "ALBE": ("array", ("MFREQ", ), "np.float64"),  # MODELQ.FOR /WINDBL/ ALBE(MFREQ)
    "IWINBL": ("scalar", (), "np.int64"),  # MODELQ.FOR /WINDBL/ IWINBL

    # ===== MODELQ.FOR : COMMON /DFEALI/ =====
    "DJMAX": ("scalar", (), "np.float64"),  # MODELQ.FOR /DFEALI/ DJMAX
    "NTRALI": ("scalar", (), "np.int64"),  # MODELQ.FOR /DFEALI/ NTRALI

    # ===== MODELQ.FOR : COMMON /OPACAD/ =====
    "ABAD": ("scalar", (), "np.float64"),  # MODELQ.FOR /OPACAD/ ABAD
    "EMAD": ("scalar", (), "np.float64"),  # MODELQ.FOR /OPACAD/ EMAD
    "SCAD": ("scalar", (), "np.float64"),  # MODELQ.FOR /OPACAD/ SCAD
    "DAT": ("scalar", (), "np.float64"),  # MODELQ.FOR /OPACAD/ DAT
    "DAN": ("scalar", (), "np.float64"),  # MODELQ.FOR /OPACAD/ DAN
    "DET": ("scalar", (), "np.float64"),  # MODELQ.FOR /OPACAD/ DET
    "DEN": ("scalar", (), "np.float64"),  # MODELQ.FOR /OPACAD/ DEN
    "DST": ("scalar", (), "np.float64"),  # MODELQ.FOR /OPACAD/ DST
    "DSN": ("scalar", (), "np.float64"),  # MODELQ.FOR /OPACAD/ DSN
    "DDN": ("array", ("MLEVEL", ), "np.float64"),  # MODELQ.FOR /OPACAD/ DDN(MLEVEL)

    # ===== MODELQ.FOR : COMMON /MODCON/ =====
    "FLXC": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /MODCON/ FLXC(MDEPTH)
    "DELTA": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /MODCON/ DELTA(MDEPTH)

    # ===== MODELQ.FOR : COMMON /RESDER/ =====
    "RSAT": ("scalar", (), "np.float64"),  # MODELQ.FOR /RESDER/ RSAT
    "RSBT": ("scalar", (), "np.float64"),  # MODELQ.FOR /RESDER/ RSBT
    "RSAN": ("scalar", (), "np.float64"),  # MODELQ.FOR /RESDER/ RSAN
    "RSBN": ("scalar", (), "np.float64"),  # MODELQ.FOR /RESDER/ RSBN
    "RSAX": ("array", ("MLEVEL", ), "np.float64"),  # MODELQ.FOR /RESDER/ RSAX(MLEVEL)
    "RSBX": ("array", ("MLEVEL", ), "np.float64"),  # MODELQ.FOR /RESDER/ RSBX(MLEVEL)

    # ===== MODELQ.FOR : COMMON /GRAYTS/ =====
    "TAUROS": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /GRAYTS/ TAUROS(MDEPTH)
    "TAUFLX": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /GRAYTS/ TAUFLX(MDEPTH)
    "TAUTHE": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /GRAYTS/ TAUTHE(MDEPTH)
    "THETA": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /GRAYTS/ THETA(MDEPTH)

    # ===== MODELQ.FOR : COMMON /TAURSS/ =====
    "TROSS": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /TAURSS/ TROSS(MDEPTH)

    # ===== MODELQ.FOR : COMMON /TCONST/ =====
    "TDISK": ("scalar", (), "np.float64"),  # MODELQ.FOR /TCONST/ TDISK
    "ITCONS": ("scalar", (), "np.int64"),  # MODELQ.FOR /TCONST/ ITCONS

    # ===== MODELQ.FOR : COMMON /HYDADD/ =====
    "PHMOL": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /HYDADD/ PHMOL(MDEPTH)
    "ANEREL": ("scalar", (), "np.float64"),  # MODELQ.FOR /HYDADD/ ANEREL
    "IHM": ("scalar", (), "np.int64"),  # MODELQ.FOR /HYDADD/ IHM
    "IH2": ("scalar", (), "np.int64"),  # MODELQ.FOR /HYDADD/ IH2
    "IH2P": ("scalar", (), "np.int64"),  # MODELQ.FOR /HYDADD/ IH2P

    # ===== MODELQ.FOR : COMMON /ELDNSP/ =====
    "ANP": ("scalar", (), "np.float64"),  # MODELQ.FOR /ELDNSP/ ANP
    "AHTOT": ("scalar", (), "np.float64"),  # MODELQ.FOR /ELDNSP/ AHTOT
    "AHMOL": ("scalar", (), "np.float64"),  # MODELQ.FOR /ELDNSP/ AHMOL

    # ===== MODELQ.FOR : COMMON /RRVALS/ =====
    "RR": ("array", ("99", "99", ), "np.float64"),  # MODELQ.FOR /RRVALS/ RR(99,99)
    "ABNDD": ("array", ("99", "MDEPTH", ), "np.float64"),  # MODELQ.FOR /RRVALS/ ABNDD(99,MDEPTH)
    "ENEV": ("array", ("99", "30", ), "np.float64"),  # MODELQ.FOR /RRVALS/ ENEV(99,30)
    "IONIZ": ("array", ("99", ), "np.int64"),  # MODELQ.FOR /RRVALS/ IONIZ(99)
    "IREF": ("scalar", (), "np.int64"),  # MODELQ.FOR /RRVALS/ IREF
    "IREFA": ("scalar", (), "np.int64"),  # MODELQ.FOR /RRVALS/ IREFA
    "LGR": ("array", ("99", ), "bool"),  # MODELQ.FOR /RRVALS/ LGR(99)
    "LRM": ("array", ("99", ), "bool"),  # MODELQ.FOR /RRVALS/ LRM(99)

    # ===== MODELQ.FOR : COMMON /STATEP/ =====
    "Q": ("scalar", (), "np.float64"),  # MODELQ.FOR /STATEP/ Q
    "QM": ("scalar", (), "np.float64"),  # MODELQ.FOR /STATEP/ QM
    "DQT": ("scalar", (), "np.float64"),  # MODELQ.FOR /STATEP/ DQT
    "DQN": ("scalar", (), "np.float64"),  # MODELQ.FOR /STATEP/ DQN
    "DQM": ("scalar", (), "np.float64"),  # MODELQ.FOR /STATEP/ DQM
    "ENER": ("scalar", (), "np.float64"),  # MODELQ.FOR /STATEP/ ENER
    "ENTR": ("scalar", (), "np.float64"),  # MODELQ.FOR /STATEP/ ENTR
    "QREF": ("scalar", (), "np.float64"),  # MODELQ.FOR /STATEP/ QREF
    "DQTR": ("scalar", (), "np.float64"),  # MODELQ.FOR /STATEP/ DQTR
    "DQNR": ("scalar", (), "np.float64"),  # MODELQ.FOR /STATEP/ DQNR
    "PFHYD": ("scalar", (), "np.float64"),  # MODELQ.FOR /STATEP/ PFHYD

    # ===== MODELQ.FOR : COMMON /ODFCHT/ =====
    "CHANT": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /ODFCHT/ CHANT(MDEPTH)

    # ===== MODELQ.FOR : COMMON /STRAUX/ =====
    "XK0": ("array", ("MLINH", ), "np.float64"),  # MODELQ.FOR /STRAUX/ XK0(MLINH)
    "XK": ("scalar", (), "np.float64"),  # MODELQ.FOR /STRAUX/ XK
    "DBETA": ("scalar", (), "np.float64"),  # MODELQ.FOR /STRAUX/ DBETA
    "BETAD": ("scalar", (), "np.float64"),  # MODELQ.FOR /STRAUX/ BETAD
    "ADH": ("scalar", (), "np.float64"),  # MODELQ.FOR /STRAUX/ ADH
    "DIVH": ("scalar", (), "np.float64"),  # MODELQ.FOR /STRAUX/ DIVH

    # ===== MODELQ.FOR : COMMON /STDPAR/ =====
    "ELSTD": ("scalar", (), "np.float64"),  # MODELQ.FOR /STDPAR/ ELSTD
    "IDSTD": ("scalar", (), "np.int64"),  # MODELQ.FOR /STDPAR/ IDSTD

    # ===== MODELQ.FOR : COMMON /HYDPRF/ =====
    "PRFHYD": ("array", ("MLINH", "MHWL", "MHT", "MHE", ), "np.float64"),  # MODELQ.FOR /HYDPRF/ PRFHYD(MLINH,MHWL,MHT,MHE)
    "WLHYD": ("array", ("MLINH", "MHWL", ), "np.float64"),  # MODELQ.FOR /HYDPRF/ WLHYD(MLINH,MHWL)
    "WLH": ("array", ("MHWL", "MLINH", ), "np.float64"),  # MODELQ.FOR /HYDPRF/ WLH(MHWL,MLINH)
    "XTLEM": ("array", ("MHT", "MLINH", ), "np.float64"),  # MODELQ.FOR /HYDPRF/ XTLEM(MHT,MLINH)
    "XNELEM": ("array", ("MHE", "MLINH", ), "np.float64"),  # MODELQ.FOR /HYDPRF/ XNELEM(MHE,MLINH)
    "NWLHYD": ("array", ("MLINH", ), "np.int64"),  # MODELQ.FOR /HYDPRF/ NWLHYD(MLINH)
    "NWLH": ("array", ("MLINH", ), "np.int64"),  # MODELQ.FOR /HYDPRF/ NWLH(MLINH)
    "NTH": ("array", ("MLINH", ), "np.int64"),  # MODELQ.FOR /HYDPRF/ NTH(MLINH)
    "NEH": ("array", ("MLINH", ), "np.int64"),  # MODELQ.FOR /HYDPRF/ NEH(MLINH)
    "ILINH": ("array", ("4", "22", ), "np.int64"),  # MODELQ.FOR /HYDPRF/ ILINH(4,22)
    "IHYDPR": ("scalar", (), "np.int64"),  # MODELQ.FOR /HYDPRF/ IHYDPR

    # ===== MODELQ.FOR : COMMON /XENPRF/ =====
    "PRFXB": ("array", ("MLINH", "MHWL", "MHT", "MHE", ), "np.float64"),  # MODELQ.FOR /XENPRF/ PRFXB(MLINH,MHWL,MHT,MHE)
    "PRFXR": ("array", ("MLINH", "MHWL", "MHT", "MHE", ), "np.float64"),  # MODELQ.FOR /XENPRF/ PRFXR(MLINH,MHWL,MHT,MHE)
    "ALXEN": ("array", ("MLINH", "MHWL", ), "np.float64"),  # MODELQ.FOR /XENPRF/ ALXEN(MLINH,MHWL)
    "XTXEN": ("array", ("MHT", "MLINH", ), "np.float64"),  # MODELQ.FOR /XENPRF/ XTXEN(MHT,MLINH)
    "XNEXEN": ("array", ("MHE", "MLINH", ), "np.float64"),  # MODELQ.FOR /XENPRF/ XNEXEN(MHE,MLINH)
    "XNEMIN": ("scalar", (), "np.float64"),  # MODELQ.FOR /XENPRF/ XNEMIN
    "NWLXEN": ("array", ("MLINH", ), "np.int64"),  # MODELQ.FOR /XENPRF/ NWLXEN(MLINH)
    "NTHXEN": ("array", ("MLINH", ), "np.int64"),  # MODELQ.FOR /XENPRF/ NTHXEN(MLINH)
    "NEHXEN": ("array", ("MLINH", ), "np.int64"),  # MODELQ.FOR /XENPRF/ NEHXEN(MLINH)
    "ILXEN": ("array", ("4", "22", ), "np.int64"),  # MODELQ.FOR /XENPRF/ ILXEN(4,22)
    "IHXENB": ("scalar", (), "np.int64"),  # MODELQ.FOR /XENPRF/ IHXENB

    # ===== MODELQ.FOR : COMMON /LTEGRP/ =====
    "TAUFIR": ("scalar", (), "np.float64"),  # MODELQ.FOR /LTEGRP/ TAUFIR
    "TAULAS": ("scalar", (), "np.float64"),  # MODELQ.FOR /LTEGRP/ TAULAS
    "ABROS0": ("scalar", (), "np.float64"),  # MODELQ.FOR /LTEGRP/ ABROS0
    "TSURF": ("scalar", (), "np.float64"),  # MODELQ.FOR /LTEGRP/ TSURF
    "ALBAVE": ("scalar", (), "np.float64"),  # MODELQ.FOR /LTEGRP/ ALBAVE
    "DION0": ("scalar", (), "np.float64"),  # MODELQ.FOR /LTEGRP/ DION0
    "DM1": ("scalar", (), "np.float64"),  # MODELQ.FOR /LTEGRP/ DM1
    "ABPLA0": ("scalar", (), "np.float64"),  # MODELQ.FOR /LTEGRP/ ABPLA0
    "NNEWD": ("scalar", (), "np.int64"),  # MODELQ.FOR /LTEGRP/ NNEWD
    "NDGREY": ("scalar", (), "np.int64"),  # MODELQ.FOR /LTEGRP/ NDGREY
    "IDGREY": ("scalar", (), "np.int64"),  # MODELQ.FOR /LTEGRP/ IDGREY

    # ===== MODELQ.FOR : COMMON /COMPTF/ =====
    "DLNFR": ("array", ("MFREQ", ), "np.float64"),  # MODELQ.FOR /COMPTF/ DLNFR(MFREQ)
    "BNUS": ("array", ("MFREQ", ), "np.float64"),  # MODELQ.FOR /COMPTF/ BNUS(MFREQ)
    "CDER10": ("array", ("MFREQ", ), "np.float64"),  # MODELQ.FOR /COMPTF/ CDER10(MFREQ)
    "CDER1P": ("array", ("MFREQ", ), "np.float64"),  # MODELQ.FOR /COMPTF/ CDER1P(MFREQ)
    "CDER1M": ("array", ("MFREQ", ), "np.float64"),  # MODELQ.FOR /COMPTF/ CDER1M(MFREQ)
    "CDER20": ("array", ("MFREQ", ), "np.float64"),  # MODELQ.FOR /COMPTF/ CDER20(MFREQ)
    "CDER2P": ("array", ("MFREQ", ), "np.float64"),  # MODELQ.FOR /COMPTF/ CDER2P(MFREQ)
    "CDER2M": ("array", ("MFREQ", ), "np.float64"),  # MODELQ.FOR /COMPTF/ CDER2M(MFREQ)
    "DELJ": ("array", ("MFREQ", "MDEPTH", ), "np.float64"),  # MODELQ.FOR /COMPTF/ DELJ(MFREQ,MDEPTH)

    # ===== MODELQ.FOR : COMMON /VISPAR/ =====
    "TVISC": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /VISPAR/ TVISC(MDEPTH)
    "DTVIST": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /VISPAR/ DTVIST(MDEPTH)
    "DTVISN": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /VISPAR/ DTVISN(MDEPTH)
    "DTVISR": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /VISPAR/ DTVISR(MDEPTH)

    # ===== MODELQ.FOR : COMMON /TABLOP/ =====
    "FRTB1": ("scalar", (), "np.float64"),  # MODELQ.FOR /TABLOP/ FRTB1
    "FRTB2": ("scalar", (), "np.float64"),  # MODELQ.FOR /TABLOP/ FRTB2
    "RTAB1": ("scalar", (), "np.float64"),  # MODELQ.FOR /TABLOP/ RTAB1
    "RTAB2": ("scalar", (), "np.float64"),  # MODELQ.FOR /TABLOP/ RTAB2
    "TTAB1": ("scalar", (), "np.float64"),  # MODELQ.FOR /TABLOP/ TTAB1
    "TTAB2": ("scalar", (), "np.float64"),  # MODELQ.FOR /TABLOP/ TTAB2

    # ===== MODELQ.FOR : COMMON /numbopac/ =====
    "numfreq": ("scalar", (), "np.int64"),  # MODELQ.FOR /numbopac/ numfreq
    "numrho": ("scalar", (), "np.int64"),  # MODELQ.FOR /numbopac/ numrho
    "numtemp": ("scalar", (), "np.int64"),  # MODELQ.FOR /numbopac/ numtemp
    "numrh": ("array", ("MTABT", ), "np.int64"),  # MODELQ.FOR /numbopac/ numrh(mtabt)

    # ===== MODELQ.FOR : COMMON /vectors/ =====
    "tempvec": ("array", ("MTABT", ), "np.float64"),  # MODELQ.FOR /vectors/ tempvec(mtabt)
    "rhovec": ("array", ("MTABR", ), "np.float64"),  # MODELQ.FOR /vectors/ rhovec(mtabr)
    "rhomat": ("array", ("MTABT", "MTABR", ), "np.float64"),  # MODELQ.FOR /vectors/ rhomat(mtabt,mtabr)

    # ===== MODELQ.FOR : COMMON /opacities/ =====
    "frtab": ("array", ("MFRTAB", ), "np.float64"),  # MODELQ.FOR /opacities/ frtab(mfrtab)
    "frtlim": ("scalar", (), "np.float64"),  # MODELQ.FOR /opacities/ frtlim
    "absopac": ("array", ("MTABT", "MTABR", "MFRTAB", ), "np.float64"),  # MODELQ.FOR /opacities/ absopac

    # ===== MODELQ.FOR : COMMON /raytbl/ =====
    "raytab": ("array", ("MTABT", "MTABR", ), "np.float64"),  # MODELQ.FOR /raytbl/ raytab(mtabt,mtabr)
    "raysc": ("array", ("MDEPTH", ), "np.float64"),  # MODELQ.FOR /raytbl/ raysc(mdepth)

    # ===== MODELQ.FOR : COMMON /binopa/ =====
    "ibinop": ("scalar", (), "np.int64"),  # MODELQ.FOR /binopa/ ibinop

    # ===== MODELQ.FOR : COMMON /tabhyg/ =====
    "hglim": ("scalar", (), "np.float64"),  # MODELQ.FOR /tabhyg/ hglim
    "ihgom": ("scalar", (), "np.int64"),  # MODELQ.FOR /tabhyg/ ihgom

    # ===== MODELQ.FOR : COMMON /TABLOH/ =====
    "FRGTB1": ("scalar", (), "np.float64"),  # MODELQ.FOR /TABLOH/ FRGTB1
    "FRGTB2": ("scalar", (), "np.float64"),  # MODELQ.FOR /TABLOH/ FRGTB2
    "EGTAB1": ("scalar", (), "np.float64"),  # MODELQ.FOR /TABLOH/ EGTAB1
    "EGTAB2": ("scalar", (), "np.float64"),  # MODELQ.FOR /TABLOH/ EGTAB2
    "TGTAB1": ("scalar", (), "np.float64"),  # MODELQ.FOR /TABLOH/ TGTAB1
    "TGTAB2": ("scalar", (), "np.float64"),  # MODELQ.FOR /TABLOH/ TGTAB2

    # ===== MODELQ.FOR : COMMON /numgopac/ =====
    "nugfreq": ("scalar", (), "np.int64"),  # MODELQ.FOR /numgopac/ nugfreq
    "nugele": ("scalar", (), "np.int64"),  # MODELQ.FOR /numgopac/ nugele
    "nugtemp": ("scalar", (), "np.int64"),  # MODELQ.FOR /numgopac/ nugtemp

    # ===== MODELQ.FOR : COMMON /vectorg/ =====
    "temvec": ("array", ("mtabth", ), "np.float64"),  # MODELQ.FOR /vectorg/ temvec(mtabth)
    "elevec": ("array", ("mtabeh", ), "np.float64"),  # MODELQ.FOR /vectorg/ elevec(mtabeh)

    # ===== MODELQ.FOR : COMMON /opacitieg/ =====
    "frgtab": ("array", ("mfhtab", ), "np.float64"),  # MODELQ.FOR /opacitieg/ frgtab(mfhtab)
    "hydcrs": ("array", ("mtabth", "mtabeh", "mfhtab", ), "np.float64"),  # MODELQ.FOR /opacitieg/ hydcrs(mtabth,mtabeh,mfhtab)

    # ===== ODFPAR.FOR : COMMON /ODFION/ =====
    "INODF1": ("array", ("MION", ), "np.int64"),  # ODFPAR.FOR /ODFION/ INODF1(MION)
    "INODF2": ("array", ("MION", ), "np.int64"),  # ODFPAR.FOR /ODFION/ INODF2(MION)
    "INBFCS": ("array", ("MION", ), "np.int64"),  # ODFPAR.FOR /ODFION/ INBFCS(MION)
    "IKOBS": ("array", ("MION", ), "np.int64"),  # ODFPAR.FOR /ODFION/ IKOBS(MION)

    # ===== ODFPAR.FOR : COMMON /ODFCTR/ =====
    "FRODF": ("array", ("MLEVEL", ), "np.float64"),  # ODFPAR.FOR /ODFCTR/ FRODF(MLEVEL)
    "NFRODF": ("array", ("MHOD", ), "np.int64"),  # ODFPAR.FOR /ODFCTR/ NFRODF(MHOD)
    "INDODF": ("array", ("MLEVEL", ), "np.int64"),  # ODFPAR.FOR /ODFCTR/ INDODF(MLEVEL)
    "JNDODF": ("array", ("MTRANS", ), "np.int64"),  # ODFPAR.FOR /ODFCTR/ JNDODF(MTRANS)

    # ===== ODFPAR.FOR : COMMON /ODFFRQ/ =====
    "FROS": ("array", ("MFRO", "MHOD", ), "np.float64"),  # ODFPAR.FOR /ODFFRQ/ FROS(MFRO,MHOD)
    "WNUS": ("array", ("MFRO", "MHOD", ), "np.float64"),  # ODFPAR.FOR /ODFFRQ/ WNUS(MFRO,MHOD)
    "XDO": ("array", ("3", "MHOD", ), "np.float64"),  # ODFPAR.FOR /ODFFRQ/ XDO(3,MHOD)
    "KDO": ("array", ("4", "MHOD", ), "np.int64"),  # ODFPAR.FOR /ODFFRQ/ KDO(4,MHOD)

    # ===== ODFPAR.FOR : COMMON /ODFMOD/ =====
    "I1ODF": ("array", ("MLEVEL", ), "np.int64"),  # ODFPAR.FOR /ODFMOD/ I1ODF(MLEVEL)
    "I2ODF": ("array", ("MLEVEL", ), "np.int64"),  # ODFPAR.FOR /ODFMOD/ I2ODF(MLEVEL)
    "NQLODF": ("array", ("MLEVEL", ), "np.int64"),  # ODFPAR.FOR /ODFMOD/ NQLODF(MLEVEL)

    # ===== ODFPAR.FOR : COMMON /ODFSTK/ =====
    "XKIJ": ("array", ("MHOD", "NLMX", ), "np.float64"),  # ODFPAR.FOR /ODFSTK/ XKIJ(MHOD,NLMX)
    "WL0": ("array", ("MHOD", "NLMX", ), "np.float64"),  # ODFPAR.FOR /ODFSTK/ WL0(MHOD,NLMX)
    "FIJ": ("array", ("MHOD", "NLMX", ), "np.float64"),  # ODFPAR.FOR /ODFSTK/ FIJ(MHOD,NLMX)

    # ===== ODFPAR.FOR : COMMON /SPLCOM/ =====
    "SIGFE": ("array", ("MDODF", "MCFE", ), "np.float32"),  # ODFPAR.FOR /SPLCOM/ SIGFE(MDODF,MCFE)
    "FRS1": ("scalar", (), "np.float64"),  # ODFPAR.FOR /SPLCOM/ FRS1
    "FRS2": ("scalar", (), "np.float64"),  # ODFPAR.FOR /SPLCOM/ FRS2
    "DXNU": ("scalar", (), "np.float64"),  # ODFPAR.FOR /SPLCOM/ DXNU
    "XJID": ("array", ("MDEPTH", ), "np.float64"),  # ODFPAR.FOR /SPLCOM/ XJID(MDEPTH)
    "JIDI": ("array", ("MDEPTH", ), "np.int64"),  # ODFPAR.FOR /SPLCOM/ JIDI(MDEPTH)
    "JIDR": ("array", ("MDODF", ), "np.int64"),  # ODFPAR.FOR /SPLCOM/ JIDR(MDODF)
    "JIDS": ("scalar", (), "np.int64"),  # ODFPAR.FOR /SPLCOM/ JIDS
    "JIDN": ("scalar", (), "np.int64"),  # ODFPAR.FOR /SPLCOM/ JIDN
    "NFRS1": ("scalar", (), "np.int64"),  # ODFPAR.FOR /SPLCOM/ NFRS1
    "NFTT": ("scalar", (), "np.int64"),  # ODFPAR.FOR /SPLCOM/ NFTT

    # ===== ODFPAR.FOR : COMMON /OPALIM/ =====
    "M1FILE": ("array", ("NLMX", "MHOD", ), "np.int64"),  # ODFPAR.FOR /OPALIM/ M1FILE(NLMX,MHOD)
    "M2FILE": ("array", ("NLMX", "MHOD", ), "np.int64"),  # ODFPAR.FOR /OPALIM/ M2FILE(NLMX,MHOD)
    "IMERG": ("scalar", (), "np.int64"),  # ODFPAR.FOR /OPALIM/ IMERG

    # ===== ODFPAR.FOR : COMMON /OPLIMT/ =====
    "ALLIM1": ("scalar", (), "np.float64"),  # ODFPAR.FOR /OPLIMT/ ALLIM1
    "ABLIM1": ("scalar", (), "np.float64"),  # ODFPAR.FOR /OPLIMT/ ABLIM1
    "ABLIM2": ("scalar", (), "np.float64"),  # ODFPAR.FOR /OPLIMT/ ABLIM2
    "ABLIM3": ("scalar", (), "np.float64"),  # ODFPAR.FOR /OPLIMT/ ABLIM3

    # ===== ODFPAR.FOR : COMMON /LEVCOM/ =====
    "EMKU": ("array", ("MLEVEL", "2", ), "np.float64"),  # ODFPAR.FOR /LEVCOM/ EMKU(MLEVEL,2)
    "YMKU": ("array", ("MLEVEL", "2", ), "np.float64"),  # ODFPAR.FOR /LEVCOM/ YMKU(MLEVEL,2)
    "XEV": ("array", ("MLEVEL", "MION", ), "np.float64"),  # ODFPAR.FOR /LEVCOM/ XEV(MLEVEL,MION)
    "XOD": ("array", ("MLEVEL", "MION", ), "np.float64"),  # ODFPAR.FOR /LEVCOM/ XOD(MLEVEL,MION)
    "EU": ("array", ("2*MLEVEL", ), "np.float64"),  # ODFPAR.FOR /LEVCOM/ EU(2*MLEVEL)
    "JEN": ("array", ("2*MLEVEL", ), "np.int64"),  # ODFPAR.FOR /LEVCOM/ JEN(2*MLEVEL)
    "EEV": ("array", ("MKULEV", ), "np.float64"),  # ODFPAR.FOR /LEVCOM/ EEV(MKULEV)
    "AEV": ("array", ("MKULEV", ), "np.float64"),  # ODFPAR.FOR /LEVCOM/ AEV(MKULEV)
    "SEV": ("array", ("MKULEV", ), "np.float64"),  # ODFPAR.FOR /LEVCOM/ SEV(MKULEV)
    "WEV": ("array", ("MKULEV", ), "np.float64"),  # ODFPAR.FOR /LEVCOM/ WEV(MKULEV)
    "EOD": ("array", ("MKULEV", ), "np.float64"),  # ODFPAR.FOR /LEVCOM/ EOD(MKULEV)
    "AOD": ("array", ("MKULEV", ), "np.float64"),  # ODFPAR.FOR /LEVCOM/ AOD(MKULEV)
    "SOD": ("array", ("MKULEV", ), "np.float64"),  # ODFPAR.FOR /LEVCOM/ SOD(MKULEV)
    "WOD": ("array", ("MKULEV", ), "np.float64"),  # ODFPAR.FOR /LEVCOM/ WOD(MKULEV)
    "KSEV": ("array", ("MKULEV", ), "np.int64"),  # ODFPAR.FOR /LEVCOM/ KSEV(MKULEV)
    "KSOD": ("array", ("MKULEV", ), "np.int64"),  # ODFPAR.FOR /LEVCOM/ KSOD(MKULEV)
    "NEVKU": ("array", ("MION", ), "np.int64"),  # ODFPAR.FOR /LEVCOM/ NEVKU(MION)
    "NODKU": ("array", ("MION", ), "np.int64"),  # ODFPAR.FOR /LEVCOM/ NODKU(MION)
    "NLEVKU": ("scalar", (), "np.int64"),  # ODFPAR.FOR /LEVCOM/ NLEVKU
    "NLINKU": ("scalar", (), "np.int64"),  # ODFPAR.FOR /LEVCOM/ NLINKU
    "KEVE": ("scalar", (), "np.int64"),  # ODFPAR.FOR /LEVCOM/ KEVE
    "KODD": ("scalar", (), "np.int64"),  # ODFPAR.FOR /LEVCOM/ KODD

    # ===== ALIPAR.FOR : COMMON /FIXALP/ =====
    "ABSO": ("array", ("MFREQ", ), "np.float64"),  # ALIPAR.FOR /FIXALP/ ABSO(MFREQ)
    "EMIS": ("array", ("MFREQ", ), "np.float64"),  # ALIPAR.FOR /FIXALP/ EMIS(MFREQ)
    "SCAT": ("array", ("MFREQ", ), "np.float64"),  # ALIPAR.FOR /FIXALP/ SCAT(MFREQ)
    "REIT": ("array", ("MDEPTH", ), "np.float64"),  # ALIPAR.FOR /FIXALP/ REIT(MDEPTH)
    "REIN": ("array", ("MDEPTH", ), "np.float64"),  # ALIPAR.FOR /FIXALP/ REIN(MDEPTH)
    "REIM": ("array", ("MDEPTH", ), "np.float64"),  # ALIPAR.FOR /FIXALP/ REIM(MDEPTH)
    "REIP": ("array", ("MLVEXP", "MDEPTH", ), "np.float64"),  # ALIPAR.FOR /FIXALP/ REIP(MLVEXP,MDEPTH)
    "AREIT": ("array", ("MDEPTH", ), "np.float64"),  # ALIPAR.FOR /FIXALP/ AREIT(MDEPTH)
    "AREIN": ("array", ("MDEPTH", ), "np.float64"),  # ALIPAR.FOR /FIXALP/ AREIN(MDEPTH)
    "AREIM": ("array", ("MDEPTH", ), "np.float64"),  # ALIPAR.FOR /FIXALP/ AREIM(MDEPTH)
    "AREIP": ("array", ("MLVEXP", "MDEPTH", ), "np.float64"),  # ALIPAR.FOR /FIXALP/ AREIP(MLVEXP,MDEPTH)
    "CREIT": ("array", ("MDEPTH", ), "np.float64"),  # ALIPAR.FOR /FIXALP/ CREIT(MDEPTH)
    "CREIN": ("array", ("MDEPTH", ), "np.float64"),  # ALIPAR.FOR /FIXALP/ CREIN(MDEPTH)
    "CREIM": ("array", ("MDEPTH", ), "np.float64"),  # ALIPAR.FOR /FIXALP/ CREIM(MDEPTH)
    "CREIP": ("array", ("MLVEXP", "MDEPTH", ), "np.float64"),  # ALIPAR.FOR /FIXALP/ CREIP(MLVEXP,MDEPTH)
    "REIX": ("array", ("MDEPTH", ), "np.float64"),  # ALIPAR.FOR /FIXALP/ REIX(MDEPTH)
    "CREIX": ("array", ("MDEPTH", ), "np.float64"),  # ALIPAR.FOR /FIXALP/ CREIX(MDEPTH)
    "REDX": ("array", ("MDEPTH", ), "np.float64"),  # ALIPAR.FOR /FIXALP/ REDX(MDEPTH)
    "REDT": ("array", ("MDEPTH", ), "np.float64"),  # ALIPAR.FOR /FIXALP/ REDT(MDEPTH)
    "REDN": ("array", ("MDEPTH", ), "np.float64"),  # ALIPAR.FOR /FIXALP/ REDN(MDEPTH)
    "REDM": ("array", ("MDEPTH", ), "np.float64"),  # ALIPAR.FOR /FIXALP/ REDM(MDEPTH)
    "REDP": ("array", ("MLVEXP", "MDEPTH", ), "np.float64"),  # ALIPAR.FOR /FIXALP/ REDP(MLVEXP,MDEPTH)
    "REDXM": ("array", ("MDEPTH", ), "np.float64"),  # ALIPAR.FOR /FIXALP/ REDXM(MDEPTH)
    "REDTM": ("array", ("MDEPTH", ), "np.float64"),  # ALIPAR.FOR /FIXALP/ REDTM(MDEPTH)
    "REDNM": ("array", ("MDEPTH", ), "np.float64"),  # ALIPAR.FOR /FIXALP/ REDNM(MDEPTH)
    "REDMM": ("array", ("MDEPTH", ), "np.float64"),  # ALIPAR.FOR /FIXALP/ REDMM(MDEPTH)
    "REDPM": ("array", ("MLVEXP", "MDEPTH", ), "np.float64"),  # ALIPAR.FOR /FIXALP/ REDPM(MLVEXP,MDEPTH)
    "REDTP": ("array", ("MDEPTH", ), "np.float64"),  # ALIPAR.FOR /FIXALP/ REDTP(MDEPTH)
    "REDNP": ("array", ("MDEPTH", ), "np.float64"),  # ALIPAR.FOR /FIXALP/ REDNP(MDEPTH)
    "REDXP": ("array", ("MDEPTH", ), "np.float64"),  # ALIPAR.FOR /FIXALP/ REDXP(MDEPTH)
    "REDMP": ("array", ("MDEPTH", ), "np.float64"),  # ALIPAR.FOR /FIXALP/ REDMP(MDEPTH)
    "REDPP": ("array", ("MLVEXP", "MDEPTH", ), "np.float64"),  # ALIPAR.FOR /FIXALP/ REDPP(MLVEXP,MDEPTH)
    "HEIT": ("array", ("MDEPTH", ), "np.float64"),  # ALIPAR.FOR /FIXALP/ HEIT(MDEPTH)
    "HEIN": ("array", ("MDEPTH", ), "np.float64"),  # ALIPAR.FOR /FIXALP/ HEIN(MDEPTH)
    "HEIM": ("array", ("MDEPTH", ), "np.float64"),  # ALIPAR.FOR /FIXALP/ HEIM(MDEPTH)
    "HEIP": ("array", ("MLVEXP", "MDEPTH", ), "np.float64"),  # ALIPAR.FOR /FIXALP/ HEIP(MLVEXP,MDEPTH)
    "HEITM": ("array", ("MDEPTH", ), "np.float64"),  # ALIPAR.FOR /FIXALP/ HEITM(MDEPTH)
    "HEINM": ("array", ("MDEPTH", ), "np.float64"),  # ALIPAR.FOR /FIXALP/ HEINM(MDEPTH)
    "HEIMM": ("array", ("MDEPTH", ), "np.float64"),  # ALIPAR.FOR /FIXALP/ HEIMM(MDEPTH)
    "HEIPM": ("array", ("MLVEXP", "MDEPTH", ), "np.float64"),  # ALIPAR.FOR /FIXALP/ HEIPM(MLVEXP,MDEPTH)
    "HEITP": ("array", ("MDEPTH", ), "np.float64"),  # ALIPAR.FOR /FIXALP/ HEITP(MDEPTH)
    "HEINP": ("array", ("MDEPTH", ), "np.float64"),  # ALIPAR.FOR /FIXALP/ HEINP(MDEPTH)
    "HEIMP": ("array", ("MDEPTH", ), "np.float64"),  # ALIPAR.FOR /FIXALP/ HEIMP(MDEPTH)
    "HEIPP": ("array", ("MLVEXP", "MDEPTH", ), "np.float64"),  # ALIPAR.FOR /FIXALP/ HEIPP(MLVEXP,MDEPTH)
    "EHET": ("array", ("MDEPTH", ), "np.float64"),  # ALIPAR.FOR /FIXALP/ EHET(MDEPTH)
    "EHEN": ("array", ("MDEPTH", ), "np.float64"),  # ALIPAR.FOR /FIXALP/ EHEN(MDEPTH)
    "ERET": ("array", ("MDEPTH", ), "np.float64"),  # ALIPAR.FOR /FIXALP/ ERET(MDEPTH)
    "EREN": ("array", ("MDEPTH", ), "np.float64"),  # ALIPAR.FOR /FIXALP/ EREN(MDEPTH)
    "EHEP": ("array", ("MLVEX3", "MDEPTH", ), "np.float64"),  # ALIPAR.FOR /FIXALP/ EHEP(MLVEX3,MDEPTH)
    "EREP": ("array", ("MLVEX3", "MDEPTH", ), "np.float64"),  # ALIPAR.FOR /FIXALP/ EREP(MLVEX3,MDEPTH)
    "APT": ("array", ("MLVEXP", "MDEPTH", ), "np.float64"),  # ALIPAR.FOR /FIXALP/ APT(MLVEXP,MDEPTH)
    "APN": ("array", ("MLVEXP", "MDEPTH", ), "np.float64"),  # ALIPAR.FOR /FIXALP/ APN(MLVEXP,MDEPTH)
    "AAPT": ("array", ("MLVEX3", "MDEPTH", ), "np.float64"),  # ALIPAR.FOR /FIXALP/ AAPT(MLVEX3,MDEPTH)
    "AAPN": ("array", ("MLVEX3", "MDEPTH", ), "np.float64"),  # ALIPAR.FOR /FIXALP/ AAPN(MLVEX3,MDEPTH)
    "CAPT": ("array", ("MLVEX3", "MDEPTH", ), "np.float64"),  # ALIPAR.FOR /FIXALP/ CAPT(MLVEX3,MDEPTH)
    "CAPN": ("array", ("MLVEX3", "MDEPTH", ), "np.float64"),  # ALIPAR.FOR /FIXALP/ CAPN(MLVEX3,MDEPTH)
    "APP": ("array", ("MLVEXP", "MLVEXP", "MDEPTH", ), "np.float64"),  # ALIPAR.FOR /FIXALP/ APP(MLVEXP,MLVEXP,MDEPTH)
    "AAPP": ("array", ("MLVEX3", "MLVEX3", "MDEPTH", ), "np.float64"),  # ALIPAR.FOR /FIXALP/ AAPP(MLVEX3,MLVEX3,MDEPTH)
    "CAPP": ("array", ("MLVEX3", "MLVEX3", "MDEPTH", ), "np.float64"),  # ALIPAR.FOR /FIXALP/ CAPP(MLVEX3,MLVEX3,MDEPTH)
    "QTLAS": ("scalar", (), "np.float64"),  # ALIPAR.FOR /FIXALP/ QTLAS
    "IFALI": ("scalar", (), "np.int64"),  # ALIPAR.FOR /FIXALP/ IFALI
    "IFPOPR": ("scalar", (), "np.int64"),  # ALIPAR.FOR /FIXALP/ IFPOPR
    "irprec": ("scalar", (), "np.int64"),  # ALIPAR.FOR /FIXALP/ irprec
    "ifprec": ("scalar", (), "np.int64"),  # ALIPAR.FOR /FIXALP/ ifprec
    "itold1": ("scalar", (), "np.int64"),  # ALIPAR.FOR /FIXALP/ itold1
    "itold2": ("scalar", (), "np.int64"),  # ALIPAR.FOR /FIXALP/ itold2
    "itlas": ("scalar", (), "np.int64"),  # ALIPAR.FOR /FIXALP/ itlas


    # ================================================================
    # inline COMMON supplement: the following blocks are declared only inside
    # individual subroutines of tlusty208.f, not in the 7 include files. Extracted
    # from tlusty208.f by a one-off /tmp script; cross-reference table in INLINE_COMMONS.md.
    # ================================================================

    # ===== inline COMMON /abntab/(supplemental) =====
    # Appears in: TABINI:44476; CHCTAB:44939
    "abunt": ("array", ("MATOM", ), "np.float64"),  # inline /abntab/ abunt(matom)
    "abuno": ("array", ("MATOM", ), "np.float64"),  # inline /abntab/ abuno(matom)
    "tmolit": ("scalar", (), "np.float64"),  # inline /abntab/ tmolit
    "iophmt": ("scalar", (), "np.int64"),  # inline /abntab/ iophmt
    "ioph2t": ("scalar", (), "np.int64"),  # inline /abntab/ ioph2t
    "iophet": ("scalar", (), "np.int64"),  # inline /abntab/ iophet
    "iopcht": ("scalar", (), "np.int64"),  # inline /abntab/ iopcht
    "iopoht": ("scalar", (), "np.int64"),  # inline /abntab/ iopoht
    "ioh2mt": ("scalar", (), "np.int64"),  # inline /abntab/ ioh2mt
    "ih2h2t": ("scalar", (), "np.int64"),  # inline /abntab/ ih2h2t
    "ih2het": ("scalar", (), "np.int64"),  # inline /abntab/ ih2het
    "ioh2ht": ("scalar", (), "np.int64"),  # inline /abntab/ ioh2ht
    "iohhet": ("scalar", (), "np.int64"),  # inline /abntab/ iohhet
    "ifmolt": ("scalar", (), "np.int64"),  # inline /abntab/ ifmolt

    # ===== inline COMMON /ADCHAR/(supplemental) =====
    # Appears in: ELCOR:5727; BPOPC:18484; MOLEQ:45833
    "QADD": ("array", ("MDEPTH", ), "np.float64"),  # inline /ADCHAR/ QADD(MDEPTH)

    # ===== inline COMMON /adiaba/(supplemental) =====
    # Appears in: NSTPAR:1681; TRMDER:27290
    "grdad0": ("scalar", (), "np.float64"),  # inline /adiaba/ grdad0
    "itgrad": ("scalar", (), "np.int64"),  # inline /adiaba/ itgrad

    # ===== inline COMMON /auxcbc/(supplemental) =====
    # Appears in: COMSET:38062; RTECF0:38564; COMPT0:39589
    "cden1m": ("array", ("MDEPTH", ), "np.float64"),  # inline /auxcbc/ cden1m(mdepth)
    "cden10": ("array", ("MDEPTH", ), "np.float64"),  # inline /auxcbc/ cden10(mdepth)
    "cden2m": ("array", ("MDEPTH", ), "np.float64"),  # inline /auxcbc/ cden2m(mdepth)
    "cden20": ("array", ("MDEPTH", ), "np.float64"),  # inline /auxcbc/ cden20(mdepth)

    # ===== inline COMMON /AUXRTE/(supplemental) =====
    # Appears in: RTECF0:38560; RTECOM:38767; RTECF1:38956; RTECMC:39403; RTECMU:39800
    "COMA": ("array", ("MDEPTH", ), "np.float64"),  # inline /AUXRTE/ COMA(MDEPTH)
    "COMB": ("array", ("MDEPTH", ), "np.float64"),  # inline /AUXRTE/ COMB(MDEPTH)
    "COMC": ("array", ("MDEPTH", ), "np.float64"),  # inline /AUXRTE/ COMC(MDEPTH)
    "VL": ("array", ("MDEPTH", ), "np.float64"),  # inline /AUXRTE/ VL(MDEPTH)
    "COME": ("array", ("MDEPTH", ), "np.float64"),  # inline /AUXRTE/ COME(MDEPTH)
    "U": ("array", ("MDEPTH", ), "np.float64"),  # inline /AUXRTE/ U(MDEPTH)
    "V": ("array", ("MDEPTH", ), "np.float64"),  # inline /AUXRTE/ V(MDEPTH)
    "BS": ("array", ("MDEPTH", ), "np.float64"),  # inline /AUXRTE/ BS(MDEPTH)
    "AL": ("array", ("MDEPTH", ), "np.float64"),  # inline /AUXRTE/ AL(MDEPTH)
    "BE": ("array", ("MDEPTH", ), "np.float64"),  # inline /AUXRTE/ BE(MDEPTH)
    "GA": ("array", ("MDEPTH", ), "np.float64"),  # inline /AUXRTE/ GA(MDEPTH)

    # ===== inline COMMON /callarda/(supplemental) =====
    # Appears in: GETLAL:43850; ALLARD:43976
    "xlalp": ("array", ("1400", ), "np.float64"),  # inline /callarda/ xlalp(NXMAX)
    "plalp": ("array", ("1400", "5", ), "np.float64"),  # inline /callarda/ plalp(NXMAX,NNMAX)
    "stnnea": ("scalar", (), "np.float64"),  # inline /callarda/ stnnea
    "stncha": ("scalar", (), "np.float64"),  # inline /callarda/ stncha
    "vneua": ("scalar", (), "np.float64"),  # inline /callarda/ vneua
    "vchaa": ("scalar", (), "np.float64"),  # inline /callarda/ vchaa
    "nxalp": ("scalar", (), "np.int64"),  # inline /callarda/ nxalp
    "iwarna": ("scalar", (), "np.int64"),  # inline /callarda/ iwarna

    # ===== inline COMMON /callardb/(supplemental) =====
    # Appears in: GETLAL:43852; ALLARD:43978
    "xlbet": ("array", ("1400", ), "np.float64"),  # inline /callardb/ xlbet(NXMAX)
    "plbet": ("array", ("1400", "5", ), "np.float64"),  # inline /callardb/ plbet(NXMAX,NNMAX)
    "stnneb": ("scalar", (), "np.float64"),  # inline /callardb/ stnneb
    "stnchb": ("scalar", (), "np.float64"),  # inline /callardb/ stnchb
    "vneub": ("scalar", (), "np.float64"),  # inline /callardb/ vneub
    "vchab": ("scalar", (), "np.float64"),  # inline /callardb/ vchab
    "nxbet": ("scalar", (), "np.int64"),  # inline /callardb/ nxbet
    "iwarnb": ("scalar", (), "np.int64"),  # inline /callardb/ iwarnb

    # ===== inline COMMON /callardc/(supplemental) =====
    # Appears in: GETLAL:43856; ALLARD:43982
    "xlbal": ("array", ("1400", ), "np.float64"),  # inline /callardc/ xlbal(NXMAX)
    "plbal": ("array", ("1400", "5", ), "np.float64"),  # inline /callardc/ plbal(NXMAX,NNMAX)
    "stnnec": ("scalar", (), "np.float64"),  # inline /callardc/ stnnec
    "stnchc": ("scalar", (), "np.float64"),  # inline /callardc/ stnchc
    "vneuc": ("scalar", (), "np.float64"),  # inline /callardc/ vneuc
    "vchac": ("scalar", (), "np.float64"),  # inline /callardc/ vchac
    "nxbal": ("scalar", (), "np.int64"),  # inline /callardc/ nxbal
    "iwarnc": ("scalar", (), "np.int64"),  # inline /callardc/ iwarnc

    # ===== inline COMMON /callardg/(supplemental) =====
    # Appears in: GETLAL:43854; ALLARD:43980
    "xlgam": ("array", ("1400", ), "np.float64"),  # inline /callardg/ xlgam(NXMAX)
    "plgam": ("array", ("1400", "5", ), "np.float64"),  # inline /callardg/ plgam(NXMAX,NNMAX)
    "stnneg": ("scalar", (), "np.float64"),  # inline /callardg/ stnneg
    "stnchg": ("scalar", (), "np.float64"),  # inline /callardg/ stnchg
    "vneug": ("scalar", (), "np.float64"),  # inline /callardg/ vneug
    "vchag": ("scalar", (), "np.float64"),  # inline /callardg/ vchag
    "nxgam": ("scalar", (), "np.int64"),  # inline /callardg/ nxgam
    "iwarng": ("scalar", (), "np.int64"),  # inline /callardg/ iwarng

    # ===== inline COMMON /calphatd/(supplemental) =====
    # Appears in: GETLAL:43858; ALLARD:43984; ALLARDT:44191
    "xlalpd": ("array", ("1400", "6", ), "np.float64"),  # inline /calphatd/ xlalpd(NXMAX,NTAMAX)
    "plalpd": ("array", ("1400", "5", "6", ), "np.float64"),  # inline /calphatd/ plalpd(NXMAX,NNMAX,NTAMAX)
    "stnead": ("array", ("6", ), "np.float64"),  # inline /calphatd/ stnead(ntamax)
    "stnchd": ("array", ("6", ), "np.float64"),  # inline /calphatd/ stnchd(ntamax)
    "vneuad": ("array", ("6", ), "np.float64"),  # inline /calphatd/ vneuad(ntamax)
    "vchaad": ("array", ("6", ), "np.float64"),  # inline /calphatd/ vchaad(ntamax)
    "talpd": ("array", ("6", ), "np.float64"),  # inline /calphatd/ talpd(ntamax)
    "nxalpd": ("array", ("6", ), "np.int64"),  # inline /calphatd/ nxalpd(ntamax)
    "ntalpd": ("scalar", (), "np.int64"),  # inline /calphatd/ ntalpd

    # ===== inline COMMON /CC/(supplemental) =====
    # Appears in: TRMDRT:45671
    "DPDR": ("scalar", (), "np.float64"),  # inline /CC/ DPDR
    "DPDT": ("scalar", (), "np.float64"),  # inline /CC/ DPDT
    "DSDT": ("scalar", (), "np.float64"),  # inline /CC/ DSDT
    "DSDR": ("scalar", (), "np.float64"),  # inline /CC/ DSDR
    "CV": ("scalar", (), "np.float64"),  # inline /CC/ CV
    "S": ("scalar", (), "np.float64"),  # inline /CC/ S
    "GAMMA": ("scalar", (), "np.float64"),  # inline /CC/ GAMMA

    # ===== inline COMMON /CMATZD/(supplemental) =====
    # Appears in: SOLVE:14472; SOLVES:14798; BHED:16679
    "CZZ": ("scalar", (), "np.float64"),  # inline /CMATZD/ CZZ
    "CZN": ("scalar", (), "np.float64"),  # inline /CMATZD/ CZN
    "CZE": ("scalar", (), "np.float64"),  # inline /CMATZD/ CZE
    "CZM": ("scalar", (), "np.float64"),  # inline /CMATZD/ CZM

    # ===== inline COMMON /COLKUR/(supplemental) =====
    # Appears in: LEVCD:36492; INKUL:36763
    "OMES": ("array", ("100", "100", ), "np.float64"),  # inline /COLKUR/ OMES(100,100)
    "EKU": ("array", ("15000", ), "np.float64"),  # inline /COLKUR/ EKU(15000)
    "GKU": ("array", ("15000", ), "np.float64"),  # inline /COLKUR/ GKU(15000)
    "GST": ("scalar", (), "np.float64"),  # inline /COLKUR/ GST
    "KKU": ("array", ("15000", ), "np.int64"),  # inline /COLKUR/ KKU(15000)

    # ===== inline COMMON /COMFH1/(supplemental) =====
    # Appears in: MOLEQ:45821; RUSSEL:46119
    "COMFH1_C": ("array", ("600", "5", ), "np.float64"),  # inline /COMFH1/ C(600,5)
    "PPMOL": ("array", ("600", ), "np.float64"),  # inline /COMFH1/ PPMOL(600)
    "APMLOG": ("array", ("600", ), "np.float64"),  # inline /COMFH1/ APMLOG(600)
    "XIP": ("array", ("100", ), "np.float64"),  # inline /COMFH1/ XIP(100)
    "XIP2": ("array", ("100", ), "np.float64"),  # inline /COMFH1/ XIP2(100)
    "CCOMP": ("array", ("100", ), "np.float64"),  # inline /COMFH1/ CCOMP(100)
    "UIIDUI": ("array", ("100", ), "np.float64"),  # inline /COMFH1/ UIIDUI(100)
    "P": ("array", ("100", ), "np.float64"),  # inline /COMFH1/ P(100)
    "FP": ("array", ("100", ), "np.float64"),  # inline /COMFH1/ FP(100)
    "XKP": ("array", ("100", ), "np.float64"),  # inline /COMFH1/ XKP(100)
    "XK2": ("array", ("100", ), "np.float64"),  # inline /COMFH1/ XK2(100)
    "EPS": ("scalar", (), "np.float64"),  # inline /COMFH1/ EPS
    "SWITER": ("scalar", (), "np.float64"),  # inline /COMFH1/ SWITER
    "NELEM": ("array", ("5", "600", ), "np.int64"),  # inline /COMFH1/ NELEM(5,600)
    "NATO": ("array", ("5", "600", ), "np.int64"),  # inline /COMFH1/ NATO(5,600)
    "MMAX": ("array", ("600", ), "np.int64"),  # inline /COMFH1/ MMAX(600)
    "NELEMX": ("array", ("100", ), "np.int64"),  # inline /COMFH1/ NELEMX(100)
    "NMETAL": ("scalar", (), "np.int64"),  # inline /COMFH1/ NMETAL
    "NMOLEC": ("scalar", (), "np.int64"),  # inline /COMFH1/ NMOLEC
    "NIMAX": ("scalar", (), "np.int64"),  # inline /COMFH1/ NIMAX

    # ===== inline COMMON /comgfs/(supplemental) =====
    # Appears in: COMSET:38064; INICOM:38731; RTECOM:38771; RTECF1:38960; RTECMC:39407
    "gfm": ("array", ("MFREQ", "MDEPTC", ), "np.float64"),  # inline /comgfs/ gfm(mfreq,mdeptc)
    "gfp": ("array", ("MFREQ", "MDEPTC", ), "np.float64"),  # inline /comgfs/ gfp(mfreq,mdeptc)

    # ===== inline COMMON /CONVOUT/(supplemental) =====
    # Appears in: TRMDRT:45672
    "CFLX": ("array", ("MDEPTH", ), "np.float64"),  # inline /CONVOUT/ CFLX(MDEPTH)
    "VELCON": ("array", ("MDEPTH", ), "np.float64"),  # inline /CONVOUT/ VELCON(MDEPTH)
    "GRADAD": ("array", ("MDEPTH", ), "np.float64"),  # inline /CONVOUT/ GRADAD(MDEPTH)
    "ENT": ("array", ("MDEPTH", ), "np.float64"),  # inline /CONVOUT/ ENT(MDEPTH)

    # ===== inline COMMON /COOLCO/(supplemental) =====
    # Appears in: COOLRT:43047; OPACFA:43163
    "ABSOTI": ("array", ("MION", "MDEPTH", ), "np.float64"),  # inline /COOLCO/ ABSOTI(MION,MDEPTH)
    "EMISTI": ("array", ("MION", "MDEPTH", ), "np.float64"),  # inline /COOLCO/ EMISTI(MION,MDEPTH)
    "ABSOC1": ("array", ("MDEPTH", ), "np.float64"),  # inline /COOLCO/ ABSOC1(MDEPTH)
    "EMISC1": ("array", ("MDEPTH", ), "np.float64"),  # inline /COOLCO/ EMISC1(MDEPTH)

    # ===== inline COMMON /CTIon/(supplemental) =====
    # Appears in: HCTION:11649; BLOCK_DATA@11672:11679
    "CTIon": ("array", ("7", "4", "30", ), "np.float64"),  # inline /CTIon/ CTIon(7,4,30)

    # ===== inline COMMON /CTRecomb/(supplemental) =====
    # Appears in: HCTRECOM:11615; BLOCK_DATA@11672:11684
    "CTRecomb": ("array", ("6", "4", "30", ), "np.float64"),  # inline /CTRecomb/ CTRecomb(6,4,30)

    # ===== inline COMMON /CTRTEMP/(supplemental) =====
    # Appears in: COLIS:11212; HCTRECOM:11614; HCTION:11648
    "te": ("scalar", (), "np.float64"),  # inline /CTRTEMP/ te

    # ===== inline COMMON /CUBCON/(supplemental) =====
    # Appears in: RHSGEN:22167; CONTMP:26343; CONTMD:26572; CONVEC:27142; CONVC1:27214; CUBIC:27368; CONOUT:27434; MATCON:27606; TEMCOR:27831; CONREF:27981; LTEGRD:40925; RYBENE:47249
    "ACNV": ("scalar", (), "np.float64"),  # inline /CUBCON/ ACNV/A
    "BCNV": ("scalar", (), "np.float64"),  # inline /CUBCON/ BCNV/B
    "DEL": ("scalar", (), "np.float64"),  # inline /CUBCON/ DEL/DDEL
    "GRDADB": ("scalar", (), "np.float64"),  # inline /CUBCON/ GRDADB
    "DELMDE": ("scalar", (), "np.float64"),  # inline /CUBCON/ DELMDE/DLT
    "RHO": ("scalar", (), "np.float64"),  # inline /CUBCON/ RHO
    "FLXTOT": ("scalar", (), "np.float64"),  # inline /CUBCON/ FLXTOT
    "GRAVD": ("scalar", (), "np.float64"),  # inline /CUBCON/ GRAVD

    # ===== inline COMMON /DEPTDR/(supplemental) =====
    # Appears in: PZEVLD:28377; DMDER:40712
    "DDM": ("array", ("MDEPTH", ), "np.float64"),  # inline /DEPTDR/ DDM(MDEPTH)
    "DDP": ("array", ("MDEPTH", ), "np.float64"),  # inline /DEPTDR/ DDP(MDEPTH)
    "DD0": ("array", ("MDEPTH", ), "np.float64"),  # inline /DEPTDR/ DD0(MDEPTH)
    "DDMIN": ("array", ("MDEPTH", ), "np.float64"),  # inline /DEPTDR/ DDMIN(MDEPTH)
    "DDPLU": ("array", ("MDEPTH", ), "np.float64"),  # inline /DEPTDR/ DDPLU(MDEPTH)
    "DDA": ("array", ("MDEPTH", ), "np.float64"),  # inline /DEPTDR/ DDA(MDEPTH)
    "DDC": ("array", ("MDEPTH", ), "np.float64"),  # inline /DEPTDR/ DDC(MDEPTH)
    "DDB": ("array", ("MDEPTH", ), "np.float64"),  # inline /DEPTDR/ DDB(MDEPTH)

    # ===== inline COMMON /derdif/(supplemental) =====
    # Appears in: NSTPAR:1680; TRMDER:27288
    "dift": ("scalar", (), "np.float64"),  # inline /derdif/ dift
    "difp": ("scalar", (), "np.float64"),  # inline /derdif/ difp

    # ===== inline COMMON /deridt/(supplemental) =====
    # Appears in: NSTPAR:1674; RYBENE:47254
    "dert": ("scalar", (), "np.float64"),  # inline /deridt/ dert

    # ===== inline COMMON /dsctva/(supplemental) =====
    # Appears in: OPACFD:18620; OPACTD:45423; RYBMAT:46856; OPACTR:47662
    "dsct1": ("array", ("MDEPTH", ), "np.float64"),  # inline /dsctva/ dsct1(mdepth)
    "dscn1": ("array", ("MDEPTH", ), "np.float64"),  # inline /dsctva/ dscn1(mdepth)

    # ===== inline COMMON /eletab/(supplemental) =====
    # Appears in: TABINI:44480; ELDENC:49066
    "elecgr": ("array", ("MTABT", "MTABR", ), "np.float64"),  # inline /eletab/ elecgr(mtabt,mtabr)

    # ===== inline COMMON /entrop/(supplemental) =====
    # Appears in: MOLEQ:45830
    "entato": ("array", ("100", ), "np.float64"),  # inline /entrop/ entato(100)
    "ention": ("array", ("100", ), "np.float64"),  # inline /entrop/ ention(100)
    "entmol": ("array", ("600", ), "np.float64"),  # inline /entrop/ entmol(600)

    # ===== inline COMMON /eospar/(supplemental) =====
    # Appears in: INPMOD:3076; OPADD:23010; ELDENS:26729; RAYLEIGH:45194; MOLEQ:45826; ELDENC:49067
    "anmol": ("array", ("600", "MDEPTH", ), "np.float64"),  # inline /eospar/ anmol(600,mdepth)
    "anato": ("array", ("100", "MDEPTH", ), "np.float64"),  # inline /eospar/ anato(100,mdepth)
    "anion": ("array", ("100", "MDEPTH", ), "np.float64"),  # inline /eospar/ anion(100,mdepth)

    # ===== inline COMMON /EXTINT/(supplemental) =====
    # Appears in: RTECF1:38955; RTEANG:40008
    "WANGLE": ("scalar", (), "np.float64"),  # inline /EXTINT/ WANGLE
    "EXTIN": ("array", ("MFREQ", ), "np.float64"),  # inline /EXTINT/ EXTIN(MFREQ)

    # ===== inline COMMON /FACTRS/(supplemental) =====
    # Appears in: LTEGRD:40921; TEMPER:41451; TLOCAL:41613; NEWDM:41728; NEWDMT:41921
    "GAMJ": ("array", ("MDEPTH", ), "np.float64"),  # inline /FACTRS/ GAMJ(MDEPTH)
    "GAMH": ("scalar", (), "np.float64"),  # inline /FACTRS/ GAMH
    "FAK0": ("scalar", (), "np.float64"),  # inline /FACTRS/ FAK0

    # ===== inline COMMON /FLXAUX/(supplemental) =====
    # Appears in: NSTPAR:1669; LTEGRD:40924; TEMPER:41450; TLOCAL:41612; NEWDM:41729; NEWDMT:41922
    "T4": ("scalar", (), "np.float64"),  # inline /FLXAUX/ T4
    "PGAS": ("scalar", (), "np.float64"),  # inline /FLXAUX/ PGAS
    "PRAD": ("scalar", (), "np.float64"),  # inline /FLXAUX/ PRAD
    "PGM": ("scalar", (), "np.float64"),  # inline /FLXAUX/ PGM
    "PRADM": ("scalar", (), "np.float64"),  # inline /FLXAUX/ PRADM
    "ITGMAX": ("scalar", (), "np.int64"),  # inline /FLXAUX/ ITGMAX
    "ITGMX0": ("scalar", (), "np.int64"),  # inline /FLXAUX/ ITGMX0

    # ===== inline COMMON /freqcl/(supplemental) =====
    # Appears in: INITIA:159; NSTPAR:1670
    "frmin": ("scalar", (), "np.float64"),  # inline /freqcl/ frmin
    "frmax": ("scalar", (), "np.float64"),  # inline /freqcl/ frmax
    "nfrecl": ("scalar", (), "np.int64"),  # inline /freqcl/ nfrecl

    # ===== inline COMMON /grdpra/(supplemental) =====
    # Appears in: OUTPRI:14166; PZEVLD:28380; RYBCHN:47455; OPACTR:47664; RYBHEQ:47829; PGSET:47977
    "GRD": ("array", ("MDEPTH", ), "np.float64"),  # inline /grdpra/ GRD(MDEPTH)
    "pra": ("array", ("MDEPTH", ), "np.float64"),  # inline /grdpra/ pra(mdepth)
    "pgs0": ("array", ("MDEPTH", ), "np.float64"),  # inline /grdpra/ pgs0(mdepth)
    "ANTP": ("array", ("MDEPTH", ), "np.float64"),  # inline /grdpra/ ANTP(MDEPTH)

    # ===== inline COMMON /hediff/(supplemental) =====
    # Appears in: START:122; NSTPAR:1672; HEDIF:44346
    "hcmass": ("scalar", (), "np.float64"),  # inline /hediff/ hcmass
    "radstr": ("scalar", (), "np.float64"),  # inline /hediff/ radstr

    # ===== inline COMMON /hmolab/(supplemental) =====
    # Appears in: OPACF1:4819; OPACFD:18617; OPACF0:33407; OPACT1:45368; OPACTD:45424; MOLEQ:45831; OPACTR:47663; ELDENC:49070
    "anh2": ("array", ("MDEPTH", ), "np.float64"),  # inline /hmolab/ anh2(mdepth)
    "anhm": ("array", ("MDEPTH", ), "np.float64"),  # inline /hmolab/ anhm(mdepth)

    # ===== inline COMMON /ichndm/(supplemental) =====
    # Appears in: NSTPAR:1677; CONTMP:26344
    "ichanm": ("scalar", (), "np.int64"),  # inline /ichndm/ ichanm

    # ===== inline COMMON /icnrsp/(supplemental) =====
    # Appears in: NSTPAR:1675; RESOLV:3737; PZEVAL:28319
    "iconrs": ("scalar", (), "np.int64"),  # inline /icnrsp/ iconrs

    # ===== inline COMMON /ifpzpa/(supplemental) =====
    # Appears in: NSTPAR:1682; PZEVLD:28381
    "ifpzev": ("scalar", (), "np.int64"),  # inline /ifpzpa/ ifpzev

    # ===== inline COMMON /ijflar/(supplemental) =====
    # Appears in: INIFRC:34029; INIFRT:34899
    "ijfl": ("array", ("MLEVEL", ), "np.int64"),  # inline /ijflar/ ijfl(mlevel)

    # ===== inline COMMON /imodlc/(supplemental) =====
    # Appears in: RDATA:1035; RYBSOL:46652
    "imodl0": ("array", ("MLEVEL", ), "np.int64"),  # inline /imodlc/ imodl0(mlevel)

    # ===== inline COMMON /imucnn/(supplemental) =====
    # Appears in: NSTPAR:1676; CONREF:27982
    "imucon": ("scalar", (), "np.int64"),  # inline /imucnn/ imucon

    # ===== inline COMMON /intcff/(supplemental) =====
    # Appears in: TABINI:44475; TABINT:44841
    "INTCFF_YINT": ("array", ("MFREQ", ), "np.float64"),  # inline /intcff/ yint(mfreq)
    "jint": ("array", ("MFREQ", ), "np.int64"),  # inline /intcff/ jint(mfreq)

    # ===== inline COMMON /intcfg/(supplemental) =====
    # Appears in: GOMINI:48284; GHYDOP:48386
    "INTCFG_YINT": ("array", ("MFREQ", ), "np.float64"),  # inline /intcfg/ yint(mfreq)
    "jgint": ("array", ("MFREQ", ), "np.int64"),  # inline /intcfg/ jgint(mfreq)

    # ===== inline COMMON /INUNIT/(supplemental) =====
    # Appears in: INITIA:158; RDATA:1034
    "IUNIT": ("scalar", (), "np.int64"),  # inline /INUNIT/ IUNIT

    # ===== inline COMMON /ioniz2/(supplemental) =====
    # Appears in: MOLEQ:45829
    "anion2": ("array", ("30", "MDEPTH", ), "np.float64"),  # inline /ioniz2/ anion2(30,mdepth)

    # ===== inline COMMON /ipricr/(supplemental) =====
    # Appears in: NSTPAR:1678; OPACF1:4820
    "iprcrs": ("scalar", (), "np.int64"),  # inline /ipricr/ iprcrs
    "nprcrs": ("scalar", (), "np.int64"),  # inline /ipricr/ nprcrs

    # ===== inline COMMON /irwint/(supplemental) =====
    # Appears in: NSTPAR:1673; PARTF:23407
    "iirwin": ("scalar", (), "np.int64"),  # inline /irwint/ iirwin

    # ===== inline COMMON /LINED/(supplemental) =====
    # Appears in: IROSET:36279; INKUL:36765
    "WAVE": ("array", ("MLINE", ), "np.float64"),  # inline /LINED/ WAVE(MLINE)
    "VDOP": ("array", ("MLINE", "MDODF", ), "np.float32"),  # inline /LINED/ VDOP(MLINE,MDODF)
    "AGAM": ("array", ("MLINE", "MDODF", ), "np.float32"),  # inline /LINED/ AGAM(MLINE,MDODF)
    "SIG0": ("array", ("MLINE", "MDODF", ), "np.float32"),  # inline /LINED/ SIG0(MLINE,MDODF)
    "JTR": ("array", ("MLINE", "2", ), "np.int64"),  # inline /LINED/ JTR(MLINE,2)

    # ===== inline COMMON /moldat/(supplemental) =====
    # Appears in: NSTPAR:1683; MOLEQ:45834; MPARTF:46355
    "moltab": ("scalar", (), "np.int64"),  # inline /moldat/ moltab
    "irwtab": ("scalar", (), "np.int64"),  # inline /moldat/ irwtab

    # ===== inline COMMON /OPTDPT/(supplemental) =====
    # Appears in: RTEDF1:31608; RTEFR1:32311; RTEINT:33057; RTECF0:38558; RTECOM:38766; RTECF1:38953; TAUFR1:39699; RTECMU:39799; RADTOT:42932
    "DT": ("array", ("MDEPTH", ), "np.float64"),  # inline /OPTDPT/ DT(MDEPTH)

    # ===== inline COMMON /pfoptb/(supplemental) =====
    # Appears in: OPFRAC:25234
    "pfop": ("array", ("100", "60", "258", ), "np.float64"),  # inline /pfoptb/ pfop(mtemp,melec,mstag)
    "pfophm": ("array", ("100", "60", ), "np.float64"),  # inline /pfoptb/ pfophm(mtemp,melec)
    "frac": ("array", ("100", "60", "258", ), "np.float64"),  # inline /pfoptb/ frac(mtemp,melec,mstag)
    "frop": ("array", ("100", "60", "258", ), "np.float64"),  # inline /pfoptb/ frop(mtemp,melec,mstag)
    "PFOPTB_ITEMP": ("array", ("100", ), "np.int64"),  # inline /pfoptb/ itemp(mtemp)

    # ===== inline COMMON /PFSTDS/(supplemental) =====
    # Appears in: STATE:2255; PARTF:23406
    "PFSTD": ("array", ("MATOM", "30", ), "np.float64"),  # inline /PFSTDS/ PFSTD(matom,30)
    "MODPF": ("array", ("MATOM", ), "np.int64"),  # inline /PFSTDS/ MODPF(matom)

    # ===== inline COMMON /POPSTR/(supplemental) =====
    # Appears in: STEQEQ:5254
    "POPP": ("array", ("MLEVEL", ), "np.float64"),  # inline /POPSTR/ POPP(MLEVEL)
    "POPP1": ("array", ("MLEVEL", ), "np.float64"),  # inline /POPSTR/ POPP1(MLEVEL)
    "POPP2": ("array", ("MLEVEL", ), "np.float64"),  # inline /POPSTR/ POPP2(MLEVEL)
    "POPP3": ("array", ("MLEVEL", ), "np.float64"),  # inline /POPSTR/ POPP3(MLEVEL)

    # ===== inline COMMON /POPULS/(supplemental) =====
    # Appears in: ACCELP:29819
    "POPUL1": ("array", ("MLEVEL", "MDEPTH", ), "np.float64"),  # inline /POPULS/ POPUL1(MLEVEL,MDEPTH)
    "POPUL2": ("array", ("MLEVEL", "MDEPTH", ), "np.float64"),  # inline /POPULS/ POPUL2(MLEVEL,MDEPTH)
    "POPUL3": ("array", ("MLEVEL", "MDEPTH", ), "np.float64"),  # inline /POPULS/ POPUL3(MLEVEL,MDEPTH)

    # ===== inline COMMON /PPAPAR/(supplemental) =====
    # Appears in: STEQEQ:5256
    "IPOPST": ("array", ("MATOM", ), "np.int64"),  # inline /PPAPAR/ IPOPST(MATOM)
    "NTERST": ("scalar", (), "np.int64"),  # inline /PPAPAR/ NTERST
    "ITERST": ("scalar", (), "np.int64"),  # inline /PPAPAR/ ITERST
    "IACPPP": ("scalar", (), "np.int64"),  # inline /PPAPAR/ IACPPP
    "IACPP0": ("scalar", (), "np.int64"),  # inline /PPAPAR/ IACPP0
    "IACPPD": ("scalar", (), "np.int64"),  # inline /PPAPAR/ IACPPD
    "LACPPP": ("scalar", (), "bool"),  # inline /PPAPAR/ LACPPP

    # ===== inline COMMON /PRSAUX/(supplemental) =====
    # Appears in: CONTMD:26573; PZEVLD:28376; LTEGRD:40920; TEMPER:41449; NEWDM:41727; NEWDMT:41920; HESOLV:42106; HESOL6:42323
    "VSND2": ("array", ("MDEPTH", ), "np.float64"),  # inline /PRSAUX/ VSND2(MDEPTH)
    "HG1": ("scalar", (), "np.float64"),  # inline /PRSAUX/ HG1
    "HR1": ("scalar", (), "np.float64"),  # inline /PRSAUX/ HR1
    "RR1": ("scalar", (), "np.float64"),  # inline /PRSAUX/ RR1

    # ===== inline COMMON /quasun/(supplemental) =====
    # Appears in: NSTPAR:1671; PROFIL:8226; LINPRO:8946; QUASIM:43786; GETLAL:43849; ALLARD:43988
    "tqmprf": ("scalar", (), "np.float64"),  # inline /quasun/ tqmprf
    "iquasi": ("scalar", (), "np.int64"),  # inline /quasun/ iquasi
    "nunalp": ("scalar", (), "np.int64"),  # inline /quasun/ nunalp
    "nunbet": ("scalar", (), "np.int64"),  # inline /quasun/ nunbet
    "nungam": ("scalar", (), "np.int64"),  # inline /quasun/ nungam
    "nunbal": ("scalar", (), "np.int64"),  # inline /quasun/ nunbal

    # ===== inline COMMON /RAYSCT/(supplemental) =====
    # Appears in: RAYLEIGH:45193
    "RCS": ("array", ("MFREQ", ), "np.float64"),  # inline /RAYSCT/ RCS(MFREQ)
    "RCHE": ("array", ("MFREQ", ), "np.float64"),  # inline /RAYSCT/ RCHE(MFREQ)
    "RCH2": ("array", ("MFREQ", ), "np.float64"),  # inline /RAYSCT/ RCH2(MFREQ)

    # ===== inline COMMON /relcor/(supplemental) =====
    # Appears in: INPDIS:40344; COLUMN:40532
    "arh": ("scalar", (), "np.float64"),  # inline /relcor/ arh
    "brh": ("scalar", (), "np.float64"),  # inline /relcor/ brh
    "crh": ("scalar", (), "np.float64"),  # inline /relcor/ crh
    "drh": ("scalar", (), "np.float64"),  # inline /relcor/ drh

    # ===== inline COMMON /rhoder/(supplemental) =====
    # Appears in: OPACFD:18621; OPACTD:45421; SETDRT:45637
    "drhodt": ("array", ("MDEPTH", ), "np.float64"),  # inline /rhoder/ drhodt(mdepth)

    # ===== inline COMMON /RYBMTX/(supplemental) =====
    # Appears in: RYBSOL:46648; RYBMAT:46852; RYBENE:47250
    "RA": ("array", ("MDEPTH", ), "np.float64"),  # inline /RYBMTX/ RA(MDEPTH)
    "RB": ("array", ("MDEPTH", ), "np.float64"),  # inline /RYBMTX/ RB(MDEPTH)
    "RC": ("array", ("MDEPTH", ), "np.float64"),  # inline /RYBMTX/ RC(MDEPTH)
    "VR": ("array", ("MDEPTH", ), "np.float64"),  # inline /RYBMTX/ VR(MDEPTH)
    "UA": ("array", ("MDEPTH", ), "np.float64"),  # inline /RYBMTX/ UA(MDEPTH)
    "UB": ("array", ("MDEPTH", ), "np.float64"),  # inline /RYBMTX/ UB(MDEPTH)
    "UC": ("array", ("MDEPTH", ), "np.float64"),  # inline /RYBMTX/ UC(MDEPTH)
    "VA": ("array", ("MDEPTH", ), "np.float64"),  # inline /RYBMTX/ VA(MDEPTH)
    "VB": ("array", ("MDEPTH", ), "np.float64"),  # inline /RYBMTX/ VB(MDEPTH)
    "VC": ("array", ("MDEPTH", ), "np.float64"),  # inline /RYBMTX/ VC(MDEPTH)
    "WR": ("array", ("MDEPTH", ), "np.float64"),  # inline /RYBMTX/ WR(MDEPTH)
    "WM": ("array", ("MDEPTH", "MDEPTH", ), "np.float64"),  # inline /RYBMTX/ WM(MDEPTH,MDEPTH)

    # ===== inline COMMON /rybpgs/(supplemental) =====
    # Appears in: RYBCHN:47456; RYBHEQ:47830; PGSET:47978
    "CS": ("array", ("MDEPTH", ), "np.float64"),  # inline /rybpgs/ CS(MDEPTH)
    "PRAD2D": ("array", ("MDEPTH", ), "np.float64"),  # inline /rybpgs/ PRAD2D(MDEPTH)
    "F1HE": ("scalar", (), "np.float64"),  # inline /rybpgs/ F1HE

    # ===== inline COMMON /STFCR/(supplemental) =====
    # Appears in: ODFSET:29971
    "OFR": ("array", ("MFODF", ), "np.float64"),  # inline /STFCR/ OFR(MFODF)
    "OW": ("array", ("MFODF", ), "np.float64"),  # inline /STFCR/ OW(MFODF)
    "OWSUB": ("array", ("MFODF", ), "np.float64"),  # inline /STFCR/ OWSUB(MFODF)
    "ODFL0": ("array", ("MDODF", "MFODF", ), "np.float64"),  # inline /STFCR/ ODFL0(MDODF,MFODF)
    "ODF2": ("array", ("MDEPTH", ), "np.float64"),  # inline /STFCR/ ODF2(MDEPTH)
    "IFTRA": ("array", ("MTRANS", ), "np.int64"),  # inline /STFCR/ IFTRA(MTRANS)
    "IDODF": ("array", ("MDODF", ), "np.int64"),  # inline /STFCR/ IDODF(MDODF)
    "NDODF": ("scalar", (), "np.int64"),  # inline /STFCR/ NDODF

    # ===== inline COMMON /STOMAT/(supplemental) =====
    # Appears in: SOLVES:14796
    "STOA": ("array", ("MSMX", "MSMX", "MDEPTH", ), "np.float64"),  # inline /STOMAT/ STOA(MSMX,MSMX,MDEPTH)
    "STOB": ("array", ("MSMX", "MSMX", "MDEPTH", ), "np.float64"),  # inline /STOMAT/ STOB(MSMX,MSMX,MDEPTH)
    "STOALF": ("array", ("MSMX", "MSMX", "MDEPTH", ), "np.float64"),  # inline /STOMAT/ STOALF(MSMX,MSMX,MDEPTH)

    # ===== inline COMMON /STRPAR/(supplemental) =====
    # Appears in: INITIA:157; RDATA:1033
    "IMER": ("scalar", (), "np.int64"),  # inline /STRPAR/ IMER
    "ITR": ("scalar", (), "np.int64"),  # inline /STRPAR/ ITR
    "IC": ("scalar", (), "np.int64"),  # inline /STRPAR/ IC
    "IL": ("scalar", (), "np.int64"),  # inline /STRPAR/ IL
    "IP": ("scalar", (), "np.int64"),  # inline /STRPAR/ IP
    "NLASTE": ("scalar", (), "np.int64"),  # inline /STRPAR/ NLASTE
    "NHOD": ("scalar", (), "np.int64"),  # inline /STRPAR/ NHOD
    "LASV": ("scalar", (), "bool"),  # inline /STRPAR/ LASV

    # ===== inline COMMON /SURFEX/(supplemental) =====
    # Appears in: BHED:16678; BHEZ:17020; RTECF1:38954; RTEANG:40009; RADTOT:42933
    "EXTJ": ("array", ("MFREQ", ), "np.float64"),  # inline /SURFEX/ EXTJ(MFREQ)
    "EXTH": ("array", ("MFREQ", ), "np.float64"),  # inline /SURFEX/ EXTH(MFREQ)

    # ===== inline COMMON /TABLTD/(supplemental) =====
    # Appears in: SETTRM:45507; PRSENT:45733
    "R1": ("scalar", (), "np.float64"),  # inline /TABLTD/ R1
    "R2": ("scalar", (), "np.float64"),  # inline /TABLTD/ R2
    "T1": ("scalar", (), "np.float64"),  # inline /TABLTD/ T1
    "T2": ("scalar", (), "np.float64"),  # inline /TABLTD/ T2
    "T12": ("scalar", (), "np.float64"),  # inline /TABLTD/ T12
    "T22": ("scalar", (), "np.float64"),  # inline /TABLTD/ T22
    "INDEX": ("scalar", (), "np.int64"),  # inline /TABLTD/ INDEX

    # ===== inline COMMON /tdedge/(supplemental) =====
    # Appears in: SETTRM:45508; TRMDRT:45677; PRSENT:45734
    "redge": ("scalar", (), "np.float64"),  # inline /tdedge/ redge
    "pedge": ("array", ("100", ), "np.float64"),  # inline /tdedge/ pedge(100)
    "sedge": ("array", ("100", ), "np.float64"),  # inline /tdedge/ sedge(100)
    "cvedge": ("array", ("100", ), "np.float64"),  # inline /tdedge/ cvedge(100)
    "cpedge": ("array", ("100", ), "np.float64"),  # inline /tdedge/ cpedge(100)
    "gammaedge": ("array", ("100", ), "np.float64"),  # inline /tdedge/ gammaedge(100)
    "tedge": ("array", ("100", ), "np.float64"),  # inline /tdedge/ tedge(100)

    # ===== inline COMMON /tdflag/(supplemental) =====
    # Appears in: SETTRM:45510; TRMDRT:45679; PRSENT:45736
    "JON": ("scalar", (), "np.int64"),  # inline /tdflag/ JON

    # ===== inline COMMON /temlim/(supplemental) =====
    # Appears in: NSTPAR:1679; KURUCZ:3220
    "tfloor": ("scalar", (), "np.float64"),  # inline /temlim/ tfloor

    # ===== inline COMMON /terden/(supplemental) =====
    # Appears in: STATE:2256; ELDENS:26728; TRMDER:27289; MOLEQ:45832
    "rhoter": ("scalar", (), "np.float64"),  # inline /terden/ rhoter
    "anta": ("scalar", (), "np.float64"),  # inline /terden/ anta
    "entrp": ("scalar", (), "np.float64"),  # inline /terden/ entrp

    # ===== inline COMMON /THERM/(supplemental) =====
    # Appears in: SETTRM:45506; PRSENT:45732
    "SL": ("array", ("330", "100", ), "np.float64"),  # inline /THERM/ SL(330,100)
    "PL": ("array", ("330", "100", ), "np.float64"),  # inline /THERM/ PL(330,100)

    # ===== inline COMMON /TOPB/(supplemental) =====
    # Appears in: TOPBAS:10708; OPDATA:10767
    "SOP": ("array", ("15", "200", ), "np.float64"),  # inline /TOPB/ SOP(MOP,MMAXOP)
    "XOP": ("array", ("15", "200", ), "np.float64"),  # inline /TOPB/ XOP(MOP,MMAXOP)
    "NOP": ("array", ("200", ), "np.int64"),  # inline /TOPB/ NOP(MMAXOP)
    "NTOTOP": ("scalar", (), "np.int64"),  # inline /TOPB/ NTOTOP
    "IDLVOP": ("array", ("200", ), "object"),  # inline /TOPB/ IDLVOP(MMAXOP)
    "LOPREA": ("scalar", (), "bool"),  # inline /TOPB/ LOPREA

    # ===== inline COMMON /TOTJHK/(supplemental) =====
    # Appears in: LTEGRD:40922; RADTOT:42934
    "TOTJ": ("array", ("MDEPTH", ), "np.float64"),  # inline /TOTJHK/ TOTJ(MDEPTH)
    "TOTH": ("array", ("MDEPTH", ), "np.float64"),  # inline /TOTJHK/ TOTH(MDEPTH)
    "TOTK": ("array", ("MDEPTH", ), "np.float64"),  # inline /TOTJHK/ TOTK(MDEPTH)
    "RDOPAC": ("array", ("MDEPTH", ), "np.float64"),  # inline /TOTJHK/ RDOPAC(MDEPTH)
    "FLOPAC": ("array", ("MDEPTH", ), "np.float64"),  # inline /TOTJHK/ FLOPAC(MDEPTH)
}

_DTYPES = {
    "np.float64": np.float64,
    "np.int64": np.int64,
    "bool": bool,
    "np.int16": np.int16,
    "np.float32": np.float32,
    "object": object,
}

_SCALAR_DEFAULTS = {
    "np.float64": 0.0,
    "np.int64": 0,
    "bool": False,
    "np.int16": 0,
    "np.float32": 0.0,
    "object": "",
}


def _dim(expr):
    """Evaluate a dimension expression (identifiers taken from params.py)."""
    return int(eval(expr, {"__builtins__": {}}, dict(vars(P))))


def _allocate(name):
    """Allocate a variable per its DECLS declaration: arrays +1 per dimension, scalars return a default."""
    kind, dims, dtype = DECLS[name]
    if kind == "scalar":
        return _SCALAR_DEFAULTS[dtype]
    shape = tuple(_dim(d) + 1 for d in dims)
    if dtype == "object":
        arr = np.empty(shape, dtype=object)
        arr[...] = ""
        return arr
    return np.zeros(shape, dtype=_DTYPES[dtype])


def __getattr__(name):
    """PEP 562: lazily allocate a COMMON variable on first access and cache it in module globals."""
    if name not in DECLS:
        raise AttributeError("COMMON variable not declared in commons: %r" % name)
    value = _allocate(name)
    globals()[name] = value
    return value


def __dir__():
    return sorted(set(globals()) | set(DECLS))
