# -*- coding: utf-8 -*-
# chunk15: synspec54.f 行 19179–20743 的逐行直译
# 子程序: RUSSEL, SETWIN, SETRAY, WGTJH1, TRIDAG, RESOLW, RTESCA, RTEWIN, VELSET


def russel(tem, pg):
    """      SUBROUTINE RUSSEL(TEM,PG)
    c     =========================

    对应 synspec54.f 行 19179–19408。
    RUSSEL 不修改标量哑元 TEM、PG，故无返回值约定。
    """
    econst = 4.3426e-1
    #       ECONST=4.342945E-1
    xkcon = 6.667343e-1
    epsdie = 5.0e-5
    t = 5040.4 / tem
    pglog = math.log10(pg)
    tk = 1.0 / (tem * 1.38054e-16)

    #    HEH=helium/hydrogen ratio by number
    heh = C.CCOMP[2] / C.CCOMP[1]
    #       HEH=YTOT(1)-UN

    #    evaluation of log XKP(MOL)
    for j in range(1, C.NMOLEC + 1):
        aplogj = C.C[j, 5]  # /COMFH1/ 的数组 C(600,5)，经 commons 别名记作 C.C
        for k in range(1, 5):
            km5 = 5 - k
            aplogj = aplogj * t + C.C[j, km5]
        C.APMLOG[j] = aplogj
    C.APMLOG[1] = -math.log10(1.0353e-16 / tem / math.sqrt(tem) * tk *
                              math.exp(8762.9 / tem))
    dhh = (((0.1196952e-02 * t - 0.2125713e-01) * t + 0.1545253e+00) * t
           - 0.5161452e+01) * t + 0.1277356e+02
    dhh = math.exp(dhh / econst)

    #  evaluation of the ionization constants
    tem25 = tem ** 2 * math.sqrt(tem)
    # 局部数组（DATA 无，普通 DIMENSION）
    fx = np.zeros(101)
    dfx = np.zeros(101)
    z = np.zeros(101)
    prev = np.zeros(101)
    wa = np.zeros(101)
    uiidu2 = np.zeros(101)
    for i in range(1, C.NMETAL + 1):
        nelemi = C.NELEMX[i]
        # calculation of the partition functions following Irwin (1981)
        # irwpf 改写标量哑元 u（其余标量哑元不改），按约定返回全部标量哑元
        g0 = 0.0  # u 为纯输出，传入值不被读取
        nelemi, _ion, _indmol, tem, g0 = irwpf(nelemi, 1, 0, tem, g0)
        g1 = 0.0
        nelemi, _ion, _indmol, tem, g1 = irwpf(nelemi, 2, 0, tem, g1)
        g2 = 0.0
        nelemi, _ion, _indmol, tem, g2 = irwpf(nelemi, 3, 0, tem, g2)
        #          uiidui(nelemi)=g1/g0*0.6665
        C.UIIDUI[nelemi] = g1 / g0 * xkcon
        uiidu2[nelemi] = g2 / g1 * xkcon
        C.XKP[nelemi] = C.UIIDUI[nelemi] * tem25 * \
            math.exp(-C.XIP[nelemi] * t / econst)
        C.XK2[nelemi] = uiidu2[nelemi] * tem25 * \
            math.exp(-C.XI2[nelemi] * t / econst)
        C.XK2[nelemi] = max(C.XK2[nelemi], 1.0e-70)
    hkp = C.XKP[1]
    C.XK2[1] = 0.0

    #   preliminary value of PH at high temperatures
    hkp = C.XKP[1]
    if t < 0.6:
        pph = math.sqrt(hkp * (pg / (1.0 + heh) + hkp)) - hkp
        ph = pph ** 2 / hkp
    else:
        if pg / dhh <= 0.1:
            ph = pg / (1.0 + heh)
        else:
            ph = 0.5 * (math.sqrt(dhh * (dhh + 4.0 * pg / (1.0 + heh))) - dhh)

    #  evaluation of the fictitious pressures of hydrogen
    #     PG=PH+PHH+2.0*PPH+HEH*(PH+2.0*PHH+PPH)
    u = (1.0 + 2.0 * heh) / dhh
    q = 1.0 + heh
    r = (2.0 + heh) * math.sqrt(hkp)
    s = -1.0 * pg
    x = math.sqrt(ph)

    #       Russell iterations
    iterat = 0
    while True:  # 标号 10（GO TO 10 回到此处）
        f = ((u * x ** 2 + q) * x + r) * x + s
        df = 2.0 * (2.0 * u * x ** 2 + q) * x + r
        xr = x - f / df
        if abs((x - xr) / xr) > epsdie:
            iterat = iterat + 1
            if iterat > 50:
                #  710    FORMAT(1H1, ' NOT CONVERGE IN RUSSEL '/// 'TEM=',F9.2,5X,'PG=',
                #     *        E12.5,5X,'X1=',E12.5,5X,'X2=',E12.5,5X,'PH=',E12.5/////)
                print('\f NOT CONVERGE IN RUSSEL \n\n\n'
                      'TEM=%9.2f     PG=%12.5E     X1=%12.5E     X2=%12.5E'
                      '     PH=%12.5E\n\n\n\n\n' % (tem, pg, x, xr, ph))
            else:
                x = xr
                continue  # GO TO 10
        break
    ph = xr ** 2
    phh = ph ** 2 / dhh
    pph = math.sqrt(hkp * ph)
    fph = ph + 2.0 * phh + pph
    C.P[100] = pph

    #   evaluation of the fictitious pressure of each element
    for i in range(1, C.NMETAL + 1):
        nelemi = C.NELEMX[i]
        C.FP[nelemi] = C.CCOMP[nelemi] * fph

    pe = C.P[99]

    #    Russell equations
    niterr = 0
    while True:  # 标号 20（GO TO 20 回到此处）
        for i in range(1, C.NMETAL + 1):
            nelemi = C.NELEMX[i]
            #          FX(NELEMI)=-FP(NELEMI)+P(NELEMI)*(1.0+XKP(NELEMI)/PE)
            dfx[nelemi] = 1.0 + C.XKP[nelemi] / pe * (1.0 + C.XK2[nelemi] / pe)
            fx[nelemi] = -C.FP[nelemi] + C.P[nelemi] * dfx[nelemi]

        spnion = 0.0
        spnplu = 0.0
        for j in range(1, C.NMOLEC + 1):
            mmaxj = C.MMAX[j]
            pmoljl = -C.APMLOG[j]
            for m in range(1, mmaxj + 1):
                nelemj = C.NELEM[m, j]
                natomj = C.NATO[m, j]
                pmoljl = pmoljl + float(natomj) * math.log10(C.P[nelemj])

            pmolj = math.exp(pmoljl / econst)
            for m in range(1, mmaxj + 1):
                nelemj = C.NELEM[m, j]
                natomj = C.NATO[m, j]
                atomj = float(natomj)
                if nelemj == 99:
                    if natomj >= 0:
                        spnion = spnion + pmolj * natomj
                    else:
                        spnplu = spnplu - pmolj * natomj
                for i in range(1, C.NMETAL + 1):
                    nelemi = C.NELEMX[i]
                    if nelemj == nelemi:
                        fx[nelemi] = fx[nelemi] + atomj * pmolj
                        dfx[nelemi] = dfx[nelemi] + atomj ** 2 * \
                            pmolj / C.P[nelemi]
            C.PPMOL[j] = pmolj

        #   solution of the Russell equations by Newton-Raphson method
        for i in range(1, C.NMETAL + 1):
            nelemi = C.NELEMX[i]
            wa[i] = math.log10(C.P[nelemi] + 1.0e-70)
        imaxp1 = C.NMETAL + 1
        wa[imaxp1] = math.log10(pe + 1.0e-70)
        deltrs = 0.0
        for i in range(1, C.NMETAL + 1):
            nelemi = C.NELEMX[i]
            prev[nelemi] = C.P[nelemi] - fx[nelemi] / dfx[nelemi]
            prev[nelemi] = abs(prev[nelemi])
            if prev[nelemi] < 1.0e-70:
                prev[nelemi] = 1.0e-70
            z[nelemi] = prev[nelemi] / C.P[nelemi]
            deltrs = deltrs + abs(z[nelemi] - 1.0)
            if C.SWITER > 0.0:
                C.P[nelemi] = (prev[nelemi] + C.P[nelemi]) * 0.5
            else:
                C.P[nelemi] = prev[nelemi]

        #   ionization equilibrium
        perev = spnplu
        for i in range(1, C.NMETAL + 1):
            nelemi = C.NELEMX[i]
            perev = perev + C.XKP[nelemi] * C.P[nelemi] * \
                (1.0 + C.XK2[nelemi] / pe)
        #        write(6,631) i,nelemi,p(nelemi),XKP(NELEMI)*P(NELEMI),
        #    *   xkp(nelemi),xk2(nelemi),1.+xk2(nelemi)/pe,
        #    *   XKP(NELEMI)*P(NELEMI)*(1.+xk2(nelemi)/pe),perev
        # 631    format(2i4,1p7e11.3)

        perev = math.sqrt(perev / (1.0 + spnion / pe))
        deltrs = deltrs + abs((pe - perev) / pe)
        if C.IPRIN > 4:
            #  601     format('russel iterations ',i4,1p7e13.4)
            print('russel iterations ' + '%4d' % niterr +
                  ''.join('%13.4E' % v for v in
                          (tem, pg * tk, fph * tk, pe * tk, perev * tk,
                           (perev + pe) * 0.5 * tk, deltrs)))
        pe = (perev + pe) * 0.5
        C.P[99] = pe
        if deltrs > C.EPS:
            niterr = niterr + 1
            if niterr <= C.NIMAX:
                continue  # GO TO 20
            else:
                #  605   FORMAT(1H0,'*DOES NOT CONVERGE AFTER ',I4,' ITERATIONS')
                print('\n*DOES NOT CONVERGE AFTER %4d ITERATIONS' % C.NIMAX)
        break

    if C.IPRIN > 4:
        #  601     format('russel iterations ',i4,1p7e13.4)
        print('russel iterations ' + '%4d' % niterr +
              ''.join('%13.4E' % v for v in
                      (tem, pg * tk, fph * tk, pe * tk, perev * tk,
                       (perev + pe) * 0.5 * tk, deltrs)))
        print(' ')
    return


