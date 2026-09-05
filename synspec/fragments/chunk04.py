def croset(cross):
    """
C     SET UP ARRAY CROSS  - PHOTOIONIZATION CROSS-SECTIONS
    对应 synspec54.f 行 3462–3496
    """
    ij0 = 2
    if C.NFREQ == 1:
        ij0 = 1
    if C.IMODE == 2:
        ij0 = C.NFREQ
    for ij in range(1, ij0 + 1):
        for it in range(1, MCROSS + 1):
            cross[it, ij] = 0.0
    for it in range(1, C.NLEVEL + 1):
        if C.indexp[it] != 5:
            for ij in range(1, ij0 + 1):
                fr = C.FREQ[ij]
                cross[it, ij] = sigk(fr, it, 0)
        else:
            for ij in range(1, ij0 + 1):
                fr = C.FREQ[ij]
                cross[it, ij] = sigk(fr, it, 1)
                if fr < C.fropc[it]:
                    cross[it, ij] = 0.0
    return


def crosew(cross):
    """
C     SET UP COMMON/PHOPAR/  - PHOTOIONIZATION CROSS-SECTIONS
    对应 synspec54.f 行 3500–3532
    """
    ij0 = C.NFREQC
    for ij in range(1, ij0 + 1):
        for it in range(1, MCROSS + 1):
            cross[it, ij] = 0.0
    for it in range(1, C.NLEVEL + 1):
        if C.indexp[it] != 5:
            for ij in range(1, ij0 + 1):
                fr = C.FREQC[ij]
                cross[it, ij] = sigk(fr, it, 0)
        else:
            for ij in range(1, ij0 + 1):
                fr = C.FREQC[ij]
                cross[it, ij] = sigk(fr, it, 1)
                if fr < C.fropc[it]:
                    cross[it, ij] = 0.0
    return


def sigk(fr, itr, mode):
    """
C     driver for evaluating the photoionization cross-sections
C
C     Input: FR  -  frequency
C            ITR -  index of the transition
c            mode - =0 cross-section equal to zero longward of edge
c            mode - >0 cross-section non-zero (extrapolated) longward of edge
    对应 synspec54.f 行 3538–3708
    """
    # PARAMETER (SIH0=2.815D29, E10=2.3025851)
    SIH0 = 2.815e29
    E10 = 2.3025851
    # parameter (wi1=911.753878, wi2=227.837832, un=1.e0)
    wi1 = 911.753878
    wi2 = 227.837832
    un = 1.0e0
    # 语句函数（statement functions）
    # PEACH(X,S,A,B)  =A*X**S*(B+X*(1.-B))*1.E-18
    def peach(x, s, a, b):
        return a * x**s * (b + x * (1.0 - b)) * 1.0e-18
    # HENRY(X,S,A,B,C)=A*X**S*(C+X*(B-2.*C+X*(1.+C-B)))*1.E-18
    def henry(x, s, a, b, c):
        return a * x**s * (c + x * (b - 2.0 * c + x * (1.0 + c - b))) * 1.0e-18
    # DIMENSION XFIT(MFIT), SFIT(MFIT)  — 局部数组，1 基索引
    xfit = np.zeros(MFIT + 1)
    sfit = np.zeros(MFIT + 1)

    sigk_v = 0.0
    ii = itr
    fr0 = C.ENION[ii] / 6.6256e-27
    if fr0 <= 0.0:
        return sigk_v
    wl0 = 2.997925e18 / fr0

    #     wavelength with an explicit correction to the air wavalength
    if wl0 > C.vaclim:
        alm = 1.0e8 / (wl0 * wl0)
        xn1 = 64.328 + 29498.1 / (146.0 - alm) + 255.4 / (41.0 - alm)
        wl0 = wl0 / (xn1 * 1.0e-6 + un)
        fr0 = 2.997925e18 / wl0

    if mode == 0 and fr < fr0:
        return sigk_v

    #     IBF(ITR) is the switch controlling the mode of evaluation of the
    #        cross-section:
    #      = 0  hydrogenic cross-section, with Gaunt factor set to 1
    #      = 1  hydrogenic cross-section with exact Gaunt factor
    #      = 2  Peach-type expression (see function PEACH)
    #      = 3  Henry-type expression (see function HENRY)
    #      = 4  Butler new calculations
    #      = 7  hydrogenic cross-section with Gaunt factor from K. Werner
    #      = 9  Opacity project fits (routine TOPBAS - interpolations)
    #      > 100 - cross-sections extracted form TOPBASE, for several points
    #           In this case, IBF-100 is the number of points
    #      < 0  non-standard, user supplied expression (user should update
    #           subroutine SPSIGK)
    #
    #      for H- : for any IBF > 0  - standard expression
    #      for He I:
    #       for IBF = 11 or = 13  -  Opacity Project cross section
    #                Seaton-Ferney's cubic fits, Hummer's procedure (HEPHOT)
    #           IBF = 11  means that the multiplicity S=1 (singlet)
    #           IBF = 13  means that the multiplicity S=3 (triplet)
    #       for IBF = 10  - cross section, based on Opacity Project, but
    #                       appropriately averaged for an averaged level

    ib = C.IBF[itr]
    iq = C.NQUANT[ii]
    ie = C.IEL[ii]
    if ie == C.IELHM:
        sigk_v = sbfhmi(fr)
        return sigk_v
    if ie == C.IELHE1 and ib >= 10 and ib <= 13:
        sigk_v = sbfhe1(ii, ib, fr)
        return sigk_v

    ch = C.IZ[ie] * C.IZ[ie]
    iq5 = iq * iq * iq * iq * iq

    if ib == 0:
        #        hydrogenic expression (for IBF = 0)
        sigk_v = SIH0 / fr / fr / fr * ch * ch / iq5

    #        exact hydrogenic - with Gaunt factor (for IBF=1)
    elif ib == 1:
        sigk_v = SIH0 / fr / fr / fr * ch * ch / iq5
        #        IF(FR.GE.FR0.OR.(IE.EQ.IELH.AND.IQ.LE.3))
        #    *   SIGK=SIGK*GAUNT(IQ,FR/CH)
        fr0l = 0.95 * fr0
        if fr >= fr0:
            sigk_v = sigk_v * gaunt(iq, fr / ch)
        elif fr >= fr0l:
            gau0 = gaunt(iq, fr0 / ch)
            corg = (fr - fr0l) / (fr0 - fr0l) * (gau0 - 1.0) + 1.0
            sigk_v = sigk_v * corg

    elif ib == 2:
        #        Peach-type formula (for IBF=2)
        if C.GAMBF[ii] > 0.0:
            if C.GAMBF[ii] < 1.0e6:
                fr0 = 2.997925e18 / C.GAMBF[ii]
            else:
                fr0 = C.GAMBF[ii]
            if fr < fr0:
                return sigk_v
        frel = fr0 / fr
        sigk_v = peach(frel, C.S0BF[ii], C.ALFBF[ii], C.BETBF[ii])

    elif ib == 3:
        #        Henry-type formula (for IBF=3)
        frel = fr0 / fr
        sigk_v = henry(frel, C.S0BF[ii], C.ALFBF[ii], C.BETBF[ii], C.GAMBF[ii])

    #     Butler expression
    elif ib == 4:
        frel = fr0 / fr
        xl = math.log(frel)
        sl = C.S0BF[ii] + xl * (C.ALFBF[ii] + xl * C.BETBF[ii])
        sigk_v = math.exp(sl)

    #     exact hydrogenic - with Gaunt factor from K Werner (for IBF=7)
    elif ib == 7:
        iq5 = iq * iq * iq * iq * iq
        sigk_v = SIH0 / (fr * fr * fr) * ch * ch / iq5 * gntk(iq, fr / ch)

    #     selected Opacity Project data (for IBF=9)
    #     (c.-s. evaluated by routine TOPBAS which needs an input file RBF.DAT)
    elif ib == 9:
        sigk_v = topbas(fr, fr0, C.TYPLEV[ii])

    #     other Opacity Project data (for IBF>100)
    #     (c.-s. evaluated by interpolating from direct input data)
    elif ib > 100:
        nfit = ib - 100
        x = math.log10(fr / fr0)
        if x < C.XTOP[1, ii]:
            sigm = 0.0
        else:
            for ifit in range(1, nfit + 1):
                xfit[ifit] = C.XTOP[ifit, ii]
                sfit[ifit] = C.CTOP[ifit, ii]
            sigm = ylintp(x, xfit, sfit, nfit, MFIT)
            sigm = 1.0e-18 * math.exp(E10 * sigm)
        sigk_v = sigm

    elif ib < 0:
        # CALL SPSIGK(ITR,IB,FR,SIGSP) — SPSIGK 给标量哑元 SIGSP 赋值，按约定解包接收
        sigsp = 0.0
        itr, ib, fr, sigsp = spsigk(itr, ib, fr, sigsp)
        sigk_v = sigsp

    if C.IATM[ii] == C.IATH and ii > C.N0HN + 2.0 and ib <= 1 and fr < fr0:
        fr1 = C.fropc[ii]
        frdec = min(fr1 * 1.25, fr0)
        if fr > fr1 and fr < frdec:
            sigk_v = sigk_v * (fr - fr1) / (frdec - fr1)
    return sigk_v


