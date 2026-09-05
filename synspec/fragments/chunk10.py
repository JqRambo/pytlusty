# -*- coding: utf-8 -*-
# chunk10: synspec54.f 行 11048–12332 的逐行直译
# 覆盖子程序: INKUR, INPMOD, INPBF, LEVSOL, CHANGE, RATMAT, SABOLF,
#             SBFHMI_old, OPADD, WN, WNSTOR, (TIMING 注释块), QUIT, VOIGTE, SIGAVS


def inkur():
    """C     ================
    C
    C     Input of a Kurucz model atmosphere
    C
    C     Input values (extracted from the Kurucz files):
    C      TEF, G  - effective temperature, log g (appears only in output)
    C      ND      - number of depth points
    C     and for each depth:
    C      DM      - m, m is the mass depth coordinate
    C      T       - temperature
    C      P       - gass pressure
    C      ANE     - electron density
    C
    对应 synspec54.f 行 11048–11112
    """
    # DIMENSION POP(MLEVEL),ES(MLEVEL,MLEVEL),BS(MLEVEL),POPLTE(MLEVEL)
    # COMMON POP,ES,BS   → C.POP, C.ES, C.BS（POP 本例程未用到）
    poplte = np.zeros(MLEVEL + 1)          # POPLTE 为纯局部数组
    # READ(8,501) TEF,GRAV
    #  501 FORMAT(4X,F8.0,9X,F8.5)
    _line = read_line(8)
    tef = float(_line[4:12])               # 4X,F8.0（TEF 仅用于输出，局部量）
    C.GRAV = float(_line[21:29])           # 9X,F8.5
    # READ(8,502) ND
    #  502 FORMAT(/////////////////////10X,I3/)
    for _i in range(21):                   # 21 个 '/' ：跳过 21 条记录
        read_line(8)
    _line = read_line(8)
    C.ND = int(_line[10:13])               # 10X,I3
    read_line(8)                           # 格式末尾的 '/' ：再多跳过一条记录
    C.ND = C.ND - 1                        # ND=ND-1
    # WRITE(6,600) TEF,GRAV
    #  600 FORMAT(' INPUT KURUCZ MODEL FOR TEFF=',F7.0,'   LOG G =',
    #     *       F7.2//1H ,7X,'MASS',9X,'T',9X,'NE',9X,'DENS'/
    #     *       '-----------------------------------------------'/)
    print(f" INPUT KURUCZ MODEL FOR TEFF={tef:7.0f}   LOG G ={C.GRAV:7.2f}")
    print()
    print("        MASS         T        NE       DENS")
    print("-----------------------------------------------")
    print()
    for id in range(1, C.ND + 1):                       # DO 10 ID=1,ND
        # READ(8,*) DM(ID),TEMP(ID),P,ELEC(ID)（自由格式）
        _t = read_line(8).replace(',', ' ').split()
        C.DM[id] = float(_t[0])
        C.TEMP[id] = float(_t[1])
        p = float(_t[2])
        C.ELEC[id] = float(_t[3])
        an = p / C.TEMP[id] / BOLK                       # AN=P/TEMP(ID)/BOLK
        C.DENS[id] = C.WMM[id] * (an - C.ELEC[id])
        # WRITE(6,601) ID,DM(ID),TEMP(ID),ELEC(ID),DENS(ID)
        #  601 FORMAT(1H ,I5,1PE10.3,0PF10.1,1P2E12.3)
        print(f" {id:5d}{C.DM[id]:10.3e}{C.TEMP[id]:10.1f}"
              f"{C.ELEC[id]:12.3e}{C.DENS[id]:12.3e}")
        t = C.TEMP[id]
        if C.IFMOL > 0 and t < C.TMOLIM:
            # AN=TOTN(ID)（原注释行）
            aein = C.ELEC[id]
            # CALL MOLEQ(ID,T,AN,AEIN,ANE,1)；MOLEQ 给标量哑元 ANE 赋值，
            # 按约定返回全部标量哑元；字面量 1 用临时变量 _ipri 接收
            id, t, an, aein, ane, _ipri = moleq(id, t, an, aein, ane, 1)
        else:
            for iat in range(1, C.NATOM + 1):            # DO IAT=1,NATOM
                C.ATTOT[iat, id] = (C.DENS[id] / C.WMM[id] / C.YTOT[id]
                                    * C.ABUND[iat, id])
        # WRITE(6,601) ...（原注释行，略）
        wnstor(id)                                       # CALL WNSTOR(ID)
        sabolf(id)                                       # CALL SABOLF(ID)
        ratmat(id, C.ES, C.BS)                           # CALL RATMAT(ID,ES,BS)
        levsol(C.ES, C.BS, poplte, C.NLEVEL)             # CALL LEVSOL(ES,BS,POPLTE,NLEVEL)
        for j in range(1, C.NLEVEL + 1):                 # DO J=1,NLEVEL
            C.POPUL[j, id] = poplte[j]
    # 10 CONTINUE
    # WRITE(77,503) ND, 3 / WRITE(77,504) (DM(ID),ID=1,ND)（原注释行，略）
    for id in range(1, C.ND + 1):                        # DO ID=1,ND
        # WRITE(77,504) TEMP(ID),ELEC(ID),DENS(ID)
        #  504 FORMAT(1P6E13.6)
        write_line(77, f"{C.TEMP[id]:13.6e}{C.ELEC[id]:13.6e}{C.DENS[id]:13.6e}")
    close_unit(8)                                        # CLOSE(8)
    return


