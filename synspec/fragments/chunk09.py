# chunk09: synspec54.f 行 9867–11047 的逐行直译
# 包含: NLTSET, PHTION, NLTE, LINOP, LINOPW, PROFIL, GRIEM, GAMHE, EPS, XK2DOP


def nltset(mode, il, iat, ion, alam0, excl, excu, ql, qu,
           isql, ilql, ipql, isqu, ilqu, ipqu, ieven, innlt0, ilmatch):
    """NLTE option -  automatic assignement of level indices

    对应 synspec54.f 行 9867–10269。
    标量哑元 IEVEN/INNLT0/ILMATCH 在体内被赋值, 按约定 return 全部 18 个
    标量哑元(按哑元声明顺序), 调用点须解包接收。
    """
    # PARAMETER (MNION = MIOEX, MNLEV = MLEVEL, ECONST= 5.03411142E15)
    # PARAMETER (INLLEV = 13)
    econst = 5.03411142e15
    inllev = 13
    # character*2 typin(60)
    # DATA typin /' 1',' 2',' 3',...,'60'/  (DATA 后不再修改)
    typin = [''] + [(' ' + str(k)) if k < 10 else str(k) for k in range(1, 61)]

    # +++++++++++++++++++++++++++
    # MODE = 0  -  initialization
    # +++++++++++++++++++++++++++
    if mode == 0:
        C.NNION = 0
        # READ(INLLEV,*,END=55,ERR=55) NNION
        _end55 = False
        try:
            C.NNION = int(read_line(inllev).split()[0])
        except (EOFError, ValueError, IndexError):
            _end55 = True            # END=55 / ERR=55 → 转到标号 55
        # IF(NNION.LE.0) GO TO 55
        if not _end55 and C.NNION > 0:
            for i in range(1, C.NNION + 1):
                # READ(INLLEV,*) IATN(I),IONN(I)
                _tok = read_line(inllev).split()
                C.IATN[i] = int(_tok[0])
                C.IONN[i] = int(_tok[1])
                # READ(INLLEV,*) NEVEN(I)
                C.NEVEN[i] = int(read_line(inllev).split()[0])
                if C.NEVEN[i] > 0:
                    for j in range(1, C.NEVEN[i] + 1):
                        # READ(INLLEV,*) ELIMEV(I,J)
                        C.ELIMEV[i, j] = float(read_line(inllev).split()[0])
                    # READ(INLLEV,*) NODD(I)
                    C.NODD[i] = int(read_line(inllev).split()[0])
                    C.NODD0 = C.NODD[i]
                    if C.NODD[i] > 0:
                        for j in range(1, C.NODD[i] + 1):
                            # READ(INLLEV,*) ELIMOD(I,J)
                            C.ELIMOD[i, j] = float(read_line(inllev).split()[0])
                    else:
                        C.NODD[i] = C.NEVEN[i]
                        for j in range(1, C.NODD[i] + 1):
                            C.ELIMOD[i, j] = C.ELIMEV[i, j]
                    indion = 0
                    for ionex in range(1, C.NION + 1):
                        n0i = C.NFIRST[ionex]
                        ia = C.NUMAT[C.IATM[n0i]]
                        if ia == C.IATN[i] and C.IZ[ionex] - 1 == C.IONN[i]:
                            indion = ionex
                    if indion <= 0:
                        quit(' INCONSISTENCY IN UNIT 13 INPUT - NLTE')
                    noff = C.NFIRST[indion] - 1   # 赋值后未再使用
                    ine = 1
                    ino = 1
                    for ii in range(C.NFIRST[indion], C.NLAST[indion] + 1):
                        typ = C.TYPLEV[ii]
                        typ1 = typ[1:5]          # typ(2:5)
                        typ2 = typ[7:9]          # typ(8:9)
                        iev = 0
                        if feq(typ1, 'even'):
                            iev = 1
                        ind = 0   # TODO(port): Fortran 未初始化 IND, 且之后未使用(死变量)
                        for k in range(1, 61):
                            if feq(typin[k], typ2):
                                ind = k
                        if iev == 1:
                            C.INDEV[i, ine] = ii
                            # write(11,*) 'super-e ',i,ii,ine,elimev(i,ine)
                            write_line(11, 'super-e  %d %d %d %g'
                                       % (i, ii, ine, C.ELIMEV[i, ine]))
                            ine += 1
                        else:
                            C.INDOD[i, ino] = ii
                            # write(11,*) 'super-o ',i,ii,ino,elimod(i,ino)
                            write_line(11, 'super-o  %d %d %d %g'
                                       % (i, ii, ino, C.ELIMOD[i, ino]))
                            ino += 1

        # 55 CONTINUE

        indion = C.NNION
        for ionex in range(1, C.NION + 1):      # DO 90
            n0i = C.NFIRST[ionex]
            ia = C.NUMAT[C.IATM[n0i]]
            if C.isemex[ia] >= 1:
                continue                        # GO TO 90
            ionm1 = C.IZ[ionex] - 1
            if ia == 1 or ia == 2:
                continue                        # GO TO 90
            _skip90 = False
            for i in range(1, C.NNION + 1):
                if ia == C.IATN[i] and ionm1 == C.IONN[i]:
                    _skip90 = True
                    break                       # GO TO 90
            if _skip90:
                continue
            if C.NFIRST[ionex] == C.NLAST[ionex]:
                continue                        # GO TO 90
            indion += 1
            eion = C.ENION[C.NFIRST[ionex]]
            C.NLEVS[indion] = C.NLAST[ionex] - C.NFIRST[ionex] + 1
            C.INDIO[indion] = ionex
            C.NEVEN[indion] = 0
            C.IATN[indion] = ia
            C.IONN[indion] = ionm1
            dele = 0.
            for ii in range(C.NFIRST[ionex], C.NLAST[ionex] + 1):
                i = ii - C.NFIRST[ionex] + 1
                e = (eion - C.ENION[ii]) * econst
                if ii < C.NLAST[ionex]:
                    e1 = (eion - C.ENION[ii + 1]) * econst
                    dele = 0.5 * (e1 - e)
                    C.ELIML[indion, i] = e + dele
                else:
                    if C.INLTE >= 2:
                        C.ELIML[indion, i] = e + dele
                    else:
                        C.ELIML[indion, i] = eion * econst
                C.INDLV[indion, i] = ii
        # 90 CONTINUE 循环结束
        C.NNION = indion

        # Header for the table with the level assignments
        if C.INLTE > 0 and C.IPRIN >= 1:
            # WRITE(11,*)'NLTSET: IAT ION      LAMBDA     EXCL '//
            #  '      EXCU    ILWN  IUN'
            write_line(11, 'NLTSET: IAT ION      LAMBDA     EXCL '
                           '      EXCU    ILWN  IUN')

        return (mode, il, iat, ion, alam0, excl, excu, ql, qu,
                isql, ilql, ipql, isqu, ilqu, ipqu, ieven, innlt0, ilmatch)

    # ++++++++++++++++++++++++++++++++++++++++++
    # MODE > 0  -  level indices for the line IL
    # ++++++++++++++++++++++++++++++++++++++++++

    if C.NNION <= 0:
        return (mode, il, iat, ion, alam0, excl, excu, ql, qu,
                isql, ilql, ipql, isqu, ilqu, ipqu, ieven, innlt0, ilmatch)
    inion = 0
    ionm1 = ion - 1
    for i in range(1, C.NNION + 1):
        if iat == C.IATN[i] and ionm1 == C.IONN[i]:
            inion = i
    if C.isemex[iat] >= 1:
        return (mode, il, iat, ion, alam0, excl, excu, ql, qu,
                isql, ilql, ipql, isqu, ilqu, ipqu, ieven, innlt0, ilmatch)
    if inion <= 0:
        return (mode, il, iat, ion, alam0, excl, excu, ql, qu,
                isql, ilql, ipql, isqu, ilqu, ipqu, ieven, innlt0, ilmatch)
    if C.NEVEN[inion] == 0:
        ieven = 2
    # TODO(port): Fortran 局部变量跨调用静态保留; 个别路径下 ILWN/IUN 未赋值
    # 即被使用(如无匹配时 GO TO 145/200 跳过后续), 这里统一先初始化为 0
    ilwn = 0
    iun = 0
    inmatchl = 0
    inmatchu = 0
    # IF(NEVEN(INION).LT.0) GOTO 400 → 整个 IEVEN 分支块仅当 NEVEN>=0 执行
    if C.NEVEN[inion] >= 0:

        if ieven == 1:
            ind = 0
            _found = False
            for j in range(1, C.NEVEN[inion] + 1):      # DO 110
                if excl <= C.ELIMEV[inion, j]:
                    ind = j
                    _found = True
                    break                               # GO TO 120
            if not _found:
                ilwn = 0
                # GO TO 145 → 跳过 IUN 的搜索
            else:
                # 120 CONTINUE
                ilwn = C.INDEV[inion, ind]

                ind = 0
                _found = False
                for j in range(1, C.NODD[inion] + 1):   # DO 130
                    if excu <= C.ELIMOD[inion, j]:
                        ind = j
                        _found = True
                        break                           # GO TO 140
                if not _found:
                    iun = 0
                else:
                    # 140 CONTINUE
                    iun = C.INDOD[inion, ind]
            # 145 CONTINUE

        elif ieven == 0:
            ind = 0
            _found = False
            for j in range(1, C.NODD[inion] + 1):       # DO 150
                if excl <= C.ELIMOD[inion, j]:
                    ind = j
                    _found = True
                    break                               # GO TO 160
            if not _found:
                ilwn = 0
                # GO TO 200 → 跳过 IUN 的搜索
            else:
                # 160 CONTINUE
                ilwn = C.INDOD[inion, ind]

                ind = 0
                _found = False
                for j in range(1, C.NEVEN[inion] + 1):  # DO 170
                    if excu <= C.ELIMEV[inion, j]:
                        ind = j
                        _found = True
                        break                           # GO TO 180
                if not _found:
                    iun = 0
                else:
                    # 180 CONTINUE
                    iun = C.INDEV[inion, ind]
            # 200 CONTINUE

        else:
            # transition between levels without a distinction in parity

            if C.ILIMITS[C.INDIO[inion]] == 0 or C.INLIST >= 10:
                # level identification: using only energy limits

                ind = 0
                _found = False
                for j in range(1, C.NLEVS[inion] + 1):  # DO 210
                    if excl <= C.ELIML[inion, j]:
                        ind = j
                        _found = True
                        break                           # GO TO 220
                if not _found:
                    ilwn = 0
                    iun = 0
                    # GO TO 300 → 跳过 IUN 的搜索
                else:
                    # 220 CONTINUE
                    ilwn = C.INDLV[inion, ind]

                    ind = 0
                    _found = False
                    for j in range(1, C.NLEVS[inion] + 1):  # DO 230
                        if excu <= C.ELIML[inion, j]:
                            ind = j
                            _found = True
                            break                       # GO TO 240
                    if not _found:
                        iun = 0
                    else:
                        # 240 CONTINUE
                        iun = C.INDLV[inion, ind]
                # 300 CONTINUE

            elif C.ILIMITS[C.INDIO[inion]] == 1 and C.INLIST < 10:

                # level identification: using energy limits and quantum numbers

                ind = 0
                inmatchl = 0
                for j in range(1, C.NLEVS[inion] + 1):  # DO 310
                    _lv = C.INDLV[inion, j]
                    if (excl >= C.ENION1[_lv] and excl <= C.ENION2[_lv]
                            and ((ipql >= C.PQUANT1[_lv]
                                  and ipql <= C.PQUANT2[_lv]) or ipql == -1)
                            and ((isql >= C.SQUANT1[_lv]
                                  and isql <= C.SQUANT2[_lv]) or isql == -1)
                            and ((ilql >= C.LQUANT1[_lv]
                                  and ilql <= C.LQUANT2[_lv]) or ilql == -1)):
                        ind = j
                        inmatchl += 1
                        # GO TO 320(原代码中被注释掉)
                if inmatchl > 1:
                    # FORMAT '(A55,1X,F12.4)'
                    write_line(11, ' NLTSET: WARNING-- multiple matches for '
                                   'lower level of  %12.4f' % alam0)
                if inmatchl > 0:            # GO TO 320
                    # 320 CONTINUE
                    ilwn = C.INDLV[inion, ind]

                    ind = 0
                    inmatchu = 0
                    for j in range(1, C.NLEVS[inion] + 1):  # DO 330
                        _lv = C.INDLV[inion, j]
                        if (excu >= C.ENION1[_lv] and excu <= C.ENION2[_lv]
                                and ((ipqu >= C.PQUANT1[_lv]
                                      and ipqu <= C.PQUANT2[_lv]) or ipqu == -1)
                                and ((isqu >= C.SQUANT1[_lv]
                                      and isqu <= C.SQUANT2[_lv]) or isqu == -1)
                                and ((ilqu >= C.LQUANT1[_lv]
                                      and ilqu <= C.LQUANT2[_lv]) or ilqu == -1)):
                            ind = j
                            inmatchu += 1
                            # GO TO 340(原代码中被注释掉)
                    if inmatchu > 1:
                        # FORMAT '(A55,1X,F12.4)'
                        write_line(11, ' NLTSET: WARNING-- multiple matches for '
                                       'upper level of  %12.4f' % alam0)
                    if inmatchu > 0:        # GO TO 340
                        # 340 CONTINUE
                        iun = C.INDLV[inion, ind]
                    else:
                        iun = 0
                else:
                    ilwn = 0
                    iun = 0
                    # GO TO 350 → 跳过上限搜索
                # 350 CONTINUE

                if inmatchl == 0 or inmatchu == 0:
                    ilmatch = 0
                elif inmatchl > 1 or inmatchu > 1:
                    ilmatch = 2
                else:
                    ilmatch = 1

            else:

                # write(11,*)('ILIMITS is neither 0 or 1')
                write_line(11, 'ILIMITS is neither 0 or 1')

            if C.INLTE > 0 and C.IPRIN >= 1:
                # FORMAT '(10x,2(i2,1x),3x,3(F10.3,1x),2(i4,1x))'
                write_line(11, '%10s%2d %2d   %10.3f %10.3f %10.3f %4d %4d'
                           % ('', iat, ion, alam0, excl, excu, ilwn, iun))

    # 400
    if C.NEVEN[inion] < 0:
        nev1 = -C.NEVEN[inion]
        if ieven == 1:
            ilwn = 0
            j = 1
            while ilwn == 0 and j <= nev1:
                if ql == C.ELIMEV[inion, j]:
                    de = C.ENREV[inion, j]
                    if excl != 0.:
                        de = (excl - de) / excl
                    if abs(de) < 1.e-5:
                        ilwn = C.INDEV[inion, j]
                j += 1
            iun = 0
            j = 1
            while iun == 0 and j <= C.NODD[inion]:
                if qu == C.ELIMOD[inion, j]:
                    de = (excu - C.ENROD[inion, j]) / excu
                    if abs(de) < 1.e-5:
                        iun = C.INDOD[inion, j]
                j += 1
        elif ieven == 0:
            ilwn = 0
            j = 1
            while ilwn == 0 and j <= C.NODD[inion]:
                if ql == C.ELIMOD[inion, j]:
                    de = C.ENROD[inion, j]
                    if excl != 0.:
                        de = (excl - de) / excl
                    if abs(de) < 1.e-5:
                        ilwn = C.INDOD[inion, j]
                j += 1
            iun = 0
            j = 1
            while iun == 0 and j <= nev1:
                if qu == C.ELIMEV[inion, j]:
                    de = (excu - C.ENREV[inion, j]) / excu
                    if abs(de) < 1.e-5:
                        iun = C.INDEV[inion, j]
                j += 1

    if C.INLTE == 5:
        innlt0 += 1
        C.INDNLT[il] = innlt0
    elif C.INLTE == 4:
        if ilwn > 0 and iun > 0:
            C.INDNLT[il] = -1
    elif C.INLTE == 3:
        if ilwn > 0:
            C.INDNLT[il] = -1
    else:
        C.INDNLT[il] = -1
    # BNUL(IL)=real(BN*(FREQ0(IL)*1.E-15)**3) —— real 即 SNGL → float
    C.BNUL[il] = float(BN * (C.FREQ0[il] * 1.e-15) ** 3)
    C.ILOWN[il] = ilwn
    C.IUPN[il] = iun
    return (mode, il, iat, ion, alam0, excl, excu, ql, qu,
            isql, ilql, ipql, isqu, ilqu, ipqu, ieven, innlt0, ilmatch)


