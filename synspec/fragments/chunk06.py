# ============================================================================
# chunk06: synspec54.f 行 5425–6876 的逐行直译
# 包含: HYDLIN, HYDLIW, HE2SET, HE2SEW, HE2LIN, HE2LIW,
#       STARK0, STARKA, STARKIR, DIVSTR
# ============================================================================

# DATA 初始化且之后被修改的局部量（Fortran 隐含 SAVE）→ 提升为模块级
_save_hydlin_init = 0            # HYDLIN: DATA INIT /0/
_save_hydlin_frh = 3.289017e15   # HYDLIN: DATA FRH /3.289017E15/
_save_hydliw_init = 0            # HYDLIW: DATA INIT /0/
_save_hydliw_frh = 3.289017e15   # HYDLIW: DATA FRH /3.289017E15/


def hydlin(id, i0, i1, absoh, emish):
    """
C     opacity and emissivity of hydrogen lines
    对应 synspec54.f 行 5425–5797
    """
    global _save_hydlin_init, _save_hydlin_frh
    # PARAMETER (FRH1=3.28805E15,FRH2=FRH1/4.,UN=1.,SIXTH=1./6.)
    frh1 = 3.28805e15
    frh2 = frh1 / 4.0
    un = 1.0
    sixth = 1.0 / 6.0
    # PARAMETER (CPP=4.1412E-16,CPJ=157803.)
    cpp = 4.1412e-16
    cpj = 157803.0
    # PARAMETER (C00=1.25E-9,CDOP=1.284523E12,CID=0.02654,TWO=2.)
    c00 = 1.25e-9
    cdop = 1.284523e12
    cid = 0.02654
    two = 2.0
    # PARAMETER (CPJ4=CPJ/4.,AL10=2.3025851,CINV=UN/2.997925E18)
    cpj4 = cpj / 4.0
    al10 = 2.3025851
    cinv = un / 2.997925e18
    # PARAMETER (CID1=0.01497)
    cid1 = 0.01497
    # common/quasun/nunalp,nunbet,nungam,nunbal
    # common/hhebrd/sthe,nunhhe
    # common/gompar/hglim,ihgom
    # DIMENSION PJ(40),PRF0(54),OSCH(4,22),ABSO(MFREQ),EMIS(MFREQ),ABSOH(MFREQ),EMISH(MFREQ)
    # TODO(port): Fortran 中 PJ 维数为 40，但下面 DO IL=1,50 会越界写到 50；
    #             这里按 50 分配以保持可运行
    pj = np.zeros(51)
    prf0 = np.zeros(55)
    osch = np.zeros((5, 23))
    abso = np.zeros(MFREQ + 1)
    emis = np.zeros(MFREQ + 1)
    # dimension wlir(15),irlow(15),irupp(15)
    # DATA FRH    /3.289017E15/  → 模块级 _save_hydlin_frh
    # data wlir/.../（之后不再修改，直接函数顶部赋值）
    wlir = np.zeros(16)
    wlir[1:] = [123680.0, 75005.0, 59066.0, 51273.0, 190570.0, 113060.0,
                87577.0, 75061.0, 277960.0, 162050.0, 123840.0, 105010.0,
                223340.0, 168760.0, 141790.0]
    # data irlow/4*6, 4*7, 4*8, 3*9/
    irlow = np.zeros(16, dtype=np.int64)
    irlow[1:] = [6, 6, 6, 6, 7, 7, 7, 7, 8, 8, 8, 8, 9, 9, 9]
    # data irupp/7,8,9,10,8,9,10,11,9,10,11,12,11,12,13/
    irupp = np.zeros(16, dtype=np.int64)
    irupp[1:] = [7, 8, 9, 10, 8, 9, 10, 11, 9, 10, 11, 12, 11, 12, 13]
    # data nlinir/15/
    nlinir = 15
    #
    # DATA INIT /0/  → 模块级 _save_hydlin_init
    #
    for ij in range(i0, i1 + 1):
        absoh[ij] = 0.0
        emish[ij] = 0.0
    #
    if C.IATH <= 0 or C.RRR[1, 1, 1] == 0.0:
        return
    izz = 1
    #
    if _save_hydlin_init == 0:
        for i in range(1, 5):
            for j in range(i + 1, 23):
                # STARK0 修改标量哑元 → 按约定解包接收全部标量哑元
                i, j, izz, xk, wl0, fij, fij0 = stark0(i, j, izz, 0.0, 0.0, 0.0, 0.0)
                C.WLINE[i, j] = wl0
                osch[i, j] = fij + fij0
        _save_hydlin_init = 1
    for ij in range(i0, i1 + 1):
        abso[ij] = 0.0
        emis[ij] = 0.0
    #
    if C.ILOWH <= 0:
        return
    #
    t = C.TEMP[id]
    t1 = un / t
    sqt = math.sqrt(t)
    ane = C.ELEC[id]
    anes = math.exp(sixth * math.log(ane))
    tl = math.log10(t)
    anel = math.log10(ane)
    #
    # populations of the first 40 levels of hydrogen
    #
    anp = C.POPUL[C.NKH, id]
    pp = cpp * ane * anp * t1 / sqt
    nlh = C.N1H - C.N0HN + 1
    # if(ifwop(n1h).lt.0) nlh=nlh-1
    nlh = nlh - 1
    for il in range(1, 51):
        x = il * il
        if il <= nlh:
            pj[il] = C.POPUL[C.N0HN + il - 1, id]
        if il > nlh:
            pj[il] = pp * math.exp(cpj / x * t1) * x * C.WNHINT[il, id]
    p2 = pp * math.exp(cpj4 * t1) * 4.0 * C.WNHINT[2, id]
    #
    # Frequency- and line-independent parameters for evaluating the
    # asymptotic Stark profile
    #
    f00 = c00 * anes * anes * anes * anes
    dop0 = 1.0e8 * math.sqrt(1.65e8 * t + C.VTURB[id])
    #
    # -------------------------------------------------------------------
    # overall loop over spectral series (only in the infrared region)
    # -------------------------------------------------------------------
    #
    iserl = C.ILOWH
    iseru = C.ILOWH
    #
    if C.WLAM[i0] > 14000.0:
        iseru = 4
    if C.WLAM[i0] > 22700.0:
        iseru = 5
    if C.WLAM[i0] > 32800.0:
        iseru = 6
    if C.WLAM[i0] > 44660.0:
        iseru = 7
    if C.WLAM[i0] > 60000.0:
        iserl = 4
    #
    if iserl == 3 and iseru == 3 and C.nunbal > 0:
        iserl = 2
    for ij in range(i0, i1 + 1):
        abso[ij] = 0.0
        emis[ij] = 0.0
    #
    # ========================
    # loop over spectral series
    # ========================
    #
    _goto200 = False  # GO TO 200 标志：跳出谱系循环并跳过远红外块
    for i in range(iserl, iseru + 1):
        #
        # skip the following calculations if one uses the Gomez tables
        #
        if C.ihgom > 0 and C.ELEC[id] > C.hglim:
            if 1 <= i <= C.ihgom:
                ghydop(id, i0, i1, pj, absoh, emish)
                _goto200 = True  # GO TO 200
                break
        #
        ii = i * i
        xii = un / ii
        popi = pj[i]
        if i == 1:
            _save_hydlin_frh = 3.28805e15
        #
        # determination of which hydrogen lines contribute in a current
        # frequency region
        #
        m1 = C.M10
        if i < C.ILOWH:
            m1 = C.ILOWH - 1
        m2 = m1 + 1
        m1 = m1 - 1
        m2 = C.M20 + 3
        if m1 < i + 1:
            m1 = i + 1
        if C.GRAV > 3.0:
            m2 = m2 + 5
            m1 = m1 - 3
            if m1 > i + 6:
                m1 = m1 - 3
        #  new!
        if i >= 3:
            m1 = i + 1
            m2 = i + 40
        if i >= 4:
            m2 = i + 20
        if i >= 6:
            m2 = i + 10
        #
        # loop over lines which contribute at given wavelength region
        #
        m1 = min(m1, 40)
        m2 = min(m2, 40)
        m1 = max(m1, i + 1)
        m2 = max(m2, i + 2)
        for j in range(m1, m2 + 1):
            iline = 0
            jj = j * j
            xjj = un / jj
            abtra = pj[i] * C.WNHINT[j, id]
            emtra = pj[j] * C.WNHINT[i, id] * ii * xjj * math.exp(cpj * (xii - xjj) * t1)
            if i <= 2 and j <= i + 2:
                abtra = pj[i]
                emtra = pj[j] * C.WNHINT[i, id] / C.WNHINT[j, id] * \
                    ii * xjj * math.exp(cpj * (xii - xjj) * t1)
            if i <= 4 and j <= 22:
                iline = C.ILIN0[i, j]
            #
            # quasi-molecular opacity for Lyman-alpha and beta satellites
            #
            lquasi = i == 1 and j == 2 and C.nunalp > 0
            lquasi = lquasi or i == 1 and j == 3 and C.nunbet > 0
            lquasi = lquasi or i == 1 and j == 4 and C.nungam > 0
            lquasi = lquasi or i == 2 and j == 3 and C.nunbal > 0
            lalhhe = i == 1 and j == 2 and C.nunhhe > 0
            if lquasi:
                for ij in range(i0, i1 + 1):
                    # ALLARD 仅给标量哑元 PROF(SG) 赋值；按约定解包全部标量哑元
                    _xl, popi, anp, sg, i, j = allard(C.WLAM[ij], popi, anp, 0.0, i, j)
                    abso[ij] = abso[ij] + sg * abtra
                    emis[ij] = emis[ij] + sg * emtra
            ahe = 0.0
            if C.IATHE > 0:
                ahe = C.POPUL[C.N0A[C.IATHE], id]
            if lalhhe and ahe > 0.0:
                rel = 1.0 / 6.2831855
                for ij in range(i0, i1 + 1):
                    # LYAHHE 仅给标量哑元 PROF(SG0) 赋值；按约定解包全部标量哑元
                    _xl, ahe, sg0 = lyahhe(C.WLAM[ij], ahe, 0.0)
                    sg = sg0 * rel
                    abso[ij] = abso[ij] + sg * abtra
                    emis[ij] = emis[ij] + sg * emtra
            #
            # lines with special Stark broadening tables
            #
            if iline > 0:
                fid = cid * osch[i, j]
                #
                # switch to either original Lemke/Tremblay of Xenomorph
                #
                if C.ILXEN[i, j] == 0 or anel < C.XNEMIN:
                    #
                    # original Lemke/Tremblay
                    #
                    nwl = C.NWLHYD[iline]
                    for iwl in range(1, nwl + 1):
                        prf0[iwl] = C.PRFHYD[iline, id, iwl]
                    for ij in range(i0, i1 + 1):
                        al = abs(C.WLAM[ij] - C.WLINE[i, j])
                        if al < 1.0e-4:
                            al = 1.0e-4
                        if C.ILEMKE == 1:
                            al = al / f00
                        al = math.log10(al)
                        # DO 30 IWL=1,NWL-1 ... GO TO 40
                        for iwl in range(1, nwl):
                            iw0 = iwl
                            if al <= C.WLHYD[iline, iwl + 1]:
                                break  # GO TO 40
                        # 标号 40
                        iw1 = iw0 + 1
                        prff = (prf0[iw0] * (C.WLHYD[iline, iw1] - al) + prf0[iw1] *
                                (al - C.WLHYD[iline, iw0])) / \
                               (C.WLHYD[iline, iw1] - C.WLHYD[iline, iw0])
                        sg = math.exp(prff * al10) * fid
                        sg0 = math.exp(prff * al10)
                        if C.ILEMKE == 1:
                            sg = sg * C.WLINE[i, j] ** 2 * cinv / f00
                        abso[ij] = abso[ij] + sg * abtra
                        emis[ij] = emis[ij] + sg * emtra
                #
                # XENOMORPH data for selected lines
                #
                else:
                    ixn = C.ILXEN[i, j]
                    nwl = C.NWLXEN[ixn]
                    fr0l = 2.997925e18 / C.WLINE[i, j]
                    for ij in range(i0, i1 + 1):
                        al = (C.FREQ[ij] - fr0l) / f00
                        if abs(al) < 1.0e-4:
                            al = 1.0e-4
                        all = math.log10(abs(al))  # 原变量名 ALL
                        # do 51 iwl=1,nwl-1 ... go to 52
                        for iwl in range(1, nwl):
                            iw0 = iwl
                            if all <= C.ALXEN[ixn, iwl + 1]:
                                break  # GO TO 52
                        # 标号 52
                        iw1 = iw0 + 1
                        if al > 0.0:
                            prff = (C.PRFB[ixn, id, iw0] * (C.ALXEN[ixn, iw1] - all) +
                                    C.PRFB[ixn, id, iw1] * (all - C.ALXEN[ixn, iw0])) / \
                                   (C.ALXEN[ixn, iw1] - C.ALXEN[ixn, iw0])
                        else:
                            prff = (C.PRFR[ixn, id, iw0] * (C.ALXEN[ixn, iw1] - all) +
                                    C.PRFR[ixn, id, iw1] * (all - C.ALXEN[ixn, iw0])) / \
                                   (C.ALXEN[ixn, iw1] - C.ALXEN[ixn, iw0])
                        sg = math.exp(prff * al10) * fid / f00
                        abso[ij] = abso[ij] + sg * abtra
                        emis[ij] = emis[ij] + sg * emtra
            #
            # lines without special Stark broadening tables
            #
            else:
                # STARK0 修改标量哑元 → 按约定解包接收全部标量哑元
                i, j, izz, xkij, wl0, fij, fij0 = stark0(i, j, izz, 0.0, 0.0, 0.0, 0.0)
                if (wl0 <= C.WLAM[i1] and 1.25 * wl0 > C.WLAM[i0]) or \
                   (wl0 >= C.WLAM[i0] and 0.75 * wl0 < C.WLAM[i1]):
                    fxk = f00 * xkij
                    fxk1 = un / fxk
                    dop = dop0 / wl0
                    dbeta = wl0 * wl0 * cinv * fxk1
                    C.DBETA = dbeta   # DBETA 属 COMMON /AUXHYD/（STARKIR 经 COMMON 读取）
                    betad = dop * dbeta
                    C.BETAD = betad   # BETAD 属 COMMON /AUXHYD/（DIVSTR/STARKA 经 COMMON 读取）
                    fid = cid * fij * dbeta
                    # FID0=CID1*FIJ0/DOP
                    # TODO(port): DIVSTR 在 BETAD<BL 时提前返回且不赋 DIV
                    # （Fortran 中此时 DIV 为未定义值，但该分支 STARKA 不会用到 DIV）
                    ad, div = divstr(0.0, 0.0)
                    fac = two
                    if lquasi:
                        fac = un
                    for ij in range(i0, i1 + 1):
                        fr = C.FREQ[ij]
                        beta = abs(C.WLAM[ij] - wl0) * fxk1
                        if i < 5:
                            sg = starka(beta, ad, div, fac) * fid
                            if C.IOPHLI == 2 and i == 1 and j == 2:
                                sg = sg * feautr(fr, id)
                        else:
                            sg = starkir(ii, jj, t, ane, beta) * fid
                        abso[ij] = abso[ij] + sg * abtra
                        emis[ij] = emis[ij] + sg * emtra
        # END DO (J 循环)
    # END DO (I 循环)
    #
    # far infrared hydrogen lines
    #
    if not _goto200 and C.WLAM[i1] > 70000.0:
        for i in range(8, 14):
            ii = i * i
            xii = un / ii
            for j in range(i + 1, i + 5):
                jj = j * j
                xjj = un / jj
                i, j, izz, xkij, wl0, fij, fij0 = stark0(i, j, izz, 0.0, 0.0, 0.0, 0.0)
                if (wl0 <= C.WLAM[i1] and 1.5 * wl0 > C.WLAM[i0]) or \
                   (wl0 >= C.WLAM[i0] and 0.5 * wl0 < C.WLAM[i1]):
                    fxk = f00 * xkij
                    fxk1 = un / fxk
                    dop = dop0 / wl0
                    dbeta = wl0 * wl0 * cinv * fxk1
                    C.DBETA = dbeta   # DBETA 属 COMMON /AUXHYD/（STARKIR 经 COMMON 读取）
                    betad = dop * dbeta
                    C.BETAD = betad   # BETAD 属 COMMON /AUXHYD/（DIVSTR/STARKA 经 COMMON 读取）
                    fid = cid * fij * dbeta
                    ad, div = divstr(0.0, 0.0)
                    fac = two
                    for ij in range(i0, i1 + 1):
                        fr = C.FREQ[ij]
                        beta = abs(C.WLAM[ij] - wl0) * fxk1
                        sg = starkir(ii, jj, t, ane, beta) * fid
                        abso[ij] = abso[ij] + sg * abtra
                        emis[ij] = emis[ij] + sg * emtra
    # 标号 200
    #
    if C.WLAM[i1] > 5.0e5:
        for ij in range(i0, i1 + 1):
            fr = C.FREQ[ij]
            for ilir in range(1, nlinir + 1):
                if C.WLAM[ij] > wlir[ilir] * 0.95 and \
                   C.WLAM[ij] < wlir[ilir] * 1.05:
                    j = irupp[ilir]
                    jj = j * j
                    i = irlow[ilir]
                    ii = i * i
                    xii = un / ii
                    xjj = un / jj
                    abtra = pj[i] * C.WNHINT[j, id]
                    emtra = pj[j] * C.WNHINT[i, id] * ii * xjj * math.exp(cpj * (xii - xjj) * t1)
                    i, j, izz, xkij, wl0, fij, fij0 = stark0(i, j, izz, 0.0, 0.0, 0.0, 0.0)
                    fxk = f00 * xkij
                    fxk1 = un / fxk
                    dop = dop0 / wl0
                    dbeta = wl0 * wl0 * cinv * fxk1
                    C.DBETA = dbeta   # DBETA 属 COMMON /AUXHYD/（STARKIR 经 COMMON 读取）
                    betad = dop * dbeta
                    C.BETAD = betad   # BETAD 属 COMMON /AUXHYD/（DIVSTR/STARKA 经 COMMON 读取）
                    fid = cid * fij * dbeta
                    ad, div = divstr(0.0, 0.0)
                    fac = two
                    beta = abs(C.WLAM[ij] - wl0) * fxk1
                    sg = starka(beta, ad, div, fac) * fid
                    abso[ij] = abso[ij] + sg * abtra
                    emis[ij] = emis[ij] + sg * emtra
    #
    # ----------------------------
    # total opacity and emissivity
    # ----------------------------
    #
    for ij in range(i0, i1 + 1):
        f = C.FREQ[ij]
        f15 = f * 1.0e-15
        xkf = math.exp(-4.79928e-11 * f * t1)
        xkfb = xkf * 1.4743e-2 * f15 * f15 * f15
        absoh[ij] = abso[ij] - xkf * emis[ij]
        emish[ij] = xkfb * emis[ij]
    return