def setwin():
    """      SUBROUTINE SETWIN
    C     =================
    C
    C     Initialisation of an extended radial structure
    C      (spherical symmetry is assumed)
    C     with a continuous connection between the lower quasi-hydrostatic
    C     layers and the upper, supersonic layers. The velocity structure
    C     in the upper layers is a beta-type law (v=vinf*(1-r0/r)^beta).
    C
    C     Additional input are read at the end of Unit 8:
    C      RCORE : Core radius (deepest layer, in solar radii or in cm)
    C      NDRAD : Number of layers
    C      NRCORE: Number of core rays
    C      INRV  : Switch indicating the data to be read:
    C           = 0 : Read an hydrostatic, plane-parallel model only; the
    C                   routine builds the radial points, density and
    C                   velocity structure;
    C           < 0 : Read also an hydrostatic, plane-parallel model, but
    C                   an empirical velocity law V(r) is read at each
    C                   radial point (r(id) is read);
    C           > 0 : Input from an extended model atmosphere; the velocity
    C                   law is read; the density structure is recomputed for
    C                   a possibly different mass-loss rate.
    C      XMDOT  : Mass loss rate (in solar mass/yr)
    C      BETAV, VINF : Parameters of the velocity law (VINF in km/s)
    C      RD, VEL: Radial points, expansion velocity
    C
    C     Synspec version

    对应 synspec54.f 行 19416–19485。
    """
    rsun = 6.96e10  # PARAMETER (RSUN=6.96D10)

    def _f(s):  # 自由格式读入的浮点解析（容许 Fortran D 指数）
        return float(s.replace('D', 'E').replace('d', 'e'))

    #     Read data for spherical atmosphere and velocity law
    # READ(8,*,END=9,ERR=9)：文件结束或读错误 → 标号 9（RETURN）
    try:
        _toks = []
        while len(_toks) < 6:  # 自由格式读可跨记录续行
            _toks.extend(read_line(8).replace(',', ' ').split())
        C.RCORE = _f(_toks[0])
        ndrad = int(_f(_toks[1]))  # 局部量（不属于任何 COMMON 块）
        C.NRCORE = int(_f(_toks[2]))
        inrv = int(_f(_toks[3]))   # 局部量，读入后未被使用
        C.NFIRY = int(_f(_toks[4]))
        C.NDF = int(_f(_toks[5]))
    except (EOFError, ValueError):
        return  # END=9 / ERR=9 → 9 continue → RETURN
    if C.RCORE < 1.0e5:
        C.RCORE = C.RCORE * rsun
    if ndrad > MDEPTH:
        quit('NDRAD too large')
    #      READ(8,*) XMDOT,BETAV,VINF
    _toks = []
    while len(_toks) < 3:
        _toks.extend(read_line(8).replace(',', ' ').split())
    C.XMDOT = _f(_toks[0])
    C.BETAV = _f(_toks[1])
    C.VINF = _f(_toks[2])
    C.XMDOT = 6.30289e25 * C.XMDOT
    C.VINF = 1.0e5 * C.VINF
    C.ND = ndrad
    for id in range(1, C.ND + 1):
        #        READ(8,*) RD(ID),VEL(ID),VTURB(ID),DENSCON(ID)
        _toks = []
        while len(_toks) < 4:
            _toks.extend(read_line(8).replace(',', ' ').split())
        C.RD[id] = _f(_toks[0])
        C.VEL[id] = _f(_toks[1])
        C.VTURB[id] = _f(_toks[2])
        C.DENSCON[id] = _f(_toks[3])
        if C.DENSCON[id] == 0.0:
            C.DENSCON[id] = 1.0
        C.VTURB[id] = C.VTURB[id] * C.VTURB[id]

    #   Apply density contrast for clumping
    for id in range(1, C.ND + 1):
        C.ELEC[id] = C.ELEC[id] * C.DENSCON[id]
        C.DENS[id] = C.DENS[id] * C.DENSCON[id]
        for i in range(1, C.NLEVEL + 1):
            C.POPUL[i, id] = C.POPUL[i, id] * C.DENSCON[id]

    #  Set up rays and weights
    C.itrad = 1
    radtem()
    setray()
    wgtjh1()

    #    9 continue
    return


