# -*- coding: utf-8 -*-
"""chunk01: synspec54.f 行 1–1115 的逐行直译。

包含：PROGRAM SYNSPEC（→ main）、SUBROUTINE START、SUBROUTINE INITIA、
SUBROUTINE RDATA。
按 CONVENTIONS.md：禁止 import；COMMON 变量一律用 C.名字；数组保持 1 基索引。
"""


# ---------------------------------------------------------------- 本片的局部辅助

def _ld(line):
    """列表导向（自由格式）READ 的分词：逗号视为分隔符, 支持引号字符串。

    引号字符串作为单个 token 返回并去掉引号(如  ' H 1' 'data/h1.dat'
    → [' H 1', 'data/h1.dat'])。TODO(port): 不支持 r*c 重复计数。
    """
    toks = []
    i, n = 0, len(line)
    while i < n:
        c = line[i]
        if c in ' ,':
            i += 1
        elif c == "'":
            j = line.find("'", i + 1)
            if j < 0:
                j = n
            toks.append(line[i + 1:j])
            i = j + 1
        else:
            j = i
            while j < n and line[j] not in ' ,':
                j += 1
            toks.append(line[i:j])
            i = j
    return toks


def _f(tok):
    """列表导向浮点转换，兼容 Fortran 的 D 指数。"""
    return float(str(tok).replace('D', 'e').replace('d', 'e'))


def _l(tok):
    """列表导向逻辑转换：T/.TRUE. 开头为真。"""
    t = str(tok).strip().upper()
    return t.startswith('T') or t.startswith('.T')


# DATA iexp0/0/（RDATA），之后会被修改 → 隐含 SAVE，提升为模块级变量
_save_rdata_iexp0 = 0


# ==================================================================== 主程序

def main():
    """PROGRAM SYNSPEC

C =====================================================================I
C                                                                      I
C Program for evaluting synthetic spectra for a given model atmosphere I
C                                                                      I
C *****************                                                    I
C VERSION SYNSPEC54                                                    I
C *****************                                                    I
C                                                                      I
C Input: the same as input to TLUSTY or TLUSDISK - unit 5              I
C        additional 6 lines of input - unit 55 (proc. START and INIBL0)I
C        chemical composition - unit 56 (if a switch is on in unit 55) I
C        model atmosphere - unit 8  (procedures INPMOD or INKUR)       I
C        line list        - unit 19 (procedure INISET)                 I
C                                                                      I
C Output: diagnostic outprint - unit 6 (several procedures)            I
C         synthetic spectrum  - unit 7 (procedure OUTPRI)              I
C         flux in continuum   - unit 17 (procedure OUTPRI)             I
C         identification table- unit 12 (procedure INIBLA)             I
C         partial equiv.widths- unit 16 (procedure OUTPRI)             I
C         elapsed time        - unit 69 (procedure TIMING - UNIX only) I
C                                                                      I
C      -- if specific intensities are also calculated (set up by the   I
C         input on unit 55), there are two aditional output files:     I
C                                                                      I
C         specific intensities - unit 10                               I
C         specific intensities in continuum - unit 18                  I
C                                                                      I
C      -- in the iron-curtain option (IMODE=-2), there is another      I
C         output file:                                                 I
C         monochromatic opacities - unit 27                            I
C                                                                      I
C     ***  The contents of units 7 and 17 serve as an input to the     I
C          program ROTIN, which performs rotational and instrumental   I
C          ROTIN, which performs rotational and instrumental           I
C          convolutions, and sets up files for a plot.                 I
C                                                                      I
C Basic options: controlled by switch IMODE                            I
C IMODE    =  0 - normal synthetic spectrum                            I
C                 (ie. identification table + emergent flux)           I
C          =  1 - detailed profiles of a few individual lines          I
C          =  2 - emergent flux in the continuum (without the          I
C                 contribution of lines)                               I
C          = -1 - only identification table, ie. a list of lines which I
C                 contribute to opacity in a given wavelength          I
C                 region, together with their approximate equivalent   I
C                 widths. Synthetic spectrum is not calculated.        I
C          = -2 - the "iron curtain" option, ie. a monochromatic       I
c                 opacity for a homogeneous slab of a given T and n_e  I
C                                                                      I
C ==================================================================== I

    对应 synspec54.f 行 1–174
    """
    # INCLUDE 'PARAMS.FOR' / 'LINDAT.FOR' / 'MODELP.FOR' / 'SYNTHP.FOR' → C.*
    # OPEN(UNIT=12,STATUS='UNKNOWN') / OPEN(UNIT=14,STATUS='UNKNOWN')
    # 未指定 FILE，Fortran 约定连接 fort.<unit>
    open_unit(12, 'fort.12', 'w')  # TODO(port): 假定写模式；Fortran STATUS='UNKNOWN' 在首次 I/O 时才创建文件
    open_unit(14, 'fort.14', 'w')  # TODO(port): 同上

    # INITIALIZATION - INPUT OF BASIC PARAMETERS AND MODEL ATMOSPHERE
    start()
    if C.IFEOS > 0:
        C.IMODE = -3
    if C.IBFAC > 1:
        lte0 = C.LTE
        C.LTE = True
    inext = 0  # TODO(port): Fortran 中 inext 未初始化即传入 INGRID
    if C.IMODE >= -2 and C.IFEOS <= 0:
        if C.INMOD > 0:
            inpmod()
        if C.INMOD == 0:
            inkur()
        if C.ICHANG != 0:
            change()
        if C.IBFAC > 1:
            inpbf()
            C.LTE = lte0
        if C.IFWIN > 1:
            setwin()
    else:
        # ingrid 给标量哑元 inext 赋值 → 按约定解包接收全部标量哑元
        _mode, inext, _igrd = ingrid(0, inext, 0)

    inibl0()
    inimod()
    tint()

    C.IMODE0 = C.IMODE
    if C.IMODE0 == -4:
        C.IMODE = 2
    igrd = 0
    # 标号 1：不透明度网格（IMODE0<-2 时的网格点）循环
    while True:  # 对应 Fortran 标号 1
        if C.IMODE0 <= -3 and C.IFEOS <= 0:
            inibl1(igrd)
        if C.IFMOL > 0:
            molini()
            if C.IFEOS != 0:
                eospri()

        # zero abundances for selected species (if required)
        if C.IMODE0 <= -3:
            abnchn(1)

        C.IBLANK = 0
        C.NXTSET = 0
        if C.IFMOL > 0 and C.IMODE < 2:
            for ilist in range(1, C.NMLIST + 1):
                C.NXTSEM[ilist] = 0
                C.INACTM[ilist] = 0
                C.NLINMT[ilist] = 0

        if C.IFEOS <= 0:
            if C.IMODE < 2:
                inilin()

            if C.IFMOL > 0 and C.IMODE < 2:
                for ilist in range(1, C.NMLIST + 1):
                    if C.IMODE == -3 and C.TEMP[1] < C.TMLIM[ilist]:
                        inmoli(ilist)
                    if C.IMODE >= -2 and C.IMODE <= 1:
                        inmoli(ilist)

        # 标号 5：线表/分子线表更新后的重入点
        while True:  # 对应 Fortran 标号 5
            # ACTUAL CALCULATION OF THE SYNTHETIC SPECTRUM
            if C.IFEOS > 0:
                break  # GO TO 30
            _go5 = False
            # 标号 10：IBLANK（波长区段）循环
            while True:  # 对应 Fortran 标号 10
                C.IBLANK = C.IBLANK + 1
                _skip_outpri = False
                if C.IFWIN <= 0:
                    resolv()
                    if C.IMODE0 < 0:
                        _skip_outpri = True  # GO TO 20（跳过 RTE/RTECD 与 OUTPRI）
                    else:
                        if C.IFREQ <= 10 and C.INMOD <= 1:
                            rtecd()
                        else:
                            rte()
                else:
                    resolw()
                if not _skip_outpri:
                    outpri()
                # 20 CONTINUE
                if ((C.IMODE >= 0 and C.IMODE != 7 and C.IPRIN >= 1)
                        or (C.IMODE < 0 and C.IPRIN >= 2)):
                    idtab()
                    if C.IFMOL > 0:
                        idmtab()
                if C.IBLANK < C.NBLANK:
                    continue  # GO TO 10
                if C.NXTSET == 1 and C.IRLIST == 0:
                    if C.IMODE < 2:
                        inilin()
                    _go5 = True
                    break  # GO TO 5
                if C.IFMOL > 0 and C.IMODE < 2 and C.IRLIST > 0:
                    for ilist in range(1, C.NMLIST + 1):
                        if C.NXTSEM[ilist] == 1 and C.INACTM[ilist] == 0:
                            inmoli(ilist)
                            C.IBLANK = 0
                            _go5 = True
                            break  # GO TO 5
                    if _go5:
                        break
                break  # 顺序落入标号 30
            if not _go5:
                break  # 落入标号 30
            # _go5 为真 → GO TO 5（继续本层 while）

        # 30 CONTINUE
        if C.IMODE0 < -2:
            # ingrid 给标量哑元 inext 赋值 → 按约定解包接收
            _mode, inext, igrd = ingrid(1, inext, igrd)
            igrd = igrd + 1
            # call timing(1,igrd)  —— 原代码已注释，保留注释
            if inext > 0:
                continue  # GO TO 1
        break
    if C.IMODE0 <= -3 and C.IFEOS <= 0:
        fingrd()
    timing(2, C.IBLANK)
    return  # END


