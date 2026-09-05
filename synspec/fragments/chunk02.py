# ============================================================================
# chunk02: synspec54.f 行 1116–2075
# NSTPAR / count_words / GETWRD / STATE0 / INIMOD / STATE / TINT
# ============================================================================

# --- DATA PVALUE（NSTPAR），之后会被修改（Fortran 隐含 SAVE）→ 提升为模块级
_save_nstpar_pvalue = [''] + [
    '     1', '  1.D0', '     0', '     0', ' 1.e19',
    '    70', '   120', '     0', '     0', '     0',
    '     0', '     1', '     1', '     1', '     1',
    '     1', '     1', '     1', '     1', '     1',
    '     1', '     1', '     1', '     1', '    0.',
    '    0.', '    2.', '     1', ' 9000.', '     1',
    '     1', '     1', '     1', '    0.', '    0.',
    '     0', '3.1e-5', '1.0e-7', '     0', ' 1.e18',
    '  0.10', '     1', '     1', '     1',
]

# --- DATA D（STATE0）：D(3,MATOM)，列主序填充；之后被修改（d(2,i)=...，
#     Fortran 隐含 SAVE）→ 提升为模块级
_save_state0_D = np.zeros((4, MATOM + 1))
_save_state0_D[1:4, 1:MATOM + 1] = np.array([
    1.008, 1.0, 2.0, 4.003, 0.1, 3.0,
    6.941, 1.26e-11, 3.0, 9.012, 2.51e-11, 3.0,
    10.81, 5e-10, 4.0, 12.011, 0.000331, 5.0,
    14.007, 8.32e-05, 5.0, 16.0, 0.000676, 5.0,
    18.918, 3.16e-08, 4.0, 20.179, 0.00012, 4.0,
    22.99, 2.14e-06, 4.0, 24.305, 3.8e-05, 4.0,
    26.982, 2.95e-06, 4.0, 28.086, 3.55e-05, 5.0,
    30.974, 2.82e-07, 5.0, 32.06, 2.14e-05, 5.0,
    35.453, 3.16e-07, 5.0, 39.948, 2.52e-06, 5.0,
    39.098, 1.32e-07, 5.0, 40.08, 2.29e-06, 5.0,
    44.956, 1.48e-09, 5.0, 47.9, 1.05e-07, 5.0,
    50.941, 1e-08, 5.0, 51.996, 4.68e-07, 5.0,
    54.938, 2.45e-07, 5.0, 55.847, 3.16e-05, 5.0,
    58.933, 8.32e-08, 5.0, 58.7, 1.78e-06, 5.0,
    63.546, 1.62e-08, 5.0, 65.38, 3.98e-08, 5.0,
    69.72, 1.34896324e-09, 3.0, 72.6, 4.26579633e-09, 3.0,
    74.92, 2.34422821e-10, 3.0, 78.96, 2.23872066e-09, 3.0,
    79.91, 4.26579633e-10, 3.0, 83.8, 1.69824373e-09, 3.0,
    85.48, 2.51188699e-10, 3.0, 87.63, 8.51138173e-10, 3.0,
    88.91, 1.65958702e-10, 3.0, 91.22, 4.07380181e-10, 3.0,
    92.91, 2.5118863e-11, 3.0, 95.95, 9.12010923e-11, 3.0,
    99.0, 1e-24, 3.0, 101.1, 6.60693531e-11, 3.0,
    102.9, 1.23026887e-11, 3.0, 106.4, 5.01187291e-11, 3.0,
    107.9, 1.73780087e-11, 3.0, 112.4, 5.75439927e-11, 3.0,
    114.8, 6.6069344e-12, 3.0, 118.7, 1.3803846e-10, 3.0,
    121.8, 1.0964781e-11, 3.0, 127.6, 1.73780087e-10, 3.0,
    126.9, 3.23593651e-11, 3.0, 131.3, 1.69824373e-10, 3.0,
    132.9, 1.31825676e-11, 3.0, 137.4, 1.62181025e-10, 3.0,
    138.9, 1.58489337e-11, 3.0, 140.1, 4.07380293e-11, 3.0,
    140.9, 6.02559549e-12, 3.0, 144.3, 2.95120943e-11, 3.0,
    147.0, 1e-24, 3.0, 150.4, 9.33254366e-12, 3.0,
    152.0, 3.46736869e-12, 3.0, 157.3, 1.1748977e-11, 3.0,
    158.9, 2.13796216e-12, 3.0, 162.5, 1.41253747e-11, 3.0,
    164.9, 3.16227767e-12, 3.0, 167.3, 8.91250917e-12, 3.0,
    168.9, 1.34896287e-12, 3.0, 173.0, 8.91250917e-12, 3.0,
    175.0, 1.31825674e-12, 3.0, 178.5, 5.37031822e-12, 3.0,
    181.0, 1.34896287e-12, 3.0, 183.9, 4.78630102e-12, 3.0,
    186.3, 1.86208719e-12, 3.0, 190.2, 2.3988329e-11, 3.0,
    192.2, 2.34422885e-11, 3.0, 195.1, 4.78630036e-11, 3.0,
    197.0, 6.76082952e-12, 3.0, 200.6, 1.23026887e-11, 3.0,
    204.4, 6.6069344e-12, 3.0, 207.2, 1.12201834e-10, 3.0,
    209.0, 5.12861361e-12, 3.0, 210.0, 1e-24, 3.0,
    211.0, 1e-24, 3.0, 222.0, 1e-24, 3.0,
    223.0, 1e-24, 3.0, 226.1, 1e-24, 3.0,
    227.1, 1e-24, 3.0, 232.0, 1.20226443e-12, 3.0,
    231.0, 1e-24, 3.0, 238.0, 3.23593651e-13, 3.0,
    237.0, 1e-24, 3.0, 244.0, 1e-24, 3.0,
    243.0, 1e-24, 3.0, 247.0, 1e-24, 3.0,
    247.0, 1e-24, 3.0, 251.0, 1e-24, 3.0,
    254.0, 1e-24, 3.0,
]).reshape((3, MATOM), order='F')