def setray():
    """      SUBROUTINE SETRAY
    C     =================
    C
    C     Setup impact rays and angles
    C      (assumes one impact ray tangent to every depth layer)

    对应 synspec54.f 行 19491–19701。
    """
    pi4 = 4.0 * 3.141592654  # PARAMETER (PI4=4.*3.141592654)
    un = 1.0
    # PARAMETER (UN=1., TWO=2., HALF=0.5)
    rs = np.zeros(MDEPF + 1)
    rdx = np.zeros(MDEPF + 1)
    ziu = np.zeros(MDEPTH + 1)
    viu = np.zeros(MDEPTH + 1)
    ziuf = np.zeros(MDEPF + 1)
    viuf = np.zeros(MDEPF + 1)

    #     Fine radial grid
    if C.NDF == 0 or C.NDF == C.ND:
        C.NDF = C.ND
        for id in range(1, C.NDF + 1):
            C.DENSF[id] = C.DENS[id]
    else:
        xr1 = math.log(C.DENS[1])
        xr2 = math.log(C.DENS[C.ND])
        dxr = (xr2 - xr1) / float(C.NDF - 1)
        for id in range(1, C.NDF + 1):
            C.DENSF[id] = math.exp(xr1 + float(id - 1) * dxr)

    #     Impact rays
    C.NREXT = C.ND
    for id in range(1, C.NREXT + 1):
        C.PIM[id] = C.RD[id]
        C.NUD[id] = id
    for iu in range(1, C.NRCORE + 1):
        C.PIM[C.NREXT + iu] = float(C.NRCORE - iu) / float(C.NRCORE) * C.RCORE
        C.NUD[C.NREXT + iu] = C.ND
    C.KMU = C.NREXT + C.NRCORE

    #     Angles
    for id in range(1, C.ND + 1):
        rd1 = un / C.RD[id]
        for iu in range(id, C.KMU + 1):
            prr = C.PIM[iu] * rd1
            C.BMU[iu, id] = math.sqrt(un - prr * prr)

    #     Depth increments along each ray
    C.DELZ[1, 1] = 0.0
    C.DFRQ[1, 1] = 0.0
    for iu in range(2, C.KMU + 1):
        C.NUDF[iu] = C.NUD[iu]
        iu1 = iu
        if iu > C.ND:
            iu1 = C.ND
        for id in range(1, iu1 - 1 + 1):
            C.DELZ[iu, id] = C.BMU[iu, id] * C.RD[id] - \
                C.BMU[iu, id + 1] * C.RD[id + 1]
            C.DFRQ[iu, id] = C.BMU[iu, id] * C.VEL[id] / CL
            jd = 2 * C.NUD[iu] - id
            C.DFRQ[iu, jd] = -C.DFRQ[iu, id]
        C.DELZ[iu, iu1] = C.DELZ[iu, iu1 - 1]
        C.DFRQ[iu, iu1] = 0.0
        if iu > C.NREXT:
            C.DFRQ[iu, C.ND] = C.BMU[iu, C.ND] * C.VEL[C.ND] / CL

    # Finer grid along the NFIRY most external rays
    #   velocity steps DVD(ID)
    C.XMD4 = C.XMDOT / pi4
    clv = un / CL
    for id in range(1, C.ND + 1):
        C.DVD[id] = math.sqrt(1.6e7 * C.TEMP[id] + C.VTURB[id]) * 0.3
        #        DVD(ID)=SQRT(1.6D7*TEMP(ID))
    nudx = C.ND
    for iu in range(2, C.NFIRY + 1):
        if C.PIM[iu] > 0.0:
            for id in range(1, C.NUD[iu] + 1):
                iid = C.NUD[iu] - id + 1
                ziu[id] = C.VEL[iid]
                viu[id] = C.DFRQ[iu, iid] * CL
        else:
            for id in range(1, C.NUD[iu] + 1):
                iid = C.NUD[iu] - id + 1
                ziu[id] = C.RD[iid]
                viu[id] = C.DFRQ[iu, iid] * CL
        C.NUDF[iu] = 1
        viuf[1] = C.DFRQ[iu, 1] * CL
        for id in range(1, C.NUD[iu] - 1 + 1):
            vz1 = C.DFRQ[iu, id] * CL
            vz2 = C.DFRQ[iu, id + 1] * CL
            # Fortran INT：向零截断，Python int() 同为向零截断
            nfg = int((vz1 - vz2) / C.DVD[id]) + 1
            xfg = (vz1 - vz2) / float(nfg)
            iv0 = C.NUDF[iu]
            for iv in range(1, nfg + 1):
                viuf[iv0 + iv] = vz1 - float(iv) * xfg
            C.NUDF[iu] = C.NUDF[iu] + nfg
            if C.NUDF[iu] > MDEPF:
                quit('Too many points in fine grid - SETRAY')
        if C.NUDF[iu] > nudx:
            nudx = C.NUDF[iu]
        inrp = 2
        if iu > 8:
            inrp = 4
        interp(viu, ziu, viuf, ziuf, C.NUD[iu], C.NUDF[iu], inrp, 0, 0)
        if C.PIM[iu] > 0.0:
            for id in range(1, C.NUDF[iu] + 1):
                dmu = viuf[id] / ziuf[id]
                rs[id] = C.PIM[iu] / math.sqrt(un - dmu * dmu)
                C.DFRQF[iu, id] = viuf[id] * clv
                C.VELF[iu, id] = ziuf[id]
                rdx[id] = C.XMD4 / (rs[id] * rs[id] * C.VELF[iu, id])
                ziuf[id] = dmu * rs[id]
        else:
            for id in range(1, C.NUDF[iu] + 1):
                rs[id] = ziuf[id]
                C.DFRQF[iu, id] = viuf[id] * clv
                C.VELF[iu, id] = viuf[id]
                rdx[id] = C.XMD4 / (rs[id] * rs[id] * C.VELF[iu, id])
        if iu <= C.NREXT:
            for id in range(1, C.NUDF[iu] + 1):
                jd = 2 * C.NUDF[iu] - id
                C.DFRQF[iu, jd] = -C.DFRQF[iu, id]
        for id in range(1, C.NUDF[iu] - 1 + 1):
            C.DELZF[iu, id] = ziuf[id] - ziuf[id + 1]
        C.DELZF[iu, C.NUDF[iu]] = C.DELZF[iu, C.NUDF[iu] - 1]

        #   Assign depth index
        C.KRAY[iu, 1] = 2
        C.DRAY[iu, 1] = 0.0
        idk = 1
        for id in range(2, C.NUDF[iu] + 1):
            # DO WHILE (RDX(ID).GE.DENSF(IDK).and.idk.le.ndf)
            # （调整条件顺序以避免 idk=NDF+1 时越界，逻辑等价）
            while idk <= C.NDF and rdx[id] >= C.DENSF[idk]:
                idk = idk + 1
            #          IDK=IDK+1
            if idk > C.NDF:
                idk = C.NDF
            C.KRAY[iu, id] = idk
            C.DRAY[iu, id] = (rdx[id] - C.DENSF[idk - 1]) / \
                (C.DENSF[idk] - C.DENSF[idk - 1])
        if iu <= C.NREXT:
            for id in range(1, C.NUDF[iu] + 1):
                jd = 2 * C.NUDF[iu] - id
                C.KRAY[iu, jd] = C.KRAY[iu, id]
                C.DRAY[iu, jd] = C.DRAY[iu, id]

    #    remaining rays (without finer grid)
    if C.NFIRY < C.KMU:
        iu = C.KMU
        C.KRAY[iu, 1] = 2
        C.DRAY[iu, 1] = 0.0
        idk = 1
        for id in range(2, C.NUDF[iu] + 1):
            # DO WHILE (DENS(ID).GE.DENSF(IDK).and.idk.le.ndf)（条件顺序同上）
            while idk <= C.NDF and C.DENS[id] >= C.DENSF[idk]:
                idk = idk + 1
            #          IDK=IDK+1
            if idk > C.NDF:
                idk = C.NDF
            C.KRAY[iu, id] = idk
            C.DRAY[iu, id] = (C.DENS[id] - C.DENSF[idk - 1]) / \
                (C.DENSF[idk] - C.DENSF[idk - 1])
        for iu in range(C.NFIRY + 1, C.KMU + 1):
            for id in range(1, C.NUDF[iu] + 1):
                C.KRAY[iu, id] = C.KRAY[C.KMU, id]
                C.DRAY[iu, id] = C.DRAY[C.KMU, id]
                C.DFRQF[iu, id] = C.DFRQ[iu, id]
                C.DELZF[iu, id] = C.DELZ[iu, id]
            if iu <= C.NREXT:
                for id in range(1, C.NUDF[iu] + 1):
                    jd = 2 * C.NUDF[iu] - id
                    C.KRAY[iu, jd] = C.KRAY[iu, id]
                    C.DRAY[iu, jd] = C.DRAY[iu, id]
                    C.DFRQF[iu, jd] = -C.DFRQF[iu, id]

    nftot = 0
    for iu in range(2, C.KMU + 1):
        iud = C.NUD[iu]
        if iu <= C.NREXT:
            iud = 2 * C.NUDF[iu] - 1
        nftot = nftot + iud
    #      write(10,*) 'NFTOT=',NFTOT
    write_line(10, ' NFTOT= %d' % nftot)

    return


def wgtjh1():
    """      SUBROUTINE WGTJH1
    C     =================
    C
    C     Angle quadrature weights
    C      from Hummer, Kunasz, & Kunasz, 1973, Comp. Phys. Comm. 6, 38
    C
    C     The present version of this routine assumes that there are
    C      impact rays tangent to every depth layers (i.e. NREXT=ND)

    对应 synspec54.f 行 19707–19808。
    """
    un = 1.0
    two = 2.0
    half = 0.5  # PARAMETER (UN=1., TWO=2., HALF=0.5)
    six = 6.0     # PARAMETER (SIX=6.)
    c03 = un / 3.0
    d03 = 2.0 / 3.0
    c04 = un / 4.0
    c06 = un / 6.0  # PARAMETER (C03=UN/3.,D03=2./3.,C04=UN/4.,C06=UN/6.)
    c24 = un / 24.0
    c45 = un / 45.0
    d45 = 2.0 / 45.0
    c72 = un / 72.0  # PARAMETER (C24=UN/24.,C45=UN/45.,D45=2./45.,C72=UN/72.)
    waj = np.zeros(MKU + 1)
    wbj = np.zeros(MKU + 1)
    ahh = np.zeros((MKU + 1, 5))
    bmuh = np.zeros(MKU + 1)
    bmuhp = np.zeros(MKU + 1)
    wah = np.zeros(MKU + 1)
    wbh = np.zeros(MKU + 1)
    wsd = np.zeros(MKU + 1)
    wsu = np.zeros(MKU + 1)
    wsl = np.zeros(MKU + 1)
    wuu = np.zeros(MKU + 1)
    wtd = np.zeros(MKU + 1)
    wtu = np.zeros(MKU + 1)
    wtl = np.zeros(MKU + 1)

    for id in range(1, C.ND + 1):  # DO 100 ID=1,ND
        for iu in range(id + 1, C.KMU + 1):
            ahh[iu, 1] = C.BMU[iu, id] - C.BMU[iu - 1, id]
            ahh[iu, 2] = ahh[iu, 1] * ahh[iu, 1]
            ahh[iu, 3] = ahh[iu, 2] * ahh[iu, 1]
            ahh[iu, 4] = ahh[iu, 3] * ahh[iu, 1]
            bmuh[iu] = C.BMU[iu, id] * ahh[iu, 1]
            bmuhp[iu] = C.BMU[iu - 1, id] * ahh[iu, 1]

        #     Weights for J
        waj[id] = half * ahh[id + 1, 1]
        waj[C.KMU] = half * ahh[C.KMU, 1]
        wbj[id] = -c24 * ahh[id + 1, 3]
        wbj[C.KMU] = -c24 * ahh[C.KMU, 3]
        wsl[id + 1] = c06 * ahh[id + 1, 1]
        wsu[C.KMU - 1] = 0.0
        wsd[id] = c03 * ahh[id + 1, 1]
        wsd[C.KMU] = un
        wtl[id + 1] = un / ahh[id + 1, 1]
        wtu[C.KMU - 1] = 0.0
        wtd[id] = -wtl[id + 1]
        wtd[C.KMU] = 0.0
        for iu in range(id + 1, C.KMU - 1 + 1):
            waj[iu] = half * (ahh[iu, 1] + ahh[iu + 1, 1])
            wbj[iu] = -c24 * (ahh[iu + 1, 3] + ahh[iu, 3])
            ah1 = six / (ahh[iu, 1] + ahh[iu + 1, 1])
            wsl[iu + 1] = c06 * ah1 * ahh[iu + 1, 1]
            wsu[iu - 1] = un - wsl[iu + 1]
            wsd[iu] = two
            wtl[iu + 1] = ah1 / ahh[iu + 1, 1]
            wtu[iu - 1] = ah1 / ahh[iu, 1]
            wtd[iu] = -six / ahh[iu, 1] / ahh[iu + 1, 1]
        nmud = C.KMU - id + 1
        # TODO(port): 原文按数组基址传 WSL/WSD/WSU/WBJ/WUU（而非 WSL(ID) 起的
        # 偏移），TRIDAG 内部从下标 1 起用；此处按原文直译。
        tridag(wsl, wsd, wsu, wbj, wuu, nmud)
        C.WMUJ[id, id] = waj[id] + wtd[id] * wuu[id] + wtu[id] * wuu[id + 1]
        C.WMUJ[C.KMU, id] = waj[C.KMU] + wtl[C.KMU] * wuu[C.KMU - 1] + \
            wtd[C.KMU] * wuu[C.KMU]
        for iu in range(id + 1, C.KMU - 1 + 1):
            C.WMUJ[iu, id] = waj[iu] + wtl[iu] * wuu[iu - 1] + \
                wtd[iu] * wuu[iu] + wtu[iu] * wuu[iu + 1]

        #     Weights for emergent flux H
        if id > 1:
            continue  # IF(ID.GT.1) GO TO 100 → 进入下一循环步
        wah[id] = half * bmuh[id + 1] - c03 * ahh[id + 1, 2]
        wah[C.KMU] = half * bmuhp[C.KMU] + c03 * ahh[C.KMU, 2]
        wbh[id] = ahh[id + 1, 3] * (c45 * ahh[id + 1, 1] -
                                    c24 * C.BMU[id + 1, id])
        wbh[C.KMU] = -ahh[C.KMU, 3] * (c45 * ahh[C.KMU, 1] +
                                       c24 * C.BMU[C.KMU - 1, id])
        wsl[id + 1] = 0.0
        wsd[id] = un
        wtl[id + 1] = 0.0
        wtd[id] = 0.0
        for iu in range(id + 1, C.KMU - 1 + 1):
            wah[iu] = half * (bmuh[iu + 1] + bmuhp[iu]) - \
                c03 * (ahh[iu + 1, 2] - ahh[iu, 2])
            wbh[iu] = -c24 * (bmuh[iu + 1] * ahh[iu + 1, 2] +
                              bmuhp[iu] * ahh[iu, 2]) + \
                c45 * (ahh[iu + 1, 4] - ahh[iu, 4])
        tridag(wsl, wsd, wsu, wbh, wuu, nmud)
        C.WMUH[id] = wah[id] + wtd[id] * wuu[id] + wtu[id] * wuu[id + 1]
        C.WMUH[C.KMU] = wah[C.KMU] + wtl[C.KMU] * wuu[C.KMU - 1] + \
            wtd[C.KMU] * wuu[C.KMU]
        for iu in range(id + 1, C.KMU - 1 + 1):
            C.WMUH[iu] = wah[iu] + wtl[iu] * wuu[iu - 1] + \
                wtd[iu] * wuu[iu] + wtu[iu] * wuu[iu + 1]
        #  100 CONTINUE

    #     Weights for H are overwritten by trapezoidal weigths
    id = 1
    C.WMUH[1] = C.BMU[1, id] * (C.BMU[2, id] - C.BMU[1, id]) * half
    C.WMUH[C.KMU] = C.BMU[C.KMU, id] * \
        (C.BMU[C.KMU, id] - C.BMU[C.KMU - 1, id]) * half
    for iu in range(2, C.KMU - 1 + 1):
        C.WMUH[iu] = C.BMU[iu, id] * \
            (C.BMU[iu + 1, id] - C.BMU[iu - 1, id]) * half
    return


