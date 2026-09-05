# -*- coding: utf-8 -*-
# chunk14: synspec54.f 第 17483–19178 行的逐行直译
# 包含: frac1, fractn, dwnfr0, dwnfr1, chckab, molini, inmoli, molset,
#       iniblm, idmtab, molop, sbfhmi, sffhmi, mpartf, moleq
# 本分片禁止 import;np / math / C / params 常量 / fortran 辅助函数由组装模块头部提供。


# ---------------------------------------------------------------- 本分片私有解析辅助

def _c14_rdf(s):
    """按 Fortran 数值场语义解析浮点数:允许 D/d 指数,空白按 0 处理。"""
    s = str(s).strip()
    if s == "":
        return 0.0
    return float(s.replace("D", "E").replace("d", "e"))


def _c14_rdi(s):
    """按 Fortran 整数场语义解析整数:空白按 0 处理。"""
    s = str(s).strip()
    if s == "":
        return 0
    return int(s)


def _c14_unf_record(unit):
    """读一条 g77/gfortran 无格式顺序记录,返回 real*8 的 numpy 数组。

    记录结构: 4 字节长度标记 + 数据 + 4 字节长度标记。
    TODO(port): 假定记录标记为 4 字节 little-endian(gfortran 默认)。
    """
    fh = funits[unit]
    hdr = fh.read(4)
    if len(hdr) < 4:
        raise EOFError("unit %d: end of file" % unit)
    nb = int.from_bytes(hdr, "little", signed=True)
    data = fh.read(nb)
    if len(data) < nb:
        raise EOFError("unit %d: truncated unformatted record" % unit)
    fh.read(4)   # 尾部记录标记
    return np.frombuffer(data, dtype=np.float64)


# ---------------------------------------------------------------- SAVE / DATA 提升变量

_save_molset_imlast = 0                          # MOLSET: SAVE IMLAST(无 DATA,按 0 初始化)

_save_sffhmi_istart = 0                          # SFFHMI: DATA ISTART/0/,之后置 1
_save_sffhmi_fflog = np.zeros((23, 12))          # SFFHMI: FFLOG(22,11),首次调用计算后需保持
_save_sffhmi_wfflog = np.zeros(23)               # SFFHMI: WFFLOG(22),同上

_save_mpartf_iread = 0                           # MPARTF: DATA iread/0/(SAVE)
_save_mpartf_a = np.zeros((7, 4, 93))            # MPARTF: SAVE a(6,3,92)
_save_mpartf_am = np.zeros((7, 501))             # MPARTF: SAVE am(6,500)
# TODO(port): irw(500) 在原文中无 SAVE,但只在首次调用时赋值、之后一直使用,
# 依赖编译器保留局部数组;为保证语义正确提升为模块级。
_save_mpartf_irw = np.zeros(501, dtype=np.int64)

_save_moleq_iread = 1                            # MOLEQ: DATA iread/1/,之后置 0


# ******************************************************************

def frac1():
    """对应 synspec54.f 行 17483–17570(SUBROUTINE FRAC1,原无头注释)。"""
    mtemp = 100; melec = 60; mion1 = 30   # 局部 PARAMETER(仅用于说明,数组用 MDEPTH)
    xxt = np.zeros(MDEPTH + 1)
    xxe = np.zeros(MDEPTH + 1)
    kt0 = np.zeros(MDEPTH + 1, dtype=np.int64)
    kn0 = np.zeros(MDEPTH + 1, dtype=np.int64)
    # common/fracop/frac,fracm,itemp,ntt → C.frac 等

    for id in range(1, C.ND + 1):
        xxt[id] = math.log10(C.TEMP[id])
        kt0[id] = 2 * int(20.0 * xxt[id])      # INT 向零截断 = Python int()
        xxe[id] = math.log10(C.ELEC[id])
        kn0[id] = int(2.0 * xxe[id])

    for iat in range(1, 31):                   # DO 20 IAT=1,30
        iatnum = iat
        iatnum = fractn(iatnum)                # FRACTN 修改标量哑元 iatnum
        if iatnum <= 0:
            continue                           # GO TO 20
        for id in range(1, C.ND + 1):
            if kt0[id] < C.itemp[1]:
                kt1 = 1
                # 611 format(' (FRACOP) Extrapol. in T (low)',i4,f7.0)
                print(' (FRACOP) Extrapol. in T (low)%4d%7.0f' % (id, C.TEMP[id]))
                # goto 41
            elif kt0[id] >= C.itemp[C.ntt]:
                kt1 = C.ntt - 1
                # 612 format(' (FRACOP) Extrapol. in T (high)',i4,f12.0)
                print(' (FRACOP) Extrapol. in T (high)%4d%12.0f' % (id, C.TEMP[id]))
                # goto 41
            else:
                for it in range(1, C.ntt + 1):     # do 40 it=1,ntt
                    if kt0[id] == C.itemp[it]:
                        kt1 = it
                        break                      # goto 41
                # 40 continue
            # 41 continue
            if kn0[id] < 1:
                kn1 = 1
                # goto 49
            elif kn0[id] >= 60:
                kn1 = 59
                # 614 format(' (FRACOP) Extrapol. in Ne (high)',i4,f9.4)
                print(' (FRACOP) Extrapol. in Ne (high)%4d%9.4f' % (id, xxe[id]))
                # goto 49
            else:
                kn1 = kn0[id]
            # 49 continue
            xt1 = 0.025 * C.itemp[kt1]
            dxt = 0.05
            at1 = (xxt[id] - xt1) / dxt
            xn1 = 0.5 * kn1
            dxn = 0.5
            an1 = (xxe[id] - xn1) / dxn
            for ion in range(1, mion1 + 1):
                x11 = C.frac[kt1, kn1, ion]
                x21 = C.frac[kt1 + 1, kn1, ion]
                x12 = C.frac[kt1, kn1 + 1, ion]
                x22 = C.frac[kt1 + 1, kn1 + 1, ion]
                x1221 = x11 * x21 * x12 * x22
                if x1221 == 0.0:
                    xx1 = x11 + at1 * (x21 - x11)
                    xx2 = x12 + at1 * (x22 - x12)
                    rrx = xx1 + an1 * (xx2 - xx1)
                else:
                    x11 = math.log10(x11)
                    x21 = math.log10(x21)
                    x12 = math.log10(x12)
                    x22 = math.log10(x22)
                    xx1 = x11 + at1 * (x21 - x11)
                    xx2 = x12 + at1 * (x22 - x12)
                    rrx = xx1 + an1 * (xx2 - xx1)
                    rrx = math.exp(2.3025851 * rrx)
                C.RRR[id, ion, iat] = rrx * C.ABNDD[iat, id] * \
                    C.DENS[id] / C.WMM[id] / C.YTOT[id]
        # 20 CONTINUE
    return


# ******************************************************************