def inpmod():
    """C     =================
    C
    C     Read an initial model atmosphere from unit 8
    C     File 8 contains:
    C      1. NDPTH -  number of depth points in which the initial model is
    C                  given (if not equal to ND, routine interpolates
    C                  automatically to the set DM by linear interpolation
    C                  in log(DM)
    C         NUMPAR - number of input model parameters in each depth
    C                  = 3 for LTE model - ie. N, T, N(electron);
    C                  > 3 for NLTE model)
    C      2. DEPTH(ID),ID=1,NDPTH - mass-depth points for the input model
    C      3. for each depth:
    C                 T   - temperature
    C                 ANE - electron density
    C                 RHO - mass density
    C                 level populations - only for NLTE input model
    C                       Number of input level populations need not be
    C                       equal to NLEVEL; in that case the procedure
    C                       CHANGE is called from START to calculate the
    C                       remaining level populations
    C
    C     Note: The output file 7, which is created by this program
    C           (procedure OUTPUT) has the same structure as file 8
    C           and may thus be used as input to another run of the
    C           program
    C     INTRPL - switch indicating whether (and, if so, how) interpolate
    C              the initial model if the depth scales for the input model
    C              and the present depth scale are different
    C            = 0  -  no interpolation, i.e. scale DEPTH coincides with DM
    C            > 0  -  polynomial interpolation of the (INTRPL-1)th order
    C
    对应 synspec54.f 行 11118–11277
    """
    # PARAMETER (MINPUT=MLEVEL+4)
    # 无名 COMMON 的 ESEMAT,BESE,POPLTE,POPUL0,X,TEMP0,ELEC0,DENS0,PPL0,
    # PPL,DEPTH,DM0,DP 以及 /NLTPOP/PNLT、/quasex/iexpl,iltot → C.* 访问
    totn = np.zeros(MDEPTH + 1)                          # TOTN(MDEPTH) 局部
    plte = np.zeros((MLEVEL + 1, MDEPTH + 1))            # PLTE(MLEVEL,MDEPTH) 局部
    numlt = 3
    if C.INMOD == 2:
        numlt = 4
    # READ(8,*) NDPTH,NUMPAR
    _t = read_line(8).replace(',', ' ').split()
    ndpth = int(_t[0])
    numpar = int(_t[1])
    # READ(8,*) (DEPTH(I),I=1,NDPTH)（自由格式，可能跨多条记录）
    _vals = []
    while len(_vals) < ndpth:
        _vals += read_line(8).replace(',', ' ').split()
    for i in range(1, ndpth + 1):
        C.DEPTH[i] = float(_vals[i - 1])
    C.ND = ndpth                                         # ND=NDPTH
    nump = abs(numpar)                                   # NUMP=ABS(NUMPAR)
    for id in range(1, ndpth + 1):                       # DO 30 ID=1,NDPTH
        # READ(8,*) (X(I),I=1,NUMP)
        _vals = []
        while len(_vals) < nump:
            _vals += read_line(8).replace(',', ' ').split()
        for i in range(1, nump + 1):
            C.X[i] = float(_vals[i - 1])
        C.TEMP[id] = C.X[1]
        C.ELEC[id] = C.X[2]
        C.DENS[id] = C.X[3]
        totn[id] = C.DENS[id] / C.WMM[id] + C.ELEC[id]
        wnstor(id)                                       # CALL WNSTOR(ID)
        sabolf(id)                                       # CALL SABOLF(ID)
        ip = numlt                                       # IP=NUMLT
        if numpar < 0:
            ip = ip + 1
            totn[id] = C.X[ip]
        if C.INMOD == 2:
            ip = ip + 1
        # first compute LTE level populations for all levels,
        # i.e. explicit, semi-explisit, and quasi-explicit
        nlev0 = C.NLEVEL                                 # NLEV0=NLEVEL
        C.TEMP[id] = C.X[1]
        C.ELEC[id] = C.X[2]
        C.DENS[id] = C.X[3]
        t = C.TEMP[id]
        if C.IFMOL > 0 and t < C.TMOLIM:
            ipri = 1
            aein = C.ELEC[id]
            an = totn[id]
            # CALL MOLEQ(ID,T,AN,AEIN,ANE,IPRI)；MOLEQ 给 ANE 赋值，
            # 按约定返回全部标量哑元
            id, t, an, aein, ane, ipri = moleq(id, t, an, aein, ane, ipri)
        else:
            if C.IMODE > -2:
                for iat in range(1, C.NATOM + 1):
                    C.ATTOT[iat, id] = (C.DENS[id] / C.WMM[id] / C.YTOT[id]
                                        * C.ABUND[iat, id])
            else:
                for iat in range(1, C.NATOM + 1):
                    C.ATTOT[iat, id] = (C.DENS[id] / C.WMM[1] / C.YTOT[1]
                                        * C.ABUND[iat, 1])
        wnstor(id)                                       # CALL WNSTOR(ID)
        sabolf(id)                                       # CALL SABOLF(ID)
        ratmat(id, C.ESEMAT, C.BESE)                     # CALL RATMAT(ID,ESEMAT,BESE)
        levsol(C.ESEMAT, C.BESE, C.POPLTE, nlev0)        # CALL LEVSOL(ESEMAT,BESE,POPLTE,NLEV0)
        for i in range(1, nlev0 + 1):                    # DO I=1,NLEV0
            C.POPUL[i, id] = C.POPLTE[i]
            plte[i, id] = C.POPLTE[i]
            # if(id.eq.1) write(6,651) ...（原注释行，略）
        # if the input file fort.8 contains also NLTE level populations
        # of b-factors, replace the LTE populations by those
        if nump > ip:
            nlev0 = nump - ip
            for i in range(1, nlev0 + 1):
                j = C.iltot[i]
                C.POPUL[j, id] = C.X[ip + i] * C.RELAB[C.IATM[i], id]
                # if(id.eq.1) write(6,651) ...（原注释行，略）
                #  651 format('in',2i4,1p2e12.4)
            # （原注释掉的负占据数修补循环，略）
            # in the case the input "NLTE populations are in fact b-factors,
            # compute the real populations
            if C.IBFAC == 1:
                for i in range(1, nlev0 + 1):
                    j = C.iltot[i]
                    C.POPUL[j, id] = C.POPUL[j, id] * plte[j, id]
    # 30 CONTINUE
    close_unit(8)                                        # close(8)
    # write(6,600)
    #  600 format(/' INPUT TLUSTY MODEL'/' ------------------'/
    #     *         1H ,8X,'MASS',9X,'T',9X,'NE',9X,'DENS'//)
    print()
    print(" INPUT TLUSTY MODEL")
    print(" ------------------")
    print("         MASS         T        NE       DENS")
    print()
    print()
    C.ND = ndpth                                         # nd=ndpth
    for id in range(1, C.ND + 1):                        # DO 40 ID=1,ND
        C.DM[id] = C.DEPTH[id]
        # write(6,601) id,dm(id),temp(id),elec(id),dens(id),popul(1,id)
        #  601 format(i6,1pe10.3,0pf10.1,1p4e12.3)
        print(f"{id:6d}{C.DM[id]:10.3e}{C.TEMP[id]:10.1f}{C.ELEC[id]:12.3e}"
              f"{C.DENS[id]:12.3e}{C.POPUL[1, id]:12.3e}")
    # 40 CONTINUE
    for id in range(1, C.ND + 1):                        # DO 100 ID=1,ND
        bcon = C.ELEC[id] / C.TEMP[id] / math.sqrt(C.TEMP[id]) * 2.0706e-16
        for ione in range(1, C.NION + 1):                # DO 100 IONE=1,NION
            ion = C.IZ[ione]
            iat = C.NUMAT[C.IATM[C.NFIRST[ione]]]
            nki = C.NNEXT[ione]
            if ion > 0:
                C.PNLT[iat, ion, id] = C.POPUL[nki, id] / C.G[nki] * bcon
    # 100 CONTINUE
    # check abundances
    # CALL CHCKAB（原注释行，略）
    return


def inpbf():
    """C     ================
    C
    对应 synspec54.f 行 11284–11318
    """
    # PARAMETER (MINPUT=MLEVEL+4)
    # DIMENSION DEPTH(MDEPTH),X(MINPUT,MDEPTH),XX(MDEPTH),BF(MDEPTH)
    # 注意：此处的 DEPTH/X 是本例程纯局部数组（不在 COMMON 中）
    minput = MLEVEL + 4
    depth = np.zeros(MDEPTH + 1)
    x = np.zeros((minput + 1, MDEPTH + 1))
    xx = np.zeros(MDEPTH + 1)
    bf = np.zeros(MDEPTH + 1)
    open_unit(8, 'bfactors', 'r')          # OPEN(8,FILE='bfactors',STATUS='OLD')
    numlt = 3
    if C.INMOD == 2:
        numlt = 4
    # READ(8,*) NDPTH,NUMPAR
    _t = read_line(8).replace(',', ' ').split()
    ndpth = int(_t[0])
    numpar = int(_t[1])
    # READ(8,*) (DEPTH(I),I=1,NDPTH)（自由格式，可能跨多条记录）
    _vals = []
    while len(_vals) < ndpth:
        _vals += read_line(8).replace(',', ' ').split()
    for i in range(1, ndpth + 1):
        depth[i] = float(_vals[i - 1])
    if numpar < 0:
        numlt = numlt + 1
    nump = abs(numpar)
    for id in range(1, ndpth + 1):                       # DO ID=1,NDPTH
        # READ(8,*) (X(I,ID),I=1,NUMP)
        _vals = []
        while len(_vals) < nump:
            _vals += read_line(8).replace(',', ' ').split()
        for i in range(1, nump + 1):
            x[i, id] = float(_vals[i - 1])
    close_unit(8)                                        # CLOSE(8)
    # interpolate the input b-factors to the original DM-scale;
    # compute new NLTE populations
    for i in range(numlt + 1, nump + 1):                 # DO I=NUMLT+1,NUMP
        for id in range(1, ndpth + 1):
            xx[id] = x[i, id]
        # CALL INTERP(DEPTH,XX,DM,BF,NDPTH,ND,2,1,1)
        # INTERP 只修改数组哑元（含 ILOGX=1 时对 DEPTH/DM 就地取 LOG10）
        interp(depth, xx, C.DM, bf, ndpth, C.ND, 2, 1, 1)
        for id in range(1, C.ND + 1):
            C.POPUL[i - numlt, id] = C.POPUL[i - numlt, id] * bf[id]
    return


