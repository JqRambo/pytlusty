# -*- coding: utf-8 -*-
# chunk07: synspec54.f 第 6877–8073 行的逐行直译
# 包含: HYDINI, HYDTAB, INTHYD, YINT, HE1INI, WTOT, EXTPRF, PHE1,
#       HE2INI, INTHE2, DIVHE2, PHE2, ISPEC, HESET

# DATA INIT /0/，之后被修改为 1（Fortran 隐含 SAVE）→ 提升为模块级变量
_save_hydini_init = 0


def hydini():
    """Initializes necessary arrays for evaluating hydrogen line profiles
    from the Lemke, Tremblay-Bergeron, or Schoening-Butler tables

    对应 synspec54.f 行 6877–7067
    """
    global _save_hydini_init
    # DIMENSION IILW(100),IIUP(100)
    iilw = np.zeros(101, dtype=np.int64)
    iiup = np.zeros(101, dtype=np.int64)
    # CHARACTER*1 CHAR
    # DATA INIT /0/  → 模块级 _save_hydini_init
    iline = 0  # TODO(port): Lemke 分支首次执行时 Fortran 中 ILINE 未初始化
               # （依赖静态存储残值，实际为 0）；这里显式初始化为 0
    ilne = 0   # 同上，NLIHYD=ILNE 依赖其残值

    if _save_hydini_init == 0:
        for i in range(1, 5):
            for j in range(i + 1, 23):
                # TODO(port): IZZ/XK/WL0/FIJ/FIJ0 在调用前未初始化
                # （Fortran 中为未定义值，实际静态存储为 0）
                izz = 0
                wl0 = 0.0
                fij = 0.0
                fij0 = 0.0
                # STARK0 给标量哑元 XKIJ,WL0,FIJ,FIJ0 赋值 → 全部解包接收
                # （XK 即 COMMON /AUXHYD/ 的 C.XK）
                i, j, izz, C.XK, wl0, fij, fij0 = \
                    stark0(i, j, izz, C.XK, wl0, fij, fij0)
                C.WLINE[i, j] = wl0
                # OSCH(I,J)=FIJ+FIJ0  （原代码中已注释掉）
        _save_hydini_init = 1
    for i in range(1, 5):
        for j in range(1, 23):
            C.ILIN0[i, j] = 0

    # --------------------------------------------
    #     Schoening-Butler tables - for IHYDPR < 0
    # --------------------------------------------
    if C.IHYDPR < 0:
        C.IHYDPR = 67
        C.ILEMKE = 0
        nline = 12
        # OPEN(UNIT=IHYDPR,FILE='./data/hydprf.dat',STATUS='OLD')
        open_unit(C.IHYDPR, './data/hydprf.dat', 'r')
        print(' reading Schoening-Butler tables')

        for i in range(1, 13):
            read_line(C.IHYDPR)  # READ(IHYDPR,500)  500 FORMAT(1X)
        # DO 100 ILINE=1,NLINE
        for iline in range(1, nline + 1):
            # read the tables, which have to be stored in file
            # unit IHYDPR (which is the input parameter in the progarm)
            # READ(IHYDPR,501) I,J
            # 501 FORMAT(12X,I1,9X,I1)
            _l = read_line(C.IHYDPR)
            i = int(_l[12:13])   # 12X,I1
            j = int(_l[22:23])   # 9X,I1
            if iline == 12:
                j = 10
            wl0 = C.WLINE[i, j]
            C.ILIN0[i, j] = iline
            # READ(IHYDPR,*) CHAR,NWL,(WL(I,ILINE),I=1,NWL)
            # 自由格式读，值可跨多条记录（按 token 累计，记录剩余部分丢弃）
            _tok = read_line(C.IHYDPR).split()
            char = _tok[0].strip("'\"")  # CHARACTER*1，数据中带引号
            nwl = int(_tok[1])
            while len(_tok) < 2 + nwl:
                _tok.extend(read_line(C.IHYDPR).split())
            for i in range(1, nwl + 1):
                C.WL[i, iline] = float(_tok[1 + i])
            # READ(IHYDPR,*) CHAR,NT,(XT(I,ILINE),I=1,NT)
            _tok = read_line(C.IHYDPR).split()
            char = _tok[0].strip("'\"")
            nt = int(_tok[1])
            while len(_tok) < 2 + nt:
                _tok.extend(read_line(C.IHYDPR).split())
            for i in range(1, nt + 1):
                C.XT[i, iline] = float(_tok[1 + i])
            # READ(IHYDPR,*) CHAR,NE,(XNE(I,ILINE),I=1,NE)
            _tok = read_line(C.IHYDPR).split()
            char = _tok[0].strip("'\"")
            ne = int(_tok[1])
            while len(_tok) < 2 + ne:
                _tok.extend(read_line(C.IHYDPR).split())
            for i in range(1, ne + 1):
                C.XNE[i, iline] = float(_tok[1 + i])
            read_line(C.IHYDPR)  # READ(IHYDPR,500)
            C.NWLH[iline] = nwl
            C.NWLHYD[iline] = nwl
            C.NTH[iline] = nt
            C.NEH[iline] = ne

            for i in range(1, nwl + 1):
                if C.WL[i, iline] < 1.0e-4:
                    C.WL[i, iline] = 1.0e-4
                C.WLHYD[iline, i] = math.log10(C.WL[i, iline])

            for ie in range(1, ne + 1):
                for it in range(1, nt + 1):
                    read_line(C.IHYDPR)  # READ(IHYDPR,500)
                    # READ(IHYDPR,*) (PRF(IWL,IT,IE,ILINE),IWL=1,NWL)
                    _tok = read_line(C.IHYDPR).split()
                    while len(_tok) < nwl:
                        _tok.extend(read_line(C.IHYDPR).split())
                    for iwl in range(1, nwl + 1):
                        C.PRF[iwl, it, ie, iline] = float(_tok[iwl - 1])

            # coefficient for the asymptotic profile is determined from
            # the input data
            xclog = C.PRF[nwl, 1, 1, iline] \
                + 2.5 * math.log10(C.WL[nwl, iline]) + 31.5304 \
                - C.XNE[1, iline] - 2.0 * math.log10(wl0)
            xklog = 0.6666667 * (xclog - 0.176)
            C.XK = math.exp(xklog * 2.3025851)

            for id in range(1, C.ND + 1):
                # temperature is modified in order to account for the
                # effect of turbulent velocity on the Doppler width
                t = C.TEMP[id] + 6.06e-9 * C.VTURB[id]
                ane = C.ELEC[id]
                tl = math.log10(t)
                anel = math.log10(ane)
                f00 = 1.25e-9 * ane ** 0.666666667
                C.FXK = f00 * C.XK
                dop = 1.0e8 / wl0 * math.sqrt(1.65e8 * t)
                C.DBETA = wl0 * wl0 / 2.997925e18 / C.FXK
                C.BETAD = C.DBETA * dop

                # interpolation to the actual values of temperature and
                # electron density. The result is stored at array PRFHYD,
                # having indices
                # ILINE (line number: 1 for L-alpha,..., 4 for H-delta, etc.);
                #                       5 for H-alpha,..., 8 for H-delta, etc.)
                # ID - depth index
                # IWL - wavelength index
                for iwl in range(1, nwl + 1):
                    # INTHYD 给标量哑元 W0 赋值 → 全部解包接收
                    prof = 0.0  # Fortran 中 PROF 未初始化；INTHYD 总会对其赋值
                    prof, tl, anel, iwl, iline = \
                        inthyd(prof, tl, anel, iwl, iline)
                    C.PRFHYD[iline, id, iwl] = prof
        # 100 CONTINUE
        close_unit(C.IHYDPR)  # CLOSE(IHYDPR)

        #  500 FORMAT(1X)
        #  501 FORMAT(12X,I1,9X,I1)

        C.IHYDPR = -C.IHYDPR
        return

    # ---------------------------------
    #     read Lemke or Tremblay tables
    # ---------------------------------
    if C.IHYDPR < 20:
        C.IHYDPR = C.IHYDPR + 20
    if C.IHYDPR == 21:
        open_unit(C.IHYDPR, './data/lemke.dat', 'r')
        #  641 format(' -----------'/
        #     *       ' reading Lemke tables; ihydpr =',i3,/
        #     *       ' -----------')
        print(' -----------')
        print(' reading Lemke tables; ihydpr =%3d' % C.IHYDPR)
        print(' -----------')
    elif C.IHYDPR == 22:
        open_unit(C.IHYDPR, './data/tremblay.dat', 'r')
        #  642 format(' -----------'/
        #     *       ' reading Tremblay tables; ihydpr =',i3,/
        #     *       ' -----------')
        print(' -----------')
        print(' reading Tremblay tables; ihydpr =%3d' % C.IHYDPR)
        print(' -----------')

    C.ILEMKE = 1
    # READ(IHYDPR,*) NTAB
    _tok = read_line(C.IHYDPR).split()
    while not _tok:
        _tok = read_line(C.IHYDPR).split()
    ntab = int(_tok[0])
    #  611 format(' ntab',i4)
    print(' ntab%4d' % ntab)
    for itab in range(1, ntab + 1):
        ilineb = iline
        # READ(IHYDPR,*) NLLY
        _tok = read_line(C.IHYDPR).split()
        nlly = int(_tok[0])
        for ili in range(1, nlly + 1):
            iline = iline + 1
            # READ(IHYDPR,*) I,J,ALMIN,ANEMIN,TMIN,DLA,DLE,DLT,NWL,NE,NT
            # 自由格式，11 个值可跨多条记录
            _tok = read_line(C.IHYDPR).split()
            while len(_tok) < 11:
                _tok.extend(read_line(C.IHYDPR).split())
            i = int(_tok[0])
            j = int(_tok[1])
            almin = float(_tok[2])
            anemin = float(_tok[3])
            tmin = float(_tok[4])
            dla = float(_tok[5])
            dle = float(_tok[6])
            dlt = float(_tok[7])
            nwl = int(_tok[8])
            ne = int(_tok[9])
            nt = int(_tok[10])
            wl0 = C.WLINE[i, j]
            C.ILIN0[i, j] = iline
            C.NWLH[iline] = nwl
            C.NWLHYD[iline] = nwl
            C.NTH[iline] = nt
            C.NEH[iline] = ne
            iilw[iline] = i
            iiup[iline] = j
            for iwl in range(1, nwl + 1):
                C.WL[iwl, iline] = almin + (iwl - 1) * dla
                C.WLHYD[iline, iwl] = C.WL[iwl, iline]
                C.WL[iwl, iline] = math.exp(2.3025851 * C.WL[iwl, iline])
            for ine in range(1, ne + 1):
                C.XNE[ine, iline] = anemin + (ine - 1) * dle
            for it in range(1, nt + 1):
                C.XT[it, iline] = tmin + (it - 1) * dlt

        for ili in range(1, nlly + 1):
            ilne = ilineb + ili
            nwl = C.NWLH[ilne]
            read_line(C.IHYDPR)  # READ(IHYDPR,500)
            for ine in range(1, C.NEH[ilne] + 1):
                for it in range(1, C.NTH[ilne] + 1):
                    # READ(IHYDPR,*) QLT,(PRF(IWL,IT,INE,ILNE),IWL=1,NWL)
                    _tok = read_line(C.IHYDPR).split()
                    while len(_tok) < 1 + nwl:
                        _tok.extend(read_line(C.IHYDPR).split())
                    qlt = float(_tok[0])  # QLT 读出后未再使用
                    for iwl in range(1, nwl + 1):
                        C.PRF[iwl, it, ine, ilne] = float(_tok[iwl])

            i = iilw[ilne]
            j = iiup[ilne]
            for id in range(1, C.ND + 1):
                hydtab(i, j, id)  # HYDTAB 不修改标量哑元
    C.NLIHYD = ilne
    close_unit(C.IHYDPR)  # CLOSE(IHYDPR)

    return