def gaunt(i, fr):
    """
C     Hydrogenic bound-free Gaunt factor for the principal quantum
C     number I and frequency FR
    对应 synspec54.f 行 3715–3756
    """
    x = fr / 2.99793e14
    gaunt_v = 1.0
    if i == 1:
        gaunt_v = (1.2302628 + x * (-2.9094219e-3 + x * (7.3993579e-6 - 8.7356966e-9 * x))
                   + (12.803223 / x - 5.5759888) / x)
    elif i == 2:
        gaunt_v = (1.1595421 + x * (-2.0735860e-3 + 2.7033384e-6 * x) + (-1.2709045 +
                   (-2.0244141 / x + 2.1325684) / x) / x)
    elif i == 3:
        gaunt_v = (1.1450949 + x * (-1.9366592e-3 + 2.3572356e-6 * x) + (-0.55936432 +
                   (-0.23387146 / x + 0.52471924) / x) / x)
    elif i == 4:
        gaunt_v = (1.1306695 + x * (-1.3482273e-3 + x * (-4.6949424e-6 + 2.3548636e-8 * x))
                   + (-0.31190730 + (0.19683564 - 5.4418565e-2 / x) / x) / x)
    elif i == 5:
        gaunt_v = (1.1190904 + x * (-1.0401085e-3 + x * (-6.9943488e-6 + 2.8496742e-8 * x))
                   + (-0.16051018 + (5.5545091e-2 - 8.9182854e-3 / x) / x) / x)
    elif i == 6:
        gaunt_v = (1.1168376 + x * (-8.9466573e-4 + x * (-8.8393133e-6 + 3.4696768e-8 * x))
                   + (-0.13075417 + (4.1921183e-2 - 5.5303574e-3 / x) / x) / x)
    elif i == 7:
        gaunt_v = (1.1128632 + x * (-7.4833260e-4 + x * (-1.0244504e-5 + 3.8595771e-8 * x))
                   + (-9.5441161e-2 + (2.3350812e-2 - 2.2752881e-3 / x) / x) / x)
    elif i == 8:
        gaunt_v = (1.1093137 + x * (-6.2619148e-4 + x * (-1.1342068e-5 + 4.1477731e-8 * x))
                   + (-7.1010560e-2 + (1.3298411e-2 - 9.7200274e-4 / x) / x) / x)
    elif i == 9:
        gaunt_v = (1.1078717 + x * (-5.4837392e-4 + x * (-1.2157943e-5 + 4.3796716e-8 * x))
                   + (-5.6046560e-2 + (8.5139736e-3 - 4.9576163e-4 / x) / x) / x)
    elif i == 10:
        gaunt_v = (1.1052734 + x * (-4.4341570e-4 + x * (-1.3235905e-5 + 4.7003140e-8 * x))
                   + (-4.7326370e-2 + (6.1516856e-3 - 2.9467046e-4 / x) / x) / x)
    return gaunt_v


def gntk(i, fr):
    """
C     Hydrogenic bound-free Gaunt factor for the principal quantum
C     number I and frequency FR (from Klaus Werner)
    对应 synspec54.f 行 3763–3780
    """
    gntk_v = 1.0
    if i > 3:
        return gntk_v  # GO TO 16 → RETURN
    y = 1.0 / fr
    # GO TO (1,2,3),I —— 计算 GO TO，重构为 if/elif
    if i == 1:
        gntk_v = 0.9916 + y * (2.71852e13 - y * 2.26846e30)
    elif i == 2:
        gntk_v = 1.1050 - y * (2.37490e14 - y * 4.07677e28)
    elif i == 3:
        gntk_v = 1.1010 - y * (0.98632e14 - y * 1.03540e28)
    # 标号 16
    return gntk_v


