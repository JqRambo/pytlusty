# -*- coding: utf-8 -*-
# chunk03: synspec54.f 行 2076–3461 的逐行直译
# 子程序: INIBL0 / INIBL1 / RESOLV / RTE / OUTPRI
# 按 CONVENTIONS.md: 分片内禁止 import; 直接用 np, math, C, params 常量, fortran 辅助函数


# ---------------------------------------------------------------- 辅助(非 Fortran 原文)

def _ldtok(unit, n):
    """辅助: list-directed READ(unit,*) —— 从单元读行并分词(逗号视为分隔符),
    至少凑够 n 个 token(不足时续读下一行); EOF 时 read_line 抛 EOFError
    (对应 Fortran 的 end= 分支)。多余的 token 丢弃(下一 READ 从新记录开始)。"""
    toks = []
    while len(toks) < n:
        toks += read_line(unit).replace(',', ' ').split()
    return toks


def _f8(s):
    """辅助: 解析 Fortran 实数 token(允许 D/d 指数)。"""
    return float(s.replace('D', 'e').replace('d', 'e'))


# OUTPRI 的 EQWT/EQWTP 是局部变量, 但跨调用累加(仅 IBLANK==1 时清零),
# 依赖 Fortran 局部变量的静态存储语义 → 提升为模块级变量(隐含 SAVE)
_save_outpri_eqwt = 0.0
_save_outpri_eqwtp = 0.0


# ***********************************************************************