def hydtab(i, j, id):
    """interpolated hydrogen line broadening table for line I->J and
    for parameters (TEMP, ELEC) at depth ID

    对应 synspec54.f 行 7074–7121
    """
    iline = C.ILIN0[i, j]
    if iline == 0:
        return
    wl0 = C.WLINE[i, j]
    nwl = C.NWLH[iline]

    # coefficient for the asymptotic profile is determined from
    # the input data
    if id == 1:
        xclog = C.PRF[nwl, 1, 1, iline] + 2.5 * C.WLHYD[iline, nwl] - 0.477121
        xklog = 0.6666667 * xclog
        C.XK = math.exp(xklog * 2.3025851)

    # temperature is modified in order to account for the
    # effect of turbulent velocity on the Doppler width
    t = C.TEMP[id] + 6.06e-9 * C.VTURB[id]
    ane = C.ELEC[id]
    tl = math.log10(t)
    anel = math.log10(ane)
    f00 = 1.25e-9 * ane ** 0.666666667
    C.FXK = f00 * C.XK
    dop = 1.0e8 / wl0 * math.sqrt(1.65e8 * t)
    C.DBETA = wl0 * wl0 / 2.997925e18 / C.FXK
    C.BETAD = C.DBETA * dop

    # interpolation to the actual values of temperature and electron
    # density. The result is stored at array PRFHYD, having indices
    #   ILINE - line number
    #   ID    - depth index
    #   IWL   - wavelength index
    for iwl in range(1, nwl + 1):
        # INTHYD 给标量哑元 W0 赋值 → 全部解包接收
        prof = 0.0  # Fortran 中 PROF 未初始化；INTHYD 总会对其赋值
        prof, tl, anel, iwl, iline = inthyd(prof, tl, anel, iwl, iline)
        C.PRFHYD[iline, id, iwl] = prof

    return


