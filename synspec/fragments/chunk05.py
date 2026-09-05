# ======================================================================
# chunk05: synspec54.f 行 4541-5424 的逐行直译
# 含 OPAC / OPACW / OPACON / SGMERG / GFREE / SFFHMI_old /
#     LYMLIN / FEAUTR / HYLSET / HYLSEW
# ======================================================================


# ===== LYMLIN 的 SAVE 变量(Fortran 局部变量隐含 SAVE, 跨调用保留)=====
_save_lymlin_icomp = 0      # DATA icomp/0/, 首次调用时置 1
_save_lymlin_ifstrk = 0     # 由 unit 4 读入或取默认值, 之后跨调用保留
_save_lymlin_ifnat = 0
_save_lymlin_ifres = 0
_save_lymlin_ifprd = 0
_save_lymlin_ifsti = 0
# DATA SN / SR, 且在循环体内可能被置 0(ifnat/ifres 为 0 时), 隐含 SAVE;
# 1 基索引, 下标 0 不用
_save_lymlin_sn = np.array([0.0, 1.308e5, 5.280e3, 5.847e2, 1.078e2])
_save_lymlin_sr = np.array([0.0, 1.218e-16, 9.196e-17, 1.058e-16, 1.296e-16])


def opac(id, cross, abso, emis, scat):
    """Absorption, emission, and scattering coefficients
    at depth ID and for several frequencies (some or all)

    Input: ID    - depth index
           CROSS - two dimensional array of photoionization
                   cross-sections
    Output: ABSO - array of absorption coefficient
            EMIS - array of emission coefficient
            SCAT - array of scattering coefficient (all scattering
                   mechanisms except electron scattering)

    对应 synspec54.f 行 4541–4763 (SUBROUTINE OPAC)
    """
    # DIMENSION ABSO(MFREQ),EMIS(MFREQ),SCAT(MFREQ),
    #  *          ABLIN(MFREQ),EMLIN(MFREQ)
    ablin = np.zeros(MFREQ + 1)
    emlin = np.zeros(MFREQ + 1)
    UN = 1.0
    TEN15 = 1.0e-15
    CSB = 2.0706e-16
    CFF = 3.694e8        # PARAMETER (UN=1.,TEN15=1.E-15,CSB=2.0706E-16,CFF=3.694E8)

    if C.IMODE == -1 and id != C.IDSTD:
        return
    T = C.TEMP[id]
    ANE = C.ELEC[id]
    T1 = UN / T
    HKT = HK * T1
    TK = HKT / H
    SRT = UN / math.sqrt(T)
    SGFF = CFF * SRT
    CON = CSB * T1 * SRT
    conts = 1.0e-36 / CON
    ABLY = 0.0
    EMLY = 0.0
    SCLY = 0.0
    sce = ANE * SIGE
    IJ0 = 2
    if C.NFREQ == 1:
        IJ0 = 1
    if C.IMODE == 2:
        IJ0 = C.NFREQ
    M = 3
    if C.ICONTL == 1:
        M = 1

    # Opacity and emissivity in continuum
    # **** calculated only in the first and the last frequency *****

    ABLY1 = 0.0     # 仅在下面 IJ==1 时赋值, 预先初始化避免未定义
    EMLY1 = 0.0
    SCLY1 = 0.0
    for IJ in range(1, IJ0 + 1):        # DO 200 IJ=1,IJ0
        FR = C.FREQ[IJ]
        FR15 = FR * TEN15
        BNU = BN * FR15 * FR15 * FR15
        HKF = HKT * FR
        ABF = 0.0
        EBF = 0.0
        AFF = 0.0
        for IL in range(1, C.NION + 1):     # DO 100 IL=1,NION
            N0I = C.NFIRST[IL]
            N1I = C.NLAST[IL]
            NKE = C.NNEXT[IL]
            XN = C.POPUL[NKE, id]

            # Bound-free contribution + possibly
            # pseudo-continuum (accounting for dissolved fraction)

            for II in range(N0I, N1I + 1):      # DO 10 II=N0I,N1I
                SG = 0.0
                if C.ifwop[II] < 0:
                    SG = sgmerg(II, id, FR)
                else:
                    SG = cross[II, IJ]
                    if C.indexp[II] == 5:
                        IZZ = C.IZ[C.IEL[II]]
                        FR0 = C.ENION[II] / 6.6256e-27
                        DW1 = 0.0   # 临时变量; DWNFR1 修改标量哑元 DW1
                        FR, FR0, id, IZZ, DW1 = dwnfr1(FR, FR0, id, IZZ, DW1)
                        SG = SG * DW1
                if SG <= 0.0:
                    continue        # if(sg.le.0.) go to 10
                ABF = ABF + SG * C.POPUL[II, id]
                XX = SG * XN * math.exp(C.ENION[II] * TK) * C.WOP[II, id]
                if XX < conts:
                    continue        # IF(XX.lt.conts) go to 10
                EBF = EBF + XX * CON * C.G[II] / C.G[NKE]
            # 10 CONTINUE

            IT = C.IFREE[IL]
            if IT == 0:
                continue            # IF(IT.EQ.0) GO TO 100

            # Free-free contribution

            IE = IL
            if IE == C.IELHM:       # IF(IE.EQ.IELHM) GO TO 65
                SFF = sffhmi(XN, FR, T)     # 65
            else:
                CH = C.IZ[IL] * C.IZ[IL]
                SF1 = CH * XN * SGFF / (FR * FR * FR)

                # The following expression is the so-called modified free-free
                # opacity, ie. allowing for the photoionization from higher,
                # non-explicit, LTE energy levels of the ion IL

                HKFM = HKT * min(C.FF[IL], FR)
                SF2 = math.exp(HKFM)
                if IT == 2:         # IF(IT.NE.2) GO TO 50
                    SG = gfree(T, FR / CH)
                    SF2 = SF2 + SG - UN
                SFF = SF1 * SF2     # 50
            # GO TO 70
            AFF = AFF + SFF         # 70
        # 100 CONTINUE

        # Additional opacities

        _mode = 0   # 字面量 0 作为 MODE 实参; OPADD 修改标量哑元, 用临时变量接收
        _mode, id, FR, ABAD, EMAD, SCAD = opadd(_mode, id, FR, 0.0, 0.0, 0.0)
        if C.IOPHLI != 0:
            # LYMLIN 修改标量哑元 ABLY/EMLY/SCLY, 解包接收
            id, FR, ABLY, EMLY, SCLY = lymlin(id, FR, ABLY, EMLY, SCLY)

        # Total opacity and emissivity

        X = math.exp(-HKF)
        X1 = UN - X
        BNE = BNU * X * ANE
        # ABSO(IJ)=ABF+ANE*(X1*AFF-X*EBF)+ABAD+ABLY
        abso[IJ] = ABF + ANE * (X1 * AFF - X * EBF) + ABAD
        emis[IJ] = BNE * (AFF + EBF) + EMAD + EMLY
        scat[IJ] = SCAD + SCLY + sce
        if IJ == 1:
            ABLY1 = ABLY
            EMLY1 = EMLY
            SCLY1 = SCLY
    # 200 CONTINUE
    AVAB = (abso[1] + abso[2] + scat[1] + scat[2]) * 0.5 * C.RELOP
    if C.NFREQ <= 2 or C.IMODE == -1:
        return
    if C.IMODE != 2:        # IF(IMODE.EQ.2) GO TO 225

        # interpolated continuum opacity, emissivity, and scattering
        # for all frequencies

        for IJ in range(3, C.NFREQ + 1):
            abso[IJ] = C.FRX1[IJ] * abso[2] + C.FRX2[IJ] * abso[1]
            emis[IJ] = C.FRX1[IJ] * emis[2] + C.FRX2[IJ] * emis[1]
            scat[IJ] = C.FRX1[IJ] * scat[2] + C.FRX2[IJ] * scat[1]

        # hydrogen lines -- for IHYL = 0
        # *** calculated only for the first and the last frequency
        # and interpolated hydrogen line opacity and emissivity
        # for all frequencies

        if C.IHYL == 0:
            hydlin(id, 1, 2, ablin, emlin)
            for IJ in range(M, C.NFREQ + 1):
                abso[IJ] = abso[IJ] + C.FRX1[IJ] * ablin[2] + C.FRX2[IJ] * ablin[1]
                emis[IJ] = emis[IJ] + C.FRX1[IJ] * emlin[2] + C.FRX2[IJ] * emlin[1]

        # **** Opacity and emissivity in lines ****

        linop(id, ablin, emlin, AVAB)
        for IJ in range(3, C.NFREQ + 1):
            abso[IJ] = abso[IJ] + ablin[IJ]
            emis[IJ] = emis[IJ] + emlin[IJ]

        # **** Opacity and emissivity in molecular lines ****

        if C.IFMOL > 0:
            for ilist in range(1, C.NMLIST + 1):
                molop(id, ablin, emlin, AVAB, ilist)
                for IJ in range(3, C.NFREQ + 1):
                    abso[IJ] = abso[IJ] + ablin[IJ]
                    emis[IJ] = emis[IJ] + emlin[IJ]
    # 225 CONTINUE

    # **** Detailed opacity and emissivity in hydrogen lines ****
    #      (for IHYL=1)

    if C.IHYL > 0 or C.IMODE == 2:
        hydlin(id, M, C.NFREQ, ablin, emlin)
        for IJ in range(M, C.NFREQ + 1):
            abso[IJ] = abso[IJ] + ablin[IJ]
            emis[IJ] = emis[IJ] + emlin[IJ]

    # **** Detailed opacity and emissivity in HE II lines ****
    #      (for IHE2L=1)

    if C.IHE2L > 0:
        he2lin(id, M, C.NFREQ, ablin, emlin)
        for IJ in range(M, C.NFREQ + 1):
            abso[IJ] = abso[IJ] + ablin[IJ]
            emis[IJ] = emis[IJ] + emlin[IJ]

    # opacity due to detailed photoinization cross-section
    # (from tables; including resonance features)
    # The two routines may be called and correspond to different formats
    # as well as difference in INPUT!

    phtion(id, abso, emis, C.FREQ, C.NFREQ)
    phtx(id, abso, emis, C.FREQ, 0)

    if C.IMODE >= 0:
        for ij in range(1, C.NFREQ + 1):
            abso[ij] = abso[ij] + scat[ij]

    if C.ICONTL == 1:
        return
    abso[1] = abso[1] - ABLY1
    emis[1] = emis[1] - EMLY1
    scat[1] = scat[1] - SCLY1
    abso[2] = abso[2] - ABLY
    emis[2] = emis[2] - EMLY
    scat[2] = scat[2] - SCLY
    return