def phtion(id, abso, emis, fre, nfre):
    """Opacity due to detailed photoionization (read from tables by
    routine READPH)

    对应 synspec54.f 行 10276–10321。
    标量哑元 ID/NFRE 不被修改, 数组 ABSO/EMIS 就地累加, 无返回值。
    """
    # PARAMETER (C3=1.4387886)
    c3 = 1.4387886
    # DIMENSION PLANF(MFRQ),STIMU(MFRQ) —— 局部数组, 1 基索引
    planf = np.zeros(MFRQ + 1)
    stimu = np.zeros(MFRQ + 1)

    if C.NPHT <= 0:
        return
    t = C.TEMP[id]
    for ij in range(1, nfre + 1):            # DO 10
        xx = fre[ij]
        x15 = xx * 1.e-15
        bnu = BN * x15 * x15 * x15
        hkf = HK * xx
        exh = math.exp(hkf / t)
        planf[ij] = bnu / (exh - 1.)
        stimu[ij] = 1. - 1. / exh
    # 10 CONTINUE
    for i in range(1, C.NPHT + 1):           # DO 30
        if C.JPHT[i] <= 0:
            iat = int(C.APHT[i])             # Fortran INT, 向零截断
            x = (C.APHT[i] - float(iat) + 1.e-4) * 1.e2
            ion = int(x) + 1
            pop = C.RRR[id, ion, iat] * C.GPHT[i] * math.exp(-C.EPHT[i] * c3 / t)
        else:
            jj = C.JPHT[i]
            pop = C.POPUL[jj, id]
        for ij in range(1, nfre + 1):        # DO 20
            ab = C.PHOT[ij, i] * pop * stimu[ij]
            abso[ij] += ab
            emis[ij] += ab * planf[ij]
    # 20/30 CONTINUE
    return


