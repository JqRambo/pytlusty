# chunk17: synspec54.f 行 22330–23917
# DENSIT / TODENS / RHONEN / ELDENS / TIMING / EOSPRI / CIA 不透明度 /
# LOCATE / H2MINUS / H2OPF / VOPF / GVDW / EXOPF / IRWPF

# ---------------------------------------------------------------------------
# 模块级 SAVE 变量（Fortran DATA/SAVE 或依赖静态存储的局部数组，提升至此）
# ---------------------------------------------------------------------------

_save_timing_t0 = 0.0  # TIMING: DATA T0/0./ SAVE T0，之后被修改

_save_eospri_init = 1  # EOSPRI: DATA init/1/，之后被修改

# cia_h2h2: DATA ifirst/0/ 被修改；freq/alpha 首次调用读入、后续调用重用（静态存储）
_save_cia_h2h2_ifirst = 0
_save_cia_h2h2_freq = np.zeros(1001)          # freq(nlines=1000)
_save_cia_h2h2_alpha = np.zeros((1001, 8))    # alpha(nlines,7)

# cia_h2he: 同上
_save_cia_h2he_ifirst = 0
_save_cia_h2he_freq = np.zeros(243)           # freq(nlines=242)
_save_cia_h2he_alpha = np.zeros((243, 8))     # alpha(nlines,7)

# cia_h2h: 同上
_save_cia_h2h_ifirst = 0
_save_cia_h2h_freq = np.zeros(68)             # freq(nlines=67)
_save_cia_h2h_alpha = np.zeros((68, 5))       # alpha(nlines,4)

# cia_hhe: 同上
_save_cia_hhe_ifirst = 0
_save_cia_hhe_freq = np.zeros(44)             # freq(nlines=43)
_save_cia_hhe_alpha = np.zeros((44, 12))      # alpha(nlines,11)

# h2opf: DATA init/1/ 被修改；ttab/pftab 首次调用读入后重用
_save_h2opf_init = 1
_save_h2opf_ttab = np.zeros(10001)
_save_h2opf_pftab = np.zeros(10001)

# vopf: 同上
_save_vopf_init = 1
_save_vopf_ttab = np.zeros(10001)
_save_vopf_pftab = np.zeros(10001)

# exopf: DATA iread/1/ 被修改；ntemp 首次调用时被改写；pf 读入后重用
_save_exopf_iread = 1
_save_exopf_ntemp = np.array([0,  # 1 基索引，元素 0 不用
    9,  10,   8,   3,   9,   3,   3,   8,   3,  10,
    10,   5,   5,   3,   5,   9,   5,   5,   5,   5,
    5,   4,   5,   5,   9,   5,  48,   8,   8,  10,
    3,   5], dtype=np.int64)  # DATA ntemp/.../
_save_exopf_pf = np.zeros((33, 10001))        # pf(nmol=32,10000)

# irwpf: SAVE iread,a,am（显式 SAVE 语句）
_save_irwpf_iread = 0                          # DATA iread/0/
_save_irwpf_a = np.zeros((7, 4, 93))           # a(6,3,92)
_save_irwpf_am = np.zeros((7, 501))            # am(6,500)


def densit(rho, idens):
    """C     ============================
C
C     determining the state parameters for the opacity grid
C     calculations

    对应 synspec54.f 行 22330–22386
    """
    # DIMENSION ES(MLEVEL,MLEVEL),BS(MLEVEL),POPLTE(MLEVEL)
    es = np.zeros((MLEVEL + 1, MLEVEL + 1))
    bs = np.zeros(MLEVEL + 1)
    poplte = np.zeros(MLEVEL + 1)

    id = 1
    C.DM[id] = 0.0
    if C.IFMOL == 0 or C.TEMP[id] > C.TMOLIM:
        C.WMM[id] = C.WMY[id] * HMASS / C.YTOT[id]
    if idens == 0:
        C.ELEC[id] = rho
        ane = C.ELEC[id]
        an = 0.0  # AN 未赋初值传入，TODENS 输出
        id, _t, an, ane = todens(id, C.TEMP[id], an, ane)  # 哑元 T 对应 TEMP(ID)
        C.DENS[id] = (an - ane) * C.WMM[id]
        p = an * BOLK * C.TEMP[id]  # p 之后未使用（原代码如此）
        # WRITE(6,602) ID,TEMP(ID),DENS(ID),ELEC(ID)  （原代码已注释）
    elif idens < 0:
        an = rho / C.TEMP[id] / BOLK
        ane = 0.0  # ANE 未赋初值传入，ELDENS 输出
        id, _t, an, ane = eldens(id, C.TEMP[id], an, ane)
        C.ELEC[id] = ane
        C.DENS[id] = C.WMM[id] * (an - C.ELEC[id])
        # WRITE(6,601) ID,TEMP(ID),DENS(ID),ELEC(ID),ane0,an  （原代码已注释）
    elif idens == 1:
        C.DENS[id] = rho
        an = 0.0
        ane = 0.0
        id, _t, rho, an, ane = rhonen(id, C.TEMP[id], rho, an, ane)
        C.ELEC[id] = ane
        C.DENS[id] = rho
        rho0 = C.WMM[id] * (an - ane)
        # WRITE(6,601) IDens,TEMP(ID),DENS(ID),ane,rho0,an  （原代码已注释）
    elif idens == 2:
        an = 0.0
        ane = 0.0
        id, _t, rho, an, ane = rhonen(id, C.TEMP[id], rho, an, ane)
        C.DENS[id] = rho
        ane = C.ELEC[id]
        rho0 = C.WMM[id] * (an - ane)
        # WRITE(6,601) idens,TEMP(ID),DENS(ID),ane,rho0,an  （原代码已注释）
    # 601 FORMAT(' **densit** t,rho,ne,rho0,an',I3,0PF10.1,1P5D11.3)
    # 602 FORMAT(' **densit** t,rho,ne',I3,0PF10.1,1P5D11.3)

    inimod()

    wnstor(id)
    sabolf(id)
    ratmat(id, es, bs)
    levsol(es, bs, poplte, C.NLEVEL)
    for j in range(1, C.NLEVEL + 1):
        C.POPUL[j, id] = poplte[j]

    return


def todens(id, t, an, ane):
    """C     ==============================
C
C     determines AN (and ANP, AHTOT, and AHMOL) from T and ANE
C
C     Input parameters:
C     T    - temperature
C     ANE  - electron number density
C
C     Output:
C     AN    - total particle density
C     ANP   - proton number density
C     AHTOT - total hydrogen number density
C     AHMOL - relative number of hydrogen molecules with respect to the
C             total number of hydrogens

    对应 synspec54.f 行 22393–22501
    修改标量哑元 AN → 按约定返回全部标量哑元 (id, t, an, ane)
    """
    # common/hydmol/anhmi,ahmol → C.anhmi, C.ahmol
    # parameter (un=1.d0,two=2.d0,half=0.5d0)
    UN = 1.0
    TWO = 2.0
    HALF = 0.5

    qm = 0.0
    q2 = 0.0
    qp = 0.0
    q = 0.0
    dqn = 0.0
    tk = BOLK * t
    thet = 5.0404e3 / t

    # Coefficients entering ionization (dissociation) balance of:
    # atomic hydrogen          - QH;
    # negative hydrogen ion    - QM
    # hydrogen molecule        - QP
    # ion of hydrogen molecule - Q2

    qm = 1.0353e-16 / t / math.sqrt(t) * math.exp(8762.9 / t)
    qh = math.exp((15.38287 + 1.5 * math.log10(t) - 13.595 * thet) * 2.30258509299405)

    if t > 16000.0:
        ih2 = 0
        ih2p = 0
    else:
        qp = tk * math.exp((-11.206998 + thet * (2.7942767 + thet *
             (0.079196803 - 0.024790744 * thet))) * 2.30258509299405)
        q2 = tk * math.exp((-12.533505 + thet * (4.9251644 + thet *
             (-0.056191273 + 0.0032687661 * thet))) * 2.30258509299405)
        ih2 = 1

    # procedure STATE determines Q (and DQN) - the total charge (and its
    # derivative wrt temperature) due to ionization of all atoms which
    # are considered (both explicit and non-explicit), by solving the set
    # of Saha equations for the current values of T and ANE

    id, t, ane, q = state(id, t, ane, q)

    # Auxiliary parameters for evaluating the elements of matrix of
    # linearized equations.
    # Note that complexity of the matrix depends on whether the hydrogen
    # molecule is taken into account
    # Treatment of hydrogen ionization-dissociation is based on
    # Mihalas, in Methods in Comput. Phys. 7, p.10 (1967)

    g2 = qh / ane
    g3 = 0.0
    g4 = 0.0
    g5 = 0.0
    d = 0.0
    e = 0.0
    g3 = qm * ane
    a = UN + g2 + g3
    d = g2 - g3
    it = 0  # TODO(port): IT 在 TODENS 中从未赋值（疑遗漏），按静态零初值处理，IF(IT.LE.1) 恒真
    if it <= 1:
        if ih2 == 0:
            f1 = UN / a
            fe = d / a + q
        else:
            e = g2 * qp / q2
            b = TWO * (UN + e)
            gg = ane * q2
            c1 = b * (gg * b + a * d) - e * a * a
            c2 = a * (TWO * e + b * q) - d * b
            c3 = -e - b * q
            f1 = (math.sqrt(c2 * c2 - 4.0 * c1 * c3) - c2) * HALF / c1
            fe = f1 * d + e * (UN - a * f1) / b + q
        ah = ane / fe
        anh = ah * f1
    ae = anh / ane
    gg = ae * qp
    e = anh * q2
    b = anh * qm

    # S(1)=AN-ANE-YTOT(ID)*AH
    # S(2)=ANH*(D+GG)+Q*AH-ANE
    # S(3)=AH-ANH*(A+TWO*(E+GG))

    hhn = a + TWO * (e + gg)
    anh = ane / (d + gg + q * hhn)
    ah = anh * hhn
    an = ane + C.YTOT[id] * ah

    ahtot = ah  # 局部变量（TODENS 未声明 common/hydato）
    C.ahmol = TWO * anh * (anh * q2 + anh / ane * qp) / ah
    anp = anh / ane * qh  # 局部变量
    return id, t, an, ane