def opacw(id, cross, abso, emis, absoc, emisc, scatc, modc):
    """Absorption, emission, and scattering coefficients
    at depth ID and for several frequencies (some or all)
    (variant for winds, INCLUDE 'WINCOM.FOR')

    Input: ID    - depth index
           CROSS - two dimensional array of photoionization
                   cross-sections
    Output: ABSO - array of absorption coefficient
            EMIS - array of emission coefficient
            SCAT - array of scattering coefficient (all scattering
                   mechanisms except electron scattering)

    对应 synspec54.f 行 4770–4968 (SUBROUTINE OPACW)
    """
    # DIMENSION ABSO(MFREQ),EMIS(MFREQ),SCAT(MFREQ),
    #  *          ABSOC(MFREQC),EMISC(MFREQC),SCATC(MFREQC),
    #  *          ABLIN(MFREQ),EMLIN(MFREQ),
    #  *          ABL1(MFREQC),EML1(MFREQC),SCL1(MFREQC)
    ablin = np.zeros(MFREQ + 1)
    emlin = np.zeros(MFREQ + 1)
    abl1 = np.zeros(MFREQC + 1)
    eml1 = np.zeros(MFREQC + 1)
    scl1 = np.zeros(MFREQC + 1)
    # common/lasers/lasdel  (声明了但本例程未使用)
    UN = 1.0
    TEN15 = 1.0e-15
    CSB = 2.0706e-16
    CFF = 3.694e8        # PARAMETER (UN=1.,TEN15=1.E-15,CSB=2.0706E-16,CFF=3.694E8)

    if C.IMODE == -1 and id != C.IDSTD:
        return
    T = C.TEMP[id]
    ANE = C.ELEC[id]
    T1 = UN / T
    HKT = HK * T1
    TK = HKT / H
    SRT = UN / math.sqrt(T)
    SGFF = CFF * SRT
    CON = CSB * T1 * SRT
    conts = 1.0e-36 / CON
    ABLY = 0.0
    EMLY = 0.0
    SCLY = 0.0
    IJ0 = 2
    if C.NFREQ == 1:
        IJ0 = 1
    if C.IMODE == 2:
        IJ0 = C.NFREQ
    M = 3

    # Opacity and emissivity in continuum
    # **** calculated only for the continuum frequencies *****

    for IJ in range(1, C.NFREQC + 1):       # DO 200 IJ=1,NFREQC
        FR = C.FREQC[IJ]
        FR15 = FR * TEN15
        BNU = BN * FR15 * FR15 * FR15
        HKF = HKT * FR
        ABF = 0.0
        EBF = 0.0
        AFF = 0.0
        for IL in range(1, C.NION + 1):     # DO 100 IL=1,NION
            N0I = C.NFIRST[IL]
            N1I = C.NLAST[IL]
            NKE = C.NNEXT[IL]
            XN = C.POPUL[NKE, id]

            # Bound-free contribution + possibly
            # pseudo-continuum (accounting for dissolved fraction)

            for II in range(N0I, N1I + 1):      # DO 10 II=N0I,N1I
                SG = 0.0
                if C.ifwop[II] < 0:
                    SG = sgmerg(II, id, FR)
                else:
                    SG = cross[II, IJ]
                    if C.indexp[II] == 5:
                        IZZ = C.IZ[C.IEL[II]]
                        FR0 = C.ENION[II] / 6.6256e-27
                        DW1 = 0.0   # 临时变量; DWNFR1 修改标量哑元 DW1
                        FR, FR0, id, IZZ, DW1 = dwnfr1(FR, FR0, id, IZZ, DW1)
                        SG = SG * DW1
                ABF = ABF + SG * C.POPUL[II, id]
                XX = SG * XN * math.exp(C.ENION[II] * TK) * C.WOP[II, id]
                if XX < conts:
                    continue        # IF(XX.lt.conts) go to 10
                EBF = EBF + XX * CON * C.G[II] / C.G[NKE]
            # 10 CONTINUE
            IT = C.IFREE[IL]
            if IT == 0:
                continue            # IF(IT.EQ.0) GO TO 100

            # Free-free contribution

            IE = IL
            if IE == C.IELHM:       # IF(IE.EQ.IELHM) GO TO 65
                SFF = sffhmi(XN, FR, T)     # 65
            else:
                CH = C.IZ[IL] * C.IZ[IL]
                SF1 = CH * XN * SGFF / (FR * FR * FR)

                # The following expression is the so-called modified free-free
                # opacity, ie. allowing for the photoionization from higher,
                # non-explicit, LTE energy levels of the ion IL

                HKFM = HKT * min(C.FF[IL], FR)
                SF2 = math.exp(HKFM)
                if IT == 2:         # IF(IT.NE.2) GO TO 50
                    SG = gfree(T, FR / CH)
                    SF2 = SF2 + SG - UN
                SFF = SF1 * SF2     # 50
            # GO TO 70
            AFF = AFF + SFF         # 70
        # 100 CONTINUE

        # Additional opacities

        _mode = 0   # 字面量 0 作为 MODE 实参; OPADD 修改标量哑元, 用临时变量接收
        _mode, id, FR, ABAD, EMAD, SCAD = opadd(_mode, id, FR, 0.0, 0.0, 0.0)
        if C.IOPHLI != 0:
            # LYMLIN 修改标量哑元 ABLY/EMLY/SCLY, 解包接收
            id, FR, ABLY, EMLY, SCLY = lymlin(id, FR, ABLY, EMLY, SCLY)

        # Total opacity and emissivity

        X = math.exp(-HKF)
        X1 = UN - X
        BNE = BNU * X * ANE
        absoc[IJ] = ABF + ANE * (X1 * AFF - X * EBF) + ANE * SIGE + ABAD + ABLY
        emisc[IJ] = BNE * (AFF + EBF) + EMAD + EMLY
        scatc[IJ] = SCAD + SCLY
        abl1[IJ] = ABLY
        eml1[IJ] = EMLY
        scl1[IJ] = SCLY
    # 200 CONTINUE

    if modc == 0:
        return

    if C.NFREQ <= 2 or C.IMODE == -1:
        return

    # interpolated continuum and hydrogen line opacity and emissivity
    # for all frequencies

    for IJ in range(1, C.NFREQ + 1):
        IJC = C.IJCINT[IJ]
        abso[IJ] = C.FRX1[IJ] * absoc[IJC] + (1.0 - C.FRX1[IJ]) * absoc[IJC + 1]
        emis[IJ] = C.FRX1[IJ] * emisc[IJC] + (1.0 - C.FRX1[IJ]) * emisc[IJC + 1]
        scat[IJ] = C.FRX1[IJ] * scatc[IJC] + (1.0 - C.FRX1[IJ]) * scatc[IJC + 1]
    if C.IMODE != 2:        # IF(IMODE.EQ.2) GO TO 225

        # **** Opacity and emissivity in lines ****

        linopw(id, ablin, emlin)
        for IJ in range(1, C.NFREQ + 1):
            abso[IJ] = abso[IJ] + ablin[IJ]
            emis[IJ] = emis[IJ] + emlin[IJ]

        # **** Opacity and emissivity in molecular lines ****

        if C.IFMOL > 0:
            avab = 0.0  # TODO(port): OPACW 中 AVAB 未赋值即传给 MOLOP(Fortran 依赖未定义值), 此处取 0.0
            for ilist in range(1, C.NMLIST + 1):
                molop(id, ablin, emlin, avab, ilist)
                for IJ in range(1, C.NFREQ + 1):
                    abso[IJ] = abso[IJ] + ablin[IJ]
                    emis[IJ] = emis[IJ] + emlin[IJ]
    # 225 CONTINUE

    # **** Detailed opacity and emissivity in hydrogen lines ****

    hydliw(id, ablin, emlin)
    for IJ in range(1, C.NFREQ + 1):
        abso[IJ] = abso[IJ] + ablin[IJ]
        emis[IJ] = emis[IJ] + emlin[IJ]

    # **** Detailed opacity and emissivity in HE II lines ****
    #      (for IHE2L=1)

    he2liw(id, ablin, emlin)
    for IJ in range(1, C.NFREQ + 1):
        abso[IJ] = abso[IJ] + ablin[IJ]
        emis[IJ] = emis[IJ] + emlin[IJ]

    # opacity due to detailed photoinization cross-section
    # (from tables; including resonance features)
    # The two routines may be called and correspond to different formats
    # as well as difference in INPUT!

    phtion(id, abso, emis, C.FREQ, C.NFREQ)
    phtx(id, abso, emis, C.FREQ, 0)

    if C.ICONTL == 1:
        return
    for IJ in range(1, C.NFREQC + 1):
        absoc[IJ] = absoc[IJ] - abl1[IJ]
        emisc[IJ] = emisc[IJ] - eml1[IJ]
        scatc[IJ] = scatc[IJ] - scl1[IJ]
    return