def nlte(il, ilw, iun, gi, gj):
    """Control procedure for the NLTE option

    对应 synspec54.f 行 10327–10421。
    标量哑元均不被修改, 无返回值。
    """
    # PARAMETER (UN=1., C3=1.4387886, XET=8067.6, XET3=XET*C3)
    un = 1.
    c3 = 1.4387886
    xet = 8067.6
    xet3 = xet * c3

    # CALCULATION OF THE
    # CENTRAL OPACITY (ABCENT) AND THE LINE SOURCE FUNCTION  (SLIN)

    if gi <= 0. or gj <= 0.:
        return
    ilnlt = C.INDNLT[il]
    if ilnlt <= 0:
        return
    iat = idiv(C.INDAT[il], 100)             # Fortran 整数除法
    ion = imod(C.INDAT[il], 100)
    egf = math.exp(C.GF0[il])
    bnu = BN * (C.FREQ0[il] * 1.e-15) ** 3
    dp0 = 3.33564e-11 * C.FREQ0[il]
    dp1 = 1.651e8 / C.AMAS[iat]
    # IF(ILW.LE.0) GO TO 100
    if ilw > 0:

        # line is a transition between explicit levels of the
        # input model

        nki = C.NNEXT[C.IEL[ilw]]            # 赋值后未再使用
        for id in range(1, C.ND + 1):        # DO 60
            t = C.TEMP[id]
            cor = 1.
            pp = C.PNLT[iat, ion, id]
            if ilw > 0:
                pi = C.POPUL[ilw, id] / C.G[ilw]
            else:
                pi = pp * math.exp((C.ENEV[iat, ion] * xet3 - C.EXCL0[il]) / t)
            if iun > 0:
                pj = C.POPUL[iun, id] / C.G[iun]
                cor = ((C.EXCU0[il] - C.EXCL0[il]
                        + (C.ENION[iun] - C.ENION[ilw]) / 1.38054e-16) / t)
                cor = math.exp(cor)
            else:
                pj = pp * math.exp((C.ENEV[iat, ion] * xet3 - C.EXCU0[il]) / t)
            if pj > 0.:
                x = pi / pj * cor
            else:
                x = un
            if x == un:
                x = math.exp(4.79928e-11 * C.FREQ0[il] / t)
            dop = dp0 * math.sqrt(dp1 * t + C.VTURB[id])
            C.SLIN[ilnlt, id] = bnu / (x - un)
            if pi > 0.:
                C.ABCENT[ilnlt, id] = pi * (un - un / x) * egf / dop
        # 60 CONTINUE
        return

    # Approximate NLTE for resonance lines - second order escape
    # probablity theory form of the source function
    #
    # Optical depth scale

    # 100 CONTINUE
    almil = 2.997925e17 / C.FREQ0[il]
    hkf = HK * C.FREQ0[il]
    tau = 0.     # TODO(port): TAU 在 ID=1 分支内被赋值后累加; 初始化仅为防御
    abm = 0.
    for id in range(1, C.ND + 1):            # DO 110
        t = C.TEMP[id]
        dop = dp0 * math.sqrt(dp1 * t + C.VTURB[id])
        x = math.exp(hkf / t)
        C.ABCENT[ilnlt, id] = (egf * math.exp(-C.EXCL0[il] / t)
                               * C.RRR[id, ion, iat] / dop * (1. - 1. / x))
        ab = C.ABSTD[id] + C.ABCENT[ilnlt, id] * 1.77245
        if C.IFWIN > 0:
            ab = C.ABSTDW[C.IJCONT[il], id] + C.ABCENT[ilnlt, id] * 1.77245
        if id == 1:
            abm = ab / C.DENS[1]
            tau = 0.5 * C.DM[1] * abm
        else:
            ab0 = ab / C.DENS[id]
            tau = tau + 0.5 * (C.DM[id] - C.DM[id - 1]) * (ab0 + abm)
            abm = ab0

        # approximate epsilon after Kastner

        e = eps(t, C.ELEC[id], almil, ion, iun)
        xk2 = xk2dop(tau)
        C.SLIN[ilnlt, id] = math.sqrt(e / (e + (1. - e) * xk2)) * bnu / (x - 1.)
    # 110 CONTINUE
    return