def tridag(a, b, c, r, u, n):
    """      SUBROUTINE TRIDAG(A,B,C,R,U,N)
    C     ==============================
    C
    C     Solve tridiagonal system of equations
    C      from Numerical Recipes (standard Gaussian elimination)

    对应 synspec54.f 行 19814–19837。
    TRIDAG 不修改标量哑元 N，故无返回值约定。
    """
    gtrid = np.zeros(MKU + 1)

    btrid = b[1]
    u[1] = r[1] / btrid
    for j in range(2, n + 1):
        gtrid[j] = c[j - 1] / btrid
        btrid = b[j] - a[j] * gtrid[j]
        u[j] = (r[j] - a[j] * u[j - 1]) / btrid
    for j in range(n - 1, 0, -1):
        u[j] = u[j] - gtrid[j + 1] * u[j + 1]

    return


def resolw():
    """      SUBROUTINE RESOLW
    C     =================
    C
    C     driver for evaluating opacities and emissivities which then
    C     enter the solution of the radiative transfer equation (RTEWIN)
    C     Setup opacities for a given frequency set
    C     Oversample in radial and frequency space for later interpolation

    对应 synspec54.f 行 19843–20029。
    """
    un = 1.0
    # PARAMETER (UN=1., TWO=2., HALF=0.5)
    cross = np.zeros((MCROSS + 1, MOPAC + 1))
    abso = np.zeros(MOPAC + 1)
    emis = np.zeros(MOPAC + 1)
    absoc = np.zeros(MFREQC + 1)
    emisc = np.zeros(MFREQC + 1)
    scatc = np.zeros(MFREQC + 1)
    absd = np.zeros(MDEPTH + 1)
    asf = np.zeros(MDEPF + 1)
    xds = np.zeros(MDEPTH + 1)
    xdsf = np.zeros(MDEPF + 1)

    #     set up the partial line list for the current interval
    iniset()

    #     output of information about selected lines
    if C.IMODE < 2:
        inibla()

    #  Setup fine grid of frequencies
    clv = un / 2.997925e10
    fq1 = C.FREQ[1] * (un + C.VINF * clv)
    fq2 = C.FREQ[C.NFREQ] * (un - C.VINF * clv)
    vxd = math.sqrt(0.3e7 * C.TSTD) * C.FREQ[1] * clv
    vxs = C.SPACE0 * C.FREQ[1] * C.FREQ[1] * clv * 1.0e-7
    #     DVX=MAX(VXD,VXS)
    dvx = vxs
    C.NOPAC = int((fq1 - fq2) / dvx) + 1  # INT 向零截断
    dvx = (fq1 - fq2) / float(C.NOPAC)
    C.NOPAC = C.NOPAC + 3
    C.NOPAC = C.NFREQ
    #  600 FORMAT(/,' Opacity table for',i5,' frequencies and',/,
    #     *         '                  ',i5,' radial (density) points')
    print('\n Opacity table for%5d frequencies and\n'
          '                  %5d radial (density) points' % (C.NOPAC, C.NDF))
    if C.NOPAC > MOPAC:
        quit('Too many freqs in fine grid')
    ijc = 1  # TODO(port): Fortran 中 IJC 未赋初值即用作下面 DO 循环初值；取 1
    for ij in range(1, C.NOPAC + 1):
        C.FFQ[ij] = fq1 - float(ij - 1) * dvx
        #         freq(ij)=ffq(ij)
        #         wlam(ij)=2.997925e18/freq(ij)
        fr = C.FREQ[ij] * 1.0e-15
        C.BNUE[ij] = BN * fr * fr * fr
        ijci = ijc
        while ijci <= C.NFREQC - 1:  # DO IJCI=IJC,NFREQC-1
            if C.WLAM[ij] <= C.WLAMC[ijci]:
                break  # GO TO 248
            ijci += 1
        #  248    CONTINUE
        ijc = ijci
        C.IJCINT[ij] = max(ijc - 1, 1)
        ijci = C.IJCINT[ij]
        C.FRX1[ij] = (C.FREQ[ij] - C.FREQC[ijci + 1]) / \
            (C.FREQC[ijci] - C.FREQC[ijci + 1])
        #         write(80,681) ij,ijci,wlam(ij),wlamc(ijci),freq(ij),frx1(ij)
        #  681 format(2i5,2f10.3,1p2e11.3)
    C.NFREQ = C.NOPAC
    for ji in range(1, C.NOPAC - 1 + 1):
        C.FFQV[ji] = un / (C.FFQ[ji] - C.FFQ[ji + 1])
    C.FFQV[C.NOPAC] = un

    #     the continuum opacities and radiation field - done only once
    #     -----------------------------------
    r2f = 1.0  # TODO(port): Fortran 中仅 iblank<=1 时赋值；此处给安全初值
    if C.IBLANK <= 1:
        #     determine the "core" radius and the factor that multiplies
        #     H_nu at ID=1 to get physical flux there (R2F)
        id0 = C.ND
        while C.TEMP[id0] > C.TEFF and id0 > 1:
            id0 = id0 - 1
        id0 = id0 + 1
        r2f = C.RD[1] * C.RD[1] / C.RD[id0] / C.RD[id0]

        #     photoinization cross-sections
        crosew(cross)

        #     store opacity and emissivity in continuum
        for id in range(1, C.ND + 1):
            opacw(id, cross, abso, emis, absoc, emisc, scatc, 0)
            for ij in range(1, C.NFREQC + 1):
                C.CHC[ij, id] = absoc[ij] / C.DENSCON[id]
                C.ETC[ij, id] = emisc[ij] / C.DENSCON[id]
                C.SCC[ij, id] = (scatc[ij] + C.ELEC[id] * SIGE) / C.DENSCON[id]

        #     radiation field in the continuum
        rtesca()
        for ij in range(1, C.NFREQC + 1):
            #  640 FORMAT(1H ,F10.4,1PE15.5)
            write_line(17, ' %10.4f%15.5E' % (C.WLAMC[ij], C.FLUXC[ij] * r2f))
    #     -----------------------------------

    #     Store opacity and thermal source function in all frequencies
    #     and depths
    for id in range(1, C.ND + 1):
        opacw(id, cross, abso, emis, absoc, emisc, scatc, 1)
        for ij in range(1, C.NOPAC + 1):
            C.AB[ij, id] = abso[ij] / C.DENSCON[id]
            C.STH[ij, id] = emis[ij] / abso[ij]

    #      do id=1,nd
    #      do ij=1,nopac
    #         write(92,693) id,ij,wlam(ij),ab(ij,id),sth(ij,id)
    #      end do
    #      end do
    #  693 format(2i5,f10.3,1p2e10.3)

    #  Interpolate to a finer radial (density) grid
    if C.NDF != C.ND:
        for id in range(1, C.ND + 1):
            xds[id] = math.log10(C.DENS[id])
        for id in range(1, C.NDF + 1):
            xdsf[id] = math.log10(C.DENSF[id])
        for ij in range(1, C.NOPAC + 1):
            for id in range(1, C.ND + 1):
                absd[id] = C.AB[ij, id]
            interp(xds, absd, xdsf, asf, C.ND, C.NDF, 2, 0, 1)
            for id in range(1, C.NDF + 1):
                C.AB[ij, id] = asf[id]
            for id in range(1, C.ND + 1):
                absd[id] = C.STH[ij, id]
            interp(xds, absd, xdsf, asf, C.ND, C.NDF, 2, 0, 1)
            for id in range(1, C.NDF + 1):
                C.STH[ij, id] = asf[id]
        for ij in range(1, C.NFREQC + 1):
            for id in range(1, C.ND + 1):
                absd[id] = C.SCC[ij, id]
            interp(xds, absd, xdsf, asf, C.ND, C.NDF, 2, 0, 1)
            for id in range(1, C.NDF + 1):
                C.SCH[ij, id] = asf[id]
    #  601 FORMAT(' Done'/)
    print(' Done')
    print()

    #     Loop on rays, solving radiative transfer equation
    for ij in range(1, C.NFREQ + 1):
        C.FLUX[ij] = 0.0
    for iu in range(2, C.KMU + 1):
        rtewin(iu)
    for ij in range(1, C.NFREQ + 1):
        C.FLUX[ij] = C.FLUX[ij] * r2f

    return