def spsigk(itr, ib, fr, sigsp):
    """
C     Non-standard evaluation of the photoionization cross-sections
C     Basically user-suppled procedure; here are some examples
    对应 synspec54.f 行 3787–3820

    给标量哑元 SIGSP 赋值 → 按约定返回全部标量哑元 (itr, ib, fr, sigsp)
    """
    sigsp = 0.0
    if itr <= 0:
        return itr, ib, fr, sigsp

    #     Special formula for the He I ground state
    if ib == -201:
        sigsp = 7.3e-18 * math.exp(1.373 - 2.311e-16 * fr)

    #     Special formula for the averaged <n=2> level of He I
    if ib == -202:
        sigsp = sghe12(fr)

    #     Carbon ground configuration levels 2p2 1D and 1S
    if ib == -602 or ib == -603:
        # CALL CARBON(IB,FR,SG) — CARBON 给标量哑元 SG 赋值，按约定解包接收
        sg = 0.0
        ib, fr, sg = carbon(ib, fr, sg)
        sigsp = sg

    #     Hidalgo (Ap.J. 153, 981, 1968) photoionization data
    if ib <= -101 and ib >= -137:
        sigsp = hidalg(ib, fr)

    #     Reilman and Manson (Ap.J. Suppl. 40, 815, 1979) photoionization data
    if ib <= -301 and ib >= -337:
        sigsp = reiman(ib, fr)
    return itr, ib, fr, sigsp


def carbon(ib, fr, sg):
    """
C     Photoionization cross-section for neutral carbon 2p1D and 2p1S
C     levels (G.B.Taylor - private communication)
    对应 synspec54.f 行 3828–3879

    给标量哑元 SG 赋值 → 按约定返回全部标量哑元 (ib, fr, sg)
    """
    # DIMENSION FR2(34),SG2(34),FR3(45),SG3(45)
    # DATA 初始化且之后不再修改 —— 函数顶部直接赋值（1 基索引，索引 0 不用）
    fr2 = np.array([0.0,
        0.74, 0.75, 0.76, 0.77, 0.78, 0.79, 0.80, 0.81, 0.82,
        0.83,       0.85, 0.86, 0.87, 0.88, 0.89, 0.90,
        0.91, 0.92, 0.93, 0.94, 0.95, 0.96, 0.97, 0.98, 0.99,
        1.00, 1.10, 1.20, 1.30, 1.45, 1.50, 1.60, 1.80, 2.0])
    sg2 = np.array([0.0,
        12.04, 12.03, 12.09, 12.26, 12.60, 13.24, 14.36, 16.24,
        19.28, 23.94, 37.41, 42.88, 44.76, 43.41, 40.46, 37.19,
        34.26, 31.82, 29.96, 28.57, 27.68, 27.37, 27.84, 29.69,
        34.45, 46.35, 13.80, 11.54, 10.40,  8.96,  8.54,  7.47,
         6.53,  5.66])
    fr3 = np.array([0.0,
        0.66, 0.68, 0.70, 0.72, 0.74, 0.76, 0.78, 0.80, 0.82,
        0.84, 0.86, 0.864, 0.866, 0.868, 0.87, 0.874, 0.876, 0.88,
        0.882, 0.884, 0.886, 0.888, 0.89, 0.894, 0.896, 0.898, 0.90,
        0.904, 0.908, 0.910, 0.920, 0.94, 0.98, 1.00, 1.10, 1.20,
        1.26, 1.34, 1.36, 1.40, 1.46, 1.60, 1.70, 1.80, 2.0])
    sg3 = np.array([0.0,
        13.94, 13.29, 12.56, 11.73, 10.82, 10.18,  8.62,  7.27,
         5.74,  4.14,  4.61,  5.92,  6.94,  8.34, 10.21, 16.12,
        20.64, 34.56, 44.82, 57.71, 73.09, 89.99, 106.38, 127.08,
       128.38, 124.44, 117.17, 99.32, 82.95, 76.05, 52.65, 33.23,
        21.29, 18.69, 12.62, 11.44,  9.77,  7.53, 10.47,  9.65,
        10.19,  7.28,  6.70,  6.11,  4.96])
    # DATA NC2,NC3/34,45/
    nc2 = 34
    nc3 = 45
    # DATA FR0/3.28805E15/
    fr0 = 3.28805e15

    f = fr / fr0
    # IF(IB.NE.-602) GO TO 25
    if ib == -602:
        j = 2
        # IF(F.LE.FR2(1)) GO TO 20 —— 直接用第一个间隔外推
        if f > fr2[1]:
            for i in range(2, nc2 + 1):  # DO 10 I=2,NC2
                j = i
                if f > fr2[i - 1] and f <= fr2[i]:
                    break  # GO TO 20
            # 循环正常结束时 j 保持最后赋值（=NC2），与 Fortran 一致
        # 标号 20
        sg = (f - fr2[j - 1]) / (fr2[j] - fr2[j - 1]) * (sg2[j] - sg2[j - 1]) + sg2[j - 1]
        sg = sg * 1.0e-18
    # 标号 25；IF(IB.NE.-603) GO TO 50
    if ib == -603:
        j = 2
        # IF(F.LE.FR3(1)) GO TO 40
        if f > fr3[1]:
            for i in range(2, nc3 + 1):  # DO 30 I=2,NC3
                j = i
                if f > fr3[i - 1] and f <= fr3[i]:
                    break  # GO TO 40
        # 标号 40
        sg = (f - fr3[j - 1]) / (fr3[j] - fr3[j - 1]) * (sg3[j] - sg3[j - 1]) + sg3[j - 1]
        sg = sg * 1.0e-18
    # 标号 50
    return ib, fr, sg


def sghe12(fr):
    """
C     Special formula for the photoionization cross-section from the
C     averaged <n=2> level of He I
    对应 synspec54.f 行 3885–3901
    """
    # DATA C1/3.E0/,C2/9.E0/,C3/1.6E1/,
    #  A1/6.45105E-18/,A2/3.02E-19/,A3/9.9847E-18/,A4/1.1763673E-17/,
    #  A5/3.63662E-19/,A6/-2.783E2/,A7/1.488E1/,A8/-2.311E-1/,
    #  E1/3.5E0/,E2/3.6E0/,E3/1.91E0/,E4/2.9E0/,E5/3.3E0/
    c1 = 3.0e0
    c2 = 9.0e0
    c3 = 1.6e1
    a1 = 6.45105e-18
    a2 = 3.02e-19
    a3 = 9.9847e-18
    a4 = 1.1763673e-17
    a5 = 3.63662e-19
    a6 = -2.783e2
    a7 = 1.488e1
    a8 = -2.311e-1
    e1 = 3.5e0
    e2 = 3.6e0
    e3 = 1.91e0
    e4 = 2.9e0
    e5 = 3.3e0
    x = fr * 1.0e-15
    xx = math.log(fr)
    sghe12_v = (c1 * (a1 / x**e1 + a2 / x**e2) + a3 / x**e3 + c2 * (a4 / x**e4 + a5 / x**e5) +
                c1 * math.exp(a6 + xx * (a7 + xx * a8))) / c3
    return sghe12_v


