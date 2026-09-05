# ======================================================================
# chunk11: synspec54.f 行 12333–13582
# 包含: PHTX, GETLAL, ALLARD, LYAHHE, READBF, PRETAB, VOIGTK, RTECD, RTEDFE
# ======================================================================


# PHTX 的 SAVE 局部数组（Fortran SAVE，跨调用保持），提升为模块级
_save_phtx_photi = np.zeros((MCROSS + 1, MFREQ + 1))          # SAVE PHOTI(MCROSS,MFREQ)
_save_phtx_ijp = np.zeros(MLEVEL + 1, dtype=np.int64)         # SAVE IJP(MLEVEL)
_save_phtx_ijq = np.zeros(MPHOT + 1, dtype=np.int64)          # SAVE IJQ(MPHOT)

# LYAHHE 的 SAVE 标量（DATA iread/0/，之后被修改，隐含 SAVE）
_save_lyahhe_iread = 0                                        # DATA IREAD/0/


def phtx(id, abso, emis, fre, icon):
    """SUBROUTINE PHTX(ID,ABSO,EMIS,fre,icon)

C     Opacity due to detailed photoionization (read from tables by
C     routine SIGAVS)

    对应 synspec54.f 行 12333–12433
    """
    photi = _save_phtx_photi          # SAVE 数组别名
    ijp = _save_phtx_ijp
    ijq = _save_phtx_ijq
    c3 = 1.4387886                    # PARAMETER (C3=1.4387886)
    planf = np.zeros(MFREQ + 1)       # PLANF(MFREQ)
    stimu = np.zeros(MFREQ + 1)       # STIMU(MFREQ)

    if C.IASV == 0 and C.NQHT == 0:
        return
    t = C.TEMP[id]
    nfre = C.NFREQ
    ij0 = 3                           # ij0 之后未被使用（原代码如此）
    if icon == 1:
        ij0 = 1
        nfre = C.NFREQC

    for ij in range(1, nfre + 1):     # DO 10 IJ=1,NFRE
        xx = fre[ij]
        x15 = xx * 1.0e-15
        bnu = BN * x15 * x15 * x15
        hkf = HK * xx
        exh = math.exp(hkf / t)
        planf[ij] = bnu / (exh - 1.0)
        stimu[ij] = 1.0 - 1.0 / exh

    if C.IASV != 0:                   # IF(IASV.EQ.0) GOTO 100
        if id == 1:
            for i in range(1, C.NLEVEL + 1):          # DO 40 I=1,NLEVEL
                if C.CRMX[i] == 0.0:
                    continue                          # GOTO 40
                ik1 = max(2, ijp[i])                  # MAX0
                for ij in range(3, nfre + 1):         # DO 42 IJ=3,NFRE
                    ik2 = ik1  # Fortran 中若 45 循环内未赋值，IK2 沿用上次值
                    for ik in range(ik1, C.NFCR[i] + 1):  # DO 45 IK=IK1,NFCR(I)
                        if C.FRECR[i, ik] < fre[ij]:
                            ik2 = ik
                            break                     # GOTO 46
                    # 标号 46
                    ik1 = ik2
                    if ij == 3:
                        ijp[i] = ik1
                    dfr = (fre[ij] - C.FRECR[i, ik1]) / \
                        (C.FRECR[i, ik1 - 1] - C.FRECR[i, ik1])
                    photi[i, ij] = C.CROSR[i, ik1] + \
                        dfr * (C.CROSR[i, ik1 - 1] - C.CROSR[i, ik1])
                photi[i, 1] = photi[i, 3]
                photi[i, 2] = photi[i, C.NFREQ]
        for i in range(1, C.NLEVEL + 1):              # DO 30 I=1,NLEVEL
            if C.CRMX[i] == 0.0:
                continue                              # GOTO 30
            pop = C.POPUL[i, id]
            for ij in range(1, nfre + 1):             # DO 20 IJ=1,NFRE
                ab = photi[i, ij] * pop * stimu[ij]
                abso[ij] = abso[ij] + ab
                emis[ij] = emis[ij] + ab * planf[ij]

    # 标号 100
    if C.NQHT == 0:
        return
    if id == 1:
        for i in range(1, C.NQHT + 1):                # DO 110 I=1,NQHT
            if C.CRMY[i] == 0.0:
                continue                              # GOTO 110
            ik1 = max(2, ijq[i])
            for ij in range(3, nfre + 1):             # DO 120 IJ=3,NFRE
                ik2 = ik1  # Fortran 中若 125 循环内未赋值，IK2 沿用上次值
                for ik in range(ik1, C.NFQHT[i] + 1):  # DO 125 IK=IK1,NFQHT(I)
                    if C.FRECQ[i, ik] < fre[ij]:
                        ik2 = ik
                        break                         # GOTO 126
                # 标号 126
                ik1 = ik2
                if ij == 3:
                    ijq[i] = ik1
                dfr = (fre[ij] - C.FRECQ[i, ik1]) / \
                    (C.FRECQ[i, ik1 - 1] - C.FRECQ[i, ik1])
                photi[i, ij] = C.QHOT[i, ik1] + \
                    dfr * (C.QHOT[i, ik1 - 1] - C.QHOT[i, ik1])
    for i in range(1, C.NQHT + 1):                    # DO 210 I=1,NQHT
        if C.CRMY[i] == 0.0:
            continue                                  # GOTO 210
        iat = int(C.AQHT[i])                          # int(AQHT(I))
        x = (C.AQHT[i] - float(iat) + 1.0e-4) * 100.0
        ion = int(x) + 1
        pop = C.RRR[id, ion, iat] * C.GQHT[i] * math.exp(-C.EQHT[i] * c3 / t)
        for ij in range(3, nfre + 1):                 # DO 220 IJ=3,NFRE
            ab = photi[i, ij] * pop * stimu[ij]
            abso[ij] = abso[ij] + ab
            emis[ij] = emis[ij] + ab * planf[ij]

    return