def inthyd(w0, x0, z0, iwl, iline):
    """Interpolation in temperature and electron density from the
    hydrogen odening tables to the actual valus of
    temperature and electron density

    对应 synspec54.f 行 7125–7216
    """
    # PARAMETER (TWO=2.)
    two = 2.0
    # DIMENSION ZZ(3),XX(3),WX(3),WZ(3)
    zz = np.zeros(4)
    xx = np.zeros(4)
    wx = np.zeros(4)
    wz = np.zeros(4)

    nx = 3
    nz = 3
    nt = C.NTH[iline]
    ne = C.NEH[iline]
    beta = C.WL[iwl, iline] / C.FXK
    if C.ILEMKE == 1:
        beta = C.WL[iwl, iline] / C.XK
        nx = 2
        nz = 2

    _goto500 = False

    # for values lower than the lowest grid value of electron density
    # the profiles are determined by the approximate expression
    # (see STARKA); not by an extrapolation in the HYD tables which may
    # be very inaccurate
    if z0 < C.XNE[1, iline] * 0.99 or z0 > C.XNE[ne, iline] * 1.01:
        # DIVSTR 给标量哑元 A,DIV 赋值 → 全部解包接收
        # TODO(port): A,DIV 传入前未初始化（Fortran 未定义值，实际为 0）
        a, div = divstr(0.0, 0.0)
        w0 = starka(beta, a, div, two) * C.DBETA
        w0 = math.log10(w0)
        _goto500 = True  # GO TO 500

    # Otherwise, one interpolates (or extrapolates for higher than the
    # highes grid value of electron density) in the HYD tables
    if not _goto500:
        ipz = ne - 1  # 循环正常结束时 IPZ 保留最后一次迭代值
        for izz in range(1, ne):  # DO IZZ=1,NE-1
            ipz = izz
            if z0 <= C.XNE[izz + 1, iline]:
                break  # GO TO 20
        # 标号 20
        n0z = ipz - idiv(nz, 2) + 1  # Fortran 整数除法 NZ/2
        if n0z < 1:
            n0z = 1
        if n0z > ne - nz + 1:
            n0z = ne - nz + 1
        n1z = n0z + nz - 1

        for izz in range(n0z, n1z + 1):  # DO 300 IZZ=N0Z,N1Z
            i0z = izz - n0z + 1
            zz[i0z] = C.XNE[izz, iline]

            # Likewise, the approximate expression instead of extrapolation
            # is used for higher that the highest grid value of temperature,
            # if the Doppler width expressed in beta units (BETAD) is
            # sufficiently large (> 10)
            if x0 > 1.01 * C.XT[nt, iline] and C.BETAD > 10.0:
                a, div = divstr(0.0, 0.0)
                w0 = starka(beta, a, div, two) * C.DBETA
                w0 = math.log10(w0)
                _goto500 = True
                break  # GO TO 500

            # Otherwise, normal inter- or extrapolation
            #
            # Both interpolations (in T as well as in electron density) are
            # by default the quadratic interpolations in logarithms
            ipx = nt - 1  # 循环正常结束时 IPX 保留最后一次迭代值
            for ix in range(1, nt):  # DO IX=1,NT-1
                ipx = ix
                if x0 <= C.XT[ix + 1, iline]:
                    break  # GO TO 40
            # 标号 40
            n0x = ipx - idiv(nx, 2) + 1  # Fortran 整数除法 NX/2
            if n0x < 1:
                n0x = 1
            if n0x > nt - nx + 1:
                n0x = nt - nx + 1
            n1x = n0x + nx - 1
            for ix in range(n0x, n1x + 1):
                i0 = ix - n0x + 1
                xx[i0] = C.XT[ix, iline]
                wx[i0] = C.PRF[iwl, ix, izz, iline]
            # TODO(port): NX=2(LEMKE) 时 WX(3) 从未赋值，Fortran 中为
            # 未定义残值；这里为 0.0
            if wx[1] < -99.0 or wx[2] < -99.0 or wx[3] < -99.0:
                a, div = divstr(0.0, 0.0)
                w0 = starka(beta, a, div, two) * C.DBETA
                w0 = math.log10(w0)
                _goto500 = True
                break  # GO TO 500
            else:
                wz[i0z] = yint(xx, wx, x0)
        # 300 CONTINUE
        if not _goto500:
            w0 = yint(zz, wz, z0)
    # 标号 500
    # 500 CONTINUE
    return w0, x0, z0, iwl, iline


def yint(xl, yl, xl0):
    """Quadratic interpolation routine

    Input:  XL - array of x
            YL - array of f(x)
            XL0 - the point x(0) to which one interpolates

    对应 synspec54.f 行 7220–7236
    """
    # DIMENSION XL(3),YL(3)
    a0 = (xl[2] - xl[1]) * (xl[3] - xl[2]) * (xl[3] - xl[1])
    a1 = (xl0 - xl[2]) * (xl0 - xl[3]) * (xl[3] - xl[2])
    a2 = (xl0 - xl[1]) * (xl[3] - xl0) * (xl[3] - xl[1])
    a3 = (xl0 - xl[1]) * (xl0 - xl[2]) * (xl[2] - xl[1])
    return (yl[1] * a1 + yl[2] * a2 + yl[3] * a3) / a0


def he1ini():
    """Initializes necessary arrays for evaluating the He I line
    absorption profiles using data calculated by Barnard, Cooper
    and Smith JQSRT 14, 1025, 1974 (for 4471)
    or Shamey, unpublished PhD thesis, 1969 (for other lines)

    This procedure is quite analogous to HYDINI for hydrogen lines

    对应 synspec54.f 行 7242–7296
    """
    # COMMON/PROHE1/PRFHE1(50,4,8,3),DLMHE1(50,8,3),XNEHE1(8),NWLAM(8,4)
    # COMMON/PRO447/PRF447(80,4,7),DLM447(80,7),XNE447(7)
    nt = 4  # DATA NT /4/

    ih = 67
    # OPEN(UNIT=IH,FILE='./data/he1prf.dat',STATUS='OLD')
    open_unit(ih, './data/he1prf.dat', 'r')

    # read the Barnard, Cooper, Smith tables for He I 4471 line,
    # which have to be stored in file unit IH
    ne = 7
    for ie in range(1, ne + 1):
        # READ(IH,501) IL,WL0,IE1,XXNE,NWL
        #  501 FORMAT(/9X,I2,7X,F10.3,13X,I2,6X,E8.1,7X,I3/)
        read_line(ih)            # 开头的 '/'：跳过一条记录
        _l = read_line(ih)
        il = int(_l[9:11])       # 9X,I2
        wl0 = float(_l[18:28])   # 7X,F10.3
        ie1 = int(_l[41:43])     # 13X,I2
        xxne = float(_l[49:57])  # 6X,E8.1
        nwl = int(_l[64:67])     # 7X,I3
        read_line(ih)            # 末尾的 '/'：跳过一条记录
        C.NWLAM[ie, 1] = nwl
        C.XNE447[ie] = math.log10(xxne)
        for i in range(1, nwl + 1):
            # READ(IH,502) DLM447(I,IE),(PRF447(I,IT,IE),IT=1,NT)
            #  502 FORMAT(5E10.2)
            _l = read_line(ih)
            C.DLM447[i, ie] = float(_l[0:10])
            for it in range(1, nt + 1):
                C.PRF447[i, it, ie] = float(_l[10 * it:10 * it + 10])

    # read Shamey's tables for He I 4387, 4026, and 4922 lines
    # which have to be stored in file unit IH
    ne = 8
    for iln in range(1, 4):
        for ie in range(1, ne + 1):
            # READ(IH,501) IL,WL0,IE1,XXNE,NWL
            read_line(ih)            # '/'
            _l = read_line(ih)
            il = int(_l[9:11])
            wl0 = float(_l[18:28])
            ie1 = int(_l[41:43])
            xxne = float(_l[49:57])
            nwl = int(_l[64:67])
            read_line(ih)            # 末尾 '/'
            C.NWLAM[ie, iln + 1] = nwl
            C.XNEHE1[ie] = math.log10(xxne)
            for i in range(1, nwl + 1):
                # READ(IH,*) DLMHE1(I,IE,ILN),(PRFHE1(I,IT,IE,ILN),IT=1,NT)
                # 自由格式，1+NT 个值
                _tok = read_line(ih).split()
                while len(_tok) < 1 + nt:
                    _tok.extend(read_line(ih).split())
                C.DLMHE1[i, ie, iln] = float(_tok[0])
                for it in range(1, nt + 1):
                    C.PRFHE1[i, it, ie, iln] = float(_tok[it])
    close_unit(ih)  # CLOSE(IH)

    #  501 FORMAT(/9X,I2,7X,F10.3,13X,I2,6X,E8.1,7X,I3/)
    #  502 FORMAT(5E10.2)
    return