def hydliw(id, absoh, emish):
    """
C     opacity and emissivity of hydrogen lines
    对应 synspec54.f 行 5798–6060
    """
    global _save_hydliw_init, _save_hydliw_frh
    # PARAMETER (FRH1=3.28805E15,FRH2=FRH1/4.,UN=1.,SIXTH=1./6.)
    frh1 = 3.28805e15
    frh2 = frh1 / 4.0
    un = 1.0
    sixth = 1.0 / 6.0
    # PARAMETER (CPP=4.1412E-16,CPJ=157803.)
    cpp = 4.1412e-16
    cpj = 157803.0
    # PARAMETER (C00=1.25E-9,CDOP=1.284523E12,CID=0.02654,TWO=2.)
    c00 = 1.25e-9
    cdop = 1.284523e12
    cid = 0.02654
    two = 2.0
    # PARAMETER (CPJ4=CPJ/4.,AL10=2.3025851,CINV=UN/2.997925E18)
    cpj4 = cpj / 4.0
    al10 = 2.3025851
    cinv = un / 2.997925e18
    # PARAMETER (CID1=0.01497)
    cid1 = 0.01497
    # common/lasers/lasdel
    # common/quasun/nunalp,nunbet,nungam,nunbal
    # DIMENSION PJ(40),PRF0(54),OSCH(4,22),ABSO(MFREQ),EMIS(MFREQ),ABSOH(MFREQ),EMISH(MFREQ)
    pj = np.zeros(41)
    prf0 = np.zeros(55)
    osch = np.zeros((5, 23))
    abso = np.zeros(MFREQ + 1)
    emis = np.zeros(MFREQ + 1)
    # DATA FRH    /3.289017E15/  → 模块级 _save_hydliw_frh
    # DATA INIT /0/              → 模块级 _save_hydliw_init
    #
    if C.IATH <= 0:
        return
    izz = 1
    #
    if _save_hydliw_init == 0:
        for i in range(1, 5):
            for j in range(i + 1, 23):
                i, j, izz, xk, wl0, fij, fij0 = stark0(i, j, izz, 0.0, 0.0, 0.0, 0.0)
                C.WLINE[i, j] = wl0
                osch[i, j] = fij + fij0
        _save_hydliw_init = 1
    for ij in range(1, NFREQ + 1):
        abso[ij] = 0.0
        emis[ij] = 0.0
        absoh[ij] = 0.0
        emish[ij] = 0.0
    t = C.TEMP[id]
    t1 = un / t
    sqt = math.sqrt(t)
    ane = C.ELEC[id]
    anes = math.exp(sixth * math.log(ane))
    #
    # populations of the first 40 levels of hydrogen
    #
    anp = C.POPUL[C.NKH, id]
    pp = cpp * ane * anp * t1 / sqt
    nlh = C.N1H - C.N0HN + 1
    if C.ifwop[C.N1H] < 0:
        nlh = nlh - 1
    # DO 5 IL=1,40
    for il in range(1, 41):
        x = il * il
        if il <= nlh:
            pj[il] = C.POPUL[C.N0HN + il - 1, id]
        if il > nlh:
            pj[il] = pp * math.exp(cpj / x * t1) * x * C.WNHINT[il, id]
    # 5 CONTINUE
    p2 = pp * math.exp(cpj4 * t1) * 4.0 * C.WNHINT[2, id]
    #
    # Frequency- and line-independent parameters for evaluating the
    # asymptotic Stark profile
    #
    f00 = c00 * anes * anes * anes * anes
    dop0 = 1.0e8 * math.sqrt(1.65e8 * t + C.VTURB[id])
    #
    # -------------------------------------------------------------------
    # overall loop over spectral series (only in the infrared region)
    # -------------------------------------------------------------------
    #
    # DO 300 IJ=1,NFREQ
    for ij in range(1, NFREQ + 1):
        if C.IHYLW[ij] <= 0:
            continue  # GO TO 300
        iserl = C.ILOWHW[ij]
        iseru = C.ILOWHW[ij]
        if C.WLAM[ij] > 17000.0 and C.WLAM[ij] <= 21000.0:
            iserl = 3
            iseru = 4
        elif C.WLAM[ij] > 22700.0 and C.WLAM[ij] <= 29000.0:
            iserl = 4
            iseru = 5
        elif C.WLAM[ij] > 32800.0 and C.WLAM[ij] <= 37000.0:
            iserl = 5
            iseru = 6
        elif C.WLAM[ij] > 37000.0 and C.WLAM[ij] <= 44600.0:
            iserl = 4
            iseru = 6
        elif C.WLAM[ij] > 44660.0 and C.WLAM[ij] <= 58300.0:
            iserl = 5
            iseru = 7
        elif C.WLAM[ij] > 58300.0 and C.WLAM[ij] <= 72000.0:
            iserl = 6
            iseru = 8
        elif C.WLAM[ij] > 72000.0 and C.WLAM[ij] <= 73800.0:
            iserl = 5
            iseru = 8
        elif C.WLAM[ij] > 73800.0 and C.WLAM[ij] <= 77000.0:
            iserl = 5
            iseru = 9
        elif C.WLAM[ij] > 77000.0:
            iserl = 6
            iseru = 9
        #
        if iserl == 3 and iseru == 3 and C.nunbal > 0:
            iserl = 2
        #
        abso[ij] = 0.0
        emis[ij] = 0.0
        # DO 200 I=ISERL,ISERU
        for i in range(iserl, iseru + 1):
            ii = i * i
            xii = un / ii
            pltei = pp * math.exp(cpj * t1 * xii) * ii
            popi = pj[i]
            if i == 1:
                _save_hydliw_frh = 3.28805e15
            #
            # determination of which hydrogen lines contribute in a current
            # frequency region
            #
            m1 = C.M10W[ij]
            if i < C.ILOWHW[ij]:
                m1 = C.ILOWHW[ij] - 1
            m2 = m1 + 1
            if m1 < i + 1:
                m1 = i + 1
            # IF(grav.lt.3..and.M1.LE.16.AND.I.EQ.7) GO TO 10（及以下一串）的逆分支
            _goto10 = C.GRAV < 3.0 and (
                (m1 <= 16 and i == 7) or (m1 <= 14 and i == 6) or
                (m1 <= 12 and i == 5) or (m1 <= 10 and i == 4) or
                (m1 <= 8 and i == 3) or (m1 <= 6 and i == 2) or
                (m1 <= 4 and i == 1))
            if not _goto10:
                m1 = m1 - 1
                m2 = C.M20W[ij] + 3
                if m1 < i + 1:
                    m1 = i + 1
            # 标号 10
            if C.GRAV > 3.0:
                m2 = m2 + 5
                m1 = m1 - 3
                if m1 > i + 6:
                    m1 = m1 - 3
            if C.GRAV > 6.0:
                m2 = m2 + 2
                m1 = m1 - 1
                if m1 > i + 6:
                    m1 = m1 - 1
            if m1 < i + 1:
                m1 = i + 1
            #      if(m2.gt.30) then
            #        m2=m20W(IJ)+8
            #         m1=m1-4
            #      end if
            if m2 > 40:
                m2 = 40
            #     if(id.eq.1) write(6,666) i,m1,m2
            # 666 format(/' hydrogen lines contribute - ilow=',i2,', iup from ',i3,
            #    *       ' to',i3/)
            #
            a = 0.0
            e = 0.0
            #
            # loop over lines which contribute at given wavelength region
            #
            # DO 100 J=M1,M2
            for j in range(m1, m2 + 1):
                if i == 1 and j <= 5 and C.IOPHLI < 0:
                    continue  # GO TO 100
                iline = 0
                jj = j * j
                xjj = un / jj
                abtra = pj[i] * C.WNHINT[j, id]
                emtra = pj[j] * C.WNHINT[i, id] * ii * xjj * math.exp(cpj * (xii - xjj) * t1)
                if i <= 2 and j <= i + 2:
                    abtra = pj[i]
                    emtra = pj[j] * C.WNHINT[i, id] / C.WNHINT[j, id] * \
                        ii * xjj * math.exp(cpj * (xii - xjj) * t1)
                if i <= 4 and j <= 22:
                    iline = C.ILIN0[i, j]
                #
                # quasi-molecular opacity for Lyman-alpha and beta satellites
                #
                lquasi = i == 1 and j == 2 and C.nunalp > 0
                lquasi = lquasi or i == 1 and j == 3 and C.nunbet > 0
                lquasi = lquasi or i == 1 and j == 4 and C.nungam > 0
                lquasi = lquasi or i == 2 and j == 3 and C.nunbal > 0
                if lquasi:
                    i, j, izz, xkij, wl0, fij, fij0 = stark0(i, j, izz, 0.0, 0.0, 0.0, 0.0)
                    fxk = f00 * xkij
                    fxk1 = un / fxk
                    dop = dop0 / wl0
                    dbeta = wl0 * wl0 * cinv * fxk1
                    C.DBETA = dbeta   # DBETA 属 COMMON /AUXHYD/（STARKIR 经 COMMON 读取）
                    betad = dop * dbeta
                    C.BETAD = betad   # BETAD 属 COMMON /AUXHYD/（DIVSTR/STARKA 经 COMMON 读取）
                    fid = cid * fij * dbeta
                    ad, div = divstr(0.0, 0.0)
                    fr = C.FREQ[ij]
                    beta = abs(C.WLAM[ij] - wl0) * fxk1
                    # ALLARD 仅给标量哑元 PROF(SG) 赋值；按约定解包全部标量哑元
                    _xl, popi, anp, sg, i, j = allard(C.WLAM[ij], popi, anp, 0.0, i, j)
                    sg = sg + starka(beta, ad, div, un) * fid
                    abso[ij] = abso[ij] + sg * abtra
                    emis[ij] = emis[ij] + sg * emtra
                    continue  # GO TO 100
                #
                # lines with special Stark broadening tables
                #
                if iline > 0:
                    nwl = C.NWLHYD[iline]
                    for iwl in range(1, nwl + 1):
                        prf0[iwl] = C.PRFHYD[iline, id, iwl]
                    fid = cid * osch[i, j]
                    al = abs(C.WLAM[ij] - C.WLINE[i, j])
                    if al < 1.0e-4:
                        al = 1.0e-4
                    if C.ILEMKE == 1:
                        al = al / f00
                    al = math.log10(al)
                    # DO 30 IWL=1,NWL-1 ... GO TO 40
                    for iwl in range(1, nwl):
                        iw0 = iwl
                        if al <= C.WLHYD[iline, iwl + 1]:
                            break  # GO TO 40
                    # 标号 40
                    iw1 = iw0 + 1
                    prff = (prf0[iw0] * (C.WLHYD[iline, iw1] - al) + prf0[iw1] *
                            (al - C.WLHYD[iline, iw0])) / \
                           (C.WLHYD[iline, iw1] - C.WLHYD[iline, iw0])
                    sg = math.exp(prff * al10) * fid
                    if C.ILEMKE == 1:
                        sg = sg * C.WLINE[i, j] ** 2 * cinv / f00
                    abso[ij] = abso[ij] + sg * abtra
                    emis[ij] = emis[ij] + sg * emtra
                #
                # lines without special Stark broadening tables
                #
                else:
                    i, j, izz, xkij, wl0, fij, fij0 = stark0(i, j, izz, 0.0, 0.0, 0.0, 0.0)
                    fxk = f00 * xkij
                    fxk1 = un / fxk
                    dop = dop0 / wl0
                    dbeta = wl0 * wl0 * cinv * fxk1
                    C.DBETA = dbeta   # DBETA 属 COMMON /AUXHYD/（STARKIR 经 COMMON 读取）
                    betad = dop * dbeta
                    C.BETAD = betad   # BETAD 属 COMMON /AUXHYD/（DIVSTR/STARKA 经 COMMON 读取）
                    fid = cid * fij * dbeta
                    ad, div = divstr(0.0, 0.0)
                    fr = C.FREQ[ij]
                    beta = abs(C.WLAM[ij] - wl0) * fxk1
                    sg = starka(beta, ad, div, two) * fid
                    if C.IOPHLI == 2 and i == 1 and j == 2:
                        sg = sg * feautr(fr, id)
                    abso[ij] = abso[ij] + sg * abtra
                    emis[ij] = emis[ij] + sg * emtra
            # 100 CONTINUE
        # 200 CONTINUE
        #
        # ----------------------------
        # total opacity and emissivity
        # ----------------------------
        #
        f = C.FREQ[ij]
        f15 = f * 1.0e-15
        xkf = math.exp(-4.79928e-11 * f * t1)
        xkfb = xkf * 1.4743e-2 * f15 * f15 * f15
        if abso[ij] <= 0.0 and C.lasdel:
            abso[ij] = 0.0
            emis[ij] = 0.0
        absoh[ij] = abso[ij] - xkf * emis[ij]
        emish[ij] = xkfb * emis[ij]
    # 300 CONTINUE
    return