def getlal():
    """subroutine getlal

c     getlal reads in the profile functions for Lyman alpha, beta, gamma,
c     and Balmer alpha, including the quasi-molecular satellites;
c     valid for first and second order in neutral and ionized H density
c     modified routine provided originally by D. Koester

    对应 synspec54.f 行 12438–12530
    """
    # parameter (NXMAX=1400,NNMAX=5)
    nnmax = 5
    # TODO(port): Fortran 自由格式(list-directed) READ 在值不够时会自动续读下一条
    # 记录；这里按“每条记录一行、值齐全”解析，并用 _f 兼容 D 指数。
    _f = lambda s: float(s.replace('D', 'E').replace('d', 'e'))

    # Lyman alpha
    C.nxalp = 0
    if C.nunalp > 0:
        C.nunalp = 67
        open_unit(C.nunalp, './data/laquasi.dat', 'r')   # status='old'
        p = read_line(C.nunalp).split()
        C.nxalp = int(p[0])
        C.stnnea = _f(p[1])
        C.stncha = _f(p[2])
        C.vneua = _f(p[3])
        C.vchaa = _f(p[4])
        for i in range(1, C.nxalp + 1):
            p = read_line(C.nunalp).split()
            C.xlalp[i] = _f(p[0])
            for j in range(1, nnmax + 1):
                C.plalp[i, j] = _f(p[j])
        close_unit(C.nunalp)
        C.stnnea = 10.0 ** C.stnnea
        C.stncha = 10.0 ** C.stncha
        C.iwarna = 0
        # TODO(port): 原代码此处第二次 close(nunalp)；fortran.py 的 close_unit
        # 对未打开单元会抛 KeyError
        close_unit(C.nunalp)
        print()
        print(' read quasi-molecular data for L alpha')

    # Lyman beta
    C.nxbet = 0
    if C.nunbet > 0:
        C.nunbet = 67
        open_unit(C.nunbet, './data/lbquasi.dat', 'r')   # status='old'
        p = read_line(C.nunbet).split()
        C.nxbet = int(p[0])
        C.stnneb = _f(p[1])
        C.stnchb = _f(p[2])
        C.vneub = _f(p[3])
        C.vchab = _f(p[4])
        for i in range(1, C.nxbet + 1):
            p = read_line(C.nunbet).split()
            C.xlbet[i] = _f(p[0])
            for j in range(1, nnmax + 1):
                C.plbet[i, j] = _f(p[j])
        close_unit(C.nunbet)
        C.stnneb = 10.0 ** C.stnneb
        C.stnchb = 10.0 ** C.stnchb
        C.iwarnb = 0
        print(' read quasi-molecular data for L beta')

    # Lyman gamma
    C.nxgam = 0
    if C.nungam > 0:
        C.nungam = 67
        # 原代码 open 的是 nunalp（笔误），但两者都已被置为 67，语义一致
        open_unit(C.nunalp, './data/lgquasi.dat', 'r')   # status='old'
        p = read_line(C.nungam).split()
        C.nxgam = int(p[0])
        C.stnneg = _f(p[1])
        C.stnchg = _f(p[2])
        C.vneug = _f(p[3])
        C.vchag = _f(p[4])
        for i in range(1, C.nxgam + 1):
            p = read_line(C.nungam).split()
            C.xlgam[i] = _f(p[0])
            for j in range(1, nnmax + 1):
                C.plgam[i, j] = _f(p[j])
        close_unit(C.nungam)
        C.stnneg = 10.0 ** C.stnneg
        C.stnchg = 10.0 ** C.stnchg
        C.iwarng = 0
        print(' read quasi-molecular data for L gamma')

    # Balmer alpha
    C.nxbal = 0
    if C.nunbal > 0:
        C.nunbal = 67
        # 原代码 open 的是 nunalp（笔误），同上，均为 67
        open_unit(C.nunalp, './data/lhquasi.dat', 'r')   # status='old'
        p = read_line(C.nunbal).split()
        C.nxbal = int(p[0])
        C.stnnec = _f(p[1])
        C.stnchc = _f(p[2])
        C.vneuc = _f(p[3])
        C.vchac = _f(p[4])
        for i in range(1, C.nxbal + 1):
            p = read_line(C.nunbal).split()
            C.xlbal[i] = _f(p[0])
            for j in range(1, nnmax + 1):
                C.plbal[i, j] = _f(p[j])
        close_unit(C.nunbal)
        C.stnnec = 10.0 ** C.stnnec
        C.stnchc = 10.0 ** C.stnchc
        C.iwarnc = 0
        print(' read quasi-molecular data for H alpha')
    print()
    return