def rhonen(id, t, rho, an, ane):
    """c     ==================================
c
c     iterative determination of N and Ne from given T and RHO
c
C     Input:  T   - temperature
C             RHO - mass density
C     Output: AN  - total particle density
C             ANE - elctron density

    对应 synspec54.f 行 22507–22547
    修改标量哑元 AN、ANE → 返回全部标量哑元 (id, t, rho, an, ane)
    """
    # common/nerela/anerel → C.anerel

    it = 0
    if id == 1 and C.anerel == 0.0:
        C.anerel = 0.5
        if t < 9000.0:
            C.anerel = 0.4
        if t < 8000.0:
            C.anerel = 0.1
        if t < 7000.0:
            C.anerel = 0.01
        if t < 6000.0:
            C.anerel = 0.001
        if t < 5500.0:
            C.anerel = 0.0001
        # if(t.lt.5000.) anerel=1.e-5
        # if(t.lt.4000.) anerel=1.e-6
    while True:  # 标号 10 循环
        it += 1
        an = rho / C.WMM[id] / (1.0 - C.anerel)
        ane0 = C.anerel * an
        id, t, an, ane = eldens(id, t, an, ane)
        C.anerel = ane / an
        # 602 format(/' **** rhonen it,id,t,r,N,Ne,wmm,ner',2i4,f7.0,1p5e11.4)
        print(f"\n **** rhonen it,id,t,r,N,Ne,wmm,ner{it:4d}{id:4d}{t:7.0f}"
              f"{rho:11.4e}{an:11.4e}{ane:11.4e}{C.WMM[id]:11.4e}{C.anerel:11.4e}")
        if abs((ane - ane0) / ane0) < 1.0e-5:
            break  # GO TO 20
        if it < 50:
            continue  # GO TO 10
        break  # 迭代达 50 次未收敛，顺序落入标号 20
        # write(6,601) an,ane,ane0  （原代码已注释）
    # 601 format(/' slow convergence of RHONEN - N,Ne,Nep=',1p3e11.3)
    # 标号 20:

    return id, t, rho, an, ane


def eldens(id, t, an, ane):
    """C     ==============================
C
C     Evaluation of the electron density and the total hydrogen
C     number density for a given total particle number density
C     and temperature;
C     by solving the set of Saha equations, charge conservation and
C     particle conservation equations (by a Newton-Raphson method)
C
C     Input parameters:
C     T    - temperature
C     AN   - total particle number density
C
C     Output:
C     ANE   - electron density
C     ANP   - proton number density
C     AHTOT - total hydrogen number density
C     AHMOL - relativer number of hydrogen molecules with respect to the
C             total number of hydrogens
C     ENERG - part of the internal energy: excitation and ionization

    对应 synspec54.f 行 22552–22761
    修改标量哑元 ANE → 返回全部标量哑元 (id, t, an, ane)
    """
    # common/hydmol/anhmi,ahmol  → C.anhmi, C.ahmol
    # common/hydato/ah,anh,anp   → C.ah, C.anh, C.anp
    # common/nerela/anerel       → C.anerel
    # parameter (un=1.d0,two=2.d0,half=0.5d0)
    UN = 1.0
    TWO = 2.0
    HALF = 0.5
    # DIMENSION R(3,3),S(3),P(3)
    r = np.zeros((4, 4))
    s = np.zeros(4)
    p = np.zeros(4)

    tk = BOLK * t
    if C.IFMOL > 0 and t < C.TMOLIM:
        aein = an * C.anerel
        _ipri = 0  # 实参为字面量 0；moleq 修改标量哑元 ANE，返回全部标量哑元
        id, t, an, aein, ane, _ipri = moleq(id, t, an, aein, ane, _ipri)
        C.anerel = ane / an
        return id, t, an, ane

    qm = 0.0
    q2 = 0.0
    qp = 0.0
    q = 0.0
    dqn = 0.0
    tk = BOLK * t
    thet = 5.0404e3 / t

    # Coefficients entering ionization (dissociation) balance of:
    # atomic hydrogen          - QH;
    # negative hydrogen ion    - QM
    # hydrogen molecule        - Q2
    # ion of hydrogen molecule - QP

    qh0 = 0.0  # TODO(port): IATREF!=IATH 时 QH0 未赋值（隐式零初值），但下面无条件使用
    ih2 = 0    # TODO(port): 同上（IATREF!=IATH 时未赋值）
    if C.IATREF == C.IATH:
        qm = 1.0353e-16 / t / math.sqrt(t) * math.exp(8762.9 / t)
        qh0 = math.exp((15.38287 + 1.5 * math.log10(t) - 13.595 * thet) * 2.30258509299405)

        if t > 16000.0:
            ih2 = 0
        else:
            ih2 = 1
            qp = tk * math.exp((-11.206998 + thet * (2.7942767 + thet *
                 (0.079196803 - 0.024790744 * thet))) * 2.30258509299405)
            q2 = tk * math.exp((-12.533505 + thet * (4.9251644 + thet *
                 (-0.056191273 + 0.0032687661 * thet))) * 2.30258509299405)

    # Initial estimate of the electron density

    if C.anerel <= 0.0:
        if t > 1.0e4:
            C.anerel = 0.5
        else:
            if C.ELEC[id] > 0.0 and C.DENS[id] > 0.0:
                C.anerel = C.ELEC[id] / (C.ELEC[id] + C.DENS[id] / C.WMM[id])
            else:
                C.anerel = 0.1

    ane = an * C.anerel
    it = 0

    # Basic Newton-Raphson loop - solution of the non-linear set
    # for the unknown vector P, consistiong of AH, ANH (neutral
    # hydrogen number density) and ANE.

    # TODO(port): QREF、DQNR 在全程序中无任何声明与赋值（隐式局部量，
    # 仅用于 IATREF!=IATH 分支），按静态零初值处理
    qref = 0.0
    dqnr = 0.0
    delne = 0.0
    while True:  # 标号 10: Newton-Raphson 迭代
        it += 1

        # procedure STATE determines Q (and DQN) - the total charge (and its
        # derivative wrt temperature) due to ionization of all atoms which
        # are considered (both explicit and non-explicit), by solving the set
        # of Saha equations for the current values of T and ANE

        id, t, ane, q = state(id, t, ane, q)
        qh = qh0 * 2.0 / C.PFSTD[1, 1]

        # Auxiliary parameters for evaluating the elements of matrix of
        # linearized equations.
        # Note that complexity of the matrix depends on whether the hydrogen
        # molecule is taken into account
        # Treatment of hydrogen ionization-dissociation is based on
        # Mihalas, in Methods in Comput. Phys. 7, p.10 (1967)

        if C.IATREF == C.IATH:
            g2 = qh / ane
            g3 = 0.0
            g4 = 0.0
            g5 = 0.0
            d = 0.0
            e = 0.0
            g3 = qm * ane
            a = UN + g2 + g3
            d = g2 - g3
            if it <= 1:
                if ih2 == 0:
                    f1 = UN / a
                    fe = d / a + q
                else:
                    e = g2 * qp / q2
                    b = TWO * (UN + e)
                    gg = ane * q2
                    c1 = b * (gg * b + a * d) - e * a * a
                    c2 = a * (TWO * e + b * q) - d * b
                    c3 = -e - b * q
                    f1 = (math.sqrt(c2 * c2 - 4.0 * c1 * c3) - c2) * HALF / c1
                    fe = f1 * d + e * (UN - a * f1) / b + q
                C.ah = ane / fe
                C.anh = C.ah * f1
            ae = C.anh / ane
            gg = ae * qp
            e = C.anh * q2
            b = C.anh * qm

            # Matrix of the linearized system R, and the rhs vector S

            r[1, 1] = C.YTOT[id]
            # R(1,2)=0.  （原代码已注释）
            r[1, 2] = -TWO * (C.anh * q2 + gg)
            r[1, 3] = UN
            r[2, 1] = -q
            r[2, 2] = -d - TWO * gg
            r[2, 3] = UN + b + ae * (g2 + gg) - dqn * C.ah
            r[3, 1] = -UN
            r[3, 2] = a + 4.0 * (C.anh * q2 + gg)
            r[3, 3] = b - ae * (g2 + TWO * gg)
            s[1] = an - ane - C.YTOT[id] * C.ah + C.anh * (C.anh * q2 + gg)
            s[2] = C.anh * (d + gg) + q * C.ah - ane
            s[3] = C.ah - C.anh * (a + TWO * (C.anh * q2 + gg))

            # Solution of the linearized equations for the correction vector P

            lineqs(r, s, p, 3, 3)

            # New values of AH, ANH, and ANE

            C.ah = C.ah + p[1]
            C.anh = C.anh + p[2]
            delne = p[3]
            ane = ane + delne

        # hydrogen is not the reference atom

        else:

            # Matrix of the linearized system R, and the rhs vector S

            if it == 1:
                ane = an * HALF
                C.ah = ane / C.YTOT[id]
            r[1, 1] = C.YTOT[id]
            r[1, 2] = UN
            r[2, 1] = -q - qref
            r[2, 2] = UN - (dqn + dqnr) * C.ah
            s[1] = an - ane - C.YTOT[id] * C.ah
            s[2] = (q + qref) * C.ah - ane

            # Solution of the linearized equations for the correction vector P

            lineqs(r, s, p, 2, 3)
            C.ah = C.ah + p[1]
            delne = p[2]
            ane = ane + delne

        # Convergence criterion

        if ane <= 0.0:
            ane = 1.0e-7 * an
        if abs(delne / ane) > 1.0e-6 and it <= 20:
            continue  # GO TO 10
        break

    # ANEREL is the exact ratio betwen electron density and total
    # particle density, which is going to be used in the subseguent
    # call of ELDENS

    C.anerel = ane / an
    ahtot = C.ah  # 局部变量（ELDENS 未将 AHTOT 放入 COMMON）
    if C.IATREF == C.IATH:
        # AHMOL=TWO*ANH*(ANH*Q2+ANH/ANE*QP)/AH  （原代码已注释）
        C.ahmol = C.anh * C.anh * q2
        C.anp = C.anh / ane * qh
        C.anhmi = C.anh * ane * qm
        anhn = C.anh + C.anp + C.anhmi + 2.0 * C.ahmol
        C.WMM[id] = C.WMY[id] / (C.YTOT[id] - C.ahmol / anhn) * HMASS

    return id, t, an, ane