def linop(id, ablin, emlin, avab):
    """TOTAL LINE OPACITY (ABLIN)  AND EMISSIVITY (EMLIN)

    对应 synspec54.f 行 10427–10584。
    标量哑元 ID/AVAB 不被修改, 数组 ABLIN/EMLIN 就地累加, 无返回值。
    """
    # PARAMETER (UN=1., EXT0=3.17, TEN=10., C3=1.4387886, XET=8067.6,
    #            XET3=XET*C3)
    un = 1.
    ext0 = 3.17
    ten = 10.
    c3 = 1.4387886
    xet = 8067.6
    xet3 = xet * c3
    # DIMENSION ABLINN(MFREQ) —— 局部数组, 1 基索引
    ablinn = np.zeros(MFREQ + 1)

    for ij in range(1, C.NFREQ + 1):         # DO 10
        ablin[ij] = 0.
        ablinn[ij] = 0.
        emlin[ij] = 0.
    # 10 CONTINUE

    if C.NLIN == 0:
        return

    # overall loop over contributing lines

    tem1 = un / C.TEMP[id]
    for i in range(1, C.NLIN + 1):           # DO 100
        il = C.INDLIN[i]
        innlt = C.INDNLT[il]
        iat = idiv(C.INDAT[il], 100)         # Fortran 整数除法
        ion = imod(C.INDAT[il], 100)
        lpr = True
        isp = C.ISPRF[il]
        if isp > 1 and isp <= 5:
            lpr = False
        if isp >= 6:
            continue                         # GO TO 100
        agam = 0.                            # PROFIL 会重写 AGAM, 先给初值
        il, iat, id, agam = profil(il, iat, id, agam)
        dop1 = C.DOPA1[iat, id]
        fr0 = C.FREQ0[il]
        sl0 = 0.   # TODO(port): NLTE 分支才用; Fortran 中此处亦可能未定义
        if innlt == 0:
            ab0 = (math.exp(C.GF0[il] - C.EXCL0[il] * tem1)
                   * C.RRR[id, ion, iat] * dop1 * C.STIM[id])
        elif innlt > 0:
            ab0 = C.ABCENT[innlt, id]
            sl0 = C.SLIN[innlt, id]
        else:
            ilw = C.ILOWN[il]
            iun = C.IUPN[il]
            cor = 1.
            pp = C.PNLT[iat, ion, id]
            if ilw > 0:
                pi = C.POPUL[ilw, id] / C.G[ilw]
            else:
                pi = pp * math.exp((C.ENEV[iat, ion] * xet3 - C.EXCL0[il]) * tem1)
            if iun > 0:
                pj = C.POPUL[iun, id] / C.G[iun]
                cor = ((C.EXCU0[il] - C.EXCL0[il]
                        + (C.ENION[iun] - C.ENION[ilw]) / 1.38054e-16) * tem1)
                cor = math.exp(cor)
            else:
                pj = pp * math.exp((C.ENEV[iat, ion] * xet3 - C.EXCU0[il]) * tem1)
            if pj > 0.:
                x = pi / pj * cor
            else:
                x = un
            if x == un:
                x = math.exp(4.79928e-11 * C.FREQ0[il] * tem1)
            sl0 = C.BNUL[il] / (x - un)
            ab0 = 0.
            if pi > 0.:
                ab0 = pi * (un - un / x) * math.exp(C.GF0[il]) * dop1
        if ab0 <= 0. and C.lasdel:
            continue                         # GO TO 100

        # set up limiting frequencies where the line I is supposed to
        # contribute to the opacity

        ex0 = ab0 / avab * agam
        ext = ext0
        if ex0 > ten:
            ext = math.sqrt(ex0)
        ext = ext / dop1
        xijext = C.DFRCON * ext + 1.5
        # IJ1=MAX(IJCNTR(I)-IJEXT,3)
        # IJ2=MIN(IJCNTR(I)+IJEXT,NFREQS)
        ij1 = int(max(float(C.IJCNTR[i]) - xijext, 3.))
        ij2 = int(min(float(C.IJCNTR[i]) + xijext, float(C.NFREQS)))
        if ij1 >= C.NFREQ or ij2 <= 2:
            continue                         # GO TO 100

        if innlt == 0:

            # *********
            # LTE lines
            # *********

            if lpr:

                for ij in range(ij1, ij2 + 1):      # DO 40
                    xf = abs(C.FREQ[ij] - fr0) * dop1
                    ablin[ij] += ab0 * voigtk(agam, xf)

            else:
                # special expressions for 4 selected He I lines
                for ij in range(3, C.NFREQ + 1):    # DO 60
                    fr = C.FREQ[ij]
                    abl = ab0 * phe1(id, fr, isp - 1)
                    ablin[ij] += abl

        else:
            # **********
            # NLTE LINES
            # **********

            if lpr:

                for ij in range(ij1, ij2 + 1):      # DO 80
                    xf = abs(C.FREQ[ij] - fr0) * dop1
                    abl = ab0 * voigtk(agam, xf)
                    ablinn[ij] += abl
                    emlin[ij] += abl * sl0

            else:
                # again, special expressions for 4 selected He I lines
                for ij in range(3, C.NFREQ + 1):    # DO 90
                    fr = C.FREQ[ij]
                    abl = ab0 * phe1(id, fr, isp - 1)
                    ablinn[ij] += abl
                    emlin[ij] += abl * sl0
    # 100 CONTINUE

    for ij in range(3, C.NFREQ + 1):         # DO 110
        emlin[ij] += ablin[ij] * C.PLAN[id]
        ablin[ij] += ablinn[ij]
    # 110 CONTINUE

    # special routine for selected He II lines

    if C.NSP == 0:
        return
    for iis in range(1, C.NSP + 1):          # DO 120 (IS 改名 iis, 避开关键字)
        isp = C.ISP0[iis]
        if isp >= 6 and isp <= 24:
            phe2(isp, id, ablin, emlin)
    # 120 CONTINUE

    return