def allard(xl, hneutr, hcharg, prof, iq, jq):
    """subroutine allard(xl,hneutr,hcharg,prof,iq,jq)

c     quasi-molecular opacity for Lyman alpha, beta, and Balmer alpha
c     modified routine provided originally by D. Koester
c
c     Input:  xl:  wavelength in [A]
c             hneutr:  neutral H particle density [cm-3]
c             hcharg: ionized H particle density [cm-3]
c             iq:   quantum number of the lower level
c             jq:   quantum number of the upper level;
c                   =2  -  Lyman alpha
c                   =3  -  Lyman beta
c     Output: prof:  Lyman alpha line profile, normalized to 1.0e8
c             if integrated over A;
c             It then renormalized by multiplying by
c             8.853e-29*lambda_0^2*f_ij

    对应 synspec54.f 行 12535–12762

    prof 为被赋值的标量哑元 → 按约定返回全部标量哑元
    (xl, hneutr, hcharg, prof, iq, jq)。
    """
    # parameter (NXMAX=1400,NNMAX=5)
    # parameter (xnorma=..., xnormb=..., xnormg=..., xnormc=...)
    xnorma = 8.8528e-29 * 1215.6 * 1215.6 * 0.41618
    xnormb = 8.8528e-29 * 1025.73 * 1025.7 * 0.0791   # 原代码即 1025.73*1025.7
    xnormg = 8.8528e-29 * 972.53 * 972.53 * 0.0290
    xnormc = 8.8528e-29 * 6562.0 * 6562.0 * 0.6407

    prof = 0.0

    # Lyman alpha
    if iq == 1 and jq == 2:
        # c if(xl.lt.xlalp(1).or.xl.gt.xlalp(nxalp)) return
        if xl < C.xlalp[1]:
            return xl, hneutr, hcharg, prof, iq, jq
        vn1 = hneutr / C.stnnea
        vn2 = hcharg / C.stncha
        vns = vn1 * C.vneua + vn2 * C.vchaa
        if C.iwarna == 0:
            if vn1 * C.vneua > 0.3 or vn2 * C.vchaa > 0.3:
                print('          warning: density too high for',
                      ' Lyman alpha expansion')
                C.iwarna = 1
        vn11 = vn1 * vn1
        vn22 = vn2 * vn2
        vn12 = vn1 * vn2
        xnorm = 1.0 / (1.0 + vns + 0.5 * vns * vns)

        if xl <= C.xlalp[C.nxalp]:
            jl = 0
            ju = C.nxalp + 1
            # 标号 10: GO TO 10 → while 二分查找循环
            while ju - jl > 1:
                jm = idiv(ju + jl, 2)                 # Fortran 整数除法
                if (C.xlalp[C.nxalp] > C.xlalp[1]) == (xl > C.xlalp[jm]):  # .EQV.
                    jl = jm
                else:
                    ju = jm
            j = jl
            if j == 0:
                j = 1
            if j == C.nxalp:
                j = j - 1
            a1 = (xl - C.xlalp[j]) / (C.xlalp[j + 1] - C.xlalp[j])
            p1 = vn1 * ((1.0 - a1) * C.plalp[j, 1] + a1 * C.plalp[j + 1, 1])
            p11 = vn11 * ((1.0 - a1) * C.plalp[j, 2] + a1 * C.plalp[j + 1, 2])
            p2 = vn2 * ((1.0 - a1) * C.plalp[j, 3] + a1 * C.plalp[j + 1, 3])
            p22 = vn22 * ((1.0 - a1) * C.plalp[j, 4] + a1 * C.plalp[j + 1, 4])
            p12 = vn12 * ((1.0 - a1) * C.plalp[j, 5] + a1 * C.plalp[j + 1, 5])
            prof = (p1 + p2 + p11 + p22 + p12) * xnorm * xnorma
        else:
            j = C.nxalp - 1
            # c a1=(xl-xlalp(j))/(xlalp(j+1)-xlalp(j))
            a1 = 1.0
            p1 = vn1 * ((1.0 - a1) * C.plalp[j, 1] + a1 * C.plalp[j + 1, 1])
            p11 = vn11 * ((1.0 - a1) * C.plalp[j, 2] + a1 * C.plalp[j + 1, 2])
            p2 = vn2 * ((1.0 - a1) * C.plalp[j, 3] + a1 * C.plalp[j + 1, 3])
            p22 = vn22 * ((1.0 - a1) * C.plalp[j, 4] + a1 * C.plalp[j + 1, 4])
            p12 = vn12 * ((1.0 - a1) * C.plalp[j, 5] + a1 * C.plalp[j + 1, 5])
            pro0 = (p1 + p2 + p11 + p22 + p12) * xnorm * xnorma
            xlas = C.xlalp[C.nxalp]
            x0 = 1215.67
            dxlas = C.xlalp[C.nxalp] - x0
            dx = xl - x0
            prof = pro0 / (dx / dxlas) ** 2.5
        return xl, hneutr, hcharg, prof, iq, jq

    # Lyman beta
    if iq == 1 and jq == 3:
        if C.nxbet == 0:
            return xl, hneutr, hcharg, prof, iq, jq
        if xl < C.xlbet[1] or xl > C.xlbet[C.nxbet]:
            return xl, hneutr, hcharg, prof, iq, jq
        vn1 = hneutr / C.stnneb
        vn2 = hcharg / C.stnchb
        vns = vn1 * C.vneub + vn2 * C.vchab
        if C.iwarnb == 0:
            if vn1 * C.vneub > 0.3 or vn2 * C.vchab > 0.3:
                print('          warning: density too high for',
                      ' Lyman beta expansion')
                C.iwarnb = 1
        vn11 = vn1 * vn1
        vn22 = vn2 * vn2
        vn12 = vn1 * vn2
        xnorm = 1.0 / (1.0 + vns + 0.5 * vns * vns)

        jl = 0
        ju = C.nxbet + 1
        # 标号 20: GO TO 20 → while 二分查找循环
        while ju - jl > 1:
            jm = idiv(ju + jl, 2)
            if (C.xlbet[C.nxbet] > C.xlbet[1]) == (xl > C.xlbet[jm]):
                jl = jm
            else:
                ju = jm
        j = jl
        if j == 0:
            j = 1
        if j == C.nxbet:
            j = j - 1
        a1 = (xl - C.xlbet[j]) / (C.xlbet[j + 1] - C.xlbet[j])
        p1 = vn1 * ((1.0 - a1) * C.plbet[j, 1] + a1 * C.plbet[j + 1, 1])
        p11 = vn11 * ((1.0 - a1) * C.plbet[j, 2] + a1 * C.plbet[j + 1, 2])
        p2 = vn2 * ((1.0 - a1) * C.plbet[j, 3] + a1 * C.plbet[j + 1, 3])
        p22 = vn22 * ((1.0 - a1) * C.plbet[j, 4] + a1 * C.plbet[j + 1, 4])
        p12 = vn12 * ((1.0 - a1) * C.plbet[j, 5] + a1 * C.plbet[j + 1, 5])
        prof = (p1 + p2 + p11 + p22 + p12) * xnorm * xnormb
        return xl, hneutr, hcharg, prof, iq, jq

    # Lyman gamma
    if iq == 1 and jq == 4:
        if C.nxgam == 0:
            return xl, hneutr, hcharg, prof, iq, jq
        if xl < C.xlgam[1] or xl > C.xlgam[C.nxgam]:
            return xl, hneutr, hcharg, prof, iq, jq
        vn1 = hneutr / C.stnneg
        vn2 = hcharg / C.stnchg
        vns = vn1 * C.vneug + vn2 * C.vchag
        if C.iwarng == 0:
            if vn1 * C.vneug > 0.3 or vn2 * C.vchag > 0.3:
                print('          warning: density too high for',
                      ' Lyman gamma expansion')
                C.iwarng = 1
        vn11 = vn1 * vn1
        vn22 = vn2 * vn2
        vn12 = vn1 * vn2
        xnorm = 1.0 / (1.0 + vns + 0.5 * vns * vns)

        jl = 0
        ju = C.nxgam + 1
        # 标号 30: GO TO 30 → while 二分查找循环
        while ju - jl > 1:
            jm = idiv(ju + jl, 2)
            if (C.xlgam[C.nxgam] > C.xlgam[1]) == (xl > C.xlgam[jm]):
                jl = jm
            else:
                ju = jm
        j = jl
        if j == 0:
            j = 1
        if j == C.nxgam:
            j = j - 1
        a1 = (xl - C.xlgam[j]) / (C.xlgam[j + 1] - C.xlgam[j])
        p1 = vn1 * ((1.0 - a1) * C.plgam[j, 1] + a1 * C.plgam[j + 1, 1])
        p11 = vn11 * ((1.0 - a1) * C.plgam[j, 2] + a1 * C.plgam[j + 1, 2])
        p2 = vn2 * ((1.0 - a1) * C.plgam[j, 3] + a1 * C.plgam[j + 1, 3])
        p22 = vn22 * ((1.0 - a1) * C.plgam[j, 4] + a1 * C.plgam[j + 1, 4])
        p12 = vn12 * ((1.0 - a1) * C.plgam[j, 5] + a1 * C.plgam[j + 1, 5])
        prof = (p1 + p2 + p11 + p22 + p12) * xnorm * xnormg
        return xl, hneutr, hcharg, prof, iq, jq

    # Balmer alpha
    if iq == 2 and jq == 3:
        if xl < C.xlbal[1] or xl > C.xlbal[C.nxbal]:
            return xl, hneutr, hcharg, prof, iq, jq
        # c vn1=hneutr/stnnec
        vn1 = 0.0
        vn2 = hcharg / C.stnchc
        vns = vn1 * C.vneuc + vn2 * C.vchac
        vn11 = vn1 * vn1
        vn22 = vn2 * vn2
        vn12 = vn1 * vn2
        xnorm = 1.0 / (1.0 + vns + 0.5 * vns * vns)

        jl = 0
        ju = C.nxbal + 1
        # 标号 40: GO TO 40 → while 二分查找循环
        while ju - jl > 1:
            jm = idiv(ju + jl, 2)
            if (C.xlbal[C.nxbal] > C.xlbal[1]) == (xl > C.xlbal[jm]):
                jl = jm
            else:
                ju = jm
        j = jl
        if j == 0:
            j = 1
        if j == C.nxbal:
            j = j - 1
        a1 = (xl - C.xlbal[j]) / (C.xlbal[j + 1] - C.xlbal[j])
        p1 = vn1 * ((1.0 - a1) * C.plbal[j, 1] + a1 * C.plbal[j + 1, 1])
        p11 = vn11 * ((1.0 - a1) * C.plbal[j, 2] + a1 * C.plbal[j + 1, 2])
        p2 = vn2 * ((1.0 - a1) * C.plbal[j, 3] + a1 * C.plbal[j + 1, 3])
        p22 = vn22 * ((1.0 - a1) * C.plbal[j, 4] + a1 * C.plbal[j + 1, 4])
        p12 = vn12 * ((1.0 - a1) * C.plbal[j, 5] + a1 * C.plbal[j + 1, 5])
        prof = (p1 + p2 + p11 + p22 + p12) * xnorm * xnormc

    return xl, hneutr, hcharg, prof, iq, jq


def lyahhe(xl, ahe, prof):
    """subroutine lyahhe(xl,ahe,prof)

c     Lyman alpha broadening by helium - after N. Allard

    对应 synspec54.f 行 12768–12828

    prof 被赋值（且 iread=0 的首次调用中 dummy xl 被 READ 覆写，原代码如此）
    → 按约定返回全部标量哑元 (xl, ahe, prof)。
    """
    global _save_lyahhe_iread
    # parameter (nxmax=1000)
    nxmax = 1000
    xlhh0 = np.zeros(nxmax + 1)       # xlhh0(nxmax)
    sighh0 = np.zeros(nxmax + 1)      # sighh0(nxmax)
    # TODO(port): 自由格式 READ，_f 兼容 D 指数
    _f = lambda s: float(s.replace('D', 'E').replace('d', 'e'))

    if _save_lyahhe_iread == 0:
        # c nxhhe=679
        # c open(unit=67, file='siglyhhe_21_T14500.lam', status='old')
        it = 0
        for i in range(1, nxmax + 1):
            # read(67,*,err=5,end=5) xl,sig —— 读取出错或 EOF → 标号 5
            try:
                p = read_line(67).split()
                xl = _f(p[0])         # TODO(port): 哑元 xl 被 READ 覆写（原代码如此）
                sig = _f(p[1])
            except (EOFError, ValueError, IndexError):
                break                 # err=5 / end=5
            it = it + 1
            if C.nunhhe == 1:
                xl = 1.0 / (1.0e-8 * xl + 1.0 / 1215.67)
            xlhh0[it] = xl
            sighh0[it] = sig
        # 标号 5
        C.nxhhe = it
        for i in range(1, C.nxhhe + 1):
            C.xlhhe[i] = xlhh0[C.nxhhe - i + 1]
            C.sighhe[i] = sighh0[C.nxhhe - i + 1]
        # c do i=1,nxhhe
        # c    j=nxhhe-i+1
        # c    read(67,*) xlhhe(j),sighhe(j)
        # c end do
        close_unit(67)
        _save_lyahhe_iread = 1

    prof = 0.0
    if xl > C.xlhhe[C.nxhhe]:
        return xl, ahe, prof
    jl = 0
    ju = C.nxhhe + 1
    # 标号 10: GO TO 10 → while 二分查找循环
    while ju - jl > 1:
        jm = idiv(ju + jl, 2)
        if (C.xlhhe[C.nxhhe] > C.xlhhe[1]) == (xl > C.xlhhe[jm]):  # .EQV.
            jl = jm
        else:
            ju = jm
    j = jl
    if j == 0:
        j = 1
    if j == C.nxhhe:
        j = j - 1
    a1 = (xl - C.xlhhe[j]) / (C.xlhhe[j + 1] - C.xlhhe[j])
    s1 = (1.0 - a1) * C.sighhe[j] + a1 * C.sighhe[j + 1]
    prof = s1 * ahe / C.sthe * 6.2831855
    return xl, ahe, prof