def he2set():
    """
C     Initialization procedure for treating the He II line opacity
    对应 synspec54.f 行 6061–6157
    """
    # dimension frhe(12)
    # DATA FRHE /.../（之后不再修改）
    frhe = np.zeros(13)
    frhe[1:] = [1.3158153e16, 3.2895381e15, 1.4624854e15,
                8.2261878e14, 5.2647201e14, 3.6560459e14,
                2.6860713e14, 2.0565220e14, 1.6249055e14,
                1.3161730e14, 1.0877460e14, 9.1400851e13]
    #
    # IHE2L=-1  -  He II lines are excluded a priori
    #
    C.IHE2L = -1
    if C.IFHE2 <= 0:
        return
    if C.FREQ[2] >= 1.315812e16:
        return
    al0 = 2.997925e17 / C.FREQ[1]
    al1 = 2.997925e17 / C.FREQ[2]
    #      IF(AL0.GT.390.) RETURN
    if C.GRAV < 6.0:
        if al0 > 31.0 and al1 < 91.1:
            return
        if al0 > 26.1 and al1 < 29.8:
            return
        if al0 > 24.8 and al1 < 25.1:
            return
        if al0 > 122.1 and al1 < 162.9:
            return
        if al0 > 165.1 and al1 < 204.9:
            return
        if al0 > 109.0 and al1 < 120.9:
            return
        if al0 > 103.0 and al1 < 107.9:
            return
        if al0 > 99.7 and al1 < 102.0:
            return
        if al0 > 320.8 and al1 < 364.4:
            return
        if al0 > 273.8 and al1 < 319.8:
            return
        if al0 > 251.6 and al1 < 272.8:
            return
        if al0 > 239.0 and al1 < 250.6:
            return
        if al0 > 231.1 and al1 < 238.0:
            return
        if al0 > 225.8 and al1 < 230.1:
            return
    elif C.GRAV < 7.0:
        if al0 > 33.0 and al1 < 91.1:
            return
        if al0 > 124.1 and al1 < 160.9:
            return
        if al0 > 167.1 and al1 < 202.9:
            return
        if al0 > 111.0 and al1 < 118.9:
            return
        if al0 > 322.8 and al1 < 364.4:
            return
        if al0 > 275.8 and al1 < 317.8:
            return
        if al0 > 253.6 and al1 < 270.8:
            return
        if al0 > 241.0 and al1 < 248.6:
            return
        if al0 > 233.1 and al1 < 236.0:
            return
    else:
        if al0 > 39.0 and al1 < 91.1:
            return
        if al0 > 134.1 and al1 < 150.9:
            return
        if al0 > 177.1 and al1 < 202.9:
            return
    #
    # otherwise, He II lines are included
    #
    C.IHE2L = 1
    C.MHE10 = 60
    C.MHE20 = 60
    if al1 < 91.0:
        C.ILWHE2 = 1
    elif al0 < 204.0:
        C.ILWHE2 = 2
    elif al0 < 364.0:
        C.ILWHE2 = 3
    elif al0 < 569.0:
        C.ILWHE2 = 4
    elif al0 < 819.0:
        C.ILWHE2 = 5
    elif al0 < 1116.0:
        C.ILWHE2 = 6
    elif al0 < 1457.0:
        C.ILWHE2 = 7
    elif al0 < 1844.0:
        C.ILWHE2 = 8
    elif al0 < 2277.0:
        C.ILWHE2 = 9
    elif al0 < 2756.0:
        C.ILWHE2 = 10
    elif al0 < 3279.0:
        C.ILWHE2 = 11
    else:
        C.ILWHE2 = 12
    frion = frhe[C.ILWHE2]
    fr1 = frion * C.ILWHE2 * C.ILWHE2
    if frion > C.FREQ[2]:
        C.MHE10 = int(math.sqrt(fr1 / (frion - C.FREQ[2])))
    if frion > C.FREQ[1]:
        C.MHE20 = int(math.sqrt(fr1 / (frion - C.FREQ[1])))
    #  601 FORMAT(1H0/ ' *** HE II LINES CONTRIBUTE'/
    #     * '     THE NEAREST LINE ON THE SHORT-WAVELENGTH SIDE IS',
    #     * I3,'  TO ',I3/)
    print()
    print(' *** HE II LINES CONTRIBUTE')
    print('     THE NEAREST LINE ON THE SHORT-WAVELENGTH SIDE IS'
          f'{C.ILWHE2:3d}  TO {C.MHE20 + 1:3d}')
    print()
    return