def timing(mod, iter):
    """C     ===========================
C
C     Timing procedure (call machine dependent routine!!)

    对应 synspec54.f 行 22769–22793
    不修改标量哑元 → 无返回
    """
    global _save_timing_t0
    # CHARACTER ROUT*6
    # dimension dummy(2)
    dummy = np.zeros(3)

    # TODO(port): TIME=etime(dummy) —— etime 为机器相关例程，fortran.py 无对应实现，暂以 0.0 占位
    time = 0.0
    dt = time - _save_timing_t0
    _save_timing_t0 = time
    ip = iter
    rout = ''  # TODO(port): MOD 非 1/2 时 ROUT 未定义（隐式初值），置空串
    if mod == 1:
        rout = ' TABLE'
    elif mod == 2:
        rout = ' FINAL'
    # 600 FORMAT(I6,2F11.2,2X,A6)
    write_line(69, f"{ip:6d}{time:11.2f}{dt:11.2f}  {rout:6s}")
    C.dtim = dt
    return


def eospri():
    """c     =================
c
c     Outprint of Equation of State parameters

    对应 synspec54.f 行 22799–23045
    """
    global _save_eospri_init
    # common/moltst/pfmol,anmol,pfato,anato,pfion,anion → C.pfmol 等
    # common/hydmol/anhmi,ahmol → C.anhmi, C.ahmol
    # common/hydato/ah,anh,anp  → C.ah, C.anh, C.anp
    # common/ioniz2/anion2      → C.anion2
    # dimension nelemx(38) —— DATA，之后不修改
    nelemx = [0,  # 1 基索引
        1, 2, 3, 4, 5, 6, 7, 8, 9,
        11, 12, 13, 14, 15, 16, 17, 19, 20,
        21, 22, 23, 24, 25, 26, 28, 29, 32,
        35, 37, 38, 39, 40, 41, 53, 56, 57, 58, 60]
    # data amh2/.../ —— DATA，之后不修改
    amh2 = [0.0, 1.13390e+01, -2.97499e+00, 4.10842e-02, -3.58550e-03,
            1.31844e-04]
    # data insm/.../ —— DATA，之后不修改
    insm = [0, 2, 3, 4, 5, 6, 7, 8, 12, 17, 25, 29, 30, 32, 34, 122, 126, 134,
            179, 198, 214]
    xml = np.zeros(21)
    # data init/1/ → 模块级 _save_eospri_init（隐含 SAVE，之后被修改）

    # id=idstd （原代码已注释）
    istp = 1
    if C.IFEOS < 0:
        istp = -C.IFEOS

    for id in range(1, C.ND + 1, istp):
        t = C.TEMP[id]
        ane = C.ELEC[id]
        rho = C.DENS[id]
        ann = C.DENS[id] / C.WMM[id] + C.ELEC[id]

        if C.IFMOL == 0 or t > C.TMOLIM:
            it = 0
            while True:  # 标号 10 循环
                ann0 = ann
                it += 1
                id, t, ann, ane = eldens(id, t, ann, ane)
                C.anmol[1, id] = C.anhmi
                C.anmol[2, id] = C.ahmol
                C.anato[1, id] = C.anh
                C.anion[1, id] = C.anp
                hpop = C.DENS[id] / C.WMY[id] / HMASS
                for i in range(1, C.NMETAL + 1):
                    j = nelemx[i]
                    C.anato[j, id] = C.anato[j, id] * hpop
                    C.anion[j, id] = C.anion[j, id] * hpop
                    if 2 <= j <= 30:
                        C.anion2[j, id] = C.anion2[j, id] * hpop
                C.anato[1, id] = C.anh
                C.anion[1, id] = C.anp
                # wmm(id)=(wmy(id)+2.*anmol(2,id)/hpop)/ytot(id)*hmass  （原代码已注释）
                C.WMM[id] = C.WMY[id] / (C.YTOT[id] - C.anmol[2, id] / hpop) * HMASS
                ann = C.DENS[id] / C.WMM[id] + ane
                if (ann - ann0) / ann0 > 1.0e-5:
                    continue  # GO TO 10
                break

        C.NMETAL = 38  # nmetal=38（COMMON /COMFH1/ 变量）
        print('')
        print('atomic number densities and partition functions')
        print('')
        atot = 0.0
        for i in range(1, C.NMETAL + 1):
            j = nelemx[i]
            # 621 format(i4,a3,3x,1p2e12.4)
            if j <= 28:
                print(f"{j:4d}{C.TYPAT[j][:3]:3s}   {C.anato[j, id]:12.4e}{C.pfato[j, id]:12.4e}")
            atot = atot + C.anato[j, id]
        print('')
        print('ionic number densities and partition functions')
        print('')
        ctot = 0.0
        for i in range(1, C.NMETAL + 1):
            j = nelemx[i]
            # 622 format(i4,a3,'+',2x,1p2e12.4)
            if j <= 28:
                print(f"{j:4d}{C.TYPAT[j][:3]:3s}+  {C.anion[j, id]:12.4e}{C.pfion[j, id]:12.4e}")
            atot = atot + C.anion[j, id]
            ctot = ctot + C.anion[j, id]

        if C.IFMOL > 0 and t <= C.TMOLIM:
            # 600 format(/ 'Molecular number densities and partition functions'/)
            print('\nMolecular number densities and partition functions\n')
            for i in range(1, C.NMOLEC + 1):
                # 601 format(i4,1x,A8,1x,1pe12.4,1x,e12.4)
                if C.anmol[i, id] > ann * 1.0e-15:
                    print(f"{i:4d} {C.CMOL[i]:8s} {C.anmol[i, id]:12.4e} {C.pfmol[i, id]:12.4e}")
                atot = atot + C.anmol[i, id]

        ahmi = 1.0353e-16 / t / math.sqrt(t) * math.exp(8762.9 / t) * \
               C.anato[1, id] * ane

        # original B&C H2+

        aplogj = amh2[5]
        te = 5040.0 / t
        for k in range(1, 5):
            km5 = 5 - k
            aplogj = aplogj * te + amh2[km5]
        tk = 1.38054e-16 * t
        ph2 = -aplogj + math.log10(C.anato[1, id] * C.anion[1, id]) + 2.0 * math.log10(tk)
        anh2b = (10.0 ** ph2) / tk

        htot = (C.anato[1, id] + C.anion[1, id] + C.anmol[1, id] +
                2.0 * (C.anmol[2, id] + C.anmol[3, id]) + C.anmol[4, id] + C.anmol[5, id] +
                C.anmol[12, id] + 2.0 * C.anmol[13, id] + C.anmol[14, id] +
                C.anmol[15, id] +
                C.anmol[16, id] + C.anmol[17, id] + C.anmol[32, id] + C.anmol[34, id] +
                4.0 * C.anmol[37, id] + 2.0 * C.anmol[38, id] + 3.0 * C.anmol[39, id] +
                2.0 * C.anmol[40, id] + 3.0 * C.anmol[41, id] + 2.0 * C.anmol[57, id] +
                C.anmol[118, id] + C.anmol[133, id] +
                2.0 * C.anmol[140, id] + 3.0 * C.anmol[141, id] + 4.0 * C.anmol[142, id] +
                C.anmol[148, id] + 2.0 * C.anmol[149, id] + C.anmol[222, id])
        ahe = (C.anato[2, id] + C.anion[2, id] + C.anion2[2, id]) / htot
        aca = (C.anato[6, id] + C.anion[6, id] + C.anion2[6, id]) / htot
        acm = (C.anmol[5, id] + C.anmol[6, id] +
               C.anmol[7, id] + 2.0 * (C.anmol[8, id] + 2.0 * C.anmol[13, id]) +
               C.anmol[14, id] + 2.0 * C.anmol[15, id] + C.anmol[20, id] +
               C.anmol[37, id] + C.anmol[38, id] + C.anmol[39, id] +
               C.anmol[44, id] + C.anmol[118, id] + C.anmol[119, id] +
               C.anmol[437, id] + C.anmol[453, id]
               ) / htot
        ana = (C.anato[7, id] + C.anion[7, id] + C.anion2[7, id]) / htot
        anm = (C.anmol[7, id] + 2.0 * C.anmol[9, id] + C.anmol[11, id] +
               C.anmol[12, id] + C.anmol[14, id] + C.anmol[23, id] +
               C.anmol[24, id] + C.anmol[40, id] + C.anmol[41, id] +
               C.anmol[109, id] + C.anmol[152, id] + C.anmol[347, id] +
               C.anmol[438, id] + C.anmol[452, id] + C.anmol[454, id]
               ) / htot
        aoa = (C.anato[8, id] + C.anion[8, id] + C.anion2[8, id]) / htot
        aom = (C.anmol[3, id] + C.anmol[4, id] +
               C.anmol[6, id] + 2.0 * C.anmol[10, id] + C.anmol[11, id] + C.anmol[25, id] +
               C.anmol[26, id] + C.anmol[29, id] + C.anmol[30, id] + C.anmol[31, id] +
               C.anmol[35, id] + 2.0 * C.anmol[44, id] + C.anmol[49, id] + C.anmol[51, id] +
               C.anmol[54, id] + 2.0 * C.anmol[56, id] + C.anmol[65, id] +
               2.0 * C.anmol[66, id] + C.anmol[84, id] + C.anmol[109, id] +
               C.anmol[113, id] + C.anmol[115, id] + C.anmol[118, id] +
               C.anmol[119, id] + C.anmol[126, id] + C.anmol[134, id] +
               C.anmol[153, id] + C.anmol[179, id] + C.anmol[184, id] +
               2.0 * C.anmol[185, id] + C.anmol[200, id] + C.anmol[216, id] +
               C.anmol[221, id] + 2.0 * C.anmol[247, id] + C.anmol[292, id] +
               C.anmol[439, id] + C.anmol[453, id] + C.anmol[454, id]
               ) / htot
        ac = aca + acm
        an = ana + anm
        ao = aoa + aom
        # 623 format(/'EOS useful quantities - summary'//
        #      'T,rho       ',f13.2,1pe13.5/
        #      'N           ',1p2e13.5/
        #      'n_e         ',1p2e13.5/
        #      'H,H+,H-,H2  ',1p4e13.5/
        #      'H2-,H2+,H2+b',1p3e13.5/
        #      'Htot        ',1pe13.5/
        #      'H-          ',1p3e13.5/
        #      'C,C+,CO,CH4 ',1p4e13.5/
        #      'N,N+,N2,NH3 ',1p4e13.5/
        #      'O,O+,H2O,CO ',1p4e13.5/
        #      'He/H        ',1p2e13.5/
        #      'C/H         ',1p2e13.5/
        #      'N/H         ',1p2e13.5/
        #      'O/H         ',1p2e13.5/)
        print(f"\nEOS useful quantities - summary\n"
              f"\nT,rho       {t:13.2f}{C.DENS[id]:13.5e}"
              f"\nN           {ann:13.5e}{atot + ane:13.5e}"
              f"\nn_e         {ane:13.5e}{ctot - C.anmol[1, id]:13.5e}"
              f"\nH,H+,H-,H2  {C.anato[1, id]:13.5e}{C.anion[1, id]:13.5e}"
              f"{C.anmol[1, id]:13.5e}{C.anmol[2, id]:13.5e}"
              f"\nH2-,H2+,H2+b{C.anmol[312, id]:13.5e}{C.anmol[426, id]:13.5e}{anh2b:13.5e}"
              f"\nHtot        {htot:13.5e}"
              f"\nH-          {C.anmol[1, id]:13.5e}{ahmi:13.5e}{C.anmol[1, id] / ahmi:13.5e}"
              f"\nC,C+,CO,CH4 {C.anato[6, id]:13.5e}{C.anion[6, id]:13.5e}"
              f"{C.anmol[6, id]:13.5e}{C.anmol[37, id]:13.5e}"
              f"\nN,N+,N2,NH3 {C.anato[7, id]:13.5e}{C.anion[7, id]:13.5e}"
              f"{C.anmol[9, id]:13.5e}{C.anmol[41, id]:13.5e}"
              f"\nO,O+,H2O,CO {C.anato[8, id]:13.5e}{C.anion[8, id]:13.5e}"
              f"{C.anmol[3, id]:13.5e}{C.anmol[6, id]:13.5e}"
              f"\nHe/H        {ahe:13.5e}{ahe / C.ABNDD[2, id]:13.5e}"
              f"\nC/H         {ac:13.5e}{ac / C.ABNDD[6, id]:13.5e}"
              f"\nN/H         {an:13.5e}{an / C.ABNDD[7, id]:13.5e}"
              f"\nO/H         {ao:13.5e}{ao / C.ABNDD[8, id]:13.5e}")
        act = ac * htot
        ant = an * htot
        aot = ao * htot

        if _save_eospri_init == 1:
            # 625 format('    T      rho     w_mol    Ne/Ntot  N(Htot)    '
            # 'n(H)   n(H2)',6x,
            # 'a(He)   a(C)    a(N)    a(O)   molfr(C) molfr(N) molfr(O)'/)
            write_line(52, '    T      rho     w_mol    Ne/Ntot  N(Htot)    '
                       'n(H)   n(H2)' + ' ' * 6 +
                       'a(He)   a(C)    a(N)    a(O)   molfr(C) molfr(N) molfr(O)')
            write_line(52, '')
            # 626 format('    T      rho     w_mol      N        Ne     N(Htot)   ',
            # 'N(H)    N(H+)    N(H-)   N(H2)    N(H2-)    N(H2+)'/)
            write_line(51, '    T      rho     w_mol      N        Ne     N(Htot)   '
                       'N(H)    N(H+)    N(H-)   N(H2)    N(H2-)    N(H2+)')
            write_line(51, '')
            # 653 format(' log10(N/U)'/'   T     rho   ',20a6/)
            write_line(53, ' log10(N/U)')
            write_line(53, '   T     rho   ' +
                       ''.join(f"{C.CMOL[insm[i]][:6]:6s}" for i in range(1, 21)))
            write_line(53, '')
            # 654 format(' log10[N/n(H)]'/'   T     rho   ',20a6/)
            write_line(54, ' log10[N/n(H)]')
            write_line(54, '   T     rho   ' +
                       ''.join(f"{C.CMOL[insm[i]][:6]:6s}" for i in range(1, 21)))
            write_line(54, '')

            _save_eospri_init = 0

        # write(51,624) ...  （原代码已注释的版本略，见 624 format 注释）
        # 624 format(f8.1,1pe9.2,0pf8.5,1x,1p4e9.2,1x,0p4f8.5,1x,1p3e9.2,1x,
        #      3e9.2,1x,3e9.2)
        write_line(52, f"{t:8.1f}{C.DENS[id]:9.2e}{C.WMM[id] / HMASS:8.5f} "
                   f"{ane / ann:9.2e}{htot:9.2e}{C.anato[1, id]:9.2e}{2.0 * C.anmol[2, id]:9.2e} "
                   f"{ahe / C.ABNDD[2, id]:8.5f}{ac / C.ABNDD[6, id]:8.5f}"
                   f"{an / C.ABNDD[7, id]:8.5f}{ao / C.ABNDD[8, id]:8.5f} "
                   f"{acm / ac:9.2e}{anm / an:9.2e}{aom / ao:9.2e}")

        # 627 format(f8.1,1pe9.2,0pf8.5,1x,1p10e9.2)
        write_line(51, f"{t:8.1f}{C.DENS[id]:9.2e}{C.WMM[id] / HMASS:8.5f} "
                   f"{ann:9.2e}{ane:9.2e}{htot:9.2e}"
                   f"{C.anato[1, id]:9.2e}{C.anion[1, id]:9.2e}{C.anmol[1, id]:9.2e}"
                   f"{C.anmol[2, id]:9.2e}{C.anmol[312, id]:9.2e}{C.anmol[426, id]:9.2e}")

        if C.IFMOL > 0 and t <= C.TMOLIM:
            for i in range(1, 21):
                im = insm[i]
                xml[i] = math.log10(C.anmol[im, id] / C.pfmol[im, id])
            # 655 format(2f6.1,1x,20f6.1)
            write_line(53, f"{t:6.1f}{math.log10(C.DENS[id]):6.1f} " +
                       ''.join(f"{xml[i]:6.1f}" for i in range(1, 21)))
            for i in range(1, 21):
                im = insm[i]
                xml[i] = math.log10(C.anmol[im, id] / htot)
                # xml(i)=log10(anmol(im,id))  （原代码已注释）
            write_line(54, f"{t:6.1f}{math.log10(C.DENS[id]):6.1f} " +
                       ''.join(f"{xml[i]:6.1f}" for i in range(1, 21)))

    return