def rtesca():
    """      SUBROUTINE RTESCA
    C     =================
    C
    C     Solution of the radiative transfer equation
    C      for deriving the scattering in continuum
    C
    C     Solution along every rays, for the spherically-symmetric case
    C
    C     Solution in the optical depth scale
    C
    C     The numerical method used:
    C     Discontinuous Finite Element method
    C     Castor, Dykema, Klein, 1992, ApJ 387, 561.

    对应 synspec54.f 行 20035–20275。
    """
    un = 1.0
    two = 2.0
    half = 0.5  # PARAMETER (UN=1., TWO=2., HALF=0.5)
    ntrali = 10
    djmax = 1.0e-3  # PARAMETER (NTRALI=10,DJMAX=1.D-3)
    st0 = np.zeros(MDEPF + 1)
    rad00 = np.zeros(MDEPF + 1)
    ab0 = np.zeros(MDEPF + 1)
    ali1 = np.zeros(MDEPF + 1)
    rip = np.zeros(MDEPF + 1)
    rim = np.zeros(MDEPF + 1)
    riin = np.zeros(MDEPF + 1)
    riup = np.zeros(MDEPF + 1)
    aip = np.zeros(MDEPF + 1)
    aim = np.zeros(MDEPF + 1)
    aiin = np.zeros(MDEPF + 1)
    aiup = np.zeros(MDEPF + 1)
    dt = np.zeros(MDEPF + 1)
    dtau = np.zeros(MDEPF + 1)
    rdx = np.zeros(MDEPF + 1)
    ptx = np.zeros(MDEPF + 1)
    uf = np.zeros(MDEPF + 1)
    af = np.zeros(MDEPF + 1)
    ss0 = np.zeros(MDEPF + 1)
    scx = np.zeros(MDEPTH + 1)
    densr = np.zeros(MDEPF + 1)
    rdy = np.zeros(MDEPF + 1)
    abc0 = np.zeros(MDEPF + 1)
    abc1 = np.zeros(MDEPF + 1)
    stc0 = np.zeros(MDEPF + 1)
    stc1 = np.zeros(MDEPF + 1)
    scc0 = np.zeros(MDEPF + 1)
    scc01 = np.zeros(MDEPF + 1)

    #     overall loop over continuum frequencies
    for ij in range(1, C.NFREQC + 1):  # DO 500 IJ=1,NFREQC
        fr = C.FREQC[ij]

        #     Initialisation of J=B
        if ij == 1:
            fr15 = fr * 1.0e-15
            bnu = BN * fr15 * fr15 * fr15
            hkfr = HK * fr
            for id in range(1, C.ND + 1):
                rad00[id] = bnu / (math.exp(hkfr / C.TEMP[id]) - un)

        #     Loop over electron scattering
        itrali = 0
        while True:  # 标号 10（GO TO 10 回到此处）
            itrali = itrali + 1
            C.FLUXC[ij] = 0.0

            for id in range(1, C.ND + 1):
                C.RAD1[id] = 0.0
                ali1[id] = 0.0

            #     Loop over impact rays
            if C.ND == C.NDF:
                for id in range(1, C.ND + 1):
                    C.DENSF[id] = C.DENS[id]
                    rdx[id] = rad00[id]
                    abc0[id] = C.CHC[ij, id]
                    stc0[id] = C.ETC[ij, id] / C.CHC[ij, id]
                    scc0[id] = C.SCC[ij, id]
            else:
                interp(C.DENS, rad00, C.DENSF, rdx, C.ND, C.NDF, 4, 1, 0)
                for id in range(1, C.ND + 1):
                    abc1[id] = C.CHC[ij, id]
                    stc1[id] = C.ETC[ij, id] / C.CHC[ij, id]
                    # TODO(port): 原文下标为 ij（频率索引），疑为 id 之笔误，按原文直译
                    scc01[ij] = C.SCC[ij, id]
                interp(C.DENS, abc1, C.DENSF, abc0, C.ND, C.NDF, 4, 1, 0)
                interp(C.DENS, stc1, C.DENSF, stc0, C.ND, C.NDF, 4, 1, 0)
                interp(C.DENS, scc01, C.DENSF, scc0, C.ND, C.NDF, 4, 1, 0)
            for iu in range(1, C.KMU + 1):  # DO 100 IU=1,KMU
                iud = C.NUD[iu]
                if iu <= C.NFIRY:
                    iud = C.NUDF[iu]
                if iud <= 1:
                    continue  # goto 100
                for id in range(1, iud + 1):
                    ky = C.KRAY[iu, id]
                    ydr = C.DRAY[iu, id]
                    ydr1 = un - C.DRAY[iu, id]
                    densr[id] = ydr1 * C.DENSF[ky - 1] + ydr * C.DENSF[ky]
                    ab0[id] = ydr1 * abc0[ky - 1] + ydr * abc0[ky]
                    st0[id] = ydr1 * stc0[ky - 1] + ydr * stc0[ky]
                    sc0 = ydr1 * scc0[ky - 1] + ydr * scc0[ky]
                    rdy[id] = ydr1 * rdx[ky - 1] + ydr * rdx[ky]
                    ss0[id] = sc0 / ab0[id]
                    st0[id] = st0[id] + ss0[id] * rdy[id]
                if iu <= C.NFIRY:
                    for id in range(1, iud - 1 + 1):
                        dtau[id] = half * (ab0[id] + ab0[id + 1]) * \
                            C.DELZF[iu, id]
                else:
                    for id in range(1, iud - 1 + 1):
                        dt[id] = half * (ab0[id] + ab0[id + 1])
                        dtau[id] = dt[id] * C.DELZ[iu, id]

                #        incoming intensity   (TAUMIN=0.)
                rim[1] = 0.0
                aim[1] = 0.0
                for id in range(1, iud - 1 + 1):
                    dt0 = dtau[id]
                    dtaup1 = dt0 + un
                    dtau2 = dt0 * dt0
                    bb = two * dtaup1
                    cc = dt0 * dtaup1
                    aa = un / (dtau2 + bb)
                    rip[id] = (bb * rim[id] + cc * st0[id] -
                               dt0 * st0[id + 1]) * aa
                    rim[id + 1] = (two * rim[id] + dt0 * st0[id] +
                                   cc * st0[id + 1]) * aa
                    aip[id] = (cc + bb * aim[id]) * aa
                    aim[id + 1] = cc * aa
                for id in range(2, iud - 1 + 1):
                    dtt = un / (dtau[id - 1] + dtau[id])
                    riin[id] = (rim[id] * dtau[id] +
                                rip[id] * dtau[id - 1]) * dtt
                    aiin[id] = (aim[id] * dtau[id] +
                                aip[id] * dtau[id - 1]) * dtt
                riin[1] = rim[1]
                riin[iud] = rim[iud]
                aiin[1] = aim[1]
                aiin[iud] = aim[iud]
                rip[iud] = rim[iud]

                #        Outgoing intensity
                #          symmetric boundary condition (rim(iud)=riin(iud))
                #       or diffusion approx. for core rays
                if iu > C.NREXT:
                    pland = bnu / (math.exp(hkfr / C.TEMP[C.ND]) - un)
                    dplan = pland - bnu / (math.exp(hkfr / C.TEMP[C.ND - 1]) - un)
                    #         rim(iud)=PLAND+dplan/dtau(iud-1)
                    rip[iud] = pland + dplan / dtau[iud - 1]
                    dt0 = dtau[iud - 1]
                    dtaup1 = dt0 + un
                    dtau2 = dt0 * dt0
                    bb = two * dtaup1
                    cc = dt0 * dtaup1
                    aa = dtau2 + bb
                    rim[iud] = (aa * rip[iud] - cc * st0[iud] +
                                dt0 * st0[iud - 1]) / bb
                for id in range(iud - 1, 0, -1):
                    dt0 = dtau[id]
                    dtaup1 = dt0 + un
                    dtau2 = dt0 * dt0
                    bb = two * dtaup1
                    cc = dt0 * dtaup1
                    aa = un / (dtau2 + bb)
                    rip[id + 1] = (bb * rim[id + 1] + cc * st0[id + 1] -
                                   dt0 * st0[id]) * aa
                    rim[id] = (two * rim[id + 1] + dt0 * st0[id + 1] +
                               cc * st0[id]) * aa
                    aip[id + 1] = (cc + bb * aim[id + 1]) * aa
                    aim[id] = cc * aa
                for id in range(2, iud - 1 + 1):
                    dtt = un / (dtau[id - 1] + dtau[id])
                    riup[id] = (rim[id] * dtau[id - 1] +
                                rip[id] * dtau[id]) * dtt
                    aiup[id] = (aim[id] * dtau[id - 1] +
                                aip[id] * dtau[id]) * dtt
                riup[1] = rim[1]
                riup[iud] = rim[iud]
                aiup[1] = aim[1]
                aiup[iud] = aim[iud]

                #      symmetrized (Feautrier) intensity  -- (riin+riup)/2 --
                #        and interpolation in original radial grid
                for id in range(1, iud + 1):
                    uf[id] = riup[id] + riin[id]
                    af[id] = aiup[id] + aiin[id]
                if iu <= C.NFIRY:
                    inrp = min(C.NUD[iu], 4)
                    interp(densr, uf, C.DENS, ptx, iud, C.NUD[iu], inrp, 1, 0)
                    for id in range(1, C.NUD[iu] + 1):
                        uf[id] = ptx[id]
                    interp(densr, af, C.DENS, ptx, iud, C.NUD[iu], inrp, 1, 0)
                    for id in range(1, C.NUD[iu] + 1):
                        af[id] = ptx[id]
                    iud = C.NUD[iu]

                #       Contribution to J
                for id in range(1, C.NUD[iu] + 1):
                    C.RAD1[id] = C.RAD1[id] + C.WMUJ[iu, id] * uf[id]
                    ali1[id] = ali1[id] + C.WMUJ[iu, id] * af[id]
                C.FLUXC[ij] = C.FLUXC[ij] + C.WMUH[iu] * rim[1]

            #    End loop over impact rays
            #  100 CONTINUE

            #     solution of the transfer equation
            #     Variables:
            #     RAD1    - mean intensity
            ndx = C.NUDF[C.KMU]
            interp(densr, ss0, C.DENS, scx, ndx, C.ND, 4, 1, 1)
            djtot = 0.0
            for id in range(1, C.ND + 1):
                C.RAD1[id] = C.RAD1[id] * half
                ali1[id] = ali1[id] * half
                sss = scx[id]
                #        DELTAJ=(UN+SSS*ALI1(ID))*(RAD1(ID)-RAD00(ID))
                deltaj = (C.RAD1[id] - rad00[id]) / (un - sss * ali1[id])
                #        DELTAJ=RAD1(ID)-RAD00(ID)
                rad00[id] = rad00[id] + deltaj
                djtot = max(djtot, abs(deltaj / rad00[id]))
            #  1600 format(' IJ,LAM,ITRALI,DJ',i5,f10.2,i5,1p2e12.3)
            print(' IJ,LAM,ITRALI,DJ%5d%10.2f%5d%12.3E%12.3E' %
                  (ij, 2.997925e18 / fr, itrali, djtot, djmax))
            if djtot > djmax and itrali <= ntrali:
                continue  # GO TO 10
            break

        #     end loop for electron scattering
        interp(C.DENS, rad00, C.DENSF, rdx, C.ND, C.NDF, 4, 1, 0)
        for id in range(1, C.NDF + 1):
            C.SCCF[ij, id] = scc0[id] * rdx[id]
        C.FLUXC[ij] = C.FLUXC[ij] * 2.997925e18 / C.WLAMC[ij] ** 2 * 0.5

    #  500 CONTINUE
    return