def levsol(a, b, popp, nlvcal):
    """C     ==================================
    C
    C     new populations by inverting several partial rate matrices for the
    C     individual chemical species
    C
    对应 synspec54.f 行 11326–11362
    """
    # DIMENSION A(MLEVEL,MLEVEL),B(MLEVEL),POPP(MLEVEL),
    #    AP(MLEVEL,MLEVEL),BP(MLEVEL),POPP1(MLEVEL)
    ap = np.zeros((MLEVEL + 1, MLEVEL + 1))
    bp = np.zeros(MLEVEL + 1)
    popp1 = np.zeros(MLEVEL + 1)
    if nlvcal <= 0:
        return
    for iat in range(1, C.NATOM + 1):                    # DO 50 IAT=1,NATOM
        n1 = C.N0A[iat]
        nk = C.NKA[iat]
        if n1 <= 0:
            for i in range(C.N0A[iat], C.NKA[iat] + 1):  # DO 1 I=N0A(IAT),NKA(IAT)
                n1 = i
                if i > 0:
                    break                                # IF(I.GT.0) GO TO 2
            # 1 CONTINUE / 2 CONTINUE
        if n1 <= 0:
            continue                                     # IF(N1.LE.0) GO TO 50
        nlp = nk - n1 + 1
        for i in range(n1, nk + 1):                      # DO 20 I=N1,NK
            for j in range(n1, nk + 1):                  # DO 10 J=N1,NK
                ap[i - n1 + 1, j - n1 + 1] = a[i, j]
            bp[i - n1 + 1] = b[i]
        # CALL LINEQS(AP,BP,POPP1,NLP,MLEVEL)；LINEQS 只修改数组哑元
        lineqs(ap, bp, popp1, nlp, MLEVEL)
        for i in range(n1, nk + 1):                      # DO 30 I=N1,NK
            popp[i] = popp1[i - n1 + 1]
    # 50 CONTINUE
    return


def change():
    """C     =================
    C
    C     This procedure controls an evaluation of initial level
    C     populations in case where the system of explicit levels
    C     (ie. the choice of explicit level, their numbering, or their
    C     total number) is not consistent with that for the input level
    C     populations read by procedure INPMOD.
    C     Obviously, this procedure need be used only for NLTE input models.
    C
    C     Input from unit 5:
    C     For each explicit level, II=1,NLEVEL, the following parameters:
    C      IOLD   -  NE.0 - means that population of this level is
    C                       contained in the set of input populations;
    C                       IOLD is then its index in the "old" (i.e. input)
    C                       numbering.
    C                       All the subsequent parameters have no meaning
    C                       in this case.
    C             -  EQ.0 - means that this level has no equivalent in the
    C                       set of "old" levels. Population of this level
    C                       has thus to be evaluated.
    C      MODE   -    indicates how the population is evaluated:
    C             = 0  - population is equal to the population of the "old"
    C                    level with index ISIOLD, multiplied by REL;
    C             = 1  - population assumed to be LTE, with respect to the
    C                    first state of the next ionization degree whose
    C                    population must be contained in the set of "old"
    C                    (ie. input) populations, with index NXTOLD in the
    C                    "old" numbering.
    C                    The population determined of this way may further
    C                    be multiplied by REL.
    C             = 2  - population determined assuming that the b-factor
    C                    (defined as the ratio between the NLTE and
    C                    LTE population) is the same as the b-factor of
    C                    the level ISINEW (in the present numbering). The
    C                    level ISINEW must have the equivalent in the "old"
    C                    set; its index in the "old" set is ISIOLD, and the
    C                    index of the first state of the next ionization
    C                    degree, in the "old" numbering, is NXTSIO.
    C                    The population determined of this way may further
    C                    be multiplied by REL.
    C             = 3  - level corresponds to an ion or atom which was not
    C                    explicit in the old system; population is assumed
    C                    to be LTE.
    C      NXTOLD  -  see above
    C      ISINEW  -  see above
    C      ISIOLD  -  see above
    C      NXTSIO  -  see above
    C      REL     -  population multiplier - see above
    C                 if REL=0, the program sets up REL=1
    C
    对应 synspec54.f 行 11369–11468
    """
    # 无名 COMMON 的 ESEMAT,BESE,POPLTE,POPUL0,POPULL,POPL → C.* 访问
    s = 2.0706e-16                                       # PARAMETER (S = 2.0706E-16)
    ifese = 0
    for ii in range(1, C.NLEVEL + 1):                    # DO 100 II=1,NLEVEL
        # READ(ICHANG,*) IOLD,MODE,NXTOLD,ISINEW,ISIOLD,NXTSIO,REL
        _t = read_line(C.ICHANG).replace(',', ' ').split()
        iold = int(_t[0])
        mode = int(_t[1])
        nxtold = int(_t[2])
        isinew = int(_t[3])
        isiold = int(_t[4])
        nxtsio = int(_t[5])
        rel = float(_t[6])
        if mode >= 3:
            ifese = ifese + 1
        if rel == 0.0:
            rel = 1.0
        for id in range(1, C.ND + 1):                    # DO 90 ID=1,ND
            if iold != 0:                                # IF(IOLD.EQ.0) GO TO 10
                C.POPUL0[ii, id] = C.POPUL[iold, id]
                continue                                 # GO TO 90
            # 标号 10
            if mode == 0:                                # IF(MODE.NE.0) GO TO 20
                C.POPUL0[ii, id] = C.POPUL[isiold, id] * rel
                continue                                 # GO TO 90
            # 标号 20
            t = C.TEMP[id]
            ane = C.ELEC[id]
            if mode >= 3:                                # IF(MODE.GE.3) GO TO 40
                # 标号 40
                if ifese == 1:
                    sabolf(id)                           # CALL SABOLF(ID)
                    ratmat(id, C.ESEMAT, C.BESE)         # CALL RATMAT(ID,ESEMAT,BESE)
                    # CALL LINEQS(ESEMAT,BESE,POPLTE,NLEVEL,MLEVEL)
                    lineqs(C.ESEMAT, C.BESE, C.POPLTE, C.NLEVEL, MLEVEL)
                    for iii in range(1, C.NLEVEL + 1):   # DO 50 III=1,NLEVEL
                        C.POPULL[iii, id] = C.POPLTE[iii]
                C.POPUL0[ii, id] = C.POPULL[ii, id]
                continue                                 # （落到 90 CONTINUE）
            nxtnew = C.NNEXT[C.IEL[ii]]
            sb = (s / t / math.sqrt(t) * C.G[ii] / C.G[nxtnew]
                  * math.exp(C.ENION[ii] / t / BOLK))
            if mode <= 1:                                # IF(MODE.GT.1) GO TO 30
                C.POPUL0[ii, id] = sb * ane * C.POPUL[nxtold, id] * rel
                continue                                 # GO TO 90
            # 标号 30
            kk = isinew
            knext = C.NNEXT[C.IEL[kk]]
            sbk = (s / t / math.sqrt(t) * C.G[kk] / C.G[knext]
                   * math.exp(C.ENION[kk] / t / BOLK))
            C.POPUL0[ii, id] = (sb / sbk * C.POPUL[nxtold, id]
                                / C.POPUL[nxtsio, id] * C.POPUL[isiold, id] * rel)
            # GO TO 90（continue 隐含）
        # 90 CONTINUE
    # 100 CONTINUE
    for i in range(1, C.NLEVEL + 1):                     # DO 110 I=1,NLEVEL
        for id in range(1, C.ND + 1):                    # DO 110 ID=1,ND
            C.POPUL[i, id] = C.POPUL0[i, id]
    # 110 CONTINUE
    return