def hidalg(ib, fr):
    """
C     Read table of wavelengths and photo-ionization cross-sections
C     from Hidalgo (1968, Ap. J., 153, 981) for the species indicated by IB
C     (Hidalgo's number = INDEX = -IB-100).
C     Compute linearly interpolated value of the cross-section
C     at the frequency FR.
    对应 synspec54.f 行 3907–3980
    """
    # DIMENSION WL1(20),WL2(20),WLI(20),SIG0(20,24),SIGS(20)
    # DATA WL1 /.../
    wl1 = np.array([0.0,
        39.1, 80.9, 97.6, 100.1, 104.3, 107.2, 108.7, 111.9, 113.6, 115.4,
        117.1, 119.0, 124.8, 126.9, 129.1, 131.3, 133.6, 136.0, 138.5, 141.1])
    # DATA WL2 /.../
    wl2 = np.array([0.0,
        68.5, 80.9, 100.1, 120.9, 158.8, 165.7, 177.3, 190.6, 200.7, 206.2,
        211.9, 218.0, 224.5, 231.3, 246.3, 0.0, 0.0, 0.0, 0.0, 0.0])  # 5*0.
    # DATA SIG0 /.../ —— 480 个值按 Fortran 列主序填充 (20,24)
    _sig0_flat = (
        [0.0] * 120 +
        [.0460, .2400, .3500, .3700, .4000, .4300, .4400, .4600, .4700, .4900,
         .5000, .5200, .5700, .6200] + [0.0] * 6 +
        [0.0] * 80 +
        [.0092, .1000, .1900, .2100, .2300, .2500, .2600, .2900, .3000, .3200,
         .3400, .3500, .4100, .4300, .4500, .4800, .5000, .5300, .5600, .5900] +
        [0.0] * 20 +
        [.3400, .4600, .6300, .7700, .9100, 1.080] + [0.0] * 14 +
        [0.0] * 20 +
        [.0064, .1100, .2200, .4100, .9400, 1.000, 1.300, 1.600] + [0.0] * 12 +
        [0.0] * 80 +
        [.0370, .0650, .1300, .2400, .5500, .6300, .7700, .9500, 1.100, 1.250] +
        [0.0] * 10 +
        [0.0] * 40 +
        [.0220, .0390, .0800, .1500, .3500, .4000, .4900, .6200, .7200, .7800,
         .8500, .9300, 1.020] +
        [0.0] * 7
    )
    sig0 = np.zeros((21, 25))
    sig0[1:21, 1:25] = np.array(_sig0_flat).reshape((20, 24), order='F')
    wli = np.zeros(21)
    sigs = np.zeros(21)

    index = -ib - 100
    num = 20
    if index >= 13 and index <= 27:
        num = 15
    # TODO(port): IB 在 [-137,-114] 时 INDEX∈[14,37]，超出 SIG0 声明的第二维 24；
    # 原 Fortran 会越界读相邻存储，此处按声明维度直译，越界时 numpy 会报错。
    for i in range(1, num + 1):  # DO 10 I=1,NUM
        if index < 13:
            wli[i] = wl1[i]
        if index >= 13:
            wli[i] = wl2[i]
        sigs[i] = sig0[i, index]

    wlam = 2.997925e18 / fr
    il = 1
    ir = num
    for i in range(1, num):  # DO 50 I=1,NUM-1
        if wlam >= wli[i] and wlam <= wli[i + 1]:
            il = i
            ir = i + 1
            break  # GO TO 60
    # 标号 60：LINEAR INTERPOLATION:
    sigm = (sigs[ir] - sigs[il]) * (wlam - wli[il]) / (wli[ir] - wli[il]) + sigs[il]

    #     IF OUTSIDE WAVELENGTH RANGE SET TO FIRST(LAST) VALUE:
    if wlam <= wli[1]:
        sigm = sigs[1]
    if wlam >= wli[num]:
        sigm = sigs[num]

    #     IF LAST NON-ZERO SIG VALUES, NO INTERPOLATION:
    #       IF(SIGS(IR).EQ.0.) SIGM=SIGS(IL)

    hidalg_v = sigm * 1.0e-18
    return hidalg_v


def reiman(ib, fr):
    """
C     Read table of photon energies and photo-ionization cross-sections
C     from Reilman & Manson (1979, Ap. J. Suppl., 40, 815) for the species
C     indicated by IB
C
C     Compute linearly interpolated value of the cross-section
C     at the frequency FR.
C
C     (At the moment, only a few transitions are considered)
    对应 synspec54.f 行 3986–4052
    """
    # DIMENSION HEV(30),F0(30),SIG0(30,2),SIGS(30)
    # DATA HEV /.../
    hev = np.array([0.0,
        130., 160., 190., 210., 240., 270., 300., 330., 360., 390.,
        420., 450., 480., 510., 540., 570., 600., 630., 660., 690.,
        720., 750., 780., 810., 840., 870., 900., 930., 960., 990.])
    # DATA SIG0 /.../ —— 60 个值按 Fortran 列主序填充 (30,2)
    _sig0_flat = (
        [0.0] * 3 +
        [4.422e-1, 3.478e-1,
         2.794e-1, 2.286e-1, 1.899e-1, 1.598e-1, 1.360e-1,
         1.169e-1, 1.013e-1, 8.845e-2, 7.776e-2, 6.877e-2,
         6.114e-2, 5.463e-2, 4.904e-2, 4.419e-2, 3.998e-2,
         3.629e-2, 3.305e-2, 3.019e-2, 2.766e-2, 2.540e-2,
         2.339e-2, 2.158e-2, 1.996e-2, 1.850e-2, 1.718e-2] +
        [0.0] * 4 +
        [1.981e-1, 1.584e-1,
         1.290e-1, 1.066e-1, 8.932e-2, 7.567e-2, 6.475e-2,
         5.589e-2, 4.862e-2, 4.259e-2, 3.754e-2, 3.329e-2,
         2.966e-2, 2.656e-2, 2.388e-2, 2.157e-2, 1.954e-2,
         1.777e-2, 1.621e-2, 1.484e-2, 1.362e-2, 1.253e-2,
         1.155e-2, 1.067e-2, 9.888e-3, 9.179e-3]
    )
    sig0 = np.zeros((31, 3))
    sig0[1:31, 1:3] = np.array(_sig0_flat).reshape((30, 2), order='F')
    f0 = np.zeros(31)
    sigs = np.zeros(31)

    index = -ib - 300
    num = 30
    # TODO(port): INDEX 只能为 1 或 2（IB=-301 或 -302），否则超出 SIG0 第二维；
    # 原代码注释亦说明 "only a few transitions are considered"。
    for i in range(1, num + 1):  # DO 10 I=1,NUM
        f0[i] = hev[i] * 2.418573e14
        sigs[i] = sig0[i, index]

    il = 1
    ir = num
    for i in range(1, num):  # DO 50 I=1,NUM-1
        if fr >= f0[i] and fr <= f0[i + 1]:
            il = i
            ir = i + 1
            break  # GO TO 60
    # 标号 60：LINEAR INTERPOLATION:
    sigm = (sigs[ir] - sigs[il]) * (fr - f0[il]) / (f0[ir] - f0[il]) + sigs[il]

    #     IF OUTSIDE WAVELENGTH RANGE SET TO FIRST(LAST) VALUE:
    if fr <= f0[1]:
        sigm = sigs[1]
    if fr >= f0[num]:
        sigm = sigs[num]

    #     IF LAST NON-ZERO SIG VALUES, NO INTERPOLATION:
    #       IF(SIGS(IR).EQ.0.) SIGM=SIGS(IL)

    reiman_v = sigm * 1.0e-18
    return reiman_v