def fractn(iatnum):
    """对应 synspec54.f 行 17574–17728(SUBROUTINE FRACTN,原无头注释)。

    修改标量哑元 iatnum(数据不存在时置 -1),按约定返回全部标量哑元。
    """
    mtemp = 100; melec = 60; mion1 = 30; mdat = 17   # 局部 PARAMETER
    inp = 71                                          # 局部 PARAMETER
    # frac0(-1:mion1)、z0(-1:mion1)、ioo(-1:mion1):下标 i 映射为 i+1
    frac0 = np.zeros(mion1 + 2)
    ioo = np.zeros(mion1 + 2, dtype=np.int64)
    z0 = np.zeros(mion1 + 2)
    g0 = np.zeros(mion1 + 1)
    u0 = np.zeros(mion1 + 1)
    uu = np.zeros((mion1 + 1, mdat + 1))
    gg = np.zeros((mion1 + 1, mdat + 1))

    # DATA idat / 1, 2, 0, 0, 0, 3, 4, 5, 0, 6,
    #             7, 8, 9,10, 0,11, 0,12, 0,13,
    #             0, 0, 0,14,15,16, 0,17, 0, 0/
    idat = np.zeros(mion1 + 1, dtype=np.int64)
    idat[1:] = [1, 2, 0, 0, 0, 3, 4, 5, 0, 6,
                7, 8, 9, 10, 0, 11, 0, 12, 0, 13,
                0, 0, 0, 14, 15, 16, 0, 17, 0, 0]

    # DATA gg/.../(30x17,按列填充;保留原文的 n*0 重复记法)
    gg_flat = (
        [2.] + [0.]*29 +                                  # 第 1 列
        [2., 1.] + [0.]*28 +                              # 第 2 列
        [2., 1., 2., 1., 6., 9.] + [0.]*24 +              # 第 3 列
        [2., 1., 2., 1., 6., 9., 4.] + [0.]*23 +          # 第 4 列
        [2., 1., 2., 1., 6., 9., 4., 9.] + [0.]*22 +      # 第 5 列
        [2., 1., 2., 1., 6., 9., 4., 9., 6., 1.] + [0.]*20 +
        [2., 1., 2., 1., 6., 9., 4., 9., 6., 1., 2.] + [0.]*19 +
        [2., 1., 2., 1., 6., 9., 4., 9., 6., 1., 2., 1.] + [0.]*18 +
        [2., 1., 2., 1., 6., 9., 4., 9., 6., 1., 2., 1., 6.] + [0.]*17 +
        [2., 1., 2., 1., 6., 9., 4., 9., 6., 1., 2., 1., 6., 9.] + [0.]*16 +
        [2., 1., 2., 1., 6., 9., 4., 9., 6., 1., 2., 1., 6., 9., 4., 9.] + [0.]*14 +
        [2., 1., 2., 1., 6., 9., 4., 9., 6., 1., 2., 1., 6., 9., 4., 9.,
         6., 1.] + [0.]*12 +                              # 第 12 列
        [2., 1., 2., 1., 6., 9., 4., 9., 6., 1., 2., 1., 6., 9., 4., 9.,
         6., 1., 2., 1.] + [0.]*10 +                      # 第 13 列
        [2., 1., 2., 1., 6., 9., 4., 9., 6., 1., 2., 1.,
         6., 9., 4., 9., 6., 1., 10., 21., 28., 25., 6., 7.] + [0.]*6 +
        [2., 1., 2., 1., 6., 9., 4., 9., 6., 1., 2., 1., 6., 9., 4., 9.,
         6., 1., 10., 21., 28., 25., 6., 7., 6.] + [0.]*5 +
        [2., 1., 2., 1., 6., 9., 4., 9., 6., 1., 2., 1., 6., 9., 4., 9.,
         6., 1., 10., 21., 28., 25., 6., 25., 30., 25.] + [0.]*4 +
        [2., 1., 2., 1., 6., 9., 4., 9., 6., 1., 2., 1., 6., 9., 4., 9.,
         6., 1., 10., 21., 28., 25., 6., 25., 28., 21., 10., 21., 0., 0.]
    )
    gg[1:, 1:] = np.array(gg_flat).reshape((mion1, mdat), order='F')

    # DATA uu(1,1)/109.6787/, uu(1,2)/198.3108/, uu(2,2)/438.9089/
    uu[1, 1] = 109.6787
    uu[1, 2] = 198.3108
    uu[2, 2] = 438.9089
    # EQUIVALENCE (u6(1),uu(1,3)),(u7(1),uu(1,4)),...,(u28(1),uu(1,17)):
    # u6..u28 分别是 uu 第 3..17 列的前若干个元素;DATA 直接写入 uu 对应列。
    uu[1:7, 3] = [90.82, 196.665, 386.241, 520.178, 3162.395, 3952.061]          # u6
    uu[1:8, 4] = [117.225, 238.751, 382.704, 624.866, 789.537, 4452.758,
                  5380.089]                                                     # u7
    uu[1:9, 5] = [109.837, 283.24, 443.086, 624.384, 918.657, 1114.008,
                  5963.135, 7028.393]                                           # u8
    uu[1:11, 6] = [173.93, 330.391, 511.8, 783.3, 1018., 1273.8, 1671.792,
                   1928.462, 9645.005, 10986.876]                               # u10
    uu[1:12, 7] = [41.449, 381.395, 577.8, 797.8, 1116.2, 1388.5, 1681.5,
                   2130.8, 2418.7, 11817.061, 13297.676]                        # u11
    uu[1:13, 8] = [61.671, 121.268, 646.41, 881.1, 1139.4, 1504.3, 1814.3,
                   2144.7, 2645.2, 2964.4, 14210.261, 15829.951]                # u12
    uu[1:14, 9] = [48.278, 151.86, 229.446, 967.8, 1239.8, 1536.3, 1947.3,
                   2295.4, 2663.4, 3214.8, 3565.6, 16825.022, 18584.138]        # u13
    uu[1:15, 10] = [65.748, 131.838, 270.139, 364.093, 1345.1, 1653.9, 1988.4,
                    2445.3, 2831.9, 3237.8, 3839.8, 4222.4, 19661.693,
                    21560.63]                                                   # u14
    uu[1:17, 11] = [83.558, 188.2, 280.9, 381.541, 586.2, 710.184, 2265.9,
                    2647.4, 3057.7, 3606.1, 4071.4, 4554.3, 5255.9, 5703.6,
                    26002.663, 28182.535]                                       # u16
    uu[1:19, 12] = [127.11, 222.848, 328.6, 482.4, 605.1, 734.04, 1002.73,
                    1157.08, 3407.3, 3860.9, 4347., 4986.6, 5533.8, 6095.5,
                    6894.2, 7404.4, 33237.173, 35699.936]                       # u18
    uu[1:21, 13] = [49.306, 95.752, 410.642, 542.6, 681.6, 877.4, 1026.,
                    1187.6, 1520.64, 1704.047, 4774., 5301., 5861., 6595.,
                    7215., 7860., 8770., 9338., 41366., 44177.41]               # u20
    uu[1:25, 14] = [54.576, 132.966, 249.7, 396.5, 560.2, 731.02, 1291.9,
                    1490., 1688., 1971., 2184., 2404., 2862., 3098.52, 8151.,
                    8850., 9560., 10480., 11260., 12070., 13180., 13882.,
                    60344., 63675.9]                                            # u24
    uu[1:26, 15] = [59.959, 126.145, 271.55, 413., 584., 771.1, 961.44, 1569.,
                    1789., 2003., 2307., 2536., 2771., 3250., 3509.82, 9152.,
                    9872., 10620., 11590., 12410., 13260., 14420., 15162.,
                    65660., 69137.4]                                            # u25
    uu[1:27, 16] = [63.737, 130.563, 247.22, 442., 605., 799., 1008., 1218.38,
                    1884., 2114., 2341., 2668., 2912., 3163., 3686., 3946.82,
                    10180., 10985., 11850., 12708., 13620., 14510., 15797.,
                    16500., 71203., 74829.6]                                    # u26
    uu[1:29, 17] = [61.6, 146.542, 283.8, 443., 613.5, 870., 1070., 1310.,
                    1560., 1812., 2589., 2840., 3100., 3470., 3740., 4020.,
                    4606., 4896.2, 12430., 13290., 14160., 15280., 16220.,
                    17190., 18510., 19351., 82984., 86909.4]                    # u28

    if idat[iatnum] == 0:
        # 600 format(' OP data for element no. ',i3,' do not exist')
        print(' OP data for element no. %3d do not exist' % iatnum)
        iatnum = -1
        return iatnum

    g0[iatnum + 1] = 1.0
    for i in range(1, iatnum + 1):
        ig0 = iatnum - i + 1
        g0[ig0] = gg[i, idat[iatnum]]
        u0[i] = uu[i, idat[iatnum]] * 1000.0

    if iatnum == 1:
        open_unit(inp, 'ioniz.dat', 'r')   # open(inp,file='ioniz.dat',status='old')
    for it in range(1, mtemp + 1):         # do 10
        for ie in range(1, melec + 1):
            C.fracm[it, ie] = 0.0
            for ion in range(1, mion1 + 1):
                C.frac[it, ie, ion] = 0.0

    read_line(inp)                         # read(inp,*)
    # read(inp,*) it0,it1,itstp(自由格式)
    _tk = read_line(inp).replace(',', ' ').split()
    it0 = int(_c14_rdf(_tk[0])); it1 = int(_c14_rdf(_tk[1])); itstp = int(_c14_rdf(_tk[2]))
    C.ntt = idiv(it1 - it0, itstp) + 1

    for it in range(1, C.ntt + 1):
        # read(inp,*) itt,ie0,ie1,iestp
        _tk = read_line(inp).replace(',', ' ').split()
        itt = int(_c14_rdf(_tk[0])); ie0 = int(_c14_rdf(_tk[1]))
        ie1 = int(_c14_rdf(_tk[2])); iestp = int(_c14_rdf(_tk[3]))
        C.itemp[it] = itt
        net = idiv(ie1 - ie0, iestp) + 1
        t = math.exp(2.3025851 * 0.025 * itt)
        safac0 = math.sqrt(t) * t / 2.07e-16
        tkcm = 0.69496 * t
        for ie in range(1, net + 1):
            # 601 format(3i4,2x,4(i4,1x,e9.3))
            _ln = read_line(inp)
            iee = _c14_rdi(_ln[0:4]); ion0 = _c14_rdi(_ln[4:8]); ion1 = _c14_rdi(_ln[8:12])
            _pos = 14
            for i in range(ion0, min(ion1, ion0 + 3) + 1):
                ioo[i + 1] = _c14_rdi(_ln[_pos:_pos + 4])
                frac0[i + 1] = _c14_rdf(_ln[_pos + 5:_pos + 14])
                _pos += 14
            ane = math.exp(2.3025851 * 0.25 * iee)
            safac = safac0 / ane
            nio = ion1 - ion0
            if nio >= 3:
                nlin = idiv(nio, 4)
                for ilin in range(1, nlin + 1):
                    # 602 format(14x,4(i4,1x,e9.3))
                    _ln = read_line(inp)
                    _pos = 14
                    for i in range(ion0 + 4 * ilin, min(ion1, ion0 + 4 * ilin + 3) + 1):
                        ioo[i + 1] = _c14_rdi(_ln[_pos:_pos + 4])
                        frac0[i + 1] = _c14_rdf(_ln[_pos + 5:_pos + 14])
                        _pos += 14
            ieind = idiv(iee, 2)
            for ion in range(ion0, ion1 + 1):
                if ion < iatnum:
                    if ion == ion0:
                        z0[ion + 1] = g0[iatnum - ion]
                    else:
                        z0[ion + 1] = frac0[ion + 1] / frac0[ion] * safac * z0[ion]
                        z0[ion + 1] = z0[ion + 1] * math.exp(-u0[iatnum - ion] / tkcm)
                    C.frac[it, ieind, iatnum - ion] = frac0[ion + 1] / z0[ion + 1]
                else:
                    u0hm = 6090.5
                    z0hm = frac0[ion + 1] / frac0[ion] * safac
                    z0hm = z0hm * math.exp(-u0hm / tkcm)
                    C.fracm[it, ieind] = frac0[ion + 1] / z0hm
    return iatnum


# *******************************************************************

def dwnfr0(id):
    """Auxiliary quantities for dissolved fractions

    对应 synspec54.f 行 17735–17758(SUBROUTINE DWNFR0)。
    """
    UN = 1.0; SIXTH = UN / 6.0; CCOR = 0.09          # PARAMETER
    p1 = 0.1402; p2 = 0.1285; p3 = UN; p4 = 3.15; p5 = 4.0
    f23 = -2.0 / 3.0

    ane = C.ELEC[id]
    C.ELEC23[id] = math.exp(f23 * math.log(ane))
    anes = math.exp(SIXTH * math.log(ane))
    acor = CCOR * anes / math.sqrt(C.TEMP[id])
    x = math.exp(p4 * math.log(UN + p3 * acor))
    C.DWC2[id] = p2 * x
    a3 = acor * acor * acor
    for izz in range(1, MZZ + 1):                    # DO 10 IZZ=1,MZZ
        C.Z3[izz] = izz * izz * izz
        C.DWC1[izz, id] = p1 * (x + p5 * (izz - 1.0) * a3)
    return


# *******************************************************************