def nstpar(finstd):
    """
    settiing up the default values of various input flags, and
    input of non-standard values of various input flags and parameters

    对应 synspec54.f 行 1116–1251

    原 COMMON 声明：
      common/hhebrd/sthe,nunhhe
      common/gompar/hglim,ihgom
      common/brdstd/gsstd,gwstd
    """
    MVAR = 44          # PARAMETER(MVAR=44)
    INPFI = 4          # PARAMETER(INPFI=4)
    # DATA VARNAM /.../ —— 只读，不作为 SAVE 提升
    varnam = [''] + [
        'IATREF', 'BERGFC', 'IHYDPR', 'NUNHHE', 'STHE  ',
        'ND    ', 'NFREQS', 'IBFAC ', 'INTRPL', 'ICHANG',
        'IFEOS ', 'IOPHMI', 'IOPH2P', 'IOPHEM', 'IOPCH ',
        'IOPOH ', 'IOPH2M', 'IOH2H2', 'IOH2HE', 'IOH2H1',
        'IOHHE ', 'IRSCT ', 'IRSCH2', 'IRSCHE', 'TRAD  ',
        'WDIL  ', 'VTB   ', 'IFMOL', 'TMOLIM', 'MOLTAB',
        'IRWTAB', 'IIRWIN', 'IPFEXO', 'CUTLYM', 'CUTBAL',
        'IHXENB', 'GSSTD ', 'GWSTD ', 'IHGOM ', 'HGLIM ',
        'ERANGE', 'ISPICK', 'ILPICK', 'IPPICK',
    ]
    pvalue = _save_nstpar_pvalue   # 别名：DATA 初始化且被修改 → 模块级 SAVE 数组
    # DATA BLNK/'                    '/,BLNK6/'      '/
    blnk = ' ' * 20
    blnk6 = ' ' * 6

    if not feq(finstd, blnk):      # IF(FINSTD.NE.BLNK)
        # OPEN(UNIT=INPFI,FILE=FINSTD,STATUS='UNKNOWN')（用于读）
        open_unit(INPFI, finstd, 'r')

    indv = -1
    # K1/K2 是 GETWRD 的输出哑元，首次调用前 Fortran 中未定义；
    # GETWRD 入口处即置 K1=K2=0，故此处初值不影响语义
    k1 = 0
    k2 = 0

    # go through the input file line by line
    #  601 format(/' INPUT KEYWORD PARAMETERS:'/
    #   *        ' -------------------------')
    print()
    print(' INPUT KEYWORD PARAMETERS:')
    print(' -------------------------')

    _label = 10                    # 对应 Fortran 标号 10
    while True:
        if _label == 10:
            k0 = 1
            # READ(INPFI,500,END=70,ERR=70) TEXT ; 500 FORMAT(A)
            try:
                text = read_line(INPFI).ljust(80)[:80]
            except EOFError:       # END=70 / ERR=70
                _label = 70
                continue
            print(text)            # WRITE(6,*) TEXT
            _label = 20
            continue
        if _label == 20:
            # CALL GETWRD(TEXT,K0,K1,K2)：GETWRD 给标量哑元 K1,K2 赋值，
            # 按约定返回全部哑元并重新接收
            text, k0, k1, k2 = getwrd(text, k0, k1, k2)
            if k1 == 0:
                _label = 60        # GO TO 60
                continue
            k0 = k2 + 2
            if text[k1 - 1:k2] == '=':
                continue           # GO TO 20
            indv = -indv
            if indv == 1:
                found = False
                for i in range(1, MVAR + 1):       # DO 40 I=1,MVAR
                    # TEXT(K1:K2).EQ.VARNAM(I)(1:K2-K1+1)
                    if text[k1 - 1:k2] == varnam[i][0:k2 - k1 + 1]:
                        found = True
                        break      # GO TO 50
                if not found:
                    text, k0, k1, k2 = getwrd(text, k0, k1, k2)
                    if k1 == 0:
                        k0 = 1
                        # 标号 45：反复读下一行，直到取得一个词
                        while True:
                            # READ(INPFI,500,END=70) TEXT ; 500 FORMAT(A)
                            try:
                                text = read_line(INPFI).ljust(80)[:80]
                            except EOFError:   # END=70
                                _label = 70
                                break
                            text, k0, k1, k2 = getwrd(text, k0, k1, k2)
                            if k1 == 0:
                                continue       # GO TO 45
                            break
                        if _label == 70:
                            continue
                    k0 = k2 + 2
                    indv = -indv
                    continue       # GO TO 20
                # 50 CONTINUE
                ivar = i
            else:
                pvalue[ivar] = blnk6
                # PVALUE(IVAR)(6-K2+K1:6)=TEXT(K1:K2)：词右对齐写入 6 字符场
                # （假定词长不超过 6，否则 Fortran 也会下标越界）
                ist = 6 - k2 + k1
                pvalue[ivar] = ' ' * (ist - 1) + text[k1 - 1:k2]
            continue               # GO TO 20
        if _label == 60:
            _label = 10            # GO TO 10
            continue
        if _label == 70:
            break

    # 把 44 个参数值写入临时单元 84。unit 84 未显式 OPEN，Fortran 隐式连接
    # fort.84；为随后 CLOSE+REWIND 之后的表式 READ，先以 w+ 打开
    open_unit(84, 'fort.84', 'w+')
    for i in range(1, MVAR + 1):
        #  684    FORMAT(1X,A)
        write_line(84, ' ' + pvalue[i])
    close_unit(84)                 # CLOSE(UNIT=84)
    # REWIND(84)：对已关闭的单元，Fortran 重新连接 fort.84 并定位到开头
    open_unit(84, 'fort.84', 'r')

    # READ(84,*) IATREF,BERGFC,IHYDPR,NUNHHE,STHE,ND,NFREQS,IBFAC,INTRPL,
    #            ICHANG,IFEOS,IOPHMI,IOPH2P,IOPHEM,IOPCH,IOPOH,IOPH2M,
    #            IOH2H2,IOH2HE,IOH2H1,IOHHE,IRSCT,IRSCH2,IRSCHE,TRAD,WDIL,
    #            VTB,IFMOL,TMOLIM,MOLTAB,IRWTAB,IIRWIN,IPFEXO,CUTLYM,CUTBAL,
    #            IHXENB,GSSTD,GWSTD,IHGOM,HGLIM,ERANGE,ISPICK,ILPICK,IPPICK
    # 表式读：每个记录一个值（上面 WRITE 时每行写一个）
    _recs = [read_line(84) for _ in range(MVAR)]

    def _tok(idx):
        """取第 idx 个（1 基）记录中的第一个场。"""
        t = _recs[idx - 1].split()
        return t[0] if t else ''

    def _pi(idx):
        """按整数解析（兼容 Fortran D 指数写法）。"""
        s = _tok(idx)
        return int(float(s.replace('D', 'e').replace('d', 'e'))) if s else 0

    def _pf(idx):
        """按实数解析（兼容 Fortran D 指数写法）。"""
        s = _tok(idx)
        return float(s.replace('D', 'e').replace('d', 'e')) if s else 0.0

    C.IATREF = _pi(1)
    C.BERGFC = _pf(2)
    C.IHYDPR = _pi(3)
    C.nunhhe = _pi(4)
    C.sthe = _pf(5)
    C.ND = _pi(6)
    C.NFREQS = _pi(7)
    C.IBFAC = _pi(8)
    C.INTRPL = _pi(9)
    C.ICHANG = _pi(10)
    C.IFEOS = _pi(11)
    C.IOPHMI = _pi(12)
    C.IOPH2P = _pi(13)
    C.IOPHEM = _pi(14)
    C.IOPCH = _pi(15)
    C.IOPOH = _pi(16)
    C.IOPH2M = _pi(17)
    C.IOH2H2 = _pi(18)
    C.IOH2HE = _pi(19)
    C.IOH2H1 = _pi(20)
    C.IOHHE = _pi(21)
    C.IRSCT = _pi(22)
    C.IRSCH2 = _pi(23)
    C.IRSCHE = _pi(24)
    # TODO(port): TRAD/WDIL 在 NSTPAR 的三个 INCLUDE 中均未声明，
    # 按 IMPLICIT REAL*8 它们是本例程的局部标量（与 WINCOM.FOR 中的
    # C.TRAD/C.WDIL 数组无关），读入后未被使用
    trad = _pf(25)
    wdil = _pf(26)
    C.VTB = _pf(27)
    C.IFMOL = _pi(28)
    C.TMOLIM = _pf(29)
    C.MOLTAB = _pi(30)
    C.IRWTAB = _pi(31)
    C.IIRWIN = _pi(32)
    C.IPFEXO = _pi(33)
    C.CUTLYM = _pf(34)
    C.CUTBAL = _pf(35)
    C.IHXENB = _pi(36)
    C.gsstd = _pf(37)
    C.gwstd = _pf(38)
    C.ihgom = _pi(39)
    C.hglim = _pf(40)
    C.ERANGE = _pf(41)
    C.ISPICK = _pi(42)
    C.ILPICK = _pi(43)
    C.IPPICK = _pi(44)

    if C.IMODE <= -3:
        C.IRSCT = 0
        C.IRSCHE = 0
        C.IRSCH2 = 0

    return