def wtot(t, ane, id, iline):
    """Evaluates the total (electron + ion) impact Stark width
    for four HeI lines
    After Griem (1974); and Barnard, Cooper, Smith (1974) JQSRT 14,
    1025 for the 4471 line

    Input: T     - temperature
           ANE   - electron density
           ID    - depth index
           ILINE - index of the line ( = 1  for 4471,
                                       = 2  for 4387,
                                       = 3  for 4026,
                                       = 4  for 4922)
    Output: WTOT - Stark width in Angstroms

    对应 synspec54.f 行 7301–7340
    """
    # DIMENSION ALPH0(4,4),W0(4,4),ALAM0(4)
    # DATA（只读，未修改）→ 函数顶部赋值；Fortran DATA 按列优先填充
    # DATA ALPH0 / 0.107, 0.119, 0.134, 0.154,
    # *            0.206, 0.235, 0.272, 0.317,
    # *            0.172, 0.193, 0.218, 0.249,
    # *            0.121, 0.136, 0.157, 0.184/
    alph0 = np.zeros((5, 5))
    alph0[1:, 1:] = np.array([
        0.107, 0.119, 0.134, 0.154,
        0.206, 0.235, 0.272, 0.317,
        0.172, 0.193, 0.218, 0.249,
        0.121, 0.136, 0.157, 0.184]).reshape((4, 4), order='F')
    # DATA W0    / 1.460, 1.269, 1.079, 0.898,
    # *            6.130, 5.150, 4.240, 3.450,
    # *            4.040, 3.490, 2.960, 2.470,
    # *            2.312, 1.963, 1.624, 1.315/
    w0 = np.zeros((5, 5))
    w0[1:, 1:] = np.array([
        1.460, 1.269, 1.079, 0.898,
        6.130, 5.150, 4.240, 3.450,
        4.040, 3.490, 2.960, 2.470,
        2.312, 1.963, 1.624, 1.315]).reshape((4, 4), order='F')
    # DATA ALAM0 / 4471.50, 4387.93, 4026.20, 4921.93/
    alam0 = np.zeros(5)
    alam0[1:] = [4471.50, 4387.93, 4026.20, 4921.93]

    i = C.JT[id]
    alpha = (C.TI0[id] * alph0[i, iline] + C.TI1[id] * alph0[i - 1, iline]
             + C.TI2[id] * alph0[i - 2, iline]) * (ane * 1.0e-13) ** 0.25
    we = (C.TI0[id] * w0[i, iline] + C.TI1[id] * w0[i - 1, iline]
          + C.TI2[id] * w0[i - 2, iline]) * ane * 1.0e-16
    f0 = 1.884e19 / alam0[iline] / alam0[iline]
    sig = (4.32e-5 * we / math.sqrt(t) * f0 / ane ** 0.3333) ** 0.3333
    return we * (1.0 + 1.36 / sig * alpha ** 0.8889)


def extprf(dlam, it, iline, anel, dlast, plast):
    """Extrapolation in wavelengths in Shamey, or Barnard, Cooper,
    Smith tables
    Special formula suggested by Cooper

    对应 synspec54.f 行 7346–7366
    """
    # DIMENSION W0(4,4)
    # DATA W0（只读，列优先填充）
    w0 = np.zeros((5, 5))
    w0[1:, 1:] = np.array([
        1.460, 1.269, 1.079, 0.898,
        6.130, 5.150, 4.240, 3.450,
        4.040, 3.490, 2.960, 2.470,
        2.312, 1.963, 1.624, 1.315]).reshape((4, 4), order='F')

    we = w0[it, iline] * math.exp(anel * 2.3025851) * 1.0e-16
    dlasta = abs(dlast)
    d52 = dlasta * dlasta * math.sqrt(dlasta)
    f = d52 * (plast - we / 3.14159 / dlast / dlast)
    return (we / 3.14159 + f / math.sqrt(abs(dlam))) / dlam / dlam


def phe1(id, freq, iline):
    """Absorption profile for four lines of He I, given by
    Barnard, Cooper, Smith (1974) JQSRT 14, 1025 for the 4471 line;
    Shamey (1969) PhD thesis, for other lines

    Input: ID    - depth index
           FREQ  - frequency
           ILINE - index of the line ( = 1  for 4471,
                                       = 2  for 4387,
                                       = 3  for 4026,
                                       = 4  for 4922)

    Output: PHE1 - profile coefficient in frequency units,
                   normalized to sqrt(pi) [not unity]

    对应 synspec54.f 行 7372–7529
    """
    nt = 4  # PARAMETER (NT=4)
    # COMMON/PROHE1/PRFHE1(50,NT,8,3),DLMHE1(50,8,3),XNEHE1(8),NWLAM(8,NT)
    # COMMON/PRO447/PRF447(80,NT,7),DLM447(80,7),XNE447(7)
    # DIMENSION WLAM0(4),XT0(NT),XX(3),WX(3),YY(2),PP(2),ZZ(3),WZ(3)
    xx = np.zeros(4)
    wx = np.zeros(4)
    yy = np.zeros(3)
    pp = np.zeros(3)
    zz = np.zeros(4)
    wz = np.zeros(4)
    # DATA WLAM0 / 4471.50, 4387.93, 4026.20, 4921.93/
    wlam0 = np.zeros(5)
    wlam0[1:] = [4471.50, 4387.93, 4026.20, 4921.93]
    # DATA XT0/ 3.699, 4.000, 4.301, 4.602/
    xt0 = np.zeros(5)
    xt0[1:] = [3.699, 4.000, 4.301, 4.602]

    # temperature is modified in order to account for the
    # effect of turbulent velocity on the Doppler width
    t = C.TEMP[id] + 2.42e-8 * C.VTURB[id]
    tl = math.log10(t)
    ane = C.ELEC[id]
    anel = math.log10(ane)
    alam = 2.997925e18 / freq
    dlam = alam - wlam0[iline]
    dopl = math.sqrt(4.125e7 * t) * wlam0[iline] / 2.997925e10

    # IF(TL.GT.XT0(NT)+0.1) GO TO 5
    # IF(ILINE.EQ.1.AND.ANEL.GE.XNE447(1)) GO TO 10
    # IF(ILINE.NE.1.AND.ANEL.GE.XNEHE1(1)) GO TO 10
    if not (tl <= xt0[nt] + 0.1
            and ((iline == 1 and anel >= C.XNE447[1])
                 or (iline != 1 and anel >= C.XNEHE1[1]))):
        # 标号 5: isolated line approximation for low electron densities
        a = wtot(t, ane, id, iline) / dopl
        v = abs(dlam) / dopl
        v1 = abs(alam - 4471.682) / dopl
        phe1 = voigtk(a, v)
        if iline == 1:
            phe1 = (8.0 * phe1 + voigtk(a, v1)) / 9.0
        return phe1

    # 标号 10: otherwise, interpolation (or extrapolation) in tables
    nx = 3
    nz = 3
    ny = 2
    ne = 8
    ilne = iline - 1
    if iline == 1:
        ne = 7

    # Interpolation in electron density
    ipz = ne - 1  # 循环正常结束时 IPZ 保留最后一次迭代值
    for jz in range(1, ne):  # DO JZ=1,NE-1
        ipz = jz
        if iline == 1 and anel <= C.XNE447[jz + 1]:
            break  # GO TO 30
        if iline != 1 and anel <= C.XNEHE1[jz + 1]:
            break  # GO TO 30
    # 标号 30
    n0z = ipz - idiv(nz, 2) + 1  # Fortran 整数除法 NZ/2
    if n0z < 1:
        n0z = 1
    if n0z > ne - nz + 1:
        n0z = ne - nz + 1
    n1z = n0z + nz - 1
    for jz in range(n0z, n1z + 1):  # DO 300 JZ=N0Z,N1Z
        i0z = jz - n0z + 1
        if iline == 1:
            zz[i0z] = C.XNE447[jz]
        if iline != 1:
            zz[i0z] = C.XNEHE1[jz]

        # Interpolation in temperature
        ipx = nt - 1  # 循环正常结束时 IPX 保留最后一次迭代值
        for ix in range(1, nt):  # DO IX=1,NT-1
            ipx = ix
            if tl <= xt0[ix + 1]:
                break  # GO TO 50
        # 标号 50
        n0x = ipx - idiv(nx, 2) + 1  # Fortran 整数除法 NX/2
        if n0x < 1:
            n0x = 1
        if n0x > nt - nx + 1:
            n0x = nt - nx + 1
        n1x = n0x + nx - 1
        for ix in range(n0x, n1x + 1):  # DO 200 IX=N0X,N1X
            i0x = ix - n0x + 1
            xx[i0x] = xt0[ix]

            # Interpolation in wavelength
            #
            # 1. For delta lambda beyond tabulated values - special
            #    extrapolation (Cooper's suggestion)
            nlst = C.NWLAM[jz, iline]
            prf0 = None  # None 表示未走 GO TO 150 的外推分支
            if iline == 1:
                d1 = C.DLM447[1, jz]
                d2 = C.DLM447[nlst, jz]
                if dlam < d1:
                    prf0 = extprf(dlam, ix, iline, zz[i0z], d1,
                                  C.PRF447[1, ix, jz])
                    # GO TO 150
                elif dlam > d2:
                    prf0 = extprf(dlam, ix, iline, zz[i0z], d2,
                                  C.PRF447[nlst, ix, jz])
                    # GO TO 150
            else:
                d1 = C.DLMHE1[1, jz, ilne]
                d2 = C.DLMHE1[nlst, jz, ilne]
                if dlam < d1:
                    prf0 = extprf(dlam, ix, iline, zz[i0z], d1,
                                  C.PRFHE1[1, ix, jz, ilne])
                    # GO TO 150
                elif dlam > d2:
                    prf0 = extprf(dlam, ix, iline, zz[i0z], d2,
                                  C.PRFHE1[nlst, ix, jz, ilne])
                    # GO TO 150

            if prf0 is None:
                # normal linear interpolation in wavelength
                # (for 4471, linear interpolation in logarithms)
                ipy = nlst - 1  # 循环正常结束时 IPY 保留最后一次迭代值
                for iy in range(1, nlst):  # DO IY=1,NLST-1
                    ipy = iy
                    if iline == 1 and dlam <= C.DLM447[iy + 1, jz]:
                        break  # GO TO 70
                    if iline != 1 and dlam <= C.DLMHE1[iy + 1, jz, ilne]:
                        break  # GO TO 70
                # 标号 70
                n0y = ipy - idiv(ny, 2) + 1  # Fortran 整数除法 NY/2
                if n0y < 1:
                    n0y = 1
                if n0y > nlst - ny + 1:
                    n0y = nlst - ny + 1
                n1y = n0y + ny - 1
                for iy in range(n0y, n1y + 1):
                    i0 = iy - n0y + 1
                    if iline == 1:
                        yy[i0] = C.DLM447[iy, jz]
                    if iline == 1:
                        pp[i0] = math.log(C.PRF447[iy, ix, jz])
                    if iline != 1:
                        yy[i0] = C.DLMHE1[iy, jz, ilne]
                    if iline != 1:
                        pp[i0] = C.PRFHE1[iy, ix, jz, ilne]
                if iline != 1:
                    wx[i0x] = (pp[2] * (dlam - yy[1])
                               + pp[1] * (yy[2] - dlam)) / (yy[2] - yy[1])
                else:
                    wx[i0x] = (pp[2] * (dlam - yy[1])
                               + pp[1] * (yy[2] - dlam)) / (yy[2] - yy[1])
                    wx[i0x] = math.exp(wx[i0x])
                # GO TO 200
            else:
                # 标号 150
                wx[i0x] = prf0
            # 200 CONTINUE
        wz[i0z] = yint(xx, wx, tl)
    # 300 CONTINUE
    w0 = yint(zz, wz, anel)
    phe1 = w0 * dopl * 1.772454
    return phe1