def linopw(id, ablin, emlin):
    """TOTAL LINE OPACITY (ABLIN)  AND EMISSIVITY (EMLIN)
    (a variant for winds)

    对应 synspec54.f 行 10590–10830。
    标量哑元 ID 不被修改, 数组 ABLIN/EMLIN 就地累加, 无返回值。
    """
    # PARAMETER (UN=1., EXT0=3.17, TEN=10., C3=1.4387886, XET=8067.6,
    #            XET3=XET*C3)
    un = 1.
    ext0 = 3.17
    ten = 10.
    c3 = 1.4387886
    xet = 8067.6
    xet3 = xet * c3
    # DIMENSION ABLINN(MFREQ) —— 局部数组, 1 基索引
    ablinn = np.zeros(MFREQ + 1)

    for ij in range(1, C.NFREQ + 1):         # DO 10
        ablin[ij] = 0.
        ablinn[ij] = 0.
        emlin[ij] = 0.
    # 10 CONTINUE
    C.WDIL[id] = 1.
    plw = C.PLAN[id] * C.WDIL[id]            # 赋值后未再使用
    # plw=xjcon(id)(原代码中被注释掉)

    if C.NLIN == 0:
        return

    # overall loop over contributing lines

    tem1 = un / C.TEMP[id]
    hkt = HK * tem1
    xx = C.FREQ[C.NOPAC] - C.FREQ[1]
    C.DFRCON = C.NOPAC - 1
    C.DFRCON = -C.DFRCON / xx
    ifrcon = int(C.DFRCON)                   # 赋值后未再使用
    for i in range(1, C.NLIN + 1):           # DO 100
        il = C.INDLIN[i]
        innlt = C.INDNLT[il]

        # rejecting lines for v > velmax

        if C.ilvi[id] > 0:
            if innlt == 0:
                continue                     # GO TO 100
            else:
                if C.nltoff != 0:
                    continue                 # GO TO 100

        # frequency indices of the line centers

        if id == 1:

            fr0 = C.FREQ0[il]
            xjc = 3. + C.DFRCON * (C.FREQ[1] - fr0)
            ijc = int(xjc)                   # Fortran INT, 向零截断
            C.IJCNTR[i] = ijc
            if ijc <= 1 or ijc >= C.NOPAC:
                pass                         # GO TO 255 → 跳过中心频率细化
            else:
                if fr0 < C.FREQ[ijc]:
                    ijc0 = ijc
                    dfr0 = C.FREQ[ijc0] - fr0
                    while True:              # 标号 252 的 GO TO 循环
                        ijc0 += 1
                        dfr = abs(C.FREQ[ijc0] - fr0)
                        if dfr < dfr0:
                            ijc = ijc0
                            ijc0 += 1
                            dfr0 = dfr
                            continue         # GO TO 252
                        break
                elif fr0 > C.FREQ[ijc]:
                    ijc0 = ijc
                    dfr0 = fr0 - C.FREQ[ijc0]
                    while True:              # 标号 254 的 GO TO 循环
                        ijc0 -= 1
                        dfr = abs(C.FREQ[ijc0] - fr0)
                        if dfr < dfr0:
                            ijc = ijc0
                            ijc0 -= 1
                            dfr0 = dfr
                            continue         # GO TO 254
                        break
                C.IJCNTR[i] = ijc
            # 255 continue
            # write(80,*) i,ijcntr(i),2.997925e18/freq0(il)(原代码中被注释掉)

        iat = idiv(C.INDAT[il], 100)         # Fortran 整数除法
        ion = imod(C.INDAT[il], 100)
        fr0 = C.FREQ0[il]
        lpr = True
        isp = C.ISPRF[il]
        if isp > 1 and isp <= 5:
            lpr = False
        if isp >= 6:
            continue                         # GO TO 100
        agam = 0.                            # PROFIL 会重写 AGAM, 先给初值
        il, iat, id, agam = profil(il, iat, id, agam)
        dop1 = C.DOPA1[iat, id] / fr0
        fr0 = C.FREQ0[il]
        sl0 = 0.   # TODO(port): 部分路径才赋值; Fortran 中此处亦可能未定义
        if innlt == 0:
            if C.itrad <= 0:
                ab0 = (math.exp(C.GF0[il] - C.EXCL0[il] * tem1)
                       * C.RRR[id, ion, iat]
                       * dop1 * (1. - math.exp(-hkt * fr0)))
            else:
                trl = C.TRAD[C.IPOTL[il], id]
                xx = math.exp(-hkt * fr0)
                ab0 = (math.exp(C.GF0[il] - C.EXCL0[il] / trl)
                       * C.RRR[id, ion, iat]
                       * dop1 * (1. - xx))
                if C.EXCL0[il] > 2000.:
                    ab0 = ab0 * C.WDIL[id]
                pla = 1.4743e-2 * (fr0 * 1.e-15) ** 3 * xx / (1. - xx)
                sl0 = pla * C.WDIL[id]
        elif innlt > 0:
            ab0 = C.ABCENT[innlt, id]
            sl0 = C.SLIN[innlt, id]
        else:
            ilw = C.ILOWN[il]
            iun = C.IUPN[il]
            cor = 1.
            pp = C.PNLT[iat, ion, id]
            if ilw > 0:
                pi = C.POPUL[ilw, id] / C.G[ilw]
            else:
                pi = pp * math.exp((C.ENEV[iat, ion] * xet3 - C.EXCL0[il]) * tem1)
            if iun > 0:
                pj = C.POPUL[iun, id] / C.G[iun]
                cor = ((C.EXCU0[il] - C.EXCL0[il]
                        + (C.ENION[iun] - C.ENION[ilw]) / 1.38054e-16) * tem1)
                cor = math.exp(cor)
            else:
                pj = pp * math.exp((C.ENEV[iat, ion] * xet3 - C.EXCU0[il]) * tem1)
            if pj > 0.:
                x = pi / pj * cor
            else:
                x = un
            if x == un:
                x = math.exp(4.79928e-11 * C.FREQ0[il] * tem1)
            sl0 = C.BNUL[il] / (x - un)
            ab0 = 0.
            if pi > 0.:
                ab0 = pi * (un - un / x) * math.exp(C.GF0[il]) * dop1
        if ab0 <= 0. and C.lasdel:
            continue                         # GO TO 100

        # set up limiting frequencies where the line I is supposed to
        # contribute to the opacity

        # if(ifwin.le.0) then(原代码中被注释掉)
        avabw = C.ABSTDW[C.IJCONT[il], id] * C.RELOP
        ex0 = ab0 / avabw * agam
        ext = ext0
        if ex0 > ten:
            ext = math.sqrt(ex0)
        ext = ext / dop1
        ijext = int((C.DFRCON * ext) + 1.5)  # Fortran INT, 向零截断
        ij1 = max(C.IJCNTR[i] - ijext, 1)
        ij2 = min(C.IJCNTR[i] + ijext, C.NFREQ)
        if ij1 >= C.NFREQ or ij2 <= 2:
            continue                         # GO TO 100
        # else
        # ij1=3
        # ij2=nfreq
        # end if(以上四行为原代码中的注释)

        if innlt == 0 and C.itrad <= 0:

            # *********
            # LTE lines
            # *********

            if lpr:

                for ij in range(ij1, ij2 + 1):      # DO 40
                    xf = abs(C.FREQ[ij] - fr0) * dop1
                    ablin[ij] += ab0 * voigtk(agam, xf)

            else:
                # special expressions for 4 selected He I lines
                for ij in range(1, C.NFREQ + 1):    # DO 60
                    fr = C.FREQ[ij]
                    abl = ab0 * phe1(id, fr, isp - 1)
                    ablin[ij] += abl

        else:
            # **********
            # NLTE LINES
            # **********

            if lpr:

                for ij in range(ij1, ij2 + 1):      # DO 80
                    xf = abs(C.FREQ[ij] - fr0) * dop1
                    abl = ab0 * voigtk(agam, xf)
                    ablinn[ij] += abl
                    if C.ilne[id] > 0:
                        continue             # GO TO 80 → 跳过发射项
                    emlin[ij] += abl * sl0

            else:
                # again, special expressions for 4 selected He I lines
                for ij in range(1, C.NFREQ + 1):    # DO 90
                    fr = C.FREQ[ij]
                    abl = ab0 * phe1(id, fr, isp - 1)
                    ablinn[ij] += abl
                    if C.ilne[id] > 0:
                        continue             # GO TO 90 → 跳过发射项
                    emlin[ij] += abl * sl0
    # 100 CONTINUE

    if C.VEL[id] <= C.velmax:
        for ij in range(1, C.NFREQ + 1):     # DO 110
            pla = C.BNUE[ij] / (math.exp(hkt * C.FREQ[ij]) - 1.)
            emlin[ij] += ablin[ij] * pla * C.WDIL[id]
            ablin[ij] += ablinn[ij]
        # 110 CONTINUE

    # special routine for selected He II lines

    if C.NSP == 0:
        return
    for iis in range(1, C.NSP + 1):          # DO 120
        isp = C.ISP0[iis]
        if isp >= 6 and isp <= 24:
            phe2(isp, id, ablin, emlin)
    # 120 CONTINUE

    return