def count_words(cadena, n):
    """
    Counts the number of words separated by blanks in a string

    对应 synspec54.f 行 1257–1272

    标量哑元 n 被赋值，按约定返回全部哑元 (cadena, n)。
    TODO(port): Fortran 按声明长度 LEN(cadena)=1000 循环，这里按实际
    字符串长度；差异只涉及尾部空格，不影响词数统计。
    """
    # character*1000  cadena ; character*1 a,b
    n = 0
    a = cadena[0:1]
    if a != ' ':
        n = 1
    for i in range(2, len(cadena) + 1):
        b = cadena[i - 1:i]
        if b != ' ' and a == ' ':
            n = n + 1
        a = b
    return cadena, n


def getwrd(text, k0, k1, k2):
    """
    FINDS NEXT WORD IN TEXT FROM INDEX K0. NEXT WORD IS TEXT(K1:K2)
    THE NEXT WORD STARTS AT THE FIRST ALPHANUMERIC CHARACTER AT K0
    OR AFTER. IT ENDS WITH THE LAST ALPHANUMERIC CHARACTER IN A ROW
    FROM THE START

    TAKEN FROM MULTI - M. CARLSSON (1976)

    对应 synspec54.f 行 1278–1324

    标量哑元 K1,K2 被赋值，按约定返回全部哑元 (text, k0, k1, k2)。
    """
    MSEPAR = 7                     # PARAMETER (MSEPAR=7)
    # DATA SEPAR/' ','(',')','=','*','/',','/
    separ = [' ', '(', ')', '=', '*', '/', ',']

    k1 = 0
    k2 = 0
    found = False
    for i in range(k0, len(text) + 1):     # DO 400 I=K0,LEN(TEXT)
        if k1 == 0:
            # 未在词内：若当前字符不是分隔符则 K1=I（词起点），
            # 否则经 200 CONTINUE 继续扫描
            if text[i - 1] not in separ:
                k1 = i
            # 200 CONTINUE
        else:
            # 词内：遇到分隔符 → GO TO 500
            if text[i - 1] in separ:
                k2 = i - 1         # 500：NEW WORD IN TEXT(K1:I-1)
                found = True
                break
        # 400 CONTINUE
    if not found:
        # NO NEW WORD. RETURN K1=K2=0（GO TO 999）
        # 注意：词一直延伸到 TEXT 末尾而无结束分隔符时，Fortran 原逻辑
        # 同样返回 K1=K2=0，此处保持原样
        k1 = 0
        k2 = 0
    # 999 CONTINUE
    return text, k0, k1, k2