def inibl0():
    """
    AUXILIARY INITIALIZATION PROCEDURE

    Parameters controlling an evaluation of the synthetic spectrum:

    ALAM0, ALAM1 - synthetic spectrum is evaluated between wavelengths
                   ALAM0 (initial) and ALAM1 (final), given in Anstroms
    CUTOF0       - cutoff parameter for normal lines (given in Angstroms)
                   ie the maximum distance from the line center, in
                   which the opacity in the line is allowd to contribute
                   to the total opacity (recommended 5 - 10)
    CUTOFS  = SPACON
    SPACON       - spacing of the continuum wavelength points
                   (at the midpoint of teh total interval; actual spacing
                   is equidistant in log(lambda)
    RELOP        - the minimum value of the ratio (opacity in the line
                   center)/(opacity in continuum), for which is the line
                   taken into account (usually 1d-4 to 1d-3)
    SPACE        - the maximum distance of two neighbouring frequency
                   points for evaluating the spectrum; in Angstroms

    INLTE        = 0  -  pure LTE (no line in NLTE)
                 ne.0 -  NLTE option, ie one or more lines treated
                         in the exact or approximate NLTE approach
    IFHE2        gt.0 -  He II line opacity in the first four series
                         (Lyman, Balmer, Paschen, Brackett)
                         for lines with lambda < 3900 A
                         is taken into account even if line list
                         does not contain any He II lines (i.e.
                         He II lines are treated as the hydrogen lines)

    IHYDPR      = 0  - means that hydrogen lines Stark profiles
                       are calculated by approximate formulae
                > 0  - hydrogen lines Stark profiles are calculated
                       in detail, using the Schoening & Butler tables;
                       (for 1-2 to 1-5; 2-3 to 2-10).
                       the tables are stored in file FOR0xx.dat,
                       where xx=IHYDPR;
                       higher Balmer lines are calculated as before

    the meaning of other parameters is quite analogous, for the
    following lines

    IHE1PR    - He I lines at 4471, 4026, 4387, and 4922 Angstroms
                (tables calculated by Barnard, Cooper, and Shamey)
    IHE2PR    - for the He II lines calculated by Schoening and Butler,

    对应 synspec54.f 行 2076–2531
    """
    un = 1.                     # parameter (un=1.)
    # character*2 iu / character*6 ilab → Python str
    # 局部数组(对应 DIMENSION 语句, 1 基索引)
    cross = np.zeros((MCROSS + 1, MFRQ + 1))
    abso = np.zeros(MFREQ + 1)
    emis = np.zeros(MFREQ + 1)
    scat = np.zeros(MFREQ + 1)
    absoc = np.zeros(MFREQC + 1)
    emisc = np.zeros(MFREQC + 1)
    scatc = np.zeros(MFREQC + 1)
    # TODO(port): IFEOS>0 时 alast/cutofs/space 未经 READ 赋值,
    # Fortran 中依赖局部变量的静态残留值; 此处按 0 初始化
    alast = 0.
    cutofs = 0.
    space = 0.

    if C.IFEOS <= 0:
        # READ(55,*) IFREQ,INLTE,ICONTL,INLIST,IFHE2
        _t = _ldtok(55, 5)
        C.IFREQ = int(_t[0])
        C.INLTE = int(_t[1])
        C.ICONTL = int(_t[2])
        C.INLIST = int(_t[3])
        C.IFHE2 = int(_t[4])
        if C.LTE:
            C.INLTE = 0
        # READ(55,*) IHYDPR,IHE1PR,IHE2PR
        _t = _ldtok(55, 3)
        C.IHYDPR = int(_t[0])
        C.IHE1PR = int(_t[1])
        C.IHE2PR = int(_t[2])
        # READ(55,*) ALAM0,ALAST,CUTOF0,CUTOFS,RELOP,SPACE
        # (ALAST/CUTOFS/SPACE 是本子程序的局部变量, 不在任何 COMMON 中)
        _t = _ldtok(55, 6)
        C.ALAM0 = _f8(_t[0])
        alast = _f8(_t[1])
        C.CUTOF0 = _f8(_t[2])
        cutofs = _f8(_t[3])
        C.RELOP = _f8(_t[4])
        space = _f8(_t[5])

    if C.IDSTD == 0:
        id1 = 5
        C.NDSTEP = idiv(C.ND - 2*id1, 2)   # Fortran 整数除法
        C.IDSTD = idiv(2*C.ND, 3)          # Fortran 整数除法
    elif C.IDSTD < 0:
        id1 = 1
        C.NDSTEP = -C.IDSTD
        C.IDSTD = idiv(2*C.ND, 3)          # Fortran 整数除法
    if C.IMODE <= -3:
        C.NDSTEP = 1

    C.ALAM0s = C.ALAM0
    C.ALASTs = alast
    C.CUTOF0s = C.CUTOF0
    C.CUTOFSs = cutofs
    C.RELOPs = C.RELOP
    C.SPACEs = space

    # if ALAST.lt.0 - set up vacuum wavelengths everywhere
    C.vaclim = 2000.
    if alast < 0.:
        alast = abs(alast)
        C.ALASTs = alast
        C.vaclim = 1.e18

    if C.INLTE < 10:
        C.lasdel = True
    elif C.INLTE <= 20:
        C.INLTE = C.INLTE - 10
        C.lasdel = False
    elif C.INLTE <= 30:
        C.INLTE = C.INLTE - 20
        C.IFREQ = 11
        C.lasdel = True
    elif C.INLTE <= 40:
        C.INLTE = C.INLTE - 30
        C.IFREQ = 11
        C.lasdel = False

    C.IBIN[0] = imod(C.INLIST, 10)
    for ilist in range(1, MMLIST + 1):
        C.TMLIM[ilist] = C.TMOLIM
        C.IBIN[ilist] = imod(C.INLIST, 10)
        C.IVDWLI[ilist] = 0
        iun = 19 + ilist
        iu = f"{iun:2d}"            # write(iu,622) iun —— 内部写; 622 format(i2)
        C.AMLIST[ilist] = 'fort.' + iu

    if -3 <= C.IMODE <= 1:
        C.NMLIST = 0
        numlis = 0
        # read(55,*,err=5,end=5) nmlist,(iunitm(ilist),ilist=1,nmlist)
        _rdok = True
        try:
            _t = _ldtok(55, 1)
            C.NMLIST = int(_t[0])
            _t = _t[1:]
            while len(_t) < C.NMLIST:   # 隐式 DO 列表, 不够时续读下一记录
                _t += read_line(55).replace(',', ' ').split()
            for ilist in range(1, C.NMLIST + 1):
                C.IUNITM[ilist] = int(_t[ilist - 1])
        except (EOFError, ValueError, IndexError):
            _rdok = False               # err=5 / end=5 → 跳到标号 5
            # TODO(port): 读部分失败时 Fortran 会保留已赋值的部分, 此处整体放弃
        if _rdok:
            for ilist in range(1, C.NMLIST + 1):
                iu = f"{C.IUNITM[ilist]:2d}"   # write(iu,622) iunitm(ilist); 622 format(i2)
                C.AMLIST[ilist] = 'fort.' + iu
        # 5 continue

        ilist = 0
        C.AMLIST[0] = 'fort.19'
        # read(3,*,err=20,end=20) amlist(0),ibin(0)
        _goto20 = False
        try:
            _t = _ldtok(3, 2)
            C.AMLIST[0] = _t[0]
            C.IBIN[0] = int(_t[1])
        except (EOFError, ValueError, IndexError):
            _goto20 = True              # err=20 / end=20 → 跳到标号 20
        if not _goto20:
            ilist = 0
            # 10 continue —— 循环读入各线列表, 直到文件结束(end=20)
            while True:
                ilist = ilist + 1
                try:
                    _t = _ldtok(3, 3)
                    C.AMLIST[ilist] = _t[0]
                    C.IBIN[ilist] = int(_t[1])
                    C.TMLIM[ilist] = _f8(_t[2])
                except (EOFError, ValueError, IndexError):
                    break               # end=20 → 出循环到标号 20
                numlis = numlis + 1
                # go to 10
        # 20 continue
        if numlis > 0:
            C.NMLIST = numlis
        if C.NMLIST > 0 and C.IFMOL == 0:
            print('NEEDS TO SET IFMOL > 0 with NMLIST>0')   # write(*,*)
            raise SystemExit            # STOP

        ilist = 0
        ilab = 'ATOMIC'
        #  623 format(/'************************'/
        #      *        ' LINE LISTS:'/
        #      *       /' ILIST',8x,'FILENAME  IBIN  TMLIM'/
        #      *        i4,2x,a6,2x,a,2x,i4,f11.1)
        # (ilist=0 这条只给 4 个输出项, 格式尾部 f11.1 无对应项 → 不输出)
        print()
        print('************************')
        print(' LINE LISTS:')
        print()
        print(' ILIST' + ' '*8 + 'FILENAME  IBIN  TMLIM')
        print(f"{ilist:4d}  {ilab:6s}  {C.AMLIST[ilist].rstrip()}  {C.IBIN[ilist]:4d}")
        ilab = 'MOLEC '
        for ilist in range(1, C.NMLIST + 1):
            # 624 format( i4,2x,a6,2x,a,2x,i4,f11.1)
            print(f"{ilist:4d}  {ilab:6s}  {C.AMLIST[ilist].rstrip()}  "
                  f"{C.IBIN[ilist]:4d}{C.TMLIM[ilist]:11.1f}")

    # VTB    - turbulent velocity (in km/s). In non-negative, this
    #          value overwrites the value given by the standard input
    _goto30 = False
    try:
        vtb = _f8(_ldtok(55, 1)[0])     # read(55,*,err=30,end=30) VTB
    except (EOFError, ValueError, IndexError):
        _goto30 = True                  # err=30 / end=30 → 跳到标号 30
    if not _goto30:
        if C.IFWIN <= 0:
            if vtb >= 0.:
                #  608 FORMAT(//' TURBULENT VELOCITY  -  CHANGED TO   VTURB =',
                #      *      1PE10.3,'  KM/S'/' ------------------'/)
                print()
                print()
                print(f" TURBULENT VELOCITY  -  CHANGED TO   VTURB ={vtb:10.3e}  KM/S")
                print(' ------------------')
                print()
                for id in range(1, C.ND + 1):
                    C.VTURB[id] = vtb*vtb*1.e10
        C.TSTD = C.TEMP[C.IDSTD]
        vts = C.VTURB[C.IDSTD]
        C.DSTD = math.sqrt(1.4e7*C.TSTD + vts)
    # 30 continue

    # angle points (in case the specific intensities are evaluated
    #
    # NMU0      -    number of angles:
    #           >0 - and if also ANG0>0, angles (mu's) equidistant
    #                between 1 and ANG0
    #           >0 - and if also ANG0<0, angles (mu's) equidistant
    #                between 0.7 and ANG0, and sinuses equidistatnt for
    #                others
    #           <0 - angles read in the next record
    # ANG0      -    minimum mu (see above)
    # IFLUX     -    mode for evaluating angle-dependent intensities and
    #                the corresponding flux:
    #           =0 - no specifiec intensities are evaluated; only usual
    #                flux is stored (unit 7 and 17)
    #           =1 - specific intensities are evaluated;
    #                and stored on unit 18
    #           =2 - (interesting only for the case of macroscopic
    #                velocity field); specific intensities evaluated by
    #                a simple formal solution (RESOLV)
    C.NMU0 = 1
    ang0 = 1.                   # ANG0 是局部变量(不在 COMMON 中)
    C.ANGL[1] = 1.
    C.WANGL[1] = 0.
    C.IFLUX = 0
    C.velmax = 3.e5
    C.nltoff = 0
    C.iemoff = 0
    C.itrad = 0
    for id in range(1, C.ND + 1):
        C.WDIL[id] = un
    if C.IFWIN <= 0:
        # READ(55,*,end=100,err=100) NMU0,ANG0,IFLUX
        _goto100 = False
        try:
            _t = _ldtok(55, 3)
            C.NMU0 = int(_t[0])
            ang0 = _f8(_t[1])
            C.IFLUX = int(_t[2])
        except (EOFError, ValueError, IndexError):
            _goto100 = True             # end=100 / err=100 → 跳到标号 100
        if not _goto100:
            # determinantion of the angle points and weights
            if C.NMU0 < 0:
                C.NMU0 = abs(C.NMU0)
                # READ(55,*) (ANGL(IMU),IMU=1,NMU0)
                _t = _ldtok(55, C.NMU0)
                for imu in range(1, C.NMU0 + 1):
                    C.ANGL[imu] = _f8(_t[imu - 1])
                for imu in range(2, C.NMU0):        # DO IMU=2,NMU0-1
                    C.WANGL[imu] = 0.5*(C.ANGL[imu - 1] + C.ANGL[imu + 1])
                C.WANGL[1] = 0.5*(C.ANGL[1] - C.ANGL[2])
                C.WANGL[C.NMU0] = 0.5*(C.ANGL[C.NMU0 - 1] - C.ANGL[C.NMU0])
            else:
                if ang0 > 0.:
                    if C.NMU0 > 1:
                        dmu = (1. - ang0)/(C.NMU0 - 1)
                        for imu in range(1, C.NMU0 + 1):
                            C.ANGL[imu] = 1. - (imu - 1)*dmu
                            C.WANGL[imu] = dmu
                        C.WANGL[1] = 0.5*dmu
                        C.WANGL[C.NMU0 - 1] = 0.5*dmu
                        C.WANGL[C.NMU0] = 2.*dmu
                else:
                    angh = 0.70710678
                    dmu = angh/(C.NMU0 - 1)
                    for imu in range(1, C.NMU0 + 1):
                        C.ANGL[imu] = (imu - 1)*dmu
                        C.ANGL[imu] = math.sqrt(1. - C.ANGL[imu]**2)
                        # 注意: Fortran 原文此处引用尚未算出的 ANGL(IMU+1), 按原文直译
                        if imu > 1 and imu < C.NMU0:
                            C.WANGL[imu] = 0.5*(C.ANGL[imu - 1] + C.ANGL[imu + 1])
                    C.WANGL[1] = 0.5*(C.ANGL[1] - C.ANGL[2])
                    C.WANGL[C.NMU0] = 0.5*(C.ANGL[C.NMU0 - 1] - C.ANGL[C.NMU0])
                    if ang0 < 0.:
                        dmu = (angh + ang0)/(C.NMU0 - 1)
                    for imu in range(1, C.NMU0 - 1):      # DO IMU=1,NMU0-2
                        C.ANGL[imu + C.NMU0] = angh - imu*dmu
                        C.WANGL[imu + C.NMU0] = dmu
                    C.WANGL[C.NMU0] = C.WANGL[C.NMU0] + 0.5*dmu
                    C.WANGL[2*C.NMU0 - 3] = 0.5*dmu
                    C.WANGL[2*C.NMU0 - 2] = 2.*dmu
                    C.NMU0 = 2*C.NMU0 - 2
            if C.NMU0 > 0:
                # (IF(NMU0.LE.0) GO TO 100 → 跳过此输出)
                #  609 FORMAT(//' SPECIFIC INTENSITIES COMPUTED FOR',I3,
                #      *         ' ANGLES  mu=cos(theta) ='/
                #      *         ' ---------------------------------',
                #      *         '------------------------'//
                #      *         (10F7.2))
                print()
                print()
                print(f" SPECIFIC INTENSITIES COMPUTED FOR{C.NMU0:3d}"
                      f" ANGLES  mu=cos(theta) =")
                print(' ---------------------------------'
                      '------------------------')
                print()
                for i0 in range(1, C.NMU0 + 1, 10):
                    print(''.join(f"{C.ANGL[i]:7.2f}"
                                  for i in range(i0, min(i0 + 10, C.NMU0 + 1))))
        # 100 continue
    else:
        C.itrad = 1
        try:
            # read(55,*,end=110,err=110) velmax,ITRAD,nltoff,iemoff
            _t = _ldtok(55, 4)
            C.velmax = _f8(_t[0])
            C.itrad = int(_t[1])
            C.nltoff = int(_t[2])
            C.iemoff = int(_t[3])
        except (EOFError, ValueError, IndexError):
            pass                        # end=110 / err=110 → 直接到标号 110
        # 110 —— 标号在 WRITE 语句上, 无论读是否成功都执行
        #  602 format(//' velmax (velocity for line rejection)',
        #      *       ' itrad,nltoff,iemoff',f10.1,2i3)
        # TODO(port): 输出 4 项但格式只有 f10.1,2i3, Fortran 发生格式回绕; 这里按 4 项输出
        print()
        print()
        print(f" velmax (velocity for line rejection) itrad,nltoff,iemoff"
              f"{C.velmax:10.1f}{C.itrad:3d}{C.nltoff:3d}{C.iemoff:3d}")
        if C.velmax < 0.:
            C.velmax = 3.e5
            # go to 120 → 跳过下面的射线与权重设置
        else:
            # Set up rays and weights
            velset()
            radtem()
            setray()
            wgtjh1()

    # 120 continue
    C.velmax = C.velmax*1.e5
    for id in range(1, C.ND + 1):
        C.ilvi[id] = 0
        C.ilne[id] = 0
        if C.VEL[id] > C.velmax and C.iemoff == 0:
            C.ilvi[id] = 1
        if C.VEL[id] > C.velmax and C.nltoff > 0 and C.iemoff > 0:
            C.ilne[id] = 1

    if C.IMODE == -1:
        C.INLTE = 0
        C.CUTOF0 = 0.

    # continuum frequencies
    if C.IFWIN <= 0:
        C.ALAM0 = C.ALAM0s
        if C.ALAM0s == 0.:
            C.ALAM0 = 5.e7/C.TEMP[1]/10.
        if C.ALAM0s < 0.:
            C.ALAM0 = -5.e7/C.TEMP[1]/C.ALAM0s
        alast = C.ALASTs
        if C.ALASTs == 0.:
            alast = 5.e7/C.TEMP[1]*20.
        if C.ALASTs < 0.:
            alast = -5.e7/C.TEMP[1]*C.ALASTs
        # if(alast.gt.1.e5) alast=1.e5   (原文注释掉的语句, 保留)
        C.ALAMC = (C.ALAM0 + alast)*0.5
        if space == 0.:
            space = 4.3e-8*math.sqrt(C.TEMP[C.IDSTD])*C.ALAMC
        if space < 0.:
            space = -5.72e-8*math.sqrt(C.TEMP[C.IDSTD])*C.ALAMC*space
        spacf = 2.997925e18/C.ALAMC/C.ALAMC*space
        #  601 FORMAT(//'----------------------------------------------'/
        #      *           ' BASIC INPUT PARAMETERS FOR SYNTHETIC SPECTRA'/
        #      *           ' ---------------------------------------------'/
        #      *           ' INITIAL LAMBDA',28X,1H=,F10.3,' ANGSTROMS'/
        #      *           ' FINAL   LAMBDA',28X,1H=,F10.3,' ANGSTROMS'/
        #      *           ' CUTOFF PARAMETER',26X,1H=,F10.3,' ANGSTROMS'/
        #      *           ' MINIMUM VALUE OF (LINE OPAC.)/(CONT.OPAC) =',1PE10.1/
        #      *           ' MAXIMUM FREQUENCY SPACING',17X,1H=,1PE10.3,'  I.E.',
        #      *             0PF6.3,'  ANGSTROMS'/
        #      *           ' ---------------------------------------------'/)
        print()
        print()
        print('----------------------------------------------')
        print(' BASIC INPUT PARAMETERS FOR SYNTHETIC SPECTRA')
        print(' ---------------------------------------------')
        print(' INITIAL LAMBDA' + ' '*28 + f"={C.ALAM0:10.3f} ANGSTROMS")
        print(' FINAL   LAMBDA' + ' '*28 + f"={alast:10.3f} ANGSTROMS")
        print(' CUTOFF PARAMETER' + ' '*26 + f"={C.CUTOF0:10.3f} ANGSTROMS")
        print(f" MINIMUM VALUE OF (LINE OPAC.)/(CONT.OPAC) ={C.RELOP:10.1e}")
        print(' MAXIMUM FREQUENCY SPACING' + ' '*17
              + f"={spacf:10.3e}  I.E.{space:6.3f}  ANGSTROMS")
        print(' ---------------------------------------------')
        print()
        C.CUTOF0 = 0.1*C.CUTOF0
        C.SPACE0 = space*0.1
        C.ALAM0 = 1.e-1*C.ALAM0
        alast = 1.e-1*alast
        C.ALAMC = C.ALAMC*0.1
        C.ALST00 = alast
        C.FRLAST = 2.997925e17/alast
        C.NFREQ = 2
        C.FREQ[1] = 2.997925e17/C.ALAM0
        C.FREQ[2] = C.FRLAST
    else:
        spacon = cutofs             # CUTOFS = SPACON
        if spacon == 0:
            spacon = 3.
        xfr = (alast - C.ALAM0)/spacon
        C.NFREQC = int(xfr) + 1     # INT(XFR) 截断取整
        C.NFREQC = min(C.NFREQC, MFREQC)
        C.NFREQC = max(C.NFREQC, 2)
        C.DLAMLO = math.log10(alast/C.ALAM0)/(C.NFREQC - 1)
        al0l = math.log10(C.ALAM0)
        C.ALAMBE = C.ALAM0
        for ij in range(1, C.NFREQC + 1):
            al = al0l + (ij - 1)*C.DLAMLO
            alam = math.exp(2.3025851*al)
            C.WLAMC[ij] = alam
            C.FREQC[ij] = 2.997925e18/alam
        C.ALAMC = (C.ALAM0 + alast)*0.5
        spacf = 2.997925e18/C.ALAMC/C.ALAMC*space
        # WRITE(6,601) —— 格式同上(行 2517–2526 的 601 FORMAT)
        print()
        print()
        print('----------------------------------------------')
        print(' BASIC INPUT PARAMETERS FOR SYNTHETIC SPECTRA')
        print(' ---------------------------------------------')
        print(' INITIAL LAMBDA' + ' '*28 + f"={C.ALAM0:10.3f} ANGSTROMS")
        print(' FINAL   LAMBDA' + ' '*28 + f"={alast:10.3f} ANGSTROMS")
        print(' CUTOFF PARAMETER' + ' '*26 + f"={C.CUTOF0:10.3f} ANGSTROMS")
        print(f" MINIMUM VALUE OF (LINE OPAC.)/(CONT.OPAC) ={C.RELOP:10.1e}")
        print(' MAXIMUM FREQUENCY SPACING' + ' '*17
              + f"={spacf:10.3e}  I.E.{space:6.3f}  ANGSTROMS")
        print(' ---------------------------------------------')
        print()
        C.CUTOF0 = 0.1*C.CUTOF0
        C.SPACE0 = space*0.1
        C.ALAM0 = 1.e-1*C.ALAM0
        alast = 1.e-1*alast
        C.ALAMC = C.ALAMC*0.1
        C.ALST00 = alast
        C.FRLAST = 2.997925e17/alast
        C.NFREQ = 2
        C.FREQ[1] = 2.997925e17/C.ALAM0
        C.FREQ[2] = C.FRLAST

    sigavs()
    if C.IHYDPR != 0:
        hydini()
        xenini()
    if C.IHE1PR > 0:
        he1ini()
    if C.IHE2PR > 0:
        he2ini()

    # auxiliary quantities for dissolved fractions
    for id in range(1, C.ND + 1):
        dwnfr0(id)
        wnstor(id)

    # pretabulate expansion coefficients for the Voigt function
    pretab()

    # calculate the characteristic standard opacity
    if C.IMODE <= 2:
        if C.IFWIN <= 0 and C.NDSTEP == 0:
            # old procedure
            croset(cross)
            for id in range(1, C.ND + 1):
                opac(id, cross, abso, emis, scat)
                C.ABSTD[id] = min(abso[1], abso[2])
        else:
            # new procedure
            if C.IFWIN <= 0:
                C.NFREQC = int(cutofs)      # ifix(real(cutofs,4)) 截断取整
                if C.NFREQC == 0:
                    C.NFREQC = MFREQ
                all0 = math.log(C.ALAM0)
                all1 = math.log(alast)
                dlc = (all1 - all0)/(C.NFREQC - 1)
                for ijc in range(1, C.NFREQC + 1):
                    C.WLAMC[ijc] = math.exp(all0 + (ijc - 1)*dlc)
                    C.FREQC[ijc] = 2.997925e17/C.WLAMC[ijc]
                crosew(cross)
                for id in range(1, C.ND + 1):
                    opacon(id, cross, absoc, emisc, scatc)
                    for ijc in range(1, C.NFREQC + 1):
                        C.ABSTDW[ijc, id] = absoc[ijc]
                # write(*,*) 'abstdw(1,ij)',(abstdw(ij,1),ij=1,nfreqc)   (原文注释)
                # write(*,*) 'abstdw(50,ij)',(abstdw(ij,50),ij=1,nfreqc) (原文注释)
            else:
                crosew(cross)
                for id in range(1, C.ND + 1):
                    opacw(id, cross, abso, emis, absoc, emisc, scatc, 0)
                    for ij in range(1, C.NFREQC + 1):
                        C.ABSTDW[ij, id] = absoc[ij]/C.DENSCON[id]

    # 612 format(/'IDSTD, NDSTEP = ',2i5/)
    print()
    print(f"IDSTD, NDSTEP = {C.IDSTD:5d}{C.NDSTEP:5d}")
    print()
    return