# ==================================================================== START

def start():
    """SUBROUTINE START
    ================

    General input and initialization procedure

    common/quasun/nunalp,nunbet,nungam,nunbal

    ------------------------------------------------
    Additional basic input parameters - from unit 55
    ------------------------------------------------

    IMODE     =  0 - normal synthetic spectrum
              =  1 - detailed profiles of a few individual lines
              =  2 - emergent flux in the continuum (without the
                     contribution of lines)
              = -1 - identification table, ie. a list of lines which
                     contribute to opacity in a given wavelength
                     region, together with their approximate equivalent
                     widths. Synthetic spectrum is not calculated.
              = -2 - the "iron curtain" option, ie. a monochromatic
                     opacity for a homogeneous slab of a given T and n_e

    IDSTD      - index of the "standard depth" (ie the depth at which
                 the continuum optical depth is of the order of unity)
                 (for detailed explanation see the code TLUSTY)

    IPRIN      - determines the amount of output:
               =0 - standard output:
                    condensed output on unit 6 (basics + error messages),
                    no output on unit 96 (depths of formation);
                    normal output on 16 (equivalent widths);
                    normal output on 12 (identification table)
               >0 - more output:
                    =1 - emergent flux on unit 6, no unit 96
                    =2 - identification table + flux on unit 6, no unit 96
                    =3 - as before, plus unit 96 (depths of formation);
                    =4 - as before, plus unit 97 (contribution functions);
               <0 - less output:
                    =-1 - no output on unit 16
                    =-2 - no output on units 16 and 12

    INMOD      = 0  -  input model atmosphere as a Kurucz model
                       (read by procedure INKUR)
               = 1  -  input model atmosphere is a model calculated
                       by the program TLUSTY
                       (read by procedure INPMOD)
               = 2  -  input model is a model of the vertical structure
                       of one ring of an accretion disk
    INTRPL     - switch indicating whether the input model has to be
                 interpolated to the present depth scale;
                 for details see procedure INPMOD
    ICHANG     - switch indicating whether the populations from the
                 input model have to be updated;
                 for details see procedure CHANGE
    ICHEMC     - switch indicating that new chemical composition will
                 be read from unit 56
    IOPHLI     - switch for treatment the Lyman line wings -see LYMLIN

    对应 synspec54.f 行 181–287
    """
    C.IFWIN = 0
    C.nunalp = 0
    C.nunbet = 0
    C.nungam = 0
    C.nunbal = 0
    C.IUNITM[1] = 20
    C.NMLIST = 0
    C.NDSTEP = 0
    if C.IFEOS <= 0:
        # READ(55,*,END=3) ... 三组；任一读遇 END/ERR 跳到标号 3
        try:
            _w = _ld(read_line(55))
            C.IMODE = int(_w[0])
            C.IDSTD = int(_w[1])
            C.IPRIN = int(_w[2])
            _w = _ld(read_line(55))
            C.INMOD = int(_w[0])
            C.INTRPL = int(_w[1])
            C.ICHANG = int(_w[2])
            C.ICHEMC = int(_w[3])
            _w = _ld(read_line(55))
            C.IOPHLI = int(_w[0])
            C.nunalp = int(_w[1])
            C.nunbet = int(_w[2])
            C.nungam = int(_w[3])
            C.nunbal = int(_w[4])
        except (EOFError, ValueError, IndexError):
            pass  # 标号 3：END=/ERR= 跳转至此
    if C.IMODE < -90:
        C.IMODE = -C.IMODE - 100
        C.IFWIN = 1
    if C.IMODE > 5:
        C.IMODE = C.IMODE - 10
        C.IFMOL = 1
        C.NMLIST = 1
        C.IUNITM[1] = 20
    # disabling an old option
    C.IOPHLI = 0

    # standard initialization
    initia()

    # if needed, read tables with data for quasimolecular satellites of
    # Lyman alpha, beta, gamma, and Balmer alpha
    getlal()

    if C.IMODE < -1:
        C.ND = 1
        C.IDSTD = 1
    if C.INMOD > 0 and C.INTRPL > 0:
        # READ(55,*) (DM(I),I=1,ND)
        _w = _ld(read_line(55))
        for i in range(1, C.ND + 1):
            C.DM[i] = _f(_w[i - 1])
    return


# ==================================================================== INITIA