def profil(il, iat, id, agam):
    """对应 synspec54.f 行 10836–10889。
    (原 Fortran 无头部注释, 仅 SUBROUTINE PROFIL(IL,IAT,ID,AGAM))
    标量哑元 AGAM 在体内被赋值, 按约定 return 全部 4 个标量哑元。
    """
    # PARAMETER (PI4=7.95774715E-2)
    pi4 = 7.95774715e-2
    # DIMENSION WGR(4) —— 局部数组, 1 基索引
    wgr = np.zeros(5)

    iprf = C.IPRF0[il]
    t = C.TEMP[id]
    ane = C.ELEC[id]

    # radiative broadening (classical)

    agam = C.GAMR0[il]

    # Stark broadening - standard (given in the line list or classical)

    if iprf == 0:
        agam = agam + C.GS0[il] * ane

    # Stark broadening - special expressions for He I

    elif iprf > 0:
        anp = C.POPUL[C.NKH, id]
        gam = 0.                             # GAMHE 会重写 GAM, 先给初值
        iprf, t, ane, anp, id, gam = gamhe(iprf, t, ane, anp, id, gam)
        agam = agam + gam

    # Stark broadening - Griem

    else:
        for i in range(1, 5):                # DO 10
            wgr[i] = C.WGR0[i, C.IGRIEM[il]]
        fr = C.FREQ0[il]
        ion = imod(C.INDAT[il], 100)
        gam = 0.                             # GRIEM 会重写 GAM, 先给初值
        id, t, ane, ion, fr, gam = griem(id, t, ane, ion, fr, wgr, gam)
        agam = agam + gam

    # Van Der Waals broadening

    agam = agam + C.GW0[il] * C.VDWC[id]

    # final Voigt parameter a

    dop1 = C.DOPA1[iat, id]
    if C.IFWIN > 0:
        dop1 = dop1 / C.FREQ0[il]
    agam = agam * dop1 * pi4

    return il, iat, id, agam