def he2sew(ij):
    """
C     Initialization procedure for treating the He II line opacity
    对应 synspec54.f 行 6158–6246
    """
    # dimension frhe(12)
    # DATA FRHE /.../（之后不再修改）
    frhe = np.zeros(13)
    frhe[1:] = [1.3158153e16, 3.2895381e15, 1.4624854e15,
                8.2261878e14, 5.2647201e14, 3.6560459e14,
                2.6860713e14, 2.0565220e14, 1.6249055e14,
                1.3161730e14, 1.0877460e14, 9.1400851e13]
    #
    # IHE2L=-1  -  He II lines are excluded a priori
    #
    C.IHE2LW[ij] = -1
    if C.IFHE2 <= 0:
        return
    fr = C.FREQ[ij]
    al0 = 2.997925e17 / fr
    al1 = 2.997925e17 / fr
    if C.GRAV < 6.0:
        if al0 > 31.0 and al1 < 91.1:
            return
        if al0 > 26.1 and al1 < 29.8:
            return
        if al0 > 24.8 and al1 < 25.1:
            return
        if al0 > 122.1 and al1 < 162.9:
            return
        if al0 > 165.1 and al1 < 204.9:
            return
        if al0 > 109.0 and al1 < 120.9:
            return
        if al0 > 103.0 and al1 < 107.9:
            return
        if al0 > 99.7 and al1 < 102.0:
            return
        if al0 > 320.8 and al1 < 364.4:
            return
        if al0 > 273.8 and al1 < 319.8:
            return
        if al0 > 251.6 and al1 < 272.8:
            return
        if al0 > 239.0 and al1 < 250.6:
            return
        if al0 > 231.1 and al1 < 238.0:
            return
        if al0 > 225.8 and al1 < 230.1:
            return
    elif C.GRAV < 7.0:
        if al0 > 33.0 and al1 < 91.1:
            return
        if al0 > 124.1 and al1 < 160.9:
            return
        if al0 > 167.1 and al1 < 202.9:
            return
        if al0 > 111.0 and al1 < 118.9:
            return
        if al0 > 322.8 and al1 < 364.4:
            return
        if al0 > 275.8 and al1 < 317.8:
            return
        if al0 > 253.6 and al1 < 270.8:
            return
        if al0 > 241.0 and al1 < 248.6:
            return
        if al0 > 233.1 and al1 < 236.0:
            return
    else:
        if al0 > 39.0 and al1 < 91.1:
            return
        if al0 > 134.1 and al1 < 150.9:
            return
        if al0 > 177.1 and al1 < 202.9:
            return
    #
    # otherwise, He II lines are included
    #
    C.IHE2LW[ij] = 1
    C.MHE10W[ij] = 60
    C.MHE20W[ij] = 60
    if al1 < 91.0:
        C.ILWHEW[ij] = 1
    elif al0 < 204.0:
        C.ILWHEW[ij] = 2
    elif al0 < 364.0:
        C.ILWHEW[ij] = 3
    elif al0 < 569.0:
        C.ILWHEW[ij] = 4
    elif al0 < 819.0:
        C.ILWHEW[ij] = 5
    elif al0 < 1116.0:
        C.ILWHEW[ij] = 6
    elif al0 < 1457.0:
        C.ILWHEW[ij] = 7
    elif al0 < 1844.0:
        C.ILWHEW[ij] = 8
    elif al0 < 2277.0:
        C.ILWHEW[ij] = 9
    elif al0 < 2756.0:
        C.ILWHEW[ij] = 10
    elif al0 < 3279.0:
        C.ILWHEW[ij] = 11
    else:
        C.ILWHEW[ij] = 12
    frion = frhe[C.ILWHEW[ij]]
    fr1 = frion * C.ILWHEW[ij] * C.ILWHEW[ij]
    if frion > fr:
        C.MHE10W[ij] = int(math.sqrt(fr1 / (frion - fr)))
    return