def readbf():
    """subroutine readbf

c     auxiliary subroutine for enabling reading of input data with
c     comments
c
c     lines beginning with ! or * are understood as comments

    对应 synspec54.f 行 12834–12853
    """
    # 501 format(a)
    # 显式以 w+ 打开 IBUFF(=fort.95): 隐式打开是 "w" 只写模式,
    # 后面 rewind 后要回读, w+ 保证可读且每次运行截断旧内容
    open_unit(IBUFF, 'fort.95', 'w+')
    # 标号 10 → while 循环开头
    while True:
        # read(5,501,end=20) buff
        # TODO(port): read_stdin_line 遇 EOF 抛 SystemExit；此处按 END=20 捕获并跳出
        try:
            buff = read_stdin_line()
        except SystemExit:
            break                     # END=20 → 标号 20
        # buff(1:1) 比较；Python 空串切片安全（Fortran 空白行首字符为空格）
        if buff[:1] == '!' or buff[:1] == '*':
            continue                  # GO TO 10
        write_line(IBUFF, buff)       # write(ibuff,501) buff
        # GO TO 10
    # 标号 20
    rewind_unit(IBUFF)                # rewind ibuff
    return


def pretab():
    """SUBROUTINE PRETAB

C     pretabulate expansion coefficients for the Voigt function
C     200 steps per doppler width - up to 10 Doppler widths

    对应 synspec54.f 行 12860–12898
    """
    # PARAMETER (VSTEPS=200.,MVOI=2001)
    vsteps = 200.0
    mvoi = 2001
    # DATA TABVI/.../（DATA 后不再修改 → 函数内直接赋值）
    tabvi = np.zeros(82)
    tabvi[1:] = [
        0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3,
        1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7,
        2.8, 2.9, 3.0, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9, 4.0, 4.2,
        4.4, 4.6, 4.8, 5.0, 5.2, 5.4, 5.6, 5.8, 6.0, 6.2, 6.4, 6.6, 6.8, 7.0,
        7.2, 7.4, 7.6, 7.8, 8.0, 8.2, 8.4, 8.6, 8.8, 9.0, 9.2, 9.4, 9.6, 9.8,
        10.0, 10.2, 10.4, 10.6, 10.8, 11.0, 11.2, 11.4, 11.6, 11.8, 12.0]
    # DATA TABH1/.../
    tabh1 = np.zeros(82)
    tabh1[1:] = [
        -1.12838, -1.10596, -1.04048, -0.93703, -0.80346, -0.64945,
        -0.48552, -0.32192, -0.16772, -0.03012, 0.08594, 0.17789, 0.24537,
        0.28981, 0.31394, 0.32130, 0.31573, 0.30094, 0.28027, 0.25648,
        0.231726, 0.207528, 0.184882, 0.164341, 0.146128, 0.130236, 0.116515,
        0.104739, 0.094653, 0.086005, 0.078565, 0.072129, 0.066526, 0.061615,
        0.057281, 0.053430, 0.049988, 0.046894, 0.044098, 0.041561, 0.039250,
        0.035195, 0.031762, 0.028824, 0.026288, 0.024081, 0.022146, 0.020441,
        0.018929, 0.017582, 0.016375, 0.015291, 0.014312, 0.013426, 0.012620,
        0.0118860, 0.0112145, 0.0105990, 0.0100332, 0.0095119, 0.0090306,
        0.0085852, 0.0081722, 0.0077885, 0.0074314, 0.0070985, 0.0067875,
        0.0064967, 0.0062243, 0.0059688, 0.0057287, 0.0055030, 0.0052903,
        0.0050898, 0.0049006, 0.0047217, 0.0045526, 0.0043924, 0.0042405,
        0.0040964, 0.0039595]

    n = mvoi                              # N=MVOI
    for i in range(1, n + 1):             # DO 10 I=1,N
        C.H0TAB[i] = float(i - 1) / vsteps
    # INTERP 不修改标量哑元 → 调用点不解包
    interp(tabvi, tabh1, C.H0TAB, C.H1TAB, 81, n, 2, 0, 0)
    for i in range(1, n + 1):             # DO 20 I=1,N
        vv = (float(i - 1) / vsteps) ** 2
        C.H0TAB[i] = math.exp(-vv)
        C.H2TAB[i] = C.H0TAB[i] - (vv + vv) * C.H0TAB[i]
    return


def voigtk(a, v):
    """FUNCTION VOIGTK(A,V)

C     Voigt function after Kurucz (in Computational Astrophysics)

    对应 synspec54.f 行 12905–12945
    """
    # PARAMETER (MVOI=2001)
    # PARAMETER (ONE=1., THREE=3., TEN=10., FIFTN=15., TWOH=200., ...)
    one = 1.0
    three = 3.0
    ten = 10.0
    fiftn = 15.0
    twoh = 200.0
    c14142 = 1.4142
    c11283 = 1.12838
    c15 = 1.5
    c32 = 3.2
    c05642 = 0.5642
    c79788 = 0.79788
    c02 = 0.2
    c14 = 1.4
    c37613 = 0.37613
    c23 = 2.0 / 3.0
    cv1 = -0.122727278
    cv2 = 0.532770573
    cv3 = -0.96284325
    cv4 = 0.979895032

    iv = int(v * twoh + c15)
    if a < c02:
        if v <= ten:
            voigtk_val = (C.H2TAB[iv] * a + C.H1TAB[iv]) * a + C.H0TAB[iv]
        else:
            voigtk_val = c05642 * a / (v * v)
        return voigtk_val
    if a > c14 or a + v > c32:
        # IF(A.GT.C14) GO TO 10 / IF(A+V.GT.C32) GO TO 10 → 标号 10
        aa = a * a
        vv = v * v
        u = (aa + vv) * c14142
        uu = u * u
        voigtk_val = ((((aa - ten * vv) * aa * three + fiftn * vv * vv) / uu
                       + three * vv - aa) / uu + one) * a * c79788 / u
        return voigtk_val
    vv = v * v
    hh1 = C.H1TAB[iv] + C.H0TAB[iv] * c11283
    hh2 = C.H2TAB[iv] + hh1 * c11283 - C.H0TAB[iv]
    hh3 = (one - C.H2TAB[iv]) * c37613 - hh1 * c23 * vv + hh2 * c11283
    hh4 = (three * hh3 - hh1) * c37613 + C.H0TAB[iv] * c23 * vv * vv
    voigtk_val = ((((hh4 * a + hh3) * a + hh2) * a + hh1) * a + C.H0TAB[iv]) * \
        (((cv1 * a + cv2) * a + cv3) * a + cv4)
    return voigtk_val