def state0(modold):
    """
    Initialization of the basic parameters for the Saha equation

    对应 synspec54.f 行 1330–1875

    原 PARAMETER：parameter (enhe1=24.5799,enhe2=54.3999)
    """
    enhe1 = 24.5799
    enhe2 = 54.3999
    d = _save_state0_D   # 别名：DATA 初始化且被修改 → 模块级 SAVE 数组

    # DATA DYP —— 元素符号（character*4），只读
    dyp = [''] + [
        ' H  ', ' He ', ' Li ', ' Be ', ' B  ',
        ' C  ', ' N  ', ' O  ', ' F  ', ' Ne ',
        ' Na ', ' Mg ', ' Al ', ' Si ', ' P  ',
        ' S  ', ' Cl ', ' Ar ', ' K  ', ' Ca ',
        ' Sc ', ' Ti ', ' V  ', ' Cr ', ' Mn ',
        ' Fe ', ' Co ', ' Ni ', ' Cu ', ' Zn ',
        ' Ga ', ' Ge ', ' As ', ' Se ', ' Br ',
        ' Kr ', ' Rb ', ' Sr ', ' Y  ', ' Zr ',
        ' Nb ', ' Mo ', ' Tc ', ' Ru ', ' Rh ',
        ' Pd ', ' Ag ', ' Cd ', ' In ', ' Sn ',
        ' Sb ', ' Te ', ' I  ', ' Xe ', ' Cs ',
        ' Ba ', ' La ', ' Ce ', ' Pr ', ' Nd ',
        ' Pm ', ' Sm ', ' Eu ', ' Gd ', ' Tb ',
        ' Dy ', ' Ho ', ' Er ', ' Tm ', ' Yb ',
        ' Lu ', ' Hf ', ' Ta ', ' W  ', ' Re ',
        ' Os ', ' Ir ', ' Pt ', ' Au ', ' Hg ',
        ' Tl ', ' Pb ', ' Bi ', ' Po ', ' At ',
        ' Rn ', ' Fr ', ' Ra ', ' Ac ', ' Th ',
        ' Pa ', ' U  ', ' Np ', ' Pu ', ' Am ',
        ' Cm ', ' Bk ', ' Cf ', ' Es ',
    ]

    # Standard atomic constants for first 99 species
    #  Abundances for the first 30 from Grevesse & Sauval,
    #     (1998, Space Sci. Rev. 85, 161)
    #
    #        Element Atomic  Solar    Std.
    #                weight abundance highest
    #                                 ionization stage
    # （D 的 DATA 初值已提升为模块级 _save_state0_D）

    # data abun0 —— 只读
    abun0 = np.zeros(MATOM + 1)
    abun0[1:MATOM + 1] = [
        12.0, 10.93, 1.05, 1.38, 2.7, 8.39,
        7.78, 8.66, 4.56, 7.84, 6.17, 7.53,
        6.37, 7.51, 5.36, 7.14, 5.5, 6.18,
        5.08, 6.31, 3.05, 4.9, 4.0, 5.64,
        5.39, 7.45, 4.92, 6.23, 4.21, 4.6,
        2.88, 3.58, 2.29, 3.33, 2.56, 3.28,
        2.6, 2.92, 2.21, 2.59, 1.42, 1.92,
        -9.99, 1.84, 1.12, 1.69, 0.94, 1.77,
        1.6, 2.0, 1.0, 2.19, 1.51, 2.27,
        1.07, 2.17, 1.13, 1.58, 0.71, 1.45,
        -9.99, 1.01, 0.52, 1.12, 0.28, 1.14,
        0.51, 0.93, 0.0, 1.08, 0.06, 0.88,
        -0.17, 1.11, 0.23, 1.45, 1.38, 1.64,
        1.01, 1.13, 0.9, 2.0, 0.65, -9.99,
        -9.99, -9.99, -9.99, -9.99, -9.99, 0.06,
        -9.99, -0.52, -9.99, -9.99, -9.99, -9.99,
        -9.99, -9.99, -9.99,
    ]

    # data abun1 —— 只读
    abun1 = np.zeros(MATOM + 1)
    abun1[1:MATOM + 1] = [
        12.0, 10.93, 3.26, 1.38, 2.79, 8.43,
        7.83, 8.69, 4.56, 7.93, 6.24, 7.6,
        6.45, 7.51, 5.41, 7.12, 5.5, 6.4,
        5.08, 6.34, 3.15, 4.95, 3.93, 5.64,
        5.43, 7.5, 4.99, 6.22, 4.19, 4.56,
        3.04, 3.65, 2.3, 3.34, 2.54, 3.25,
        2.36, 2.87, 2.21, 2.58, 1.46, 1.88,
        -9.99, 1.75, 1.06, 1.65, 1.2, 1.71,
        0.76, 2.04, 1.01, 2.18, 1.55, 2.24,
        1.08, 2.18, 1.1, 1.58, 0.72, 1.42,
        -9.99, 0.96, 0.52, 1.07, 0.3, 1.1,
        0.48, 0.92, 0.1, 0.92, 0.1, 0.85,
        -0.12, 0.65, 0.26, 1.4, 1.38, 1.62,
        0.8, 1.17, 0.77, 2.04, 0.65, -9.99,
        -9.99, -9.99, -9.99, -9.99, -9.99, 0.06,
        -9.99, -0.54, -9.99, -9.99, -9.99, -9.99,
        -9.99, -9.99, -9.99,
    ]

    # Ionization potentials for first 99 species:
    # DATA XI —— XI(8,MATOM)，列主序填充，只读
    # Element Ionization potentials (eV)
    #          I     II      III     IV       V     VI     VII    VIII
    xi = np.zeros((9, MATOM + 1))
    xi[1:9, 1:MATOM + 1] = np.array([
        13.595, 0.0, 0.0, 0.0, 0.0, 0.0,
        0.0, 0.0, 24.58, 54.4, 0.0, 0.0,
        0.0, 0.0, 0.0, 0.0, 5.392, 75.619,
        122.451, 0.0, 0.0, 0.0, 0.0, 0.0,
        9.322, 18.206, 153.85, 217.713, 0.0, 0.0,
        0.0, 0.0, 8.296, 25.149, 37.92, 259.298,
        340.22, 0.0, 0.0, 0.0, 11.264, 24.376,
        47.864, 64.476, 391.99, 489.98, 0.0, 0.0,
        14.53, 29.593, 47.426, 77.45, 97.86, 551.93,
        667.03, 0.0, 13.614, 35.108, 54.886, 77.394,
        113.87, 138.08, 739.11, 871.39, 17.418, 34.98,
        62.646, 87.14, 114.21, 157.12, 185.14, 953.6,
        21.559, 41.07, 63.5, 97.02, 126.3, 157.91,
        207.21, 239.0, 5.138, 47.29, 71.65, 98.88,
        138.37, 172.09, 208.44, 264.16, 7.664, 15.03,
        80.12, 102.29, 141.23, 186.49, 224.9, 265.96,
        5.984, 18.823, 28.44, 119.96, 153.77, 190.42,
        241.38, 284.53, 8.151, 16.35, 33.46, 45.14,
        166.73, 205.11, 246.41, 303.07, 10.484, 19.72,
        30.156, 51.354, 65.01, 220.41, 263.31, 309.26,
        10.357, 23.4, 35.0, 47.29, 72.5, 88.03,
        280.99, 328.8, 12.97, 23.8, 39.9, 53.5,
        67.8, 96.7, 114.27, 348.3, 15.755, 27.62,
        40.9, 59.79, 75.0, 91.3, 124.0, 143.46,
        4.339, 31.81, 46.0, 60.9, 82.6, 99.7,
        118.0, 155.0, 6.111, 11.87, 51.21, 67.7,
        84.39, 109.0, 128.0, 147.0, 6.56, 12.89,
        24.75, 73.9, 92.0, 111.1, 138.0, 158.7,
        6.83, 13.63, 28.14, 43.24, 99.8, 120.0,
        140.8, 168.5, 6.74, 14.2, 29.7, 48.0,
        65.2, 128.9, 151.0, 173.7, 6.763, 16.49,
        30.95, 49.6, 73.0, 90.6, 161.1, 184.7,
        7.432, 15.64, 33.69, 53.0, 76.0, 97.0,
        119.24, 196.46, 7.87, 16.183, 30.652, 54.8,
        75.0, 99.1, 125.0, 151.06, 7.86, 17.06,
        33.49, 51.3, 79.5, 102.0, 129.0, 157.0,
        7.635, 18.168, 35.17, 54.9, 75.5, 108.0,
        133.0, 162.0, 7.726, 20.292, 36.83, 55.2,
        79.9, 103.0, 139.0, 166.0, 9.394, 17.964,
        39.722, 59.4, 82.6, 108.0, 134.0, 174.0,
        6.0, 20.509, 30.7, 99.99, 99.99, 99.99,
        99.99, 99.99, 7.89944, 15.93462, 34.058, 45.715,
        99.99, 99.99, 99.99, 99.99, 9.7887, 18.5892,
        28.351, 99.99, 99.99, 99.99, 99.99, 99.99,
        9.75, 21.5, 32.0, 99.99, 99.99, 99.99,
        99.99, 99.99, 11.839, 21.6, 35.9, 99.99,
        99.99, 99.99, 99.99, 99.99, 13.995, 24.559,
        36.9, 99.99, 99.99, 99.99, 99.99, 99.99,
        4.175, 27.5, 40.0, 99.99, 99.99, 99.99,
        99.99, 99.99, 5.692, 11.026, 43.0, 99.99,
        99.99, 99.99, 99.99, 99.99, 6.2171, 12.2236,
        20.5244, 60.607, 99.99, 99.99, 99.99, 99.99,
        6.6339, 13.13, 23.17, 34.418, 80.348, 99.99,
        99.99, 99.99, 6.879, 14.319, 25.039, 99.99,
        99.99, 99.99, 99.99, 99.99, 7.099, 16.149,
        27.149, 99.99, 99.99, 99.99, 99.99, 99.99,
        7.28, 15.259, 30.0, 99.99, 99.99, 99.99,
        99.99, 99.99, 7.364, 16.759, 28.46, 99.99,
        99.99, 99.99, 99.99, 99.99, 7.46, 18.07,
        31.049, 99.99, 99.99, 99.99, 99.99, 99.99,
        8.329, 19.419, 32.92, 99.99, 99.99, 99.99,
        99.99, 99.99, 7.574, 21.48, 34.819, 99.99,
        99.99, 99.99, 99.99, 99.99, 8.99, 16.903,
        37.47, 99.99, 99.99, 99.99, 99.99, 99.99,
        5.784, 18.86, 28.029, 99.99, 99.99, 99.99,
        99.99, 99.99, 7.342, 14.627, 30.49, 72.3,
        99.99, 99.99, 99.99, 99.99, 8.639, 16.5,
        25.299, 44.2, 55.7, 99.99, 99.99, 99.99,
        9.0096, 18.6, 27.96, 37.4, 58.7, 99.99,
        99.99, 99.99, 10.454, 19.09, 32.0, 99.99,
        99.99, 99.99, 99.99, 99.99, 12.12984, 20.975,
        31.05, 45.0, 54.14, 99.99, 99.99, 99.99,
        3.893, 25.1, 35.0, 99.99, 99.99, 99.99,
        99.99, 99.99, 5.21, 10.0, 37.0, 99.99,
        99.99, 99.99, 99.99, 99.99, 5.58, 11.06,
        19.169, 99.99, 99.99, 99.99, 99.99, 99.99,
        5.65, 10.85, 20.08, 99.99, 99.99, 99.99,
        99.99, 99.99, 5.419, 10.55, 23.2, 99.99,
        99.99, 99.99, 99.99, 99.99, 5.49, 10.73,
        20.0, 99.99, 99.99, 99.99, 99.99, 99.99,
        5.55, 10.899, 20.0, 99.99, 99.99, 99.99,
        99.99, 99.99, 5.629, 11.069, 20.0, 99.99,
        99.99, 99.99, 99.99, 99.99, 5.68, 11.25,
        20.0, 99.99, 99.99, 99.99, 99.99, 99.99,
        6.159, 12.1, 20.0, 99.99, 99.99, 99.99,
        99.99, 99.99, 5.849, 11.519, 20.0, 99.99,
        99.99, 99.99, 99.99, 99.99, 5.93, 11.67,
        20.0, 99.99, 99.99, 99.99, 99.99, 99.99,
        6.02, 11.8, 20.0, 99.99, 99.99, 99.99,
        99.99, 99.99, 6.099, 11.93, 20.0, 99.99,
        99.99, 99.99, 99.99, 99.99, 6.18, 12.05,
        23.7, 99.99, 99.99, 99.99, 99.99, 99.99,
        6.25, 12.17, 20.0, 99.99, 99.99, 99.99,
        99.99, 99.99, 6.099, 13.899, 19.0, 99.99,
        99.99, 99.99, 99.99, 99.99, 7.0, 14.899,
        23.299, 99.99, 99.99, 99.99, 99.99, 99.99,
        7.879, 16.2, 24.0, 99.99, 99.99, 99.99,
        99.99, 99.99, 7.86404, 17.7, 25.0, 99.99,
        99.99, 99.99, 99.99, 99.99, 7.87, 16.6,
        26.0, 99.99, 99.99, 99.99, 99.99, 99.99,
        8.5, 17.0, 27.0, 99.99, 99.99, 99.99,
        99.99, 99.99, 9.1, 20.0, 28.0, 99.99,
        99.99, 99.99, 99.99, 99.99, 8.95868, 18.563,
        33.227, 99.99, 99.99, 99.99, 99.99, 99.99,
        9.22, 20.5, 30.0, 99.99, 99.99, 99.99,
        99.99, 99.99, 10.43, 18.75, 34.2, 99.99,
        99.99, 99.99, 99.99, 99.99, 6.10829, 20.4283,
        29.852, 50.72, 99.99, 99.99, 99.99, 99.99,
        7.416684, 15.0325, 31.9373, 42.33, 69.0, 99.99,
        99.99, 99.99, 7.285519, 16.679, 25.563, 45.32,
        56.0, 88.0, 99.99, 99.99, 8.43, 19.0,
        27.0, 99.99, 99.99, 99.99, 99.99, 99.99,
        9.3, 20.0, 29.0, 99.99, 99.99, 99.99,
        99.99, 99.99, 10.745, 20.0, 30.0, 99.99,
        99.99, 99.99, 99.99, 99.99, 4.0, 22.0,
        33.0, 99.99, 99.99, 99.99, 99.99, 99.99,
        5.276, 10.144, 34.0, 99.99, 99.99, 99.99,
        99.99, 99.99, 6.9, 12.1, 20.0, 99.99,
        99.99, 99.99, 99.99, 99.99, 6.0, 12.0,
        20.0, 99.99, 99.99, 99.99, 99.99, 99.99,
        6.0, 12.0, 20.0, 99.99, 99.99, 99.99,
        99.99, 99.99, 6.0, 12.0, 20.0, 99.99,
        99.99, 99.99, 99.99, 99.99, 6.0, 12.0,
        20.0, 99.99, 99.99, 99.99, 99.99, 99.99,
        6.0, 12.0, 20.0, 99.99, 99.99, 99.99,
        99.99, 99.99, 6.0, 12.0, 20.0, 99.99,
        99.99, 99.99, 99.99, 99.99, 6.0, 12.0,
        20.0, 99.99, 99.99, 99.99, 99.99, 99.99,
        6.0, 12.0, 20.0, 99.99, 99.99, 99.99,
        99.99, 99.99, 6.0, 12.0, 20.0, 99.99,
        99.99, 99.99, 99.99, 99.99, 6.0, 12.0,
        20.0, 99.99, 99.99, 99.99, 99.99, 99.99,
    ]).reshape((8, MATOM), order='F')

    def _read_vals(unit, n):
        """表式（list-directed）读 n 个值；一个记录不够时自动续读下一记录。"""
        toks = []
        while len(toks) < n:
            toks.extend(read_line(unit).split())
        return toks[:n]

    def _fi(s):
        """表式整数场解析（兼容 D 指数写法）。"""
        return int(float(s.replace('D', 'e').replace('d', 'e')))

    def _ff(s):
        """表式实数场解析（兼容 D 指数写法）。"""
        return float(s.replace('D', 'e').replace('d', 'e'))

    # An element (hydrogen through zinc) can be considered in one of
    # the three following options:
    # 1. explicitly - some of energy levels of some of its ionization
    #                 states are considered explicitly, ie. their
    #                 populations are determined by solving statistical
    #                 equilibrium
    # 2. implicitly - the atom is assumed not to contribute to
    #                 opacity; but is allowed to contribute to the
    #                 total number of particles and to the total charge;
    #                 the latter is evaluated assuming LTE ionization
    #                 balance, ie. by solving a set of Saha equations
    # 3. not considered at all
    #
    # Input:
    #
    # For each element from 1 (hydrogen) to NATOMS, the following
    # parameters:
    #
    # MA     =  0  - if the element is not considered (option 3)
    #        =  1  - if the element is non-explicit (option 2)
    #        =  2  - if the element is explicit (option 1)
    #        =  4  - if the element is semi-explicit (i.e. behaves
    #                like MA=2 for continua and MA=1 for lines
    # NA0,NAK - have the meaning only for MA=2; indicate that the
    #           explicit energy levels of the present species have
    #           the indices between NA0 and NAK (NAK is thus the index
    #           of the highest ionization state, which is represented
    #           as one-level ion).
    # ION    -  has the meaning for MA=1 only;
    #           if ION=0, standard number of ionization degrees is
    #                     considered
    #                     (counting the neutral state also; so for
    #                     instance to treat all stages of He requires
    #                     ION=3, which is a default anyhow).
    #           if ION>0, then ION ionization degrees is considered
    # MODPF  -  mode of evaluation of partition functions
    #        =  0  -  standard evaluation (see procedure PARTF)
    #        >  0  -  partition functions evaluated from the
    #                 Opacity Project ionization fraction tables
    #        <  0  -  non-standard evaluation, by user supplied
    #                 procedure PFSPEC
    # ABN    -  if ABN=0, solar abundance is assumed (given above;
    #                     abundance here is assumed as relative
    #                     to hydrogen by number
    #           if ABN>0, non-solar abundance ABN is assumed; in an
    #                     arbitrary scale
    #           if ABN<0, non-solar abundance ABN is assumed;
    #                     (-ABN times the solar value)
    # PFS    -  see above

    iabset = 0
    # read(ibuff,'(a80)') dum
    dum = read_line(IBUFF).ljust(80)[:80]
    # read(dum,*,iostat=kstat) natoms,iabset —— 内部文件表式读
    _toks = dum.split()
    kstat = 0
    try:
        C.NATOMS = _fi(_toks[0])
        iabset = _fi(_toks[1])
    except (IndexError, ValueError):
        kstat = 1
    if kstat != 0:
        C.NATOMS = _fi(_toks[0])   # READ(dum,*) NATOMS

    #  600 FORMAT(1H0//' CHEMICAL ELEMENTS INCLUDED'/
    #     *            ' --------------------------'//
    #     * ' NUMBER  ELEMENT           ABUNDANCE'/1H ,16X,
    #     * 'A=N(ELEM)/N(H)  A/A(SOLAR)'/)
    print()
    print()
    print()
    print(' CHEMICAL ELEMENTS INCLUDED')
    print(' --------------------------')
    print()
    print()
    print(' NUMBER  ELEMENT           ABUNDANCE')
    print(' ' + ' ' * 16 + 'A=N(ELEM)/N(H)  A/A(SOLAR)')
    iat = 0
    iref = 0
    if C.NATOMS < 0:
        C.NATOMS = -C.NATOMS
    # TODO(port): MODOLD/=0 时 NA0/NAK 不会被读入赋值，但后面
    # WRITE(6,602) 仍引用它们（Fortran 中为未定义值）；这里先置 0
    na0 = 0
    nak = 0

    for i in range(1, MATOM + 1):
        for j in range(1, MION0 + 1):
            C.RR[i, j] = 0.
        if iabset == 1:
            d[2, i] = 10.**(abun1[i] - 12.)
        elif iabset != 2:
            d[2, i] = 10.**(abun0[i] - 12.)
    for id in range(1, C.ND + 1):
        C.YTOT[id] = 0.
        C.WMY[id] = 0.

    for i in range(1, MATOM + 1):
        C.TYPAT[i] = dyp[i]
        C.LGR[i] = True
        C.LRM[i] = True
        C.IATEX[i] = -1
        if i <= C.NATOMS:
            if modold == 0:
                # READ(IBUFF,*) MA,NA0,NAK,ION,MODPF(I),ABN,(PFSTD(J,I),J=1,5)
                _v = _read_vals(IBUFF, 11)
                ma = _fi(_v[0])
                na0 = _fi(_v[1])
                nak = _fi(_v[2])
                ion = _fi(_v[3])
                C.MODPF[i] = _fi(_v[4])
                abn = _ff(_v[5])
                for j in range(1, 6):
                    C.PFSTD[j, i] = _ff(_v[5 + j])
                ma = abs(ma)       # MA=IABS(MA)
            else:
                # READ(IBUFF,*) MA,ABN,MODPF(I)
                _v = _read_vals(IBUFF, 3)
                ma = _fi(_v[0])
                abn = _ff(_v[1])
                C.MODPF[i] = _fi(_v[2])
                ion = 0
        elif imod(C.IMODE, 10) <= 1 and C.IMODE != -4:
            ma = 1
            abn = 0.
            ion = 0
            C.MODPF[i] = 0
        else:
            ma = 0
        C.AMAS[i] = d[1, i]
        C.ABND[i] = d[2, i]
        if iref > 0:
            C.ABND[i] = d[2, i]*C.ABND[iref]/d[2, iref]
        C.IONIZ[i] = int(d[3, i])
        C.isemex[i] = 0

        # increase the standard highest ionization for Teff>30,000 K
        if C.TEFF > 3.e4:
            if i <= 8:
                C.IONIZ[i] = i + 1
            if i > 8 and i <= 30:
                C.IONIZ[i] = 9

        for j in range(1, 10):
            if j <= 8:
                C.ENEV[i, j] = xi[j, i]
                enev_ij = C.ENEV[i, j]
            else:
                # TODO(port): ENEV 只声明到 MI1=8，Fortran 中 ENEV(I,9)
                # 越界；按 COMMON/ATOBLN/ 列主序布局 ENEV 之后紧跟
                # AMAS(MATOM)，实际读到的是 AMAS(I)（此时已赋为 D(1,I)）
                enev_ij = C.AMAS[i]
            if enev_ij >= enhe2:
                C.INPOT[i, j] = 3
            elif enev_ij >= enhe1:
                C.INPOT[i, j] = 2
            else:
                C.INPOT[i, j] = 1
        if ma > 0:
            C.LGR[i] = False
            if abn > 0:
                C.ABND[i] = abn
            if abn < 0:
                C.ABND[i] = abs(abn)*d[2, i]
            if ion != 0:
                C.IONIZ[i] = ion
            if abn > 1.e6:
                # READ(IBUFF,*) (ABNDD(I,ID),ID=1,ND)
                _v = _read_vals(IBUFF, C.ND)
                for id in range(1, C.ND + 1):
                    C.ABNDD[i, id] = _ff(_v[id - 1])
            else:
                for id in range(1, C.ND + 1):
                    C.ABNDD[i, id] = C.ABND[i]
            if ma == 1:
                C.LRM[i] = False
                C.IATEX[i] = 0
            else:
                iat = iat + 1
                C.IATEX[i] = iat
                if ma == 4:
                    C.isemex[i] = 1
                if ma == 5:
                    C.isemex[i] = 2
                if iat == C.IATREF:
                    iref = i
                    for id in range(1, C.ND + 1):
                        C.ABNREF[id] = C.ABNDD[i, id]

                # store parameters for explicit atoms
                for id in range(1, C.ND + 1):
                    C.ABUND[iat, id] = C.ABNDD[i, id]
                C.AMASS[iat] = C.AMAS[i]*HMASS
                C.NUMAT[iat] = i
                if modold == 0:
                    C.N0A[iat] = na0
                    C.NKA[iat] = nak
            for id in range(1, C.ND + 1):
                C.YTOT[id] = C.YTOT[id] + C.ABNDD[i, id]
                C.WMY[id] = C.WMY[id] + C.ABNDD[i, id]*C.AMAS[i]
            abn = C.ABND[i]/d[2, i]
            #  601 FORMAT(1H ,I4,3X,A5,1P2E14.2)
            if ma == 1:
                print(f" {i:4d}   {C.TYPAT[i]:>5}"
                      f"{C.ABND[i]:14.2e}{abn:14.2e}")
            #  602 FORMAT(1H ,I4,3X,A5,1P2E14.2,3X,
            #     *       'EXPLICIT: IAT=',I3,'  N0A=',I3,'  NKA=',I3)
            if ma == 2:
                print(f" {i:4d}   {C.TYPAT[i]:>5}"
                      f"{C.ABND[i]:14.2e}{abn:14.2e}"
                      f"   EXPLICIT: IAT={iat:3d}  N0A={na0:3d}  NKA={nak:3d}")
    if imod(C.IMODE, 10) <= 1:
        C.NATOMS = MATOM
    for id in range(1, C.ND + 1):
        C.WMM[id] = C.WMY[id]*HMASS/C.YTOT[id]
    for jj in range(1, C.NATOMS + 1):
        for id in range(1, C.ND + 1):
            # TODO(port): NATOMS 可能因 NATOMS=MATOM(=99) 超过 RELAB 的
            # 声明上界 MATEX(=30)，Fortran 中会越界写入 /ATOPAR/ 后继
            # 存储；这里按声明上界截断
            if jj <= MATEX:
                C.RELAB[jj, id] = 1.

    # IF(ICHEMC.NE.1) go to 100
    if C.ICHEMC == 1:
        # abundance change with respect to the model atmosphere input
        # (unit 5);
        # this option is switched on by the parameter ICHEMC (read from
        # unit 55), if it is non-zero, an additional input from
        # unit 56 is required
        #
        # unit 56 input:
        #
        # NCHANG  -  number of chemical elements for which the abundances
        #            are going to be changes;
        #
        # then there are NCHANG records, each contains:
        #
        # I       - atomic number
        # ABN     - new abundance; coded using the same conventions as in
        #           the standard input

        # READ(56,*,ERR=566,END=566) NCHANG
        try:
            nchang = _fi(read_line(56).split()[0])
        except (EOFError, IndexError, ValueError):
            # 566 —— READ(56) 的 ERR/END 分支
            #  656 FORMAT(//' CHEMICAL COMPOSITION COULD NOT BE READ FROM ',
            #     *       'UNIT 56'//' STOP.')
            print()
            print()
            print(' CHEMICAL COMPOSITION COULD NOT BE READ FROM UNIT 56')
            print()
            print()
            print(' STOP.')
            raise SystemExit      # STOP
        #  610 FORMAT(//'    CHEMICAL ELEMENTS INCLUDED - CHANGED (unit 56)'
        #     *           /'    --------------------------'//
        #     * ' NUMBER  ELEMENT           ABUNDANCE'/1H ,16X,
        #     * 'A=N(ELEM)/N(H)  A/A(SOLAR)'/)
        print()
        print()
        print('    CHEMICAL ELEMENTS INCLUDED - CHANGED (unit 56)')
        print('    --------------------------')
        print()
        print()
        print(' NUMBER  ELEMENT           ABUNDANCE')
        print(' ' + ' ' * 16 + 'A=N(ELEM)/N(H)  A/A(SOLAR)')
        for ii in range(1, nchang + 1):
            # READ(56,*) I,ABN
            _v = _read_vals(56, 2)
            i = _fi(_v[0])
            abn = _ff(_v[1])
            C.ABND[i] = d[2, i]
            if abn > 0:
                C.ABND[i] = abn
            if abn < 0:
                C.ABND[i] = -abn*d[2, i]
            if abn > 1.:
                C.ABND[i] = 10.**(abn - 12.)
            if abn > 1.e6:
                # READ(56,*) (ABNDD(I,ID),ID=1,ND)
                _v = _read_vals(56, C.ND)
                for id in range(1, C.ND + 1):
                    C.ABNDD[i, id] = _ff(_v[id - 1])
            else:
                for id in range(1, C.ND + 1):
                    C.ABNDD[i, id] = C.ABND[i]
            C.LGR[i] = False
            iatx = C.IATEX[i]
            if iatx > 0:
                for id in range(1, C.ND + 1):
                    C.RELAB[iatx, id] = C.ABNDD[i, id]/C.ABUND[iatx, id]
                    C.ABUND[iatx, id] = C.ABNDD[i, id]
            abnr = C.ABND[i]/d[2, i]
            #  601 FORMAT(1H ,I4,3X,A5,1P2E14.2)
            print(f" {i:4d}   {C.TYPAT[i]:>5}"
                  f"{C.ABND[i]:14.2e}{abnr:14.2e}")

    # renormalize abundances to have the standard element abundance
    # equal to unity
    #
    # 100 IF(IREF.LE.1) RETURN
    if iref <= 1:
        return
    #  620 FORMAT(1H0//'    CHEMICAL ELEMENTS INCLUDED - RENORMALIZATION'/
    #     *            '    --------------------------'//
    #     * ' NUMBER  ELEMENT           ABUNDANCE'/1H ,16X,
    #     * 'A=N(ELEM)/N(H)  A/A(SOLAR)'/)
    print()
    print()
    print()
    print('    CHEMICAL ELEMENTS INCLUDED - RENORMALIZATION')
    print('    --------------------------')
    print()
    print()
    print(' NUMBER  ELEMENT           ABUNDANCE')
    print(' ' + ' ' * 16 + 'A=N(ELEM)/N(H)  A/A(SOLAR)')
    for i in range(1, MATOM + 1):
        iat = C.IATEX[i]
        if iat >= 0:
            for id in range(1, C.ND + 1):
                C.ABNDD[i, id] = C.ABNDD[i, id]/C.ABNREF[id]
                C.YTOT[id] = C.YTOT[id] + C.ABNDD[i, id]
                C.WMY[id] = C.WMY[id] + C.ABNDD[i, id]*C.AMAS[i]
            abnr = C.ABND[i]/d[2, i]
            if iat == 0:
                #  601 FORMAT(1H ,I4,3X,A5,1P2E14.2)
                print(f" {i:4d}   {C.TYPAT[i]:>5}"
                      f"{C.ABND[i]:14.2e}{abnr:14.2e}")
            else:
                for id in range(1, C.ND + 1):
                    C.ABUND[iat, id] = C.ABNDD[i, id]
                #  602 FORMAT(1H ,I4,3X,A5,1P2E14.2,3X,
                #     *       'EXPLICIT: IAT=',I3,'  N0A=',I3,'  NKA=',I3)
                print(f" {i:4d}   {C.TYPAT[i]:>5}"
                      f"{C.ABND[i]:14.2e}{abnr:14.2e}"
                      f"   EXPLICIT: IAT={iat:3d}"
                      f"  N0A={C.N0A[iat]:3d}  NKA={C.NKA[iat]:3d}")
    for id in range(1, C.ND + 1):
        C.WMM[id] = C.WMY[id]*HMASS/C.YTOT[id]
    return