def he2lin(id, i0, i1, absoh, emish):
    """
C     opacity and emissivity of He II lines  (these which are not considered
C     explicitly)
    对应 synspec54.f 行 6247–6450
    """
    # PARAMETER (UN=1.,SIXTH=1./6.)
    un = 1.0
    sixth = 1.0 / 6.0
    # PARAMETER (CPP=4.1412E-16,CPJ=631479.)
    cpp = 4.1412e-16
    cpj = 631479.0
    # PARAMETER (C00=1.25E-9,CDOP=1.284523E12,CID=0.02654,TWO=2.)
    c00 = 1.25e-9
    cdop = 1.284523e12
    cid = 0.02654
    two = 2.0
    # PARAMETER (CPJ4=CPJ/4.,AL10=2.3025851,CINV=UN/2.997925E18)
    cpj4 = cpj / 4.0
    al10 = 2.3025851
    cinv = un / 2.997925e18
    # PARAMETER (CID1=0.01497)
    cid1 = 0.01497
    # DIMENSION PJ(80),FRHE(12),OSCHE2(19),PRF0(36),ABSO(MFREQ),EMIS(MFREQ),ABSOH(MFREQ),EMISH(MFREQ)
    pj = np.zeros(81)
    # DATA FRHE /.../（之后不再修改）
    frhe = np.zeros(13)
    frhe[1:] = [1.3158153e16, 3.2895381e15, 1.4624854e15,
                8.2261878e14, 5.2647201e14, 3.6560459e14,
                2.6860713e14, 2.0565220e14, 1.6249055e14,
                1.3161730e14, 1.0877460e14, 9.1400851e13]
    # DATA OSCHE2/.../（之后不再修改）
    osche2 = np.zeros(20)
    osche2[1:] = [6.407e-1, 1.506e-1, 5.584e-2, 2.768e-2,
                  1.604e-2, 1.023e-2, 6.980e-3,
                  8.421e-1, 3.230e-2, 1.870e-2, 1.196e-2, 8.187e-3,
                  5.886e-3, 4.393e-3, 3.375e-3, 2.656e-3,
                  1.038, 1.793e-1, 6.549e-2]
    prf0 = np.zeros(37)
    abso = np.zeros(MFREQ + 1)
    emis = np.zeros(MFREQ + 1)
    # COMMON/HE2PRF/PRFHE2(19,MDEPTH,36),WLHE2(19,36),NWLHE2(19),ILHE2(19),IUHE2(19)
    #
    i = C.ILWHE2
    izz = 2
    for ij in range(i0, i1 + 1):
        abso[ij] = 0.0
        emis[ij] = 0.0
        absoh[ij] = 0.0
        emish[ij] = 0.0
    t = C.TEMP[id]
    t1 = un / t
    sqt = math.sqrt(t)
    ane = C.ELEC[id]
    anes = math.exp(sixth * math.log(ane))
    #
    # He III populations (either LTE or NLTE, depending on input model)
    #
    if C.IELHE2 > 0:
        anp = C.POPUL[C.NNEXT[C.IELHE2], id]
        nlhe2 = C.NLAST[C.IELHE2] - C.NFIRST[C.IELHE2] + 1
    else:
        anp = C.RRR[id, 3, 2]
        nlhe2 = 0
    #
    # populations of the first 60 levels of He II
    #
    pp = cpp * ane * anp * t1 / sqt
    for il in range(1, 61):
        x = il * il
        iil = C.NFIRST[C.IELHE2] + il - 1
        if il <= nlhe2:
            pj[il] = C.POPUL[iil, id]
        if il > nlhe2:
            pj[il] = pp * math.exp(cpj / x * t1) * x * C.WNHE2[il, id]
    #
    # Frequency- and line-independent parameters for evaluating the
    # asymptotic Stark profile
    #
    f00 = 3.906e-11 * anes * anes * anes * anes
    dop0 = 1.0e8 * math.sqrt(4.12e7 * t + C.VTURB[id])
    #
    # -------------------------------------------------------------------
    # overall loop over spectral series (only in the infrared region)
    # -------------------------------------------------------------------
    #
    iseru = C.ILWHE2
    if C.ILWHE2 <= 3:
        iserl = C.ILWHE2
    elif C.ILWHE2 <= 5:
        iserl = C.ILWHE2 - 1
    elif C.ILWHE2 <= 7:
        iserl = C.ILWHE2 - 2
    elif C.ILWHE2 <= 9:
        iserl = C.ILWHE2 - 3
    else:
        iserl = C.ILWHE2 - 4
    #
    for ij in range(i0, i1 + 1):
        abso[ij] = 0.0
        emis[ij] = 0.0
    #
    # DO 200 I=ISERL,ISERU
    for i in range(iserl, iseru + 1):
        ii = i * i
        xii = un / ii
        popi = pj[i]
        #
        # determination of which He II lines contribute in a current
        # frequency region
        #
        m1 = C.MHE10
        if i < C.ILWHE2 and frhe[i] > C.FREQ[2]:
            m1 = int(math.sqrt(frhe[i] * ii / (frhe[i] - C.FREQ[2])))
        m2 = m1 + 1
        if m1 < i + 1:
            m1 = i + 1
        # IF(grav.lt.6..and.M1.LE.6.AND.I.EQ.2) GO TO 10（及下一条）的逆分支
        _goto10 = C.GRAV < 6.0 and ((m1 <= 6 and i == 2) or (m1 <= 4 and i == 1))
        if not _goto10:
            m1 = m1 - 1
            m2 = C.MHE20 + 3
            if m2 > 60:
                m2 = 60
        # 标号 10
        if C.GRAV > 6.0:
            m2 = m2 + 5
            m1 = m1 - 3
            if m1 > i + 6:
                m1 = m1 - 3
        if m1 < i + 1:
            m1 = i + 1
        if m2 > 60:
            m2 = 60
        #     A=0.
        #     E=0.
        #
        # loop over lines which contribute at given wavelength region
        #
        # DO 100 J=M1,M2
        for j in range(m1, m2 + 1):
            iline = 0
            jj = j * j
            xjj = un / jj
            abtra = pj[i] * C.WNHE2[j, id]
            emtra = pj[j] * C.WNHE2[i, id] * ii * xjj * math.exp(cpj * (xii - xjj) * t1)
            if i <= 2:
                wlin = 227.838 / (xii - 1.0 / jj)
            else:
                wlin = 227.7776 / (xii - 1.0 / jj)
            if i == 2:
                if j == 3 and C.IHE2PR > 0:
                    iline = 1
            elif i == 3:
                if j == 4 and C.IHE2PR > 0:
                    iline = 8
                if j > 5 and j <= 10 and C.IHE2PR > 0:
                    iline = j - 3
            elif i == 4:
                if j <= 7 and C.IHE2PR > 0:
                    iline = j + 12
                if j >= 8 and j <= 15 and C.IHE2PR > 0:
                    iline = j + 1
            if iline > 0:
                nwl = C.NWLHE2[iline]
                for iwl in range(1, nwl + 1):
                    prf0[iwl] = C.PRFHE2[iline, id, iwl]
                fid = cid * osche2[iline]
                # DO 50 IJ=I0,I1
                for ij in range(i0, i1 + 1):
                    al = abs(C.WLAM[ij] - wlin)
                    if al < 1.0e-4:
                        al = 1.0e-4
                    al = math.log10(al)
                    # DO IWL=1,NWL-1 ... GO TO 40
                    for iwl in range(1, nwl):
                        iw0 = iwl
                        if al <= C.WLHE2[iline, iwl + 1]:
                            break  # GO TO 40
                    # 标号 40
                    iw1 = iw0 + 1
                    prff = (prf0[iw0] * (C.WLHE2[iline, iw1] - al) + prf0[iw1] *
                            (al - C.WLHE2[iline, iw0])) / \
                           (C.WLHE2[iline, iw1] - C.WLHE2[iline, iw0])
                    sg = math.exp(prff * al10) * fid
                    abso[ij] = abso[ij] + sg * abtra
                    emis[ij] = emis[ij] + sg * emtra
                # 50 CONTINUE
            else:
                i, j, izz, xkij, wl0, fij, fij0 = stark0(i, j, izz, 0.0, 0.0, 0.0, 0.0)
                fxk = f00 * xkij
                fxk1 = un / fxk
                dop = dop0 / wl0
                dbeta = wl0 * wl0 * cinv * fxk1
                C.DBETA = dbeta   # DBETA 属 COMMON /AUXHYD/（STARKIR 经 COMMON 读取）
                betad = dop * dbeta
                C.BETAD = betad   # BETAD 属 COMMON /AUXHYD/（DIVSTR/STARKA 经 COMMON 读取）
                fid = cid * fij * dbeta
                #           FID0=CID1*FIJ0/DOP
                ad, div = divhe2(0.0, 0.0)  # DIVHE2 修改标量哑元 A、DIV → 解包接收
                for ij in range(i0, i1 + 1):
                    beta = abs(C.WLAM[ij] - wl0) * fxk1
                    sg = starka(beta, ad, div, un) * fid
                    #              if(fid0.gt.0.) then
                    #                 xd=beta/betad
                    #                 if(xd.lt.5.) sg=sg+exp(-xd*xd)*fid0
                    #              end if
                    abso[ij] = abso[ij] + sg * abtra
                    emis[ij] = emis[ij] + sg * emtra
        # 100 CONTINUE
    # 200 CONTINUE
    #
    # ----------------------------
    # total opacity and emissivity
    # ----------------------------
    #
    for ij in range(i0, i1 + 1):
        f = C.FREQ[ij]
        f15 = f * 1.0e-15
        xkf = math.exp(-4.79928e-11 * f * t1)
        xkfb = xkf * 1.4743e-2 * f15 * f15 * f15
        absoh[ij] = abso[ij] - xkf * emis[ij]
        emish[ij] = xkfb * emis[ij]
    return