def rtecd():
    """SUBROUTINE RTECD

C     solution of the radiative transfer equation by Feautrier method
C     for two continuum points
C     used when one employs RTEDFE, ie. the DFE method for the
C     transfer equation for the inner frequency points

    对应 synspec54.f 行 12952–13403
    """
    # PARAMETER (UN=1.D0, HALF=0.5D0)
    un = 1.0
    half = 0.5
    # PARAMETER (THIRD=UN/3., QUART=UN/4., SIXTH=UN/6.D0)
    third = un / 3.0
    quart = un / 4.0
    sixth = un / 6.0
    # PARAMETER (TAUREF = 0.6666666666667)
    tauref = 0.6666666666667
    # 局部数组（Fortran 1 基）
    d = np.zeros((4, 4, MDEPTH + 1))      # D(3,3,MDEPTH)
    anu = np.zeros((4, MDEPTH + 1))       # ANU(3,MDEPTH)
    aanu = np.zeros(MDEPTH + 1)           # AANU(MDEPTH)
    ddd = np.zeros(MDEPTH + 1)            # DDD(MDEPTH)
    aa = np.zeros((4, 4))                 # AA(3,3)
    bb = np.zeros((4, 4))                 # BB(3,3)
    cc = np.zeros((4, 4))                 # CC(3,3)
    vl = np.zeros(4)                      # VL(3)
    # DATA AMU/.887298334620742D0,.5D0,.112701665379258D0/
    amu = np.array([0.0, 0.887298334620742, 0.5, 0.112701665379258])
    # DATA WTMU/.277777777777778D0,.444444444444444D0,.277777777777778D0/
    wtmu = np.array([0.0, 0.277777777777778, 0.444444444444444, 0.277777777777778])
    dt = np.zeros(MDEPTH + 1)             # DT(MDEPTH)
    tau = np.zeros(MDEPTH + 1)            # TAU(MDEPTH)
    rdd = np.zeros(MDEPTH + 1)            # RDD(MDEPTH)
    fkk = np.zeros(MDEPTH + 1)            # FKK(MDEPTH)
    st0 = np.zeros(MDEPTH + 1)            # ST0(MDEPTH)
    ss0 = np.zeros(MDEPTH + 1)            # SS0(MDEPTH)
    rint = np.zeros((MDEPTH + 1, MMU + 1))  # RINT(MDEPTH,MMU)

    C.NMU = 3                             # NMU=3（COMMON /BASNUM/ 变量）
    nd1 = C.ND - 1
    # TODO(port): Fortran 中 IREF 未显式初始化（条件不满足时保留旧值/未定义），
    # 这里按 RTEDFE 的显式初始化取 1
    iref = 1

    # loop over two continuum frequencies
    for ij in range(1, 3):                # DO 100 IJ=1,2
        taumin = C.CH[ij, 1] / C.DENS[1] * C.DM[1] * half
        tau[1] = taumin
        for i in range(1, nd1 + 1):       # DO I=1,ND1
            dt[i] = (C.DM[i + 1] - C.DM[i]) * \
                (C.CH[ij, i + 1] / C.DENS[i + 1] + C.CH[ij, i] / C.DENS[i]) * half
            st0[i] = C.ET[ij, i] / C.CH[ij, i]
            ss0[i] = -C.SC[ij, i] / C.CH[ij, i]
            tau[i + 1] = tau[i] + dt[i]
            if tau[i] <= tauref and tau[i + 1] > tauref:
                iref = i
        st0[C.ND] = C.ET[ij, C.ND] / C.CH[ij, C.ND]
        ss0[C.ND] = -C.SC[ij, C.ND] / C.CH[ij, C.ND]
        fr = C.FREQ[ij]
        bnu = BN * (fr * 1.0e-15) ** 3
        pland = bnu / (math.exp(HK * fr / C.TEMP[C.ND]) - un)
        dplan = bnu / (math.exp(HK * fr / C.TEMP[C.ND - 1]) - un)
        dplan = (pland - dplan) / dt[nd1]

        # +++++++++++++++++++++++++++++++++++++++++
        # FIRST PART  -  VARIABLE EDDINGTON FACTORS
        # +++++++++++++++++++++++++++++++++++++++++

        # Allowance for wind blanketing
        alb1 = 0.0
        for i in range(1, C.NMU + 1):     # DO I=1,NMU
            # ************************
            # UPPER BOUNDARY CONDITION
            # ************************
            id = 1
            dtp1 = dt[1]
            q0 = 0.0
            p0 = 0.0
            # allowance for non-zero optical depth at the first depth point
            tamm = taumin / amu[i]
            if tamm > 0.01:
                p0 = un - math.exp(-tamm)
            else:
                p0 = tamm * (un - half * tamm * (un - tamm * third * (un - quart * tamm)))
            ex = un - p0                  # EX 之后未被使用（原代码如此）
            q0 = q0 + p0 * amu[i] * wtmu[i]
            div = dtp1 / amu[i] * third
            vl[i] = div * (st0[id] + half * st0[id + 1]) + st0[id] * p0
            for j in range(1, C.NMU + 1):  # DO J=1,NMU
                bb[i, j] = ss0[id] * wtmu[j] * (div + p0) - alb1 * wtmu[j]
                cc[i, j] = -half * div * ss0[id + 1] * wtmu[j]
            bb[i, i] = bb[i, i] + amu[i] / dtp1 + un + div
            cc[i, i] = cc[i, i] + amu[i] / dtp1 - half * div
            anu[i, id] = 0.0

        # Matrix inversion: instead of calling MATINV, a very fast inlined
        # routine MINV3 for a specific 3 x 3 matrix inversion
        #
        # CALL MATINV(BB,NMU,3)
        #
        # ******************************
        bb[2, 1] = bb[2, 1] / bb[1, 1]
        bb[2, 2] = bb[2, 2] - bb[2, 1] * bb[1, 2]
        bb[2, 3] = bb[2, 3] - bb[2, 1] * bb[1, 3]
        bb[3, 1] = bb[3, 1] / bb[1, 1]
        bb[3, 2] = (bb[3, 2] - bb[3, 1] * bb[1, 2]) / bb[2, 2]
        bb[3, 3] = bb[3, 3] - bb[3, 1] * bb[1, 3] - bb[3, 2] * bb[2, 3]

        bb[3, 2] = -bb[3, 2]
        bb[3, 1] = -bb[3, 1] - bb[3, 2] * bb[2, 1]
        bb[2, 1] = -bb[2, 1]

        bb[3, 3] = un / bb[3, 3]
        bb[2, 3] = -bb[2, 3] * bb[3, 3] / bb[2, 2]
        bb[2, 2] = un / bb[2, 2]
        bb[1, 3] = -(bb[1, 2] * bb[2, 3] + bb[1, 3] * bb[3, 3]) / bb[1, 1]
        bb[1, 2] = -bb[1, 2] * bb[2, 2] / bb[1, 1]
        bb[1, 1] = un / bb[1, 1]

        bb[1, 1] = bb[1, 1] + bb[1, 2] * bb[2, 1] + bb[1, 3] * bb[3, 1]
        bb[1, 2] = bb[1, 2] + bb[1, 3] * bb[3, 2]
        bb[2, 1] = bb[2, 2] * bb[2, 1] + bb[2, 3] * bb[3, 1]
        bb[2, 2] = bb[2, 2] + bb[2, 3] * bb[3, 2]
        bb[3, 1] = bb[3, 3] * bb[3, 1]
        bb[3, 2] = bb[3, 3] * bb[3, 2]
        # ******************************

        for i in range(1, C.NMU + 1):     # DO I=1,NMU
            for j in range(1, C.NMU + 1):  # DO J=1,NMU
                s = 0.0
                for k in range(1, C.NMU + 1):  # DO K=1,NMU
                    s = s + bb[i, k] * cc[k, j]
                d[i, j, id] = s
                anu[i, 1] = anu[i, 1] + bb[i, j] * vl[j]

        # *******************
        # NORMAL DEPTH POINTS
        # *******************
        for id in range(2, nd1 + 1):      # DO ID=2,ND1
            dtm1 = dtp1
            dtp1 = dt[id]
            dt0 = half * (dtm1 + dtp1)
            al = un / dtm1 / dt0
            ga = un / dtp1 / dt0
            be = al + ga
            a = (un - half * al * dtp1 * dtp1) * sixth
            # Fortran 局部变量 C 与 commons 别名 C 冲突 → 改名 c_l
            c_l = (un - half * ga * dtm1 * dtm1) * sixth
            b = un - a - c_l
            vl0 = a * st0[id - 1] + b * st0[id] + c_l * st0[id + 1]
            for i in range(1, C.NMU + 1):
                for j in range(1, C.NMU + 1):
                    aa[i, j] = -a * ss0[id - 1] * wtmu[j]
                    cc[i, j] = -c_l * ss0[id + 1] * wtmu[j]
                    bb[i, j] = b * ss0[id] * wtmu[j]
            for i in range(1, C.NMU + 1):
                div = amu[i] ** 2
                vl[i] = vl0
                aa[i, i] = aa[i, i] + div * al - a
                cc[i, i] = cc[i, i] + div * ga - c_l
                bb[i, i] = bb[i, i] + div * be + b
            for i in range(1, C.NMU + 1):
                s1 = 0.0
                for j in range(1, C.NMU + 1):
                    s = 0.0
                    s1 = s1 + aa[i, j] * anu[j, id - 1]
                    for k in range(1, C.NMU + 1):
                        s = s + aa[i, k] * d[k, j, id - 1]
                    bb[i, j] = bb[i, j] - s
                vl[i] = vl[i] + s1

            # Matrix inversion: instead of calling MATINV, a very fast inlined
            # routine MINV3 for a specific 3 x 3 matrix inversion
            #
            # CALL MATINV(BB,NMU,3)
            #
            # ******************************
            bb[2, 1] = bb[2, 1] / bb[1, 1]
            bb[2, 2] = bb[2, 2] - bb[2, 1] * bb[1, 2]
            bb[2, 3] = bb[2, 3] - bb[2, 1] * bb[1, 3]
            bb[3, 1] = bb[3, 1] / bb[1, 1]
            bb[3, 2] = (bb[3, 2] - bb[3, 1] * bb[1, 2]) / bb[2, 2]
            bb[3, 3] = bb[3, 3] - bb[3, 1] * bb[1, 3] - bb[3, 2] * bb[2, 3]

            bb[3, 2] = -bb[3, 2]
            bb[3, 1] = -bb[3, 1] - bb[3, 2] * bb[2, 1]
            bb[2, 1] = -bb[2, 1]

            bb[3, 3] = un / bb[3, 3]
            bb[2, 3] = -bb[2, 3] * bb[3, 3] / bb[2, 2]
            bb[2, 2] = un / bb[2, 2]
            bb[1, 3] = -(bb[1, 2] * bb[2, 3] + bb[1, 3] * bb[3, 3]) / bb[1, 1]
            bb[1, 2] = -bb[1, 2] * bb[2, 2] / bb[1, 1]
            bb[1, 1] = un / bb[1, 1]

            bb[1, 1] = bb[1, 1] + bb[1, 2] * bb[2, 1] + bb[1, 3] * bb[3, 1]
            bb[1, 2] = bb[1, 2] + bb[1, 3] * bb[3, 2]
            bb[2, 1] = bb[2, 2] * bb[2, 1] + bb[2, 3] * bb[3, 1]
            bb[2, 2] = bb[2, 2] + bb[2, 3] * bb[3, 2]
            bb[3, 1] = bb[3, 3] * bb[3, 1]
            bb[3, 2] = bb[3, 3] * bb[3, 2]
            # ******************************

            for i in range(1, C.NMU + 1):
                anu[i, id] = 0.0
                for j in range(1, C.NMU + 1):
                    s = 0.0
                    for k in range(1, C.NMU + 1):
                        s = s + bb[i, k] * cc[k, j]
                    d[i, j, id] = s
                    anu[i, id] = anu[i, id] + bb[i, j] * vl[j]

        # ************
        # LOWER BOUNDARY CONDITION
        # ************
        id = C.ND
        for i in range(1, C.NMU + 1):
            aa[i, i] = amu[i] / dtp1
            vl[i] = pland + amu[i] * dplan + aa[i, i] * anu[i, id - 1]
            for j in range(1, C.NMU + 1):
                bb[i, j] = -aa[i, i] * d[i, j, id - 1]
            bb[i, i] = bb[i, i] + aa[i, i] + un

        # Matrix inversion: instead of calling MATINV, a very fast inlined
        # routine MINV3 for a specific 3 x 3 matrix inversion
        #
        # CALL MATINV(BB,NMU,3)
        #
        # ******************************
        bb[2, 1] = bb[2, 1] / bb[1, 1]
        bb[2, 2] = bb[2, 2] - bb[2, 1] * bb[1, 2]
        bb[2, 3] = bb[2, 3] - bb[2, 1] * bb[1, 3]
        bb[3, 1] = bb[3, 1] / bb[1, 1]
        bb[3, 2] = (bb[3, 2] - bb[3, 1] * bb[1, 2]) / bb[2, 2]
        bb[3, 3] = bb[3, 3] - bb[3, 1] * bb[1, 3] - bb[3, 2] * bb[2, 3]

        bb[3, 2] = -bb[3, 2]
        bb[3, 1] = -bb[3, 1] - bb[3, 2] * bb[2, 1]
        bb[2, 1] = -bb[2, 1]

        bb[3, 3] = un / bb[3, 3]
        bb[2, 3] = -bb[2, 3] * bb[3, 3] / bb[2, 2]
        bb[2, 2] = un / bb[2, 2]
        bb[1, 3] = -(bb[1, 2] * bb[2, 3] + bb[1, 3] * bb[3, 3]) / bb[1, 1]
        bb[1, 2] = -bb[1, 2] * bb[2, 2] / bb[1, 1]
        bb[1, 1] = un / bb[1, 1]

        bb[1, 1] = bb[1, 1] + bb[1, 2] * bb[2, 1] + bb[1, 3] * bb[3, 1]
        bb[1, 2] = bb[1, 2] + bb[1, 3] * bb[3, 2]
        bb[2, 1] = bb[2, 2] * bb[2, 1] + bb[2, 3] * bb[3, 1]
        bb[2, 2] = bb[2, 2] + bb[2, 3] * bb[3, 2]
        bb[3, 1] = bb[3, 3] * bb[3, 1]
        bb[3, 2] = bb[3, 3] * bb[3, 2]
        # ******************************

        for i in range(1, C.NMU + 1):
            anu[i, id] = 0.0
            for j in range(1, C.NMU + 1):
                d[i, j, id] = 0.0
                anu[i, id] = anu[i, id] + bb[i, j] * vl[j]

        # ************
        # BACKSOLUTION
        # ************
        for id in range(C.ND - 1, 0, -1):  # DO ID=ND-1,1,-1
            for i in range(1, C.NMU + 1):
                for j in range(1, C.NMU + 1):
                    anu[i, id] = anu[i, id] + d[i, j, id] * anu[j, id + 1]
            aj = 0.0
            ak = 0.0
            for i in range(1, C.NMU + 1):
                div = wtmu[i] * anu[i, id]
                aj = aj + div
                ak = ak + div * amu[i] ** 2
            fkk[id] = ak / aj

        # surface Eddington actor
        ah = 0.0
        for i in range(1, C.NMU + 1):
            ah = ah + wtmu[i] * amu[i] * anu[i, 1]
        fh = ah / aj - half * alb1        # AJ 为回代循环最后一次(ID=1)的值

        fkk[C.ND] = third

        # +++++++++++++++++++++++++++++++++++++++++
        # SECOND PART  -  DETERMINATION OF THE MEAN INTENSITIES
        # RECALCULATION OF THE TRANSFER EQUATION WITH GIVEN EDDINGTON FACTORS
        # +++++++++++++++++++++++++++++++++++++++++
        dtp1 = dt[1]
        div = dtp1 * third
        bbb = fkk[1] / dtp1 + fh + div + ss0[1] * (div + q0)
        ccc = fkk[2] / dtp1 - half * div * (un + ss0[2])
        vll = div * (st0[1] + half * st0[2]) + st0[1] * q0
        aanu[1] = vll / bbb
        ddd[1] = ccc / bbb
        for id in range(2, nd1 + 1):      # DO ID=2,ND1
            dtm1 = dtp1
            dtp1 = dt[id]
            dt0 = half * (dtp1 + dtm1)
            al = un / dtm1 / dt0
            ga = un / dtp1 / dt0
            a = (un - half * dtp1 * dtp1 * al) * sixth
            c_l = (un - half * dtm1 * dtm1 * ga) * sixth   # Fortran 局部 C
            aaa = al * fkk[id - 1] - a * (un + ss0[id - 1])
            ccc = ga * fkk[id + 1] - c_l * (un + ss0[id + 1])
            bbb = (al + ga) * fkk[id] + (un - a - c_l) * (un + ss0[id])
            vll = a * st0[id - 1] + c_l * st0[id + 1] + (un - a - c_l) * st0[id]
            bbb = bbb - aaa * ddd[id - 1]
            ddd[id] = ccc / bbb
            aanu[id] = (vll + aaa * aanu[id - 1]) / bbb
        bbb = fkk[C.ND] / dtp1 + half
        aaa = fkk[nd1] / dtp1
        bbb = bbb - aaa * ddd[nd1]
        vll = half * pland + dplan * third
        rdd[C.ND] = (vll + aaa * aanu[nd1]) / bbb
        for iid in range(1, nd1 + 1):     # DO IID=1,ND1
            id = C.ND - iid
            rdd[id] = aanu[id] + ddd[id] * rdd[id + 1]
        C.FLUX[ij] = fh * rdd[1]

        if ij == 1:
            for id in range(1, C.ND + 1):
                C.SCC1[id] = -rdd[id] * ss0[id] * C.CH[1, id]
        else:
            for id in range(1, C.ND + 1):
                C.SCC2[id] = -rdd[id] * ss0[id] * C.CH[2, id]

        # if needed (if iprin.ge.3), output of interesting physical
        # quantities at the monochromatic optical depth  tau(nu)=2/3
        if C.IPRIN >= 3:
            t0 = math.log(tau[iref + 1] / tau[iref])
            x0 = math.log(tau[iref + 1] / tauref) / t0
            x1 = math.log(tauref / tau[iref]) / t0
            dmref = math.exp(math.log(C.DM[iref]) * x0 + math.log(C.DM[iref + 1]) * x1)
            tref = math.exp(math.log(C.TEMP[iref]) * x0 + math.log(C.TEMP[iref + 1]) * x1)
            stref = math.exp(math.log(st0[iref]) * x0 + math.log(st0[iref + 1]) * x1)
            scref = math.exp(math.log(-ss0[iref]) * x0 + math.log(-ss0[iref + 1]) * x1)
            ssref = math.exp(math.log(-ss0[iref] * rdd[iref]) * x0 +
                             math.log(-ss0[iref + 1] * rdd[iref + 1]) * x1)
            sref = stref + ssref
            alm = 2.997925e18 / C.FREQ[ij]
            # 636 FORMAT(1H ,I3,F10.3,I4,1PE10.3,0PF10.1,1X,1P3E10.3,E11.3)
            write_line(96, " %3d%10.3f%4d%10.3E%10.1f %10.3E%10.3E%10.3E%11.3E"
                       % (ij, alm, iref, dmref, tref, scref, stref, ssref, sref))

        # ********************************************************************
        #
        # THIRD PART  -  DETERMINATION OF THE SPECIFIC INTENSITIES
        # RECALCULATION OF THE TRANSFER EQUATION WITH GIVEN SOURCE FUNCTION
        #
        if C.IFLUX == 0:
            continue                      # go to 100
        for imu in range(1, C.NMU0 + 1):  # DO IMU=1,NMU0
            anx = C.ANGL[imu]
            dtp1 = dt[1]
            div = dtp1 * third / anx

            tamm = taumin / anx
            if tamm < 0.01:
                p0 = tamm * (un - half * tamm * (un - tamm * third * (un - quart * tamm)))
            else:
                p0 = un - math.exp(-tamm)

            bbb = anx / dtp1 + un + div
            ccc = anx / dtp1 - half * div
            vll = (div + p0) * (st0[1] - ss0[1] * rdd[1]) + \
                half * div * (st0[2] - ss0[2] * rdd[2])
            aanu[1] = vll / bbb
            ddd[1] = ccc / bbb
            div = anx * anx
            for id in range(2, nd1 + 1):  # DO ID=2,ND1
                dtm1 = dt[id - 1]
                dtp1 = dt[id]
                dt0 = half * (dtp1 + dtm1)
                al = un / dtm1 / dt0
                ga = un / dtp1 / dt0
                a = (un - half * dtp1 * dtp1 * al) * sixth
                c_l = (un - half * dtm1 * dtm1 * ga) * sixth   # Fortran 局部 C
                aaa = div * al - a
                ccc = div * ga - c_l
                bbb = div * (al + ga) + un - a - c_l
                vll = a * (st0[id - 1] - ss0[id - 1] * rdd[id - 1]) + \
                    c_l * (st0[id + 1] - ss0[id + 1] * rdd[id + 1]) + \
                    (un - a - c_l) * (st0[id] - ss0[id] * rdd[id])
                bbb = bbb - aaa * ddd[id - 1]
                ddd[id] = ccc / bbb
                aanu[id] = (vll + aaa * aanu[id - 1]) / bbb

            # Lower boundary condition
            aaa = anx / dtp1
            bbb = aaa + un
            vll = pland + anx * dplan

            rint[C.ND, imu] = (vll + aaa * aanu[nd1]) / (bbb - aaa * ddd[nd1])
            for iid in range(1, nd1 + 1):  # DO IID=1,ND1
                id = C.ND - iid
                rint[id, imu] = aanu[id] + ddd[id] * rint[id + 1, imu]

        flx = 0.0
        for imu in range(1, C.NMU0 + 1):  # DO IMU=1,NMU0
            rint[1, imu] = rint[1, imu] / half
            flx = flx + C.ANGL[imu] * C.WANGL[imu] * rint[1, imu]
        flx = flx * half

        # output of emergent specific intensities in continuum to Unit 18
        if C.IFLUX >= 1:
            # 641 FORMAT(1H ,f10.3,1pe15.5/(1P5E15.5))
            write_line(18, " %10.3f%15.5E" % (C.WLAM[ij], flx))
            for k in range(1, C.NMU0 + 1, 5):
                write_line(18, "".join("%15.5E" % rint[1, imu]
                                       for imu in range(k, min(k + 5, C.NMU0 + 1))))
        # 100 CONTINUE

    # call rtedfe for the internal points
    rtedfe()                              # CALL RTEDFE（无参数）

    return