def opacon(id, cross, absoc, emisc, scatc):
    """Absorption, emission, and scattering coefficients
    at depth ID and for several frequencies (some or all)
    (variant for continuum frequencies only, INCLUDE 'WINCOM.FOR')

    Input: ID    - depth index
           CROSS - two dimensional array of photoionization
                   cross-sections
    Output: ABSO - array of absorption coefficient
            EMIS - array of emission coefficient
            SCAT - array of scattering coefficient

    对应 synspec54.f 行 4975–5100 (SUBROUTINE OPACON)
    """
    UN = 1.0
    TEN15 = 1.0e-15
    CSB = 2.0706e-16
    CFF = 3.694e8        # PARAMETER (UN=1.,TEN15=1.E-15,CSB=2.0706E-16,CFF=3.694E8)

    T = C.TEMP[id]
    ANE = C.ELEC[id]
    T1 = UN / T
    HKT = HK * T1
    TK = HKT / H
    SRT = UN / math.sqrt(T)
    SGFF = CFF * SRT
    CON = CSB * T1 * SRT
    ABLY = 0.0
    EMLY = 0.0
    SCLY = 0.0
    sce = ANE * SIGE
    SF2 = 0.0   # TODO(port): 原代码中 SF2 未初始化即在 IT==2 分支累加(依赖跨迭代残留值), 此处初始化为 0.0

    # Opacity and emissivity in continuum
    # **** calculated only for the continuum frequencies *****

    for IJ in range(1, C.NFREQC + 1):       # DO 200 IJ=1,NFREQC
        FR = C.FREQC[IJ]
        FR15 = FR * TEN15
        BNU = BN * FR15 * FR15 * FR15
        HKF = HKT * FR
        ABF = 0.0
        EBF = 0.0
        AFF = 0.0
        for IL in range(1, C.NION + 1):     # DO 100 IL=1,NION
            N0I = C.NFIRST[IL]
            N1I = C.NLAST[IL]
            NKE = C.NNEXT[IL]
            XN = C.POPUL[NKE, id]

            # Bound-free contribution + possibly
            # pseudo-continuum (accounting for dissolved fraction)

            for II in range(N0I, N1I + 1):      # DO 10 II=N0I,N1I
                SG = 0.0
                if C.ifwop[II] < 0:
                    SG = sgmerg(II, id, FR)
                else:
                    SG = cross[II, IJ]
                    if SG <= 0.0:
                        continue    # if(sg.le.0.) go to 10
                    if C.indexp[II] == 5:
                        IZZ = C.IZ[C.IEL[II]]
                        FR0 = C.ENION[II] / 6.6256e-27
                        DW1 = 0.0   # 临时变量; DWNFR1 修改标量哑元 DW1
                        FR, FR0, id, IZZ, DW1 = dwnfr1(FR, FR0, id, IZZ, DW1)
                        SG = SG * DW1
                if C.POPUL[II, id] < 1.0e-20 or XN < 1.0e-20:
                    continue        # if(popul(ii,id).lt.1.e-20.or.xn.lt.1.e-20) go to 10
                ABF = ABF + SG * C.POPUL[II, id]
                XX = SG * XN * math.exp(C.ENION[II] * TK - HKF) * C.WOP[II, id]
                ee = math.exp(C.ENION[II] * TK - HKF)   # 原代码计算后未使用
                EBF = EBF + XX * CON * C.G[II] / C.G[NKE]
                # if(id.eq.1.or.id.eq.50) write(*,*)'opacon',id,ij,ii,
                #  popul(ii,id),sg,abf
            # 10 CONTINUE
            IT = C.IFREE[IL]
            if IT == 0:
                continue            # IF(IT.EQ.0) GO TO 100

            # Free-free contribution

            IE = IL
            if IE == C.IELHM:       # IF(IE.EQ.IELHM) GO TO 65
                SFF = sffhmi(XN, FR, T)     # 65
            else:
                CH = C.IZ[IL] * C.IZ[IL]
                SF1 = CH * XN * SGFF / (FR * FR * FR)

                # The following expression is the so-called modified free-free
                # opacity, ie. allowing for the photoionization from higher,
                # non-explicit, LTE energy levels of the ion IL

                if IT == 2:         # IF(IT.NE.2) GO TO 50
                    SG = gfree(T, FR / CH)
                    SF2 = SF2 + SG - UN
                SFF = SF1           # 50
            # GO TO 70
            AFF = AFF + SFF         # 70
        # 100 CONTINUE

        # Additional opacities

        _mode = 0   # 字面量 0 作为 MODE 实参; OPADD 修改标量哑元, 用临时变量接收
        _mode, id, FR, ABAD, EMAD, SCAD = opadd(_mode, id, FR, 0.0, 0.0, 0.0)
        if C.IOPHLI != 0:
            # LYMLIN 修改标量哑元 ABLY/EMLY/SCLY, 解包接收
            id, FR, ABLY, EMLY, SCLY = lymlin(id, FR, ABLY, EMLY, SCLY)

        # Total opacity and emissivity

        X = math.exp(-HKF)
        X1 = UN - X
        BNE = BNU * X * ANE
        absoc[IJ] = ABF + ANE * (X1 * AFF - EBF) + ABAD + ABLY
        emisc[IJ] = BNE * AFF + BNU * ANE * EBF + EMAD + EMLY
        scatc[IJ] = SCAD + SCLY + sce
        # if(id.eq.1.or.id.eq.50) write(*,*)'opacon-tot',id,ij,
        #  abf,ane,absoc(ij)
    # 200 CONTINUE

    phtion(id, absoc, emisc, C.FREQC, C.NFREQC)
    phtx(id, absoc, emisc, C.FREQC, 1)

    return