def griem(id, t, ane, ion, fr, wgr, gam):
    """STARK DAMPING PARAMETER (GAM) CALCULATED FROM INPUT VALUES
    OF STARK WIDTHS FOR  T=5000, 10000, 20000, 40000 K,
    AND FOR  NE=1.E16 (FOR NEUTRALS)  OR  NE = 1.E17 (FOR IONS)

    对应 synspec54.f 行 10893–10910。
    标量哑元 GAM 在体内被赋值, 按约定 return 全部 6 个标量哑元
    (WGR 为数组哑元, 就地使用不返回)。
    """
    if t <= 0.:
        return id, t, ane, ion, fr, gam
    j = C.JT[id]
    gam = ((C.TI0[id] * wgr[j] + C.TI1[id] * wgr[j - 1] + C.TI2[id] * wgr[j - 2])
           * ane * 1.e-10 * fr * 1.e-10 * fr * 4.2e-14)
    if ion > 1:
        gam = gam * 0.1
    if gam < 0.:
        gam = 0.
    return id, t, ane, ion, fr, gam


def gamhe(ind, t, ane, anp, id, gam):
    """NEUTRAL HELIUM STARK BROADENING PARAMETERS
    AFTER DIMITRIJEVIC AND SAHAL-BRECHOT, 1984, J.Q.S.R.T. 31, 301
    OR FREUDENSTEIN AND COOPER, 1978, AP.J. 224, 1079  (FOR C(IND).GT.0)

    对应 synspec54.f 行 10914–10982。
    标量哑元 GAM 在体内被赋值, 按约定 return 全部 6 个标量哑元。
    """
    # DIMENSION W(5,20),V(4,20),C(20)
    # DATA 初始化且之后不再修改 → 函数顶部直接赋值; Fortran DATA 按列优先
    # 填充, 故用 reshape(..., order='F') 后嵌入 1 基索引数组。
    # 局部数组 C 改名 c, 避免遮蔽 commons 别名 C。

    #   ELECTRONS T= 5000   10000   20000   40000     LAMBDA
    # DATA W / ...
    _wflat = [
        5.990, 6.650, 6.610, 6.210, 3819.60,
        2.950, 3.130, 3.230, 3.300, 3867.50,
        0.000, 0.000, 0.000, 0.000, 3871.79,
        0.142, 0.166, 0.182, 0.190, 3888.65,
        0.000, 0.000, 0.000, 0.000, 3926.53,
        1.540, 1.480, 1.400, 1.290, 3964.73,
        41.600, 50.500, 57.400, 65.800, 4009.27,
        1.320, 1.350, 1.380, 1.460, 4120.80,
        7.830, 8.750, 8.690, 8.040, 4143.76,
        5.830, 6.370, 6.820, 6.990, 4168.97,
        0.000, 0.000, 0.000, 0.000, 4437.55,
        1.630, 1.610, 1.490, 1.350, 4471.50,
        0.588, 0.620, 0.641, 0.659, 4713.20,
        2.600, 2.480, 2.240, 1.960, 4921.93,
        0.627, 0.597, 0.568, 0.532, 5015.68,
        1.050, 1.090, 1.110, 1.140, 5047.74,
        0.277, 0.298, 0.296, 0.293, 5875.70,
        0.714, 0.666, 0.602, 0.538, 6678.15,
        3.490, 3.630, 3.470, 3.190, 4026.20,
        4.970, 5.100, 4.810, 4.310, 4387.93,
    ]
    w = np.zeros((6, 21))
    w[1:, 1:] = np.array(_wflat).reshape((5, 20), order='F')

    #   PROTONS   T= 5000   10000   20000   40000
    # DATA V / ...
    _vflat = [
        1.520, 4.540, 9.140, 10.200,
        0.607, 0.710, 0.802, 0.901,
        0.000, 0.000, 0.000, 0.000,
        0.0396, 0.0434, 0.0476, 0.0526,
        0.000, 0.000, 0.000, 0.000,
        0.507, 0.585, 0.665, 0.762,
        0.930, 1.710, 13.600, 27.200,
        0.288, 0.325, 0.365, 0.410,
        1.330, 6.800, 12.900, 14.300,
        1.100, 1.370, 1.560, 1.760,
        0.000, 0.000, 0.000, 0.000,
        1.340, 1.690, 1.820, 1.630,
        0.128, 0.143, 0.161, 0.181,
        2.040, 2.740, 2.950, 2.740,
        0.187, 0.210, 0.237, 0.270,
        0.231, 0.260, 0.291, 0.327,
        0.0591, 0.0650, 0.0719, 0.0799,
        0.231, 0.260, 0.295, 0.339,
        2.180, 3.760, 4.790, 4.560,
        1.860, 5.320, 7.070, 7.150,
    ]
    v = np.zeros((5, 21))
    v[1:, 1:] = np.array(_vflat).reshape((4, 20), order='F')

    # DATA C /2*0.,1.83E-4,0.,1.13E-4,5*0.,1.6E-4,9*0./
    c = np.zeros(21)
    c[1:] = [0., 0., 1.83e-4, 0., 1.13e-4,
             0., 0., 0., 0., 0., 1.6e-4,
             0., 0., 0., 0., 0., 0., 0., 0., 0.]

    # IF(W(1,IND).EQ.0.) GO TO 10
    if w[1, ind] == 0.:
        # 10
        gam = c[ind] * t ** 0.16667 * ane
        return ind, t, ane, anp, id, gam
    j = C.JT[id]
    gam = (((C.TI0[id] * w[j, ind] + C.TI1[id] * w[j - 1, ind]
             + C.TI2[id] * w[j - 2, ind]) * ane
            + (C.TI0[id] * v[j, ind] + C.TI1[id] * v[j - 1, ind]
               + C.TI2[id] * v[j - 2, ind]) * anp)
           * 1.884e3 / w[5, ind] ** 2)
    if gam < 0.:
        gam = 0.
    return ind, t, ane, anp, id, gam