# ***********************************************************************

def inibl1(igrd):
    """=======================

    AUXILIARY INITIALIZATION PROCEDURE

    对应 synspec54.f 行 2536–2652
    """
    # parameter (un=1.,bnc=1.4743e-2,hkc=4.79928e4,clc=2.997925e17)
    un = 1.
    bnc = 1.4743e-2
    hkc = 4.79928e4
    clc = 2.997925e17
    cross = np.zeros((MCROSS + 1, MFRQ + 1))
    abso = np.zeros(MFREQ + 1)
    emis = np.zeros(MFREQ + 1)
    scat = np.zeros(MFREQ + 1)

    # auxiliary quantities for dissolved fractions
    for id in range(1, C.ND + 1):
        dwnfr0(id)
        wnstor(id)
        C.anh2[id] = 0.
        C.anhm[id] = 0.
        C.anch[id] = 0.
        C.anoh[id] = 0.
    tint()

    # reset wavelengths in case of opacity grid calculations
    if igrd >= 0:
        C.ALAM0 = C.ALAM0s
        if C.ALAM0s == 0.:
            C.ALAM0 = 5.e7/C.TEMP[1]/10.
        if C.ALAM0s < 0.:
            C.ALAM0 = -5.e7/C.TEMP[1]/C.ALAM0s
        alast = C.ALASTs
        if C.ALASTs == 0.:
            alast = 5.e7/C.TEMP[1]*20.
        if C.ALASTs < 0.:
            alast = -5.e7/C.TEMP[1]*C.ALASTs
        # if(alast.gt.1.e5) alast=1.e5   (原文注释掉的语句, 保留)
        C.CUTOF0 = C.CUTOF0s
        cutofs = C.CUTOFSs              # CUTOFS 是局部变量
        C.RELOP = C.RELOPs
        if C.RELOPs == 0:
            C.RELOP = 1.e-15
            if C.TEMP[1] < 2.e6:
                C.RELOP = 1.e-6
            if C.TEMP[1] < 1.e6:
                C.RELOP = 1.e-5
            if C.TEMP[1] < 1.e5:
                C.RELOP = 1.e-4
        space = C.SPACEs                # SPACE 是局部变量
        C.ALAMC = (C.ALAM0 + alast)*0.5
        if space == 0.:
            space = 4.3e-8*math.sqrt(C.TEMP[C.IDSTD])*C.ALAMC
        if space < 0.:
            space = -5.72e-8*math.sqrt(C.TEMP[C.IDSTD])*C.ALAMC*space
        spacf = 2.997925e18/C.ALAMC/C.ALAMC*space   # 计算后未使用, 按原文保留
        C.CUTOF0 = 0.1*C.CUTOF0
        C.SPACE0 = space*0.1
        C.ALAM0 = 1.e-1*C.ALAM0
        alast = 1.e-1*alast
        C.ALAMC = C.ALAMC*0.1
        C.ALST00 = alast
        C.FRLAST = clc/alast

        C.NFREQC = int(cutofs)          # ifix(real(cutofs,4)) 截断取整
        if C.NFREQC == 0:
            C.NFREQC = MFREQ
        all0 = math.log(C.ALAM0)
        all1 = math.log(alast)
        dlc = (all1 - all0)/(C.NFREQC - 1)
        xcc0 = hkc/C.TEMP[1]
        for ijc in range(1, C.NFREQC + 1):
            C.WLAMC[ijc] = math.exp(all0 + (ijc - 1)*dlc)
            C.FREQC[ijc] = clc/C.WLAMC[ijc]
            # frc=freqc(ijc)*1.e-15                          (原文注释)
            # plac(ijc)=bnc*frc**3/(exp(xcc0*frc)-un)        (原文注释)
        id = 1
        crosew(cross)
        opacon(id, cross, C.absoc, C.emisc, C.scatc)
        wc0 = (C.FREQC[1] - C.FREQC[2])*0.5                 # 计算后未使用, 按原文保留
        wc1 = (C.FREQC[C.NFREQC - 1] - C.FREQC[C.NFREQC])*0.5
        for ijc in range(2, C.NFREQC):  # DO IJC=2,NFREQC-1
            C.absoc[ijc] = min(C.absoc[ijc], 1.e30)
            # 642 format(f11.3,1p5e13.5) —— 只输出 2 项
            write_line(26, f"{C.WLAMC[ijc]*10.:11.3f}"
                           f"{math.log(C.absoc[ijc]/C.DENS[1]):13.5e}")

        for ijc in range(1, C.NFREQC + 1):
            C.ABSTDW[ijc, id] = C.absoc[ijc]

    # calculate the characteristic standard opacity
    if C.IMODE <= 2 and C.IMODE >= -2:
        if C.IFWIN <= 0:
            croset(cross)
            for id in range(1, C.ND + 1):
                opac(id, cross, abso, emis, scat)
                C.ABSTD[id] = min(abso[1] + scat[1], abso[2] + scat[2])
        else:
            crosew(cross)
            for id in range(1, C.ND + 1):
                opacw(id, cross, abso, emis, C.absoc, C.emisc, C.scatc, 0)
                for ij in range(1, C.NFREQC + 1):
                    C.DENSCON[id] = 1.      # 原文在 DO IJ 循环内反复赋值, 按原文保留
                    C.ABSTDW[ij, id] = C.absoc[ij]/C.DENSCON[id]

    return