def he2liw(id, absoh, emish):
    """
C     opacity and emissivity of He II lines  (these which are not considered
C     explicitly)
    对应 synspec54.f 行 6451–6649
    """
    # PARAMETER (UN=1.,SIXTH=1./6.)
    un = 1.0
    sixth = 1.0 / 6.0
    # PARAMETER (CPP=4.1412E-16,CPJ=631479.)
    cpp = 4.1412e-16
    cpj = 631479.0
    # PARAMETER (C00=1.25E-9,CDOP=1.284523E12,CID=0.02654,TWO=2.)
    c00 = 1.25e-9
    cdop = 1.284523e12
    cid = 0.02654
    two = 2.0
    # PARAMETER (CPJ4=CPJ/4.,AL10=2.3025851,CINV=UN/2.997925E18)
    cpj4 = cpj / 4.0
    al10 = 2.3025851
    cinv = un / 2.997925e18
    # PARAMETER (CID1=0.01497)
    cid1 = 0.01497
    # DIMENSION PJ(80),FRHE(12),OSCHE2(19),PRF0(36),ABSO(MFREQ),EMIS(MFREQ),ABSOH(MFREQ),EMISH(MFREQ)
    pj = np.zeros(81)
    # DATA FRHE /.../（之后不再修改）
    frhe = np.zeros(13)
    frhe[1:] = [1.3158153e16, 3.2895381e15, 1.4624854e15,
                8.2261878e14, 5.2647201e14, 3.6560459e14,
                2.6860713e14, 2.0565220e14, 1.6249055e14,
                1.3161730e14, 1.0877460e14, 9.1400851e13]
    # DATA OSCHE2/.../（之后不再修改）
    osche2 = np.zeros(20)
    osche2[1:] = [6.407e-1, 1.506e-1, 5.584e-2, 2.768e-2,
                  1.604e-2, 1.023e-2, 6.980e-3,
                  8.421e-1, 3.230e-2, 1.870e-2, 1.196e-2, 8.187e-3,
                  5.886e-3, 4.393e-3, 3.375e-3, 2.656e-3,
                  1.038, 1.793e-1, 6.549e-2]
    prf0 = np.zeros(37)
    abso = np.zeros(MFREQ + 1)
    emis = np.zeros(MFREQ + 1)
    # COMMON/HE2PRF/PRFHE2(19,MDEPTH,36),WLHE2(19,36),NWLHE2(19),ILHE2(19),IUHE2(19)
    # common/lasers/lasdel
    #
    i = C.ILWHE2
    izz = 2
    for ij in range(1, NFREQ + 1):
        abso[ij] = 0.0
        emis[ij] = 0.0
        absoh[ij] = 0.0
        emish[ij] = 0.0
    if C.IFHE2 <= 0:
        return
    t = C.TEMP[id]
    t1 = un / t
    sqt = math.sqrt(t)
    ane = C.ELEC[id]
    anes = math.exp(sixth * math.log(ane))
    #
    # He III populations (either LTE or NLTE, depending on input model)
    #
    if C.IELHE2 > 0:
        anp = C.POPUL[C.NNEXT[C.IELHE2], id]
        nlhe2 = C.NLAST[C.IELHE2] - C.NFIRST[C.IELHE2] + 1
    else:
        anp = C.RRR[id, 3, 2]
        nlhe2 = 0
    #
    # populations of the first 60 levels of He II
    #
    pp = cpp * ane * anp * t1 / sqt
    for il in range(1, 61):
        x = il * il
        iil = C.NFIRST[C.IELHE2] + il - 1
        if il <= nlhe2:
            pj[il] = C.POPUL[iil, id]
        if il > nlhe2:
            pj[il] = pp * math.exp(cpj / x * t1) * x * C.WNHE2[il, id]
    #
    # Frequency- and line-independent parameters for evaluating the
    # asymptotic Stark profile
    #
    f00 = 3.906e-11 * anes * anes * anes * anes
    dop0 = 1.0e8 * math.sqrt(4.12e7 * t + C.VTURB[id])
    #
    # -------------------------------------------------------------------
    # overall loop over spectral series (only in the infrared region)
    # -------------------------------------------------------------------
    #
    # DO 300 IJ=1,NFREQ
    for ij in range(1, NFREQ + 1):
        abso[ij] = 0.0
        emis[ij] = 0.0
        if C.IHE2LW[ij] <= 0:
            continue  # GO TO 300
        i = C.ILWHEW[ij]
        fr = C.FREQ[ij]
        iseru = C.ILWHEW[ij]
        if C.ILWHEW[ij] <= 3:
            iserl = C.ILWHEW[ij]
        elif C.ILWHEW[ij] <= 5:
            iserl = C.ILWHEW[ij] - 1
        elif C.ILWHEW[ij] <= 7:
            iserl = C.ILWHEW[ij] - 2
        elif C.ILWHEW[ij] <= 9:
            iserl = C.ILWHEW[ij] - 3
        else:
            iserl = C.ILWHEW[ij] - 4
        #
        #
        # DO 200 I=ISERL,ISERU
        for i in range(iserl, iseru + 1):
            ii = i * i
            xii = un / ii
            pltei = pp * math.exp(cpj * t1 * xii) * ii
            popi = pj[i]
            #
            # determination of which He II lines contribute in a current
            # frequency region
            #
            m1 = C.MHE10W[ij]
            if i < C.ILWHEW[ij] and frhe[i] > fr:
                m1 = int(math.sqrt(frhe[i] * ii / (frhe[i] - fr)))
            m2 = m1 + 1
            if m1 < i + 1:
                m1 = i + 1
            # IF(grav.lt.6..and.M1.LE.6.AND.I.EQ.2) GO TO 10（及下一条）的逆分支
            _goto10 = C.GRAV < 6.0 and ((m1 <= 6 and i == 2) or (m1 <= 4 and i == 1))
            if not _goto10:
                m1 = m1 - 1
                m2 = C.MHE20W[ij] + 3
                if m2 > 60:
                    m2 = 60
            # 标号 10
            if C.GRAV > 6.0:
                m2 = m2 + 5
                m1 = m1 - 3
                if m1 > i + 6:
                    m1 = m1 - 3
            if m1 < i + 1:
                m1 = i + 1
            if m2 > 60:
                m2 = 60
            #
            # loop over lines which contribute at given wavelength region
            #
            # DO 100 J=M1,M2
            for j in range(m1, m2 + 1):
                iline = 0
                jj = j * j
                xjj = un / jj
                abtra = pj[i] * C.WNHE2[j, id]
                emtra = pj[j] * C.WNHE2[i, id] * ii * xjj * math.exp(cpj * (xii - xjj) * t1)
                if i <= 2:
                    wlin = 227.838 / (xii - 1.0 / jj)
                else:
                    wlin = 227.7776 / (xii - 1.0 / jj)
                if i == 2:
                    if j == 3 and C.IHE2PR > 0:
                        iline = 1
                elif i == 3:
                    if j == 4 and C.IHE2PR > 0:
                        iline = 8
                    if j > 5 and j <= 10 and C.IHE2PR > 0:
                        iline = j - 3
                elif i == 4:
                    if j <= 7 and C.IHE2PR > 0:
                        iline = j + 12
                    if j >= 8 and j <= 15 and C.IHE2PR > 0:
                        iline = j + 1
                if iline > 0:
                    nwl = C.NWLHE2[iline]
                    for iwl in range(1, nwl + 1):
                        prf0[iwl] = C.PRFHE2[iline, id, iwl]
                    fid = cid * osche2[iline]
                    al = abs(C.WLAM[ij] - wlin)
                    if al < 1.0e-4:
                        al = 1.0e-4
                    al = math.log10(al)
                    # DO IWL=1,NWL-1 ... GO TO 40
                    for iwl in range(1, nwl):
                        iw0 = iwl
                        if al <= C.WLHE2[iline, iwl + 1]:
                            break  # GO TO 40
                    # 标号 40
                    iw1 = iw0 + 1
                    prff = (prf0[iw0] * (C.WLHE2[iline, iw1] - al) + prf0[iw1] *
                            (al - C.WLHE2[iline, iw0])) / \
                           (C.WLHE2[iline, iw1] - C.WLHE2[iline, iw0])
                    sg = math.exp(prff * al10) * fid
                    abso[ij] = abso[ij] + sg * abtra
                    emis[ij] = emis[ij] + sg * emtra
                else:
                    i, j, izz, xkij, wl0, fij, fij0 = stark0(i, j, izz, 0.0, 0.0, 0.0, 0.0)
                    fxk = f00 * xkij
                    fxk1 = un / fxk
                    dop = dop0 / wl0
                    dbeta = wl0 * wl0 * cinv * fxk1
                    C.DBETA = dbeta   # DBETA 属 COMMON /AUXHYD/（STARKIR 经 COMMON 读取）
                    betad = dop * dbeta
                    C.BETAD = betad   # BETAD 属 COMMON /AUXHYD/（DIVSTR/STARKA 经 COMMON 读取）
                    fid = cid * fij * dbeta
                    ad, div = divhe2(0.0, 0.0)  # DIVHE2 修改标量哑元 A、DIV → 解包接收
                    beta = abs(C.WLAM[ij] - wl0) * fxk1
                    sg = starka(beta, ad, div, un) * fid
                    abso[ij] = abso[ij] + sg * abtra
                    emis[ij] = emis[ij] + sg * emtra
            # 100 CONTINUE
        # 200 CONTINUE
        #
        # ----------------------------
        # total opacity and emissivity
        # ----------------------------
        #
        f = C.FREQ[ij]
        f15 = f * 1.0e-15
        xkf = math.exp(-4.79928e-11 * f * t1)
        xkfb = xkf * 1.4743e-2 * f15 * f15 * f15
        absoh[ij] = abso[ij] - xkf * emis[ij]
        emish[ij] = xkfb * emis[ij]
    # 300 CONTINUE
    return