def inimod():
    """
    SET UP COMMON/RRRVAL/  - VALUES OF  N(ION)/U(ION) FOR ALL THE ATOMS
    AND IONS CONSIDERED

    对应 synspec54.f 行 1881–1948

    原 COMMON 声明：
      COMMON/BLAPAR/RELOP,SPACE0,CUTOF0,TSTD,DSTD,ALAMC
      COMMON/HPOPST/HPOP
    """
    # 1. "low-temperature" ionization fractions
    #    (using Hamburg partition functions)
    for id in range(1, C.ND + 1):          # DO 50 ID=1,ND
        if C.IFMOL == 0 or C.TEMP[id] >= C.TMOLIM:
            # CALL STATE(ID,TEMP(ID),ELEC(ID),S1)：
            # STATE 给标量哑元 Q 赋值，按约定返回全部哑元并重新接收
            s1 = 0.0   # Fortran 中 S1 未初始化；STATE 内首先置 Q=0
            id, _te, _ane, s1 = state(id, C.TEMP[id], C.ELEC[id], s1)
            C.HPOP = C.DENS[id]/C.WMM[id]/C.YTOT[id]
            for j in range(1, MION0 + 1):
                for i in range(1, MATOM + 1):
                    C.RRR[id, j, i] = C.RR[i, j]*C.HPOP
            for iat in range(1, C.NATOM + 1):
                C.ATTOT[iat, id] = C.HPOP*C.ABUND[iat, id]
        else:
            C.HPOP = C.ATTOT[1, id]
        if id != C.IDSTD:
            continue                       # GO TO 50
        C.TSTD = C.TEMP[id]
        vts = C.VTURB[id]
        C.DSTD = math.sqrt(1.4e7*C.TSTD + vts)
        #  601 FORMAT(/' N/U  AT THE STANDARD DEPTH  (ID =',I3,
        #     *         ' ; T,Ne = ',F8.1,1P2E12.3,' )'/
        #     *         ' --------------------------'//)
        print()
        print(f" N/U  AT THE STANDARD DEPTH  (ID ={id:3d}"
              f" ; T,Ne = {C.TEMP[id]:8.1f}{C.ELEC[id]:12.3e}"
              f"{C.HPOP:12.3e} )")
        print(' --------------------------')
        print()
        # c       DO I=1,MATOM
        for i in range(1, 31):
            #  602 FORMAT(1H ,A4,1P8E9.2)
            print(f" {C.TYPAT[i]:4s}"
                  + ''.join(f"{C.RRR[id, j, i]:9.2e}"
                            for j in range(1, MION0)))  # J=1,MION0-1
        # c       WRITE(6,603)
        # c       DO I=1,MATOM
        # c          WRITE(6,602) TYPAT(I),(PFSTD(J,I),J=1,MION0-1)
        # c       END DO
        # 50 CONTINUE

    # 2. "high-temperature" ionization fractions
    #    (using the Opacity Project ionization fractions)
    if C.TEFF < 0.:
        frac1()
        id = C.IDSTD
        C.HPOP = C.DENS[id]/C.WMM[id]/C.YTOT[id]
        #  604 FORMAT(/' N/U  AT THE STANDARD DEPTH  - OP DATA',
        #     * '  (ID =',I3,' ; T,Ne = ',F8.1,1PE12.3,' )'//)
        print()
        print(f" N/U  AT THE STANDARD DEPTH  - OP DATA  (ID ={id:3d}"
              f" ; T,Ne = {C.TEMP[id]:8.1f}{C.ELEC[id]:12.3e} )")
        print()
        for i in range(1, MATOM + 1):      # DO 60 I=1,MATOM
            #  605 FORMAT(1H ,A4,(1P8E9.2))
            # FORMAT 回卷：每 8 个值换一条记录
            line = f" {C.TYPAT[i]:4s}"
            for j in range(1, MION + 1):
                if j > 1 and (j - 1) % 8 == 0:
                    print(line)
                    line = ''
                line += f"{C.RRR[id, j, i]/C.HPOP:9.2e}"
            print(line)
            C.IONIZ[i] = i + 1
    return