def cia_h2h2(t, ah2, ff, opac):
    """c     ===================--=============
c
c     CIA H2-H2 opacity
c     data from Borysow A., Jorgensen U.G., Fu Y. 2001, JQSRT 68, 235

    对应 synspec54.f 行 23052–23140
    修改标量哑元 OPAC → 返回全部标量哑元 (t, ah2, ff, opac)
    """
    global _save_cia_h2h2_ifirst
    # IMPLICIT REAL*8(A-H,O-Z)
    nlines = 1000  # parameter (nlines=1000)
    ntemp = 7      # data ntemp /7/
    # data temp / 1000.,2000.,3000.,4000.,5000.,6000.,7000. /（DATA，不修改）
    temp = np.array([0.0, 1000.0, 2000.0, 3000.0, 4000.0, 5000.0, 6000.0, 7000.0])
    amagat = 2.6867774e+19  # parameter (amagat=2.6867774d+19,fac=1./amagat**2)
    fac = 1.0 / amagat ** 2
    cas = 2.997925e10  # PARAMETER (CAS=2.997925D10)
    freq = _save_cia_h2h2_freq    # 模块级 SAVE 数组别名
    alpha = _save_cia_h2h2_alpha

    # input frequency in Hz but needed wave numbers in cm^-1
    f = ff / cas
    # read in CIA tables if this is the first call
    if _save_cia_h2h2_ifirst == 0:
        print('Reading in H2-H2 CIA opacity tables...')
        open_unit(10, './data/CIA_H2H2.dat', 'r')  # status='old'
        for i in range(1, 4):
            read_line(10)
        for i in range(1, nlines + 1):
            _p = read_line(10).split()  # read (10,*) freq(i),(alpha(i,j),j=1,ntemp)
            freq[i] = float(_p[0])
            for j in range(1, ntemp + 1):
                alpha[i, j] = float(_p[j])
        close_unit(10)

        # take logarithm of tables prior to doing linear interpolations

        for i in range(1, nlines + 1):
            for j in range(1, ntemp + 1):
                alpha[i, j] = math.log(alpha[i, j])

        _save_cia_h2h2_ifirst = 1

    # locate position in temperature array
    j = 0
    ntemp, t, j, ntemp = locate(temp, ntemp, t, j, ntemp)

    if j == 0:
        print()
        # write(*,'(a,f6.0,a)') 'Warning: requested temperature is below',temp(1),' K'
        print(f'Warning: requested temperature is below{temp[1]:6.0f} K')
        print('CIA H2-H2 opacity set to 0')
        print()
        opac = 0.0
        return t, ah2, ff, opac

    # locate position in frequency array
    i = 0
    nlines, f, i, nlines = locate(freq, nlines, f, i, nlines)

    # linearly interpolate in frequency and temperature

    if j == ntemp:
        # hold values constant if off high temperature end of table
        y1 = alpha[i, j]
        y2 = alpha[i + 1, j]
        tt = (f - freq[i]) / (freq[i + 1] - freq[i])
        alp = (1.0 - tt) * y1 + tt * y2
    elif i == 0 or i == nlines:
        # set values to a very small number if off frequency table
        alp = -50.0
    else:
        # interpolate linearly within table
        y1 = alpha[i, j]
        y2 = alpha[i + 1, j]
        y3 = alpha[i + 1, j + 1]
        y4 = alpha[i, j + 1]

        tt = (f - freq[i]) / (freq[i + 1] - freq[i])
        uu = (t - temp[j]) / (temp[j + 1] - temp[j])

        alp = ((1.0 - tt) * (1.0 - uu) * y1 + tt * (1.0 - uu) * y2 + tt * uu * y3 +
               (1.0 - tt) * uu * y4)

    alp = math.exp(alp)

    # final opacity

    opac = fac * ah2 * ah2 * alp

    return t, ah2, ff, opac