def ratmat(id, a, b):
    """C
    C     LTE RATE MATRIX  (SAHA-BOLTZMANN EQS. + CHARGE CONSERVATION EQ.)
    C
    对应 synspec54.f 行 11474–11510
    """
    un = 1.0                                             # parameter (un=1.)
    ane = C.ELEC[id]
    for i in range(1, C.NLEVEL + 1):                     # DO I=1,NLEVEL
        b[i] = 0.0
        for j in range(1, C.NLEVEL + 1):
            a[j, i] = 0.0
    for iat in range(1, C.NATOM + 1):                    # DO IAT=1,NATOM
        n0i = C.N0A[iat]
        nki = C.NKA[iat]
        n1i = nki - 1
        nrefi = nki
        for i in range(n0i, n1i + 1):                    # DO I=N0I,N1I
            a[i, i] = 1.0
            n = C.NNEXT[C.IEL[i]]
            a[i, n] = -ane * C.SBF[i] * C.WOP[i, id]
        for i in range(n0i, nki + 1):                    # DO I=N0I,NKI
            il = C.ILK[i]
            a[nrefi, i] = un
            if il != 0:
                a[nrefi, i] = 1.0 + ane * C.USUM[il]
        b[nrefi] = C.ATTOT[iat, id]
    return


def sabolf(id):
    """C     =====================
    C
    C     Saha-Boltzmann factors (SBF)
    C     and "upper sums" - sum of Saha-Boltzmann factors for upper, LTE,
    C     levels which are not included explicitly (USUM), and derivatives
    C     wrt. temperature (T) and electron density (DUSUMN)
    C
    C     Input: ID  - depth index
    C
    对应 synspec54.f 行 11514–11628
    """
    uh = 1.5                                             # PARAMETER (UH=1.5)（原代码未使用）
    cmax = 2.154e4                                       # PARAMETER (CMAX=2.154D4,...)
    ccon = 2.0706e-16
    two = 2.0
    # DCHI - approximate lowering of ionization potential for neutrals
    #  Actual lowering is DCHI*effective charge, and is considered only
    #  if IUPSUM(ION).GT.0
    t = C.TEMP[id]
    sqt = math.sqrt(t)
    ane = C.ELEC[id]
    stane = math.sqrt(t / ane)
    xmax = cmax * math.sqrt(stane)
    tk = BOLK * t
    con = ccon / t / sqt
    # Saha-Boltzmann factors
    for ion in range(1, C.NION + 1):                     # DO 50 ION=1,NION
        qz = C.IZ[ion]
        cfn = con / C.G[C.NNEXT[ion]]
        dch = 0.0                                        # DCH=0.（原代码未再使用）
        iups = C.IUPSUM[ion]
        ssbf = 0.0
        C.USUM[ion] = 0.0
        nlst = C.NLAST[ion]
        if C.ifwop[nlst] >= 0:
            nl1up = C.NQUANT[nlst] + 1
        else:
            nl1up = C.NQUANT[nlst]
        for ii in range(C.NFIRST[ion], C.NLAST[ion] + 1):  # DO 10 II=NFIRST(ION),NLAST(ION)
            if C.ifwop[ii] < 0:
                e = EH * qz * qz / tk
                sum_l = 0.0                              # SUM（避免遮蔽内建 sum）
                for j in range(nl1up, NLMX + 1):         # DO 5 J=nl1up,NLMX
                    xj = j                               # XJ=J（原代码未再使用）
                    xi = j * j
                    x = e / xi
                    fi = xi * math.exp(x) * C.WNHINT[j, id]
                    sum_l = sum_l + fi
                # 5 CONTINUE
                C.G[ii] = sum_l * two                    # g(ii)=sum*two
                C.GMER[C.IMRG[ii], id] = C.G[ii]         # gmer(imrg(ii),id)=g(ii)
            x = C.ENION[ii] / tk
            if x > 110.0:
                x = 110.0
            sb = cfn * C.G[ii] * math.exp(x)
            C.SBF[ii] = sb
            ssbf = ssbf + sb
        # 10 CONTINUE
        # Upper sums
        if C.ifwop[nlst] < 0:
            continue                                     # go to 50
        if iups == 0:
            # 1. More exact approach - using (exact) partition functions
            iat = C.NUMAT[C.IATM[C.NFIRST[ion]]]
            xmx = xmax * math.sqrt(qz)
            # CALL PARTF(IAT,IZ(ION),T,ANE,XMX,U)；PARTF 只给标量哑元 U 赋值，
            # 按约定返回全部标量哑元；C.IZ[ion] 实参用 _izi 临时接收
            u = 0.0
            iat, _izi, t, ane, xmx, u = partf(iat, C.IZ[ion], t, ane, xmx, u)
            ee = C.ENION[C.NFIRST[ion]] / tk
            if ee > 110.0:
                ee = 110.0
            cfe = cfn * math.exp(ee)
            C.USUM[ion] = cfe * u - ssbf
            xx = (ssbf - C.SBF[C.NFIRST[ion]]) / C.SBF[C.NFIRST[ion]]
            if C.USUM[ion] < 0.0 or ee >= 109.0 or xx < 1.0e-7:
                C.USUM[ion] = 0.0
            if C.USUM[ion] < 0.0:
                C.USUM[ion] = 0.0
        elif iups > 0:
            # 2. Approximate approach - summation over fixed number of upper
            #    levels, assumed hydrogenic (ie. their ionization energy and
            #    statistical weight hydrogenic)
            sum_l = 0.0
            dsum = 0.0                                   # DSUM=0.（原代码未再使用）
            e = EH * qz * qz / tk
            for j in range(C.NQUANT[C.NLAST[ion]] + 1, iups + 1):  # DO 30 J=...,IUPS
                xi = j * j
                x = e / xi
                fi = xi * math.exp(x)
                sum_l = sum_l + fi
            # 30 CONTINUE
            C.USUM[ion] = sum_l * con * two
        else:
            # 3. occupation probability form
            sum_l = 0.0
            dsum = 0.0
            e = EH * qz * qz / tk
            for j in range(C.NQUANT[C.NLAST[ion]] + 1, NLMX + 1):  # DO 40 J=...,NLMX
                xj = j
                xi = j * j
                x = e / xi
                fi = xi * math.exp(x) * C.WNHINT[j, id]
                sum_l = sum_l + fi
            # 40 CONTINUE
            C.USUM[ion] = sum_l * con * two
    # 50 CONTINUE
    return