def rtewin(iu):
    """      SUBROUTINE RTEWIN(IU)
    C     =====================
    C
    C     Solution of the radiative transfer equation - frequency by
    C     frequency - for the known source function.
    C
    C     The numerical method used:
    c     Discontinuous Finite Element (DFE) method
    c     Castor, Dykema, Klein, 1992, ApJ 387, 561.
    C
    C     Input through blank COMMON block:
    C      AB     - two-dimensional array  absorption coefficient (frequency,
    C               depth)
    C      STH     - Thermal source function
    C
    C     Version including velocity field and extension
    C      radiative transfer along ray IU

    对应 synspec54.f 行 20281–20528。
    RTEWIN 不修改标量哑元 IU，故无返回值约定。
    """
    un = 1.0
    two = 2.0
    half = 0.5  # PARAMETER (UN=1., TWO=2., HALF=0.5)
    tauref = 0.6666666666667  # PARAMETER (TAUREF = 0.6666666666667)
    st0 = np.zeros(2 * MDEPF + 1)
    tau = np.zeros(2 * MDEPF + 1)
    ab0 = np.zeros(2 * MDEPF + 1)
    rip = np.zeros(2 * MDEPF + 1)
    rim = np.zeros(2 * MDEPF + 1)
    #     dimension sc0(2*mdepf)
    sctd = np.zeros(2 * MDEPF + 1)

    iud = C.NUDF[iu]
    if iu <= C.NREXT:
        iud = 2 * C.NUDF[iu] - 1
    if iud == 1:
        return
    dlama0 = 0.0  # TODO(port): Fortran 中仅 NFREQ>1 时赋值，否则未定义
    if C.NFREQ > 1:
        dlama0 = (C.WLOBS[C.NFROBS] - C.WLOBS[1]) / (C.NFROBS - 1)

    #     overall loop over frequencies (observer's frame)
    for ij in range(1, C.NFROBS + 1):  # DO 500 IJ=1,NFROBS
        fr = C.FRQOBS[ij]
        wl0 = C.WLOBS[ij]

        #    Opacity and total source function
        #    interpolation in opacity table
        ivk = C.NOPAC - 2
        for id in range(1, iud + 1):
            ky = C.KRAY[iu, id]
            ydr = C.DRAY[iu, id]
            ydr1 = un - ydr
            dwlcom = wl0 * C.DFRQF[iu, id]
            wlcom = wl0 + dwlcom
            if wlcom <= C.WLAM[3]:
                abd1 = C.AB[1, ky - 1]
                std1 = C.STH[1, ky - 1]
                abd0 = C.AB[1, ky]
                std0 = C.STH[1, ky]
                ij1 = 1
            elif wlcom >= C.WLAM[C.NFREQ]:
                abd1 = C.AB[C.NFREQ, ky - 1]
                std1 = C.STH[C.NFREQ, ky - 1]
                abd0 = C.AB[C.NFREQ, ky]
                std0 = C.STH[C.NFREQ, ky]
                ij1 = C.NFREQ
            else:
                xijap = (wlcom - C.WLAM[3]) / dlama0
                ijap = int(xijap)  # INT 向零截断
                ijap = max(ijap, 1)
                ijap = min(ijap, C.NFREQ)
                wlap = C.WLAM[ijap]
                if wlcom < wlap:
                    ij1 = ijap - 1
                    iji = ijap - 1
                    while iji >= 1:  # do iji=ijap-1,1,-1
                        if wlcom >= C.WLAM[iji]:
                            break  # go to 20
                        iji -= 1
                    #   20          continue
                    ij1 = iji
                else:
                    ij1 = ijap + 1
                    iji = ijap + 1
                    while iji <= C.NFREQ:  # do iji=ijap+1,nfreq
                        if wlcom < C.WLAM[iji]:
                            break  # go to 30
                        iji += 1
                    #   30          continue
                    ij1 = iji - 1
                xfa = (C.WLAM[ij1 + 1] - wlcom) / \
                    (C.WLAM[ij1 + 1] - C.WLAM[ij1])
                abd1 = xfa * C.AB[ij1, ky - 1] + \
                    (1.0 - xfa) * C.AB[ij1 + 1, ky - 1]
                std1 = xfa * C.STH[ij1, ky - 1] + \
                    (1.0 - xfa) * C.STH[ij1 + 1, ky - 1]
                abd0 = xfa * C.AB[ij1, ky] + \
                    (1.0 - xfa) * C.AB[ij1 + 1, ky]
                std0 = xfa * C.STH[ij1, ky] + \
                    (1.0 - xfa) * C.STH[ij1 + 1, ky]
            ab0[id] = ydr1 * abd1 + ydr * abd0
            st0[id] = ydr1 * std1 + ydr * std0

            #   Add scattering
            ijc = C.IJCINT[ij1]
            if C.IFREQ != 17:
                sc1 = ydr1 * C.SCCF[ijc, ky - 1] + ydr * C.SCCF[ijc, ky]
                sc2 = ydr1 * C.SCCF[ijc + 1, ky - 1] + \
                    ydr * C.SCCF[ijc + 1, ky]
                sct = C.FRX1[ij1] * sc1 + (1.0 - C.FRX1[ij1]) * sc2
                sctd[id] = sct / ab0[id]
                st0[id] = st0[id] + sct / ab0[id]

        #    Optical depth scale
        tau[1] = 0.0
        iref = 1
        if iu <= C.NFIRY:
            for id in range(1, iud - 1 + 1):
                jd = id
                if id > C.NUDF[iu]:
                    jd = 2 * C.NUDF[iu] - id - 1
                dt = half * (ab0[id + 1] + ab0[id]) * C.DELZF[iu, jd]
                tau[id + 1] = tau[id] + dt
        else:
            for id in range(1, iud - 1 + 1):
                jd = id
                if id > C.NUD[iu]:
                    jd = 2 * C.NUD[iu] - id - 1
                dt = half * (ab0[id + 1] + ab0[id]) * C.DELZ[iu, jd]
                tau[id + 1] = tau[id] + dt
        if iu == C.KMU:
            for id in range(1, iud - 1 + 1):
                if tau[id] <= tauref and tau[id + 1] > tauref:
                    iref = id
            C.IREFD[ij] = iref

        #     Outgoing intensity
        if iu <= C.NREXT:
            #     1. External rays
            ndt = iud
            rip[ndt] = 0.0
            dt0 = tau[ndt] - tau[ndt - 1]
            dtaup1 = dt0 + un
            dtau2 = dt0 * dt0
            bb = two * dtaup1
            cc = dt0 * dtaup1
            aa = dtau2 + bb
            rim[ndt] = (aa * rip[ndt] - cc * st0[ndt] +
                        dt0 * st0[ndt - 1]) / bb
            for id in range(1, iud - 1 + 1):
                jd = iud - id
                dt0 = tau[jd + 1] - tau[jd]
                dtaup1 = dt0 + un
                dtau2 = dt0 * dt0
                bb = two * dtaup1
                cc = dt0 * dtaup1
                aa = un / (dtau2 + bb)
                rim[jd] = (two * rim[jd + 1] + dt0 * st0[jd + 1] +
                           cc * st0[jd]) * aa
        else:
            #      2. core rays
            ndt = iud
            fr15 = fr * 1.0e-15
            bnu = BN * fr15 * fr15 * fr15
            pland = bnu / (math.exp(HK * fr / C.TEMP[C.ND]) - un)
            dplan = bnu / (math.exp(HK * fr / C.TEMP[C.ND - 1]) - un)
            dplan = (pland - dplan) / (tau[iud] - tau[iud - 1])
            rip[ndt] = pland + dplan
            dt0 = tau[ndt] - tau[ndt - 1]
            dtaup1 = dt0 + un
            dtau2 = dt0 * dt0
            bb = two * dtaup1
            cc = dt0 * dtaup1
            aa = dtau2 + bb
            rim[ndt] = (aa * rip[ndt] - cc * st0[ndt] +
                        dt0 * st0[ndt - 1]) / bb
            for id in range(iud - 1, 0, -1):
                dt0 = tau[id + 1] - tau[id]
                dtaup1 = dt0 + un
                dtau2 = dt0 * dt0
                bb = two * dtaup1
                cc = dt0 * dtaup1
                aa = un / (dtau2 + bb)
                rim[id] = (two * rim[id + 1] + dt0 * st0[id + 1] +
                           cc * st0[id]) * aa
        C.FLUX[ij] = C.FLUX[ij] + C.WMUH[iu] * rim[1]

        #      if(ij.eq.1.or.ij.eq.3.or.ij.eq.5.or.ij.eq.9.or.ij.eq.83) then
        #      if(iu.eq.2.or.iu.eq.20.or.iu.eq.60.or.iu.eq.80) then
        #      do id=1,iud
        #         write(79,679) ij,iu,id,ab0(id),st0(id),sctd(id),
        #     *                 tau(id),rim(id),
        #     *                 flux(ij)
        #      end do
        #      end if
        #      end if
        #  679 format(3i5,1p6e12.4)

        #      CFX=WMUH(IU)*RIM(1)
        #      write(78,780) ij,iu,wlobs(ij),cfx,RIM(1)
        #  780 format(2i4,f10.3,1p2e16.8)

        #     if(iflux.ge.1) then
        #     output of emergent specific intensities to Unit 10 (line points)
        #     or 18 (two continuum points)
        #     IF(IJ.GT.2) THEN
        #     WRITE(10,618) WLAM(IJ),FLUX(IJ),RIM(1),IU
        #     ELSE
        #     WRITE(18,618) WLAM(IJ),FLUX(IJ),RIM(1),IU
        #     END IF
        #     end if
        # 618 FORMAT(1H ,f10.3,2pe15.5,i5)

        #     if needed (if iprin.ge.3), output of interesting physical
        #     quantities at the monochromatic optical depth  tau(nu)=2/3
        #     IF(IPRIN.GE.3) THEN
        #     T0=LOG(TAU(IREF+1)/TAU(IREF))
        #     X0=LOG(TAU(IREF+1)/TAUREF)/T0
        #     X1=LOG(TAUREF/TAU(IREF))/T0
        #     DMREF=EXP(LOG(DM(IREF))*X0+LOG(DM(IREF+1))*X1)
        #     TREF=EXP(LOG(TEMP(IREF))*X0+LOG(TEMP(IREF+1))*X1)
        #     STREF=EXP(LOG(ST0(IREF))*X0+LOG(ST0(IREF+1))*X1)
        #     SSREF=EXP(LOG(-SS0(IREF))*X0+LOG(-SS0(IREF+1))*X1)
        #     SREF=STREF+SSREF
        #     ALM=2.997925E18/FREQ(IJ)
        #     WRITE(36,636) IJ,ALM,IREF,DMREF,TREF,STREF,SSREF,SREF
        # 636 FORMAT(1H ,I3,F10.3,I4,1PE10.3,0PF10.1,1X,1P3E10.3)
        #     END IF

        #       Contribution to J and H
        #        do id=1,nud(iu)
        #          rad1(id)=rad1(id)+wmuj(iu,id)*uf(id)
        #          ali1(id)=ali1(id)+wmuj(iu,id)*af(id)
        #        end do
        #        FLUXc(IJ)=FLUXc(IJ)+WMUH(IU)*RIM(1)

        #     end of the loop over frequencies
    #  500 CONTINUE
    return