def locate(xx, n, x, j, nxdim):
    """c     =================================
    （二分查表定位例程）

    对应 synspec54.f 行 23149–23174
    修改标量哑元 J → 返回全部标量哑元 (n, x, j, nxdim)
    """
    # IMPLICIT REAL*8(A-H,O-Z)
    # dimension xx(nxdim)

    jl = 0
    ju = n + 1
    while ju - jl > 1:  # 标号 10 循环
        jm = idiv(ju + jl, 2)  # Fortran 整数除法
        if (xx[n] >= xx[1]) == (x >= xx[jm]):  # .EQV.
            jl = jm
        else:
            ju = jm
    if x == xx[1]:
        j = 1
    elif x == xx[n]:
        j = n - 1
    else:
        j = jl
    return n, x, j, nxdim


def cia_h2he(t, ah2, ahe, ff, opac):
    """c     ======================================
c
c     CIA H2-He opacity
c     data from Jorgensen U.G., Hammer D., Borysow A., Falkesgaard J., 2000,
c     Astronomy & Astrophysics 361, 283

    对应 synspec54.f 行 23182–23271
    修改标量哑元 OPAC → 返回全部标量哑元 (t, ah2, ahe, ff, opac)
    """
    global _save_cia_h2he_ifirst
    nlines = 242  # parameter (nlines=242)
    ntemp = 7     # data ntemp /7/
    temp = np.array([0.0, 1000.0, 2000.0, 3000.0, 4000.0, 5000.0, 6000.0, 7000.0])
    amagat = 2.6867774e+19
    fac = 1.0 / amagat ** 2
    cas = 2.997925e10
    freq = _save_cia_h2he_freq
    alpha = _save_cia_h2he_alpha

    # input frequency in Hz but needed wave numbers in cm^-1
    f = ff / cas
    # read in CIA tables if this is the first call
    if _save_cia_h2he_ifirst == 0:
        print('Reading in H2-He CIA opacity tables...')
        open_unit(10, './data/CIA_H2He.dat', 'r')  # status='old'
        for i in range(1, 4):
            read_line(10)
        for i in range(1, nlines + 1):
            _p = read_line(10).split()
            freq[i] = float(_p[0])
            for j in range(1, ntemp + 1):
                alpha[i, j] = float(_p[j])
        close_unit(10)

        # take logarithm of tables prior to doing linear interpolations

        for i in range(1, nlines + 1):
            for j in range(1, ntemp + 1):
                alpha[i, j] = math.log(alpha[i, j])

        _save_cia_h2he_ifirst = 1

    # locate position in temperature array
    j = 0
    ntemp, t, j, ntemp = locate(temp, ntemp, t, j, ntemp)

    if j == 0:
        print()
        print(f'Warning: requested temperature is below{temp[1]:6.0f} K')
        print('CIA H2-He opacity set to 0')
        print()
        opac = 0.0
        return t, ah2, ahe, ff, opac

    # locate position in frequency array
    i = 0
    nlines, f, i, nlines = locate(freq, nlines, f, i, nlines)

    # linearly interpolate in frequency and temperature

    if j == ntemp:
        # hold values constant if off high temperature end of table
        y1 = alpha[i, j]
        y2 = alpha[i + 1, j]
        tt = (f - freq[i]) / (freq[i + 1] - freq[i])
        alp = (1.0 - tt) * y1 + tt * y2
    elif i == 0 or i == nlines:
        # set values to a very small number if off frequency table
        alp = -50.0
    else:
        # interpolate linearly within table
        y1 = alpha[i, j]
        y2 = alpha[i + 1, j]
        y3 = alpha[i + 1, j + 1]
        y4 = alpha[i, j + 1]

        tt = (f - freq[i]) / (freq[i + 1] - freq[i])
        uu = (t - temp[j]) / (temp[j + 1] - temp[j])

        alp = ((1.0 - tt) * (1.0 - uu) * y1 + tt * (1.0 - uu) * y2 + tt * uu * y3 +
               (1.0 - tt) * uu * y4)

    alp = math.exp(alp)

    # final opacity

    opac = fac * ah2 * ahe * alp

    return t, ah2, ahe, ff, opac