# *******************************************************************

def resolv():
    """
    driver for evaluating opacities and emissivities which then
    enter the solution of the radiative transfer equation
    (RTE or RTEDFE)

    对应 synspec54.f 行 2657–2742
    """
    cross = np.zeros((MCROSS + 1, MFRQ + 1))
    abso = np.zeros(MFREQ + 1)
    emis = np.zeros(MFREQ + 1)
    scat = np.zeros(MFREQ + 1)

    C.IHYL = -1

    # if(imode.le.-3) call abnchn(1)   (原文注释掉的语句, 保留)

    # set up the partial line list for the current interval
    iniset()
    if C.IFMOL > 0:
        for ilist in range(1, C.NMLIST + 1):
            molset(ilist)

    # select possible hydrogen lines that may contribute to the opacity
    if C.IMODE != -1:
        hylset()

    # select possible He II lines that may contribute to the opacity
    if C.IMODE != -1:
        he2set()

    # output of information about selected lines
    inibla()
    if C.IFMOL > 0:
        iniblm()

    # photoinization cross-sections
    croset(cross)

    # monochromatic opacity and emissivity including all contributing
    # lines and continua
    if C.IMODE >= -1:
        for id in range(1, C.ND + 1):
            opac(id, cross, abso, emis, scat)
            C.ABSTD[id] = 0.5*(abso[1] + abso[2])
            for ij in range(1, C.NFREQ + 1):
                C.CH[ij, id] = abso[ij]
                C.ET[ij, id] = emis[ij]
                C.SC[ij, id] = scat[ij]
            if C.IMODE0 == -4:
                ougrid(abso)

        # output of information about selected hydrogen lines
        iniblh()

    # the iron curtain or opacity table  option - output of monochromatic opacities
    elif C.IMODE == -2:
        id = 1
        # 626 format(1p3e15.4)
        write_line(27, f"{C.TEMP[id]:15.4e}{C.DENS[id]:15.4e}{C.ELEC[id]:15.4e}")
        opac(id, cross, abso, emis, scat)
        for ij in range(3, C.NFREQ):    # DO IJ=3,NFREQ-1
            abso[ij] = (abso[ij] + scat[ij])/C.HPOP
            # 627 format(f15.3,1p2e15.5)
            write_line(27, f"{C.WLAM[ij]:15.3f}{abso[ij]:15.5e}{scat[ij]:15.5e}")
    else:
        id = 1
        opac(id, cross, abso, emis, scat)
        C.CH[1, id] = abso[1]
        C.CH[2, id] = abso[2]
        ougrid(abso)
    return