def stark0(i, j, izz, xkij, wl0, fij, fij0):
    """
C     Auxiliary procedure for evaluating the approximate Stark profile
C     of hydrogen lines - sets up necessary frequency independent
C     parameters
C
C     Input:  I     - principal quantum number of the lower level
C             J     - principal quantum number of the upper level
C             IZZ   - ionic charge (IZZ=1 for hydrogen, etc.)
C     Output: XKIJ  - coefficients K(i,j) for the Hotzmark profile;
C                     exact up to j=6, asymptotic for higher j
C             WL0   - wavelength of the line i-j
C             FIJ   - Stark f-value for the line i-j
C             FIJ0  - f-value for the undisplaced component of the line
    对应 synspec54.f 行 6650–6742

    修改标量哑元 XKIJ/WL0/FIJ/FIJ0 → 按约定返回全部标量哑元
    """
    # PARAMETER (RYD1=911.763811,RYD2=911.495745,CXKIJ=5.5E-5)
    ryd1 = 911.763811
    ryd2 = 911.495745
    cxkij = 5.5e-5
    # PARAMETER (WI1=911.753578, WI2=227.837832)
    wi1 = 911.753578
    wi2 = 227.837832
    # PARAMETER (UN=1.,TEN=10.,TWEN=20.,HUND=100.)
    un = 1.0
    ten = 10.0
    twen = 20.0
    hund = 100.0
    # DIMENSION FSTARK(10,4),XKIJT(5,4),FOSC0(10,4),FADD(5,5)
    # DATA XKIJT/.../（Fortran 按列填充；之后不再修改）
    xkijt = np.zeros((6, 5))
    xkijt[1:6, 1] = [3.56e-4, 5.23e-4, 1.09e-3, 1.49e-3, 2.25e-3]
    xkijt[1:6, 2] = [0.0125, 0.0177, 0.028, 0.0348, 0.0493]
    xkijt[1:6, 3] = [0.124, 0.171, 0.223, 0.261, 0.342]
    xkijt[1:6, 4] = [0.683, 0.866, 1.02, 1.19, 1.46]
    # DATA FSTARK/.../
    fstark = np.zeros((11, 5))
    fstark[1:11, 1] = [0.1387, 0.0791, 0.02126, 0.01394, 0.00642,
                       4.814e-3, 2.779e-3, 2.216e-3, 1.443e-3, 1.201e-3]
    fstark[1:11, 2] = [0.3921, 0.1193, 0.03766, 0.02209, 0.01139,
                       8.036e-3, 5.007e-3, 3.85e-3, 2.658e-3, 2.151e-3]
    fstark[1:11, 3] = [0.6103, 0.1506, 0.04931, 0.02768, 0.01485,
                       0.01023, 6.588e-3, 4.996e-3, 3.524e-3, 2.838e-3]
    fstark[1:11, 4] = [0.8163, 0.1788, 0.05985, 0.03189, 0.01762,
                       0.01196, 7.825e-3, 5.882e-3, 4.233e-3, 3.375e-3]
    # DATA FOSC0/.../
    fosc0 = np.zeros((11, 5))
    fosc0[1:11, 1] = [0.27746, 0.0, 0.00773, 0.0, 0.00134, 0.0,
                      0.000404, 0.0, 0.000162, 0.0]
    fosc0[1:11, 2] = [0.24869, 0.0, 0.00701, 0.0, 0.00131, 0.0,
                      0.000422, 0.0, 0.000177, 0.0]
    fosc0[1:11, 3] = [0.23175, 0.0, 0.00653, 0.0, 0.00118, 0.0,
                      0.000392, 0.0, 0.000169, 0.0]
    fosc0[1:11, 4] = [0.22148, 0.0005, 0.00563, 0.0004, 0.00108, 0.0,
                      0.000362, 0.0, 0.000159, 0.0]
    # DATA FADD/.../
    fadd = np.zeros((6, 6))
    fadd[1:6, 1] = [1.231, 0.2069, 7.448e-2, 3.645e-2, 2.104e-2]
    fadd[1:6, 2] = [1.424, 0.2340, 8.315e-2, 4.038e-2, 2.320e-2]
    fadd[1:6, 3] = [1.616, 0.2609, 9.163e-2, 4.416e-2, 2.525e-2]
    fadd[1:6, 4] = [1.807, 0.2876, 1.000e-1, 4.787e-2, 2.724e-2]
    fadd[1:6, 5] = [1.999, 0.3143, 1.083e-1, 5.152e-2, 2.918e-2]
    #
    ii = i * i
    jj = j * j
    jmin = j - i
    if jmin <= 5 and i <= 4:
        xkij = xkijt[jmin, i]
    else:
        xkij = cxkij * (ii * jj) * (ii * jj) / (jj - ii)
    if i <= 4:
        if jmin <= 10:
            fij = fstark[jmin, i]
            fij0 = fosc0[jmin, i]
        else:
            cfij = ((twen * i + hund) * j / (i + ten) / (jj - ii))
            fij = fstark[10, i] * cfij * cfij * cfij
            fij0 = 0.0
    elif i <= 9:
        if jmin <= 5:
            fij = fadd[jmin, i - 4]
            fij0 = 0.0
        else:
            cfij = ((ten * i + 25.0) * j / (i + 5.0) / (jj - ii))
            fij = fadd[5, i - 4] * cfij * cfij * cfij
            fij0 = 0.0
    else:
        cfij = un * j / (jj - ii)
        fij = 1.96 * i * cfij * cfij * cfij
        fij0 = 0.0
    #
    # wavelength with an explicit correction to the air wavalength
    #
    w0 = wi1
    if izz == 2:
        w0 = wi2
    wl0 = w0 / (un / ii - un / jj)
    if wl0 > C.vaclim:
        alm = 1.0e8 / (wl0 * wl0)
        xn1 = 64.328 + 29498.1 / (146.0 - alm) + 255.4 / (41.0 - alm)
        wl0 = wl0 / (xn1 * 1.0e-6 + un)
    return i, j, izz, xkij, wl0, fij, fij0