def sbfhmi_old(fr):
    """C     ===================
    C
    C     Bound-free cross-section for H- (negative hydrogen ion)
    C
    对应 synspec54.f 行 11634–11655
    """
    sbfhmi = 0.0        # 原代码中对名字 SBFHMI 的赋值（此处为局部变量，死代码，直译保留）
    sbfhmi_old_val = 0.0
    fr0 = 1.8259e14
    if fr < fr0:
        return sbfhmi_old_val
    if fr < 2.111e14:
        # GO TO 10 分支
        x = 2.997925e15 * (1.0 / fr0 - 1.0 / fr)
        sbfhmi = ((2.69818e-1 + x * (2.2019e-1 + x * (-4.11288e-2 + x * 2.73236e-3)))
                  * x * 1.0e-17)
        sbfhmi_old_val = sbfhmi
        return sbfhmi_old_val
    x = 2.997925e15 / fr
    sbfhmi = ((6.80133e-3 + x * (1.78708e-1 + x * (1.6479e-1 + x * (-2.04842e-2 + x *
              5.95244e-4)))) * 1.0e-17)
    sbfhmi_old_val = sbfhmi
    return sbfhmi_old_val


def opadd(mode, id, fr, abad, emad, scad):
    """C     ===========================================
    C
    C     Additional opacities
    C     This is basically user-supplied procedure; here are some more
    C     important non-standard opacity sources, namely
    C     Rayleigh scattering, H- opacity, H2+ opacity, and additional
    C     opacity of He I and He II.
    C     Inclusion of these opacities is contolled by switches transmitted
    C     by COMMON/OPCPAR - see description in START.
    C
    C     Input parameters:
    C     MODE  - controls the nature and the amount of calculations
    C           = -1 - (OPADD called from START) evaluation of relevant
    C                  depth-dependent quantities (usually photoionization
    C                  cross-sections, but also possibly other), which are
    C                  stored in array CROS
    C           = 0  - evaluation of an additional opacity, emissivity, and
    C                  scattering - for procedure OPAC0
    C     ID    - depth index
    C     FR    - frequency
    C
    C     Output:
    C
    C     ABAD  - absorption coefficient (at frequency FR and depth ID)
    C     EMAD  - emission coefficient (at frequency FR and depth ID)
    C     SCAD  - scattering coefficient (at frequency FR and depth ID)
    C
    对应 synspec54.f 行 11663–11872
    """
    frayh = 2.463e15                                     # PARAMETER (FRAYH = 2.463E15, ...)
    frayhe = 5.150e15
    frayh2 = 2.922e15
    cls = 2.997925e18
    ab0 = 0.0
    ab1 = 0.0
    abad = 0.0
    emad = 0.0
    scad = 0.0
    # TODO(port): 原代码中 MODE<0 或 IATH<=0 时 t/ane/anh/anhe/hkt 可能未赋值
    # （Fortran 依赖静态存储的残留值），此处预置 0.0 以避免 NameError
    t = 0.0
    ane = 0.0
    anh = 0.0
    anhe = 0.0
    hkt = 0.0
    t32 = 0.0
    oph2 = 0.0          # TODO(port): oph2 在调用 h2minus/cia_* 前未定义，预置 0.0
    if C.IATH > 0:
        n0hn = C.NFIRST[C.IELH]
        nkh = C.NKA[C.IATH]
        if mode >= 0:
            t = C.TEMP[id]
            ane = C.ELEC[id]
            hkt = HK / t
            t32 = 1.0 / t / math.sqrt(t)
        anh = C.DENS[id] / (C.WMM[id] * C.YTOT[id])
        anhe = C.RRR[id, 1, 2]
        it = C.NLEVEL                                    # IT=NLEVEL（原代码未再使用）
        #   -----------------------
        #   HI  Rayleigh scattering
        #   -----------------------
        if C.IRSCT != 0 and C.IOPHLI != 1 and C.IOPHLI != 2:
            x = 1.0 / (cls / min(fr, frayh)) ** 2
            sg = (5.799e-13 + (1.422e-6 + 2.784 * x) * x) * x * x
            # ABAD=POPUL(N0HN,ID)*SG（原注释行，略）
            scad = C.POPUL[n0hn, id] * sg
            scad = anh * sg
        if C.IOPHMI != 0:
            #   ----------------------------
            #   H-  bound-free and free-free
            #   ----------------------------
            #  Note: IOPHMI must not by taken non-zero if H- is considered
            #        explicitly, because H- opacity would be taken twice
            sg = sbfhmi(fr)
            xhm = 8762.9 / t
            sb = 1.0353e-16 * t32 * math.exp(xhm) * C.POPUL[n0hn, id] * ane * sg
            sf = sffhmi(C.POPUL[n0hn, id], fr, t) * ane
            ab0 = sb + sf
        #   -----------------------
        #   He I  Rayleigh scattering
        #   -----------------------
        if C.IRSCHE != 0 and mode >= 0:
            x = (cls / min(fr, frayhe)) ** 2
            cs = 5.484e-14 / x / x * (1.0 + (2.44e5 + 5.94e10 / (x - 2.90e5)) / x) ** 2
            sg = anhe * cs
            # abad=abad+sg（原注释行，略）
            scad = scad + sg
        #   -----------------------
        #   H2  Rayleigh scattering
        #   -----------------------
        if C.IRSCH2 != 0 and mode >= 0 and C.IFMOL > 0:
            x = (cls / min(fr, frayh2)) ** 2
            x2 = 1.0 / x / x
            cs = (8.14e-13 + 1.28e-6 / x + 1.61 * x2) * x2
            sg = cs * C.anh2[id]
            # abad=abad+sg（原注释行，略）
            scad = scad + sg
        if (C.IOPH2P > 0 and C.IFMOL > 0 and
                t < C.TMOLIM and fr < 3.28e15):
            #   -----------------------------
            #   H2+  bound-free and free-free
            #   -----------------------------
            x = fr * 1.0e-15
            sg1 = ((-7.342e-3 + (-2.409 + (1.028 + (-4.23e-1 +
                    (1.224e-1 - 1.351e-2 * x) * x) * x) * x) * x) * 1.602e-12 / BOLK)
            it = it + 1
            x = math.log(fr)
            sg2 = (-3.0233e3 + (3.7797e2 + (-1.82496e1 + (3.9207e-1 -
                   3.1672e-3 * x) * x) * x) * x)
            x2 = -sg1 / t + sg2
            sb = 0.0
            if x2 > -150.0:
                sb = C.POPUL[n0hn, id] * C.POPUL[nkh, id] * math.exp(x2)
            ab0 = ab0 + sb
    #   -----------------------------
    #   He-  free-free
    #   -----------------------------
    if mode >= 0 and C.IOPHEM > 0:
        a = 3.397e-46 + (-5.216e-31 + 7.039e-15 / fr) / fr
        b = -4.116e-42 + (1.067e-26 + 8.135e-11 / fr) / fr
        c = 5.081e-37 + (-8.724e-23 - 5.659e-8 / fr) / fr
        cs = a * t + b + c / t
        sg = anhe * ane * cs
        ab0 = ab0 + sg
    #   -----------------------------
    #   H2-  free-free
    #   -----------------------------
    if C.IOPH2M != 0 and mode >= 0 and C.IFMOL > 0 and t < C.TMOLIM:
        # call h2minus(t,anh2(id),ane,fr,oph2)；h2minus 只给标量哑元 oph2m 赋值，
        # 按约定返回全部标量哑元；数组元素实参用临时变量接收
        t, _anh2, ane, fr, oph2 = h2minus(t, C.anh2[id], ane, fr, oph2)
        ab1 = ab1 + oph2
    #   -----------------------------
    #     CH and OH continuuum opacity
    #   -----------------------------
    if mode >= 0 and C.IFMOL > 0 and t < C.TMOLIM:
        if C.IOPCH > 0:
            ab0 = ab0 + sbfch(fr, t) * C.anch[id]
        if C.IOPOH > 0:
            ab0 = ab0 + sbfoh(fr, t) * C.anoh[id]
        #     ---------------------------
        #     CIA H2-H2 opacity
        #     ---------------------------
        if C.IOH2H2 > 0:
            # call cia_h2h2(t,anh2(id),fr,oph2)；opac 为输出哑元
            t, _ah2, fr, oph2 = cia_h2h2(t, C.anh2[id], fr, oph2)
            ab1 = ab1 + oph2
        #     ---------------------------
        #     CIA H2-He opacity
        #     ---------------------------
        if C.IOH2HE > 0:
            # call cia_h2he(t,anh2(id),anhe,fr,oph2)
            t, _ah2, _ahe, fr, oph2 = cia_h2he(t, C.anh2[id], anhe, fr, oph2)
            ab1 = ab1 + oph2
        #     ---------------------------
        #     CIA H2-H opacity
        #     ---------------------------
        if C.IOH2H1 > 0:
            # call cia_h2h(t,anh2(id),anh,fr,oph2)
            t, _ah2, _ah, fr, oph2 = cia_h2h(t, C.anh2[id], anh, fr, oph2)
            ab1 = ab1 + oph2
        #     ---------------------------
        #     CIA H-He opacity
        #     ---------------------------
        if C.IOHHE > 0:
            # call cia_hhe(t,anh,anhe,fr,oph2)
            t, _ah, _ahe, fr, oph2 = cia_hhe(t, anh, anhe, fr, oph2)
            ab1 = ab1 + oph2
    #     ----------------------------------------------
    #     The user may supply more opacity sources here:
    #     ----------------------------------------------
    #     Finally, actual absorption and emission coefficients
    if mode < 0:
        return mode, id, fr, abad, emad, scad            # IF(MODE.LT.0) RETURN
    x = math.exp(-hkt * fr)
    x1 = 1.0 - x
    bnx = BN * (fr * 1.0e-15) ** 3 * x
    abad = abad + x1 * ab0 + ab1
    emad = emad + bnx * (ab0 + ab1 / x1)
    return mode, id, fr, abad, emad, scad