def he2ini():
    """Initializes necessary arrays for evaluating the He II line
    absorption profiles using data calculated by Schoening and
    Butler

    This procedure is quite analogous to HYDINI for hydrogen lines

    对应 synspec54.f 行 7535–7625
    """
    # COMMON/HE2PRF/PRFHE2(19,MDEPTH,36),WLHE2(19,36),NWLHE2(19),
    # *             ILHE2(19),IUHE2(19)
    # COMMON/HE2DAT/WL2(36,19),XT2(6),XNE2(11,19),PRF2(36,6,11),
    # *             NWL2,NT2,NE2
    nline1 = 19  # DATA NLINE1 /19/

    ih = 67
    # OPEN(UNIT=IH,FILE='./data/he2prf.dat',STATUS='OLD')
    open_unit(ih, './data/he2prf.dat', 'r')

    for iline in range(1, nline1 + 1):
        # read the Schoening and Butler tables, which have to be stored
        # in file he23prf.dat
        # READ(IH,501) ILHE2(ILINE),IUHE2(ILINE)
        #  501 FORMAT(//14X,I2,9X,I2/)
        read_line(ih)   # '/' ×1
        read_line(ih)   # '/' ×2
        _l = read_line(ih)
        C.ILHE2[iline] = int(_l[14:16])  # 14X,I2
        C.IUHE2[iline] = int(_l[25:27])  # 9X,I2
        read_line(ih)   # 末尾 '/'
        if C.ILHE2[iline] <= 2:
            wl00 = 227.838
        else:
            wl00 = 227.7776
        wl0 = wl00 / (1.0 / C.ILHE2[iline] ** 2 - 1.0 / C.IUHE2[iline] ** 2)
        # READ(IH,*) NWL2,(WL2(I,ILINE),I=1,NWL2)  自由格式，可跨记录
        _tok = read_line(ih).split()
        while not _tok:
            _tok = read_line(ih).split()
        C.NWL2 = int(_tok[0])
        while len(_tok) < 1 + C.NWL2:
            _tok.extend(read_line(ih).split())
        for i in range(1, C.NWL2 + 1):
            C.WL2[i, iline] = float(_tok[i])
        # READ(IH,503) NT2,(XT2(I),I=1,NT2)
        #  503 FORMAT(2X,I4,F10.3,5F12.3)
        # TODO(port): 若 NT2>6 会发生格式回转（新记录重新从 2X,I4 开始），
        # 这里只翻译了单记录情形（实际数据 NT2=6）
        _l = read_line(ih)
        C.NT2 = int(_l[2:6])
        C.XT2[1] = float(_l[6:16])  # F10.3
        for i in range(2, C.NT2 + 1):  # 5F12.3
            C.XT2[i] = float(_l[16 + (i - 2) * 12:28 + (i - 2) * 12])
        # READ(IH,504) NE2,(XNE2(I,ILINE),I=1,NE2)
        #  504 FORMAT(2X,I4,F10.2,5F12.2/4X,5F12.2)
        # TODO(port): 若 NE2>11 会发生格式回转，这里只翻译两条记录的情形
        # （实际数据 NE2=11）
        _l = read_line(ih)
        C.NE2 = int(_l[2:6])
        C.XNE2[1, iline] = float(_l[6:16])  # F10.2
        for i in range(2, min(C.NE2, 6) + 1):  # 5F12.2
            C.XNE2[i, iline] = float(_l[16 + (i - 2) * 12:28 + (i - 2) * 12])
        if C.NE2 > 6:
            _l = read_line(ih)  # '/' 换记录，4X,5F12.2
            for i in range(7, C.NE2 + 1):
                C.XNE2[i, iline] = float(_l[4 + (i - 7) * 12:16 + (i - 7) * 12])
        read_line(ih)  # READ(IH,500)  500 FORMAT(1X)
        C.NWLHE2[iline] = C.NWL2

        for i in range(1, C.NWL2 + 1):
            if C.WL2[i, iline] < 1.0e-4:
                C.WL2[i, iline] = 1.0e-4
            C.WLHE2[iline, i] = math.log10(C.WL2[i, iline])

        for ie in range(1, C.NE2 + 1):
            for it in range(1, C.NT2 + 1):
                read_line(ih)  # READ(IH,500)
                # READ(IH,505) (PRF2(IWL,IT,IE),IWL=1,NWL2)
                #  505 FORMAT(10F8.3)  —— 每记录 10 个定宽字段，可回转多记录
                iwl = 1
                while iwl <= C.NWL2:
                    _l = read_line(ih)
                    for _k in range(10):
                        if iwl > C.NWL2:
                            break
                        C.PRF2[iwl, it, ie] = float(_l[_k * 8:_k * 8 + 8])
                        iwl += 1

        # coefficient for the asymptotic profile is determined from
        # the input data
        xclog = C.PRF2[C.NWL2, 1, 1] \
            + 2.5 * math.log10(C.WL2[C.NWL2, iline]) + 31.831 \
            - C.XNE2[1, iline] - 2.0 * math.log10(wl0)
        xklog = 0.6666667 * (xclog - 0.176)
        C.XK = math.exp(xklog * 2.3025851)
        for id in range(1, C.ND + 1):
            t = C.TEMP[id] + 2.42e-8 * C.VTURB[id]
            ane = C.ELEC[id]
            tl = math.log10(t)
            anel = math.log10(ane)
            f00 = 1.25e-9 * ane ** 0.666666667
            C.FXK = f00 * C.XK
            dop = 1.0e8 / wl0 * math.sqrt(4.12e7 * t)
            C.DBETA = wl0 * wl0 / 2.997925e18 / C.FXK
            C.BETAD = C.DBETA * dop

            # interpolation to the actual values of temperature and electron
            # density. The result is stored at array PRFHE2, which has indices
            # ILINE  - index of line
            # ID     - depth index
            # IWL    - wavelength index (notice that the wavelength grid may
            #          generally be different for different lines
            for iwl in range(1, C.NWL2 + 1):
                # INTHE2 给标量哑元 W0 赋值 → 全部解包接收
                prof = 0.0  # Fortran 中 PROF 未初始化；INTHE2 总会对其赋值
                prof, tl, anel, iwl, iline = \
                    inthe2(prof, tl, anel, iwl, iline)
                C.PRFHE2[iline, id, iwl] = prof
    close_unit(ih)  # CLOSE(IH)

    #  500 FORMAT(1X)
    #  501 FORMAT(//14X,I2,9X,I2/)
    # c 502 FORMAT(2X,I4,1P6E10.3,4(/5X,0P6F10.4)/5X,5F10.4)
    #  503 FORMAT(2X,I4,F10.3,5F12.3)
    #  504 FORMAT(2X,I4,F10.2,5F12.2/4X,5F12.2)
    #  505 FORMAT(10F8.3)
    return


