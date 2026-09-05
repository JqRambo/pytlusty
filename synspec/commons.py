# -*- coding: utf-8 -*-
"""
commons.py — SYNSPEC 全部 COMMON 块变量的懒分配命名空间。

对应 5 个 include 文件（PARAMS.FOR / MODELP.FOR / LINDAT.FOR / SYNTHP.FOR /
WINCOM.FOR）中的全部 COMMON 块，以及 synspec54.f 子程序体内补充声明的
COMMON 块（含 3 处无名 blank COMMON）。

用法：
    import commons as C
    C.POPUL[i, j] = 1.0  # 数组：首次访问时按 Fortran 声明维度（每维 +1）分配
    C.ND = 5             # 标量：首次访问返回默认 0 / 0.0 / False / ''

规则：
- 保留 Fortran 1 基索引：数组每维多分配一个元素，索引 0 不使用
  （LINDAT.FOR 中 AMLIST(0:MMLIST)、IBIN(0:MMLIST) 为 0 基，分配后 0..MMLIST 全可用）。
- 类型遵循 PARAMS.FOR：IMPLICIT REAL*8 (A-H,O-Z), LOGICAL*1 (L)，
  即首字母 I-N → int64、A-H/O-Z → float64、L 开头 → bool；显式声明优先：
  INTEGER*4 → np.int64，REAL*4 → np.float32，CHARACTER*n → dtype=object（元素初值 ''）。
- DECLS 记录 {名字: (种类, 维度表达式元组, dtype)}；模块级 __getattr__（PEP 562）
  在首次访问时据此分配，并缓存到模块 globals()，后续访问走正常属性。
- 维度表达式中的 PARAMETER 名取自 params.py（Fortran 大小写不敏感，此处用规范拼写）；
  子程序局部 PARAMETER（如 MVOI=2001、NXMAX=1400）直接写成字面量并在注释中注明。
"""

import numpy as np

import params as P