def dwnfr1(fr, fr0, id, izz, dw1):
    """dissolved fraction for frequency FR

    对应 synspec54.f 行 17764–17804(SUBROUTINE DWNFR1)。
    修改标量哑元 DW1,按约定返回全部标量哑元。
    """
    UN = 1.0; TKN = 3.01; CKN = 5.33333333; CB = 8.59e14   # PARAMETER
    SQFRH = 5.734152e7
    a0 = 0.529177e-8; wa0 = -3.1415926538 / 6.0 * a0 * a0 * a0

    if fr < fr0:
        xn = SQFRH * izz / math.sqrt(fr0 - fr)
        if xn <= TKN:
            xkn = UN
        else:
            xn1 = UN / (xn + UN)
            xkn = CKN * xn * xn1 * xn1
        beta = CB * C.Z3[izz] * xkn / (xn * xn * xn * xn) * C.ELEC23[id]
        beta = beta * C.BERGFC
        beta3 = beta * beta * beta
        beta32 = math.sqrt(beta3)
        f = (C.DWC1[izz, id] * beta3) / (UN + C.DWC2[id] * beta32)

        # contribution from neutral particles

        xn2 = xn * xn + UN
        xnh = 0.0
        xnhe1 = 0.0
        if C.IELH > 0:
            xnh = C.POPUL[C.NFIRST[C.IELH], id]
        if C.IELHE1 > 0:
            xnhe1 = C.POPUL[C.NFIRST[C.IELHE1], id]
        w0 = math.exp(wa0 * xn2 * xn2 * xn2 * (xnh + xnhe1))
        w0 = 1.0

        dw1 = UN - f / (UN + f) * w0
    else:
        dw1 = UN
    return fr, fr0, id, izz, dw1


# *******************************************************************

def chckab():
    """check input abumdances of explicit atoms (unit 5) and those
    which follow from the models atmosphere (unit 7) obtained by
    summing all populations and upper sums
    The program stops if it finds discrepancy more than 10 %

    对应 synspec54.f 行 17810–17858(SUBROUTINE CHCKAB)。
    """
    sumpop = np.zeros(MATOM + 1)
    sumiat = np.zeros(MATOM + 1)

    ist = 0
    for id1 in range(1, 4):
        if id1 == 1:
            id = 1
        if id1 == 2:
            id = 46
        if id1 == 3:
            id = C.ND
        wnstor(id)                # WNSTOR 不修改标量哑元
        ane = C.ELEC[id]
        sabolf(id)                # SABOLF 不修改标量哑元
        for iat in range(1, C.NATOM + 1):
            sum_l = 0.0           # 原局部变量 SUM,改名避免遮蔽内建
            sump = 0.0
            for i in range(C.N0A[iat], C.NKA[iat] + 1):
                il = C.ILK[i]
                a = 1.0
                if il > 0:
                    a = 1.0 + ane * C.USUM[il]
                sum_l = sum_l + a * C.POPUL[i, id]
                sump = sump + C.POPUL[i, id]
            sumiat[iat] = sum_l
            sumpop[iat] = sump
        # 600 FORMAT(' check of abundances (id =',i3/
        #      ' computed from model atmosphere  - input abundances'/)
        print(' check of abundances (id =%3d' % id)
        print(' computed from model atmosphere  - input abundances')
        print('')
        for iat in range(1, C.NATOM + 1):
            x = sumiat[iat] / sumiat[C.IATREF]
            # 601 format(i5,1p3e20.3)
            print('%5d%20.3e%20.3e%20.3e' %
                  (iat, x, C.ABUND[iat, id], sumpop[iat] / sumpop[C.IATREF]))
            if x / C.ABUND[iat, id] > 1.1 or x / C.ABUND[iat, id] < 0.9:
                ist = ist + 1
    if ist > 0:
        # 602 format(' ERROR !!! - inconsistent abundances'/)
        print(' ERROR !!! - inconsistent abundances')
        print('')
        raise SystemExit          # STOP
    return


# *******************************************************************

def molini():
    """Initialization of the molecular equilibrium

    对应 synspec54.f 行 17864–17941(SUBROUTINE MOLINI)。
    """
    # common/moltst/... → C.pfmol 等
    hpo = np.zeros(MDEPTH + 1)

    aeinit = 1.0

    for id in range(1, C.ND + 1):                  # do 10 id=1,nd
        t = C.TEMP[id]
        tln = math.log(t) * 1.5
        thl = 11605.0 / t
        t32 = math.exp(tln)

        for i in range(1, MMOLEC + 1):
            C.RRMOL[i, id] = 0.0

        hpo[id] = C.DENS[id] / C.WMM[id] / C.YTOT[id]

        if t > C.TMOLIM:
            continue                               # go to 10
        hpop = C.DENS[id] / C.WMM[id] / C.YTOT[id]

        an = C.DENS[id] / C.WMM[id] + C.ELEC[id]
        aeinit = 0.1 * an
        if t < 4000.0:
            aeinit = 0.01 * an
        # MOLEQ 修改标量哑元 ane,按约定解包全部标量哑元;
        # ane 首次调用时尚未赋值,传 0.0;实参 0 对应 ipri
        id, t, an, aeinit, ane, _ipri = moleq(id, t, an, aeinit, 0.0, 0)

        # next initial guess will be the last ane determined for
        # previous depth point

        aeinit = ane

        if id == C.IDSTD:
            # 600 format(/ 'Molecular number densities at the standard depth'/)
            print('')
            print('Molecular number densities at the standard depth')
            print('')
            nmol = C.NMOLEC
            if id == 1:
                nmol = 32
            for i in range(1, nmol + 1):
                # 601 format(i4,1x,A8,1x,1pe12.2,1x,e12.2)
                print('%4d %-8s %12.2e %12.2e' %
                      (i, C.CMOL[i], C.RRMOL[i, id], C.RRMOL[i, id] / hpop))
    # 10 continue

    # update atomic populations once molecular densities are calculated

    if C.IMODE < -4:
        for i in range(1, C.NLEVEL + 1):
            iat = C.NUMAT[C.IATM[i]]
            ion = C.IZ[C.IEL[i]]
            ii = C.NFIRST[C.IEL[i]]
            ener = (C.ENION[ii] - C.ENION[i]) / BOLK
            if C.ENION[i] == 0 and C.ILK[i] > 0:
                ener = 0.0
                ion = ion + 1
            if C.ifwop[i] >= 0:
                for id in range(1, C.ND + 1):
                    C.POPUL[i, id] = C.RRR[id, ion, iat] * C.G[i] * \
                        math.exp(-ener / C.TEMP[id])
                    if iat == 1 and ion == 0:
                        C.POPUL[i, id] = C.anhm[id]
    return


# *******************************************************************