def cia_h2h(t, ah2, ah, ff, opac):
    """c     ====================================
c
c     CIA H2-H opacity - data taken from TURBOSPEC

    对应 synspec54.f 行 23278–23364
    修改标量哑元 OPAC → 返回全部标量哑元 (t, ah2, ah, ff, opac)
    """
    global _save_cia_h2h_ifirst
    nlines = 67  # parameter (nlines=67)
    ntemp = 4    # data ntemp /4/
    temp = np.array([0.0, 1000.0, 1500.0, 2000.0, 2500.0])
    amagat = 2.6867774e+19
    fac = 1.0 / amagat ** 2
    cas = 2.997925e10
    freq = _save_cia_h2h_freq
    alpha = _save_cia_h2h_alpha

    # input frequency in Hz but needed wave numbers in cm^-1
    f = ff / cas
    # read in CIA tables if this is the first call
    if _save_cia_h2h_ifirst == 0:
        print('Reading in H2-H CIA opacity tables...')
        open_unit(10, './data/CIA_H2H.dat', 'r')  # status='old'
        for i in range(1, 4):
            read_line(10)
        for i in range(1, nlines + 1):
            _p = read_line(10).split()
            freq[i] = float(_p[0])
            for j in range(1, ntemp + 1):
                alpha[i, j] = float(_p[j])
        close_unit(10)

        # take logarithm of tables prior to doing linear interpolations

        for i in range(1, nlines + 1):
            for j in range(1, ntemp + 1):
                alpha[i, j] = math.log(alpha[i, j])

        _save_cia_h2h_ifirst = 1

    # locate position in temperature array
    j = 0
    ntemp, t, j, ntemp = locate(temp, ntemp, t, j, ntemp)

    if j == 0:
        print()
        print(f'Warning: requested temperature is below{temp[1]:6.0f} K')
        print('CIA H2-H opacity set to 0')
        print()
        opac = 0.0
        return t, ah2, ah, ff, opac

    # locate position in frequency array
    i = 0
    nlines, f, i, nlines = locate(freq, nlines, f, i, nlines)

    # linearly interpolate in frequency and temperature

    if j == ntemp:
        # hold values constant if off high temperature end of table
        y1 = alpha[i, j]
        y2 = alpha[i + 1, j]
        tt = (f - freq[i]) / (freq[i + 1] - freq[i])
        alp = (1.0 - tt) * y1 + tt * y2
    elif i == 0 or i == nlines:
        # set values to a very small number if off frequency table
        alp = -50.0
    else:
        # interpolate linearly within table
        y1 = alpha[i, j]
        y2 = alpha[i + 1, j]
        y3 = alpha[i + 1, j + 1]
        y4 = alpha[i, j + 1]

        tt = (f - freq[i]) / (freq[i + 1] - freq[i])
        uu = (t - temp[j]) / (temp[j + 1] - temp[j])

        alp = ((1.0 - tt) * (1.0 - uu) * y1 + tt * (1.0 - uu) * y2 + tt * uu * y3 +
               (1.0 - tt) * uu * y4)

    alp = math.exp(alp)

    # final opacity

    opac = fac * ah2 * ah * alp

    return t, ah2, ah, ff, opac


def cia_hhe(t, ah, ahe, ff, opac):
    """c     ====================================
c
c     CIA H-He opacity
c     data from Gustafsson M., Frommhold, L. 2001, ApJ 546, 1168

    对应 synspec54.f 行 23371–23459
    修改标量哑元 OPAC → 返回全部标量哑元 (t, ah, ahe, ff, opac)
    """
    global _save_cia_hhe_ifirst
    nlines = 43  # parameter (nlines=43)
    ntemp = 11   # data ntemp /11/
    # data temp / 1000.,1500.,2250.,3000.,4000.,5000.,6000.,7000.,8000.,9000.,10000./
    temp = np.array([0.0, 1000.0, 1500.0, 2250.0, 3000.0, 4000.0, 5000.0,
                     6000.0, 7000.0, 8000.0, 9000.0, 10000.0])
    amagat = 2.6867774e+19
    fac = 1.0 / amagat ** 2
    cas = 2.997925e10
    freq = _save_cia_hhe_freq
    alpha = _save_cia_hhe_alpha

    # input frequency in Hz but needed wave numbers in cm^-1
    f = ff / cas
    # read in CIA tables if this is the first call
    if _save_cia_hhe_ifirst == 0:
        print('Reading in H-He CIA opacity tables...')
        open_unit(10, './data/CIA_HHe.dat', 'r')  # status='old'
        for i in range(1, 4):
            read_line(10)
        for i in range(1, nlines + 1):
            _p = read_line(10).split()
            freq[i] = float(_p[0])
            for j in range(1, ntemp + 1):
                alpha[i, j] = float(_p[j])
        close_unit(10)

        # take logarithm of tables prior to doing linear interpolations

        for i in range(1, nlines + 1):
            for j in range(1, ntemp + 1):
                alpha[i, j] = math.log(alpha[i, j])

        _save_cia_hhe_ifirst = 1

    # locate position in temperature array
    j = 0
    ntemp, t, j, ntemp = locate(temp, ntemp, t, j, ntemp)

    if j == 0:
        print()
        print(f'Warning: requested temperature is below{temp[1]:6.0f} K')
        print('CIA H-He opacity set to 0')
        print()
        opac = 0.0
        return t, ah, ahe, ff, opac

    # locate position in frequency array
    i = 0
    nlines, f, i, nlines = locate(freq, nlines, f, i, nlines)

    # linearly interpolate in frequency and temperature

    if j == ntemp:
        # hold values constant if off high temperature end of table
        y1 = alpha[i, j]
        y2 = alpha[i + 1, j]
        tt = (f - freq[i]) / (freq[i + 1] - freq[i])
        alp = (1.0 - tt) * y1 + tt * y2
    elif i == 0 or i == nlines:
        # set values to a very small number if off frequency table
        alp = -50.0
    else:
        # interpolate linearly within table
        y1 = alpha[i, j]
        y2 = alpha[i + 1, j]
        y3 = alpha[i + 1, j + 1]
        y4 = alpha[i, j + 1]

        tt = (f - freq[i]) / (freq[i + 1] - freq[i])
        uu = (t - temp[j]) / (temp[j + 1] - temp[j])

        alp = ((1.0 - tt) * (1.0 - uu) * y1 + tt * (1.0 - uu) * y2 + tt * uu * y3 +
               (1.0 - tt) * uu * y4)

    alp = math.exp(alp)

    # final opacity

    opac = fac * ah * ahe * alp

    return t, ah, ahe, ff, opac