# {名字: (种类 "array"/"scalar", (维度表达式, ...), dtype)}
# 每条注释注明来源：文件名/行号 + COMMON 块名 + 原始维度声明。
DECLS = {
    # ===== PARAMS.FOR : COMMON /BASNUM/ =====
    "NATOM": ("scalar", (), "np.int64"),  # PARAMS.FOR /BASNUM/ NATOM
    "NION": ("scalar", (), "np.int64"),  # PARAMS.FOR /BASNUM/ NION
    "NLEVEL": ("scalar", (), "np.int64"),  # PARAMS.FOR /BASNUM/ NLEVEL
    "ND": ("scalar", (), "np.int64"),  # PARAMS.FOR /BASNUM/ ND
    "NDSTEP": ("scalar", (), "np.int64"),  # PARAMS.FOR /BASNUM/ NDSTEP
    "NFREQ": ("scalar", (), "np.int64"),  # PARAMS.FOR /BASNUM/ NFREQ
    "NFROBS": ("scalar", (), "np.int64"),  # PARAMS.FOR /BASNUM/ NFROBS
    "NFREQC": ("scalar", (), "np.int64"),  # PARAMS.FOR /BASNUM/ NFREQC
    "NFREQS": ("scalar", (), "np.int64"),  # PARAMS.FOR /BASNUM/ NFREQS
    "NMU": ("scalar", (), "np.int64"),  # PARAMS.FOR /BASNUM/ NMU

    # ===== PARAMS.FOR : COMMON /LTESET/ =====
    "LTE": ("scalar", (), "bool"),  # PARAMS.FOR /LTESET/ LTE
    "LTEGR": ("scalar", (), "bool"),  # PARAMS.FOR /LTESET/ LTEGR

    # ===== PARAMS.FOR : COMMON /INPPAR/ =====
    "TEFF": ("scalar", (), "np.float64"),  # PARAMS.FOR /INPPAR/ TEFF
    "GRAV": ("scalar", (), "np.float64"),  # PARAMS.FOR /INPPAR/ GRAV
    "YTOT": ("array", ("MDEPTH", ), "np.float64"),  # PARAMS.FOR /INPPAR/ YTOT(MDEPTH)
    "WMM": ("array", ("MDEPTH", ), "np.float64"),  # PARAMS.FOR /INPPAR/ WMM(MDEPTH)
    "WMY": ("array", ("MDEPTH", ), "np.float64"),  # PARAMS.FOR /INPPAR/ WMY(MDEPTH)
    "vaclim": ("scalar", (), "np.float64"),  # PARAMS.FOR /INPPAR/ vaclim
    "ATTOT": ("array", ("MATOM", "MDEPTH", ), "np.float64"),  # PARAMS.FOR /INPPAR/ ATTOT(MATOM,MDEPTH)

    # ===== PARAMS.FOR : COMMON /BASICM/ =====
    "IMODE": ("scalar", (), "np.int64"),  # PARAMS.FOR /BASICM/ IMODE
    "IMODE0": ("scalar", (), "np.int64"),  # PARAMS.FOR /BASICM/ IMODE0
    "IFREQ": ("scalar", (), "np.int64"),  # PARAMS.FOR /BASICM/ IFREQ
    "INLTE": ("scalar", (), "np.int64"),  # PARAMS.FOR /BASICM/ INLTE
    "IDSTD": ("scalar", (), "np.int64"),  # PARAMS.FOR /BASICM/ IDSTD
    "IFWIN": ("scalar", (), "np.int64"),  # PARAMS.FOR /BASICM/ IFWIN
    "IFEOS": ("scalar", (), "np.int64"),  # PARAMS.FOR /BASICM/ IFEOS
    "IBFAC": ("scalar", (), "np.int64"),  # PARAMS.FOR /BASICM/ IBFAC

    # ===== PARAMS.FOR : COMMON /INTKEY/ =====
    "INMOD": ("scalar", (), "np.int64"),  # PARAMS.FOR /INTKEY/ INMOD
    "INTRPL": ("scalar", (), "np.int64"),  # PARAMS.FOR /INTKEY/ INTRPL
    "ICHANG": ("scalar", (), "np.int64"),  # PARAMS.FOR /INTKEY/ ICHANG
    "ICHEMC": ("scalar", (), "np.int64"),  # PARAMS.FOR /INTKEY/ ICHEMC
    "IATREF": ("scalar", (), "np.int64"),  # PARAMS.FOR /INTKEY/ IATREF
    "ICONTL": ("scalar", (), "np.int64"),  # PARAMS.FOR /INTKEY/ ICONTL

    # ===== PARAMS.FOR : COMMON /LBLANK/ =====
    "IBLANK": ("scalar", (), "np.int64"),  # PARAMS.FOR /LBLANK/ IBLANK
    "NBLANK": ("scalar", (), "np.int64"),  # PARAMS.FOR /LBLANK/ NBLANK

    # ===== PARAMS.FOR : COMMON /NXTINI/ =====
    "ALM00": ("scalar", (), "np.float64"),  # PARAMS.FOR /NXTINI/ ALM00
    "ALST00": ("scalar", (), "np.float64"),  # PARAMS.FOR /NXTINI/ ALST00
    "NXTSET": ("scalar", (), "np.int64"),  # PARAMS.FOR /NXTINI/ NXTSET
    "INLIST": ("scalar", (), "np.int64"),  # PARAMS.FOR /NXTINI/ INLIST
    "ALAMBE": ("scalar", (), "np.float64"),  # PARAMS.FOR /NXTINI/ ALAMBE
    "DLAMLO": ("scalar", (), "np.float64"),  # PARAMS.FOR /NXTINI/ DLAMLO

    # ===== PARAMS.FOR : COMMON /IPRNTR/ =====
    "IPRIN": ("scalar", (), "np.int64"),  # PARAMS.FOR /IPRNTR/ IPRIN

    # ===== PARAMS.FOR : COMMON /ATOPAR/ =====
    "AMASS": ("array", ("MATEX", ), "np.float64"),  # PARAMS.FOR /ATOPAR/ AMASS(MATEX)
    "ABUND": ("array", ("MATEX", "MDEPTH", ), "np.float64"),  # PARAMS.FOR /ATOPAR/ ABUND(MATEX,MDEPTH)
    "RELAB": ("array", ("MATEX", "MDEPTH", ), "np.float64"),  # PARAMS.FOR /ATOPAR/ RELAB(MATEX,MDEPTH)
    "NUMAT": ("array", ("MATEX", ), "np.int64"),  # PARAMS.FOR /ATOPAR/ NUMAT(MATEX)
    "N0A": ("array", ("MATEX", ), "np.int64"),  # PARAMS.FOR /ATOPAR/ N0A(MATEX)
    "NKA": ("array", ("MATEX", ), "np.int64"),  # PARAMS.FOR /ATOPAR/ NKA(MATEX)
    "SABND": ("array", ("MATEX", ), "np.float64"),  # PARAMS.FOR /ATOPAR/ SABND(MATEX)

    # ===== PARAMS.FOR : COMMON /IONPAR/ =====
    "FF": ("array", ("MIOEX", ), "np.float64"),  # PARAMS.FOR /IONPAR/ FF(MIOEX)
    "NFIRST": ("array", ("MIOEX", ), "np.int64"),  # PARAMS.FOR /IONPAR/ NFIRST(MIOEX)
    "NLAST": ("array", ("MIOEX", ), "np.int64"),  # PARAMS.FOR /IONPAR/ NLAST(MIOEX)
    "NNEXT": ("array", ("MIOEX", ), "np.int64"),  # PARAMS.FOR /IONPAR/ NNEXT(MIOEX)
    "IUPSUM": ("array", ("MIOEX", ), "np.int64"),  # PARAMS.FOR /IONPAR/ IUPSUM(MIOEX)
    "IZ": ("array", ("MIOEX", ), "np.int64"),  # PARAMS.FOR /IONPAR/ IZ(MIOEX)
    "IFREE": ("array", ("MIOEX", ), "np.int64"),  # PARAMS.FOR /IONPAR/ IFREE(MIOEX)
    "INBFCS": ("array", ("MIOEX", ), "np.int64"),  # PARAMS.FOR /IONPAR/ INBFCS(MIOEX)
    "ILIMITS": ("array", ("MIOEX", ), "np.int64"),  # PARAMS.FOR /IONPAR/ ILIMITS(MIOEX)

    # ===== PARAMS.FOR : COMMON /LEVPAR/ =====
    "ENION": ("array", ("MLEVEL", ), "np.float64"),  # PARAMS.FOR /LEVPAR/ ENION(MLEVEL)
    "G": ("array", ("MLEVEL", ), "np.float64"),  # PARAMS.FOR /LEVPAR/ G(MLEVEL)
    "NQUANT": ("array", ("MLEVEL", ), "np.int64"),  # PARAMS.FOR /LEVPAR/ NQUANT(MLEVEL)
    "IATM": ("array", ("MLEVEL", ), "np.int64"),  # PARAMS.FOR /LEVPAR/ IATM(MLEVEL)
    "IEL": ("array", ("MLEVEL", ), "np.int64"),  # PARAMS.FOR /LEVPAR/ IEL(MLEVEL)
    "ILK": ("array", ("MLEVEL", ), "np.int64"),  # PARAMS.FOR /LEVPAR/ ILK(MLEVEL)
    "ifwop": ("array", ("MLEVEL", ), "np.int64"),  # PARAMS.FOR /LEVPAR/ ifwop(mlevel)
    "isemex": ("array", ("MATOM", ), "np.int64"),  # PARAMS.FOR /LEVPAR/ isemex(matom)

    # ===== PARAMS.FOR : COMMON /LEVLIMITS/ =====
    "ENION1": ("array", ("MLEVEL", ), "np.float64"),  # PARAMS.FOR /LEVLIMITS/ ENION1(MLEVEL)
    "ENION2": ("array", ("MLEVEL", ), "np.float64"),  # PARAMS.FOR /LEVLIMITS/ ENION2(MLEVEL)
    "SQUANT1": ("array", ("MLEVEL", ), "np.int64"),  # PARAMS.FOR /LEVLIMITS/ INTEGER*4 SQUANT1(MLEVEL)
    "SQUANT2": ("array", ("MLEVEL", ), "np.int64"),  # PARAMS.FOR /LEVLIMITS/ INTEGER*4 SQUANT2(MLEVEL)
    "LQUANT1": ("array", ("MLEVEL", ), "np.int64"),  # PARAMS.FOR /LEVLIMITS/ INTEGER*4 LQUANT1(MLEVEL)
    "LQUANT2": ("array", ("MLEVEL", ), "np.int64"),  # PARAMS.FOR /LEVLIMITS/ INTEGER*4 LQUANT2(MLEVEL)
    "PQUANT1": ("array", ("MLEVEL", ), "np.int64"),  # PARAMS.FOR /LEVLIMITS/ INTEGER*4 PQUANT1(MLEVEL)
    "PQUANT2": ("array", ("MLEVEL", ), "np.int64"),  # PARAMS.FOR /LEVLIMITS/ INTEGER*4 PQUANT2(MLEVEL)

    # ===== PARAMS.FOR : COMMON /TRAPAR/ =====
    "IBF": ("array", ("MLEVEL", ), "np.int64"),  # PARAMS.FOR /TRAPAR/ IBF(MLEVEL)
    "S0BF": ("array", ("MLEVEL", ), "np.float64"),  # PARAMS.FOR /TRAPAR/ S0BF(MLEVEL)
    "ALFBF": ("array", ("MLEVEL", ), "np.float64"),  # PARAMS.FOR /TRAPAR/ ALFBF(MLEVEL)
    "BETBF": ("array", ("MLEVEL", ), "np.float64"),  # PARAMS.FOR /TRAPAR/ BETBF(MLEVEL)
    "GAMBF": ("array", ("MLEVEL", ), "np.float64"),  # PARAMS.FOR /TRAPAR/ GAMBF(MLEVEL)

    # ===== PARAMS.FOR : COMMON /MRGPAR/ =====
    "SGM0": ("array", ("MMER", ), "np.float64"),  # PARAMS.FOR /MRGPAR/ SGM0(MMER)
    "FRCH": ("array", ("MMER", ), "np.float64"),  # PARAMS.FOR /MRGPAR/ FRCH(MMER)
    "SGEXT1": ("array", ("MMER", "MDEPTH", ), "np.float64"),  # PARAMS.FOR /MRGPAR/ SGEXT1(MMER,MDEPTH)
    "GMER": ("array", ("MMER", "MDEPTH", ), "np.float64"),  # PARAMS.FOR /MRGPAR/ GMER(MMER,MDEPTH)
    "SGMSUM": ("array", ("NLMX", "MMER", "MDEPTH", ), "np.float64"),  # PARAMS.FOR /MRGPAR/ SGMSUM(NLMX,MMER,MDEPTH)
    "SGMG": ("array", ("MMER", "MDEPTH", ), "np.float64"),  # PARAMS.FOR /MRGPAR/ SGMG(MMER,MDEPTH)
    "IMRG": ("array", ("MLEVEL", ), "np.int64"),  # PARAMS.FOR /MRGPAR/ IMRG(MLEVEL)
    "IIMER": ("array", ("MMER", ), "np.int64"),  # PARAMS.FOR /MRGPAR/ IIMER(MMER)

    # ===== PARAMS.FOR : COMMON /DWNPAR/ =====
    "ELEC23": ("array", ("MDEPTH", ), "np.float64"),  # PARAMS.FOR /DWNPAR/ ELEC23(MDEPTH)
    "Z3": ("array", ("MZZ", ), "np.float64"),  # PARAMS.FOR /DWNPAR/ Z3(MZZ)
    "DWC1": ("array", ("MZZ", "MDEPTH", ), "np.float64"),  # PARAMS.FOR /DWNPAR/ DWC1(MZZ,MDEPTH)
    "DWC2": ("array", ("MDEPTH", ), "np.float64"),  # PARAMS.FOR /DWNPAR/ DWC2(MDEPTH)

    # ===== PARAMS.FOR : COMMON /OPCPAR/ =====
    "IOPADD": ("scalar", (), "np.int64"),  # PARAMS.FOR /OPCPAR/ IOPADD
    "IOPHMI": ("scalar", (), "np.int64"),  # PARAMS.FOR /OPCPAR/ IOPHMI
    "IOPH2P": ("scalar", (), "np.int64"),  # PARAMS.FOR /OPCPAR/ IOPH2P
    "IOPHEM": ("scalar", (), "np.int64"),  # PARAMS.FOR /OPCPAR/ IOPHEM
    "IOPCH": ("scalar", (), "np.int64"),  # PARAMS.FOR /OPCPAR/ IOPCH
    "IOPOH": ("scalar", (), "np.int64"),  # PARAMS.FOR /OPCPAR/ IOPOH
    "IOPH2M": ("scalar", (), "np.int64"),  # PARAMS.FOR /OPCPAR/ IOPH2M
    "IOH2H2": ("scalar", (), "np.int64"),  # PARAMS.FOR /OPCPAR/ IOH2H2
    "IOH2HE": ("scalar", (), "np.int64"),  # PARAMS.FOR /OPCPAR/ IOH2HE
    "IOH2H1": ("scalar", (), "np.int64"),  # PARAMS.FOR /OPCPAR/ IOH2H1
    "IOHHE": ("scalar", (), "np.int64"),  # PARAMS.FOR /OPCPAR/ IOHHE
    "IOPHLI": ("scalar", (), "np.int64"),  # PARAMS.FOR /OPCPAR/ IOPHLI
    "IRSCT": ("scalar", (), "np.int64"),  # PARAMS.FOR /OPCPAR/ IRSCT
    "IRSCHE": ("scalar", (), "np.int64"),  # PARAMS.FOR /OPCPAR/ IRSCHE
    "IRSCH2": ("scalar", (), "np.int64"),  # PARAMS.FOR /OPCPAR/ IRSCH2

    # ===== PARAMS.FOR : COMMON /AUXIND/ =====
    "IATH": ("scalar", (), "np.int64"),  # PARAMS.FOR /AUXIND/ IATH
    "IELH": ("scalar", (), "np.int64"),  # PARAMS.FOR /AUXIND/ IELH
    "IELHM": ("scalar", (), "np.int64"),  # PARAMS.FOR /AUXIND/ IELHM
    "N0H": ("scalar", (), "np.int64"),  # PARAMS.FOR /AUXIND/ N0H
    "N1H": ("scalar", (), "np.int64"),  # PARAMS.FOR /AUXIND/ N1H
    "NKH": ("scalar", (), "np.int64"),  # PARAMS.FOR /AUXIND/ NKH
    "N0HN": ("scalar", (), "np.int64"),  # PARAMS.FOR /AUXIND/ N0HN
    "N0M": ("scalar", (), "np.int64"),  # PARAMS.FOR /AUXIND/ N0M
    "IATHE": ("scalar", (), "np.int64"),  # PARAMS.FOR /AUXIND/ IATHE
    "IELHE1": ("scalar", (), "np.int64"),  # PARAMS.FOR /AUXIND/ IELHE1
    "IELHE2": ("scalar", (), "np.int64"),  # PARAMS.FOR /AUXIND/ IELHE2

    # ===== PARAMS.FOR : COMMON /MOLFLG/ =====
    "TMOLIM": ("scalar", (), "np.float64"),  # PARAMS.FOR /MOLFLG/ TMOLIM
    "MOLIND": ("array", ("11000", ), "np.int64"),  # PARAMS.FOR /MOLFLG/ MOLIND(11000)
    "NMOLEC": ("scalar", (), "np.int64"),  # PARAMS.FOR /MOLFLG/ NMOLEC
    "IFMOL": ("scalar", (), "np.int64"),  # PARAMS.FOR /MOLFLG/ IFMOL
    "MOLTAB": ("scalar", (), "np.int64"),  # PARAMS.FOR /MOLFLG/ MOLTAB
    "IRWTAB": ("scalar", (), "np.int64"),  # PARAMS.FOR /MOLFLG/ IRWTAB
    "IIRWIN": ("scalar", (), "np.int64"),  # PARAMS.FOR /MOLFLG/ IIRWIN
    "IPFEXO": ("scalar", (), "np.int64"),  # PARAMS.FOR /MOLFLG/ IPFEXO

    # ===== PARAMS.FOR : COMMON /QFLAGS/ =====
    "ERANGE": ("scalar", (), "np.float64"),  # PARAMS.FOR /QFLAGS/ ERANGE
    "ISPICK": ("scalar", (), "np.int64"),  # PARAMS.FOR /QFLAGS/ ISPICK
    "ILPICK": ("scalar", (), "np.int64"),  # PARAMS.FOR /QFLAGS/ ILPICK
    "IPPICK": ("scalar", (), "np.int64"),  # PARAMS.FOR /QFLAGS/ IPPICK

    # ===== PARAMS.FOR : COMMON /PFSTDS/ =====
    "PFSTD": ("array", ("MION", "MATOM", ), "np.float64"),  # PARAMS.FOR /PFSTDS/ PFSTD(MION,MATOM)
    "MODPF": ("array", ("MATOM", ), "np.int64"),  # PARAMS.FOR /PFSTDS/ MODPF(MATOM)

    # ===== PARAMS.FOR : COMMON /ADDPOP/ =====
    "RR": ("array", ("MATOM", "MION", ), "np.float64"),  # PARAMS.FOR /ADDPOP/ RR(MATOM,MION)

    # ===== PARAMS.FOR : COMMON /ATOBLN/ =====
    "ENEV": ("array", ("MATOM", "MI1", ), "np.float64"),  # PARAMS.FOR /ATOBLN/ ENEV(MATOM,MI1)
    "AMAS": ("array", ("MATOM", ), "np.float64"),  # PARAMS.FOR /ATOBLN/ AMAS(MATOM)
    "ABND": ("array", ("MATOM", ), "np.float64"),  # PARAMS.FOR /ATOBLN/ ABND(MATOM)
    "ABNDD": ("array", ("MATOM", "MDEPTH", ), "np.float64"),  # PARAMS.FOR /ATOBLN/ ABNDD(MATOM,MDEPTH)
    "ABNREF": ("array", ("MDEPTH", ), "np.float64"),  # PARAMS.FOR /ATOBLN/ ABNREF(MDEPTH)
    "TYPAT": ("array", ("MATOM", ), "object"),  # PARAMS.FOR /ATOBLN/ character*4 TYPAT(MATOM)
    "IATEX": ("array", ("MATOM", ), "np.int64"),  # PARAMS.FOR /ATOBLN/ IATEX(MATOM)
    "INPOT": ("array", ("MATOM", "MION0", ), "np.int64"),  # PARAMS.FOR /ATOBLN/ INPOT(MATOM,MION0)

    # ===== PARAMS.FOR : COMMON /ATOINI/ =====
    "NATOMS": ("scalar", (), "np.int64"),  # PARAMS.FOR /ATOINI/ NATOMS
    "IONIZ": ("array", ("MATOM", ), "np.int64"),  # PARAMS.FOR /ATOINI/ IONIZ(MATOM)
    "LGR": ("array", ("MATOM", ), "bool"),  # PARAMS.FOR /ATOINI/ LOGICAL LGR(MATOM)
    "LRM": ("array", ("MATOM", ), "bool"),  # PARAMS.FOR /ATOINI/ LOGICAL LRM(MATOM)

    # ===== PARAMS.FOR : COMMON /HYDPRF/ =====
    "PRFHYD": ("array", ("MLINH", "MDEPTH", "MHWL", ), "np.float64"),  # PARAMS.FOR /HYDPRF/ PRFHYD(MLINH,MDEPTH,MHWL)
    "WLHYD": ("array", ("MLINH", "MHWL", ), "np.float64"),  # PARAMS.FOR /HYDPRF/ WLHYD(MLINH,MHWL)
    "NWLHYD": ("array", ("MLINH", ), "np.int64"),  # PARAMS.FOR /HYDPRF/ NWLHYD(MLINH)
    "WL": ("array", ("MHWL", "MLINH", ), "np.float64"),  # PARAMS.FOR /HYDPRF/ WL(MHWL,MLINH)
    "XT": ("array", ("MHT", "MLINH", ), "np.float64"),  # PARAMS.FOR /HYDPRF/ XT(MHT,MLINH)
    "XNE": ("array", ("MHE", "MLINH", ), "np.float64"),  # PARAMS.FOR /HYDPRF/ XNE(MHE,MLINH)
    "PRF": ("array", ("MHWL", "MHT", "MHE", "MLINH", ), "np.float64"),  # PARAMS.FOR /HYDPRF/ PRF(MHWL,MHT,MHE,MLINH)
    "WLINE": ("array", ("4", "22", ), "np.float64"),  # PARAMS.FOR /HYDPRF/ WLINE(4,22)
    "NWLH": ("array", ("MLINH", ), "np.int64"),  # PARAMS.FOR /HYDPRF/ NWLH(MLINH)
    "NTH": ("array", ("MLINH", ), "np.int64"),  # PARAMS.FOR /HYDPRF/ NTH(MLINH)
    "NEH": ("array", ("MLINH", ), "np.int64"),  # PARAMS.FOR /HYDPRF/ NEH(MLINH)
    "ILIN0": ("array", ("4", "22", ), "np.int64"),  # PARAMS.FOR /HYDPRF/ ILIN0(4,22)
    "ILEMKE": ("scalar", (), "np.int64"),  # PARAMS.FOR /HYDPRF/ ILEMKE
    "NLIHYD": ("scalar", (), "np.int64"),  # PARAMS.FOR /HYDPRF/ NLIHYD

    # ===== PARAMS.FOR : COMMON /AUXHYD/ =====
    "XK": ("scalar", (), "np.float64"),  # PARAMS.FOR /AUXHYD/ XK
    "FXK": ("scalar", (), "np.float64"),  # PARAMS.FOR /AUXHYD/ FXK
    "BETAD": ("scalar", (), "np.float64"),  # PARAMS.FOR /AUXHYD/ BETAD
    "DBETA": ("scalar", (), "np.float64"),  # PARAMS.FOR /AUXHYD/ DBETA
    "BERGFC": ("scalar", (), "np.float64"),  # PARAMS.FOR /AUXHYD/ BERGFC
    "CUTLYM": ("scalar", (), "np.float64"),  # PARAMS.FOR /AUXHYD/ CUTLYM
    "CUTBAL": ("scalar", (), "np.float64"),  # PARAMS.FOR /AUXHYD/ CUTBAL

    # ===== PARAMS.FOR : COMMON /HHEPRF/ =====
    "IHYDPR": ("scalar", (), "np.int64"),  # PARAMS.FOR /HHEPRF/ IHYDPR
    "IHE1PR": ("scalar", (), "np.int64"),  # PARAMS.FOR /HHEPRF/ IHE1PR
    "IHE2PR": ("scalar", (), "np.int64"),  # PARAMS.FOR /HHEPRF/ IHE2PR

    # ===== PARAMS.FOR : COMMON /HYLPAR/ =====
    "IHYL": ("scalar", (), "np.int64"),  # PARAMS.FOR /HYLPAR/ IHYL
    "ILOWH": ("scalar", (), "np.int64"),  # PARAMS.FOR /HYLPAR/ ILOWH
    "M10": ("scalar", (), "np.int64"),  # PARAMS.FOR /HYLPAR/ M10
    "M20": ("scalar", (), "np.int64"),  # PARAMS.FOR /HYLPAR/ M20

    # ===== PARAMS.FOR : COMMON /HYLPAW/ =====
    "IHYLW": ("array", ("MFREQ", ), "np.int64"),  # PARAMS.FOR /HYLPAW/ IHYLW(MFREQ)
    "ILOWHW": ("array", ("MFREQ", ), "np.int64"),  # PARAMS.FOR /HYLPAW/ ILOWHW(MFREQ)
    "M10W": ("array", ("MFREQ", ), "np.int64"),  # PARAMS.FOR /HYLPAW/ M10W(MFREQ)
    "M20W": ("array", ("MFREQ", ), "np.int64"),  # PARAMS.FOR /HYLPAW/ M20W(MFREQ)

    # ===== PARAMS.FOR : COMMON /HE2PAR/ =====
    "IFHE2": ("scalar", (), "np.int64"),  # PARAMS.FOR /HE2PAR/ IFHE2
    "IHE2L": ("scalar", (), "np.int64"),  # PARAMS.FOR /HE2PAR/ IHE2L
    "ILWHE2": ("scalar", (), "np.int64"),  # PARAMS.FOR /HE2PAR/ ILWHE2
    "MHE10": ("scalar", (), "np.int64"),  # PARAMS.FOR /HE2PAR/ MHE10
    "MHE20": ("scalar", (), "np.int64"),  # PARAMS.FOR /HE2PAR/ MHE20

    # ===== PARAMS.FOR : COMMON /HE2PAW/ =====
    "IHE2LW": ("array", ("MFREQ", ), "np.int64"),  # PARAMS.FOR /HE2PAW/ IHE2LW(MFREQ)
    "ILWHEW": ("array", ("MFREQ", ), "np.int64"),  # PARAMS.FOR /HE2PAW/ ILWHEW(MFREQ)
    "MHE10W": ("array", ("MFREQ", ), "np.int64"),  # PARAMS.FOR /HE2PAW/ MHE10W(MFREQ)
    "MHE20W": ("array", ("MFREQ", ), "np.int64"),  # PARAMS.FOR /HE2PAW/ MHE20W(MFREQ)

    # ===== PARAMS.FOR : COMMON /VELPAR/ =====
    "ANGL": ("array", ("MMU", ), "np.float64"),  # PARAMS.FOR /VELPAR/ ANGL(MMU)
    "WANGL": ("array", ("MMU", ), "np.float64"),  # PARAMS.FOR /VELPAR/ WANGL(MMU)
    "VELC": ("array", ("MDEPTH", ), "np.float64"),  # PARAMS.FOR /VELPAR/ VELC(MDEPTH)
    "NMU0": ("scalar", (), "np.int64"),  # PARAMS.FOR /VELPAR/ NMU0
    "IFLUX": ("scalar", (), "np.int64"),  # PARAMS.FOR /VELPAR/ IFLUX

    # ===== MODELP.FOR : COMMON /MODELP/ =====
    "DM": ("array", ("MDEPTH", ), "np.float64"),  # MODELP.FOR /MODELP/ DM(MDEPTH)
    "TEMP": ("array", ("MDEPTH", ), "np.float64"),  # MODELP.FOR /MODELP/ TEMP(MDEPTH)
    "ELEC": ("array", ("MDEPTH", ), "np.float64"),  # MODELP.FOR /MODELP/ ELEC(MDEPTH)
    "DENS": ("array", ("MDEPTH", ), "np.float64"),  # MODELP.FOR /MODELP/ DENS(MDEPTH)
    "ZD": ("array", ("MDEPTH", ), "np.float64"),  # MODELP.FOR /MODELP/ ZD(MDEPTH)
    "VTURB": ("array", ("MDEPTH", ), "np.float64"),  # MODELP.FOR /MODELP/ VTURB(MDEPTH)
    "VTB": ("scalar", (), "np.float64"),  # MODELP.FOR /MODELP/ VTB
    "ABSTD": ("array", ("MDEPTH", ), "np.float64"),  # MODELP.FOR /MODELP/ ABSTD(MDEPTH)
    "ABSTDW": ("array", ("MFREQC", "MDEPTH", ), "np.float64"),  # MODELP.FOR /MODELP/ ABSTDW(MFREQC,MDEPTH)
    "POPUL": ("array", ("MLEVEL", "MDEPTH", ), "np.float64"),  # MODELP.FOR /MODELP/ POPUL(MLEVEL,MDEPTH)
    "POPREL": ("array", ("MLEVEL", "MDEPTH", ), "np.float64"),  # MODELP.FOR /MODELP/ POPREL(MLEVEL,MDEPTH)
    "DMR0": ("array", ("MDEPTH", ), "np.float64"),  # MODELP.FOR /MODELP/ DMR0(MDEPTH)
    "DMRP": ("array", ("MDEPTH", ), "np.float64"),  # MODELP.FOR /MODELP/ DMRP(MDEPTH)
    "SBF": ("array", ("MLEVEL", ), "np.float64"),  # MODELP.FOR /MODELP/ SBF(MLEVEL)
    "USUM": ("array", ("MIOEX", ), "np.float64"),  # MODELP.FOR /MODELP/ USUM(MIOEX)
    "WOP": ("array", ("MLEVEL", "MDEPTH", ), "np.float64"),  # MODELP.FOR /MODELP/ WOP(MLEVEL,MDEPTH)
    "WNHINT": ("array", ("NLMX", "MDEPTH", ), "np.float64"),  # MODELP.FOR /MODELP/ WNHINT(NLMX,MDEPTH)
    "WNHE2": ("array", ("NLMX", "MDEPTH", ), "np.float64"),  # MODELP.FOR /MODELP/ WNHE2(NLMX,MDEPTH)
    "RRR": ("array", ("MDEPTH", "MION", "MATOM", ), "np.float64"),  # MODELP.FOR /MODELP/ RRR(MDEPTH,MION,MATOM)（即注释所称 COMMON/RRRVAL/，synspec54.f:1883）
    "JT": ("array", ("MDEPTH", ), "np.int64"),  # MODELP.FOR /MODELP/ JT(MDEPTH)
    "TI0": ("array", ("MDEPTH", ), "np.float64"),  # MODELP.FOR /MODELP/ TI0(MDEPTH)
    "TI1": ("array", ("MDEPTH", ), "np.float64"),  # MODELP.FOR /MODELP/ TI1(MDEPTH)
    "TI2": ("array", ("MDEPTH", ), "np.float64"),  # MODELP.FOR /MODELP/ TI2(MDEPTH)

    # ===== MODELP.FOR : COMMON /MOLPAR/ =====
    "RRMOL": ("array", ("MMOLEC", "MDEPTH", ), "np.float64"),  # MODELP.FOR /MOLPAR/ RRMOL(MMOLEC,MDEPTH)
    "DOPMOL": ("array", ("MMOLEC", "MDEPTH", ), "np.float64"),  # MODELP.FOR /MOLPAR/ DOPMOL(MMOLEC,MDEPTH)
    "AMMOL": ("array", ("MMOLEC", ), "np.float64"),  # MODELP.FOR /MOLPAR/ AMMOL(MMOLEC)
    "CMOL": ("array", ("MMOLEC", ), "object"),  # MODELP.FOR /MOLPAR/ character*8 CMOL(MMOLEC)
    "anh2": ("array", ("MDEPTH", ), "np.float64"),  # MODELP.FOR /MOLPAR/ anh2(mdepth)
    "anch": ("array", ("MDEPTH", ), "np.float64"),  # MODELP.FOR /MOLPAR/ anch(mdepth)
    "anoh": ("array", ("MDEPTH", ), "np.float64"),  # MODELP.FOR /MOLPAR/ anoh(mdepth)
    "anhm": ("array", ("MDEPTH", ), "np.float64"),  # MODELP.FOR /MOLPAR/ anhm(mdepth)

    # ===== MODELP.FOR : COMMON /OPACAT/ =====
    "OPATM": ("array", ("MATOM", "MFREQ", "MDEPTH", ), "np.float64"),  # MODELP.FOR /OPACAT/ OPATM(MATOM,MFREQ,MDEPTH)
    "EMATM": ("array", ("MATOM", "MFREQ", "MDEPTH", ), "np.float64"),  # MODELP.FOR /OPACAT/ EMATM(MATOM,MFREQ,MDEPTH)
    "OPATML": ("array", ("MATOM", "MFREQ", ), "np.float64"),  # MODELP.FOR /OPACAT/ OPATML(MATOM,MFREQ)
    "GRADAT": ("array", ("MATOM", "MDEPTH", ), "np.float64"),  # MODELP.FOR /OPACAT/ GRADAT(MATOM,MDEPTH)
    "GRADFA": ("array", ("MATOM", "MDEPTH", ), "np.float64"),  # MODELP.FOR /OPACAT/ GRADFA(MATOM,MDEPTH)
    "POPAT": ("array", ("MATOM", "MDEPTH", ), "np.float64"),  # MODELP.FOR /OPACAT/ POPAT(MATOM,MDEPTH)
    "DGRAD0": ("array", ("MATOM", "MATOM", "MDEPTH", ), "np.float64"),  # MODELP.FOR /OPACAT/ DGRAD0(MATOM,MATOM,MDEPTH)
    "DGRADP": ("array", ("MATOM", "MATOM", "MDEPTH", ), "np.float64"),  # MODELP.FOR /OPACAT/ DGRADP(MATOM,MATOM,MDEPTH)

    # ===== MODELP.FOR : COMMON /RADFLD/ =====
    # （注释掉的 FAK/ALI/FLXH(MFREQ,MDEPTH) 不收录）
    "RAD": ("array", ("MFREQ", "MDEPTH", ), "np.float64"),  # MODELP.FOR /RADFLD/ RAD(MFREQ,MDEPTH)
    "RAD0": ("array", ("MFREQ", "MDEPTH", ), "np.float64"),  # MODELP.FOR /RADFLD/ RAD0(MFREQ,MDEPTH)
    "FLX0": ("array", ("MFREQ", "MDEPTH", ), "np.float64"),  # MODELP.FOR /RADFLD/ FLX0(MFREQ,MDEPTH)
    "flxt": ("array", ("MDEPTH", ), "np.float64"),  # MODELP.FOR /RADFLD/ flxt(mdepth)
    "flxi": ("array", ("MDEPTH", ), "np.float64"),  # MODELP.FOR /RADFLD/ flxi(mdepth)

    # ===== MODELP.FOR : COMMON /XENPRF/ =====
    "PRFXB": ("array", ("MLINH", "MHWL", "MHT", "MHE", ), "np.float64"),  # MODELP.FOR /XENPRF/ PRFXB(MLINH,MHWL,MHT,MHE)
    "PRFXR": ("array", ("MLINH", "MHWL", "MHT", "MHE", ), "np.float64"),  # MODELP.FOR /XENPRF/ PRFXR(MLINH,MHWL,MHT,MHE)
    "PRFB": ("array", ("MLINH", "MDEPTH", "MHWL", ), "np.float64"),  # MODELP.FOR /XENPRF/ PRFB(MLINH,MDEPTH,MHWL)
    "PRFR": ("array", ("MLINH", "MDEPTH", "MHWL", ), "np.float64"),  # MODELP.FOR /XENPRF/ PRFR(MLINH,MDEPTH,MHWL)
    "ALXEN": ("array", ("MLINH", "MHWL", ), "np.float64"),  # MODELP.FOR /XENPRF/ ALXEN(MLINH,MHWL)
    "XTXEN": ("array", ("MHT", "MLINH", ), "np.float64"),  # MODELP.FOR /XENPRF/ XTXEN(MHT,MLINH)
    "XNEXEN": ("array", ("MHE", "MLINH", ), "np.float64"),  # MODELP.FOR /XENPRF/ XNEXEN(MHE,MLINH)
    "XNEMIN": ("scalar", (), "np.float64"),  # MODELP.FOR /XENPRF/ XNEMIN
    "NWLXEN": ("array", ("MLINH", ), "np.int64"),  # MODELP.FOR /XENPRF/ NWLXEN(MLINH)
    "NTHXEN": ("array", ("MLINH", ), "np.int64"),  # MODELP.FOR /XENPRF/ NTHXEN(MLINH)
    "NEHXEN": ("array", ("MLINH", ), "np.int64"),  # MODELP.FOR /XENPRF/ NEHXEN(MLINH)
    "ILXEN": ("array", ("4", "22", ), "np.int64"),  # MODELP.FOR /XENPRF/ ILXEN(4,22)
    "IHXENB": ("scalar", (), "np.int64"),  # MODELP.FOR /XENPRF/ IHXENB

    # ===== LINDAT.FOR : COMMON /LINTOT/ =====
    "FREQ0": ("array", ("MLIN0", ), "np.float64"),  # LINDAT.FOR /LINTOT/ FREQ0(MLIN0)
    "EXCL0": ("array", ("MLIN0", ), "np.float32"),  # LINDAT.FOR /LINTOT/ REAL*4 EXCL0(MLIN0)
    "EXCU0": ("array", ("MLIN0", ), "np.float32"),  # LINDAT.FOR /LINTOT/ REAL*4 EXCU0(MLIN0)
    "GF0": ("array", ("MLIN0", ), "np.float32"),  # LINDAT.FOR /LINTOT/ REAL*4 GF0(MLIN0)
    "EXTIN": ("array", ("MLIN0", ), "np.float32"),  # LINDAT.FOR /LINTOT/ REAL*4 EXTIN(MLIN0)
    "BNUL": ("array", ("MLIN0", ), "np.float32"),  # LINDAT.FOR /LINTOT/ REAL*4 BNUL(MLIN0)
    "INDAT": ("array", ("MLIN0", ), "np.int64"),  # LINDAT.FOR /LINTOT/ INDAT(MLIN0)
    "INDNLT": ("array", ("MLIN0", ), "np.int64"),  # LINDAT.FOR /LINTOT/ INDNLT(MLIN0)
    "ILOWN": ("array", ("MLIN0", ), "np.int64"),  # LINDAT.FOR /LINTOT/ ILOWN(MLIN0)
    "IUPN": ("array", ("MLIN0", ), "np.int64"),  # LINDAT.FOR /LINTOT/ IUPN(MLIN0)
    "IJCONT": ("array", ("MLIN0", ), "np.int64"),  # LINDAT.FOR /LINTOT/ IJCONT(MLIN0)
    "INDLIN": ("array", ("MLIN", ), "np.int64"),  # LINDAT.FOR /LINTOT/ INDLIN(MLIN)
    "INDLIP": ("array", ("MLIN", ), "np.int64"),  # LINDAT.FOR /LINTOT/ INDLIP(MLIN)
    "NLIN0": ("scalar", (), "np.int64"),  # LINDAT.FOR /LINTOT/ NLIN0
    "NLIN": ("scalar", (), "np.int64"),  # LINDAT.FOR /LINTOT/ NLIN
    "IRLIST": ("scalar", (), "np.int64"),  # LINDAT.FOR /LINTOT/ IRLIST
    "NNLT": ("scalar", (), "np.int64"),  # LINDAT.FOR /LINTOT/ NNLT
    "NGRIEM": ("scalar", (), "np.int64"),  # LINDAT.FOR /LINTOT/ NGRIEM

    # ===== LINDAT.FOR : COMMON /MOLTOT/ =====
    "FREQM": ("array", ("MLINM0", "MMLIST", ), "np.float64"),  # LINDAT.FOR /MOLTOT/ FREQM(MLINM0,MMLIST)
    "EXCLM": ("array", ("MLINM0", "MMLIST", ), "np.float32"),  # LINDAT.FOR /MOLTOT/ REAL*4 EXCLM(MLINM0,MMLIST)
    "GFM": ("array", ("MLINM0", "MMLIST", ), "np.float32"),  # LINDAT.FOR /MOLTOT/ REAL*4 GFM(MLINM0,MMLIST)
    "EXTINM": ("array", ("MLINM0", "MMLIST", ), "np.float32"),  # LINDAT.FOR /MOLTOT/ REAL*4 EXTINM(MLINM0,MMLIST)
    "GRM": ("array", ("MLINM0", "MMLIST", ), "np.float32"),  # LINDAT.FOR /MOLTOT/ REAL*4 GRM(MLINM0,MMLIST)
    "GSM": ("array", ("MLINM0", "MMLIST", ), "np.float32"),  # LINDAT.FOR /MOLTOT/ REAL*4 GSM(MLINM0,MMLIST)
    "GWM": ("array", ("MLINM0", "MMLIST", ), "np.float32"),  # LINDAT.FOR /MOLTOT/ REAL*4 GWM(MLINM0,MMLIST)
    "GVDWH2": ("array", ("MLINM0", "MMLIST", ), "np.float32"),  # LINDAT.FOR /MOLTOT/ REAL*4 GVDWH2(MLINM0,MMLIST)
    "GEXPH2": ("array", ("MLINM0", "MMLIST", ), "np.float32"),  # LINDAT.FOR /MOLTOT/ REAL*4 GEXPH2(MLINM0,MMLIST)
    "GVDWHE": ("array", ("MLINM0", "MMLIST", ), "np.float32"),  # LINDAT.FOR /MOLTOT/ REAL*4 GVDWHE(MLINM0,MMLIST)
    "GEXPHE": ("array", ("MLINM0", "MMLIST", ), "np.float32"),  # LINDAT.FOR /MOLTOT/ REAL*4 GEXPHE(MLINM0,MMLIST)
    "INDATM": ("array", ("MLINM0", "MMLIST", ), "np.int64"),  # LINDAT.FOR /MOLTOT/ INDATM(MLINM0,MMLIST)
    "INMLIN": ("array", ("MLINM", "MMLIST", ), "np.int64"),  # LINDAT.FOR /MOLTOT/ INMLIN(MLINM,MMLIST)
    "INMLIP": ("array", ("MLINM", "MMLIST", ), "np.int64"),  # LINDAT.FOR /MOLTOT/ INMLIP(MLINM,MMLIST)
    "NLINM0": ("array", ("MMLIST", ), "np.int64"),  # LINDAT.FOR /MOLTOT/ NLINM0(MMLIST)
    "NLINML": ("array", ("MMLIST", ), "np.int64"),  # LINDAT.FOR /MOLTOT/ NLINML(MMLIST)
    "NLINMT": ("array", ("MMLIST", ), "np.int64"),  # LINDAT.FOR /MOLTOT/ NLINMT(MMLIST)
    "IUNITM": ("array", ("MMLIST", ), "np.int64"),  # LINDAT.FOR /MOLTOT/ IUNITM(MMLIST)
    "INACTM": ("array", ("MMLIST", ), "np.int64"),  # LINDAT.FOR /MOLTOT/ INACTM(MMLIST)
    "IVDWLI": ("array", ("MMLIST", ), "np.int64"),  # LINDAT.FOR /MOLTOT/ IVDWLI(MMLIST)
    "NMLIST": ("scalar", (), "np.int64"),  # LINDAT.FOR /MOLTOT/ NMLIST

    # ===== LINDAT.FOR : COMMON /LISPAR/ =====
    "AMLIST": ("array", ("MMLIST", ), "object"),  # LINDAT.FOR /LISPAR/ CHARACTER*40 AMLIST(0:MMLIST)（0 基，分配后 0..MMLIST 可用）
    "IBIN": ("array", ("MMLIST", ), "np.int64"),  # LINDAT.FOR /LISPAR/ IBIN(0:MMLIST)（0 基，同上）

    # ===== LINDAT.FOR : COMMON /LINPRF/ =====
    "GAMR0": ("array", ("MPRF", ), "np.float32"),  # LINDAT.FOR /LINPRF/ REAL*4 GAMR0(MPRF)
    "GS0": ("array", ("MPRF", ), "np.float32"),  # LINDAT.FOR /LINPRF/ REAL*4 GS0(MPRF)
    "GW0": ("array", ("MPRF", ), "np.float32"),  # LINDAT.FOR /LINPRF/ REAL*4 GW0(MPRF)
    "WGR0": ("array", ("4", "MGRIEM", ), "np.float32"),  # LINDAT.FOR /LINPRF/ REAL*4 WGR0(4,MGRIEM)
    "IPRF0": ("array", ("MPRF", ), "np.int64"),  # LINDAT.FOR /LINPRF/ IPRF0(MPRF)
    "ISPRF": ("array", ("MPRF", ), "np.int64"),  # LINDAT.FOR /LINPRF/ ISPRF(MPRF)
    "IGRIEM": ("array", ("MPRF", ), "np.int64"),  # LINDAT.FOR /LINPRF/ IGRIEM(MPRF)
    "ISP0": ("array", ("MSPHE2", ), "np.int64"),  # LINDAT.FOR /LINPRF/ ISP0(MSPHE2)
    "NSP": ("scalar", (), "np.int64"),  # LINDAT.FOR /LINPRF/ NSP

    # ===== LINDAT.FOR : COMMON /LINNLT/ =====
    "ABCENT": ("array", ("MNLT", "MDEPTH", ), "np.float64"),  # LINDAT.FOR /LINNLT/ ABCENT(MNLT,MDEPTH)
    "SLIN": ("array", ("MNLT", "MDEPTH", ), "np.float64"),  # LINDAT.FOR /LINNLT/ SLIN(MNLT,MDEPTH)

    # ===== LINDAT.FOR : COMMON /LINDEP/ =====
    "PLAN": ("array", ("MDEPTH", ), "np.float64"),  # LINDAT.FOR /LINDEP/ PLAN(MDEPTH)
    "STIM": ("array", ("MDEPTH", ), "np.float64"),  # LINDAT.FOR /LINDEP/ STIM(MDEPTH)
    "EXHK": ("array", ("MDEPTH", ), "np.float64"),  # LINDAT.FOR /LINDEP/ EXHK(MDEPTH)

    # ===== LINDAT.FOR : COMMON /LINCTR/ =====
    "DFRCON": ("scalar", (), "np.float64"),  # LINDAT.FOR /LINCTR/ DFRCON
    "IJCNTR": ("array", ("MLIN", ), "np.int64"),  # LINDAT.FOR /LINCTR/ IJCNTR(MLIN)
    "IJCMTR": ("array", ("MLINM", "MMLIST", ), "np.int64"),  # LINDAT.FOR /LINCTR/ IJCMTR(MLINM,MMLIST)

    # ===== LINDAT.FOR : COMMON /MLINRE/ =====
    "FRLASM": ("array", ("MMLIST", ), "np.float64"),  # LINDAT.FOR /MLINRE/ FRLASM(MMLIST)
    "ALASTM": ("array", ("MMLIST", ), "np.float64"),  # LINDAT.FOR /MLINRE/ ALASTM(MMLIST)
    "TMLIM": ("array", ("MMLIST", ), "np.float64"),  # LINDAT.FOR /MLINRE/ TMLIM(MMLIST)
    "NXTSEM": ("array", ("MMLIST", ), "np.int64"),  # LINDAT.FOR /MLINRE/ NXTSEM(MMLIST)
    "IPRSEM": ("array", ("MMLIST", ), "np.int64"),  # LINDAT.FOR /MLINRE/ IPRSEM(MMLIST)
    "IREADM": ("array", ("MMLIST", ), "np.int64"),  # LINDAT.FOR /MLINRE/ IREADM(MMLIST)

    # ===== SYNTHP.FOR : COMMON /FREQSY/ =====
    "FREQ": ("array", ("MFREQ", ), "np.float64"),  # SYNTHP.FOR /FREQSY/ FREQ(MFREQ)
    "W": ("array", ("MFREQ", ), "np.float64"),  # SYNTHP.FOR /FREQSY/ W(MFREQ)
    "WLAM": ("array", ("MFREQ", ), "np.float64"),  # SYNTHP.FOR /FREQSY/ WLAM(MFREQ)
    "FRX1": ("array", ("MFREQ", ), "np.float64"),  # SYNTHP.FOR /FREQSY/ FRX1(MFREQ)
    "FRX2": ("array", ("MFREQ", ), "np.float64"),  # SYNTHP.FOR /FREQSY/ FRX2(MFREQ)
    "BNUE": ("array", ("MFREQ", ), "np.float64"),  # SYNTHP.FOR /FREQSY/ BNUE(MFREQ)
    "FRQOBS": ("array", ("MFREQ", ), "np.float64"),  # SYNTHP.FOR /FREQSY/ FRQOBS(MFREQ)
    "WLOBS": ("array", ("MFREQ", ), "np.float64"),  # SYNTHP.FOR /FREQSY/ WLOBS(MFREQ)
    "FREQC": ("array", ("MFREQC", ), "np.float64"),  # SYNTHP.FOR /FREQSY/ FREQC(MFREQC)
    "WLAMC": ("array", ("MFREQC", ), "np.float64"),  # SYNTHP.FOR /FREQSY/ WLAMC(MFREQC)
    "IJCINT": ("array", ("MFREQ", ), "np.int64"),  # SYNTHP.FOR /FREQSY/ IJCINT(MFREQ)

    # ===== SYNTHP.FOR : COMMON /CRSAVG/ =====
    "FRECR": ("array", ("MCROSS", "MFCRA", ), "np.float64"),  # SYNTHP.FOR /CRSAVG/ FRECR(MCROSS,MFCRA)
    "CROSR": ("array", ("MCROSS", "MFCRA", ), "np.float64"),  # SYNTHP.FOR /CRSAVG/ CROSR(MCROSS,MFCRA)
    "CRMX": ("array", ("MCROSS", ), "np.float64"),  # SYNTHP.FOR /CRSAVG/ CRMX(MCROSS)
    "NFCR": ("array", ("MCROSS", ), "np.int64"),  # SYNTHP.FOR /CRSAVG/ NFCR(MCROSS)
    "IASV": ("scalar", (), "np.int64"),  # SYNTHP.FOR /CRSAVG/ IASV

    # ===== SYNTHP.FOR : COMMON /CRSAVQ/ =====
    "FRECQ": ("array", ("MPHOT", "MFCRA", ), "np.float64"),  # SYNTHP.FOR /CRSAVQ/ FRECQ(MPHOT,MFCRA)
    "QHOT": ("array", ("MPHOT", "MFCRA", ), "np.float64"),  # SYNTHP.FOR /CRSAVQ/ QHOT(MPHOT,MFCRA)
    "AQHT": ("array", ("MPHOT", ), "np.float64"),  # SYNTHP.FOR /CRSAVQ/ AQHT(MPHOT)
    "EQHT": ("array", ("MPHOT", ), "np.float64"),  # SYNTHP.FOR /CRSAVQ/ EQHT(MPHOT)
    "GQHT": ("array", ("MPHOT", ), "np.float64"),  # SYNTHP.FOR /CRSAVQ/ GQHT(MPHOT)
    "CRMY": ("array", ("MPHOT", ), "np.float64"),  # SYNTHP.FOR /CRSAVQ/ CRMY(MPHOT)
    "NFQHT": ("array", ("MPHOT", ), "np.int64"),  # SYNTHP.FOR /CRSAVQ/ NFQHT(MPHOT)
    "NQHT": ("scalar", (), "np.int64"),  # SYNTHP.FOR /CRSAVQ/ NQHT

    # ===== WINCOM.FOR : COMMON /COMANG/ =====
    "BMU": ("array", ("MKU", "MDEPTH", ), "np.float64"),  # WINCOM.FOR /COMANG/ BMU(MKU,MDEPTH)
    "WMUJ": ("array", ("MKU", "MDEPTH", ), "np.float64"),  # WINCOM.FOR /COMANG/ WMUJ(MKU,MDEPTH)
    "WMUH": ("array", ("MKU", ), "np.float64"),  # WINCOM.FOR /COMANG/ WMUH(MKU)

    # ===== WINCOM.FOR : COMMON /CORADI/ =====
    "RD": ("array", ("MDEPTH", ), "np.float64"),  # WINCOM.FOR /CORADI/ RD(MDEPTH)
    "RCORE": ("scalar", (), "np.float64"),  # WINCOM.FOR /CORADI/ RCORE
    "RFNORM": ("scalar", (), "np.float64"),  # WINCOM.FOR /CORADI/ RFNORM
    "PIM": ("array", ("MKU", ), "np.float64"),  # WINCOM.FOR /CORADI/ PIM(MKU)
    "RAD1": ("array", ("MDEPTH", ), "np.float64"),  # WINCOM.FOR /CORADI/ RAD1(MDEPTH)
    "DELZ": ("array", ("MKU", "MDEPTH", ), "np.float64"),  # WINCOM.FOR /CORADI/ DELZ(MKU,MDEPTH)
    "NUD": ("array", ("MKU", ), "np.int64"),  # WINCOM.FOR /CORADI/ NUD(MKU)
    "NUDF": ("array", ("MKU", ), "np.int64"),  # WINCOM.FOR /CORADI/ NUDF(MKU)
    "KMU": ("scalar", (), "np.int64"),  # WINCOM.FOR /CORADI/ KMU
    "NREXT": ("scalar", (), "np.int64"),  # WINCOM.FOR /CORADI/ NREXT
    "NRCORE": ("scalar", (), "np.int64"),  # WINCOM.FOR /CORADI/ NRCORE
    "NFIRY": ("scalar", (), "np.int64"),  # WINCOM.FOR /CORADI/ NFIRY
    "NDF": ("scalar", (), "np.int64"),  # WINCOM.FOR /CORADI/ NDF

    # ===== WINCOM.FOR : COMMON /CORAF/ =====
    "DELZF": ("array", ("MEXT", "MDEPF", ), "np.float64"),  # WINCOM.FOR /CORAF/ DELZF(MEXT,MDEPF)
    "DFRQF": ("array", ("MEXT", "2*MDEPF", ), "np.float64"),  # WINCOM.FOR /CORAF/ DFRQF(MEXT,2*MDEPF)

    # ===== WINCOM.FOR : COMMON /COVEL/ =====
    "VEL": ("array", ("MDEPTH", ), "np.float64"),  # WINCOM.FOR /COVEL/ VEL(MDEPTH)
    "DFRQ": ("array", ("MKU", "2*MDEPTH", ), "np.float64"),  # WINCOM.FOR /COVEL/ DFRQ(MKU,2*MDEPTH)
    "DVD": ("array", ("MDEPTH", ), "np.float64"),  # WINCOM.FOR /COVEL/ DVD(MDEPTH)
    "XMDOT": ("scalar", (), "np.float64"),  # WINCOM.FOR /COVEL/ XMDOT
    "XMD4": ("scalar", (), "np.float64"),  # WINCOM.FOR /COVEL/ XMD4
    "BETAV": ("scalar", (), "np.float64"),  # WINCOM.FOR /COVEL/ BETAV
    "VINF": ("scalar", (), "np.float64"),  # WINCOM.FOR /COVEL/ VINF

    # ===== WINCOM.FOR : COMMON /EXTMOD/ =====
    "FFQ": ("array", ("MOPAC", ), "np.float64"),  # WINCOM.FOR /EXTMOD/ FFQ(MOPAC)
    "FFQV": ("array", ("MOPAC", ), "np.float64"),  # WINCOM.FOR /EXTMOD/ FFQV(MOPAC)
    "RDF": ("array", ("MDEPF", ), "np.float64"),  # WINCOM.FOR /EXTMOD/ RDF(MDEPF)
    "DENSF": ("array", ("MDEPF", ), "np.float64"),  # WINCOM.FOR /EXTMOD/ DENSF(MDEPF)
    "VELF": ("array", ("MEXT", "MDEPF", ), "np.float64"),  # WINCOM.FOR /EXTMOD/ VELF(MEXT,MDEPF)
    "DRAY": ("array", ("MEXT", "2*MDEPF", ), "np.float64"),  # WINCOM.FOR /EXTMOD/ DRAY(MEXT,2*MDEPF)
    "KRAY": ("array", ("MEXT", "2*MDEPF", ), "np.int64"),  # WINCOM.FOR /EXTMOD/ KRAY(MEXT,2*MDEPF)
    "NOPAC": ("scalar", (), "np.int64"),  # WINCOM.FOR /EXTMOD/ NOPAC

    # ===== WINCOM.FOR : COMMON /OPAVEL/ =====
    "WDIL": ("array", ("MDEPTH", ), "np.float64"),  # WINCOM.FOR /OPAVEL/ WDIL(MDEPTH)
    "PLANW": ("array", ("MDEPTH", ), "np.float64"),  # WINCOM.FOR /OPAVEL/ PLANW(MDEPTH)
    "TRAD": ("array", ("MTRAD", "MDEPTH", ), "np.float64"),  # WINCOM.FOR /OPAVEL/ TRAD(MTRAD,MDEPTH)
    "DENSCON": ("array", ("MDEPTH", ), "np.float64"),  # WINCOM.FOR /OPAVEL/ DENSCON(MDEPTH)

    # ==================================================================
    # 以下为 synspec54.f 子程序体内补充声明的 COMMON 块
    # ==================================================================

    # ===== synspec54.f:190 /quasun/ =====
    "nunalp": ("scalar", (), "np.int64"),  # /quasun/ nunalp
    "nunbet": ("scalar", (), "np.int64"),  # /quasun/ nunbet
    "nungam": ("scalar", (), "np.int64"),  # /quasun/ nungam
    "nunbal": ("scalar", (), "np.int64"),  # /quasun/ nunbal

    # ===== synspec54.f:303 /dissol/ =====
    "fropc": ("array", ("MLEVEL", ), "np.float64"),  # /dissol/ fropc(mlevel)
    "indexp": ("array", ("MLEVEL", ), "np.int64"),  # /dissol/ indexp(mlevel)

    # ===== synspec54.f:310 /PRINTP/ =====
    "TYPLEV": ("array", ("MLEVEL", ), "object"),  # /PRINTP/ CHARACTER*10 TYPLEV(MLEVEL)（声明见 :304）

    # ===== synspec54.f:311 /IONDAT/ =====
    "IATI": ("array", ("MION", ), "np.int64"),  # /IONDAT/ IATI(MION)
    "IZI": ("array", ("MION", ), "np.int64"),  # /IONDAT/ IZI(MION)
    "NLEVS": ("array", ("MION", ), "np.int64"),  # /IONDAT/ NLEVS(MION)；/NL2PAR/ NLEVS(MNION)（MNION=MIOEX=90=MION，同尺寸共用此条目）
    "NLLIM": ("array", ("MION", ), "np.int64"),  # /IONDAT/ NLLIM(MION)

    # ===== synspec54.f:312 /IONFIL/ =====
    "FIDATA": ("array", ("MION", ), "object"),  # /IONFIL/ CHARACTER*40 FIDATA(MION)（声明见 :306）
    "FIODF1": ("array", ("MION", ), "object"),  # /IONFIL/ CHARACTER*40 FIODF1(MION)
    "FIODF2": ("array", ("MION", ), "object"),  # /IONFIL/ CHARACTER*40 FIODF2(MION)
    "FIBFCS": ("array", ("MION", ), "object"),  # /IONFIL/ CHARACTER*40 FIBFCS(MION)

    # ===== synspec54.f:313 /INUNIT/ =====
    "IUNIT": ("scalar", (), "np.int64"),  # /INUNIT/ IUNIT

    # ===== synspec54.f:314 /STRPAR/ =====
    "IMER": ("scalar", (), "np.int64"),  # /STRPAR/ IMER
    "ITR": ("scalar", (), "np.int64"),  # /STRPAR/ ITR
    "IC": ("scalar", (), "np.int64"),  # /STRPAR/ IC
    "IL": ("scalar", (), "np.int64"),  # /STRPAR/ IL
    "IP": ("scalar", (), "np.int64"),  # /STRPAR/ IP
    "NLASTE": ("scalar", (), "np.int64"),  # /STRPAR/ NLASTE
    "NHOD": ("scalar", (), "np.int64"),  # /STRPAR/ NHOD

    # ===== synspec54.f:315 /quasex/ =====
    "iexpl": ("array", ("MLEVEL", ), "np.int64"),  # /quasex/ iexpl(mlevel)
    "iltot": ("array", ("MLEVEL", ), "np.int64"),  # /quasex/ iltot(mlevel)

    # ===== synspec54.f:656 /TOPCS/ =====
    "CTOP": ("array", ("MFIT", "MCROSS", ), "np.float64"),  # /TOPCS/ CTOP(MFIT,MCROSS)  ! sigma=alog10(sigma/10^-18) of fit point
    "XTOP": ("array", ("MFIT", "MCROSS", ), "np.float64"),  # /TOPCS/ XTOP(MFIT,MCROSS)  ! x = alog10(nu/nu0) of fit point

    # ===== synspec54.f:1125 /hhebrd/ =====
    "sthe": ("scalar", (), "np.float64"),  # /hhebrd/ sthe
    "nunhhe": ("scalar", (), "np.int64"),  # /hhebrd/ nunhhe

    # ===== synspec54.f:1126 /gompar/ =====
    "hglim": ("scalar", (), "np.float64"),  # /gompar/ hglim
    "ihgom": ("scalar", (), "np.int64"),  # /gompar/ ihgom

    # ===== synspec54.f:1127 /brdstd/ =====
    "gsstd": ("scalar", (), "np.float64"),  # /brdstd/ gsstd
    "gwstd": ("scalar", (), "np.float64"),  # /brdstd/ gwstd

    # ===== synspec54.f:1888 /BLAPAR/ =====
    "RELOP": ("scalar", (), "np.float64"),  # /BLAPAR/ RELOP
    "SPACE0": ("scalar", (), "np.float64"),  # /BLAPAR/ SPACE0
    "CUTOF0": ("scalar", (), "np.float64"),  # /BLAPAR/ CUTOF0
    "TSTD": ("scalar", (), "np.float64"),  # /BLAPAR/ TSTD
    "DSTD": ("scalar", (), "np.float64"),  # /BLAPAR/ DSTD
    "ALAMC": ("scalar", (), "np.float64"),  # /BLAPAR/ ALAMC

    # ===== synspec54.f:1889 /HPOPST/ =====
    "HPOP": ("scalar", (), "np.float64"),  # /HPOPST/ HPOP

    # ===== synspec54.f:1961 /moltst/ =====
    "pfmol": ("array", ("600", "MDEPTH", ), "np.float64"),  # /moltst/ pfmol(600,mdepth)
    "anmol": ("array", ("600", "MDEPTH", ), "np.float64"),  # /moltst/ anmol(600,mdepth)
    "pfato": ("array", ("100", "MDEPTH", ), "np.float64"),  # /moltst/ pfato(100,mdepth)
    "anato": ("array", ("100", "MDEPTH", ), "np.float64"),  # /moltst/ anato(100,mdepth)
    "pfion": ("array", ("100", "MDEPTH", ), "np.float64"),  # /moltst/ pfion(100,mdepth)
    "anion": ("array", ("100", "MDEPTH", ), "np.float64"),  # /moltst/ anion(100,mdepth)

    # ===== synspec54.f:1964 /ioniz2/ =====
    "anion2": ("array", ("30", "MDEPTH", ), "np.float64"),  # /ioniz2/ anion2(30,mdepth)

    # ===== synspec54.f:2091 /LIMPAR/ =====
    "ALAM0": ("scalar", (), "np.float64"),  # /LIMPAR/ ALAM0
    "ALAM1": ("scalar", (), "np.float64"),  # /LIMPAR/ ALAM1
    "FRMIN": ("scalar", (), "np.float64"),  # /LIMPAR/ FRMIN
    "FRLAST": ("scalar", (), "np.float64"),  # /LIMPAR/ FRLAST
    "FRLI0": ("scalar", (), "np.float64"),  # /LIMPAR/ FRLI0
    "FRLIM": ("scalar", (), "np.float64"),  # /LIMPAR/ FRLIM

    # ===== synspec54.f:2093 /lasers/ =====
    "lasdel": ("scalar", (), "bool"),  # /lasers/ lasdel（IMPLICIT LOGICAL*1 (L)）

    # ===== synspec54.f:2094 /linrej/ =====
    "ilne": ("array", ("MDEPTH", ), "np.int64"),  # /linrej/ ilne(mdepth)
    "ilvi": ("array", ("MDEPTH", ), "np.int64"),  # /linrej/ ilvi(mdepth)

    # ===== synspec54.f:2095 /velaux/ =====
    "velmax": ("scalar", (), "np.float64"),  # /velaux/ velmax
    "iemoff": ("scalar", (), "np.int64"),  # /velaux/ iemoff
    "nltoff": ("scalar", (), "np.int64"),  # /velaux/ nltoff
    "itrad": ("scalar", (), "np.int64"),  # /velaux/ itrad

    # ===== synspec54.f:2096 /alsave/ =====
    "ALAM0s": ("scalar", (), "np.float64"),  # /alsave/ ALAM0s
    "ALASTs": ("scalar", (), "np.float64"),  # /alsave/ ALASTs
    "CUTOF0s": ("scalar", (), "np.float64"),  # /alsave/ CUTOF0s
    "CUTOFSs": ("scalar", (), "np.float64"),  # /alsave/ CUTOFSs
    "RELOPs": ("scalar", (), "np.float64"),  # /alsave/ RELOPs
    "SPACEs": ("scalar", (), "np.float64"),  # /alsave/ SPACEs

    # ===== synspec54.f:2549 /plaopa/ =====
    "plalin": ("scalar", (), "np.float64"),  # /plaopa/ plalin
    "plcint": ("scalar", (), "np.float64"),  # /plaopa/ plcint
    "chcint": ("scalar", (), "np.float64"),  # /plaopa/ chcint

    # ===== synspec54.f:2550 /conabs/ =====
    "absoc": ("array", ("MFREQC", ), "np.float64"),  # /conabs/ absoc(mfreqc)
    "emisc": ("array", ("MFREQC", ), "np.float64"),  # /conabs/ emisc(mfreqc)
    "scatc": ("array", ("MFREQC", ), "np.float64"),  # /conabs/ scatc(mfreqc)
    "plac": ("array", ("MFREQC", ), "np.float64"),  # /conabs/ plac(mfreqc)

    # ===== synspec54.f:2669 /RTEOPA/ =====
    "CH": ("array", ("MFREQ", "MDEPTH", ), "np.float64"),  # /RTEOPA/ CH(MFREQ,MDEPTH)
    "ET": ("array", ("MFREQ", "MDEPTH", ), "np.float64"),  # /RTEOPA/ ET(MFREQ,MDEPTH)
    "SC": ("array", ("MFREQ", "MDEPTH", ), "np.float64"),  # /RTEOPA/ SC(MFREQ,MDEPTH)

    # ===== synspec54.f:2762 /EMFLUX/ =====
    "FLUX": ("array", ("MFREQ", ), "np.float64"),  # /EMFLUX/ FLUX(MFREQ)
    "FLUXC": ("array", ("MFREQC", ), "np.float64"),  # /EMFLUX/ FLUXC(MFREQC)

    # ===== synspec54.f:2764 /CTRFUN/ =====
    "CINT1": ("array", ("MDEPTH", ), "np.float64"),  # /CTRFUN/ CINT1(MDEPTH)
    "CINT2": ("array", ("MDEPTH", ), "np.float64"),  # /CTRFUN/ CINT2(MDEPTH)
    "CTRI": ("array", ("MDEPTH", ), "np.float64"),  # /CTRFUN/ CTRI(MDEPTH)
    "CTRR": ("array", ("MDEPTH", ), "np.float64"),  # /CTRFUN/ CTRR(MDEPTH)
    "XKAR": ("array", ("MDEPTH", ), "np.float64"),  # /CTRFUN/ XKAR(MDEPTH)
    "ABXLI": ("array", ("MFREQ", ), "np.float64"),  # /CTRFUN/ ABXLI(MFREQ)
    "EMXLI": ("array", ("MFREQ", ), "np.float64"),  # /CTRFUN/ EMXLI(MFREQ)
    "IJCTR": ("array", ("MFREQ", ), "np.int64"),  # /CTRFUN/ IJCTR(MFREQ)

    # ===== synspec54.f:2767 /REFDEP/ =====
    "IREFD": ("array", ("MFREQ", ), "np.int64"),  # /REFDEP/ IREFD(MFREQ)（:9648 处写作 MFRQ，同值 2000）

    # ===== synspec54.f:2768 /CENTRL/ =====
    "ZND": ("scalar", (), "np.float64"),  # /CENTRL/ ZND
    "IFZ0": ("scalar", (), "np.int64"),  # /CENTRL/ IFZ0

    # ===== synspec54.f:4396 /TOPB/ =====
    # 局部 PARAMETER：MMAXOP=200, MOP=15（:4392-4393）
    "SOP": ("array", ("15", "200", ), "np.float64"),  # /TOPB/ SOP(MOP,MMAXOP)  ! sigma = alog10(sigma/10^-18) of fit point
    "XOP": ("array", ("15", "200", ), "np.float64"),  # /TOPB/ XOP(MOP,MMAXOP)  ! x = alog10(nu/nu0) of fit point
    "NOP": ("array", ("200", ), "np.int64"),  # /TOPB/ NOP(MMAXOP)  ! number of fit points for current level
    "NTOTOP": ("scalar", (), "np.int64"),  # /TOPB/ NTOTOP  ! total number of levels in OP data
    "IDLVOP": ("array", ("200", ), "object"),  # /TOPB/ CHARACTER*10 IDLVOP(MMAXOP)（声明见 :4394）
    "LOPREA": ("scalar", (), "bool"),  # /TOPB/ LOPREA  ! .T. OP data read in; .F. OP data not yet read in

    # ===== synspec54.f:6262 /HE2PRF/ =====
    "PRFHE2": ("array", ("19", "MDEPTH", "36", ), "np.float64"),  # /HE2PRF/ PRFHE2(19,MDEPTH,36)
    "WLHE2": ("array", ("19", "36", ), "np.float64"),  # /HE2PRF/ WLHE2(19,36)
    "NWLHE2": ("array", ("19", ), "np.int64"),  # /HE2PRF/ NWLHE2(19)
    "ILHE2": ("array", ("19", ), "np.int64"),  # /HE2PRF/ ILHE2(19)
    "IUHE2": ("array", ("19", ), "np.int64"),  # /HE2PRF/ IUHE2(19)

    # ===== synspec54.f:7254 /PROHE1/（取字面量维度版本；:7392 处 NT=4 同值） =====
    "PRFHE1": ("array", ("50", "4", "8", "3", ), "np.float64"),  # /PROHE1/ PRFHE1(50,4,8,3)
    "DLMHE1": ("array", ("50", "8", "3", ), "np.float64"),  # /PROHE1/ DLMHE1(50,8,3)
    "XNEHE1": ("array", ("8", ), "np.float64"),  # /PROHE1/ XNEHE1(8)
    "NWLAM": ("array", ("8", "4", ), "np.int64"),  # /PROHE1/ NWLAM(8,4)

    # ===== synspec54.f:7256 /PRO447/ =====
    "PRF447": ("array", ("80", "4", "7", ), "np.float64"),  # /PRO447/ PRF447(80,4,7)
    "DLM447": ("array", ("80", "7", ), "np.float64"),  # /PRO447/ DLM447(80,7)
    "XNE447": ("array", ("7", ), "np.float64"),  # /PRO447/ XNE447(7)

    # ===== synspec54.f:7548 /HE2DAT/ =====
    "WL2": ("array", ("36", "19", ), "np.float64"),  # /HE2DAT/ WL2(36,19)
    "XT2": ("array", ("6", ), "np.float64"),  # /HE2DAT/ XT2(6)
    "XNE2": ("array", ("11", "19", ), "np.float64"),  # /HE2DAT/ XNE2(11,19)
    "PRF2": ("array", ("36", "6", "11", ), "np.float64"),  # /HE2DAT/ PRF2(36,6,11)
    "NWL2": ("scalar", (), "np.int64"),  # /HE2DAT/ NWL2
    "NT2": ("scalar", (), "np.int64"),  # /HE2DAT/ NT2
    "NE2": ("scalar", (), "np.int64"),  # /HE2DAT/ NE2

    # ===== synspec54.f:8443 /PHOTCS/（:3502 注释所称 COMMON/PHOPAR/ 即此块） =====
    "PHOT": ("array", ("MFRQ", "MPHOT", ), "np.float64"),  # /PHOTCS/ PHOT(MFRQ,MPHOT)
    "WPHT0": ("scalar", (), "np.float64"),  # /PHOTCS/ WPHT0
    "WPHT1": ("scalar", (), "np.float64"),  # /PHOTCS/ WPHT1
    "APHT": ("array", ("MPHOT", ), "np.float64"),  # /PHOTCS/ APHT(MPHOT)
    "EPHT": ("array", ("MPHOT", ), "np.float64"),  # /PHOTCS/ EPHT(MPHOT)
    "GPHT": ("array", ("MPHOT", ), "np.float64"),  # /PHOTCS/ GPHT(MPHOT)
    "JPHT": ("array", ("MPHOT", ), "np.int64"),  # /PHOTCS/ JPHT(MPHOT)
    "NPHT": ("scalar", (), "np.int64"),  # /PHOTCS/ NPHT

    # ===== synspec54.f:8667 /IPOTLS/ =====
    "IPOTL": ("array", ("MLIN0", ), "np.int64"),  # /IPOTLS/ IPOTL(mlin0)

    # ===== synspec54.f:9258 /igrddd/ =====
    "igrdd": ("scalar", (), "np.int64"),  # /igrddd/ igrdd
    "irelin": ("scalar", (), "np.int64"),  # /igrddd/ irelin

    # ===== synspec54.f:9596 /PRFQUA/ =====
    "DOPA1": ("array", ("MATOM", "MDEPTH", ), "np.float64"),  # /PRFQUA/ DOPA1(MATOM,MDEPTH)
    "VDWC": ("array", ("MDEPTH", ), "np.float64"),  # /PRFQUA/ VDWC(MDEPTH)

    # ===== synspec54.f:9881 /NL2PAR/ =====
    # 局部 PARAMETER：MNION=MIOEX, MNLEV=MLEVEL（:9877-9878）
    "ELIMEV": ("array", ("MIOEX", "MLEVEL", ), "np.float64"),  # /NL2PAR/ ELIMEV(MNION,MNLEV)
    "ELIMOD": ("array", ("MIOEX", "MLEVEL", ), "np.float64"),  # /NL2PAR/ ELIMOD(MNION,MNLEV)
    "ELIML": ("array", ("MIOEX", "MLEVEL", ), "np.float64"),  # /NL2PAR/ ELIML(MNION,MNLEV)
    "ENREV": ("array", ("MIOEX", "MLEVEL", ), "np.float64"),  # /NL2PAR/ ENREV(MNION,MNLEV)
    "ENROD": ("array", ("MIOEX", "MLEVEL", ), "np.float64"),  # /NL2PAR/ ENROD(MNION,MNLEV)
    "INDEV": ("array", ("MIOEX", "MLEVEL", ), "np.int64"),  # /NL2PAR/ INDEV(MNION,MNLEV)
    "INDOD": ("array", ("MIOEX", "MLEVEL", ), "np.int64"),  # /NL2PAR/ INDOD(MNION,MNLEV)
    "INDLV": ("array", ("MIOEX", "MLEVEL", ), "np.int64"),  # /NL2PAR/ INDLV(MNION,MNLEV)
    "INDIO": ("array", ("MIOEX", ), "np.int64"),  # /NL2PAR/ INDIO(MNION)
    "NEVEN": ("array", ("MIOEX", ), "np.int64"),  # /NL2PAR/ NEVEN(MNION)
    "NODD": ("array", ("MIOEX", ), "np.int64"),  # /NL2PAR/ NODD(MNION)
    "NODD0": ("scalar", (), "np.int64"),  # /NL2PAR/ NODD0
    "IATN": ("array", ("MIOEX", ), "np.int64"),  # /NL2PAR/ IATN(MNION)
    "IONN": ("array", ("MIOEX", ), "np.int64"),  # /NL2PAR/ IONN(MNION)
    "NNION": ("scalar", (), "np.int64"),  # /NL2PAR/ NNION

    # ===== synspec54.f:10335 /NLTPOP/ =====
    "PNLT": ("array", ("MATOM", "MION", "MDEPTH", ), "np.float64"),  # /NLTPOP/ PNLT(MATOM,MION,MDEPTH)

    # ===== synspec54.f:11065 无名 COMMON（INKUR） =====
    # DIMENSION POP(MLEVEL),ES(MLEVEL,MLEVEL),BS(MLEVEL)（:11064）
    "POP": ("array", ("MLEVEL", ), "np.float64"),  # 无名 COMMON POP(MLEVEL)
    "ES": ("array", ("MLEVEL", "MLEVEL", ), "np.float64"),  # 无名 COMMON ES(MLEVEL,MLEVEL)
    "BS": ("array", ("MLEVEL", ), "np.float64"),  # 无名 COMMON BS(MLEVEL)

    # ===== synspec54.f:11156 无名 COMMON（INMOD/INSTART） =====
    # DIMENSION ESEMAT(MLEVEL,MLEVEL),BESE(MLEVEL),POPLTE(MLEVEL)（:11154）；
    # 局部 PARAMETER MINPUT=MLEVEL+4（:11153）
    "ESEMAT": ("array", ("MLEVEL", "MLEVEL", ), "np.float64"),  # 无名 COMMON ESEMAT(MLEVEL,MLEVEL)
    "BESE": ("array", ("MLEVEL", ), "np.float64"),  # 无名 COMMON BESE(MLEVEL)
    "POPLTE": ("array", ("MLEVEL", ), "np.float64"),  # 无名 COMMON POPLTE(MLEVEL)
    "POPUL0": ("array", ("MLEVEL", "MDEPTH", ), "np.float64"),  # 无名 COMMON POPUL0(MLEVEL,MDEPTH)；/relabu/ popul0(mlevel,1)（:21788）与其同名，共用此条目（relabu 只用第 1 列）
    "X": ("array", ("MLEVEL + 4", ), "np.float64"),  # 无名 COMMON X(MINPUT)，MINPUT=MLEVEL+4
    "TEMP0": ("array", ("MDEPTH", ), "np.float64"),  # 无名 COMMON TEMP0(MDEPTH)
    "ELEC0": ("array", ("MDEPTH", ), "np.float64"),  # 无名 COMMON ELEC0(MDEPTH)
    "DENS0": ("array", ("MDEPTH", ), "np.float64"),  # 无名 COMMON DENS0(MDEPTH)
    "PPL0": ("array", ("MDEPTH", ), "np.float64"),  # 无名 COMMON PPL0(MDEPTH)
    "PPL": ("array", ("MDEPTH", ), "np.float64"),  # 无名 COMMON PPL(MDEPTH)
    "DEPTH": ("array", ("MDEPTH", ), "np.float64"),  # 无名 COMMON DEPTH(MDEPTH)
    "DM0": ("array", ("MDEPTH", ), "np.float64"),  # 无名 COMMON DM0(MDEPTH)
    "DP": ("array", ("MDEPTH", ), "np.float64"),  # 无名 COMMON DP(MDEPTH)

    # ===== synspec54.f:11423 无名 COMMON（CHANGE） =====
    "POPULL": ("array", ("MLEVEL", "MDEPTH", ), "np.float64"),  # 无名 COMMON POPULL(MLEVEL,MDEPTH)
    "POPL": ("array", ("MLEVEL", ), "np.float64"),  # 无名 COMMON POPL(MLEVEL)

    # ===== synspec54.f:12450 /callarda/ =====
    # 局部 PARAMETER：NXMAX=1400, NNMAX=5（:12448）
    "xlalp": ("array", ("1400", ), "np.float64"),  # /callarda/ xlalp(NXMAX)
    "plalp": ("array", ("1400", "5", ), "np.float64"),  # /callarda/ plalp(NXMAX,NNMAX)
    "stnnea": ("scalar", (), "np.float64"),  # /callarda/ stnnea
    "stncha": ("scalar", (), "np.float64"),  # /callarda/ stncha
    "vneua": ("scalar", (), "np.float64"),  # /callarda/ vneua
    "vchaa": ("scalar", (), "np.float64"),  # /callarda/ vchaa
    "nxalp": ("scalar", (), "np.int64"),  # /callarda/ nxalp
    "iwarna": ("scalar", (), "np.int64"),  # /callarda/ iwarna

    # ===== synspec54.f:12452 /callardb/ =====
    "xlbet": ("array", ("1400", ), "np.float64"),  # /callardb/ xlbet(NXMAX)
    "plbet": ("array", ("1400", "5", ), "np.float64"),  # /callardb/ plbet(NXMAX,NNMAX)
    "stnneb": ("scalar", (), "np.float64"),  # /callardb/ stnneb
    "stnchb": ("scalar", (), "np.float64"),  # /callardb/ stnchb
    "vneub": ("scalar", (), "np.float64"),  # /callardb/ vneub
    "vchab": ("scalar", (), "np.float64"),  # /callardb/ vchab
    "nxbet": ("scalar", (), "np.int64"),  # /callardb/ nxbet
    "iwarnb": ("scalar", (), "np.int64"),  # /callardb/ iwarnb

    # ===== synspec54.f:12454 /callardg/ =====
    "xlgam": ("array", ("1400", ), "np.float64"),  # /callardg/ xlgam(NXMAX)
    "plgam": ("array", ("1400", "5", ), "np.float64"),  # /callardg/ plgam(NXMAX,NNMAX)
    "stnneg": ("scalar", (), "np.float64"),  # /callardg/ stnneg
    "stnchg": ("scalar", (), "np.float64"),  # /callardg/ stnchg
    "vneug": ("scalar", (), "np.float64"),  # /callardg/ vneug
    "vchag": ("scalar", (), "np.float64"),  # /callardg/ vchag
    "nxgam": ("scalar", (), "np.int64"),  # /callardg/ nxgam
    "iwarng": ("scalar", (), "np.int64"),  # /callardg/ iwarng

    # ===== synspec54.f:12456 /callardc/ =====
    "xlbal": ("array", ("1400", ), "np.float64"),  # /callardc/ xlbal(NXMAX)
    "plbal": ("array", ("1400", "5", ), "np.float64"),  # /callardc/ plbal(NXMAX,NNMAX)
    "stnnec": ("scalar", (), "np.float64"),  # /callardc/ stnnec
    "stnchc": ("scalar", (), "np.float64"),  # /callardc/ stnchc
    "vneuc": ("scalar", (), "np.float64"),  # /callardc/ vneuc
    "vchac": ("scalar", (), "np.float64"),  # /callardc/ vchac
    "nxbal": ("scalar", (), "np.int64"),  # /callardc/ nxbal
    "iwarnc": ("scalar", (), "np.int64"),  # /callardc/ iwarnc

    # ===== synspec54.f:12777 /calhhe/ =====
    # 局部 PARAMETER：nxmax=1000（:12774；与 callard* 的 NXMAX=1400 不同子程序）
    "xlhhe": ("array", ("1000", ), "np.float64"),  # /calhhe/ xlhhe(nxmax)
    "sighhe": ("array", ("1000", ), "np.float64"),  # /calhhe/ sighhe(nxmax)
    "nxhhe": ("scalar", (), "np.int64"),  # /calhhe/ nxhhe

    # ===== synspec54.f:12868 /VOITAB/ =====
    # 局部 PARAMETER：MVOI=2001（:12867）
    "H0TAB": ("array", ("2001", ), "np.float64"),  # /VOITAB/ H0TAB(MVOI)
    "H1TAB": ("array", ("2001", ), "np.float64"),  # /VOITAB/ H1TAB(MVOI)
    "H2TAB": ("array", ("2001", ), "np.float64"),  # /VOITAB/ H2TAB(MVOI)

    # ===== synspec54.f:12971 /CONSCA/ =====
    "SCC1": ("array", ("MDEPTH", ), "np.float64"),  # /CONSCA/ SCC1(mdepth)
    "SCC2": ("array", ("MDEPTH", ), "np.float64"),  # /CONSCA/ SCC2(MDEPTH)

    # ===== synspec54.f:17491 /fracop/ =====
    # 局部 PARAMETER：mtemp=100, melec=60, mion1=30（:17488）
    "frac": ("array", ("100", "60", "30", ), "np.float64"),  # /fracop/ frac(mtemp,melec,mion1)
    "fracm": ("array", ("100", "60", ), "np.float64"),  # /fracop/ fracm(mtemp,melec)
    "itemp": ("array", ("100", ), "np.int64"),  # /fracop/ itemp(mtemp)
    "ntt": ("scalar", (), "np.int64"),  # /fracop/ ntt

    # ===== synspec54.f:17973 /NXTINM/ =====
    "ALMM00": ("scalar", (), "np.float64"),  # /NXTINM/ ALMM00
    "ALSM00": ("scalar", (), "np.float64"),  # /NXTINM/ ALSM00

    # ===== synspec54.f:17974 /alendm/ =====
    "alend": ("array", ("MMLIST", ), "np.float64"),  # /alendm/ alend(mmlist)

    # ===== synspec54.f:18935 /COMFH1/ =====
    "C": ("array", ("600", "5", ), "np.float64"),  # /COMFH1/ C(600,5)
    "PPMOL": ("array", ("600", ), "np.float64"),  # /COMFH1/ PPMOL(600)
    "APMLOG": ("array", ("600", ), "np.float64"),  # /COMFH1/ APMLOG(600)
    "P": ("array", ("100", ), "np.float64"),  # /COMFH1/ P(100)
    "XIP": ("array", ("100", ), "np.float64"),  # /COMFH1/ XIP(100)
    "XI2": ("array", ("100", ), "np.float64"),  # /COMFH1/ XI2(100)
    "CCOMP": ("array", ("100", ), "np.float64"),  # /COMFH1/ CCOMP(100)
    "UIIDUI": ("array", ("100", ), "np.float64"),  # /COMFH1/ UIIDUI(100)
    "FP": ("array", ("100", ), "np.float64"),  # /COMFH1/ FP(100)
    "XKP": ("array", ("100", ), "np.float64"),  # /COMFH1/ XKP(100)
    "XK2": ("array", ("100", ), "np.float64"),  # /COMFH1/ XK2(100)
    "EPS": ("scalar", (), "np.float64"),  # /COMFH1/ EPS
    "SWITER": ("scalar", (), "np.float64"),  # /COMFH1/ SWITER
    "NELEM": ("array", ("5", "600", ), "np.int64"),  # /COMFH1/ NELEM(5,600)
    "NATO": ("array", ("5", "600", ), "np.int64"),  # /COMFH1/ NATO(5,600)
    "MMAX": ("array", ("600", ), "np.int64"),  # /COMFH1/ MMAX(600)
    "NELEMX": ("array", ("100", ), "np.int64"),  # /COMFH1/ NELEMX(100)
    "NMETAL": ("scalar", (), "np.int64"),  # /COMFH1/ NMETAL
    "NIMAX": ("scalar", (), "np.int64"),  # /COMFH1/ NIMAX

    # ===== synspec54.f:19860 /CONOPA/ =====
    "CHC": ("array", ("MFREQC", "MDEPTH", ), "np.float64"),  # /CONOPA/ CHC(MFREQC,MDEPTH)
    "ETC": ("array", ("MFREQC", "MDEPTH", ), "np.float64"),  # /CONOPA/ ETC(MFREQC,MDEPTH)
    "SCC": ("array", ("MFREQC", "MDEPTH", ), "np.float64"),  # /CONOPA/ SCC(MFREQC,MDEPTH)

    # ===== synspec54.f:19863 /COPAC/ =====
    "AB": ("array", ("MOPAC", "MDEPF", ), "np.float64"),  # /COPAC/ AB(MOPAC,MDEPF)
    "STH": ("array", ("MOPAC", "MDEPF", ), "np.float64"),  # /COPAC/ STH(MOPAC,MDEPF)
    "SCH": ("array", ("MFREQC", "MDEPF", ), "np.float64"),  # /COPAC/ SCH(MFREQC,MDEPF)

    # ===== synspec54.f:19866 /FRQSET/ =====
    "IFRS": ("scalar", (), "np.int64"),  # /FRQSET/ IFRS
    "NFRS": ("scalar", (), "np.int64"),  # /FRQSET/ NFRS

    # ===== synspec54.f:20060 /CONSCV/ =====
    "SCCF": ("array", ("MFREQC", "MDEPF", ), "np.float64"),  # /CONSCV/ SCCF(MFREQC,mdepf)

    # ===== synspec54.f:21617 /GOMOPA/ =====
    "frgtab": ("array", ("MFHTAB", ), "np.float64"),  # /GOMOPA/ frgtab(mfhtab)
    "wlgtab": ("array", ("MFHTAB", ), "np.float64"),  # /GOMOPA/ wlgtab(mfhtab)
    "hydopg": ("array", ("MFHTAB", "MDEPTH", ), "np.float64"),  # /GOMOPA/ hydopg(mfhtab,mdepth)
    "nugfreq": ("scalar", (), "np.int64"),  # /GOMOPA/ nugfreq

    # ===== synspec54.f:21778 /gridp0/ =====
    "tempg": ("array", ("MTTAB", ), "np.float64"),  # /gridp0/ tempg(mttab)
    "densg": ("array", ("MTTAB", "MRTAB", ), "np.float64"),  # /gridp0/ densg(mttab,mrtab)
    "elecgr": ("array", ("MTTAB", "MRTAB", ), "np.float64"),  # /gridp0/ elecgr(mttab,mrtab)
    "densg0": ("array", ("MTTAB", ), "np.float64"),  # /gridp0/ densg0(mttab)
    "temp1": ("scalar", (), "np.float64"),  # /gridp0/ temp1
    "ntemp": ("scalar", (), "np.int64"),  # /gridp0/ ntemp
    "ndens": ("scalar", (), "np.int64"),  # /gridp0/ ndens
    "nden": ("array", ("MTTAB", ), "np.int64"),  # /gridp0/ nden(mttab)

    # ===== synspec54.f:21780 /gridf0/ =====
    "wlgrid": ("array", ("MFGRID", ), "np.float64"),  # /gridf0/ wlgrid(mfgrid)
    "nfgrid": ("scalar", (), "np.int64"),  # /gridf0/ nfgrid

    # ===== synspec54.f:21781 /fintab/ =====
    "absgrd": ("array", ("MTTAB", "MRTAB", "MFGRID", ), "np.float32"),  # /fintab/ real*4 absgrd(mttab,mrtab,mfgrid)

    # ===== synspec54.f:21782 /prfrgr/ =====
    "ipfreq": ("scalar", (), "np.int64"),  # /prfrgr/ ipfreq
    "indext": ("scalar", (), "np.int64"),  # /prfrgr/ indext
    "indexn": ("scalar", (), "np.int64"),  # /prfrgr/ indexn

    # ===== synspec54.f:21784 /initab/ =====
    "absop": ("array", ("MSFTAB", ), "np.float64"),  # /initab/ absop(msftab)
    "wltab": ("array", ("MSFTAB", ), "np.float64"),  # /initab/ wltab(msftab)
    "nfrtab": ("array", ("MTTAB", "MRTAB", ), "np.int64"),  # /initab/ nfrtab(mttab,mrtab)
    "inttab": ("scalar", (), "np.int64"),  # /initab/ inttab

    # ===== synspec54.f:21786 /elecm0/ =====
    "elecm": ("array", ("MDEPTH", ), "np.float64"),  # /elecm0/ elecm(mdepth)

    # ===== synspec54.f:21787 /timeta/ =====
    "dtim": ("scalar", (), "np.float64"),  # /timeta/ dtim

    # ===== synspec54.f:21788 /relabu/ =====
    "relabn": ("array", ("MATOM", ), "np.float64"),  # /relabu/ relabn(matom)
    # popul0(mlevel,1) 与无名 COMMON 的 POPUL0 同名，见上方 POPUL0 条目注释

    # ===== synspec54.f:21791 /tabout/ =====
    "tabname": ("scalar", (), "object"),  # /tabout/ character*(80) tabname（声明见 :21790）
    "ibingr": ("scalar", (), "np.int64"),  # /tabout/ ibingr
    "idens": ("scalar", (), "np.int64"),  # /tabout/ idens

    # ===== synspec54.f:22411 /hydmol/ =====
    "anhmi": ("scalar", (), "np.float64"),  # /hydmol/ anhmi
    "ahmol": ("scalar", (), "np.float64"),  # /hydmol/ ahmol

    # ===== synspec54.f:22519 /nerela/ =====
    "anerel": ("scalar", (), "np.float64"),  # /nerela/ anerel

    # ===== synspec54.f:22576 /hydato/ =====
    "ah": ("scalar", (), "np.float64"),  # /hydato/ ah
    "anh": ("scalar", (), "np.float64"),  # /hydato/ anh
    "anp": ("scalar", (), "np.float64"),  # /hydato/ anp
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
    """求值维度表达式（标识符取自 params.py）。"""
    return int(eval(expr, {"__builtins__": {}}, dict(vars(P))))


def _allocate(name):
    """按 DECLS 声明分配变量：数组每维 +1，标量返回默认值。"""
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
    """PEP 562：首次访问 COMMON 变量时懒分配并缓存到模块全局。"""
    if name not in DECLS:
        raise AttributeError("commons 中未声明的 COMMON 变量: %r" % name)
    value = _allocate(name)
    globals()[name] = value
    return value


def __dir__():
    return sorted(set(globals()) | set(DECLS))