def inmoli(ilist):
    """read in the input molecular line list,
    selection of lines that may contribute,
    set up auxiliary fields containing line parameters,

    Input of line data - unit 20:

    For each line, one (or two) records, containing:

   ALAM    - wavelength (in nm)
   ANUM    - code of the modelcule (as in Kurucz)
             (eg. 101.00 = H2; 607.00 = CN)
   GF      - log gf
   EXCL    - excitation potential of the lower level (in cm*-1)
   GR      - gamma(rad)
   GS      - gamma(Stark)
   GW      - gamma(VdW)

    对应 synspec54.f 行 17947–18292(SUBROUTINE INMOLI)。
    """
    x = np.zeros(10)
    PI4 = 7.95774715e-2                       # PARAMETER
    C1 = 2.3025851; C2 = 4.2014672; C3 = 1.4387886; CNM = 2.997925e17
    EXT0 = 3.17; UN = 1.0; TEN = 10.0; HUND = 1.0e2
    TENM4 = 1.0e-4; TENM8 = 1.0e-8; OP4 = 0.4
    AGR0 = 2.4734e-22; XEH = 13.595; XET = 8067.6; XNF = 25.0
    R02 = 2.5; R12 = 45.0; VW0 = 4.5e-9

    # DATA INLSET /0/(已注释掉)

    if C.IMODE != -3 and C.TEMP[C.IDSTD] > C.TMOLIM:
        return
    iunit = C.IUNITM[ilist]

    if C.IBIN[ilist] == 0:
        open_unit(iunit, C.AMLIST[ilist], 'r')          # status='old'
    else:
        open_unit(iunit, C.AMLIST[ilist], 'rb')         # form='unformatted'

    # define a conversion table between Kurucz notation and Tsuji table
    # through array MOLIND

    for i in range(1, 11001):
        C.MOLIND[i] = 0
    C.MOLIND[101] = 2
    C.MOLIND[106] = 5
    C.MOLIND[107] = 12
    C.MOLIND[108] = 4
    C.MOLIND[111] = 122
    C.MOLIND[112] = 32
    C.MOLIND[114] = 17
    C.MOLIND[116] = 16
    C.MOLIND[120] = 34
    C.MOLIND[124] = 198
    C.MOLIND[126] = 214
    C.MOLIND[606] = 8
    C.MOLIND[607] = 7
    C.MOLIND[608] = 6
    C.MOLIND[614] = 21
    C.MOLIND[616] = 20
    C.MOLIND[707] = 9
    C.MOLIND[708] = 11
    C.MOLIND[714] = 24
    C.MOLIND[716] = 23
    C.MOLIND[808] = 10
    C.MOLIND[812] = 126
    C.MOLIND[813] = 134
    C.MOLIND[814] = 25
    C.MOLIND[816] = 26
    C.MOLIND[820] = 179
    C.MOLIND[822] = 29
    C.MOLIND[823] = 30
    C.MOLIND[10108] = 3

    # iunit=19+ilist

    # ================================
    # detect the type of the line list

    C.IVDWLI[ilist] = 0
    ibroad = 1

    # 局部变量 np(每条记录的值数 9/7/4)改名为 np_l,避免遮蔽 numpy 别名
    np_l = 0

    # text list

    if C.IBIN[ilist] == 0:
        dum = read_line(iunit)                  # read(iunit,'(a80)') dum
        _tk = dum.replace(',', ' ').split()
        # read(dum,*,iostat=kst1) (x(i),i=1,9) —— 内部文件自由格式读
        try:
            for i in range(1, 10):
                x[i] = _c14_rdf(_tk[i - 1])
            np_l = 9
        except (ValueError, IndexError):        # kst1 != 0
            # read(dum,*,iostat=kst2) (x(i),i=1,7)
            try:
                for i in range(1, 8):
                    x[i] = _c14_rdf(_tk[i - 1])
                np_l = 7
            except (ValueError, IndexError):    # kst2 != 0
                # read(dum,*,iostat=kst3) (x(i),i=1,4)
                try:
                    for i in range(1, 5):
                        x[i] = _c14_rdf(_tk[i - 1])
                    ibroad = 0
                    np_l = 4
                except (ValueError, IndexError):    # kst3 != 0
                    print('no applicable format of line list', ilist)
        if np_l == 9:
            C.IVDWLI[ilist] = 1
    else:
        # binary list
        # TODO(port): 原文用 read(...,err=110/120/130) 依次尝试 9/7/4 个值;
        # 这里等价地按第一条记录的载荷长度判定 np_l(随后有 REWIND,尝试性
        # 读取消费的记录不影响后续)。
        try:
            _rec = _c14_unf_record(iunit)       # read(iunit,err=110) (x(i),i=1,9)
            if len(_rec) >= 9:
                np_l = 9
            elif len(_rec) >= 7:
                np_l = 7                        # 标号 110: read(...) (x(i),i=1,7)
            else:
                np_l = 4                        # 标号 120: read(...) (x(i),i=1,4)
                ibroad = 0
            for i in range(1, np_l + 1):
                x[i] = _rec[i - 1]
        except EOFError:
            pass                                # 标号 130: 无操作
        # 150 continue
        if np_l == 9:
            C.IVDWLI[ilist] = 1
        if np_l == 9:
            C.IVDWLI[ilist] = 1                 # 原文重复两次(18087–18088)
    # =========================

    alast = CNM / C.FRLAST
    C.ALASTM[ilist] = alast
    il = 0
    if C.NXTSEM[ilist] == 1:
        C.ALAM0 = C.ALM00
        C.ALASTM[ilist] = C.ALST00
        C.FRLASM[ilist] = CNM / C.ALASTM[ilist]
        C.NXTSEM[ilist] = 0
        rewind_unit(iunit)                      # REWIND IUNIT
    C.ALMM00 = C.ALAM0
    # ALASTM(ILIST)=CNM/FRLAST
    # FRLASM(ILIST)=CNM/ALASTM(ILIST)
    dopstd = 1.0e7 / C.ALAM0 * C.DSTD
    doplam = C.ALAM0 * C.ALAM0 / CNM * dopstd
    avab = C.ABSTD[C.IDSTD] * C.RELOP
    astd = 1.0
    # IF(GRAV.GT.6.) ASTD=0.1
    cutoff = C.CUTOF0
    alast = CNM / C.FRLAST

    # first part of reading line list - read only lambda, and
    # skip all lines with wavelength below ALAM0-CUTOFF

    rewind_unit(iunit)                          # REWIND IUNIT
    alam = 0.0
    ijc = 2

    # 标号 7:跳过波长小于 ALAM0-CUTOFF 的谱线
    if C.IBIN[ilist] == 0:
        while True:
            _pos = funits[iunit].tell()         # 记录行首位置,供 BACKSPACE
            alam = _c14_rdf(read_line(iunit)[0:10])   # 510 FORMAT(F10.4)
            if not (alam < C.ALAM0 - cutoff):
                break
        funits[iunit].seek(_pos)                # BACKSPACE(IUNIT)
    else:
        while True:
            _pos = funits[iunit].tell()
            _rec = _c14_unf_record(iunit)       # read(iunit) alam
            alam = float(_rec[0])
            if not (alam < C.ALAM0 - cutoff):
                break
        funits[iunit].seek(_pos)                # BACKSPACE(IUNIT)
    # GO TO 10

    # read the line list

    ill = 0
    fr0 = 0.0   # TODO(port): 预防空表时标号 100 处引用 fr0(Fortran 中为残留值)
    while True:                                 # 标号 8 / 标号 10
        ill = ill + 1
        # ivdwli(ilist)=1(已注释掉)
        try:
            if C.IBIN[ilist] == 0:
                # if(ivdwli(ilist).ne.0) then(已注释掉)
                if np_l == 9:
                    # read(iunit,*,end=100) alam,anum,gf,excl,gr,gh2,xnh2,ghe,xnhe
                    _tk = read_line(iunit).replace(',', ' ').split()
                    alam = _c14_rdf(_tk[0]); anum = _c14_rdf(_tk[1])
                    gf = _c14_rdf(_tk[2]); excl = _c14_rdf(_tk[3])
                    gr = _c14_rdf(_tk[4]); gh2 = _c14_rdf(_tk[5])
                    xnh2 = _c14_rdf(_tk[6]); ghe = _c14_rdf(_tk[7])
                    xnhe = _c14_rdf(_tk[8])
                elif np_l == 7:
                    # READ(IUNIT,*,END=100,err=8) ALAM,ANUM,GF,EXCL,GR,GS,GW
                    try:
                        _tk = read_line(iunit).replace(',', ' ').split()
                        alam = _c14_rdf(_tk[0]); anum = _c14_rdf(_tk[1])
                        gf = _c14_rdf(_tk[2]); excl = _c14_rdf(_tk[3])
                        gr = _c14_rdf(_tk[4]); gs = _c14_rdf(_tk[5])
                        gw = _c14_rdf(_tk[6])
                    except (ValueError, IndexError):
                        continue                # err=8 → 回到标号 8(下一轮)
                else:
                    # read(iunit,*,end=100,err=8) alam,anum,gf,excl
                    try:
                        _tk = read_line(iunit).replace(',', ' ').split()
                        alam = _c14_rdf(_tk[0]); anum = _c14_rdf(_tk[1])
                        gf = _c14_rdf(_tk[2]); excl = _c14_rdf(_tk[3])
                    except (ValueError, IndexError):
                        continue                # err=8
                    gr = 2.4e13 / alam**2
                    gs = C.gsstd
                    gw = C.gwstd
            else:
                # if(ivdwli(ilist).ne.0) then(已注释掉)
                _rec = _c14_unf_record(iunit)   # read(iunit,end=100) ...
                if np_l == 9:
                    alam = _rec[0]; anum = _rec[1]; gf = _rec[2]; excl = _rec[3]
                    gr = _rec[4]; gh2 = _rec[5]; xnh2 = _rec[6]
                    ghe = _rec[7]; xnhe = _rec[8]
                elif np_l == 7:
                    alam = _rec[0]; anum = _rec[1]; gf = _rec[2]; excl = _rec[3]
                    gr = _rec[4]; gs = _rec[5]; gw = _rec[6]
                else:
                    alam = _rec[0]; anum = _rec[1]; gf = _rec[2]; excl = _rec[3]
                    gr = 2.4e13 / alam**2
                    gs = C.gsstd
                    gw = C.gwstd
        except EOFError:
            break                               # end=100

        # change wavelength to vacuum for lambda > 2000

        if alam > 200.0 and C.vaclim > 2000.0:
            wl0 = alam * 10.0
            alm = 1.0e8 / (wl0 * wl0)
            xn1 = 64.328 + 29498.1 / (146.0 - alm) + 255.4 / (41.0 - alm)
            wl0 = wl0 * (xn1 * 1.0e-6 + UN)
            alam = wl0 * 0.1

        # first selection : for a given interval

        if alam > C.ALASTM[ilist] + cutoff:
            break                               # GO TO 100

        # second selection : for line strengths

        fr0 = CNM / alam
        icod = int(anum + TENM4)

        # IF(ICOD.EQ.823) go to 10(已注释掉)

        imol = C.MOLIND[icod]
        if imol <= 0 or imol > C.NMOLEC:
            continue                            # go to 10
        excl = abs(excl)
        gfp = C1 * gf - C2
        epp = C3 * excl
        gx = gfp - epp / C.TSTD
        ab0 = 0.0

        if C.NDSTEP == 0 and C.IFWIN == 0:
            # old procedure for line rejection
            if gx > -30:
                ab0 = math.exp(gfp - epp / C.TSTD) * C.RRMOL[imol, C.IDSTD] / dopstd / avab
            if ab0 < UN:
                continue                        # GO TO 10
        else:
            # new procedure for line rejection
            for ijcn in range(ijc, C.NFREQC + 1):
                if fr0 >= C.FREQC[ijcn]:
                    break                       # go to 12
            # 12 continue(循环正常结束时 Fortran 中 ijcn=NFREQC+1,
            # 下面的 ijc 截断到 NFREQC,结果一致)
            ijc = ijcn
            if ijc > C.NFREQC:
                ijc = C.NFREQC

            tkm = 1.65e8 / C.AMMOL[imol]
            dp0 = 3.33564e-11 * fr0
            _selected = False
            for id in range(1, C.ND + 1, C.NDSTEP):
                td = C.TEMP[id]
                gx = gfp - epp / td
                ab0 = 0.0
                if gx > -30:
                    dops = dp0 * math.sqrt(tkm * td + C.VTURB[id])
                    ab0 = math.exp(gx) * C.RRMOL[imol, id] / (dops * C.ABSTDW[ijc, id] * C.RELOP)
                if ab0 >= UN:
                    _selected = True
                    break                       # go to 15
            if not _selected:
                continue                        # GO TO 10

        # truncate line list if there are more lines than maximum allowable
        # (given by MLIN0 - see include file LINDAT.FOR)

        # 15 CONTINUE
        il = il + 1
        if il > MLINM0:
            # 601 FORMAT('0 **** MORE LINES THAN MLINM0, LINE LIST TRUNCATED '/
            #      '       AT LAMBDA',F15.4,'  NM'/)
            print('0 **** MORE LINES THAN MLINM0, LINE LIST TRUNCATED ')
            print('       AT LAMBDA%15.4f  NM' % alam)
            print('')
            il = MLINM0
            C.ALASTM[ilist] = CNM / C.FREQM[il, ilist] - cutoff
            C.FRLASM[ilist] = CNM / C.ALASTM[ilist]
            C.NXTSEM[ilist] = 1
            break                               # GO TO 100

        # =============================================
        # line is selected, set up necessary parameters
        # =============================================

        # evaluation of EXTIN0 - the distance (in delta frequency) where
        # the line is supposed to contribute to the total opacity

        ex0 = ab0 * astd * 10.0
        ext = EXT0
        if ex0 > TEN:
            ext = math.sqrt(ex0)
        extin0 = ext * dopstd

        # store parameters for selected lines

        C.FREQM[il, ilist] = fr0
        C.EXCLM[il, ilist] = float(epp)         # real(EPP):目标数组为 float32
        C.GFM[il, ilist] = float(gfp)           # real(GFP)
        C.EXTINM[il, ilist] = float(extin0)     # real(EXTIN0)
        C.INDATM[il, ilist] = imol

        # ****** line broadening parameters *****
        #       assuming for Stark 1.e-8*effnsq**5/2, with effnsq=25

        C.GRM[il, ilist] = float(gr * PI4)          # real(GR*PI4)
        C.GSM[il, ilist] = float(gs * PI4 * 3.125e-5)
        C.GWM[il, ilist] = float(gw * PI4)

        # IF(imol.eq.30) gwm(il,ilist)=0.(已注释掉)

        if C.IVDWLI[ilist] != 0:
            C.GVDWH2[il, ilist] = float(gh2)        # real(gh2)
            C.GEXPH2[il, ilist] = float(xnh2)
            C.GVDWHE[il, ilist] = float(ghe)
            C.GEXPHE[il, ilist] = float(xnhe)
            C.GSM[il, ilist] = 0.0
            C.GWM[il, ilist] = 0.0

        # GO TO 10 → 回到循环开头
    # 100
    C.NLINM0[ilist] = il
    C.NLINMT[ilist] = C.NLINMT[ilist] + C.NLINM0[ilist]
    C.alend[ilist] = CNM / fr0

    xln = float(il) * 1.0e-6
    # 611 FORMAT(/' --------------------------------------------'/
    #      ' MOLECULAR LINES - FROM UNIT ',i3,
    #      ', FILE  ',a,':',f8.3,' M'/
    #      ' --------------------------------------------'/)
    print('')
    print(' --------------------------------------------')
    print(' MOLECULAR LINES - FROM UNIT %3d, FILE  %s:%8.3f M' %
          (iunit, C.AMLIST[ilist].strip(), xln))   # trim(amlist(ilist))
    print(' --------------------------------------------')
    print('')
    return