def initia():
    """SUBROUTINE INITIA
    =================

    driver for input and initializations

    对应 synspec54.f 行 294–632
    """
    # PARAMETER (WI1=911.753578, WI2=227.837832)  —— 本例程内未使用，原样保留
    WI1 = 911.753578
    WI2 = 227.837832
    # CHARACTER*4 TYPION(MIOEX),TYPIOI  —— TYPION 为局部字符数组（1 基）
    typion = [''] * (MIOEX + 1)
    # DATA IGLE/.../ IGMN/.../ IGFE/.../ IGNI/.../  —— DATA 初始化且不再修改（1 基，索引 0 为填充）
    igle = [0, 2, 1, 2, 1, 6, 9, 4, 9, 6, 1, 2, 1, 6, 9, 4, 9, 6, 1]
    igmn = [0, 2, 1, 2, 1, 6, 9, 4, 9, 6, 1, 2, 1, 6, 9, 4, 9, 6, 1,
            10, 21, 28, 25, 6, 7, 6]
    igfe = [0, 2, 1, 2, 1, 6, 9, 4, 9, 6, 1, 2, 1, 6, 9, 4, 9, 6, 1,
            10, 21, 28, 25, 6, 25, 30, 25]
    igni = [0, 2, 1, 2, 1, 6, 9, 4, 9, 6, 1, 2, 1, 6, 9, 4, 9, 6, 1,
            10, 21, 28, 25, 6, 25, 28, 21, 10, 21]
    blnk = ' '  # DATA BLNK /' '/

    readbf()

    # ------------------------------------
    # Basic input parameters - atmospheres
    # ------------------------------------
    if C.INMOD <= 1:
        # READ(IBUFF,*) TEFF,GRAV
        _w = _ld(read_line(IBUFF))
        C.TEFF = _f(_w[0])
        C.GRAV = _f(_w[1])
    elif C.INMOD == 2:
        # ------------------------------
        # Basic input parameters - disks
        # ------------------------------
        # READ(IBUFF,*) DISPAR  —— DISPAR 未在任何 COMMON 中声明，按局部标量处理
        _w = _ld(read_line(IBUFF))
        dispar = _f(_w[0])

    # ----------------------------
    # other basic input parameters
    # ----------------------------
    # READ(IBUFF,*) LTE,LTGREY  —— LTGREY 为局部逻辑变量
    _w = _ld(read_line(IBUFF))
    C.LTE = _l(_w[0])
    ltgrey = _l(_w[1])
    # READ(IBUFF,*) FINSTD  —— 局部 CHARACTER*20
    finstd = _ld(read_line(IBUFF))[0]
    nstpar(finstd)

    # ----------------------------
    # Frequency points and weights
    # ----------------------------
    # READ(IBUFF,*) NFREAD
    nfread = int(_ld(read_line(IBUFF))[0])
    njread = nfread

    if njread < 0:
        njread = -njread
        C.NFREQC = njread
        for ij in range(1, njread + 1):
            # READ(IBUFF,*) FREQEXP  —— FREQEXP 读出后未再使用（原样保留）
            freqexp = _f(_ld(read_line(IBUFF))[0])
    else:
        C.NFREQC = njread

    # WRITE(6,601) TEFF,GRAV
    #  601 FORMAT(31X,'*******************************************'/
    #     * 31X,'I',41X,'I'/
    #     * 31X,'I   S Y N T H E T I C   S P E C T R U M   I'/
    #     * 31X,'I',41X,'I'/
    #     * 31X,'I',8X,'FOR MODEL ATMOSPHERE WITH',8X,'I'/
    #     * 31X,'I',41X,'I'/
    #     * 31X,'I',14X,'TEFF  =',F7.0,13X,'I'/
    #     * 31X,'I',14X,'LOG G =',F7.2,13X,'I'/
    #     * 31X,'I',41X,'I'/
    #     * 31X,'*******************************************')
    print(' ' * 31 + '*******************************************')
    print(' ' * 31 + 'I' + ' ' * 41 + 'I')
    print(' ' * 31 + 'I   S Y N T H E T I C   S P E C T R U M   I')
    print(' ' * 31 + 'I' + ' ' * 41 + 'I')
    print(' ' * 31 + 'I' + ' ' * 8 + 'FOR MODEL ATMOSPHERE WITH' + ' ' * 8 + 'I')
    print(' ' * 31 + 'I' + ' ' * 41 + 'I')
    print(' ' * 31 + 'I' + ' ' * 14 + 'TEFF  =' + f'{C.TEFF:7.0f}' + ' ' * 13 + 'I')
    print(' ' * 31 + 'I' + ' ' * 14 + 'LOG G =' + f'{C.GRAV:7.2f}' + ' ' * 13 + 'I')
    print(' ' * 31 + 'I' + ' ' * 41 + 'I')
    print(' ' * 31 + '*******************************************')

    # ----------------------------------------------------
    #     turbulent velocities
    # ----------------------------------------------------
    if C.VTB < 1.e3:
        C.VTB = C.VTB * 1.e5
    for id in range(1, C.ND + 1):
        C.VTURB[id] = C.VTB

    # ----------------------------------------------------
    # Input parameters for explicit and non-explicit atoms
    # ----------------------------------------------------
    #
    #     Input parameters are read by procedure STATE
    #     (see description there)
    state0(1)
    id = 1
    if C.IPRIN >= 1:
        # WRITE(6,607) YTOT(ID),WMY(ID),WMM(ID)
        #  607 FORMAT(///' YTOT   =',F11.5/' WMY    =',1PE15.5/' WMM    =',E15.5)
        print()
        print()
        print(f' YTOT   ={C.YTOT[id]:11.5f}')
        print(f' WMY    ={C.WMY[id]:15.5E}')
        print(f' WMM    ={C.WMM[id]:15.5E}')
    for i in range(1, MLEVEL + 1):
        C.ILK[i] = 0
        C.iexpl[i] = 0
        C.iltot[i] = 0

    # --------------------------------------------------------------
    # Input of parameters for explicit ions, levels, and transitions
    # --------------------------------------------------------------
    ilev = 0
    iatlst = 0
    ion = 0
    ia = 0
    C.IUNIT = 34
    C.NATOM = 0
    # WRITE(6,613)
    #  613 FORMAT(//' EXPLICIT IONS INCLUDED'/
    #     *            ' ----------------------'//
    #     *  ' ION     N0    N1    NK    IZ'/)
    print()
    print(' EXPLICIT IONS INCLUDED')
    print(' ----------------------')
    print()
    print(' ION     N0    N1    NK    IZ')
    print()
    nki = 0  # TODO(port): Fortran 中 NKI 未初始化；若首次 READ 即 END=20 则使用此值
    while True:  # 对应 Fortran 标号 10
        # READ(IBUFF,*,END=20,ERR=20) IATII,IZII,NLEVSI,ILASTI,ILVLIN,
        #            NONSTD,TYPIOI,FILEI
        try:
            _w = _ld(read_line(IBUFF))
            iatii = int(_w[0])
            izii = int(_w[1])
            nlevsi = int(_w[2])
            ilasti = int(_w[3])
            ilvlin = int(_w[4])
            nonstd = int(_w[5])
            typioi = _w[6]
            filei = _w[7]
        except (EOFError, ValueError, IndexError):
            break  # END=20 / ERR=20 → GO TO 20
        if ilasti == 0:
            ion = ion + 1
            C.IATI[ion] = iatii
            C.IZI[ion] = izii
            C.NLEVS[ion] = nlevsi
            typion[ion] = typioi
            C.FIDATA[ion] = filei
            C.NLLIM[ion] = ilvlin
            C.ILIMITS[ion] = -1
            C.IUPSUM[ion] = 0
            C.FIBFCS[ion] = blnk
            modeff = 1
            nff = 0
            if C.IATI[ion] == 1 and C.IZI[ion] == 0:
                C.IUPSUM[ion] = -100
                modeff = 2
            if C.IATI[ion] == 2 and C.IZI[ion] == 1:
                modeff = 2
            if nonstd >= 10:
                # WRITE(*,*)'INITIA: QUANTUM NUMBERS AND ENERGY LIMITS WILL'
                # WRITE(*,*)'        BE IGNORED FOR ION ',IATII,'    ',IZII
                print('INITIA: QUANTUM NUMBERS AND ENERGY LIMITS WILL')
                print('        BE IGNORED FOR ION ', iatii, '    ', izii)
                C.ILIMITS[ion] = 0
                nonstd = nonstd - 10
            if nonstd > 0:
                # READ(IBUFF,*) IUPSUM(ION),ICUP,MODEFF,NFF
                _w = _ld(read_line(IBUFF))
                C.IUPSUM[ion] = int(_w[0])
                icup = int(_w[1])
                modeff = int(_w[2])
                nff = int(_w[3])
            elif nonstd < 0:
                # READ(IBUFF,*) ifil1,ifil2,FIODF1(ION),FIODF2(ION),FIBFCS(ION)
                _w = _ld(read_line(IBUFF))
                ifil1 = int(_w[0])
                ifil2 = int(_w[1])
                C.FIODF1[ion] = _w[2]
                C.FIODF2[ion] = _w[3]
                C.FIBFCS[ion] = _w[4]
                if not feq(C.FIBFCS[ion], ' '):
                    C.IUNIT = C.IUNIT + 1
                    C.INBFCS[ion] = C.IUNIT
                C.IUPSUM[ion] = 1

            if C.IATI[ion] == iatlst:
                C.NFIRST[ion] = ilev
            else:
                C.NFIRST[ion] = ilev + 1
                iatlst = C.IATI[ion]
                ia = C.IATEX[iatlst]
                C.N0A[ia] = C.NFIRST[ion]
                C.NATOM = max(C.NATOM, ia)
            C.NLAST[ion] = C.NFIRST[ion] + C.NLEVS[ion] - 1
            C.NNEXT[ion] = C.NLAST[ion] + 1
            ilev = C.NNEXT[ion]
            C.IZ[ion] = C.IZI[ion] + 1
            if nff > 0:
                C.FF[ion] = EH / H * C.IZ[ion] * C.IZ[ion] / nff / nff

            n0i = C.NFIRST[ion]
            n1i = C.NLAST[ion]
            nki = C.NNEXT[ion]
            C.IFREE[ion] = modeff
            for ii in range(n0i, n1i + 1):
                C.IEL[ii] = ion
                C.IATM[ii] = ia
            C.ILK[nki] = ion
            C.IATM[nki] = ia

            if C.NUMAT[ia] == 1:
                C.IATH = ia
                if C.IZ[ion] == 1:
                    C.IELH = ion
                if C.IZ[ion] == 0:
                    C.IELHM = ion
            if C.NUMAT[ia] == 2:
                C.IATHE = ia
                if C.IZ[ion] == 1:
                    C.IELHE1 = ion
                if C.IZ[ion] == 2:
                    C.IELHE2 = ion

            if C.IPRIN >= 0:
                # WRITE(6,614) TYPION(ION),N0I,N1I,NKI,IZ(ION)
                #  614 FORMAT(A4,4I6)
                print(f'{str(typion[ion]):4s}{n0i:6d}{n1i:6d}{nki:6d}{C.IZ[ion]:6d}')

        elif ilasti > 0:
            C.ENION[ilev] = 0.
            C.G[ilev] = ilasti
            C.NQUANT[ilev] = 1
            C.TYPLEV[ilev] = typioi
            C.ifwop[ilev] = 0
            C.IEL[ilev] = ion
            C.NKA[ia] = C.NNEXT[ion]
            if ilasti == 1 and iatii > izii:
                if iatii < 25:
                    C.G[ilev] = igle[iatii - izii]
                elif iatii == 25:
                    C.G[ilev] = igmn[iatii - izii]
                elif iatii == 26:
                    C.G[ilev] = igfe[iatii - izii]
                elif iatii == 28:
                    C.G[ilev] = igni[iatii - izii]
        else:
            break  # GO TO 20
        # GO TO 10 → 继续循环
    # 20 CONTINUE
    C.NION = ion
    C.NLEVEL = nki

    if C.IATH > 0:
        C.N0H = C.N0A[C.IATH]
        C.N1H = C.NLAST[C.IELH]
        C.NKH = C.NNEXT[C.IELH]
        C.N0HN = C.NFIRST[C.IELH]
        C.N0M = 0
        if C.IELHM > 0:
            C.N0M = C.NFIRST[C.IELHM]
            C.IOPHMI = 0
    else:
        C.N0H = 0
        C.N1H = 0
        C.NKH = 0
        C.N0HN = 0

    if C.IPRIN >= 1:
        # WRITE(6,603) INMOD,ND,IDSTD,INTRPL,ICHANG,NATOM,NION,NLEVEL,IELH,IELHM,IATH
        #  603 FORMAT(//' BASIC INPUT PARAMETERS'/
        #     *         ' ----------------------'/
        #     *            ' INMOD  =',I5/ ... /' IATH   =',I5)
        print()
        print(' BASIC INPUT PARAMETERS')
        print(' ----------------------')
        print(f' INMOD  ={C.INMOD:5d}')
        print(f' ND     ={C.ND:5d}')
        print(f' IDSTD  ={C.IDSTD:5d}')
        print(f' INTRPL ={C.INTRPL:5d}')
        print(f' ICHANG ={C.ICHANG:5d}')
        print(f' NATOM  ={C.NATOM:5d}')
        print(f' NION   ={C.NION:5d}')
        print(f' NLEVEL ={C.NLEVEL:5d}')
        print(f' IELH   ={C.IELH:5d}')
        print(f' IELHM  ={C.IELHM:5d}')
        print(f' IATH   ={C.IATH:5d}')

    # -----------------------------------------
    # Parameters for individual explicit levels
    # -----------------------------------------
    C.IMER = 0
    C.ITR = 0
    C.IC = 0
    C.IL = 0
    C.IP = 0

    for ion in range(1, C.NION + 1):
        rdata(ion)
        nff = C.NQUANT[C.NLAST[ion]] + 1
        if nff > 0:
            C.FF[ion] = EH / H * C.IZ[ion] * C.IZ[ion] / nff / nff

    if C.IPRIN >= 1:
        # WRITE(6,615)
        #  615 FORMAT(//' EXPLICIT ENERGY LEVELS INCLUDED'/
        #     *            ' -------------------------------'//
        #     * ' NO.    LEVEL    ION   ION.EN.(ERG)        G   NQUANT',
        #     * '  IEL  ILK  IAT'/)
        print()
        print(' EXPLICIT ENERGY LEVELS INCLUDED')
        print(' -------------------------------')
        print()
        print(' NO.    LEVEL    ION   ION.EN.(ERG)        G   NQUANT  IEL  ILK  IAT')
        print()
    for i in range(1, C.NLEVEL + 1):
        if C.IPRIN >= 1:
            # WRITE(6,616) I,TYPLEV(I),TYPION(IEL(I)),ENION(I),G(I),
            #              NQUANT(I),IEL(I),ILK(I),IATM(I)
            #  616 FORMAT(I4,2X,A10,A4,1PE15.7,0PF10.2,4I5)
            print(f'{i:4d}  {str(C.TYPLEV[i]):10s}{str(typion[C.IEL[i]]):4s}'
                  f'{C.ENION[i]:15.7E}{C.G[i]:10.2f}{C.NQUANT[i]:5d}'
                  f'{C.IEL[i]:5d}{C.ILK[i]:5d}{C.IATM[i]:5d}')

    # -----------------------------------------
    # Input parameters for additional opacities
    # -----------------------------------------
    if C.IPRIN >= 0:
        # WRITE(6,605) IOPHMI,IOPH2P,IOPHEM,IOPCH,IOPOH,IOPH2M,IOH2H2,IOH2HE,
        #              IOH2H1,IOHHE,IRSCT,IRSCH2,IRSCHE,IOPHLI
        #  605 FORMAT(//' ADDITIONAL OPACITY SOURCES'/ ...)
        print()
        print(' ADDITIONAL OPACITY SOURCES')
        print(' --------------------------')
        print(f' IOPHMI  (H-  OPACITY IN LTE)       ={C.IOPHMI:3d}')
        print(f' IOPH2P  (H2+  OPACITY)             ={C.IOPH2P:3d}')
        print(f' IOPHEM  (HE- B-F AND F-F)          ={C.IOPHEM:3d}')
        print(f' IOPCH   (CH OPACITY)               ={C.IOPCH:3d}')
        print(f' IOPOH   (OH OPACITY)               ={C.IOPOH:3d}')
        print(f' IOPH2M  (H2- OPACITY)              ={C.IOPH2M:3d}')
        print(f' IOH2H2  (CIA H2-H2 OPACITY         ={C.IOH2H2:3d}')
        print(f' IOH2HE  (CIA H2-He OPACITY         ={C.IOH2HE:3d}')
        print(f' IOH2H1  (CIA H2-H  OPACITY         ={C.IOH2H1:3d}')
        print(f' IOHHE   (CIA H-He OPACITY          ={C.IOHHE:3d}')
        print(f' IRSCT   (RAYLEIGH SCAT. ON H I)    ={C.IRSCT:3d}')
        print(f' IRSCH2  (RAYLEIGH SCAT. ON H2      ={C.IRSCH2:3d}')
        print(f' IRSCHE  (RAYLEIGH SCAT. ON HE I)   ={C.IRSCHE:3d}')
        print(f' IOPHLI  (LYMAN LINES WINGS)        ={C.IOPHLI:3d}')

    if C.VTB < 1.e3:
        C.VTB = C.VTB * 1.e5
    for id in range(1, C.ND + 1):
        C.VTURB[id] = C.VTB
    # WRITE(6,608) VTB*1.E-5
    #  608 FORMAT(//' TURBULENT VELOCITY  -  DEPTH-INDEPENDENT   VTURB =',
    #     * 1PE10.3,'  KM/S'/' ------------------'/)
    print()
    print(f' TURBULENT VELOCITY  -  DEPTH-INDEPENDENT   VTURB ={C.VTB * 1.e-5:10.3E}  KM/S')
    print(' ------------------')
    print()
    for i in range(1, C.ND + 1):
        C.VTURB[i] = C.VTURB[i] * C.VTURB[i]

    return