def rtedfe():
    """SUBROUTINE RTEDFE

C     Solution of the radiative transfer equation - frequency by
C     frequency - for the known source function.
C
C     The numerical method used:
c     Discontinuous Finite Element (DFE) method
c     Castor, Dykema, Klein, 1992, ApJ 387, 561.
C
C     Input through blank COMMON block:
C      CH     - two-dimensional array  absorption coefficient (frequency,
C               depth)
C      ET     - emission coefficient (frequency, depth)

    对应 synspec54.f 行 13410–13577
    """
    # PARAMETER (ONE=1.,TWO=2.,HALF=0.5)
    one = 1.0
    two = 2.0
    half = 0.5
    # PARAMETER (TAUREF = 0.6666666666667)
    tauref = 0.6666666666667
    # 局部数组（Fortran 1 基）
    dt = np.zeros(MDEPTH + 1)             # DT(MDEPTH)
    st0 = np.zeros(MDEPTH + 1)            # ST0(MDEPTH)
    ab0 = np.zeros(MDEPTH + 1)            # AB0(MDEPTH)
    deldm = np.zeros(MDEPTH + 1)          # DELDM(MDEPTH)
    dtau = np.zeros(MDEPTH + 1)           # dtau(mdepth)
    rip = np.zeros(MDEPTH + 1)            # rip(mdepth)
    rim = np.zeros(MDEPTH + 1)            # rim(mdepth)
    riup = np.zeros(MDEPTH + 1)           # riup(mdepth)
    # DATA AMU/.887298334620742D0,.5D0,.112701665379258D0/
    amu = np.array([0.0, 0.887298334620742, 0.5, 0.112701665379258])
    # DATA WTMU/.277777777777778D0,.444444444444444D0,.277777777777778D0/
    wtmu = np.array([0.0, 0.277777777777778, 0.444444444444444, 0.277777777777778])
    rint1 = np.zeros(MMU + 1)             # RINT1(MMU)
    amui = np.zeros(MMU + 1)              # AMUI(MMU)
    amuw = np.zeros(MMU + 1)              # AMUW(MMU)
    tau = np.zeros(MDEPTH + 1)            # TAU(MDEPTH)
    ss0 = np.zeros(MDEPTH + 1)            # SS0(MDEPTH)

    for i in range(1, C.ND):              # DO I=1,ND-1
        deldm[i] = half * (C.DM[i + 1] - C.DM[i])

    # angle points
    if C.IFLUX == 0:
        nmus = C.NMU
        for i in range(1, C.NMU + 1):
            amui[i] = amu[i]
            amuw[i] = amu[i] * wtmu[i]
    elif C.IFLUX == 1:
        nmus = C.NMU0
        for i in range(1, nmus + 1):
            amui[i] = C.ANGL[i]
            amuw[i] = C.ANGL[i] * C.WANGL[i]
    else:
        nmus = 0   # TODO(port): 原代码 IFLUX 既非 0 亦非 1 时 NMUS 未定义

    # overall loop over frequencies
    for ij in range(1, C.NFREQ + 1):      # DO IJ=1,NFREQ
        fr = C.FREQ[ij]

        # total source function
        for id in range(1, C.ND + 1):     # DO ID=1,ND
            ab0[id] = C.CH[ij, id]
            sct = C.FRX1[ij] * C.SCC2[id] + C.FRX2[ij] * C.SCC1[id]
            st0[id] = (C.ET[ij, id] + sct) / ab0[id]
            ss0[id] = -sct / ab0[id]
        ah = 0.0

        # optical depth scale
        tau[1] = 0.0
        iref = 1
        for id in range(1, C.ND):         # DO ID=1,ND-1
            dt[id] = deldm[id] * (ab0[id + 1] / C.DENS[id + 1] + ab0[id] / C.DENS[id])
            tau[id + 1] = tau[id] + dt[id]
            if tau[id] <= tauref and tau[id + 1] > tauref:
                iref = id
        C.IREFD[ij] = iref

        # quantities for the lower boundary condition
        fr15 = fr * 1.0e-15
        bnu = BN * fr15 * fr15 * fr15
        pland = bnu / (math.exp(HK * fr / C.TEMP[C.ND]) - one)
        dplan = bnu / (math.exp(HK * fr / C.TEMP[C.ND - 1]) - one)
        dplan = (pland - dplan) / dt[C.ND - 1]

        # loop over angle poits
        for i in range(1, nmus + 1):      # DO I=1,NMUS
            for id in range(1, C.ND):     # do id=1,nd-1
                dtau[id] = dt[id] / amui[i]

            # outgoing intensity
            rip[C.ND] = pland + amui[i] * dplan
            id = C.ND - 1
            dt0 = dtau[id]
            dtaup1 = dt0 + one
            dtau2 = dt0 * dt0
            bb = two * dtaup1
            cc = dt0 * dtaup1
            aa = dtau2 + bb
            rim[id + 1] = (aa * rip[id + 1] - cc * st0[id + 1] + dt0 * st0[id]) / bb
            for id in range(C.ND - 1, 0, -1):  # do id=nd-1,1,-1
                dt0 = dtau[id]
                dtaup1 = dt0 + one
                dtau2 = dt0 * dt0
                bb = two * dtaup1
                cc = dt0 * dtaup1
                aa = one / (dtau2 + bb)
                rim[id] = (two * rim[id + 1] + dt0 * st0[id + 1] + cc * st0[id]) * aa
                rip[id + 1] = (bb * rim[id + 1] + cc * st0[id + 1] - dt0 * st0[id]) * aa
            for id in range(2, C.ND):     # do id=2,nd-1
                riup[id] = (rim[id] * dtau[id - 1] + rip[id] * dtau[id]) / \
                    (dtau[id - 1] + dtau[id])
            riup[1] = rim[1]
            riup[C.ND] = rip[C.ND]

            ah = ah + amuw[i] * riup[1]
            rint1[i] = riup[1]
            rint1[i] = max(rint1[i], 1.0e-40)
        # end of the loop over angle points

        C.FLUX[ij] = ah * half
        if C.IFLUX >= 1:
            # output of emergent specific intensities to Unit 10 (line points)
            # or 18 (two continuum points)
            # 618 FORMAT(1H ,f10.3,1pe15.5/(1P5E15.5))
            lines = [" %10.3f%15.5E" % (C.WLAM[ij], C.FLUX[ij])]
            for k in range(1, nmus + 1, 5):
                lines.append("".join("%15.5E" % rint1[imu]
                                     for imu in range(k, min(k + 5, nmus + 1))))
            if ij > 2:
                for line in lines:
                    write_line(10, line)
            else:
                for line in lines:
                    write_line(18, line)

        # if needed (if iprin.ge.3), output of interesting physical
        # quantities at the monochromatic optical depth  tau(nu)=2/3
        if C.IPRIN >= 3:
            t0 = math.log(tau[iref + 1] / tau[iref])
            x0 = math.log(tau[iref + 1] / tauref) / t0
            x1 = math.log(tauref / tau[iref]) / t0
            dmref = math.exp(math.log(C.DM[iref]) * x0 + math.log(C.DM[iref + 1]) * x1)
            tref = math.exp(math.log(C.TEMP[iref]) * x0 + math.log(C.TEMP[iref + 1]) * x1)
            stref = math.exp(math.log(st0[iref]) * x0 + math.log(st0[iref + 1]) * x1)
            ssref = math.exp(math.log(-ss0[iref]) * x0 + math.log(-ss0[iref + 1]) * x1)
            sref = stref + ssref
            alm = 2.997925e18 / C.FREQ[ij]
            # 636 FORMAT(1H ,I3,F10.3,I4,1PE10.3,0PF10.1,1X,1P3E10.3)
            write_line(96, " %3d%10.3f%4d%10.3E%10.1f %10.3E%10.3E%10.3E"
                       % (ij, alm, iref, dmref, tref, stref, ssref, sref))
        # end of the loop over frequencies

    return