# *******************************************************************

def molset(ilist):
    """Selection of molecular lines that may contribute,
    set up auxiliary fields containing line parameters.

    对应 synspec54.f 行 18298–18440(SUBROUTINE MOLSET)。
    SAVE IMLAST → 模块级 _save_molset_imlast。
    """
    global _save_molset_imlast
    CNM = 2.997925e17                           # DATA CNM /2.997925D17/

    if C.INACTM[ilist] != 0:
        return
    il0 = 0
    C.IPRSEM[ilist] = 0
    nlinm = 0
    C.IREADM[ilist] = 1
    if C.IBLANK <= 1 or C.IMODE == 1 or C.IMODE == -1:
        C.IREADM[ilist] = 0
    if C.IBLANK <= 1:
        aprev = 0.0
    ala0 = CNM / C.FREQ[1]
    ala1 = CNM / C.FREQ[2]

    # skip if current wavelength larger than the largest wavelngth in the
    # line list

    if ala0 > C.alend[ilist]:
        C.INACTM[ilist] = 1
        return

    frminm = CNM / ala0
    frm = frminm
    space = C.SPACE0
    if C.ALAMC > 0.0:
        space = C.SPACE0 * ala0 / C.ALAMC
    if C.SPACE0 < 0.0:
        space = -C.SPACE0

    cutoff = C.CUTOF0 * 0.2
    dopstd = 1.0e7 / ala0 * C.DSTD
    distan = 0.15 * dopstd
    spac = 3.0e16 / ala0 / ala0 * space
    dista0 = 0.14 * spac
    if C.IBLANK >= 2 and C.IMODE == -1:
        il0 = _save_molset_imlast
    C.FRLI0 = frminm
    astd = 1.0
    avab = C.ABSTD[C.IDSTD] * C.RELOP

    while True:                                     # 20 CONTINUE
        # set up indices of lines
        # IL0 - is the current index of line in the numbering of all lines

        if C.IREADM[ilist] == 1:
            C.IPRSEM[ilist] = C.IPRSEM[ilist] + 1
            il0 = C.INMLIP[C.IPRSEM[ilist], ilist]
            if C.FREQM[il0, ilist] < frminm:
                C.IREADM[ilist] = 0
                il0 = C.INMLIP[C.IPRSEM[ilist] - 1, ilist] + 1
        else:
            il0 = il0 + 1
        if il0 > C.NLINM0[ilist]:
            break                                   # GO TO 210
        C.FRLIM = C.FRLI0
        fr0 = C.FREQM[il0, ilist]
        alam = CNM / fr0

        if alam < ala0 - cutoff:
            continue                                # GO TO 20
        if alam > ala1 + cutoff:
            break                                   # GO TO 210

        # SECOND SELECTION : FOR LINE STRENGHTS

        ext = C.EXTINM[il0, ilist]
        C.FRLI0 = fr0 - ext - spac
        if C.FRLI0 > C.FRLIM:
            C.FRLI0 = C.FRLIM
        if alam < ala0 and fr0 - frminm > ext + spac:
            continue                                # GO TO 20
        if C.FREQ[C.NFREQS] - fr0 > ext + spac:
            continue                                # GO TO 20

        nlinm = nlinm + 1
        if nlinm > MLINM:
            print('nlinm,mlinm', nlinm, MLINM)
            quit('too many molecular lines in a set')
        C.INMLIN[nlinm, ilist] = il0
        # GO TO 20 → 回到循环开头

    # frequency indices of the line centers

    # 210 CONTINUE
    xx = C.FREQ[2] - C.FREQ[1]
    C.DFRCON = C.NFREQ - 3
    C.DFRCON = -C.DFRCON / xx
    ifrcon = int(C.DFRCON)
    for il in range(1, nlinm + 1):                  # DO 255 IL=1,NLINM
        fr0 = C.FREQM[C.INMLIN[il, ilist], ilist]
        xjc = 3.0 + C.DFRCON * (C.FREQ[1] - fr0)
        ijc = int(xjc)
        C.IJCMTR[il, ilist] = ijc
        if ijc <= 3 or ijc >= C.NFREQ:
            continue                                # go to 255
        if fr0 < C.FREQ[ijc]:
            ijc0 = ijc
            dfr0 = C.FREQ[ijc0] - fr0
            while True:                             # 252
                ijc0 = ijc0 + 1
                dfr = abs(C.FREQ[ijc0] - fr0)
                if not (dfr < dfr0):
                    break
                ijc = ijc0
                ijc0 = ijc0 + 1
                dfr0 = dfr
                # go to 252
        elif fr0 > C.FREQ[ijc]:
            ijc0 = ijc
            dfr0 = fr0 - C.FREQ[ijc0]
            while True:                             # 254
                ijc0 = ijc0 - 1
                dfr = abs(C.FREQ[ijc0] - fr0)
                if not (dfr < dfr0):
                    break
                ijc = ijc0
                ijc0 = ijc0 - 1
                dfr0 = dfr
                # go to 254
        C.IJCMTR[il, ilist] = ijc
    # 255 continue

    for il in range(1, nlinm + 1):
        C.INMLIP[il, ilist] = C.INMLIN[il, ilist]
    C.NLINML[ilist] = nlinm
    _save_molset_imlast = C.INMLIN[C.NLINML[ilist], ilist]   # IMLAST=...

    iniblm()                                        # CALL INIBLM

    #      write(6,611) inmlin(1,ilist),inmlin(nlinm,ilist),
    #     * 2.997925e18/freqm(inmlin(1,ilist),ILIST),
    #     * 2.997925e18/freqm(inmlin(nlinm,ilist),ILIST)
    # 611  format('mols',2i7,2f10.3)
    return


# *******************************************************************

def iniblm():
    """driving procedure for treating a partial molecular line list for the
    current wavelength region

    对应 synspec54.f 行 18447–18477(SUBROUTINE INIBLM)。
    """
    DP0 = 3.33564e-11; DP1 = 1.651e8; UN = 1.0      # PARAMETER

    xx = C.FREQ[1]
    if C.NFREQ >= 2:
        xx = 0.5 * (C.FREQ[1] + C.FREQ[2])
    bnu = BN * (xx * 1.0e-15)**3
    hkf = HK * xx
    for id in range(1, C.ND + 1):
        t = C.TEMP[id]
        exh = math.exp(hkf / t)
        C.EXHK[id] = UN / exh
        C.PLAN[id] = bnu / (exh - UN)
        C.STIM[id] = UN - C.EXHK[id]
        for imol in range(1, C.NMOLEC + 1):
            if C.AMMOL[imol] > 0.0:
                C.DOPMOL[imol, id] = UN / (xx * DP0 * math.sqrt(
                    DP1 * t / C.AMMOL[imol] + C.VTURB[id]))
    return


# *******************************************************************