# ********************************************************************

def rte():
    """
    solution of the radiative transfer equation by Feautrier method

    对应 synspec54.f 行 2746–3339
    """
    # 局部数组(1 基索引; DIMENSION D(3,3,MDEPTH),ANU(3,MDEPTH),... RINT(MDEPTH,MMU))
    d = np.zeros((4, 4, MDEPTH + 1))
    anu = np.zeros((4, MDEPTH + 1))
    aanu = np.zeros(MDEPTH + 1)
    ddd = np.zeros(MDEPTH + 1)
    aa = np.zeros((4, 4))
    bb = np.zeros((4, 4))
    cc = np.zeros((4, 4))
    vl = np.zeros(4)
    dt = np.zeros(MDEPTH + 1)
    tau = np.zeros(MDEPTH + 1)
    rdd = np.zeros(MDEPTH + 1)
    fkk = np.zeros(MDEPTH + 1)
    st0 = np.zeros(MDEPTH + 1)
    ss0 = np.zeros(MDEPTH + 1)
    rint = np.zeros((MDEPTH + 1, MMU + 1))
    # DATA AMU/.887298334620742D0,.5D0,.112701665379258D0/  (之后不再修改)
    amu = np.array([0., .887298334620742, .5, .112701665379258])
    # DATA WTMU/.277777777777778D0,.444444444444444D0,.277777777777778D0/
    wtmu = np.array([0., .277777777777778, .444444444444444, .277777777777778])
    # DATA TYPION /' I  ',' II ',' III',' IV ',' V  ',' VI ',' VII','VIII',' IX '/
    typion = ['', ' I  ', ' II ', ' III', ' IV ', ' V  ', ' VI ', ' VII', 'VIII', ' IX ']
    # PARAMETER (UN=1.D0, HALF=0.5D0)
    un = 1.
    half = 0.5
    # PARAMETER (THIRD=UN/3., QUART=UN/4., SIXTH=UN/6.D0)
    third = un/3.
    quart = un/4.
    sixth = un/6.
    # PARAMETER (TAUREF = 0.6666666666667)
    tauref = 0.6666666666667

    C.NMU = 3                   # NMU 在 COMMON/BASNUM/ 中
    nd1 = C.ND - 1

    # Overall loop over frequencies
    for ij in range(1, C.NFREQ + 1):
        taumin = C.CH[ij, 1]/C.DENS[1]*C.DM[1]*half
        tau[1] = taumin
        iref = 1
        for i in range(1, nd1 + 1):     # DO I=1,ND1
            dt[i] = (C.DM[i + 1] - C.DM[i])*(C.CH[ij, i + 1]/C.DENS[i + 1]
                                             + C.CH[ij, i]/C.DENS[i])*half
            st0[i] = C.ET[ij, i]/C.CH[ij, i]
            ss0[i] = -C.SC[ij, i]/C.CH[ij, i]
            tau[i + 1] = tau[i] + dt[i]
            if tau[i] <= tauref and tau[i + 1] > tauref:
                iref = i
        C.IREFD[ij] = iref
        st0[C.ND] = C.ET[ij, C.ND]/C.CH[ij, C.ND]
        ss0[C.ND] = -C.SC[ij, C.ND]/C.CH[ij, C.ND]
        fr = C.FREQ[ij]
        bnu = BN*(fr*1.e-15)**3
        pland = bnu/(math.exp(HK*fr/C.TEMP[C.ND]) - un)
        dplan = bnu/(math.exp(HK*fr/C.TEMP[C.ND - 1]) - un)
        dplan = (pland - dplan)/dt[nd1]

        # +++++++++++++++++++++++++++++++++++++++++
        # FIRST PART  -  VARIABLE EDDINGTON FACTORS
        # +++++++++++++++++++++++++++++++++++++++++
        alb1 = 0.
        for i in range(1, C.NMU + 1):
            # ************************
            # UPPER BOUNDARY CONDITION
            # ************************
            id = 1
            dtp1 = dt[1]
            q0 = 0.
            p0 = 0.

            # allowance for non-zero optical depth at the first depth point
            tamm = taumin/amu[i]
            if tamm > 0.01:
                p0 = un - math.exp(-tamm)
            else:
                p0 = tamm*(un - half*tamm*(un - tamm*third*(un - quart*tamm)))
            ex = un - p0                # 计算后未使用, 按原文保留
            q0 = q0 + p0*amu[i]*wtmu[i]

            div = dtp1/amu[i]*third
            vl[i] = div*(st0[id] + half*st0[id + 1]) + st0[id]*p0
            for j in range(1, C.NMU + 1):
                bb[i, j] = ss0[id]*wtmu[j]*(div + p0) - alb1*wtmu[j]
                cc[i, j] = -half*div*ss0[id + 1]*wtmu[j]
            bb[i, i] = bb[i, i] + amu[i]/dtp1 + un + div
            cc[i, i] = cc[i, i] + amu[i]/dtp1 - half*div
            anu[i, id] = 0.

        # Matrix inversion: instead of calling MATINV, a very fast inlined
        # routine MINV3 for a specific 3 x 3 matrix inversion
        # CALL MATINV(BB,NMU,3)
        bb[2, 1] = bb[2, 1]/bb[1, 1]
        bb[2, 2] = bb[2, 2] - bb[2, 1]*bb[1, 2]
        bb[2, 3] = bb[2, 3] - bb[2, 1]*bb[1, 3]
        bb[3, 1] = bb[3, 1]/bb[1, 1]
        bb[3, 2] = (bb[3, 2] - bb[3, 1]*bb[1, 2])/bb[2, 2]
        bb[3, 3] = bb[3, 3] - bb[3, 1]*bb[1, 3] - bb[3, 2]*bb[2, 3]

        bb[3, 2] = -bb[3, 2]
        bb[3, 1] = -bb[3, 1] - bb[3, 2]*bb[2, 1]
        bb[2, 1] = -bb[2, 1]

        bb[3, 3] = un/bb[3, 3]
        bb[2, 3] = -bb[2, 3]*bb[3, 3]/bb[2, 2]
        bb[2, 2] = un/bb[2, 2]
        bb[1, 3] = -(bb[1, 2]*bb[2, 3] + bb[1, 3]*bb[3, 3])/bb[1, 1]
        bb[1, 2] = -bb[1, 2]*bb[2, 2]/bb[1, 1]
        bb[1, 1] = un/bb[1, 1]

        bb[1, 1] = bb[1, 1] + bb[1, 2]*bb[2, 1] + bb[1, 3]*bb[3, 1]
        bb[1, 2] = bb[1, 2] + bb[1, 3]*bb[3, 2]
        bb[2, 1] = bb[2, 2]*bb[2, 1] + bb[2, 3]*bb[3, 1]
        bb[2, 2] = bb[2, 2] + bb[2, 3]*bb[3, 2]
        bb[3, 1] = bb[3, 3]*bb[3, 1]
        bb[3, 2] = bb[3, 3]*bb[3, 2]

        for i in range(1, C.NMU + 1):
            for j in range(1, C.NMU + 1):
                s = 0.
                for k in range(1, C.NMU + 1):
                    s = s + bb[i, k]*cc[k, j]
                d[i, j, id] = s
                anu[i, 1] = anu[i, 1] + bb[i, j]*vl[j]

        # *******************
        # NORMAL DEPTH POINTS
        # *******************
        for id in range(2, nd1 + 1):
            dtm1 = dtp1
            dtp1 = dt[id]
            dt0 = half*(dtm1 + dtp1)
            al = un/dtm1/dt0
            ga = un/dtp1/dt0
            be = al + ga
            # 原文标量 A/B/C; C 与 commons 别名冲突 → a_l/b_l/c_l
            a_l = (un - half*al*dtp1*dtp1)*sixth
            c_l = (un - half*ga*dtm1*dtm1)*sixth
            b_l = un - a_l - c_l
            vl0 = a_l*st0[id - 1] + b_l*st0[id] + c_l*st0[id + 1]
            for i in range(1, C.NMU + 1):
                for j in range(1, C.NMU + 1):
                    aa[i, j] = -a_l*ss0[id - 1]*wtmu[j]
                    cc[i, j] = -c_l*ss0[id + 1]*wtmu[j]
                    bb[i, j] = b_l*ss0[id]*wtmu[j]
            for i in range(1, C.NMU + 1):
                div = amu[i]**2
                vl[i] = vl0
                aa[i, i] = aa[i, i] + div*al - a_l
                cc[i, i] = cc[i, i] + div*ga - c_l
                bb[i, i] = bb[i, i] + div*be + b_l
            for i in range(1, C.NMU + 1):
                s1 = 0.
                for j in range(1, C.NMU + 1):
                    s = 0.
                    s1 = s1 + aa[i, j]*anu[j, id - 1]
                    for k in range(1, C.NMU + 1):
                        s = s + aa[i, k]*d[k, j, id - 1]
                    bb[i, j] = bb[i, j] - s
                vl[i] = vl[i] + s1

            # Matrix inversion: instead of calling MATINV, a very fast inlined
            # routine MINV3 for a specific 3 x 3 matrix inversion
            # CALL MATINV(BB,NMU,3)
            bb[2, 1] = bb[2, 1]/bb[1, 1]
            bb[2, 2] = bb[2, 2] - bb[2, 1]*bb[1, 2]
            bb[2, 3] = bb[2, 3] - bb[2, 1]*bb[1, 3]
            bb[3, 1] = bb[3, 1]/bb[1, 1]
            bb[3, 2] = (bb[3, 2] - bb[3, 1]*bb[1, 2])/bb[2, 2]
            bb[3, 3] = bb[3, 3] - bb[3, 1]*bb[1, 3] - bb[3, 2]*bb[2, 3]

            bb[3, 2] = -bb[3, 2]
            bb[3, 1] = -bb[3, 1] - bb[3, 2]*bb[2, 1]
            bb[2, 1] = -bb[2, 1]

            bb[3, 3] = un/bb[3, 3]
            bb[2, 3] = -bb[2, 3]*bb[3, 3]/bb[2, 2]
            bb[2, 2] = un/bb[2, 2]
            bb[1, 3] = -(bb[1, 2]*bb[2, 3] + bb[1, 3]*bb[3, 3])/bb[1, 1]
            bb[1, 2] = -bb[1, 2]*bb[2, 2]/bb[1, 1]
            bb[1, 1] = un/bb[1, 1]

            bb[1, 1] = bb[1, 1] + bb[1, 2]*bb[2, 1] + bb[1, 3]*bb[3, 1]
            bb[1, 2] = bb[1, 2] + bb[1, 3]*bb[3, 2]
            bb[2, 1] = bb[2, 2]*bb[2, 1] + bb[2, 3]*bb[3, 1]
            bb[2, 2] = bb[2, 2] + bb[2, 3]*bb[3, 2]
            bb[3, 1] = bb[3, 3]*bb[3, 1]
            bb[3, 2] = bb[3, 3]*bb[3, 2]

            for i in range(1, C.NMU + 1):
                anu[i, id] = 0.
                for j in range(1, C.NMU + 1):
                    s = 0.
                    for k in range(1, C.NMU + 1):
                        s = s + bb[i, k]*cc[k, j]
                    d[i, j, id] = s
                    anu[i, id] = anu[i, id] + bb[i, j]*vl[j]

        # ************
        # LOWER BOUNDARY CONDITION
        # ************
        id = C.ND

        # First option:
        # b.c. is different from stellar atmospheres; expresses symmetry
        # at the central plane   I(taumax,-mu,nu)=I(taumax,+mu,nu)
        if C.IFZ0 == 0:
            b_l = dtp1*half
            a_l = 0.
            for i in range(1, C.NMU + 1):
                bi = b_l/amu[i]
                ai = a_l/amu[i]
                vl[i] = st0[id]*bi + st0[id - 1]*ai
                for j in range(1, C.NMU + 1):
                    aa[i, j] = -ai*ss0[id - 1]*wtmu[j]
                    bb[i, j] = bi*ss0[id]*wtmu[j]
                aa[i, i] = aa[i, i] + amu[i]/dtp1 - ai
                bb[i, i] = bb[i, i] + amu[i]/dtp1 + bi
            for i in range(1, C.NMU + 1):
                s1 = 0.
                for j in range(1, C.NMU + 1):
                    s = 0.
                    s1 = s1 + aa[i, j]*anu[j, id - 1]
                    for k in range(1, C.NMU + 1):
                        s = s + aa[i, k]*d[k, j, id - 1]
                    bb[i, j] = bb[i, j] - s
                vl[i] = vl[i] + s1

        # Second option:
        # b.c. is the same as in stellar atmospheres - the last depth point
        # is not at the central plane
        else:
            for i in range(1, C.NMU + 1):
                aa[i, i] = amu[i]/dtp1
                vl[i] = pland + amu[i]*dplan + aa[i, i]*anu[i, id - 1]
                for j in range(1, C.NMU + 1):
                    bb[i, j] = -aa[i, i]*d[i, j, id - 1]
                bb[i, i] = bb[i, i] + aa[i, i] + un

        # Matrix inversion: instead of calling MATINV, a very fast inlined
        # routine MINV3 for a specific 3 x 3 matrix inversion
        # CALL MATINV(BB,NMU,3)
        bb[2, 1] = bb[2, 1]/bb[1, 1]
        bb[2, 2] = bb[2, 2] - bb[2, 1]*bb[1, 2]
        bb[2, 3] = bb[2, 3] - bb[2, 1]*bb[1, 3]
        bb[3, 1] = bb[3, 1]/bb[1, 1]
        bb[3, 2] = (bb[3, 2] - bb[3, 1]*bb[1, 2])/bb[2, 2]
        bb[3, 3] = bb[3, 3] - bb[3, 1]*bb[1, 3] - bb[3, 2]*bb[2, 3]

        bb[3, 2] = -bb[3, 2]
        bb[3, 1] = -bb[3, 1] - bb[3, 2]*bb[2, 1]
        bb[2, 1] = -bb[2, 1]

        bb[3, 3] = un/bb[3, 3]
        bb[2, 3] = -bb[2, 3]*bb[3, 3]/bb[2, 2]
        bb[2, 2] = un/bb[2, 2]
        bb[1, 3] = -(bb[1, 2]*bb[2, 3] + bb[1, 3]*bb[3, 3])/bb[1, 1]
        bb[1, 2] = -bb[1, 2]*bb[2, 2]/bb[1, 1]
        bb[1, 1] = un/bb[1, 1]

        bb[1, 1] = bb[1, 1] + bb[1, 2]*bb[2, 1] + bb[1, 3]*bb[3, 1]
        bb[1, 2] = bb[1, 2] + bb[1, 3]*bb[3, 2]
        bb[2, 1] = bb[2, 2]*bb[2, 1] + bb[2, 3]*bb[3, 1]
        bb[2, 2] = bb[2, 2] + bb[2, 3]*bb[3, 2]
        bb[3, 1] = bb[3, 3]*bb[3, 1]
        bb[3, 2] = bb[3, 3]*bb[3, 2]

        for i in range(1, C.NMU + 1):
            anu[i, id] = 0.
            for j in range(1, C.NMU + 1):
                d[i, j, id] = 0.
                anu[i, id] = anu[i, id] + bb[i, j]*vl[j]

        # ************
        # BACKSOLUTION
        # ************
        id = C.ND
        fkk[C.ND] = third
        aj = 0.
        ak = 0.
        for i in range(1, C.NMU + 1):
            rmu = wtmu[i]*anu[i, id]
            aj = aj + rmu
            ak = ak + rmu*amu[i]*amu[i]
        rdd[id] = aj
        fkk[C.ND] = ak/aj
        for id in range(C.ND - 1, 0, -1):  # DO ID=ND-1,1,-1
            for i in range(1, C.NMU + 1):
                for j in range(1, C.NMU + 1):
                    anu[i, id] = anu[i, id] + d[i, j, id]*anu[j, id + 1]
            aj = 0.
            ak = 0.
            for i in range(1, C.NMU + 1):
                div = wtmu[i]*anu[i, id]
                aj = aj + div
                ak = ak + div*amu[i]**2
            fkk[id] = ak/aj

        # surface Eddington actor
        ah = 0.
        for i in range(1, C.NMU + 1):
            ah = ah + wtmu[i]*amu[i]*anu[i, 1]
        fh = ah/aj - half*alb1

        # FKK(ND)=THIRD   (原文注释掉的语句, 保留)

        # +++++++++++++++++++++++++++++++++++++++++
        # SECOND PART  -  DETERMINATION OF THE MEAN INTENSITIES
        # RECALCULATION OF THE TRANSFER EQUATION WITH GIVEN EDDINGTON FACTORS
        # +++++++++++++++++++++++++++++++++++++++++
        dtp1 = dt[1]
        div = dtp1*third
        bbb = fkk[1]/dtp1 + fh + div + ss0[1]*(div + q0)
        ccc = fkk[2]/dtp1 - half*div*(un + ss0[2])
        vll = div*(st0[1] + half*st0[2]) + st0[1]*q0
        aanu[1] = vll/bbb
        ddd[1] = ccc/bbb
        for id in range(2, nd1 + 1):
            dtm1 = dtp1
            dtp1 = dt[id]
            dt0 = half*(dtp1 + dtm1)
            al = un/dtm1/dt0
            ga = un/dtp1/dt0
            a_l = (un - half*dtp1*dtp1*al)*sixth
            c_l = (un - half*dtm1*dtm1*ga)*sixth
            aaa = al*fkk[id - 1] - a_l*(un + ss0[id - 1])
            ccc = ga*fkk[id + 1] - c_l*(un + ss0[id + 1])
            bbb = (al + ga)*fkk[id] + (un - a_l - c_l)*(un + ss0[id])
            vll = a_l*st0[id - 1] + c_l*st0[id + 1] + (un - a_l - c_l)*st0[id]
            bbb = bbb - aaa*ddd[id - 1]
            ddd[id] = ccc/bbb
            aanu[id] = (vll + aaa*aanu[id - 1])/bbb

        # Lower boundary condition
        # 1.option -  different from stellar atmospheres
        if C.IFZ0 == 0:
            b_l = dtp1*half
            bbb = fkk[C.ND]/dtp1 + b_l*(un + ss0[C.ND])
            aaa = fkk[C.ND - 1]/dtp1
            vll = b_l*st0[C.ND]
        # Lower boundary condition
        # 2.option - stellar atmospheric
        else:
            bbb = fkk[C.ND]/dtp1 + half
            aaa = fkk[nd1]/dtp1
            vll = half*pland + dplan*third
        bbb = bbb - aaa*ddd[nd1]
        rdd[C.ND] = (vll + aaa*aanu[nd1])/bbb
        for iid in range(1, nd1 + 1):
            id = C.ND - iid
            rdd[id] = aanu[id] + ddd[id]*rdd[id + 1]
        C.FLUX[ij] = fh*rdd[1]

        # if needed (if iprin.ge.3), output of interesting physical
        # quantities at the monochromatic optical depth  tau(nu)=2/3
        if C.IPRIN >= 3:
            t0 = math.log(tau[iref + 1]/tau[iref])
            x0 = math.log(tau[iref + 1]/tauref)/t0
            x1 = math.log(tauref/tau[iref])/t0
            dmref = math.exp(math.log(C.DM[iref])*x0 + math.log(C.DM[iref + 1])*x1)
            tref = math.exp(math.log(C.TEMP[iref])*x0 + math.log(C.TEMP[iref + 1])*x1)
            stref = math.exp(math.log(st0[iref])*x0 + math.log(st0[iref + 1])*x1)
            scref = math.exp(math.log(-ss0[iref])*x0 + math.log(-ss0[iref + 1])*x1)
            ssref = math.exp(math.log(-ss0[iref]*rdd[iref])*x0
                             + math.log(-ss0[iref + 1]*rdd[iref + 1])*x1)
            sref = stref + ssref
            alm = 2.997925e18/C.FREQ[ij]
            # 636 FORMAT(1H ,I3,F10.3,I4,1PE10.3,0PF10.1,1X,1P3E10.3,E11.3)
            write_line(96, f" {ij:3d}{alm:10.3f}{iref:4d}{dmref:10.3e}{tref:10.1f} "
                           f"{scref:10.3e}{stref:10.3e}{ssref:10.3e}{sref:11.3e}")

        # THIRD PART  -  DETERMINATION OF THE SPECIFIC INTENSITIES
        # RECALCULATION OF THE TRANSFER EQUATION WITH GIVEN SOURCE FUNCTION
        if C.IFLUX == 0:
            return                  # if(iflux.eq.0) return —— 在频率循环内提前 RETURN
        for imu in range(1, C.NMU0 + 1):
            anx = C.ANGL[imu]
            dtp1 = dt[1]
            div = dtp1*third/anx

            tamm = taumin/anx
            if tamm < 0.01:
                p0 = tamm*(un - half*tamm*(un - tamm*third*(un - quart*tamm)))
            else:
                p0 = un - math.exp(-tamm)

            bbb = anx/dtp1 + un + div
            ccc = anx/dtp1 - half*div
            vll = (div + p0)*(st0[1] - ss0[1]*rdd[1]) \
                + half*div*(st0[2] - ss0[2]*rdd[2])
            aanu[1] = vll/bbb
            ddd[1] = ccc/bbb
            div = anx*anx
            for id in range(2, nd1 + 1):
                dtm1 = dt[id - 1]
                dtp1 = dt[id]
                dt0 = half*(dtp1 + dtm1)
                al = un/dtm1/dt0
                ga = un/dtp1/dt0
                a_l = (un - half*dtp1*dtp1*al)*sixth
                c_l = (un - half*dtm1*dtm1*ga)*sixth
                aaa = div*al - a_l
                ccc = div*ga - c_l
                bbb = div*(al + ga) + un - a_l - c_l
                vll = a_l*(st0[id - 1] - ss0[id - 1]*rdd[id - 1]) \
                    + c_l*(st0[id + 1] - ss0[id + 1]*rdd[id + 1]) \
                    + (un - a_l - c_l)*(st0[id] - ss0[id]*rdd[id])
                bbb = bbb - aaa*ddd[id - 1]
                ddd[id] = ccc/bbb
                aanu[id] = (vll + aaa*aanu[id - 1])/bbb

            # Lower boundary condition
            # 1.option -  different from stellar atmospheres
            if C.IFZ0 == 0:
                b_l = dtp1*half/anx
                bbb = anx/dtp1 + b_l*(un + ss0[C.ND])
                aaa = anx/dtp1
                vll = b_l*st0[C.ND]
            # Lower boundary condition
            # 2.option - stellar atmospheric
            else:
                aaa = anx/dtp1
                bbb = aaa + un
                vll = pland + anx*dplan

            rint[C.ND, imu] = (vll + aaa*aanu[nd1])/(bbb - aaa*ddd[nd1])
            for iid in range(1, nd1 + 1):
                id = C.ND - iid
                rint[id, imu] = aanu[id] + ddd[id]*rint[id + 1, imu]

        flx = 0.
        for imu in range(1, C.NMU0 + 1):
            rint[1, imu] = rint[1, imu]/half
            flx = flx + C.ANGL[imu]*C.WANGL[imu]*rint[1, imu]
        flx = flx*half
        # FLUX(IJ)=FLX   (原文注释掉的语句, 保留)

        # output of emergent specific intensities to Unit 10
        # and 18 (continuum)
        #  641 FORMAT(1H ,f10.3,1pe15.5/(1P5E15.5))
        _unit = 10 if ij > 2 else 18
        write_line(_unit, f" {C.WLAM[ij]:10.3f}{flx:15.5e}")
        for i0 in range(1, C.NMU0 + 1, 5):
            write_line(_unit, ''.join(f"{rint[1, imu]:15.5e}"
                                      for imu in range(i0, min(i0 + 5, C.NMU0 + 1))))

        if C.IPRIN == 4:
            # compute contribution function C_i (ctri) and C_r (ctrr)
            # following Magain (1986, A&A 163, 135)
            if C.IJCTR[ij] > 0:
                xfr0 = (C.FREQ[ij] - C.FREQ[2])/(C.FREQ[1] - C.FREQ[2])
                tauc = C.CH[1, 1]/C.DENS[1]*C.DM[1]*half
                for id in range(1, C.ND + 1):
                    chc1 = C.CH[1, id]
                    chc2 = C.CH[2, id]
                    chcc = chc2 + xfr0*(chc1 - chc2)
                    etc1 = C.ET[1, id]
                    etc2 = C.ET[2, id]
                    etcc = etc2 + xfr0*(etc1 - etc2)
                    stcc = etcc/chcc
                    cint = C.CINT2[id] + xfr0*(C.CINT1[id] - C.CINT2[id])
                    avx = (chc1 + chc2)*0.5*C.RELOP
                    linop(id, C.ABXLI, C.EMXLI, avx)
                    sli0 = C.EMXLI[ij]/C.ABXLI[ij]
                    abt0 = C.CH[ij, id]
                    emt0 = C.ET[ij, id]
                    stt0 = emt0/abt0
                    C.XKAR[id] = C.ABXLI[ij] + chcc*stcc/cint
                    C.CTRI[id] = tauc*abt0/chc1*stt0*math.exp(-tau[id])
                    if tau[id] > 70.:
                        C.CTRI[id] = 0.
                    C.CTRR[id] = tauc/chc1*C.ABXLI[ij]*(un - sli0/cint)
                    if id < C.ND:
                        dtc = (C.CH[1, id + 1]/C.DENS[id + 1] + C.CH[1, id]/C.DENS[id])
                        tauc = tauc + half*dtc*(C.DM[id + 1] - C.DM[id])
                taurs = C.XKAR[1]/C.DENS[1]*C.DM[1]*half
                xcti = C.CTRI[1]*half*(C.DM[2] - C.DM[1])
                xctr = C.CTRR[1]*half*(C.DM[2] - C.DM[1])
                for i in range(1, C.ND):    # DO I=1,ND-1
                    C.CTRR[i] = C.CTRR[i]*math.exp(-taurs)
                    if i == 1:
                        xctr = xctr*math.exp(-taurs)
                    if i > 1:
                        xcti = xcti + C.CTRI[i]*half*(C.DM[i + 1] - C.DM[i - 1])
                        xctr = xctr + C.CTRR[i]*half*(C.DM[i + 1] - C.DM[i - 1])
                    if taurs > 70.:
                        C.CTRR[i] = 0.
                    dtrs = (C.DM[i + 1] - C.DM[i])*(C.XKAR[i + 1]/C.DENS[i + 1]
                                                    + C.XKAR[i]/C.DENS[i])
                    taurs = taurs + half*dtrs
                C.CTRR[C.ND] = 0.
                alam = 2.997925e18/C.FREQ[ij]
                il0 = C.IJCTR[ij]
                il = C.INDLIN[il0]
                iat = idiv(C.INDAT[il], 100)    # Fortran 整数除法
                ion = imod(C.INDAT[il], 100)
                # 376 format(i5,f11.4,2x,2a4,i8,1pe12.4,0pf10.1)
                write_line(97, f"{il:5d}{alam:11.4f}  {C.TYPAT[iat]:4s}{typion[ion]:4s}"
                               f"{iref:8d}{dmref:12.4e}{tref:10.1f}")
                for id in range(1, C.ND + 1):
                    ctrip = C.CTRI[id]/xcti
                    ctrrp = C.CTRR[id]/xctr
                    # 377 format(i4,1p4e12.4)
                    write_line(97, f"{id:4d}{C.DM[id]:12.4e}{tau[id]:12.4e}"
                                   f"{ctrip:12.4e}{ctrrp:12.4e}")
            elif ij == 1:
                for id in range(1, C.ND + 1):
                    C.CINT1[id] = rint[id, C.NMU0]
            elif ij == 2:
                for id in range(1, C.ND + 1):
                    C.CINT2[id] = rint[id, C.NMU0]

    # end of the global loop over frequencies
    return