def sgmerg(ii, id, fr):
    """formal routine - taken from TLUSTY, but not used here

    对应 synspec54.f 行 5106–5139 (FUNCTION SGMERG)
    """
    FRH = 3.28805e15
    PH2 = 2.815e29 * 2.0
    EHB = 157802.77355     # PARAMETER (FRH=3.28805E15, PH2=2.815D29*2., EHB=157802.77355)

    # sgmerg=0.
    # if(id.gt.0) return
    IE = C.IEL[ii]
    CH = C.IZ[IE] * C.IZ[IE]
    C.G[ii] = C.GMER[C.IMRG[ii], id]    # g(ii)=gmer(imrg(ii),id)
    T1 = 1.0 / C.TEMP[id]
    EX = EHB * CH * T1
    II0 = C.NQUANT[ii - 1] + 1
    SUM = 0.0
    SUD = 0.0
    for I in range(II0, NLMX + 1):     # DO 10 I=II0,NLMX（NLMX 为 PARAMETER 常量）
        X = float(I)
        XI = 1.0 / (X * X)
        FREDG = FRH * CH * XI
        if fr < FREDG:
            continue            # IF(FR.LT.FREDG) GO TO 10
        EXI = math.exp(EX * XI)
        S = EXI * C.WNHINT[I, id] * XI / X
        SUM = SUM + S
        # SUD=SUD+S*XI
    # 10 CONTINUE
    SG0 = PH2 / (fr * fr * fr * C.G[ii]) * CH * CH
    SGMERG = SUM * SG0
    # DSG=-SUD*SG0*EX*T1
    return SGMERG