def idmtab():
    """output of selected molecular line parameters (identification table)

    对应 synspec54.f 行 18482–18567(SUBROUTINE IDMTAB)。
    """
    C1 = 2.3025851; C2 = 4.2014672; C3 = 1.4387886  # PARAMETER
    # DATA APB,AP0,AP1,AP2,AP3,AP4 /'    ','   .','   *','  **',' ***','****'/
    APB = '    '; AP0 = '   .'; AP1 = '   *'
    AP2 = '  **'; AP3 = ' ***'; AP4 = '****'

    alm0 = 2.997925e18 / C.FREQ[1]
    alm1 = 2.997925e18 / C.FREQ[2]
    if C.IFWIN > 0:
        alm1 = 2.997925e18 / C.FREQ[C.NFREQ]
    if C.IPRIN <= -2:
        return
    if C.IPRIN >= 3:
        if C.IMODE >= 0:
            # 601 FORMAT(/' ',I4,'. SET (MOLECULAR LINES):',
            #      ' INTERVAL  ',F9.3,' -',F9.3,' ANGSTROMS'/' ------------')
            print('')
            print(' %4d. SET (MOLECULAR LINES): INTERVAL  %9.3f -%9.3f ANGSTROMS'
                  % (C.IBLANK, alm0, alm1))
            print(' ------------')
        if C.IMODE >= 0 or (C.IMODE == -1 and C.IBLANK == 1):
            # 602 FORMAT(/1H ,13X,'LAMBDA  MOLECULE  LOG GF       ELO
            #      LINE/CONT',2X,'EQ.WIDTH',8x,'AGAM'/)
            print('')
            print(' ' + ' ' * 13 + 'LAMBDA  MOLECULE  LOG GF       ELO    LINE/CONT'
                  + '  ' + 'EQ.WIDTH' + ' ' * 8 + 'AGAM')
            print('')

    id = C.IDSTD
    for ilist in range(1, C.NMLIST + 1):            # DO 100 ILIST=1,NMLIST
        if C.NLINML[ilist] == 0:
            continue                                # GO TO 100
        for il0 in range(1, C.NLINML[ilist] + 1):
            il = C.INMLIN[il0, ilist]
            alam = 2.997925e18 / C.FREQM[il, ilist]
            # ID=IDSTD(已注释掉)
            ijcn = C.IJCMTR[il0, ilist]
            # IF(IJCN.GE.1.AND.IJCN.LE.NFREQS) ID=IREFD(IJCN)(已注释掉)
            imol = C.INDATM[il, ilist]
            dop1 = C.DOPMOL[imol, id]
            ane = C.ELEC[id]
            # TODO(port): GVDW 在 commons.py 的 DECLS 中缺失(原文亦未见声明,
            # 疑为 GVDW(MLINM0,MMLIST,MDEPTH) 一类的隐式公共数组)
            agam = (C.GRM[il, ilist] + C.GSM[il, ilist] * ane +
                    gvdw(il, ilist, id)) * dop1
            abcnt = math.exp(C.GFM[il, ilist] - C.EXCLM[il, ilist] / C.TEMP[id]) * \
                C.RRMOL[imol, id] * dop1 * C.STIM[id]
            absta = min(C.CH[1, id], C.CH[2, id])
            str0 = abcnt / absta
            if C.IFWIN > 0:
                str0 = abcnt / C.ABSTDW[C.IJCONT[il], id]
            gf = (C.GFM[il, ilist] + C2) / C1
            excl = C.EXCLM[il, ilist] / C3
            if str0 <= 1.2:
                ww1 = 0.886 * str0 * (1.0 - str0 * (0.707 - str0 * 0.577))
            else:
                ww1 = math.sqrt(math.log(str0))
            if str0 > 55.0:
                ww2 = 0.5 * math.sqrt(3.14 * agam * str0)
                if ww2 > ww1:
                    ww1 = ww2
            eqw = alam / C.FREQM[il, ilist] * 1.0e3 / dop1 * ww1
            str_l = eqw * 10.0                      # 原局部变量 STR,改名避免歧义
            apr = APB
            if str_l >= 1.0e0 and str_l < 1.0e1:
                apr = AP0
            if str_l >= 1.0e1 and str_l < 1.0e2:
                apr = AP1
            if str_l >= 1.0e2 and str_l < 1.0e3:
                apr = AP2
            if str_l >= 1.0e3 and str_l < 1.0e4:
                apr = AP3
            if str_l >= 1.0e4:
                apr = AP4
            if alam >= alm0 and alam < alm1:
                # 603 FORMAT(F11.3,2X,A4,4X,F7.2,F12.3,1PE11.2,0PF8.1,1X,A4,
                #      i4,1PE10.2)
                write_line(15, '%11.3f  %-4s    %7.2f%12.3f%11.2e%8.1f %-4s%4d%10.2e'
                           % (alam, C.CMOL[imol], gf, excl, str0, eqw, apr, id, agam))
    # 100 CONTINUE
    return


# *******************************************************************

def molop(id, ablin, emlin, avab, ilist):
    """Total molecular line opacity (ABLIN) and emissivity (EMLIN)

    对应 synspec54.f 行 18574–18634(SUBROUTINE MOLOP)。
    数组哑元 ABLIN/EMLIN 就地修改,不返回;不修改任何标量哑元。
    """
    UN = 1.0; EXT0 = 3.17; TEN = 10.0               # PARAMETER

    for ij in range(1, C.NFREQ + 1):
        ablin[ij] = 0.0
        emlin[ij] = 0.0

    if C.TEMP[id] > C.TMOLIM:
        return
    if C.NLINML[ilist] == 0:
        return
    if C.INACTM[ilist] != 0:
        return

    # overall loop over contributing lines

    tem1 = UN / C.TEMP[id]
    ane = C.ELEC[id]
    for i in range(1, C.NLINML[ilist] + 1):
        il = C.INMLIN[i, ilist]
        imol = C.INDATM[il, ilist]
        dop1 = C.DOPMOL[imol, id]
        # TODO(port): GVDW 在 commons.py 的 DECLS 中缺失(同 IDMTAB)
        agam = (C.GRM[il, ilist] + C.GSM[il, ilist] * ane +
                gvdw(il, ilist, id)) * dop1
        fr0 = C.FREQM[il, ilist]
        ab0 = math.exp(C.GFM[il, ilist] - C.EXCLM[il, ilist] * tem1) * \
            C.RRMOL[imol, id] * dop1 * C.STIM[id]

        # set up limiting frequencies where the line I is supposed to
        # contribute to the opacity

        ex0 = ab0 / avab * agam
        ext = EXT0
        if ex0 > TEN:
            ext = math.sqrt(ex0)
        ext = ext / dop1
        xijext = C.DFRCON * ext + 1.5
        ij1 = int(max(float(C.IJCMTR[i, ilist]) - xijext, 3.0))
        ij2 = int(min(float(C.IJCMTR[i, ilist]) + xijext, float(C.NFREQS)))
        if ij1 < C.NFREQ and ij2 > 2:
            for ij in range(ij1, ij2 + 1):
                xf = abs(C.FREQ[ij] - fr0) * dop1
                ablin[ij] = ablin[ij] + ab0 * voigtk(agam, xf)

    for ij in range(3, C.NFREQ + 1):
        emlin[ij] = emlin[ij] + ablin[ij] * C.PLAN[id]

    return


# *******************************************************************

def sbfhmi(fr):
    """Bound-free cross-section for H- (negative hydrogen ion)
    Taken from Kurucz ATLAS9

    FROM MATHISEN (1984), AFTER WISHART(1979) AND BROAD AND REINHARDT (1976)

    对应 synspec54.f 行 18640–18681(FUNCTION SBFHMI)。
    """
    # DATA WBF/.../(85 个值,之后不再修改)
    wbf = np.zeros(86)
    wbf[1:] = [
        18.00, 19.60, 21.40, 23.60, 26.40, 29.80, 34.30,
        40.40, 49.10, 62.60, 111.30, 112.10, 112.67, 112.95, 113.05,
        113.10, 113.20, 113.23, 113.50, 114.40, 121.00, 139.00, 164.00,
        175.00, 200.00, 225.00, 250.00, 275.00, 300.00, 325.00, 350.00,
        375.00, 400.00, 425.00, 450.00, 475.00, 500.00, 525.00, 550.00,
        575.00, 600.00, 625.00, 650.00, 675.00, 700.00, 725.00, 750.00,
        775.00, 800.00, 825.00, 850.00, 875.00, 900.00, 925.00, 950.00,
        975.00, 1000.00, 1025.00, 1050.00, 1075.00, 1100.00, 1125.00, 1150.00,
        1175.00, 1200.00, 1225.00, 1250.00, 1275.00, 1300.00, 1325.00, 1350.00,
        1375.00, 1400.00, 1425.00, 1450.00, 1475.00, 1500.00, 1525.00, 1550.00,
        1575.00, 1600.00, 1610.00, 1620.00, 1630.00, 1643.91]
    # DATA BF/.../(85 个值)
    # Bell and Berrington J.Phys.B,vol. 20, 801-806,1987.
    bf = np.zeros(86)
    bf[1:] = [
        0.067, 0.088, 0.117, 0.155, 0.206, 0.283, 0.414,
        0.703, 1.24, 2.33, 11.60, 13.90, 24.30, 66.70, 95.00,
        56.60, 20.00, 14.60, 8.50, 7.10, 5.43, 5.91, 7.29,
        7.918, 9.453, 11.08, 12.75, 14.46, 16.19, 17.92, 19.65,
        21.35, 23.02, 24.65, 26.24, 27.77, 29.23, 30.62, 31.94,
        33.17, 34.32, 35.37, 36.32, 37.17, 37.91, 38.54, 39.07,
        39.48, 39.77, 39.95, 40.01, 39.95, 39.77, 39.48, 39.06,
        38.53, 37.89, 37.13, 36.25, 35.28, 34.19, 33.01, 31.72,
        30.34, 28.87, 27.33, 25.71, 24.02, 22.26, 20.46, 18.62,
        16.74, 14.85, 12.95, 11.07, 9.211, 7.407, 5.677, 4.052,
        2.575, 1.302, 0.8697, 0.4974, 0.1989, 0.0]

    hminbf = 0.0
    if fr > 1.82365e14:
        wave = 2.99792458e17 / fr
        hminbf = ylintp(wave, wbf, bf, 85, 85) * 1.0e-18
    return hminbf                                   # SBFHMI=HMINBF


# *******************************************************************