def h2minus(t, anh2, ane, fr, oph2m):
    """C     =======================================
C
C     H- free-free opacity
C
C     data from K L Bell 1980 J. Phys. B: At. Mol. Phys. 13 1859, Table 1
C     The first column is theta=5040/T(K)
C     The first row are names for each row corresponding to lambda (angstroms)
C     The last row for 10.0 is linearly extrapolated
C     The units of everything else is 10^26 cm4/dyn-1

    对应 synspec54.f 行 23465–23563
    修改标量哑元 OPH2M → 返回全部标量哑元 (t, anh2, ane, fr, oph2m)
    """
    # dimension FFthet(9),FFlamb(18),FFkapp(18,9) —— 全部 DATA，之后不修改
    ffthet = np.array([0.0, 0.5, 0.8, 1.0, 1.2, 1.6, 2.0,
                       2.8, 3.6, 10.0])
    nthet = 9   # data nthet /9/
    fflamb = np.array([0.0, 151883.0, 113913.0, 91130.0, 60753.0,
                       45565.0, 36452.0, 30377.0, 22783.0,
                       18226.0, 15188.0, 11391.0, 9113.0, 7594.0,
                       6509.0, 5696.0, 5063.0, 4142.0, 3505.0])
    nlamb = 18  # data nlamb /18/
    # DATA FFkapp/.../ —— Fortran 按列优先填充，用 order='F' 保持 1 基索引语义
    ffkapp = np.zeros((19, 10))
    ffkapp[1:19, 1:10] = np.array([
        7.16e+01, 4.03e+01, 2.58e+01, 1.15e+01, 6.47e+00,
        4.15e+00, 2.89e+00, 1.63e+00, 1.05e+00, 7.36e-01,
        4.20e-01, 2.73e-01, 1.92e-01, 1.43e-01, 1.10e-01,
        8.70e-02, 5.84e-02, 4.17e-02, 9.23e+01, 5.20e+01,
        3.33e+01, 1.48e+01, 8.37e+00, 5.38e+00, 3.76e+00,
        2.14e+00, 1.39e+00, 9.75e-01, 5.64e-01, 3.71e-01,
        2.64e-01, 1.98e-01, 1.54e-01, 1.24e-01, 8.43e-02,
        6.10e-02, 1.01e+02, 5.70e+01, 3.65e+01, 1.63e+01,
        9.20e+00, 5.92e+00, 4.14e+00, 2.36e+00, 1.54e+00,
        1.09e+00, 6.35e-01, 4.22e-01, 3.03e-01, 2.30e-01,
        1.80e-01, 1.46e-01, 1.01e-01, 7.34e-02, 1.08e+02,
        6.08e+01, 3.90e+01, 1.74e+01, 9.84e+00, 6.35e+00,
        4.44e+00, 2.55e+00, 1.66e+00, 1.18e+00, 6.97e-01,
        4.67e-01, 3.39e-01, 2.59e-01, 2.06e-01, 1.67e-01,
        1.17e-01, 8.59e-02, 1.18e+02, 6.65e+01, 4.27e+01,
        1.91e+01, 1.08e+01, 6.99e+00, 4.91e+00, 2.84e+00,
        1.87e+00, 1.34e+00, 8.06e-01, 5.52e-01, 4.08e-01,
        3.17e-01, 2.55e-01, 2.10e-01, 1.49e-01, 1.11e-01,
        1.26e+02, 7.08e+01, 4.54e+01, 2.04e+01, 1.16e+01,
        7.50e+00, 5.28e+00, 3.07e+00, 2.04e+00, 1.48e+00,
        9.09e-01, 6.33e-01, 4.76e-01, 3.75e-01, 3.05e-01,
        2.53e-01, 1.82e-01, 1.37e-01, 1.38e+02, 7.76e+01,
        4.98e+01, 2.24e+01, 1.28e+01, 8.32e+00, 5.90e+00,
        3.49e+00, 2.36e+00, 1.74e+00, 1.11e+00, 7.97e-01,
        6.13e-01, 4.92e-01, 4.06e-01, 3.39e-01, 2.49e-01,
        1.87e-01, 1.47e+02, 8.30e+01, 5.33e+01, 2.40e+01,
        1.38e+01, 9.02e+00, 6.44e+00, 3.90e+00, 2.68e+00,
        2.01e+00, 1.32e+00, 9.63e-01, 7.51e-01, 6.09e-01,
        5.07e-01, 4.27e-01, 3.16e-01, 2.40e-01, 2.19e+02,
        1.26e+02, 8.13e+01, 3.68e+01, 2.18e+01, 1.46e+01,
        1.08e+01, 7.18e+00, 5.24e+00, 4.17e+00, 3.00e+00,
        2.29e+00, 1.86e+00, 1.55e+00, 1.32e+00, 1.13e+00,
        8.52e-01, 6.64e-01]).reshape((18, 9), order='F')

    # locate position in temperature array
    theta = 5040.0 / t

    j = 0
    nthet, theta, j, nthet = locate(ffthet, nthet, theta, j, nthet)
    if j == 0:
        print()
        # write(*,'(a,f6.0,a)') 'Error: requested temperature is outside the ranges'
        print('Error: requested temperature is outside the ranges')
        print('h2minus:Stop')
        print()
        raise SystemExit  # STOP
    flamb = CL * 1.0e8 / fr
    # locate position in wavelength array
    i = 0
    nlamb, flamb, i, nlamb = locate(fflamb, nlamb, flamb, i, nlamb)

    # linearly interpolate in frequency and temperature
    # TODO(port): 下面的 nlines 在本子程序中从未声明/赋值（疑为 nlamb 笔误），按隐式零初值处理
    nlines = 0
    if j == nthet:
        # hold values constant if off high temperature end of table
        y1 = ffkapp[i, j]
        y2 = ffkapp[i + 1, j]
        tt = (flamb - fflamb[i]) / (fflamb[i + 1] - fflamb[i])
        fkappa = (1.0 - tt) * y1 + tt * y2
    elif i == 0 or i == nlines:
        # set values to 0 if off frequency table
        fkappa = 0.0
    else:
        # interpolate linearly within table
        y1 = ffkapp[i, j]
        y2 = ffkapp[i + 1, j]
        y3 = ffkapp[i + 1, j + 1]
        y4 = ffkapp[i, j + 1]

        tt = (flamb - fflamb[i]) / (fflamb[i + 1] - fflamb[i])
        uu = (theta - ffthet[j]) / (ffthet[j + 1] - ffthet[j])

        fkappa = ((1.0 - tt) * (1.0 - uu) * y1 + tt * (1.0 - uu) * y2 + tt * uu * y3 +
                  (1.0 - tt) * uu * y4)
    pe = ane * BOLK * t
    oph2m = anh2 * 1.0e-26 * pe * fkappa
    return t, anh2, ane, fr, oph2m


def h2opf(t, pf):
    """c
c     partition function for H2Ofrom EXOMOILA data

    对应 synspec54.f 行 23569–23590
    修改标量哑元 PF → 返回全部标量哑元 (t, pf)
    """
    global _save_h2opf_init
    ttab = _save_h2opf_ttab    # dimension ttab(10000)，模块级 SAVE 别名
    pftab = _save_h2opf_pftab

    # data init /1/ → 模块级 _save_h2opf_init
    if _save_h2opf_init == 1:
        open_unit(67, './data/h2o_exomol.pf', 'r')  # status='old'
        for i in range(1, 10001):
            _p = read_line(67).split()  # read(67,*) ttab(i),pftab(i)
            ttab[i] = float(_p[0])
            pftab[i] = float(_p[1])
        close_unit(67)
        _save_h2opf_init = 0

    itab = int(t)  # IFIX(REAL(T)) 向零截断
    pf = pftab[itab] + (t - ttab[itab]) * (pftab[itab + 1] - pftab[itab])
    return t, pf


def vopf(t, pf):
    """c
c     partition function for VO from EXOMOILA data

    对应 synspec54.f 行 23597–23618
    修改标量哑元 PF → 返回全部标量哑元 (t, pf)
    """
    global _save_vopf_init
    ttab = _save_vopf_ttab
    pftab = _save_vopf_pftab

    if _save_vopf_init == 1:
        open_unit(67, './data/vo_exomol.pf', 'r')  # status='old'
        for i in range(1, 8001):
            _p = read_line(67).split()
            ttab[i] = float(_p[0])
            pftab[i] = float(_p[1])
        close_unit(67)
        _save_vopf_init = 0

    itab = int(t)
    pf = pftab[itab] + (t - ttab[itab]) * (pftab[itab + 1] - pftab[itab])
    return t, pf


def gvdw(il, ilist, id):
    """c     ==========================
c
c     evaluation of the Van der Waals broadening parameter
c
c     currently, two possibilities, determined by the value of the parameter
c     ivdwli(ilist) - the mode of evaluation is the same for the whole line list
c       = 0 - standard expression
c       > 0 - evaluation using EXOMOL data, assuming breadening by H2 and He

    对应 synspec54.f 行 23627–23658
    不修改标量哑元 → 仅返回函数值
    """
    # COMMON/PRFQUA/DOPA1(MATOM,MDEPTH),VDWC(MDEPTH) → C.DOPA1, C.VDWC

    # clasical, original expression

    if C.IVDWLI[ilist] == 0:
        return C.GWM[il, ilist] * C.VDWC[id]

    # EXOMOL form - broadening by H2 and He

    # con= 1.e-6*c*k
    con = 4.1388e-12
    t = C.TEMP[id]
    anhe = C.RRR[id, 1, 2]
    return con * t * ((296.0 / t) ** C.GEXPH2[il, ilist] * C.GVDWH2[il, ilist] * C.anh2[id] +
                      (296.0 / t) ** C.GEXPHE[il, ilist] * C.GVDWHE[il, ilist] * anhe)


def exopf(indmol, t, u):
    """c     ============================
c
c     oartition functions from EXOMOL for 32 molewcular species

    对应 synspec54.f 行 23664–23741
    修改标量哑元 U → 返回全部标量哑元 (indmol, t, u)
    """
    global _save_exopf_iread
    nmol = 32  # parameter (nmol=32)
    # data filpf/.../ —— character*4，DATA，不修改（1 基索引）
    filpf = ['',
        ' AlO', '  C2', '  CH', '  CN', '  CO',
        '  CS', ' CaH', ' CaO', ' CrH', ' FeH',
        '  H2', ' HCl', '  HF', ' MgH', ' MgO',
        '  N2', '  NH', '  NO', '  NS', ' NaH',
        '  OH', '  PH', '  SH', ' SiH', ' SiO',
        ' SiS', ' TiH', ' TiO', '  VO',
        ' H2O', ' H2S', ' CO2']
    # data indtsu/.../ —— DATA，不修改
    indtsu = [0,
        134,   8,   5,   7,   6,  20,  34, 179, 198, 214,
          2,  36,  33,  32, 126,   9,  12,  11,  23, 122,
          4, 148,  16,  17,  25,  28, 315,  29,  30,   3,
         57,  44]
    ntemp = _save_exopf_ntemp  # DATA 后被修改 → 模块级 SAVE 数组别名
    pf = _save_exopf_pf        # pf(nmol,10000)，读入后重用
    # data iread /1/ → 模块级 _save_exopf_iread

    if _save_exopf_iread == 1:
        for i in range(1, nmol + 1):
            ntemp[i] = ntemp[i] * 1000
        ntemp[27] = idiv(ntemp[27], 10)  # Fortran 整数除法
        for i in range(1, nmol + 1):
            fil = filpf[i] + '.pf'       # character*7
            fil1 = fil[1:7]              # character*6 = fil(2:)
            fil0 = fil1[0:1]             # character*1 = fil1(:1)
            if fil0 == ' ':
                fil5 = 'data/EXOMOL/' + fil1[1:6]  # character*17 = fil1(2:)，右侧补空格
                open_unit(67, fil5.rstrip(), 'r')  # status='old'；Fortran 打开文件时忽略尾部空格
            else:
                fil6 = fil1              # character*18
                open_unit(67, ('data/EXOMOL/' + fil6).rstrip(), 'r')
            for j in range(1, ntemp[i] + 1):
                _p = read_line(67).split()  # read(67,*) tt,pf(i,j)
                tt = float(_p[0])
                pf[i, j] = float(_p[1])
            close_unit(67)
        _save_exopf_iread = 0

    ie = 0
    u = 0.0
    for i in range(1, nmol + 1):
        if indtsu[i] == indmol:
            ie = i
    if ie == 0:
        return indmol, t, u

    tmax = float(ntemp[ie])
    if t <= tmax:
        j = int(t)  # INT(T) 向零截断
        u = pf[ie, j]
    else:
        # 实参含字面量 0,0；irwpf 修改标量哑元 U，返回全部标量哑元
        _jatom, _ion, indmol, tmax, umx = irwpf(0, 0, indmol, tmax, 0.0)
        _jatom, _ion, indmol, t, uirw = irwpf(0, 0, indmol, t, 0.0)
        u = pf[ie, ntemp[ie]] / umx * uirw

    return indmol, t, u