def gfree(t, fr):
    """Hydrogenic free-free Gaunt factor, for temperature T and
    frequency FR

    对应 synspec54.f 行 5144–5164 (FUNCTION GFREE)
    """
    THET = 5040.4 / t
    if THET < 4.0e-2:
        THET = 4.0e-2
    X = fr / 2.99793e14
    if X <= 1:                  # IF(X.GT.1) GO TO 10
        if X < 0.2:
            X = 0.2
        GFREE = (1.0823 + 2.98e-2 / THET) + (6.7e-3 + 1.12e-2 / THET) / X
        return GFREE
    # 10
    C1 = (3.9999187e-3 - 7.8622889e-5 / THET) / THET + 1.070192
    C2 = (6.4628601e-2 - 6.1953813e-4 / THET) / THET + 2.6061249e-1
    C3 = (1.3983474e-5 / THET + 3.7542343e-2) / THET + 5.7917786e-1
    C4 = 3.4169006e-1 + 1.1852264e-2 / THET
    GFREE = ((C4 / X - C3) / X + C2) / X + C1
    return GFREE


def sffhmi_old(popi, fr, t):
    """Free-free cross section for H- (After Kurucz,1970,SAO 309, P.80)

    对应 synspec54.f 行 5169–5177 (FUNCTION SFFHMI_old)
    """
    SFFHMI_old = (1.3727e-25 + (4.3748e-10 - 2.5993e-7 / t) / fr) * popi / fr
    return SFFHMI_old