def wn(xn, a, id, z):
    """c     ======================
    c
    c     evaluation of the occupation probablities for a hydrogenic ion
    c     using eqs (4.26), and (4.39) of Hummer,Mihalas Ap.J. 331, 794, 1988.
    c     approximate evaluation of Q(beta) - Hummer
    c
    c     Input: xn  - real number corresponding to quantum number n
    c            a   - correlation parameter
    c            id  - depth index
    c            z   - ionic charge
    c
    对应 synspec54.f 行 11878–11930
    """
    p1 = 0.1402                                          # parameter (p1=0.1402,...)
    p2 = 0.1285
    p3 = 1.0
    p4 = 3.15
    p5 = 4.0
    un = 1.0
    tkn = 3.01                                           # parameter (tkn=3.01,...)
    ckn = 5.33333333
    cb = 8.59e14
    f23 = -2.0 / 3.0                                     # parameter (f23=-2./3.)
    a0 = 0.529177e-8                                     # parameter (a0=0.529177e-8,...)
    wa0 = -3.1415926538 / 6.0 * a0 * a0 * a0
    # evaluation of k(n)
    if xn <= tkn:
        xkn = un
    else:
        xkn = ckn * xn / (xn + un) / (xn + un)
    # evaluation of beta
    # beta=cb*bergfc*z*z*z*xkn/(xn*xn*xn*xn)*exp(f23*log(elec(id)))（原注释行）
    beta = cb * z * z * z * xkn / (xn * xn * xn * xn) * math.exp(f23 * math.log(C.ELEC[id]))
    # approximate expression for Q(beta)
    x = math.exp(p4 * math.log(un + p3 * a))
    # c1=p1*(x+p5*z*a*a*a)    ! previous expression -ERROR !!!!!!
    c1 = p1 * (x + p5 * (z - un) * a * a * a)
    c2 = p2 * x
    f = (c1 * beta * beta * beta) / (un + c2 * beta * math.sqrt(beta))
    wp = f / (un + f)
    # contribution from neutral particles
    xn2 = xn * xn + un
    xnh = 0.0
    xnhe1 = 0.0
    if C.IELH > 0:
        xnh = C.POPUL[C.NFIRST[C.IELH], id]
    if C.IELHE1 > 0:
        xnhe1 = C.POPUL[C.NFIRST[C.IELHE1], id]
    w0 = math.exp(wa0 * xn2 * xn2 * xn2 * (xnh + xnhe1))
    w0 = 1.0            # 原代码紧随其后 W0=1.（覆盖上一行，直译保留）
    wn_val = wp * w0
    return wn_val


def wnstor(id):
    """C     =====================
    C
    C     Stores occupation probabilities for hydrogen levels
    C     in common WNCOM for further use
    C
    对应 synspec54.f 行 11936–11974
    """
    un = 1.0                                             # PARAMETER (UN=1.,TWO=2.,...)
    two = 2.0
    sixth = 1.0 / 6.0
    ccor = 0.09
    p1 = 0.1402                                          # parameter (p1=0.1402,...)（原代码未使用）
    p2 = 0.1285
    p3 = 1.0
    p4 = 3.15
    p5 = 4.0
    tkn = 3.01                                           # parameter (tkn=3.01,...)（原代码未使用）
    ckn = 5.33333333
    cb = 8.59e14
    f23 = -2.0 / 3.0
    ane = C.ELEC[id]
    a = ccor * math.exp(sixth * math.log(ane)) / math.sqrt(C.TEMP[id])
    for i in range(1, NLMX + 1):                         # DO 20 I=1,NLMX
        xn = i
        C.WNHINT[i, id] = wn(xn, a, id, un)
        C.WNHE2[i, id] = wn(xn, a, id, two)
    # 20 CONTINUE
    # array WOP - occupation probabilities for explicit levels
    for ii in range(1, C.NLEVEL + 1):                    # do 30 ii=1,nlevel
        C.WOP[ii, id] = un
        if C.ifwop[ii] <= 0:
            continue                                     # go to 30
        ie = C.IEL[ii]
        nq = C.NQUANT[ii]
        if C.IZ[ie] == 1:
            C.WOP[ii, id] = C.WNHINT[nq, id]
        elif C.IZ[ie] == 2:
            C.WOP[ii, id] = C.WNHE2[nq, id]
        else:
            z = C.IZ[ie]
            xn = nq
            C.WOP[ii, id] = wn(xn, a, id, z)
    # 30 continue
    return


#  ----------------------------------------------------------------------------
#  原代码 11981–12007 行为整体注释掉的 SUBROUTINE TIMING(MOD,ITER)（计时例程，
#  调用机器相关例程 etime），无有效可执行语句，保留此说明注释。
#  ----------------------------------------------------------------------------


def quit(text):
    """c     =====================
    c
    c     stops the program and writes a text
    c
    对应 synspec54.f 行 12011–12021
    """
    # write(6,10) text
    #   10 format(1x,a)
    print(text)
    raise SystemExit                                     # stop