def inthe2(w0, x0, z0, iwl, iline):
    """Interpolation in temperature and electron density from the
    Schoening and Butler tables for He II lines to the actual
    actual values of temperature and electron density

    This procedure is quite analogous to INTHYD for hydrogen lines

    对应 synspec54.f 行 7631–7712
    """
    # PARAMETER (UN=1.)
    un = 1.0
    # COMMON/HE2DAT/WL2(36,19),XT2(6),XNE2(11,19),PRF2(36,6,11),NWL2,NT2,NE2
    # DIMENSION ZZ(3),XX(3),WX(3),WZ(3)
    zz = np.zeros(4)
    xx = np.zeros(4)
    wx = np.zeros(4)
    wz = np.zeros(4)

    nx = 3
    nz = 3

    # TODO(port): A,DIV 是未初始化局部量（Fortran 未定义值，实际为 0）；
    # 高温分支（GO TO 500 前）直接用 A,DIV 调 STARKA 而未先 CALL DIVHE2，
    # 与 INTHYD 不同，疑为原代码 bug，按字面直译
    a = 0.0
    div = 0.0

    _goto500 = False

    # for values lower than the lowest grid value of electron density
    # the profiles are determined by the approximate expression
    # (see STARKA); not by an extrapolation in the tables which may
    # be very inaccurate
    if z0 < C.XNE2[1, iline] * 0.99 or z0 > C.XNE2[C.NE2, iline] * 1.01:
        # DIVHE2 给标量哑元 A,DIV 赋值 → 全部解包接收
        a, div = divhe2(a, div)
        w0 = starka(C.WL2[iwl, iline] / C.FXK, a, div, un) * C.DBETA
        w0 = math.log10(w0)
        _goto500 = True  # GO TO 500

    # Otherwise, one interpolates (or extrapolates for higher than the
    # highes grid value of electron density) in the Schoening and
    # Butler tables
    if not _goto500:
        ipz = C.NE2 - 1  # 循环正常结束时 IPZ 保留最后一次迭代值
        for izz in range(1, C.NE2):  # DO 10 IZZ=1,NE2-1
            ipz = izz
            if z0 <= C.XNE2[izz + 1, iline]:
                break  # GO TO 20
        #  10 CONTINUE
        # 标号 20
        n0z = ipz - idiv(nz, 2) + 1  # Fortran 整数除法 NZ/2
        if n0z < 1:
            n0z = 1
        if n0z > C.NE2 - nz + 1:
            n0z = C.NE2 - nz + 1
        n1z = n0z + nz - 1

        for izz in range(n0z, n1z + 1):  # DO 300 IZZ=N0Z,N1Z
            i0z = izz - n0z + 1
            zz[i0z] = C.XNE2[izz, iline]

            # Likewise, the approximate expression instead of extrapolation
            # is used for higher that the highest grid value of temperature,
            # if the Doppler width expressed in beta units (BETAD) is
            # sufficiently large (> 10)
            if x0 > 1.01 * C.XT2[C.NT2] and C.BETAD > 10.0:
                w0 = starka(C.WL2[iwl, iline] / C.FXK, a, div, un) * C.DBETA
                w0 = math.log10(w0)
                _goto500 = True
                break  # GO TO 500

            # Otherwise, normal inter- or extrapolation
            #
            # Both interpolations (in T as well as in electron density) are
            # by default the quadratic interpolations in logarithms
            ipx = C.NT2 - 1  # 循环正常结束时 IPX 保留最后一次迭代值
            for ix in range(1, C.NT2):  # DO 30 IX=1,NT2-1
                ipx = ix
                if x0 <= C.XT2[ix + 1]:
                    break  # GO TO 40
            #  30 CONTINUE
            # 标号 40
            n0x = ipx - idiv(nx, 2) + 1  # Fortran 整数除法 NX/2
            if n0x < 1:
                n0x = 1
            if n0x > C.NT2 - nx + 1:
                n0x = C.NT2 - nx + 1
            n1x = n0x + nx - 1
            for ix in range(n0x, n1x + 1):  # DO 200 IX=N0X,N1X
                i0 = ix - n0x + 1
                xx[i0] = C.XT2[ix]
                wx[i0] = C.PRF2[iwl, ix, izz]
            #  200 CONTINUE
            wz[i0z] = yint(xx, wx, x0)
        # 300 CONTINUE
        if not _goto500:
            w0 = yint(zz, wz, z0)
    # 标号 500
    # 500 CONTINUE
    return w0, x0, z0, iwl, iline


def divhe2(a, div):
    """Auxiliary procedure for evaluating approximate Stark profile
    for He II lines
    This procedure is quite analogous to DIVSTR for hydrogen;
    the only difference is a somewhat different definition
    of the parameter A ,ie. A for He II is equal to A for hydrogen
    minus ln(2)

    对应 synspec54.f 行 7718–7746
    """
    # PARAMETER (UN=1.,TWO=2.,UNQ=1.25,UNH=1.5,TWH=2.5,FO=4.,FI=5.)
    un = 1.0
    two = 2.0
    unq = 1.25
    unh = 1.5
    twh = 2.5
    fo = 4.0
    fi = 5.0
    # PARAMETER (CA=0.978,BL=5.821,AL=1.26,CX=0.28,DX=0.0001)
    ca = 0.978
    bl = 5.821
    al = 1.26
    cx = 0.28
    dx = 0.0001

    a = unh * math.log(C.BETAD) - ca
    if C.BETAD < bl:
        return a, div  # IF(BETAD.LT.BL) RETURN —— DIV 保持调用方原值
    if a >= al:
        x = math.sqrt(a) * (un + unq * math.log(a) / (fo * a - fi))
    else:
        x = math.sqrt(cx + a)
    for i in range(1, 6):  # DO 10 I=1,5
        xn = x * (un - (x * x - twh * math.log(x) - a) / (two * x * x - twh))
        if abs(xn - x) <= dx:
            break  # GO TO 20（X 保持旧值）
        x = xn
    #  10 CONTINUE
    # 标号 20
    div = x
    return a, div