def lymlin(id, freq, ably, emly, scly):
    """OPACITY OF THE LYMAN LINES WINGS (ALPHA - DELTA)
    WITH APPROXIMATE PARTIAL REDISTRIBUTION

    对应 synspec54.f 行 5183–5250 (SUBROUTINE LYMLIN)
    修改标量哑元 ABLY/EMLY/SCLY, 返回全部标量哑元 (id, freq, ably, emly, scly)
    """
    global _save_lymlin_icomp, _save_lymlin_ifstrk, _save_lymlin_ifnat
    global _save_lymlin_ifres, _save_lymlin_ifprd, _save_lymlin_ifsti
    # DIMENSION SN(4),SR(4),SS(4),GS(4),FRLY(4),BNLY(4),GA(4)
    # DATA FRLY / 2.4660375E15, 2.9227111E15, 3.0825469E15, 3.156528E15/
    #  *    ,BNLY / 5.527E-2,     4.090E-2,     2.699E-2,     1.855E-2  /,
    #  *     SN   / 1.308E5,      5.280E3,      5.847E2,      1.078E2   /,
    #  *     SR   / 1.218E-16,    9.196E-17,    1.058E-16,    1.296E-16 /,
    #  *     SS   / 9.478E-3,     1.600E-2,     1.441E-2,     1.547E-2  /,
    #  *     GS   / 7.237E-8,     5.432E-6,     5.821E-5,     4.027E-4  /,
    #  *     GA   / 1.000,        1.791,        2.362,        2.801 /
    # 以下 DATA 数组不再修改, 直接局部赋值; SN/SR 会被修改, 见模块级 _save_lymlin_sn/sr
    FRLY = [0.0, 2.4660375e15, 2.9227111e15, 3.0825469e15, 3.156528e15]
    BNLY = [0.0, 5.527e-2, 4.090e-2, 2.699e-2, 1.855e-2]
    SS = [0.0, 9.478e-3, 1.600e-2, 1.441e-2, 1.547e-2]
    GS = [0.0, 7.237e-8, 5.432e-6, 5.821e-5, 4.027e-4]
    GA = [0.0, 1.000, 1.791, 2.362, 2.801]

    # data icomp/0/
    if C.IATH <= 0:
        return id, freq, ably, emly, scly
    if _save_lymlin_icomp == 0:
        _save_lymlin_icomp = 1
        try:
            # read(4,*,err=10,end=10) ifstrk,ifnat,ifres,ifprd,ifsti
            _parts = read_line(4).split()
            _save_lymlin_ifstrk = int(float(_parts[0]))
            _save_lymlin_ifnat = int(float(_parts[1]))
            _save_lymlin_ifres = int(float(_parts[2]))
            _save_lymlin_ifprd = int(float(_parts[3]))
            _save_lymlin_ifsti = int(float(_parts[4]))
        except Exception:
            # 10 CONTINUE: err=/end= 分支, 取默认值
            _save_lymlin_ifstrk = 0
            _save_lymlin_ifnat = 1
            _save_lymlin_ifres = 1
            _save_lymlin_ifprd = 0
            _save_lymlin_ifsti = 0
            if C.IOPHLI < 0:
                _save_lymlin_ifstrk = 1
                _save_lymlin_ifprd = 1
        # 11 CONTINUE

    ably = 0.0
    emly = 0.0
    scly = 0.0

    if freq > 3.3e15:
        return id, freq, ably, emly, scly

    P = C.POPUL[C.N0HN, id]
    T = C.TEMP[id]
    ANE = C.ELEC[id]
    for I in range(1, 5):           # DO 40 I=1,4
        DFR = abs(FRLY[I] - freq)
        if DFR <= 5.0e11:
            DFR = 1.0e12
        DFR2 = DFR * DFR
        DFRS = math.sqrt(DFR)
        COR = (2.0 * freq / (freq + FRLY[I])) ** 2
        F = 1.0
        if abs(C.IOPHLI) == 2:
            F = feautr(freq, id)
        STARK = SS[I] * ANE * F / DFR2 / DFRS
        if _save_lymlin_ifstrk == 0:
            STARK = 0.0
        if _save_lymlin_ifnat == 0:
            _save_lymlin_sn[I] = 0.0
        if _save_lymlin_ifres == 0:
            _save_lymlin_sr[I] = 0.0
        SGLY = _save_lymlin_sn[I] * (1.0 + _save_lymlin_sr[I] * P) * COR / DFR2 + STARK
        SGLY = SGLY * C.WNHINT[I + 1, id]
        GAMA = 1.0 / (GA[I] + GS[I] * ANE * F / DFRS)
        if _save_lymlin_ifprd == 0:
            GAMA = 0.0
        ably = ably + P * SGLY
        emly = emly + C.POPUL[C.N0HN + I, id] * SGLY * BNLY[I] * (1.0 - GAMA)
        if _save_lymlin_ifsti != 0:
            ably = ably - C.POPUL[C.N0HN + I, id] * SGLY / (I + 1) / (I + 1)
        scly = scly + P * SGLY * GAMA
    # 40 CONTINUE
    return id, freq, ably, emly, scly