def irwpf(jatom, ion, indmol, t, u):
    """c     ======================================
c
c     partition functions adter Irwin (1981), ApJS. 45, 621.
c     updated with the data of Barklem & Collet (2016)
C     set to the Irwin format by Y. Ossorio
c
c     Input: jatom - atomic number; if =0 - molecules
c            ion - ionization degree
c            indmol - index of a molecule in the new Tsuji-type
c                     indexing (from file tsuji.molec_bc2)
c            t - temperature
c     Output: u - partition function
c
c     array IRWIND(I) - the Irwin index corresponding to Tsuji
c           index I
c           if =0 - molecule I has no data in the Irwin table

    对应 synspec54.f 行 23749–23913
    修改标量哑元 U → 返回全部标量哑元 (jatom, ion, indmol, t, u)
    """
    global _save_irwpf_iread
    # real*8 a(6,3,92),aa(6),am(6,500),spec(500)
    # save iread,a,am → 模块级 _save_irwpf_*
    a = _save_irwpf_a
    am = _save_irwpf_am
    aa = np.zeros(7)
    spec = np.zeros(501)
    # data irwind/.../（含 5*0、4*0、7*0、10*0、3*0、16*0 重复计数，已展开；DATA 不修改）
    irwind = np.zeros(479, dtype=np.int64)
    irwind[1:] = [
        0,   1,  28,   4,   2,   7,   6,   5,   8,  10,
        9,   3,  18,  25,  53,  29,  43,   0,  17, 153,
        52,  55, 167,  44,  45, 182,  74,  46,  11, 187,
        201,  31,  27,  99, 209,  24,  22,  20,  21,  65,
        35,  19,  54,  23,   0,  14,  58,   0,  32,  12,
        47,  16,   0,  34,   0,   0,  30,   0,  13,  33,
        61,  63, 292,  57,  59,  66, 272,   0,  94, 175,
        226, 286,   0,   0,   0, 176, 227, 287,   0,   0,
        0,  96,   0, 177,   0, 267, 228, 288,   0,   0,
        0,   0,  93, 147, 162,   0,   0,   0,   0,   0,  # 5*0
        0,  50,   0,   0,   0,   0,  36,   0,  64,   0,
        0,  48,   0,   0, 148,   0,   0,  26,  49,  70,
        178,  97, 170, 229,   0, 180, 268, 230,   0, 289,
        0,   0,  15, 181,   0, 269,   0,   0,   0,   0,  # 4*0
        0,   0,   0, 231,   0, 290,   0,  38,   0,   0,
        152,  39,  40,   0,  41, 232,   0, 291,   0,   0,
        0,   0,   0,  75, 154,   0,   0,   0, 183,   0,
        0,   0,   0,   0,   0,  98, 184, 234, 185, 270,
        0,   0,   0, 186,   0,   0, 271, 235,   0,   0,
        62,   0,   0,   0,   0,   0,   0, 101,   0, 188,
        0,   0,   0,   0,   0, 102, 189,   0,   0,   0,  # 3*0
        236,   0, 294,  67,   0, 190,   0,   0,   0, 295,
        0,   0, 104, 191, 237,   0, 105, 192, 274, 238,
        296, 112, 245, 303, 113, 199,   0, 278, 246,   0,
        304,   0,   0,   0,   0, 200,   0,   0, 279, 247,
        0, 305,   0,   0, 172,   0,   0,   0,   0,   0,  # 5*0
        0, 120, 122, 208,   0, 282, 255,   0, 312,   0,
        0,   0,   0,   0,   0,   0,   0, 283, 256,   0,  # 7*0
        0,   0,   0,   0,   0,   0,   0,   0,   0,   0,  # 10*0
        275, 194, 108, 241, 299, 202,   0,  68,  69,  71,
        72,  73,  42,  37,  76,  77,  78,  79,  80,  81,
        82,  83,  92,  95, 100, 103, 106, 107, 109, 110,
        111, 114, 115, 116, 117, 118, 119, 121, 123, 124,
        125, 126, 127, 128, 129, 149, 150, 151, 155, 156,
        157, 158, 159, 163, 164, 165, 166, 168, 169, 170,
        171, 193, 195, 196, 197, 198, 203, 204, 205, 206,
        207, 210, 211, 212, 213, 214, 215, 216, 217, 218,
        225, 233, 239, 240, 242, 243, 244, 248, 249, 250,
        251, 252, 253, 254, 257, 258, 259, 260, 262, 262,
        263, 264, 265, 266, 273, 276, 277, 280, 282, 284,
        285, 293, 297, 298, 300, 301, 302, 306, 307, 308,
        309, 310, 311,  60, 313, 314, 315, 316, 317, 318,
        319, 320, 321, 322, 323, 324,  84,  85,  86,  87,
        88,  89,  90,  91, 130, 131, 132, 133, 134, 135,
        136, 137, 138, 139, 140, 141, 142, 143, 144, 145,
        146, 160, 161, 173, 174, 210, 220, 221, 222, 223,
        224,   0,   0,   0,   0,   0,   0,   0,   0,   0,  # 16*0（开始）
        0,   0,   0,   0,   0,   0,   0,  56]
    # data iread /0/ → 模块级 _save_irwpf_iread

    # call old Irwin routine MPARTF if desired

    if C.IRWTAB == 0:
        jatom, ion, indmol, t, u = mpartf(jatom, ion, indmol, t, u)
        return jatom, ion, indmol, t, u

    # read data if first call:

    if _save_irwpf_iread != 1:
        if C.IRWTAB == 0:  # 死代码（上面已返回），按原文保留
            open_unit(67, './data/irwin_orig.dat', 'r')
        else:
            open_unit(67, './data/irwin_bc.dat', 'r')
        read_line(67)  # read(67,*)
        read_line(67)
        for j in range(1, 93):
            for i in range(1, 4):
                if j == 1 and i == 3:
                    continue  # GO TO 10（H 的二次电离不存在，跳过读取）
                sp = float(j) + float(i - 1) / 100.0  # sp 之后未使用（原代码如此）
                _p = read_line(67).split()  # read(67,*) spc,aa
                spc = float(_p[0])
                for k in range(1, 7):
                    aa[k] = float(_p[k])
                for k in range(1, 7):
                    a[k, i, j] = aa[k]
                # 标号 10 continue

        read_line(67)  # read(67,*)
        read_line(67)
        read_line(67)
        for i in range(1, 325):
            try:
                _p = read_line(67).split()  # read(67,*,end=15) spec(i),aa
            except EOFError:
                break  # END=15 → 标号 15
            spec[i] = float(_p[0])
            for k in range(1, 7):
                aa[k] = float(_p[k])
            for j in range(1, 7):
                am[j, i] = aa[j]
        # 标号 15 continue
        close_unit(67)
        _save_irwpf_iread = 1

    # evaluation of the partition function
    # stop if T is out of limits of Irwin's tables

    if t < 1000.0:
        raise SystemExit('partf; temp<1000 K')  # STOP '...'
    elif t > 16000.0:
        raise SystemExit('partf; temp>16000 K')
    tl = math.log(t)
    u = 0.0

    # atomic species

    if jatom > 0 and ion > 0:
        ulog = (a[1, ion, jatom] +
            tl * (a[2, ion, jatom] +
            tl * (a[3, ion, jatom] +
            tl * (a[4, ion, jatom] +
            tl * (a[5, ion, jatom] +
            tl * (a[6, ion, jatom]))))))
        if jatom == 5 and ion == 3:
            ulog = 1.0
        # write(*,*) 'bor',ion,tl,ulog  （原代码已注释）
        # 631  format('bor',i4,1p8e11.3)  （原代码已注释）
        u = math.exp(ulog)
        return jatom, ion, indmol, t, u

    # molecular species

    if indmol > 0:
        indm = irwind[indmol]
        if indm <= 0:
            return jatom, ion, indmol, t, u
        ulog = (am[1, indm] +
            tl * (am[2, indm] +
            tl * (am[3, indm] +
            tl * (am[4, indm] +
            tl * (am[5, indm] +
            tl * (am[6, indm]))))))
        u = math.exp(ulog)
        # if(t.gt.5128..and.t.lt.5129.) write(6,631) t,indmol,indm,u  （原代码已注释）
        # 631   format('irwpf',f10.1,2i5,f16.3)  （原代码已注释）
    return jatom, ion, indmol, t, u