def sbfhe1(ii, ib, fr):
    """
C     Calculates photoionization cross sections of neutral helium
C     from states with n = 1, 2, 3, 4.
C
C     The levels are either non-averaged (l,s) states, or some
C     averaged levels.
C     The program allows only two standard possibilities of
C     constructing averaged levels:
C     i)  all states within given principal quantum number n (>1) are
C         lumped together
C     ii) all siglet states for given n, and all triplet states for
C         given n are lumped together separately (there are thus two
C         explicit levels for a given n)
C
C     The cross sections are calculated using appropriate averages
C     of the Opacity Project cross sections, calculated by procedure
C     HEPHOT
C
C     Input parameters:
C      II    - index of the lower level (in the numbering of explicit
C              levels)
C      IB    - photoionization switch IBF for the given transition
C            = 10  -  means that the given transition is from an
C                     averaged level
C            = 11  -  the given transition is from non-averaged
C                     singlet state
C            = 13  -  the given transition is from non-averaged
C                     triplet state
C      FR    - frequency
    对应 synspec54.f 行 4059–4204
    """
    ni = C.NQUANT[ii]
    igi = int(C.G[ii] + 0.01)
    is_l = ib - 10  # 原变量名 IS，与 Python 关键字冲突，改名 is_l
    sbfhe1_v = 0.0
    _goto10 = False  # GO TO 10 → 打印错误信息并 STOP

    #     ----------------------------------------------------------------
    #     IB=11 or 13  - photoionization from an non-averaged (l,s) level
    #     ----------------------------------------------------------------
    if is_l == 1 or is_l == 3:
        # IL=(IGI/IS-1)/2 —— Fortran 整数除法
        il = idiv(idiv(igi, is_l) - 1, 2)
        sbfhe1_v = hephot(is_l, il, ni, fr)

    #     ----------------------------------------------------------------
    #     IS=10 - photoionization from an averaged level
    #     ----------------------------------------------------------------
    if is_l == 0:
        if ni == 2:
            # ********    photoionization from an averaged level with n=2
            if igi == 4:
                #      a) lower level is an averaged singlet state
                sbfhe1_v = (hephot(1, 0, 2, fr) + 3.0 * hephot(1, 1, 2, fr)) / 9.0
            elif igi == 12:
                #      b) lower level is an averaged triplet state
                sbfhe1_v = (hephot(3, 0, 2, fr) + 3.0 * hephot(3, 1, 2, fr)) / 9.0
            elif igi == 16:
                #      c) lower level is an average of both singlet and triplet states
                sbfhe1_v = (hephot(1, 0, 2, fr) + 3.0 * (hephot(1, 1, 2, fr) +
                            hephot(3, 0, 2, fr)) + 9.0 * hephot(3, 1, 2, fr)) / 1.6e1
            else:
                _goto10 = True  # GO TO 10

        # ********    photoionization from an averaged level with n=3
        elif ni == 3:
            if igi == 9:
                #      a) lower level is an averaged singlet state
                sbfhe1_v = (hephot(1, 0, 3, fr) + 3.0 * hephot(1, 1, 3, fr) +
                            5.0 * hephot(1, 2, 3, fr)) / 9.0
            elif igi == 27:
                #      b) lower level is an averaged triplet state
                sbfhe1_v = (hephot(3, 0, 3, fr) + 3.0 * hephot(3, 1, 3, fr) +
                            5.0 * hephot(3, 2, 3, fr)) / 9.0
            elif igi == 36:
                #      c) lower level is an average of both singlet and triplet states
                sbfhe1_v = (hephot(1, 0, 3, fr) + 3.0 * hephot(1, 1, 3, fr) +
                            5.0 * hephot(1, 2, 3, fr) +
                            3.0 * hephot(3, 0, 3, fr) + 9.0 * hephot(3, 1, 3, fr) +
                            15.0 * hephot(3, 2, 3, fr)) / 3.6e0
                # TODO(port): 原式除以 3.6D0（=3.6），疑似原代码笔误（应为 36），此处按原文直译
            else:
                _goto10 = True  # GO TO 10

        # ********    photoionization from an averaged level with n=4
        elif ni == 4:
            if igi == 16:
                #      a) lower level is an averaged singlet state
                sbfhe1_v = (hephot(1, 0, 4, fr) + 3.0 * hephot(1, 1, 4, fr) +
                            5.0 * hephot(1, 2, 4, fr) +
                            7.0 * hephot(1, 3, 4, fr)) / 1.6e1
            elif igi == 48:
                #      b) lower level is an averaged triplet state
                sbfhe1_v = (hephot(3, 0, 4, fr) + 3.0 * hephot(3, 1, 4, fr) +
                            5.0 * hephot(3, 2, 4, fr) +
                            7.0 * hephot(3, 3, 4, fr)) / 1.6e1
            elif igi == 64:
                #      c) lower level is an average of both singlet and triplet states
                sbfhe1_v = (hephot(1, 0, 4, fr) + 3.0 * hephot(1, 1, 4, fr) +
                            5.0 * hephot(1, 2, 4, fr) +
                            7.0 * hephot(1, 3, 4, fr) +
                            3.0 * hephot(3, 0, 4, fr) +
                            9.0 * hephot(3, 1, 4, fr) +
                            15.0 * hephot(3, 2, 4, fr) +
                            21.0 * hephot(3, 3, 4, fr)) / 6.4e1
            else:
                _goto10 = True  # GO TO 10
        else:
            _goto10 = True  # GO TO 10

    if not _goto10:
        return sbfhe1_v
    # 标号 10：输入不一致，打印错误并 STOP
    #  601 FORMAT(1H0/' INCONSISTENT INPUT TO PROCEDURE SBFHE1'/
    #     * ' QUANTUM NUMBER =',I3,'  STATISTICAL WEIGHT',I4,'  S=',I3)
    print()
    print(' INCONSISTENT INPUT TO PROCEDURE SBFHE1')
    print(f' QUANTUM NUMBER ={ni:3d}  STATISTICAL WEIGHT{igi:4d}  S={is_l:3d}')
    raise SystemExit  # STOP