def voigte(a, vs):
    """c     =====================
    c
    c     computes a voigt function  h = h(a,v)
    c     a=gamma/(4*pi*dnud)   and  v=(nu-nu0)/dnud.  this  is  done after
    c     traving (landolt-b\\rnstein, p. 449).
    c
    对应 synspec54.f 行 12030–12119
    """
    # DATA ak /.../（DATA 初始化且之后不修改 → 函数顶部直接赋值，1 基索引）
    ak = [0.0,
          -1.12470432, -0.15516677, 3.28867591, -2.34357915,
          0.42139162, -4.48480194, 9.39456063, -6.61487486, 1.98919585,
          -0.22041650, 0.554153432, 0.278711796, -0.188325687, 0.042991293,
          -0.003278278, 0.979895023, -0.962846325, 0.532770573, -0.122727278]
    a1 = [0.0] * 6                                       # dimension a1(5)
    sqp = 1.772453851                                    # data sqp/1.772453851/
    sq2 = 1.414213562                                    # data sq2/1.414213562/
    v = abs(vs)
    u = a + v
    v2 = v * v
    if a == 0.0:
        # a eq 0.（标号 140）
        hh = 0.0
        if v2 < 100.0:
            hh = math.exp(-v2)
        return hh
    if a > 0.2:
        # 标号 120
        if a > 1.4 or u > 3.2:
            # a gt 1.4  or  a + v gt 3.2（标号 130）
            a2 = a * a
            u = sq2 * (a2 + v2)
            u2 = 1.0 / (u * u)
            hh = (sq2 / sqp * a / u * (1.0 + u2 * (3.0 * v2 - a2) +
                  u2 * u2 * (15.0 * v2 * v2 - 30.0 * v2 * a2 + 3.0 * a2 * a2)))
            return hh
        ex = 0.0
        if v2 < 100.0:
            ex = math.exp(-v2)
        k = 2                                            # GO TO 100（k=2 落入下方公共块）
    else:
        if v >= 5.0:
            # a le 0.2  and  v ge 5.（标号 121）
            hh = a * (15.0 + 6.0 * v2 + 4.0 * v2 * v2) / (4.0 * v2 * v2 * v2 * sqp)
            return hh
        ex = 0.0
        if v2 < 100.0:
            ex = math.exp(-v2)
        k = 1
    # 标号 100
    quo = 1.0
    if v < 2.4:
        # 标号 101
        m = 6
        if v < 1.3:
            m = 1
    else:
        quo = 1.0 / (v2 - 1.5)
        m = 11
    # 标号 102
    for i in range(1, 6):                                # do 103 i=1,5
        a1[i] = ak[m]
        m = m + 1
    h1 = quo * (a1[1] + v * (a1[2] + v * (a1[3] + v * (a1[4] + v * a1[5]))))
    if k <= 1:
        # a le 0.2  and v lt 5.（k=1 时跳过标号 110）
        hh = h1 * a + ex * (1.0 + a * a * (1.0 - 2.0 * v2))
        return hh
    # 标号 110
    pqs = 2.0 / sqp
    h1p = h1 + pqs * ex
    h2p = pqs * h1p - 2.0 * v2 * ex
    h3p = (pqs * (1.0 - ex * (1.0 - 2.0 * v2)) - 2.0 * v2 * h1p) / 3.0 + pqs * h2p
    h4p = (2.0 * v2 * v2 * ex - pqs * h1p) / 3.0 + pqs * h3p
    psi = ak[16] + a * (ak[17] + a * (ak[18] + a * ak[19]))
    # 0.2 lt a le 1.4  and  a + v le 3.2
    hh = psi * (ex + a * (h1p + a * (h2p + a * (h3p + a * h4p))))
    return hh