def state(id, te, ane, q):
    """
    modified LTE Saha equations - possibly using
    radiation temperatures after
    Schaerer and Schmutz AA 288, 321, 1994

    对应 synspec54.f 行 1953–2047

    原 COMMON 声明：
      common/moltst/pfmol(600,mdepth),anmol(600,mdepth),
                    pfato(100,mdepth),anato(100,mdepth),
                    pfion(100,mdepth),anion(100,mdepth)
      common/ioniz2/anion2(30,mdepth)

    标量哑元 Q 被赋值，按约定返回全部哑元 (id, te, ane, q)。
    """
    ffi = np.zeros(MION0 + 1)              # dimension FFI(MION0)

    q = 0.
    for i in range(1, C.NATOMS + 1):       # DO 50 I=1,NATOMS
        if C.LGR[i]:
            continue                       # GO TO 50
        ion = C.IONIZ[i]
        rq = 0.
        rs = 1.
        t = C.TRAD[C.INPOT[i, 1], id]
        if t <= 0.:
            t = te
        x = math.sqrt(t/ane)
        xmx = 2.145e4*math.sqrt(x)
        # CALL PARTF(I,1,T,ANE,XMX,UM)：PARTF 给标量哑元 U 赋值，
        # 按约定返回全部哑元并重新接收；实参 1 是字面量，
        # 用临时变量 _izi 接收对应返回值
        um = 0.0   # Fortran 中 UM 首次调用前未赋初值
        i, _izi, t, ane, xmx, um = partf(i, 1, t, ane, xmx, um)
        C.PFSTD[1, i] = um
        jmax = 1
        u = 0.0      # Fortran 中 U 首次传入 PARTF 前未赋初值
        for j in range(2, ion + 1):
            j1 = j - 1
            t = C.TRAD[C.INPOT[i, j], id]
            if t <= 0.:
                t = te
            tln = math.log(t)*1.5
            tk = BOLK*t
            thl = 11605./t
            x = math.sqrt(t/ane)
            xmx = 2.145e4*math.sqrt(x)
            dch = EH/xmx/xmx/tk
            dcht = dch*j1
            fi = 36.113 + tln - thl*C.ENEV[i, j1] + dcht
            x = float(j)                   # X=J
            xmax = xmx*math.sqrt(x)
            # CALL PARTF(I,J,T,ANE,XMAX,U)
            i, j, t, ane, xmax, u = partf(i, j, t, ane, xmax, u)
            C.PFSTD[j, i] = u
            fi = math.exp(fi)*u/um/ane
            ffi[j] = fi
            if ffi[j] > 1.:
                jmax = j
            um = u
        if jmax < ion:
            r = 1.
            rq = float(jmax - 1)           # RQ=JMAX-1（整数→实数）
            for j in range(jmax + 1, ion + 1):
                r = r*ffi[j]
                C.RR[i, j] = r/C.PFSTD[j, i]
                rs = rs + r
                rq = rq + (j - 1)*r
        if jmax > 1:
            r = 1.
            for jj in range(1, jmax):      # DO JJ=1,JMAX-1
                j = jmax - jj
                r = r/ffi[j + 1]
                C.RR[i, j] = r/C.PFSTD[j, i]
                rs = rs + r
                rq = rq + (j - 1)*r
        C.ABND[i] = C.ABNDD[i, id]
        C.RR[i, jmax] = C.ABND[i]/rs
        for j in range(1, ion + 1):
            if j != jmax:
                C.RR[i, j] = C.RR[i, j]*C.RR[i, jmax]
            if C.RR[i, j] < 1.e-35:
                C.RR[i, j] = 0.
        C.RR[i, jmax] = C.RR[i, jmax]/C.PFSTD[jmax, i]
        x = rq/rs
        # c        IF(LRM(I)) GO TO 50
        if i > 1:
            q = x*C.ABND[i] + q
        C.anato[i, id] = C.RR[i, 1]*C.PFSTD[1, i]
        C.pfato[i, id] = C.PFSTD[1, i]
        C.anion[i, id] = C.RR[i, 2]*C.PFSTD[2, i]
        C.pfion[i, id] = C.PFSTD[2, i]
        # 50 CONTINUE

    for i in range(2, 31):
        C.anion2[i, id] = C.RR[i, 3]*C.PFSTD[3, i]

    for imol in range(1, 501):
        C.anmol[imol, id] = 0.
        C.pfmol[imol, id] = 0.

    return id, te, ane, q


def tint():
    """
    LOGARITHMIC INTERPOLATION COEFFICIENTS FOR INTERPOLATION OF
    TEMP(ID) TO THE VALUES  5000,10000,20000,40000

    对应 synspec54.f 行 2051–2072
    """
    # DATA TT /3.699, 4.000, 4.301, 4.602/（只读）
    tt = [0.0, 3.699, 4.000, 4.301, 4.602]

    for id in range(1, C.ND + 1):
        t = math.log10(C.TEMP[id])
        j = 3
        if t > tt[3]:
            j = 4
        C.JT[id] = j
        x = (tt[j] - tt[j - 1])*(tt[j] - tt[j - 2])*(tt[j - 1] - tt[j - 2])
        C.TI0[id] = (t - tt[j - 2])*(t - tt[j - 1])*(tt[j - 1] - tt[j - 2])/x
        C.TI1[id] = (t - tt[j - 2])*(tt[j] - t)*(tt[j] - tt[j - 2])/x
        C.TI2[id] = (t - tt[j - 1])*(t - tt[j])*(tt[j] - tt[j - 1])/x
    return