def hephot(s, l, n, freq):
    """
C           EVALUATES HE I PHOTOIONIZATION CROSS SECTION USING SEATON
C           FERNLEY'S CUBIC FITS TO THE OPACITY PROJECT CROSS SECTIONS
C           UP TO SOME ENERGY "EFITM" IN THE RESONANCE-FREE ZONE.  BEYOND
C           THIS ENERGY LINEAR FITS TO LOG SIGMA IN LOG (E/E0) ARE USED.
C           THIS EXTRAPOLATION SHOULD BE USED UP TO THE BEGINNING OF THE
C           RESONANCE ZONE "XMAX", BUT AT PRESENT IT IS USED THROUGH IT.
C           BY CHANGING A FEW LINES THAT ARE PRESENTLY COMMENTED OUT,
C           FOR ENERGIES IN THE RESONANCE ZONE A VALUE OF 1/100 OF THE
C           THRESHOLD CROSS SECTION IS USED -- THIS IS PURELY AD HOC AND
C           ONLY A TEMPORARY MEASURE.  OBVIOUSLY ANY OTHER VALUE OR FUNCTIONAL
C           FORM CAN BE INSERTED HERE.
C
C           CALLING SEQUENCE INCLUDES:
C                S = MULTIPLICITY, EITHER 1 OR 3
C                L = ANGULAR MOMENTUM, 0, 1, OR 2;
C                    for L > 2 - hydrogenic expresion
C                FREQ = FREQUENCY
C
C           DGH JUNE 1988 JILA, slightly modified by I.H.
    对应 synspec54.f 行 4211–4374
    """
    # INTEGER S,L,SS,LL
    # DIMENSION COEF(4,53),IST(3,2),N0(3,2),
    #           FL0(53),A(53),B(53),XFITM(53)
    #      DIMENSION XMAX(53)
    # DATA IST/1,36,20,11,45,28/ —— 列主序填充 (3,2)
    ist = np.zeros((4, 3), dtype=np.int64)
    ist[1:4, 1:3] = np.array([1, 36, 20, 11, 45, 28]).reshape((3, 2), order='F')
    # DATA N0/1,2,3,2,2,3/
    n0 = np.zeros((4, 3), dtype=np.int64)
    n0[1:4, 1:3] = np.array([1, 2, 3, 2, 2, 3]).reshape((3, 2), order='F')
    # DATA FL0/.../
    fl0 = np.array([0.0,
        2.521e-01, -5.381e-01, -9.139e-01, -1.175e+00, -1.375e+00, -1.537e+00,
        -1.674e+00, -1.792e+00, -1.896e+00, -1.989e+00, -4.555e-01, -8.622e-01,
        -1.137e+00, -1.345e+00, -1.512e+00, -1.653e+00, -1.774e+00, -1.880e+00,
        -1.974e+00, -9.538e-01, -1.204e+00, -1.398e+00, -1.556e+00, -1.690e+00,
        -1.806e+00, -1.909e+00, -2.000e+00, -9.537e-01, -1.204e+00, -1.398e+00,
        -1.556e+00, -1.690e+00, -1.806e+00, -1.909e+00, -2.000e+00, -6.065e-01,
        -9.578e-01, -1.207e+00, -1.400e+00, -1.558e+00, -1.692e+00, -1.808e+00,
        -1.910e+00, -2.002e+00, -5.749e-01, -9.352e-01, -1.190e+00, -1.386e+00,
        -1.547e+00, -1.682e+00, -1.799e+00, -1.902e+00, -1.995e+00])
    # DATA XFITM/.../
    xfitm = np.array([0.0,
        3.262e-01, 6.135e-01, 9.233e-01, 8.438e-01, 1.020e+00, 1.169e+00,
        1.298e+00, 1.411e+00, 1.512e+00, 1.602e+00, 7.228e-01, 1.076e+00,
        1.206e+00, 1.404e+00, 1.481e+00, 1.464e+00, 1.581e+00, 1.685e+00,
        1.777e+00, 9.586e-01, 1.187e+00, 1.371e+00, 1.524e+00, 1.740e+00,
        1.854e+00, 1.955e+00, 2.046e+00, 9.585e-01, 1.041e+00, 1.371e+00,
        1.608e+00, 1.739e+00, 1.768e+00, 1.869e+00, 1.803e+00, 7.360e-01,
        1.041e+00, 1.272e+00, 1.457e+00, 1.611e+00, 1.741e+00, 1.855e+00,
        1.870e+00, 1.804e+00, 9.302e-01, 1.144e+00, 1.028e+00, 1.210e+00,
        1.362e+00, 1.646e+00, 1.761e+00, 1.863e+00, 1.954e+00])
    # DATA A/.../
    a = np.array([0.0,
        6.95319e-01, 1.13101e+00, 1.36313e+00, 1.51684e+00, 1.64767e+00,
        1.75643e+00, 1.84458e+00, 1.87243e+00, 1.85628e+00, 1.90889e+00,
        9.01802e-01, 1.25389e+00, 1.39033e+00, 1.55226e+00, 1.60658e+00,
        1.65930e+00, 1.68855e+00, 1.62477e+00, 1.66726e+00, 1.83599e+00,
        2.50403e+00, 3.08564e+00, 3.56545e+00, 4.25922e+00, 4.61346e+00,
        4.91417e+00, 5.19211e+00, 1.74181e+00, 2.25756e+00, 2.95625e+00,
        3.65899e+00, 4.04397e+00, 4.13410e+00, 4.43538e+00, 4.19583e+00,
        1.79027e+00, 2.23543e+00, 2.63942e+00, 3.02461e+00, 3.35018e+00,
        3.62067e+00, 3.85218e+00, 3.76689e+00, 3.49318e+00, 1.16294e+00,
        1.86467e+00, 2.02110e+00, 2.24231e+00, 2.44240e+00, 2.76594e+00,
        2.93230e+00, 3.08109e+00, 3.21069e+00])
    # DATA B/.../
    b = np.array([0.0,
        -1.29000e+00, -2.15771e+00, -2.13263e+00, -2.10272e+00, -2.10861e+00,
        -2.11507e+00, -2.11710e+00, -2.08531e+00, -2.03296e+00, -2.03441e+00,
        -1.85905e+00, -2.04057e+00, -2.02189e+00, -2.05930e+00, -2.03403e+00,
        -2.02071e+00, -1.99956e+00, -1.92851e+00, -1.92905e+00, -4.58608e+00,
        -4.40022e+00, -4.39154e+00, -4.39676e+00, -4.57631e+00, -4.57120e+00,
        -4.56188e+00, -4.55915e+00, -4.41218e+00, -4.12940e+00, -4.24401e+00,
        -4.40783e+00, -4.39930e+00, -4.25981e+00, -4.26804e+00, -4.00419e+00,
        -4.47251e+00, -3.87960e+00, -3.71668e+00, -3.68461e+00, -3.67173e+00,
        -3.65991e+00, -3.64968e+00, -3.48666e+00, -3.23985e+00, -2.95758e+00,
        -3.07110e+00, -2.87157e+00, -2.83137e+00, -2.82132e+00, -2.91084e+00,
        -2.91159e+00, -2.91336e+00, -2.91296e+00])
    # DATA ((COEF(I,J),I=1,4),J=1,53)/.../ —— 212 个值按列主序填充 (4,53)
    _coef_flat = [
        # J=1..10
        8.734e-01, -1.545e+00, -1.093e+00, 5.918e-01, 9.771e-01, -1.567e+00,
        -4.739e-01, -1.302e-01, 1.174e+00, -1.638e+00, -2.831e-01, -3.281e-02,
        1.324e+00, -1.692e+00, -2.916e-01, 9.027e-02, 1.445e+00, -1.761e+00,
        -1.902e-01, 4.401e-02, 1.546e+00, -1.817e+00, -1.278e-01, 2.293e-02,
        1.635e+00, -1.864e+00, -8.252e-02, 9.854e-03, 1.712e+00, -1.903e+00,
        -5.206e-02, 2.892e-03, 1.782e+00, -1.936e+00, -2.952e-02, -1.405e-03,
        1.845e+00, -1.964e+00, -1.152e-02, -4.487e-03,
        # J=11..19
        7.377e-01, -9.327e-01, -1.466e+00, 6.891e-01, 9.031e-01, -1.157e+00,
        -7.151e-01, 1.832e-01, 1.031e+00, -1.313e+00, -4.517e-01, 9.207e-02,
        1.135e+00, -1.441e+00, -2.724e-01, 3.105e-02, 1.225e+00, -1.536e+00,
        -1.725e-01, 7.191e-03, 1.302e+00, -1.602e+00, -1.300e-01, 7.345e-03,
        1.372e+00, -1.664e+00, -8.204e-02, -1.643e-03, 1.434e+00, -1.715e+00,
        -4.646e-02, -7.456e-03, 1.491e+00, -1.760e+00, -1.838e-02, -1.152e-02,
        # J=20..27
        1.258e+00, -3.442e+00, -4.731e-01, -9.522e-02, 1.553e+00, -2.781e+00,
        -6.841e-01, -4.083e-03, 1.727e+00, -2.494e+00, -5.785e-01, -6.015e-02,
        1.853e+00, -2.347e+00, -4.611e-01, -9.615e-02, 1.955e+00, -2.273e+00,
        -3.457e-01, -1.245e-01, 2.041e+00, -2.226e+00, -2.669e-01, -1.344e-01,
        2.115e+00, -2.200e+00, -1.999e-01, -1.410e-01, 2.182e+00, -2.188e+00,
        -1.405e-01, -1.460e-01,
        # J=28..35
        1.267e+00, -3.417e+00, -5.038e-01, -1.797e-02, 1.565e+00, -2.781e+00,
        -6.497e-01, -5.979e-03, 1.741e+00, -2.479e+00, -6.099e-01, -2.227e-02,
        1.870e+00, -2.336e+00, -4.899e-01, -6.616e-02, 1.973e+00, -2.253e+00,
        -3.972e-01, -8.729e-02, 2.061e+00, -2.212e+00, -3.072e-01, -1.060e-01,
        2.137e+00, -2.189e+00, -2.352e-01, -1.171e-01, 2.205e+00, -2.186e+00,
        -1.621e-01, -1.296e-01,
        # J=36..44
        1.129e+00, -3.149e+00, -1.910e-01, -5.244e-01, 1.431e+00, -2.511e+00,
        -3.710e-01, -1.933e-01, 1.620e+00, -2.303e+00, -3.045e-01, -1.391e-01,
        1.763e+00, -2.235e+00, -1.829e-01, -1.491e-01, 1.879e+00, -2.215e+00,
        -9.003e-02, -1.537e-01, 1.978e+00, -2.213e+00, -2.066e-02, -1.541e-01,
        2.064e+00, -2.220e+00, 3.258e-02, -1.527e-01, 2.140e+00, -2.225e+00,
        6.311e-02, -1.455e-01, 2.208e+00, -2.229e+00, 7.977e-02, -1.357e-01,
        # J=45..53
        1.204e+00, -2.809e+00, -3.094e-01, 1.100e-01, 1.455e+00, -2.254e+00,
        -4.795e-01, 6.872e-02, 1.619e+00, -2.109e+00, -3.357e-01, -2.532e-02,
        1.747e+00, -2.065e+00, -2.317e-01, -5.224e-02, 1.853e+00, -2.058e+00,
        -1.517e-01, -6.647e-02, 1.943e+00, -2.055e+00, -1.158e-01, -6.081e-02,
        2.023e+00, -2.070e+00, -6.470e-02, -6.800e-02, 2.095e+00, -2.088e+00,
        -2.357e-02, -7.250e-02, 2.160e+00, -2.107e+00, 1.065e-02, -7.542e-02,
    ]
    coef = np.zeros((5, 54))
    coef[1:5, 1:54] = np.array(_coef_flat).reshape((4, 53), order='F')

    if l > 2:
        # GO TO 20 —— Hydrogenic expression for L > 2
        #      [multiplied by relative population of state (s,l,n), ie.
        #       by  stat.weight(s,l)/stat.weight(n)]
        gn = 2.0 * n * n
        return 2.815e29 / freq / freq / freq / n**5 * (2 * l + 1) * s / gn

    #          SELECT BEGINNING AND END OF COEFFICIENTS
    # SS=(S+1)/2 —— Fortran 整数除法
    ss = idiv(s + 1, 2)
    ll = l + 1
    nsl0 = n0[ll, ss]
    i = ist[ll, ss] + n - nsl0

    #          EVALUATE CROSS SECTION
    fl = math.log10(freq / 3.28805e15)
    x = fl - fl0[i]
    hephot_v = 0.0
    if x >= -0.001:
        if x < xfitm[i]:
            p = coef[4, i]
            for k in range(1, 4):  # DO 10 K=1,3
                p = x * p + coef[4 - k, i]
            hephot_v = 1.0e-18 * 1.0e1**p
        else:
            #           OTHERWISE REMOVE INSTRUCTION AND 3 FOLLOWING "C"
            #         ELSE IF(X.LT.XMAX(I)) THEN
            hephot_v = 1.0e-18 * 1.0e1**(a[i] + b[i] * x)
            #         ELSE
            #           HEPHOT=1.D-18*1.D1**(COEF(1,I)-2.0D0)
    else:
        hephot_v = 0.0
    return hephot_v