def feautr(freq, id):
    """LYMAN-ALPHA STARK BROADENING AFTER N.FEAUTRIER

    对应 synspec54.f 行 5254–5293 (FUNCTION FEAUTR)
    """
    # DIMENSION DL(20),F05(20),F10(20),F20(20),F40(20),X(4)
    # DATA 数组不修改, 直接赋值(1 基索引, 下标 0 不用)
    F05 = [0.0, 0.0537, 0.0964, 0.1330, 0.3105, 0.4585, 0.6772, 0.8229,
           0.8556, 0.9250, 0.9618, 0.9733, 1.1076, 1.0644, 1.0525,
           0.8841, 0.8282, 0.7541, 0.7091, 0.7164, 0.7672]
    F10 = [0.0, 0.1986, 0.2764, 0.3959, 0.5740, 0.7385, 0.9448, 1.0292,
           1.0317, 0.9947, 0.8679, 0.8648, 0.9815, 1.0660, 1.0793,
           1.0699, 1.0357, 0.9245, 0.8603, 0.8195, 0.7928]
    F20 = [0.0, 0.4843, 0.5821, 0.7003, 0.8411, 0.9405, 1.0300, 1.0029,
           0.9753, 0.8478, 0.6851, 0.6861, 0.8554, 0.9916, 1.0264,
           1.0592, 1.0817, 1.0575, 1.0152, 0.9761, 0.9451]
    F40 = [0.0, 0.7862, 0.8566, 0.9290, 0.9915, 1.0066, 0.9878, 0.8983,
           0.8513, 0.6881, 0.5277, 0.5302, 0.6920, 0.8607, 0.9111,
           0.9651, 1.0793, 1.1108, 1.1156, 1.1003, 1.0839]
    DL = [0.0, -150.0, -120.0, -90.0, -60.0, -40.0, -20.0, -10.0, -8.0, -4.0,
          -2.0, 2.0, 4.0, 8.0, 10.0, 20.0, 40.0, 60.0, 90.0, 120.0, 150.0]
    X = np.zeros(5)
    DLAM = 2.997925e18 / freq - 1215.685
    for I in range(2, 21):          # DO 10 I=2,20
        if DLAM <= DL[I]:
            break                   # IF(DLAM.LE.DL(I)) GO TO 20
    else:
        I = 20                      # 循环正常结束后显式 I=20
    # 20
    J = I - 1
    C_l = DL[J] - DL[I]             # 源码局部变量名 C, 与 commons 别名冲突, 加后缀 _l
    A = (DLAM - DL[I]) / C_l
    B = (DL[J] - DLAM) / C_l
    X[1] = F05[J] * A + F05[I] * B
    X[2] = F10[J] * A + F10[I] * B
    X[3] = F20[J] * A + F20[I] * B
    X[4] = F40[J] * A + F40[I] * B
    J = C.JT[id]
    Y = C.TI0[id] * X[J] + C.TI1[id] * X[J - 1] + C.TI2[id] * X[J - 2]
    FEAUTR = 0.5 * (Y + 1.0)
    return FEAUTR