def starka(beta, a, div, fac):
    """
C     Approximate expressions for the hydrogen Stark profile
C
C     Input: BETA  - delta lambda in beta units,
C            BETAD - Doppler width in beta units
C            A     - auxiliary parameter
C                    A=1.5*LOG(BETAD)-1.671
C            DIV   - only for A > 1; division point between Doppler
C                    and asymptotic Stark wing, expressed in units
C                    of betad.
C                    DIV = solution of equation
C                    exp(-(beta/betad)**2)/betad/sqrt(pi)=
C                     = 1.5*FAC*beta**-5/2
C                    (ie. the point where Doppler profile is equal to
C                     the asymptotic Holtsmark)
C                    In order to save computer time, the division point
C                    DIV is calculated in advance by routine DIVSTR.
C            FAC   - factor by which the Holtsmark profile is to be
C                    multiplied to get total Stark Profile
C                    FAC should be taken to 2 for hydrogen, (and =1
C                    for He II)
    对应 synspec54.f 行 6743–6800

    注：BETAD 不是哑元，而是 COMMON 变量（C.BETAD）。
    """
    # PARAMETER (F0=-0.5758228,F1=0.4796232,F2=0.07209481/2.,AL=1.26)
    f0 = -0.5758228
    f1 = 0.4796232
    f2 = 0.07209481 / 2.0
    al = 1.26
    # PARAMETER (SD=0.5641895,SLO=-2.5,TRHA=1.5,BL1=1.52,BL2=8.325)
    sd = 0.5641895
    slo = -2.5
    trha = 1.5
    bl1 = 1.52
    bl2 = 8.325
    # PARAMETER (SAC=0.07966/2.)
    sac = 0.07966 / 2.0
    xd = beta / C.BETAD
    #
    # for a > 1 Doppler core + asymptotic Holtzmark wing with division
    #           point DIV
    #
    if a > al:
        if xd <= div:
            starka_v = sd * math.exp(-xd * xd) / C.BETAD
        else:
            starka_v = trha * fac * math.exp(slo * math.log(beta))
    else:
        #
        # empirical formula for a < 1
        #
        if beta <= bl1:
            starka_v = sac * fac
        elif beta < bl2:
            xl = math.log(beta)
            fl = (f0 * xl + f1) * xl
            starka_v = f2 * fac * math.exp(fl)
        else:
            starka_v = trha * fac * math.exp(slo * math.log(beta))
    return starka_v


def starkir(ii, jj, t, ane, beta):
    """
    （无原 Fortran 头注释）
    对应 synspec54.f 行 6801–6839
    """
    # PARAMETER (PI=3.14159265,PI2=2.*PI,OS0=0.026564,RYD=3.28805E15,
    #            Y2CON=PI*PI*0.5/OS0/CL)
    pi = 3.14159265
    pi2 = 2.0 * pi
    os0 = 0.026564
    ryd = 3.28805e15
    y2con = pi * pi * 0.5 / os0 / CL
    #
    del_l = beta / C.DBETA  # 原变量名 DEL；避免与内建 del 混淆加 _l
    hkt = HK / t
    xii = ii
    xjj = jj
    xx = xii / xjj
    dd = 2.0 * xjj * ryd / del_l
    y1 = xjj * del_l * 0.5 * hkt
    y2 = y2con * del_l ** 2 / ane
    qstat = 1.5 + 0.5 * (y1 ** 2 - 1.384) / (y1 ** 2 + 1.384)
    qimpa = 0.0
    # IF(Y1.GT.8..OR.Y1.GE.Y2) GO TO 10 的逆分支
    if not (y1 > 8.0 or y1 >= y2):
        exy2 = 0.0
        if y2 <= 8.0:
            exy2 = expint(y2)
        qimpa = 1.438 * math.sqrt(y1 * (1.0 - xx)) * (0.4 * math.exp(-y1) + expint(y1) - 0.5 * exy2)
    # 标号 10
    # TODO(port): QIMPT 在 Fortran 中从未赋值（隐式 REAL*8 未定义局部量），此处按 0.0 处理
    qimpt = 0.0
    if beta > 20.0:
        # GO TO 20
        prof = 1.5 / beta / beta / math.sqrt(beta)
        dioi = pi2 * 1.48e-25 * dd * ane * (math.sqrt(dd) *
               (1.3 * qstat + 0.3 * qimpt) - 3.9 * ryd * hkt)
        ratio = qstat * min(1.0 + dioi, 1.25) + qimpa
    else:
        prof = 8.0 / (80.0 + beta ** 3)
        ratio = qstat + qimpa
    # 标号 30
    starkir_v = prof * ratio
    return starkir_v


def divstr(a, div):
    """
C     Auxiliary procedure for STARKA - determination of the division
C     point between Doppler and asymptotic Stark profiles
C
C     Input:  BETAD - Doppler width in beta units
C     Output: A     - auxiliary parameter
C                     A=1.5*LOG(BETAD)-1.671
C             DIV   - only for A > 1; division point between Doppler
C                     and asymptotic Stark wing, expressed in units
C                     of betad.
C                     DIV = solution of equation
C                     exp(-(beta/betad)**2)/betad/sqrt(pi)=3*beta**-5/2
    对应 synspec54.f 行 6840–6876

    修改标量哑元 A、DIV → 按约定返回全部标量哑元
    注：BETAD 不是哑元，而是 COMMON 变量（C.BETAD）。
    """
    # PARAMETER (UN=1.,TWO=2.,UNQ=1.25,UNH=1.5,TWH=2.5,FO=4.,FI=5.)
    un = 1.0
    two = 2.0
    unq = 1.25
    unh = 1.5
    twh = 2.5
    fo = 4.0
    fi = 5.0
    # PARAMETER (CA=1.671,BL=5.821,AL=1.26,CX=0.28,DX=0.0001)
    ca = 1.671
    bl = 5.821
    al = 1.26
    cx = 0.28
    dx = 0.0001
    #
    a = unh * math.log(C.BETAD) - ca
    if C.BETAD < bl:
        return a, div
    if a >= al:
        x = math.sqrt(a) * (un + unq * math.log(a) / (fo * a - fi))
    else:
        x = math.sqrt(cx + a)
    # DO I=1,5 ... GO TO 20
    for i in range(1, 6):
        xn = x * (un - (x * x - twh * math.log(x) - a) / (two * x * x - twh))
        if abs(xn - x) <= dx:
            break  # GO TO 20（注意：跳出前不执行 X=XN，DIV 取旧 X）
        x = xn
    # 标号 20
    div = x
    return a, div