def topbas(freq, freq0, typlv):
    """
C     Procedure calculates the photo-ionisation cross section SIGMA in
C     [cm^2] at frequency FREQ. FREQ0 is the threshold frequency from
C     level I of ion KI. Threshold cross-sections will be of the order
C     of the numerical value of 10^-18.
C     Opacity-Project (OP) interpolation fit formula
    对应 synspec54.f 行 4381–4429
    """
    # PARAMETER (E10=2.3025851)
    E10 = 2.3025851
    # PARAMETER (MMAXOP = 200, MOP = 15)
    MMAXOP = 200  # maximum number of levels in OP data
    MOP = 15      # maximum number of fit points per level
    # DIMENSION XFIT(MOP), SFIT(MOP) —— 局部数组，1 基索引
    xfit = np.zeros(MOP + 1)
    sfit = np.zeros(MOP + 1)

    #     Read OP data if not yet done
    topbas_v = 0.0
    if not C.LOPREA:
        opdata()
    x = math.log10(freq / freq0)
    for iop in range(1, C.NTOTOP + 1):
        if feq(C.IDLVOP[iop], typlv):
            #           level has been detected in OP-data file
            if C.NOP[iop] <= 0:
                # GO TO 20 —— Level is not found ,or no data for this level, in RBF.DAT
                #  100 FORMAT ('SIGMA.......: OP DATA NOT AVAILABLE FOR LEVEL ',A10)
                write_line(61, f'SIGMA.......: OP DATA NOT AVAILABLE FOR LEVEL {typlv:<10s}')
                return topbas_v
            for ifit in range(1, C.NOP[iop] + 1):
                xfit[ifit] = C.XOP[ifit, iop]
                sfit[ifit] = C.SOP[ifit, iop]
            sigm = ylintp(x, xfit, sfit, C.NOP[iop], MOP)
            sigm = 1.0e-18 * math.exp(E10 * sigm)
            topbas_v = sigm
            break  # GO TO 10 → RETURN
    # 标号 10
    return topbas_v