def hylset():
    """Initialization procedure for treating the hydrogen line opacity

    对应 synspec54.f 行 5297–5360 (SUBROUTINE HYLSET)
    """
    # DIMENSION ALB(15), DATA 数组不修改(1 基索引, 下标 0 不用)
    ALB = [0.0, 656.28, 486.13, 434.05, 410.17, 397.01,
           388.91, 383.54, 379.79, 377.06, 375.02,
           373.44, 372.19, 371.20, 370.39, 369.72]

    # IHYL=-1  -  hydrogen lines are excluded a priori

    C.IHYL = -1
    if C.IATH <= 0:
        return
    if C.FREQ[2] >= 3.28805e15:
        return
    AL0 = 2.997925e17 / C.FREQ[1]
    AL1 = 2.997925e17 / C.FREQ[2]
    if AL0 > 200.0 and AL1 < 364.6:
        return
    if AL0 > 560.0 and AL1 < 580.0:
        return
    if AL0 > 720.0 and AL1 < 820.3:
        return

    # otherwise, hydrogen lines are included

    C.IHYL = 0
    C.M20 = 40
    if AL1 < 364.6:
        C.ILOWH = 1
        FRION = 3.28805e15      # FRION 不在 commons.py, 按局部变量处理
        C.M10 = int(math.sqrt(3.28805e15 / abs(FRION - C.FREQ[2])))
        if FRION > C.FREQ[1]:
            C.M20 = int(math.sqrt(3.28805e15 / (FRION - C.FREQ[1])))
        C.IHYL = 1
        if AL0 > 123.0:
            C.IHYL = 0
        if AL0 > 104.0 and AL1 < 120.0:
            C.IHYL = 0
        if AL0 > 98.5 and AL1 < 102.0:
            C.IHYL = 0
        if C.IMODE == 2 or C.IHYDPR != 0 or C.GRAV >= 6.0:
            C.IHYL = 1
    elif AL1 < 820.0:
        C.ILOWH = 2
        if C.vaclim < 3600.0:
            FRION = 8.2225e14
            C.M10 = int(math.sqrt(3.289017e15 / abs(FRION - C.FREQ[2])))
        else:
            FRION = 8.22013e14
            C.M10 = int(math.sqrt(3.28805e15 / abs(FRION - C.FREQ[2])))
        if FRION > C.FREQ[1]:
            C.M20 = int(math.sqrt(3.289017e15 / (FRION - C.FREQ[1])))
        for I in range(1, 16):      # DO 10 I=1,15
            AL = ALB[I]
            if AL < AL0 - 1.0 or AL > AL1 + 1.0:
                continue            # GO TO 10
            C.IHYL = 1
            break                   # GO TO 20
        # 10/20 CONTINUE
        if C.IMODE == 2 or C.IHYDPR != 0 or C.GRAV >= 6.0:
            C.IHYL = 1
    else:
        C.ILOWH = 3
        C.IHYL = 1

    C.IHYL = 1          # ihyl=1

    return


def hylsew(ij):
    """Initialization procedure for treating the hydrogen line opacity
    (variant for winds, per frequency IJ)

    对应 synspec54.f 行 5364–5421 (SUBROUTINE HYLSEW)
    """
    # IHYL=-1  -  hydrogen lines are excluded a priori

    C.IHYLW[ij] = 0
    if C.IATH <= 0:
        return
    FR = C.FREQ[ij]
    if FR >= 3.28805e15:
        return
    AL0 = 2.997925e17 / FR
    AL1 = AL0
    if C.GRAV < 6.0:
        if AL0 > 160.0 and AL1 < 364.6:
            return
        if AL0 > 506.0 and AL1 < 630.0:
            return
        if AL0 > 680.0 and AL1 < 820.3:
            return
    else:
        if AL0 > 540.0 and AL1 < 600.0:
            return
        if AL0 > 720.0 and AL1 < 820.3:
            return

    # otherwise, hydrogen lines are included

    C.IHYLW[ij] = 1
    C.M20W[ij] = 40
    if AL1 < 364.6:
        C.ILOWHW[ij] = 1
        FRION = 3.28805e15      # FRION 不在 commons.py, 按局部变量处理
    elif AL1 < 820.0:
        C.ILOWHW[ij] = 2
        FRION = 8.2225e14
    elif AL1 < 1458.0:
        C.ILOWHW[ij] = 3
        FRION = 3.6544142e14
    elif AL1 < 2278.0:
        C.ILOWHW[ij] = 4
        FRION = 2.0555837e14
    elif AL1 < 3281.0:
        C.ILOWHW[ij] = 5
        FRION = 1.315589e14
    elif AL1 < 4466.0:
        C.ILOWHW[ij] = 6
        FRION = 9.136394e13
    else:
        C.ILOWHW[ij] = 7
        FRION = 6.7120228e13
    if FRION > FR:
        C.M10W[ij] = int(math.sqrt(3.289017e15 / abs(FRION - FR)))
    # 以下输出语句在原代码中被注释掉:
    # c     WRITE(6,601) ILOWH,M20+1
    # c 601 FORMAT(1H0/ ' *** HYDROGEN LINES CONTRIBUTE'/
    # c    * '     THE NEAREST LINE ON THE SHORT-WAVELENGTH SIDE IS',
    # c    * I3,'  TO ',I3/)
    return