def sigavs():
    """C     =================
    C
    C     Read bound-free cross-sections for averaged levels
    C     from the unit INSA (given by IFANCY), with increasing frequencies
    C     It assumes that all continuum transitions for a given ion are
    C     given in a successive order in the data (i.e. as in TLUSTY for
    C     explicit levels. For other levels, additional input data in
    C     unit 54 !!
    C
    对应 synspec54.f 行 12125–12326
    """
    hccm = H * 2.997925e10                               # PARAMETER (HCCM=H*2.997925D10,...)
    bam = 1.0e-18
    crd = np.zeros(MFCRA + 1)                            # DIMENSION CRD(MFCRA)
    frd = np.zeros(MFCRA + 1)                            # DIMENSION FRD(MFCRA)
    # DATA XIFE/.../（DATA 初始化且之后不修改 → 直接赋值，1 基索引）
    xife = [0.0, 63480.0, 130563.0, 247220.0, 442000.0, 605000.0, 799000.0,
            1008000.0, 1218380.0]
    # COMMON/IONFIL/FIDATA,FIODF1,FIODF2,FIBFCS → C.*（本例程只用 FIBFCS）

    def _rd_err(unit, spec, errmsg):
        # READ(unit,*,END=...,ERR=...) 的直译：自由格式读一行并按
        # spec('i'=int,'f'=float) 解析；EOF 或解析错误 → 对应标号处的 quit
        try:
            _tok = read_line(unit).replace(',', ' ').split()
            return [int(v) if s == 'i' else float(v) for s, v in zip(spec, _tok)]
        except (EOFError, ValueError, IndexError):
            quit(errmsg)
            raise SystemExit                             # quit 已 STOP，明确语义

    fr1 = C.FREQ[1]
    fr2 = C.FREQ[2]
    nunit = 0
    nqht = 0
    if C.IASV != 0:                                      # IF(IASV.EQ.0) GOTO 100
        #     WRITE(6,600)（原注释行，略）
        #  600 FORMAT(///,' DETAILED PHOTOIONIZATION CROSS-SECTIONS',
        #     * ' (EXPLICIT LEVELS)',/,
        #     * ' ---------------------------------------',/)
        for i in range(1, C.NION + 1):                   # DO 10 I=1,NION
            n1 = C.NFIRST[i]
            n2 = C.NLAST[i]
            insa = 0
            for ii in range(n1, n2 + 1):                 # DO 11 II=N1,N2
                C.NFCR[ii] = 2
                C.FRECR[ii, 1] = fr1
                C.FRECR[ii, 2] = fr2
                C.CROSR[ii, 1] = 0.0
                C.CROSR[ii, 2] = 0.0
                insb = C.IBF[ii]
                if insb < 50 or insb > 100:
                    continue                             # GO TO 11
                if insa == 0:
                    insa = insb
                if insa != insb:
                    quit(' Incoherent file units in SIGAVS')
            # 11 CONTINUE
            if insa == 0:
                continue                                 # GOTO 10
            if not feq(C.FIBFCS[i], ' '):                # IF(FIBFCS(I).NE.' ')
                insa = C.INBFCS[i]
                # OPEN(INSA,FILE=FIBFCS(I),STATUS='OLD')
                open_unit(insa, C.FIBFCS[i].strip(), 'r')
            # READ(INSA,*,END=500,ERR=500) IIAT,IIZ,NSUP
            iiat, iiz, nsup = _rd_err(insa, 'iii',
                                      ' ERROR IN DATA FILE FOR BF SIG OF AVERAGED LEVELS (1)')
            ati = iiat + 0.01 * (iiz - 1)
            nbfi = nsup
            if nsup > (n2 - n1 + 1):
                nbfi = (n2 - n1 + 1)
            # call quit(' Too many bf-trans. in input file (SIGAVS)')（原注释行，略）
            # WRITE(6,601) ATI,INSA（原注释行，略）
            for ii in range(1, nbfi + 1):                # DO 12 II=1,NBFI
                # READ(INSA,*,END=500,ERR=500) IILO,EELO,GGLO,NFCRR
                iilo, eelo, gglo, nfcrr = _rd_err(
                    insa, 'iffi',
                    ' ERROR IN DATA FILE FOR BF SIG OF AVERAGED LEVELS (1)')
                ik = n1 + iilo - 1
                if ik > n2 or ik < n1:
                    quit(' Inconsistent level numbering in SIGAVS')
                if iiat == 26:                           # IF(IIAT.NE.26) GOTO 13
                    ecmr = xife[iiz] - eelo              # ECMR（原代码未再使用）
                    # DE=... / IF(DE.GT.1.D-4) call quit(...)（原注释行，略）
                # 标号 13：READ(INSA,*,END=500,ERR=500) FR0,CR0
                fr0, cr0 = _rd_err(insa, 'ff',
                                   ' ERROR IN DATA FILE FOR BF SIG OF AVERAGED LEVELS (1)')
                nfd = 1
                frd[nfd] = fr0
                crd[nfd] = cr0
                luv = False
                for ij in range(1, nfcrr):               # DO 14 IJ=1,NFCRR-1
                    # READ(INSA,*,END=500,ERR=500) FRIN,CRIN
                    frin, crin = _rd_err(
                        insa, 'ff',
                        ' ERROR IN DATA FILE FOR BF SIG OF AVERAGED LEVELS (1)')
                    if luv:
                        continue                         # GOTO 14
                    if frin > fr1:
                        if fr0 <= fr2 and ij > 1:
                            nfd = nfd + 1
                            frd[nfd] = fr0
                            crd[nfd] = cr0
                        nfd = nfd + 1
                        frd[nfd] = frin
                        crd[nfd] = crin
                        luv = True
                    elif frin > fr2:
                        if fr0 <= fr2 and ij > 1:
                            nfd = nfd + 1
                            frd[nfd] = fr0
                            crd[nfd] = cr0
                        nfd = nfd + 1
                        frd[nfd] = frin
                        crd[nfd] = crin
                        fr0 = frin
                        cr0 = crin
                    else:
                        fr0 = frin
                        cr0 = crin
                    if nfd > MFCRA:
                        quit(' Too many frequencies in SIGAVS')
                # 14 CONTINUE
                C.CRMX[ik] = 0.0
                for ij in range(1, nfd + 1):             # DO 15 IJ=1,NFD
                    C.CRMX[ik] = max(C.CRMX[ik], crd[ij])
                # 15 CONTINUE
                if C.CRMX[ik] > 0.0:
                    # WRITE(6,601) ATI,IILO,EELO,NFD（原注释行，略）
                    #  601 FORMAT(F7.2,I6,F13.3,I8)
                    C.NFCR[ik] = nfd
                    for ij in range(1, nfd + 1):         # DO 16 IJ=1,NFD
                        C.FRECR[ik, ij] = frd[nfd - ij + 1]
                        C.CROSR[ik, ij] = crd[nfd - ij + 1] * bam
                    # 16 CONTINUE
            # 12 CONTINUE
        # 10 CONTINUE
    # 标号 100：READ(50,*,END=540,ERR=540) NUNIT
    try:
        _tok = read_line(50).replace(',', ' ').split()
        nunit = int(_tok[0])
    except (EOFError, ValueError, IndexError):
        return                                           # GO TO 540 → RETURN
    if nunit <= 0:
        return
    # WRITE(6,602)
    #  602 FORMAT(///,' DETAILED PHOTOIONIZATION CROSS-SECTIONS',
    #     * ' (NON-EXPLICIT LEVELS)',/,
    #     * ' ---------------------------------------',/)
    print()
    print()
    print()
    print(" DETAILED PHOTOIONIZATION CROSS-SECTIONS (NON-EXPLICIT LEVELS)")
    print()
    print(" ---------------------------------------")
    print()
    for in_l in range(1, nunit + 1):                     # DO 110 IN=1,NUNIT
        # READ(50,*,END=540,ERR=540) ATIR,INSA,NQHTR
        try:
            _tok = read_line(50).replace(',', ' ').split()
            atir = float(_tok[0])
            insa = int(_tok[1])
            nqhtr = int(_tok[2])
        except (EOFError, ValueError, IndexError):
            return                                       # GO TO 540 → RETURN
        nqht = nqht + nqhtr
        if nqht > MPHOT:
            quit(' Too many BF cross-sections in SIGAVS')
        # READ(INSA,*,END=501,ERR=501) IIAT,IIZ,NSUP
        iiat, iiz, nsup = _rd_err(insa, 'iii',
                                  ' ERROR IN DATA FILE FOR BF SIG OF AVERAGED LEVELS (2)')
        # check the total number of superlevels
        if nqhtr > nsup:
            # WRITE(6,603) NQHTR,NSUP
            #  603 FORMAT(' NQHTR=',i4,' in Unit 50 input greater than NSUP=',
            #              i4,/' program resets NQHTR to NSUP'/)
            print(f" NQHTR={nqhtr:4d} in Unit 50 input greater than NSUP={nsup:4d}")
            print(" program resets NQHTR to NSUP")
            print()
            nqhtr = nsup
        # loop over superlevels - read cross-sections
        for i in range(1, nqhtr + 1):                    # DO 120 I=1,NQHTR
            ik = nqht - nqhtr + i
            # READ(INSA,*,END=501,ERR=501) IILO,EELO,GGLO,NFCRR
            iilo, eelo, gglo, nfcrr = _rd_err(
                insa, 'iffi',
                ' ERROR IN DATA FILE FOR BF SIG OF AVERAGED LEVELS (2)')
            C.AQHT[ik] = atir
            C.EQHT[ik] = eelo
            C.GQHT[ik] = gglo
            # READ(INSA,*) FR0,CR0（无 END/ERR 分支，直译为普通自由格式读）
            _tok = read_line(insa).replace(',', ' ').split()
            fr0 = float(_tok[0])
            cr0 = float(_tok[1])
            nfd = 1
            frd[nfd] = fr0
            crd[nfd] = cr0
            luv = False
            for ij in range(1, nfcrr):                   # DO 130 IJ=1,NFCRR-1
                # READ(INSA,*) FRIN,CRIN（无 END/ERR 分支）
                _tok = read_line(insa).replace(',', ' ').split()
                frin = float(_tok[0])
                crin = float(_tok[1])
                if luv:
                    continue                             # GOTO 130
                if frin > fr1:
                    if fr0 <= fr2 and ij > 1:
                        nfd = nfd + 1
                        frd[nfd] = fr0
                        crd[nfd] = cr0
                    nfd = nfd + 1
                    frd[nfd] = frin
                    crd[nfd] = crin
                    luv = True
                elif frin > fr2:
                    if fr0 <= fr2 and ij > 1:
                        nfd = nfd + 1
                        frd[nfd] = fr0
                        crd[nfd] = cr0
                    nfd = nfd + 1
                    frd[nfd] = frin
                    crd[nfd] = crin
                    fr0 = frin
                    cr0 = crin
                else:
                    fr0 = frin
                    cr0 = crin
                # TODO(port): 原代码此处没有循环 14 中的 NFD>MFCRA 检查，
                # nfd 超过 MFCRA 时数组会越界（与 Fortran 越界写对应）
            # 130 CONTINUE
            C.CRMY[ik] = 0.0
            for ij in range(1, nfd + 1):                 # DO 140 IJ=1,NFD
                C.CRMY[ik] = max(C.CRMY[ik], crd[ij])
            # 140 CONTINUE
            if C.CRMY[ik] > 0.0:
                # WRITE(6,611) ATIR,IILO,EELO,NFD
                #  611 FORMAT(F7.2,I6,F13.3,I8)
                print(f"{atir:7.2f}{iilo:6d}{eelo:13.3f}{nfd:8d}")
                C.NFQHT[ik] = nfd
                for ij in range(1, nfd + 1):             # DO 150 IJ=1,NFD
                    C.FRECQ[ik, ij] = frd[nfd - ij + 1]
                    C.QHOT[ik, ij] = crd[nfd - ij + 1] * bam
                # 150 CONTINUE
        # 120 CONTINUE
    # 110 CONTINUE
    # 540 RETURN
    # 500 call quit(' ERROR IN DATA FILE FOR BF SIG OF AVERAGED LEVELS (1)')
    #     → 由 _rd_err 内联实现（标号 500）
    # 501 call quit(' ERROR IN DATA FILE FOR BF SIG OF AVERAGED LEVELS (2)')
    #     → 由 _rd_err 内联实现（标号 501）
    return