def phe2(ispec, id, ablin, emlin):
    """Evaluation of the opacity and emissivity in a given He II line,
    using profile coefficients calculated by Schoening and Butler.

    Input: ISPEC - line index, defined in HE2INI
           ID    - depth index
    Output: ABLIN - absorption coefficient
            EMLIN - emission coefficient

    对应 synspec54.f 行 7752–7849
    """
    # DIMENSION ABLIN(1),EMLIN(1),OSCHE2(19),PRF0(40),WLL(40)
    prf0 = np.zeros(41)
    wll = np.zeros(41)
    # COMMON/HE2PRF/...  common/lasers/lasdel
    # DATA OSCHE2/.../（只读）
    osche2 = np.zeros(20)
    osche2[1:] = [6.407e-1, 1.506e-1, 5.584e-2, 2.768e-2,
                  1.604e-2, 1.023e-2, 6.980e-3,
                  8.421e-1, 3.230e-2, 1.870e-2, 1.196e-2, 8.187e-3,
                  5.886e-3, 4.393e-3, 3.375e-3, 2.656e-3,
                  1.038, 1.793e-1, 6.549e-2]

    # ILINE - line index
    iline = ispec - 5

    for iwl in range(1, C.NWLHE2[iline] + 1):  # DO 10
        prf0[iwl] = C.PRFHE2[iline, id, iwl]
        wll[iwl] = C.WLHE2[iline, iwl]
    #  10 CONTINUE

    i = C.ILHE2[iline]
    j = C.IUHE2[iline]
    ii = i * i
    jj = j * j
    if i <= 2:
        wlin = 227.838 / (1.0 / ii - 1.0 / jj)
    else:
        wlin = 227.7776 / (1.0 / ii - 1.0 / jj)
    t = C.TEMP[id]

    # He III population (either LTE or NLTE, depending on input model)
    if C.IELHE2 > 0 and C.INLTE > 0:
        pp = C.POPUL[C.NNEXT[C.IELHE2], id]
        nlhe2 = C.NLAST[C.IELHE2] - C.NFIRST[C.IELHE2] + 1
    else:
        pp = C.RRR[id, 3, 2]
        nlhe2 = 0

    # population of the lower level of the given transition
    # (again either LTE or NLTE)
    pp = pp * C.ELEC[id] * 4.1412e-16 / t / math.sqrt(t) * ii
    if i <= nlhe2 and C.INLTE > 0:
        popi = C.POPUL[C.NFIRST[C.IELHE2] + i - 1, id]
    else:
        popi = pp * math.exp(631479.0 / t / ii)

    # population of the upper level of the given transition
    # (again either LTE or NLTE)
    if j <= nlhe2:
        popj = C.POPUL[C.NFIRST[C.IELHE2] + j - 1, id] * ii / jj
    else:
        popj = pp * math.exp(631479.0 / t / jj)

    # loop over frequency points - opacity and emissivity in the given line
    # absorption coefficent is found by interpolating in previously
    # calculated tables, based on calculations of Schoening and Butler
    # (see procedure HE2INI)
    fid = 0.02654 * osche2[iline]
    for ij in range(3, C.NFREQ + 1):  # DO 50 IJ=3,NFREQ
        al = abs(C.WLAM[ij] - wlin)
        if al < 1.0e-4:
            al = 1.0e-4
        al = math.log10(al)
        iw0 = C.NWLHE2[iline] - 1  # 循环正常结束时 IW0 保留最后一次迭代值
        for iwl in range(1, C.NWLHE2[iline]):  # DO 20 IWL=1,NWLHE2(ILINE)-1
            iw0 = iwl
            if al <= wll[iwl + 1]:
                break  # GO TO 30
        #  20 CONTINUE
        # 标号 30
        iw1 = iw0 + 1
        prh = (prf0[iw0] * (wll[iw1] - al) + prf0[iw1] * (al - wll[iw0])) \
            / (wll[iw1] - wll[iw0])
        sg = math.exp(prh * 2.3025851) * fid
        if (popi - popj) <= 0.0 and C.lasdel:
            continue  # goto 50
        ablin[ij] = ablin[ij] + sg * (popi - popj)
        emlin[ij] = emlin[ij] + sg * popj * 1.4747e-2 \
            * (C.FREQ[ij] * 1.0e-15) ** 3
    #  50 CONTINUE
    return


def ispec(iat, ion, alam):
    """Auxiliary procedure for INISET

    Input:  IAT  - atomic number
            ION  - ion (=1 for neutrals, =2 for once ionized, etc.)
            ALAM - wavelength in nanometers
    Output: ISPEC - parameter specifying whether the given line
                    is taken with a special (pretabulated) absorption
                    profile - only for hydrogen and helium
                  = 0  - profile is taken as an ordinary Voigt profile
                  > 0  - special profile

    对应 synspec54.f 行 7855–7913
    """
    ispec = 0
    if iat > 2:
        return ispec

    if iat == 1:
        ispec = 1
        return ispec
    else:
        if ion == 1:
            if abs(alam - 447.1) < 0.5 and C.IHE1PR > 0:
                ispec = 2
            if abs(alam - 438.8) < 0.2 and C.IHE1PR > 0:
                ispec = 3
            if abs(alam - 402.6) < 0.2 and C.IHE1PR > 0:
                ispec = 4
            if abs(alam - 492.2) < 0.2 and C.IHE1PR > 0:
                ispec = 5
        else:
            if alam < 163.0 or alam > 1012.7:
                return ispec
            if alam < 321.0:
                if abs(alam - 164.0) < 0.2 and C.IHE2PR > 0:
                    ispec = 6
                if abs(alam - 320.3) < 0.2 and C.IHE2PR > 0:
                    ispec = 7
                if abs(alam - 273.3) < 0.2 and C.IHE2PR > 0:
                    ispec = 8
                if abs(alam - 251.1) < 0.2 and C.IHE2PR > 0:
                    ispec = 9
                if abs(alam - 238.5) < 0.2 and C.IHE2PR > 0:
                    ispec = 10
                if abs(alam - 230.6) < 0.2 and C.IHE2PR > 0:
                    ispec = 11
                if abs(alam - 225.3) < 0.2 and C.IHE2PR > 0:
                    ispec = 12
            elif alam < 541.0:
                if alam < 392.3:
                    return ispec
                if abs(alam - 468.6) < 0.2 and C.IHE2PR > 0:
                    ispec = 13
                if abs(alam - 485.9) < 0.2 and C.IHE2PR > 0:
                    ispec = 14
                if abs(alam - 454.2) < 0.2 and C.IHE2PR > 0:
                    ispec = 15
                if abs(alam - 433.9) < 0.2 and C.IHE2PR > 0:
                    ispec = 16
                if abs(alam - 420.0) < 0.2 and C.IHE2PR > 0:
                    ispec = 17
                if abs(alam - 410.0) < 0.2 and C.IHE2PR > 0:
                    ispec = 18
                if abs(alam - 402.6) < 0.2 and C.IHE2PR > 0:
                    ispec = 19
                if abs(alam - 396.8) < 0.2 and C.IHE2PR > 0:
                    ispec = 20
                if abs(alam - 392.3) < 0.2 and C.IHE2PR > 0:
                    ispec = 21
            else:
                if abs(alam - 1012.4) < 0.2 and C.IHE2PR > 0:
                    ispec = 22
                if abs(alam - 656.0) < 0.2 and C.IHE2PR > 0:
                    ispec = 23
                if abs(alam - 541.2) < 0.2 and C.IHE2PR > 0:
                    ispec = 24
    return ispec