# ==================================================================== RDATA

def rdata(ion):
    """SUBROUTINE RDATA(ION)
    =====================

    读入一个电离种的能级、连续跃迁与线跃迁输入参数
    （对应数据文件 FIDATA(ION)）。

    对应 synspec54.f 行 639–1110
    """
    global _save_rdata_iexp0
    # PARAMETER (WI1=911.753578, WI2=227.837832)
    WI1 = 911.753578
    WI2 = 227.837832
    # PARAMETER (T15=1.D-15)  —— 未使用，原样保留
    T15 = 1.e-15
    # PARAMETER (ECONST=  5.03411142E15)
    ECONST = 5.03411142e15
    # PARAMETER (MCFIT=10)
    MCFIT = 10
    # dimension CTEMP(MCFIT),CRATE(MCFIT)  —— 1 基局部数组
    ctemp = np.zeros(MCFIT + 1)
    crate = np.zeros(MCFIT + 1)
    # data iexp0/0/  —— 之后被修改，隐含 SAVE → 模块级 _save_rdata_iexp0

    # IUNIT=94
    C.IUNIT = 94
    # OPEN(IUNIT,FILE=FIDATA(ION),STATUS='OLD')
    open_unit(C.IUNIT, str(C.FIDATA[ion]).strip(), 'r')

    #     read the first record - a label for the energy level input
    # READ(IUNIT,501) A
    #  501 FORMAT(A1)
    a = (read_line(C.IUNIT) + ' ')[0]

    #   -----------------------------------------------------
    #   input parameters for explicit energy levels
    #   -----------------------------------------------------
    #
    #   If ILIMITS(ION) < 0, the program finds out whether energy and
    #   quantum numbers are included in the input data files
    ie = 0  # TODO(port): Fortran 中 IE 在能级循环外沿用上次循环的遗留值；若循环未执行则未定义
    if C.ILIMITS[ion] < 0:
        # READ(IUNIT,'(1000A)')CADENA
        _fh = funits[C.IUNIT]
        _pos = _fh.tell()
        cadena = read_line(C.IUNIT).ljust(1000)  # TODO(port): (1000A) 格式，右侧补空格至 1000 字符
        # BACKSPACE(IUNIT)：普通文件回退一行
        _fh.seek(_pos)  # TODO(port): 用 tell/seek 模拟 BACKSPACE
        # count_words（行 1257）给标量哑元 n 赋值 → 按约定解包接收
        now = 0
        cadena, now = count_words(cadena, now)
        if now < 14:
            C.ILIMITS[ion] = 0
        else:
            C.ILIMITS[ion] = 1

    #   Standard format: ENION(I),G(I),NQUANT(I),TYPLEV(I),ifwop(i)
    if C.ILIMITS[ion] == 0:

        # 注意：IL 属于 COMMON/STRPAR/，Fortran 中 DO 循环直接改写 COMMON 变量
        for C.IL in range(1, C.NLEVS[ion] + 1):
            i = C.IL + C.NFIRST[ion] - 1
            ie = C.IEL[i]
            n0i = C.NFIRST[ie]
            nki = C.NNEXT[ie]
            ia = C.NUMAT[C.IATM[n0i]]
            if C.isemex[ia] <= 1:
                _save_rdata_iexp0 = _save_rdata_iexp0 + 1
                C.iexpl[i] = _save_rdata_iexp0
                C.iltot[_save_rdata_iexp0] = i
                # write(6,671) il,i,ia,ion,isemex(ia),iexp0,iltot(iexp0)  —— 原代码已注释
                if C.IL == C.NLEVS[ion]:
                    if nki == C.NKA[C.IATM[i]]:
                        _save_rdata_iexp0 = _save_rdata_iexp0 + 1
                        C.iexpl[nki] = _save_rdata_iexp0
                        C.iltot[_save_rdata_iexp0] = nki
                        # write(6,671) il+1,nki,ia,ion,isemex(ia),iexp0,iltot(iexp0)  —— 原代码已注释
                #  671 format('il,i,ia,ion,isem,iexp,iltot',7i4)  —— 原代码已注释
            iq = i - n0i + 1
            x = float(iq * iq)
            C.ifwop[i] = 0
            izz = C.IZ[ie]
            # READ(IUNIT,*) ENION(I),G(I),NQUANT(I),TYPLEV(I),ifwop(i)
            _w = _ld(read_line(C.IUNIT))
            C.ENION[i] = _f(_w[0])
            C.G[i] = _f(_w[1])
            C.NQUANT[i] = int(_w[2])
            C.TYPLEV[i] = _w[3]
            C.ifwop[i] = int(_w[4])
            if C.ifwop[i] < 0 and i != C.NLAST[ie]:
                quit('conflict in negative ifwop')
            if C.ifwop[i] >= 2:
                C.ifwop[i] = 0
            if i < nki:
                e = C.ENION[i]
                e0 = e
                if e < 0.:
                    e = -e
                    e0 = e
                if e == 0.:
                    # if(izz.le.2) then  —— 原代码已注释，实际条件为 izz.le.-2
                    if izz <= -2:
                        w0 = WI1
                        if izz == 2:
                            w0 = WI2
                        wl0 = w0 * x
                        if wl0 > 2000.:
                            alm = 1.e8 / (wl0 * wl0)
                            xn1 = 64.328 + 29498.1 / (146. - alm) + 255.4 / (41. - alm)
                            wl0 = wl0 / (xn1 * 1.e-6 + 1.0)
                        e0 = H * CL * 1.e8 / wl0
                    else:
                        e0 = EH * izz * izz / x
                if e > 1.e-7 and e < 100.:
                    e0 = 1.6018e-12 * e
                if e > 100. and e < 1.e7:
                    e0 = 1.9857e-16 * e
                if e > 1.e7:
                    e0 = H * e
                if C.ENION[i] >= 0.:
                    C.ENION[i] = e0
                else:
                    C.ENION[i] = -e0
                if C.G[i] == 0.:
                    C.G[i] = 2.0 * x
                if C.NQUANT[i] == 0:
                    C.NQUANT[i] = iq
            else:
                # if(modref.ge.0) nref(iatm(i))=nka(iatm(i))  —— 原代码已注释
                if C.G[i] == 0. and nki == C.NKA[C.IATM[i]]:
                    C.G[i] = 1.
            if C.ifwop[i] < 0:
                C.ENION[i] = 0.
                C.FF[ie] = 0.
                C.IMER = C.IMER + 1
                C.IMRG[i] = C.IMER
                C.IIMER[C.IMER] = i
            C.fropc[i] = 0.

    #     Upgraded format including limits for energies, and quantum numbers
    else:

        for C.IL in range(1, C.NLEVS[ion] + 1):
            i = C.IL + C.NFIRST[ion] - 1
            ie = C.IEL[i]
            n0i = C.NFIRST[ie]
            nki = C.NNEXT[ie]
            ia = C.NUMAT[C.IATM[n0i]]
            if C.isemex[ia] <= 1:
                _save_rdata_iexp0 = _save_rdata_iexp0 + 1
                C.iexpl[i] = _save_rdata_iexp0
                C.iltot[_save_rdata_iexp0] = i
                if C.IL == C.NLEVS[ion]:
                    if nki == C.NKA[C.IATM[i]]:
                        _save_rdata_iexp0 = _save_rdata_iexp0 + 1
                        C.iexpl[nki] = _save_rdata_iexp0
                        C.iltot[_save_rdata_iexp0] = nki
            iq = i - n0i + 1
            x = float(iq * iq)
            C.ifwop[i] = 0
            izz = C.IZ[ie]
            # READ(IUNIT,*) ENION(I),G(I),NQUANT(I),TYPLEV(I),ifwop(i),frdodf,imodl,
            #   ENION1(I),ENION2(I),SQUANT1(I),SQUANT2(I),
            #   LQUANT1(I),LQUANT2(I),PQUANT1(I),PQUANT2(I)
            _w = _ld(read_line(C.IUNIT))
            C.ENION[i] = _f(_w[0])
            C.G[i] = _f(_w[1])
            C.NQUANT[i] = int(_w[2])
            C.TYPLEV[i] = _w[3]
            C.ifwop[i] = int(_w[4])
            frdodf = _f(_w[5])
            imodl = int(_w[6])
            C.ENION1[i] = _f(_w[7])
            C.ENION2[i] = _f(_w[8])
            C.SQUANT1[i] = _f(_w[9])
            C.SQUANT2[i] = _f(_w[10])
            C.LQUANT1[i] = int(_w[11])
            C.LQUANT2[i] = int(_w[12])
            C.PQUANT1[i] = int(_w[13])
            C.PQUANT2[i] = int(_w[14])
            if C.ifwop[i] < 0 and i != C.NLAST[ie]:
                quit('conflict in negative ifwop')
            if C.ifwop[i] >= 2:
                C.ifwop[i] = 0
            if i < nki:

                # check and, if necessary, transform ENION(I)
                e = C.ENION[i]
                e0 = e
                if e < 0.:
                    e = -e
                    e0 = e
                if e == 0.:
                    # if(izz.le.2) then  —— 原代码已注释，实际条件为 izz.le.-2
                    if izz <= -2:
                        w0 = WI1
                        if izz == 2:
                            w0 = WI2
                        wl0 = w0 * x
                        if wl0 > 2000.:
                            alm = 1.e8 / (wl0 * wl0)
                            xn1 = 64.328 + 29498.1 / (146. - alm) + 255.4 / (41. - alm)
                            wl0 = wl0 / (xn1 * 1.e-6 + 1.0)
                        e0 = H * CL * 1.e8 / wl0
                    else:
                        e0 = EH * izz * izz / x
                if e > 1.e-7 and e < 100.:
                    e0 = 1.6018e-12 * e
                if e > 100. and e < 1.e7:
                    e0 = 1.9857e-16 * e
                if e > 1.e7:
                    e0 = H * e
                if C.ENION[i] >= 0.:
                    C.ENION[i] = e0
                else:
                    C.ENION[i] = -e0

                # check and, if necessary, transform ENION1(I)
                e = C.ENION1[i]
                e0 = e
                if e < 0.:
                    e = -e
                    e0 = e
                if e == 0.:
                    # if(izz.le.2) then  —— 原代码已注释，实际条件为 izz.le.-2
                    if izz <= -2:
                        w0 = WI1
                        if izz == 2:
                            w0 = WI2
                        wl0 = w0 * x
                        if wl0 > 2000.:
                            alm = 1.e8 / (wl0 * wl0)
                            xn1 = 64.328 + 29498.1 / (146. - alm) + 255.4 / (41. - alm)
                            wl0 = wl0 / (xn1 * 1.e-6 + 1.0)
                        e0 = H * CL * 1.e8 / wl0
                    else:
                        e0 = EH * izz * izz / x
                if e > 1.e-7 and e < 100.:
                    e0 = 1.6018e-12 * e
                if e > 100. and e < 1.e7:
                    e0 = 1.9857e-16 * e
                if e > 1.e7:
                    e0 = H * e
                if C.ENION1[i] >= 0.:
                    C.ENION1[i] = e0
                else:
                    C.ENION1[i] = -e0

                # check and, if necessary, transform ENION2(I)
                e = C.ENION2[i]
                e0 = e
                if e < 0.:
                    e = -e
                    e0 = e
                if e == 0.:
                    # if(izz.le.2) then  —— 原代码已注释，实际条件为 izz.le.-2
                    if izz <= -2:
                        w0 = WI1
                        if izz == 2:
                            w0 = WI2
                        wl0 = w0 * x
                        if wl0 > 2000.:
                            alm = 1.e8 / (wl0 * wl0)
                            xn1 = 64.328 + 29498.1 / (146. - alm) + 255.4 / (41. - alm)
                            wl0 = wl0 / (xn1 * 1.e-6 + 1.0)
                        e0 = H * CL * 1.e8 / wl0
                    else:
                        e0 = EH * izz * izz / x
                if e > 1.e-7 and e < 100.:
                    e0 = 1.6018e-12 * e
                if e > 100. and e < 1.e7:
                    e0 = 1.9857e-16 * e
                if e > 1.e7:
                    e0 = H * e
                if C.ENION2[i] >= 0.:
                    C.ENION2[i] = e0
                else:
                    C.ENION2[i] = -e0

                #       Enforce an energy tolerance of 10% when the input files
                #       do not have  any (e.g. pure levels in MODION models)
                if (C.ENION1[i] - C.ENION[i]) / C.ENION[i] < 1e-6:
                    C.ENION1[i] = C.ENION[i] * (1. + C.ERANGE)
                if (C.ENION[i] - C.ENION2[i]) / C.ENION[i] < 1e-6:
                    C.ENION2[i] = C.ENION[i] * (1. - C.ERANGE)

                #       Convert ENION1,ENION2 to cm-1 from the ground level
                #       so they can be directly used in NLTSET
                C.ENION1[i] = (C.ENION[n0i] - C.ENION1[i]) * ECONST
                C.ENION2[i] = (C.ENION[n0i] - C.ENION2[i]) * ECONST

                if C.G[i] == 0.:
                    C.G[i] = 2.0 * x
                if C.NQUANT[i] == 0:
                    C.NQUANT[i] = iq
            else:
                # if(modref.ge.0) nref(iatm(i))=nka(iatm(i))  —— 原代码已注释
                if C.G[i] == 0. and nki == C.NKA[C.IATM[i]]:
                    C.G[i] = 1.
            if C.ifwop[i] < 0:
                # write(*,*)'RDATA:  IFWOP<0 and ILIMITS is not 0'
                print('RDATA:  IFWOP<0 and ILIMITS is not 0')
                # stop
                raise SystemExit
                # STOP 之后的不可达代码（原 Fortran 语句，原样保留）
                C.ENION[i] = 0.
                C.FF[ie] = 0.
                C.IMER = C.IMER + 1
                C.IMRG[i] = C.IMER
                C.IIMER[C.IMER] = i
            C.fropc[i] = 0.

    # ----------------------------------------------------------------------
    #
    #   skip lines if more levels than needed, and skip the continuum transition
    #   label
    #
    # 标号 5：跳行直到 '*' 行
    while True:  # 对应 Fortran 标号 5
        # READ(IUNIT,501) A
        a = (read_line(C.IUNIT) + ' ')[0]
        if feq(a, '*'):
            break  # A.EQ.'*' 退出；否则 GO TO 5
    ii0 = C.NFIRST[ion] - 1
    illim = C.NLLIM[ion] + ii0  # ILLIM 计算后未再使用（原样保留）
    jcorr = 0

    #   -----------------------------------------------------
    #   input parameters for continuum transitions
    #   -----------------------------------------------------
    fropci = 0.0  # TODO(port): Fortran 中 FROPCI 可能沿用上次迭代值；首次迭代未定义
    _goto = None
    while True:  # 对应 Fortran 标号 10
        #     READ(IUNIT,*,END=20,ERR=15) II,JJ,MODE,IFANCY,ICOLIS,
        #                                 IFRQ0,IFRQ1,OSC,CPARAM  —— 原代码已注释
        # READ(IUNIT,'(A100)',END=20) DUM
        try:
            dum = read_line(C.IUNIT)[:100]
        except EOFError:
            _goto = 20  # END=20 → GO TO 20
            break
        # READ(DUM,*,IOSTAT=KSTAT) II,JJ,MODE,IFANCY,ICOLIS,
        #      IFRQ0,IFRQ1,OSC,CPARAM,NCOL  —— 内部文件读
        _w = _ld(dum)
        try:
            ii = int(_w[0])
            jj = int(_w[1])
            mode = int(_w[2])
            ifancy = int(_w[3])
            icolis = int(_w[4])
            ifrq0 = int(_w[5])
            ifrq1 = int(_w[6])
            osc = _f(_w[7])
            cparam = _f(_w[8])
            ncol = int(_w[9])
            kstat = 0
        except (ValueError, IndexError):
            kstat = -1  # TODO(port): IOSTAT 具体错误码未知，仅区分成功/失败
        if kstat != 0:
            # READ(DUM,*,ERR=15) II,JJ,MODE,IFANCY,ICOLIS,IFRQ0,IFRQ1,OSC,CPARAM
            try:
                ii = int(_w[0])
                jj = int(_w[1])
                mode = int(_w[2])
                ifancy = int(_w[3])
                icolis = int(_w[4])
                ifrq0 = int(_w[5])
                ifrq1 = int(_w[6])
                osc = _f(_w[7])
                cparam = _f(_w[8])
                ncol = 0
            except (ValueError, IndexError):
                _goto = 15  # ERR=15 → GO TO 15
                break
        if ncol != 0:
            for iic in range(1, ncol + 1):
                # READ(IUNIT,*) ITYPE, NCTEMP
                _w = _ld(read_line(C.IUNIT))
                itype = int(_w[0])
                nctemp = int(_w[1])
                # READ(IUNIT,*) (CTEMP(IFIT),IFIT=1,NCTEMP)
                _w = _ld(read_line(C.IUNIT))
                for ifit in range(1, nctemp + 1):
                    ctemp[ifit] = _f(_w[ifit - 1])
                # READ(IUNIT,*) (CRATE(IFIT),IFIT=1,NCTEMP)
                _w = _ld(read_line(C.IUNIT))
                for ifit in range(1, nctemp + 1):
                    crate[ifit] = _f(_w[ifit - 1])

        if ii == 0:
            if jj == 0:
                _goto = 30  # GO TO 30
                break
            ii0 = jj - 1
            continue  # GO TO 10
        if abs(mode) > 100:
            # READ(IUNIT,*) FR0INP
            fr0inp = _f(_ld(read_line(C.IUNIT))[0])
        if abs(mode) == 2:
            # READ(IUNIT,*) kdo
            kdo = int(_ld(read_line(C.IUNIT))[0])
            continue  # GO TO 10
        if ifancy > 49 and ifancy < 100:
            C.IASV = 1
        if abs(mode) == 3 or abs(mode) == 4:
            continue  # GO TO 10
        if abs(mode) == 5 or abs(mode) == 15:
            # READ(IUNIT,*) FROPCI
            fropci = _f(_ld(read_line(C.IUNIT))[0])
            if ion == C.IELH:
                if ii == 1 and C.CUTLYM != 0:
                    fropci = -C.CUTLYM
                if ii == 2 and C.CUTBAL != 0:
                    fropci = -C.CUTBAL
            if abs(fropci) < 1.e10:
                fropci = 2.997925e18 / fropci
        if ii == 1:
            jcorr = C.NLEVS[ion] + 1 - jj
        ii = ii + ii0
        jj = jj + ii0 + jcorr
        C.fropc[ii] = fropci
        n0i = C.NFIRST[ie]  # IE 为前面能级输入循环的遗留值（Fortran 语义）
        nki = C.NNEXT[ie]
        if jj >= nki:
            lpc = False
            if C.IELHE2 >= 0:
                if (ii >= C.NFIRST[C.IELHE2] and ii <= C.NLAST[C.IELHE2]
                        and C.ifwop[ii] >= 0):
                    lpc = True
            if ii >= C.N0HN and ii <= C.N1H and C.ifwop[ii] >= 0:
                lpc = True
            if lpc:
                mode = 5
                xi = float(C.NQUANT[ii])
                x2 = xi + 3.
                if ii >= 8:
                    x2 = xi + 2.
                if C.fropc[ii] >= 0.:
                    C.fropc[ii] = C.ENION[ii] / 6.6256e-27 * (1. - xi * xi / (x2 * x2))
                else:
                    C.fropc[ii] = abs(C.fropc[ii])
                # write(6,671) ii,fropc(ii),enion(ii)/h,2.997925e18/fropc(ii)  —— 原代码已注释
                #  671 format(i4,1p2e13.5,0pf10.1)  —— 原代码已注释
        if mode == 0:
            if ii < C.NLAST[ion]:
                continue  # GO TO 10
            if ii == C.NLAST[ion]:
                _goto = 15  # GO TO 15
                break

        #   -----------------------------------------------------
        #   Additional input parameters for continuum transitions
        #   -----------------------------------------------------
        #
        #     Only for IFANCY = 2, 3, or 4
        #     S0BF, ALFBF, BETBF, GAMBF  - parameters for evaluation the
        #         photoionization cross-section
        if ifancy >= 2 and ifancy <= 4:
            # READ(IUNIT,*) S0BF(II),ALFBF(II),BETBF(II),GAMBF(II)
            _w = _ld(read_line(C.IUNIT))
            C.S0BF[ii] = _f(_w[0])
            C.ALFBF[ii] = _f(_w[1])
            C.BETBF[ii] = _f(_w[2])
            C.GAMBF[ii] = _f(_w[3])

        #   -----------------------------------------------------
        #   Additional input parameters for continuum transitions -TOPBASE DATA
        #   -----------------------------------------------------
        #
        #     Only for IFANCY > 100 there are IFANCY-100 fit points
        #
        #     XTOP(MFIT,MCROSS) -  x = alog10(nu/nu0) of a fit point
        #     CTOP(MFIT,MCROSS) -  sigma = alog10(sigma/10^-18) of a fit point
        if ifancy > 100:
            nfit = ifancy - 100
            if nfit > MFIT:
                quit(' nfit too large (TOPBASE fits)')
            # READ(IUNIT,*) (XTOP(IFIT,II),IFIT=1,NFIT)
            _w = _ld(read_line(C.IUNIT))
            for ifit in range(1, nfit + 1):
                C.XTOP[ifit, ii] = _f(_w[ifit - 1])
            # READ(IUNIT,*) (CTOP(IFIT,II),IFIT=1,NFIT)
            _w = _ld(read_line(C.IUNIT))
            for ifit in range(1, nfit + 1):
                C.CTOP[ifit, ii] = _f(_w[ifit - 1])
        C.IBF[ii] = ifancy
        C.indexp[ii] = abs(mode)
        if ii < C.NLAST[ion]:
            continue  # GO TO 10
        _goto = 15  # 顺序落入标号 15
        break

    # 标号 15：跳行直到 '*' 行
    if _goto == 15:
        while True:  # 对应 Fortran 标号 15
            # READ(IUNIT,501) A  —— 无 END=，遇 EOF 按 Fortran 语义报错（EOFError 抛出）
            a = (read_line(C.IUNIT) + ' ')[0]
            if feq(a, '*'):
                break  # A.EQ.'*' 退出；否则 GO TO 15

    #  -----------------------------------------------------------
    #  Input parameters for line transitions
    #  -----------------------------------------------------------
    if _goto != 30:
        while True:  # 对应 Fortran 标号 20
            # READ(IUNIT,*,END=30,ERR=30) II,JJ,MODE,IFANCY,ICOLIS,
            #                             IFRQ0,IFRQ1,OSC,CPARAM
            try:
                _w = _ld(read_line(C.IUNIT))
                ii = int(_w[0])
                jj = int(_w[1])
                mode = int(_w[2])
                ifancy = int(_w[3])
                icolis = int(_w[4])
                ifrq0 = int(_w[5])
                ifrq1 = int(_w[6])
                osc = _f(_w[7])
                cparam = _f(_w[8])
            except (EOFError, ValueError, IndexError):
                break  # END=30 / ERR=30 → GO TO 30
            if abs(mode) > 100:
                # READ(IUNIT,*) FR0INP
                fr0inp = _f(_ld(read_line(C.IUNIT))[0])
            if jj > C.NLEVS[ion]:
                if abs(mode) == 2:
                    # READ(IUNIT,*) K1,K2,K3,X1,X2,X3,K4
                    _w = _ld(read_line(C.IUNIT))
                    k1 = int(_w[0])
                    k2 = int(_w[1])
                    k3 = int(_w[2])
                    x1 = _f(_w[3])
                    x2 = _f(_w[4])
                    x3 = _f(_w[5])
                    k4 = int(_w[6])
                    continue  # GO TO 20
                if abs(mode) == 1:
                    # READ(IUNIT,*) LCMP
                    # TODO(port): LCMP 以 L 开头，按 PARAMS.FOR 的 IMPLICIT LOGICAL*1(L)
                    # 为 LOGICAL（数据文件中为 'T'/'F'），且读入后未使用
                    lcmp = _ld(read_line(C.IUNIT))[0].upper().startswith('T')
                if abs(ifancy) == 1:
                    # READ(IUNIT,*) GAMR,STARK1,STARK2,STARK3,VDWH
                    _w = _ld(read_line(C.IUNIT))
                    gamr = _f(_w[0])
                    stark1 = _f(_w[1])
                    stark2 = _f(_w[2])
                    stark3 = _f(_w[3])
                    vdwh = _f(_w[4])
                continue  # GO TO 20
            if abs(mode) == 2:
                # READ(IUNIT,*) K1,K2,K3,X1,X2,X3,K4
                _w = _ld(read_line(C.IUNIT))
                k1 = int(_w[0])
                k2 = int(_w[1])
                k3 = int(_w[2])
                x1 = _f(_w[3])
                x2 = _f(_w[4])
                x3 = _f(_w[5])
                k4 = int(_w[6])
                continue  # GO TO 20
            if abs(mode) == 3 or abs(mode) == 4:
                continue  # GO TO 20
            if mode == 0:
                continue  # GO TO 20

            #  -----------------------------------------------------------
            #  Additional input parameters for "clasical" line transitions
            #   (i.e. those not represented by ODF's - ie ABS(MODE)=1)
            #  -----------------------------------------------------------
            # READ(IUNIT,*) LCOMP,INTMOD,NF,XMAX,TSTD
            _w = _ld(read_line(C.IUNIT))
            # TODO(port): LCOMP 以 L 开头，按 PARAMS.FOR 的 IMPLICIT LOGICAL*1(L)
            # 为 LOGICAL（数据文件中为 'T'/'F'），且读入后未使用
            lcomp = _w[0].upper().startswith('T')
            intmod = int(_w[1])
            nf = int(_w[2])
            xmax = _f(_w[3])
            tstd = _f(_w[4])
            if abs(ifancy) == 1:
                # READ(IUNIT,*) GAMR,STARK1,STARK2,STARK3,VDWH
                _w = _ld(read_line(C.IUNIT))
                gamr = _f(_w[0])
                stark1 = _f(_w[1])
                stark2 = _f(_w[2])
                stark3 = _f(_w[3])
                vdwh = _f(_w[4])
            continue  # GO TO 20

    # 30 CONTINUE
    close_unit(C.IUNIT)
    return