# ********************************************************************

def outpri():
    """
    Output of synthetic spectrum

    Output onto unit 7 serves as an input to the next program
    ROTINS, which performs convolutions for the rotational and
    instrumental broadening, and plots the synthetic spectrum

    对应 synspec54.f 行 3343–3458
    """
    # EQWT/EQWTP 跨调用累加(隐含 SAVE) → 模块级变量
    global _save_outpri_eqwt, _save_outpri_eqwtp
    # PARAMETER (UN=1.,CAS=1./2.997925D18,EQWC=1.19917D22)
    un = 1.
    cas = 1./2.997925e18
    eqwc = 1.19917e22
    # PARAMETER (PI2=3.141592654/2.)
    pi2 = 3.141592654/2.        # 定义后未使用, 按原文保留
    # DIMENSION FLX(3),REL(3),ALX(3)
    flx = np.zeros(4)
    rel = np.zeros(4)
    alx = np.zeros(4)

    if C.IFWIN <= 0:
        # output of synthetic spectrum on unit 7
        for ij in range(3, C.NFREQ):    # DO IJ=3,NFREQ-1
            flam = C.FLUX[ij]*C.FREQ[ij]*C.FREQ[ij]*cas
            # 701 FORMAT(F12.5,1PE15.5)
            write_line(7, f"{C.WLAM[ij]:12.5f}{flam:15.5e}")

        # output of the continuum flux on unit 17
        flam = C.FLUX[1]*C.FREQ[1]*C.FREQ[1]*cas
        write_line(17, f"{C.WLAM[1]:12.5f}{flam:15.5e}")
        if C.IBLANK == C.NBLANK:
            flam = C.FLUX[C.NFREQ]*C.FREQ[C.NFREQ]*C.FREQ[C.NFREQ]*cas
            write_line(7, f"{C.WLAM[C.NFREQ]:12.5f}{flam:15.5e}")
            flam = C.FLUX[2]*C.FREQ[2]*C.FREQ[2]*cas
            write_line(17, f"{C.WLAM[2]:12.5f}{flam:15.5e}")
    else:
        for ij in range(1, C.NFROBS + 1):
            flam = C.FLUX[ij]*C.FRQOBS[ij]*C.FRQOBS[ij]*cas*0.5
            flam = max(flam, 1.e-40)
            write_line(7, f"{C.WLOBS[ij]:12.5f}{flam:15.5e}")

    # unit 6 and 16 outputs
    if C.IPRIN < 3:
        return
    if C.IPRIN >= 3:
        # 600 FORMAT(/' EMERGENT RADIATION'/' ------------------'/)
        print()
        print(' EMERGENT RADIATION')
        print(' ------------------')
        print()
        # 601 FORMAT(3('   LAMBDA  LOG HLAM    REL')/)
        print('   LAMBDA  LOG HLAM    REL'
              '   LAMBDA  LOG HLAM    REL'
              '   LAMBDA  LOG HLAM    REL')
        print()
    k1 = 0
    eqw = 0.
    eqwp = 0.
    if C.IBLANK == 1:
        _save_outpri_eqwt = 0.
    if C.IBLANK == 1:
        _save_outpri_eqwtp = 0.
    xx = un/(C.FREQ[2] - C.FREQ[1])
    xxx = un/(C.FREQ[1] + C.FREQ[2])/(C.FREQ[1] + C.FREQ[2])
    if C.IFWIN <= 0:
        for ij in range(1, C.NFREQ + 1):
            flam = C.FLUX[ij]*C.FREQ[ij]*C.FREQ[ij]*cas
            cont = ((C.FREQ[ij] - C.FREQ[1])*C.FLUX[2]
                    + (C.FREQ[2] - C.FREQ[ij])*C.FLUX[1])*xx
            re0 = C.FLUX[ij]/cont
            eqw = eqw + (un - re0)*C.W[ij]
            rep = re0
            if rep > un:
                rep = un
            eqwp = eqwp + (un - rep)*C.W[ij]
            k1 = k1 + 1
            flx[k1] = math.log10(flam)
            alx[k1] = C.WLAM[ij]
            rel[k1] = re0
            if k1 == 3 or ij == C.NFREQ:
                # 602 FORMAT(3(2X,F9.3,F8.4,F7.3))
                print(''.join(f"  {alx[i]:9.3f}{flx[i]:8.4f}{rel[i]:7.3f}"
                              for i in range(1, k1 + 1)))
                k1 = 0
    else:
        for ij in range(1, C.NFROBS + 1):
            flam = C.FLUX[ij]*C.FREQ[ij]*C.FREQ[ij]*cas
            cont = ((C.FRQOBS[ij] - C.FREQ[1])*C.FLUX[2]
                    + (C.FREQ[2] - C.FRQOBS[ij])*C.FLUX[1])*xx
            re0 = C.FLUX[ij]/cont
            eqw = eqw + (un - re0)*C.W[ij]
            rep = re0
            if rep > un:
                rep = un
            eqwp = eqwp + (un - rep)*C.W[ij]
            if C.IPRIN > 0:
                k1 = k1 + 1
                flx[k1] = math.log10(flam)
                alx[k1] = C.WLAM[ij]    # 原文此处用 WLAM(而非 WLOBS), 按原文直译
                rel[k1] = re0
                # TODO(port): 原文判断用 IJ.EQ.NFREQ(而非 NFROBS), 按原文直译
                if k1 == 3 or ij == C.NFREQ:
                    print(''.join(f"  {alx[i]:9.3f}{flx[i]:8.4f}{rel[i]:7.3f}"
                                  for i in range(1, k1 + 1)))
                    k1 = 0

    # output of partial equivalent widths on unit 16
    eqw = eqw*eqwc*xxx
    _save_outpri_eqwt = _save_outpri_eqwt + eqw
    eqwp = eqwp*eqwc*xxx
    _save_outpri_eqwtp = _save_outpri_eqwtp + eqwp
    if C.IPRIN > 2:
        #  603 FORMAT(/,'  EQUIVALENT WIDTH THIS SET  =',2F8.1,' mA'/
        #      *            '  EQUIVALENT WIDTH TOTAL     =',2F8.1,' mA'//)
        print()
        print(f"  EQUIVALENT WIDTH THIS SET  ={eqw:8.1f}{eqwp:8.1f} mA")
        print(f"  EQUIVALENT WIDTH TOTAL     ="
              f"{_save_outpri_eqwt:8.1f}{_save_outpri_eqwtp:8.1f} mA")
        print()
        print()
    # 616 FORMAT(2F12.3,4F12.1)
    write_line(16, f"{C.WLAM[1]:12.3f}{C.WLAM[2]:12.3f}{eqw:12.1f}{eqwp:12.1f}"
                   f"{_save_outpri_eqwt:12.1f}{_save_outpri_eqwtp:12.1f}")
    return