def sffhmi(popi, fr, t):
    """Free-free cross-section for H- (negative hydrogen ion)
    Taken from Kurucz ATLAS9

    From Bell and Berrington J.Phys.B,vol. 20, 801-806,1987.

    对应 synspec54.f 行 18688–18757(FUNCTION SFFHMI)。
    DATA ISTART/0/ 之后被修改 → 模块级 _save_sffhmi_istart;
    FFLOG/WFFLOG 只在首次调用计算、之后使用 → 模块级 _save_sffhmi_fflog/_wfflog。
    """
    global _save_sffhmi_istart
    CONFF = 5040.0 * 1.380658e-16; CONTH = 5040.0   # PARAMETER
    # FFCS(11,22); EQUIVALENCE (FFCS(1,1),FFBEG(1,1)),(FFCS(1,12),FFEND(1,1)):
    # FFCS 的第 1–11 列 = FFBEG,第 12–22 列 = FFEND(列主序)
    wavek = np.zeros(23)
    wavek[1:] = [0.50, 0.40, 0.35, 0.30, 0.25, 0.20, 0.18, 0.16, 0.14, 0.12,
                 0.10, 0.09, 0.08, 0.07, 0.06, 0.05, 0.04, 0.03, 0.02, 0.01,
                 0.008, 0.006]
    thetaff = np.zeros(12)
    thetaff[1:] = [0.5, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0, 2.8, 3.6]
    # DATA FFBEG/(11x11,按列填充)
    ffbeg_flat = [
        .0178, .0222, .0308, .0402, .0498, .0596, .0695, .0795, .0896, .131, .172,
        .0228, .0280, .0388, .0499, .0614, .0732, .0851, .0972, .110, .160, .211,
        .0277, .0342, .0476, .0615, .0760, .0908, .105, .121, .136, .199, .262,
        .0364, .0447, .0616, .0789, .0966, .114, .132, .150, .169, .243, .318,
        .0520, .0633, .0859, .108, .131, .154, .178, .201, .225, .321, .418,
        .0791, .0959, .129, .161, .194, .227, .260, .293, .327, .463, .602,
        .0965, .117, .157, .195, .234, .272, .311, .351, .390, .549, .711,
        .121, .146, .195, .241, .288, .334, .381, .428, .475, .667, .861,
        .154, .188, .249, .309, .367, .424, .482, .539, .597, .830, 1.07,
        .208, .250, .332, .409, .484, .557, .630, .702, .774, 1.06, 1.36,
        .293, .354, .468, .576, .677, .777, .874, .969, 1.06, 1.45, 1.83]
    # DATA FFEND/(11x11,按列填充)
    ffend_flat = [
        .358, .432, .572, .702, .825, .943, 1.06, 1.17, 1.28, 1.73, 2.17,
        .448, .539, .711, .871, 1.02, 1.16, 1.29, 1.43, 1.57, 2.09, 2.60,
        .579, .699, .924, 1.13, 1.33, 1.51, 1.69, 1.86, 2.02, 2.67, 3.31,
        .781, .940, 1.24, 1.52, 1.78, 2.02, 2.26, 2.48, 2.69, 3.52, 4.31,
        1.11, 1.34, 1.77, 2.17, 2.53, 2.87, 3.20, 3.51, 3.80, 4.92, 5.97,
        1.73, 2.08, 2.74, 3.37, 3.90, 4.50, 5.01, 5.50, 5.95, 7.59, 9.06,
        3.04, 3.65, 4.80, 5.86, 6.86, 7.79, 8.67, 9.50, 10.3, 13.2, 15.6,
        6.79, 8.16, 10.7, 13.1, 15.3, 17.4, 19.4, 21.2, 23.0, 29.5, 35.0,
        27.0, 32.4, 42.6, 51.9, 60.7, 68.9, 76.8, 84.2, 91.4, 117., 140.,
        42.3, 50.6, 66.4, 80.8, 94.5, 107., 120., 131., 142., 183., 219.,
        75.1, 90.0, 118., 144., 168., 191., 212., 234., 253., 325., 388.]
    ffcs = np.zeros((12, 23))
    ffcs[1:12, 1:12] = np.array(ffbeg_flat).reshape((11, 11), order='F')
    ffcs[1:12, 12:23] = np.array(ffend_flat).reshape((11, 11), order='F')
    fftt = np.zeros(12)
    fflog2 = np.zeros(23)

    if _save_sffhmi_istart == 0:
        _save_sffhmi_istart = 1
        for iwave in range(1, 23):                  # DO 2 IWAVE=1,22
            _save_sffhmi_wfflog[iwave] = math.log(91.134 / wavek[iwave])
            for itheta in range(1, 12):
                _save_sffhmi_fflog[iwave, itheta] = math.log(ffcs[itheta, iwave] * 1.0e-26)
        # 2 CONTINUE

    wave = 2.99792458e17 / fr
    wavelog = math.log(wave)

    for itheta in range(1, 12):                     # DO 21 ITHETA=1,11
        for iwave in range(1, 23):
            fflog2[iwave] = _save_sffhmi_fflog[iwave, itheta]
        fftlog = ylintp(wavelog, _save_sffhmi_wfflog, fflog2, 22, 22)
        fftt[itheta] = math.exp(fftlog) / thetaff[itheta] * CONFF
    # 21 CONTINUE

    theta = CONTH / t
    ffth = ylintp(theta, thetaff, fftt, 11, 11)
    return ffth * popi / (1.0 - math.exp(-HK * fr / t))   # SFFHMI=...


# *************************************************************************

def mpartf(jatom, ion, indmol, t, u):
    """yields partition functions with polynomial data from
    ref. Irwin, A.W., 1981, ApJ Suppl. 45, 621.
    ln u(temp)=sum(a(i)*(ln(temp))**(i-1)) 1<=a<=6

    Input:
      jatom = element number in periodic table
      ion   = 1 for neutral, 2 for once ionized and 3 for twice ionized
      indmol= index of a molecular specie (Tsuji index)
      temp  = temperature
    Output:
      u     = partf.(linear scale) for iat,ion, or indmol, and temperature t

    对应 synspec54.f 行 18768–18901(SUBROUTINE MPARTF)。
    修改标量哑元 u,按约定返回全部标量哑元。
    save iread,a,am → 模块级 _save_mpartf_*(irw 一并提升,见模块级注释)。
    """
    global _save_mpartf_iread
    aa = np.zeros(7)

    # data indtsu(324 个值;原文另有两组被注释掉的旧版本)
    indtsu = np.zeros(325, dtype=np.int64)
    indtsu[1:] = ([2, 5, 12, 4, 8, 7, 6,
                   9, 11, 10, 29, 50, 59, 46, 133, 52, 19,
                   13, 42, 38, 39, 37, 44, 36, 14, 118, 33,
                   3, 16, 57, 32, 49, 60, 54, 41, 107, 304,
                   148, 152, 153, 155, 303, 17, 24, 25, 28, 51,
                   112, 119, 102, 0, 21, 15, 43, 22, 478, 64,
                   47, 65, 414, 61, 191, 62, 109, 40, 66, 214]
                  + [0] * 120 + [30] + [0] * 136)

    # data iread /0/ → 模块级 _save_mpartf_iread

    # read data if first call:

    if _save_mpartf_iread != 1:
        if C.IRWTAB == 0:
            open_unit(67, './data/irwin_orig.dat', 'r')
            nummol = 66
        else:
            open_unit(67, './data/irwin_bc.dat', 'r')
            nummol = 324
        read_line(67)                               # read(67,*)
        read_line(67)                               # read(67,*)
        for j in range(1, 93):
            for i in range(1, 4):
                if j == 1 and i == 3:
                    continue                        # goto 10
                sp = float(j) + float(i - 1) / 100.0
                # read(67,*) spec,aa
                _tk = read_line(67).replace(',', ' ').split()
                spec = _c14_rdf(_tk[0])
                for k in range(1, 7):
                    aa[k] = _c14_rdf(_tk[k])
                for k in range(1, 7):
                    _save_mpartf_a[k, i, j] = aa[k]
            # 10 continue

        read_line(67)                               # read(67,*)
        read_line(67)                               # read(67,*)
        read_line(67)                               # read(67,*)
        for i in range(1, 501):
            _save_mpartf_irw[i] = 0
        i = 0
        while i < nummol:                           # do i=1,nummol(end=15)
            i = i + 1
            try:
                # read(67,*,end=15) spec,aa
                _tk = read_line(67).replace(',', ' ').split()
            except EOFError:
                break                               # end=15
            spec = _c14_rdf(_tk[0])
            for k in range(1, 7):
                aa[k] = _c14_rdf(_tk[k])
            indm = indtsu[i]
            if indm > 0:
                _save_mpartf_irw[indm] = i
                for j in range(1, 7):
                    _save_mpartf_am[j, indm] = aa[j]
        # 15 continue
        close_unit(67)
        _save_mpartf_iread = 1

    # evaluation of the partition function
    # stop if T is out of limits of Irwin's tables

    if t < 1000.0:
        raise SystemExit('partf; temp<1000 K')      # stop 'partf; temp<1000 K'
    elif t > 16000.0:
        raise SystemExit('partf; temp>16000 K')     # stop 'partf; temp>16000 K'
    tl = math.log(t)
    u = 0.0

    # atomic species

    if jatom > 0 and ion > 0:
        ulog = (_save_mpartf_a[1, ion, jatom] +
                tl * (_save_mpartf_a[2, ion, jatom] +
                tl * (_save_mpartf_a[3, ion, jatom] +
                tl * (_save_mpartf_a[4, ion, jatom] +
                tl * (_save_mpartf_a[5, ion, jatom] +
                tl * (_save_mpartf_a[6, ion, jatom]))))))
        if jatom == 5 and ion == 3:
            ulog = 1.0
        u = math.exp(ulog)

    # molecular species

    if indmol > 0:
        indm = indmol
        if _save_mpartf_irw[indm] > 0:
            ulog = (_save_mpartf_am[1, indm] +
                    tl * (_save_mpartf_am[2, indm] +
                    tl * (_save_mpartf_am[3, indm] +
                    tl * (_save_mpartf_am[4, indm] +
                    tl * (_save_mpartf_am[5, indm] +
                    tl * (_save_mpartf_am[6, indm]))))))
            u = math.exp(ulog)
            # if(t.gt.5128..and.t.lt.5129)
            #     write(6,631) t,indmol,indm,u(已注释掉)
            # 631 format('mpartf',f10.1,2i5,f16.3)
    return jatom, ion, indmol, t, u


# *************************************************************************