def eps(t, ane, alam, ion, n):
    """NLTE PARAMETER EPSILON (COLLISIONAL/SPONTANEOUS DEEXCITATION)
    AFTER  KASTNER, 1981, J.Q.S.R.T. 26, 377

    对应 synspec54.f 行 10986–11008。
    标量哑元均不被修改, 返回函数值。
    """
    # DATA CK0,CK1 /7.75E-8, 2.58E-8/  (DATA 后不再修改)
    ck0 = 7.75e-8
    ck1 = 2.58e-8
    x = 1.438e8 / alam / t
    xkt = 12390. / alam
    tt = 0.75 * x
    t1 = tt + 1.
    a = 4.36e7 * xkt * xkt / (1. - math.exp(-x))
    # IF(ION.EQ.1) GO TO 10
    if ion == 1:
        # 10  (局部变量 C 改名 c, 避免遮蔽 commons 别名 C)
        c = 2.16 / t / math.sqrt(t) / x ** 1.68 * ane
    else:
        b = 1.1 + math.log(t1 / tt) - 0.4 / t1 / t1
        c = x * b * math.sqrt(t) / xkt / xkt * ane
        if n == 0:
            c = ck0 * c
        if n != 0:
            c = ck1 * c
    # 20
    return c / (c + a)


def xk2dop(tau):
    """KERNEL FUNCTION K2  (AUXILIARY PROCEDURE TO NLTE)
    AFTER  HUMMER,  1981, J.Q.S.R.T. 26, 187

    对应 synspec54.f 行 11012–11044。
    标量哑元 TAU 不被修改, 返回函数值。
    """
    # DATA 常数(之后不再修改)
    pi2sq = 2.506628275
    pisq = 1.772453851
    a0, a1, a2, a3, a4 = (1.0, -1.117897000e-1, -1.249099917e-1,
                          -9.136358767e-3, -3.370280896e-4)
    b0, b1, b2, b3, b4, b5 = (1.0, 1.566124168e-1, 9.013261660e-3,
                              1.908481163e-4, -1.547417750e-7, -6.657439727e-9)
    c0, c1, c2, c3, c4 = (1.0, 1.915049608e1, 1.007986843e2,
                          1.295307533e2, -3.143372468e1)
    d0, d1, d2, d3, d4, d5 = (1.0, 1.968910391e1, 1.102576321e2,
                              1.694911399e2, -1.669969409e1, -3.666448000e1)
    val = 1.0                                # XK2DOP=1.D0
    if tau <= 0.:
        return val
    # IF(TAU.GT.11.) GO TO 10
    if tau > 11.:
        # 10
        x = 1.0 / math.log(tau / pisq)
        p = c0 + x * (c1 + x * (c2 + x * (c3 + x * c4)))
        q = d0 + x * (d1 + x * (d2 + x * (d3 + x * (d4 + x * d5))))
        val = p / q / 2.0 / tau / math.sqrt(math.log(tau / pisq))
        return val
    p = a0 + tau * (a1 + tau * (a2 + tau * (a3 + tau * a4)))
    q = b0 + tau * (b1 + tau * (b2 + tau * (b3 + tau * (b4 + tau * b5))))
    val = tau / pi2sq * math.log(tau / pisq) + p / q
    return val