def heset(il, alm, excl, excu, ion, iprf0, ilwn, iupn):
    """Auxiliary procedure for INISET - set up quantities:
    IPRF0      - index for the procedure evaluating standard absorption
                 profile coefficient for He I lines - see GAMHE
    ILWN,IUPN  - only in NLTE option is switched on;
                 indices of the lower and upper level associated with
                 the given line

    Input: IL - line index
           ALM - line wavelength in nm
           EXCL - excitation potential of the lower level (in cm**-1)
           EXCU - excitation potential of the upper level (in cm**-1)
           ION  - ionisation degree (1=neutrals, 2=once ionized, etc.)

    对应 synspec54.f 行 7920–8069
    """
    # DIMENSION JU(24),NU(24),IT(24)
    # DATA（只读）
    it = np.zeros(25, dtype=np.int64)
    it[1:] = [1, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 1, 0, 1, 0,
              0, 0, 0, 0]
    nu = np.zeros(25, dtype=np.int64)
    nu[1:] = [6, 6, 9, 3, 8, 4, 7, 5, 6, 6, 5, 4, 4, 4, 3, 4, 3, 3, 5, 5,
              7, 8, 10, 2]
    ju = np.zeros(25, dtype=np.int64)
    ju[1:] = [15, 3, 5, 9, 5, 3, 5, 3, 5, 1, 1, 15, 3, 5, 3, 1, 15, 5, 15,
              5, 1, 1, 1, 9]

    # ******* He I  ***********
    if ion == 1:  # IF(ION.NE.1) GO TO 20 → else 分支即 He I 部分
        # switch IPRF0 - see GAMHE
        il1 = il  # IL1 赋值后未再使用
        alam = alm * 10.0
        iprf = 0
        if abs(alam - 3819.60) < 1.0:
            iprf = 1
        if abs(alam - 3867.50) < 1.0:
            iprf = 2
        if abs(alam - 3871.79) < 1.0:
            iprf = 3
        if abs(alam - 3888.65) < 1.0:
            iprf = 4
        if abs(alam - 3926.53) < 1.0:
            iprf = 5
        if abs(alam - 3964.73) < 1.0:
            iprf = 6
        if abs(alam - 4009.27) < 1.0:
            iprf = 7
        if abs(alam - 4120.80) < 1.0:
            iprf = 8
        if abs(alam - 4143.76) < 1.0:
            iprf = 9
        if abs(alam - 4168.97) < 1.0:
            iprf = 10
        if abs(alam - 4437.55) < 1.0:
            iprf = 11
        if abs(alam - 4471.50) < 1.0:
            iprf = 12
        if abs(alam - 4713.20) < 1.0:
            iprf = 13
        if abs(alam - 4921.93) < 1.0:
            iprf = 14
        if abs(alam - 5015.68) < 1.0:
            iprf = 15
        if abs(alam - 5047.74) < 1.0:
            iprf = 16
        if abs(alam - 5875.70) < 1.0:
            iprf = 17
        if abs(alam - 6678.15) < 1.0:
            iprf = 18
        if abs(alam - 4026.20) < 1.0:
            iprf = 19
        if abs(alam - 4387.93) < 1.0:
            iprf = 20
        if abs(alam - 4023.97) < 1.0:
            iprf = 21
        if abs(alam - 3935.91) < 1.0:
            iprf = 22
        if abs(alam - 3833.55) < 1.0:
            iprf = 23
        if abs(alam - 10830.0) < 1.0:
            iprf = 24
        if 0 < iprf <= 20:
            iprf0 = iprf

        # Indices of NLTE levels associated with the given line
        # IF(INLTE.gt.5.OR.IELHE1.EQ.0) RETURN
        # （条件成立时直接 RETURN；此处等价地用 if not 包裹后续代码——
        #  因为 ion==1 时标号 20 处的 He II 分支本来也会立即 RETURN）
        if not (C.INLTE > 5 or C.IELHE1 == 0):
            n0i = C.NFIRST[C.IELHE1]
            n1i = C.NLAST[C.IELHE1]
            hc = CL * H  # CL, H 为 params.py 常量
            eion = C.ENION[n0i] / hc
            ilw = 0
            iun = 0
            nql = 0
            if iprf > 0:
                nql = nu[iprf]
            igl = 0  # TODO(port): 若 EX 条件从未满足，Fortran 中 IGL 未定义
            for i in range(n0i, n1i + 1):  # DO 10 I=N0I,N1I
                nq = C.NQUANT[i]
                ex = eion - C.ENION[i] / hc
                if abs(excl - ex) < 100.0:
                    ilw = i
                    igl = int(C.G[i] + 0.001)  # INT 截断取整
                if nq == nql:
                    ig = int(C.G[i] + 0.001)
                    # TODO(port): IPRF=0 时 Fortran 读 IT(0)（越界残值）；
                    # 这里 it[0]=0 走 EQ.0 分支
                    if it[iprf] == 0:
                        if nq == 2 and ig == ju[iprf]:
                            iun = i
                        if nq == 3:
                            if ig == ju[iprf]:
                                if ig == 1 or ig == 5:
                                    iun = i
                                if ig == 3 and igl == 1:
                                    iun = i
                            else:
                                if ig == 9:
                                    iun = i
                        if nq == 4:
                            if ig == ju[iprf]:
                                if ig == 1 or ig == 5 or ig == 7:
                                    iun = i
                                if ig == 3 and igl == 1:
                                    iun = i
                            else:
                                if ig == 16:
                                    iun = i
                        if ig == 25 or ig == 36:
                            iun = i
                        if ig == 49 or ig == 64 or ig == 81:
                            iun = i
                        if ig == 100 or ig == 121 or ig == 144:
                            iun = i
                    else:
                        if nq == 3:
                            if ig == ju[iprf]:
                                if ig == 9 or ig == 15:
                                    iun = i
                                if ig == 3 and igl == 9:
                                    iun = i
                            else:
                                if ig == 27:
                                    iun = i
                        if nq == 4:
                            if ig == ju[iprf]:
                                if ig == 9 or ig == 15 or ig == 21:
                                    iun = i
                                if ig == 3 and igl == 9:
                                    iun = i
                            else:
                                if ig == 48:
                                    iun = i
                        if ig == 75:
                            iun = i
                        if ig == 108 or ig == 147 or ig == 192:
                            iun = i
                        if ig == 243 or ig == 300 or ig == 363:
                            iun = i
                    if nq == 2 and ig == 16:
                        iun = i
                    if nq == 3 and ig == 36:
                        iun = i
                    if nq == 4 and ig == 64:
                        iun = i
                    if nq == 5 and ig == 100:
                        iun = i
                    if nq == 6 and ig == 144:
                        iun = i
                    if nq == 7 and ig == 196:
                        iun = i
                    if nq == 8 and ig == 256:
                        iun = i
                    if nq == 9 and ig == 324:
                        iun = i
                    if nq == 10 and ig == 400:
                        iun = i
            #  10 CONTINUE
            # print *, 'il,iprof,ilw,iupn',il,iprf,ilw,iun （原代码中已注释掉）
            ilwn = ilw
            iupn = iun

    # ******* He II ***********
    # 标号 20
    if ion != 2 or C.IELHE2 <= 0:
        return il, alm, excl, excu, ion, iprf0, ilwn, iupn
    n0i = C.NFIRST[C.IELHE2]
    nlhe2 = C.NLAST[C.IELHE2] - n0i + 1
    xl = math.sqrt(1.0 / (1.0 - excl / 438916.146))
    ilw = int(xl)  # INT 截断取整
    if float(ilw) - xl < 0.0:
        ilw = ilw + 1
    xu = math.sqrt(1.0 / (1.0 - excu / 438916.146))
    iun = int(xu)
    if float(iun) - xu < 0.0:
        iun = iun + 1
    if ilw <= nlhe2:
        ilwn = ilw + n0i - 1
    if iun <= nlhe2:
        iupn = iun + n0i - 1
    return il, alm, excl, excu, ion, iprf0, ilwn, iupn