def opdata():
    """
C     Procedure reads photo-ionization cross sections fit coefficients
C     based on Opacity-Project (OP) data from file RBF.DAT
C     Data, as stored, requires linear interpolation.
C
C     Meaning of global variables:
C        NTOTOP    = total number of levels in Opacity Project data
C        IDLVOP() = level identifyer of current level
C        NOP()     = number of fit points for current level
C        XOP(,)    = x     = alog10(nu/nu0)       of fit point
C        SOP(,)    = sigma = alog10(sigma/10^-18) of fit point
    对应 synspec54.f 行 4435–4499
    """
    # CHARACTER*4 IONID
    open_unit(40, 'RBF.DAT', mode='r')  # OPEN (UNIT=40,FILE='RBF.DAT',STATUS='OLD')
    #     Skip header
    for iread in range(1, 22):  # DO IREAD = 1, 21
        read_line(40)  # READ (40,*)
    iop = 0
    #         = initialize sequential level index op Opacity Project data
    #     Read number of elements in file
    # TODO(port): 自由格式(list-directed) READ 按空白/逗号分隔解析；
    # 若 RBF.DAT 的能级标识符内含空格需另行处理。
    neop = int(read_line(40).split()[0])  # READ (40,*) NEOP
    for ieop in range(1, neop + 1):
        #        Skip element name header
        for iread in range(1, 4):  # DO IREAD = 1, 3
            read_line(40)  # READ (40,*)
        #        Read number of ionization stages of current element in  file
        niop = int(read_line(40).split()[0])  # READ (40,*) NIOP
        for iiop in range(1, niop + 1):
            #           Read ion identifyer, atomic & electron number, # of levels
            #           for current ion
            _tok = read_line(40).split()  # READ (40,*) IONID, IATOM_OP, IELEC_OP, NLEVEL_OP
            ionid = _tok[0]
            iatom_op = int(_tok[1])
            ielec_op = int(_tok[2])
            nlevel_op = int(_tok[3])
            for ilop in range(1, nlevel_op + 1):
                #              Increase sequential level index of Opacity Project data
                iop = iop + 1
                #              Read level identifyer and number of sigma fit points
                _tok = read_line(40).split()  # READ (40,*) IDLVOP(IOP), NOP(IOP)
                C.IDLVOP[iop] = _tok[0]
                C.NOP[iop] = int(_tok[1])
                #              Read normalized log10 frequency and log10 cross section values
                for is_l in range(1, C.NOP[iop] + 1):  # DO IS = 1, NOP(IOP)；IS 与关键字冲突改名 is_l
                    _tok = read_line(40).split()  # READ (40,*) INDEX, XOP(IS,IOP), SOP(IS,IOP)
                    index = int(_tok[0])
                    C.XOP[is_l, iop] = float(_tok[1])
                    C.SOP[is_l, iop] = float(_tok[2])
    C.NTOTOP = iop
    #             = total number of levels in Opacity Project data
    C.LOPREA = True
    #             = set flag as data has been read in
    return


def ylintp(xint, x, y, n, ntot):
    """
C     linear interpolation routine. Determines YINT = Y(XINT) from
C     grid Y(X) with N points and dimension NTOT.
    对应 synspec54.f 行 4506–4534
    """
    #     bisection (see Numerical Recipes par 3.4 page 90)
    jl = 0
    ju = n + 1
    # 标号 10 + GO TO 10 → while 循环
    while ju - jl > 1:
        jm = idiv(ju + jl, 2)  # Fortran 整数除法
        if (x[n] > x[1]) == (xint > x[jm]):  # .EQV.
            jl = jm
        else:
            ju = jm
    j = jl
    if j == n:
        j = j - 1
    if j == 0:
        j = j + 1
    rc = (y[j + 1] - y[j]) / (x[j + 1] - x[j])
    ylintp_v = rc * (xint - x[j]) + y[j]
    return ylintp_v