def moleq(id, tt, an, aein, ane, ipri):
    """calculation of the equilibrium state of atoms and molecules

    Input:  id    - depth point
            tt    - temperature [K]
            an    - number density
            aein  - initial estimate of the electron density

    Output: ane    - electron density

    Output through common/atomol:
            rrr(id,j,i) - N/U for the atom with atomic number i and
                    ion j (j=1 for neutral, and j=2 for 1st ions)
            rrmol(imol,id) - N/U for the molecule with index imol
                    (the index is given by the ordering of
                    in the input file  tsuji.molec


    Input data for molecules  iven in the file
    tsuji.molec

    对应 synspec54.f 行 18909–19170(SUBROUTINE MOLEQ)。
    修改标量哑元 ane,按约定返回全部标量哑元 (id,tt,an,aein,ane,ipri)。
    DATA iread/1/ 之后被修改 → 模块级 _save_moleq_iread。
    """
    global _save_moleq_iread
    # 注意: COMMON/COMFH1/ 中的数组 C(600,5) 经 commons.py 访问为 C.C
    #       ( commons 模块别名为 C,公共块变量名为 C,故写作 C.C[j,k] )
    natomm = np.zeros(6, dtype=np.int64)
    nelemm = np.zeros(6, dtype=np.int64)
    emass = np.zeros(101)
    uelem = np.zeros(101)
    ull = np.zeros(101)
    anden = np.zeros(801)
    aelem = np.zeros(101)
    denso = np.zeros(MDEPTH + 1)
    eleco = np.zeros(MDEPTH + 1)
    wmmo = np.zeros(MDEPTH + 1)
    nelemi = 0   # TODO(port): 见下文 aelem(99) 处对 nelemi 的引用

    # data nmetal/92/(初始化 COMFH1 公共块变量,见下)
    # data iread/1/ → 模块级 _save_moleq_iread

    molec = 'data/tsuji.molec_bc2'                  # character*128 MOLEC
    if C.MOLTAB == 0:
        molec = 'data/tsuji.molec_orig'

    econst = 4.342945e-1
    avo = 0.602217e24
    spa = 0.196e-1
    gra = 0.275423e5
    ahe = 0.100e0
    tk = 1.0 / (tt * 1.38054e-16)
    pgas = an / tk
    sahcon = 1.87840e20 * tt * math.sqrt(tt)
    C.NIMAX = 3000
    C.EPS = 1.0e-5
    C.SWITER = 0.0

    # ---- data for atoms  ----------------

    if _save_moleq_iread == 1:
        C.NMETAL = 92   # data nmetal/92/(COMFH1 公共块变量的 DATA 初始化)

        for i in range(1, C.NMETAL + 1):
            ia = i
            C.NELEMX[i] = ia
            C.CCOMP[ia] = C.ABNDD[ia, id]
            C.XIP[ia] = C.ENEV[ia, 1]
            C.XI2[ia] = C.ENEV[ia, 2]
            emass[ia] = C.AMAS[ia]

        # ---- read molecular data from a table  ----------------------

        j = 0
        open_unit(26, molec, 'r')                   # OPEN(UNIT=26,FILE=MOLEC,STATUS='OLD')
        while True:                                 # 10
            j = j + 1
            try:
                _ln = read_line(26)
            except EOFError:
                break                               # end=20
            if C.MOLTAB >= 1:
                # 510 format(a8,5e13.5,9i3)
                C.CMOL[j] = _ln[0:8]
                for k in range(1, 6):
                    C.C[j, k] = _c14_rdf(_ln[8 + 13 * (k - 1): 8 + 13 * k])
                C.MMAX[j] = _c14_rdi(_ln[73:76])
                for m in range(1, 5):
                    nelemm[m] = _c14_rdi(_ln[76 + 6 * (m - 1): 79 + 6 * (m - 1)])
                    natomm[m] = _c14_rdi(_ln[79 + 6 * (m - 1): 82 + 6 * (m - 1)])
            else:
                # 511 FORMAT (A8,E11.5,4E12.5,I1,(I2,I3),3(I2,I2))
                C.CMOL[j] = _ln[0:8]
                C.C[j, 1] = _c14_rdf(_ln[8:19])
                for k in range(2, 6):
                    C.C[j, k] = _c14_rdf(_ln[19 + 12 * (k - 2): 19 + 12 * (k - 1)])
                C.MMAX[j] = _c14_rdi(_ln[67:68])
                nelemm[1] = _c14_rdi(_ln[68:70])
                natomm[1] = _c14_rdi(_ln[70:73])
                for m in range(2, 5):
                    nelemm[m] = _c14_rdi(_ln[73 + 4 * (m - 2): 75 + 4 * (m - 2)])
                    natomm[m] = _c14_rdi(_ln[75 + 4 * (m - 2): 77 + 4 * (m - 2)])

            # for now, exclude all molecules with 4 or more C atoms

            _excluded = False
            for m in range(1, 5):
                if nelemm[m] == 6 and natomm[m] >= 5:
                    j = j - 1
                    _excluded = True
                    break                           # go to 10
            if _excluded:
                continue

            mmaxj = C.MMAX[j]
            if mmaxj == 0:
                break                               # GO TO 20
            for m in range(1, mmaxj + 1):
                C.NELEM[m, j] = nelemm[m]
                C.NATO[m, j] = natomm[m]
            # write(6,680) j,cmol(j)(已注释掉)
            # 680 format(i5,a10)
            # GO TO 10 → 回到循环开头
        # 20
        C.NMOLEC = j - 1
        close_unit(26)

        for i in range(1, C.NMETAL + 1):
            nelemi = C.NELEMX[i]
            C.P[nelemi] = 1.0e-70
        _save_moleq_iread = 0

    # ---- end of reading atomic and molecular data  ----------------------

    C.P[99] = aein / tk
    pesave = C.P[99]
    C.P[99] = pesave

    theta = 5040.0 / tt
    tem = tt
    pglog = math.log10(pgas)
    pg = pgas

    russel(tem, pg)             # CALL RUSSEL(TEM,PG);RUSSEL 不修改标量哑元

    pe = C.P[99]
    ane = pe * tk
    pelog = math.log10(pe)
    emass[99] = 5.486e-4
    uelem[99] = 2.0
    # TODO(port): 原文此处引用局部变量 nelemi,但在 MOLEQ 内此时它从未被赋值
    # (疑为原代码笔误,很可能本意是 emass(99));这里 nelemi=0,取数组未使用的
    # 0 号槽(值为 0.0),与 Fortran 未初始化局部变量的不确定值同样可疑。
    aelem[99] = pe * tk / (2.0 * sahcon * emass[nelemi]**1.5)
    ull[99] = math.log10(aelem[99])

    # ----atoms-----------------------------------------------------------------

    tmass = 0.0
    for i in range(1, C.NMETAL + 1):
        nelemi = C.NELEMX[i]
        fplog = math.log10(C.FP[nelemi])
        anden[i] = (C.P[nelemi] + 1.0e-70) * tk
        tmass = tmass + anden[i] * emass[nelemi]
        # IRWPF 修改标量哑元 u,按约定解包;实参 1/0 对应 ion/indmol
        nelemi, _ion_l, _ind_l, tt, u0 = irwpf(nelemi, 1, 0, tt, 0.0)
        uelem[nelemi] = u0
        aelem[nelemi] = anden[i] / (u0 * sahcon * emass[nelemi]**1.5)
        ull[nelemi] = math.log10(aelem[nelemi])
        C.RRR[id, 1, nelemi] = anden[i] / u0
        C.anato[nelemi, id] = anden[i]
        C.pfato[nelemi, id] = u0
    an1 = anden[1]

    # ---- positive ions ---------------------------------------------------------

    for i in range(1, C.NMETAL + 1):
        nelemi = C.NELEMX[i]
        plog = math.log10(C.P[nelemi] + 1.0e-70)
        xkplog = math.log10(C.XKP[nelemi] + 1.0e-70)
        pionl = plog + xkplog - pelog
        anden[i + C.NMETAL] = math.exp(pionl / econst) * tk
        tmass = tmass + anden[i + C.NMETAL] * emass[nelemi]
        nelemi, _ion_l, _ind_l, tt, u1 = irwpf(nelemi, 2, 0, tt, 0.0)
        C.anion[nelemi, id] = anden[i + C.NMETAL]
        C.pfion[nelemi, id] = u1
        C.RRR[id, 2, nelemi] = anden[i + C.NMETAL] / u1
        if nelemi >= 2 and nelemi <= 30:
            x2log = math.log10(C.XK2[nelemi] + 1.0e-70)
            pion2 = pionl + x2log - pelog
            C.anion2[nelemi, id] = math.exp(pion2 / econst) * tk
    C.anion2[1, id] = 0.0

    # ---- molecules-------------------------------------------------------------

    for j in range(1, C.NMOLEC + 1):
        jm = j + 2 * C.NMETAL
        pmoll = math.log10(C.PPMOL[j] + 1.0e-70)
        anden[jm] = math.exp(pmoll / econst) * tk
        C.RRMOL[j, id] = 0.0
        umoll = 1.0
        if pmoll > -30.0:
            umoll = math.log10(anden[jm]) + C.C[j, 2] * theta
            amasm = 0.0
            for jjj in range(1, C.MMAX[j] + 1):
                i = C.NELEM[jjj, j]
                amasm = amasm + C.NATO[jjj, j] * emass[i]
                umoll = umoll - C.NATO[jjj, j] * ull[i]
            C.AMMOL[j] = amasm
            tmass = tmass + anden[jm] * amasm
            umoll = math.exp(umoll / econst) / (sahcon * amasm**1.5)

            # replace with EXOMOL data whenever available

            um = 0.0
            if C.IPFEXO > 0 and tt <= 9000.0:
                j, tt, um = exopf(j, tt, um)        # EXOPF 修改标量哑元 u
            if um > 0.0:
                umoll = um
            else:
                # or with modified Irwin (Barklem & Collet) data whenever available
                _ja_l, _io_l, j, tt, um = irwpf(0, 0, j, tt, um)
                if um > 0.0:
                    umoll = um

            # H-

            if j == 1:
                umoll = 1.0

            # set up array RRR = number density/partition function

            C.RRMOL[j, id] = anden[jm] / umoll

        C.anmol[j, id] = anden[jm]
        C.pfmol[j, id] = umoll

    jm = 2 * C.NMETAL
    C.anhm[id] = anden[1 + jm]
    C.anh2[id] = anden[2 + jm]
    C.anch[id] = anden[5 + jm]
    C.anoh[id] = anden[4 + jm]

    # save new density, molecular weight, and abundances of
    # atomic species

    ipri1 = ipri
    denso[id] = C.DENS[id]
    eleco[id] = C.ELEC[id]
    wmmo[id] = C.WMM[id]
    C.DENS[id] = tmass * HMASS
    C.ELEC[id] = pe * tk
    C.WMM[id] = C.DENS[id] / (an - C.ELEC[id])
    ane = C.ELEC[id]

    for i in range(1, C.NMETAL + 1):
        nelemi = C.NELEMX[i]
        ia = C.IATEX[nelemi]
        if ia > 0:
            C.ATTOT[ia, id] = C.anato[nelemi, id] + C.anion[nelemi, id]

    if id == C.ND:
        # 610 format(/'  id     m         T       ne(old)   ne(new)',
        #      '  dens(old) dens(new) wmm(old)  wmm(new)'/)
        write_line(86, '')
        write_line(86, '  id     m         T       ne(old)   ne(new)'
                       '  dens(old) dens(new) wmm(old)  wmm(new)')
        write_line(86, '')
        for iid in range(1, C.ND + 1):
            # 611 format(i4,1p8e10.2)
            write_line(86, '%4d' % iid + ''.join('%10.2e' % v for v in (
                C.DM[iid], C.TEMP[iid], C.ELEC[iid], eleco[iid],
                C.DENS[iid], denso[iid], C.WMM[iid], wmmo[iid])))

    return id, tt, an, aein, ane, ipri