def velset():
    """      SUBROUTINE VELSET
    C     =================
    C
    C     Determination of the macroscopic velocity as a function of depth
    C
    C     Input:
    C
    C     RSTAR   - stellar radius (in solar radii or in cm)
    C     RMAX    - maximum radial extent (in stellar radii)
    C     AMLOSS  - mass loss rate ( in solar masses per year)
    C     VELMAX  - maximum velocity (= V_infinity) - in km/s
    C     BETA    - beta exponent in the beta-law for velocity
    C     NDRAD   - Number of layers
    C     NRCORE  - Number of core rays

    对应 synspec54.f 行 20534–20737。
    """
    #      parameter (un=1.,two=2.)
    zz = np.zeros(MDEPTH + 1)
    vel0 = np.zeros(MDEPTH + 1)
    rrel = np.zeros(MDEPTH + 1)
    #     *          dvel0(mdepth),vel1(mdepth),hstt(mdepth),
    den0 = np.zeros(MDEPTH + 1)
    vel00 = np.zeros(MDEPTH + 1)
    ind = np.zeros(MDEPTH + 1, dtype=np.int64)
    densa = np.zeros(MDEPTH + 1)
    eleca = np.zeros(MDEPTH + 1)
    tempa = np.zeros(MDEPTH + 1)
    rda = np.zeros(MDEPTH + 1)
    rrela = np.zeros(MDEPTH + 1)
    vel0a = np.zeros(MDEPTH + 1)

    un = 1.0
    two = 2.0

    def _f(s):  # 自由格式读入的浮点解析（容许 Fortran D 指数）
        return float(s.replace('D', 'E').replace('d', 'e'))

    # read(55,*,err=100,end=100)：文件结束或读错误 → 标号 100（return）
    try:
        _toks = []
        while len(_toks) < 10:  # 自由格式读可跨记录续行
            _toks.extend(read_line(55).replace(',', ' ').split())
        rstar = _f(_toks[0])
        rmax = _f(_toks[1])
        amloss = _f(_toks[2])
        C.VINF = _f(_toks[3])
        beta = _f(_toks[4])
        ndrad = int(_f(_toks[5]))  # 局部量（不属于任何 COMMON 块）
        C.NRCORE = int(_f(_toks[6]))
        C.NFIRY = int(_f(_toks[7]))
        C.NDF = int(_f(_toks[8]))
        nda = int(_f(_toks[9]))    # 局部量
    except (EOFError, ValueError):
        return  # err=100 / end=100 → 100 continue → return
    rstr = rstar
    if rstar < 1.0e5:
        rstr = rstar * 6.9598e10
    amdot = amloss * 6.3029e25
    C.RCORE = rstr
    C.XMDOT = amdot
    C.BETAV = beta
    con = amdot / 12.566e5
    conr = con / rstr / rstr
    nrext0 = ndrad - C.ND
    zz[C.ND + nrext0] = 0.0
    C.RD[C.ND + nrext0] = rstr
    rrel[C.ND + nrext0] = 1.0
    for iid in range(1, C.ND - 1 + 1):
        id = C.ND - iid
        zz[id + nrext0] = zz[id + 1 + nrext0] + 2.0 * \
            (C.DM[id + 1] - C.DM[id]) / (C.DENS[id + 1] + C.DENS[id])
        C.RD[id + nrext0] = rstr + zz[id + nrext0]
        rrel[id + nrext0] = C.RD[id + nrext0] / rstr

    for id in range(1 + nrext0, C.ND + nrext0 + 1):
        vel0[id] = con / C.RD[id] ** 2 / C.DENS[id - nrext0]
        vel00[id] = vel0[id]
        if vel00[id] > C.VINF:
            vel00[id] = C.VINF
    vin = vel0[nrext0 + 1]
    r1 = rrel[nrext0 + 1]

    if rrel[1 + nrext0] < rmax and C.ND < ndrad:
        rl1 = 1.0 - 1.0 / rrel[1 + nrext0]
        rl2 = 1.0 - 1.0 / rmax
        drl = (rl2 - rl1) / nrext0
        for id in range(1, nrext0 + 1):
            rlo = rl2 - (id - 1) * drl
            rrel[id] = 1.0 / (1.0 - rlo)
            C.RD[id] = rrel[id] * rstr

    # TODO(port): idc/rc/r0/r00/numid0/v2 在 Fortran 中依赖下面循环内赋值，
    # 若循环不执行或提前 GO TO 10 则未定义；此处给安全初值。
    numid0 = 0
    idc = 0
    rc = 0.0
    r0 = 0.0
    r00 = 0.0
    v2 = 0.0
    for id in range(C.ND + nrext0 - 1, nrext0 + 1 - 1, -1):
        r0 = rrel[id]
        numid = 0
        for id1 in range(C.ND + nrext0 - 1, nrext0 + 1 - 1, -1):
            x = un - r0 / rrel[id1]
            if x < 1.0e-6:
                x = 1.0e-6
            v2 = C.VINF * x ** beta
            ind[id1] = 0
            if v2 >= vel0[id1]:
                ind[id1] = id1
                numid = numid + 1
        if numid == 0:
            break  # go to 10
        rsum = 0.0
        isum = 0
        for id1 in range(C.ND + nrext0 - 1, nrext0 + 1 - 1, -1):
            if ind[id1] > 0:
                rsum = rsum + rrel[id1]
                isum = isum + id1
        rc = rsum / numid
        idc = idiv(isum, numid)  # Fortran 整数除法
        numid0 = numid
        r00 = r0
    #   10 continue
    v1 = vel0[idc]
    r0 = (r0 + r00) * 0.5
    if r0 < rc:
        v2 = C.VINF * (un - r0 / rc) ** beta
    #  602 format('numid,idc,rc,r0,v1,v2 ',2i4,4f10.5)
    print('numid,idc,rc,r0,v1,v2 %4d%4d%10.5f%10.5f%10.5f%10.5f' %
          (numid0, idc, rc, r0, v1, v2))

    for id in range(C.ND + nrext0 - 1, 0, -1):
        if rrel[id] > rc and rrel[id] > r0:
            vel0[id] = C.VINF * (1.0 - r0 / rrel[id]) ** beta

    t1 = C.TEMP[1]
    erel = C.ELEC[1] / C.DENS[1]
    for id in range(C.ND, 0, -1):
        C.TEMP[id + nrext0] = C.TEMP[id]
        den0[id + nrext0] = C.DENS[id]
        C.ELEC[id + nrext0] = C.ELEC[id]
        for i in range(1, C.NLEVEL + 1):
            C.POPUL[i, id + nrext0] = C.POPUL[i, id]
        C.WMM[id + nrext0] = C.WMM[id]
        C.WMY[id + nrext0] = C.WMY[id]
        C.YTOT[id + nrext0] = C.YTOT[id]
        for i in range(1, C.NATOM + 1):
            C.RELAB[i, id + nrext0] = C.RELAB[i, id]
            C.ABUND[i, id + nrext0] = C.ABUND[i, id]
        for i in range(1, MATOM + 1):
            C.ABNDD[i, id + nrext0] = C.ABNDD[i, id]

    for id in range(1, nrext0 + 1):
        C.TEMP[id] = t1
        C.WMM[id] = C.WMM[nrext0 + 1]
        C.WMY[id] = C.WMY[nrext0 + 1]
        C.YTOT[id] = C.YTOT[nrext0 + 1]
        for i in range(1, C.NATOM + 1):
            C.RELAB[i, id] = C.RELAB[i, nrext0 + 1]
            C.ABUND[i, id] = C.ABUND[i, nrext0 + 1]
        for i in range(1, MATOM + 1):
            C.ABNDD[i, id] = C.ABNDD[i, nrext0 + 1]
    C.IDSTD = C.IDSTD + nrext0

    C.VINF = C.VINF * 1.0e5
    #  600 format('    ID    M      TEMP       ELEC      DENS             ',
    #     *       'R       Rrel     VEL'/)
    print('    ID    M      TEMP       ELEC      DENS             '
          'R       Rrel     VEL')
    print()
    for id in range(1, C.ND + nrext0 + 1):
        if vel0[id] > 0.0:
            C.DENS[id] = con / C.RD[id] ** 2 / vel0[id]
        C.VEL[id] = vel0[id] * 1.0e5
        #        velc(id)=vel0(id)/2.997925e5

    for id in range(C.ND, 0, -1):
        id1 = id + nrext0
        C.ELEC[id1] = C.ELEC[id1] * C.DENS[id1] / den0[id1]
        for i in range(1, C.NLEVEL + 1):
            C.POPUL[i, id1] = C.POPUL[i, id1] * C.DENS[id1] / den0[id1]

    for id in range(1, nrext0 + 1):
        C.ELEC[id] = C.ELEC[nrext0 + 1] * C.DENS[id] / C.DENS[nrext0 + 1]
        for i in range(1, C.NLEVEL + 1):
            C.POPUL[i, id] = C.POPUL[i, nrext0 + 1] * \
                C.DENS[id] / C.DENS[nrext0 + 1]

    C.ND = ndrad
    if C.NDF == 0:
        C.NDF = C.ND
    for id in range(1, C.ND + 1):
        #  601 format(1h ,i3,1pe10.3,0pf8.0,1p3e12.3,0pf10.4,0p2f8.2)
        print(' %3d%10.3E%8.0f%12.3E%12.3E%12.3E%10.4f%8.2f' %
              (id, C.DM[id], C.TEMP[id], C.ELEC[id], C.DENS[id], C.RD[id],
               rrel[id], vel0[id]))
        write_line(96, ' %3d%10.3E%8.0f%12.3E%12.3E%12.3E%10.4f%8.2f%8.2f' %
                   (id, C.DM[id], C.TEMP[id], C.ELEC[id], C.DENS[id],
                    C.RD[id], rrel[id], vel0[id], vel00[id]))

    if nda > 0:
        xr1 = math.log(C.DENS[1])
        xr2 = math.log(C.DENS[C.ND])
        dxr = (xr2 - xr1) / float(nda - 1)
        for id in range(1, nda + 1):
            densa[id] = math.exp(xr1 + float(id - 1) * dxr)
        interp(C.DENS, C.TEMP, densa, tempa, C.ND, nda, 3, 1, 1)
        interp(C.DENS, C.ELEC, densa, eleca, C.ND, nda, 3, 1, 1)
        interp(C.DENS, C.RD, densa, rda, C.ND, nda, 3, 1, 1)
        interp(C.DENS, rrel, densa, rrela, C.ND, nda, 3, 1, 1)
        interp(C.DENS, vel0, densa, vel0a, C.ND, nda, 3, 1, 1)
        for id in range(1, nda + 1):
            #  603 format(1h ,i3,0pf8.0,1p3e12.3,0pf10.4,0p2f8.2)
            print(' %3d%8.0f%12.3E%12.3E%12.3E%10.4f%8.2f' %
                  (id, tempa[id], eleca[id], densa[id], rda[id],
                   rrela[id], vel0a[id]))
            write_line(96, ' %3d%8.0f%12.3E%12.3E%12.3E%10.4f%8.2f' %
                       (id, tempa[id], eleca[id], densa[id], rda[id],
                        rrela[id], vel0a[id]))

    #  100 continue
    return
