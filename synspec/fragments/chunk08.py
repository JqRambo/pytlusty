# -*- coding: utf-8 -*-
"""chunk08: synspec54.f 行 8074–9866 的逐行直译。

包含子程序:
    INISET      (8074–8427)
    READPH      (8432–8581)
    INILIN      (8586–9192)
    INILIN_grid (9197–9579)
    INIBLA      (9586–9631)
    IDTAB       (9636–9732)
    INIBLH      (9737–9861)

模块级 _save_* 变量对应 Fortran 的 SAVE / DATA（隐含 SAVE）语义；
_chunk08_* 是本分片自带的 I/O 辅助（BACKSPACE 与无格式记录读）。
"""

# ===== DATA / SAVE 提升（Fortran 77 局部变量静态存活语义）=====
_save_iniset_illast = 0    # INISET: SAVE ILLAST
_save_iniset_aprev = 0.0   # INISET: APREV 需跨调用保留（原代码无 SAVE，但实际静态存活）
_save_inilin_inlset = 0    # INILIN: DATA INLSET /0/，随后置 1（隐含 SAVE）
_save_readph_numfil = 0                        # READPH: SAVE NUMFIL
_save_readph_ipht = np.zeros(MPHOT + 1, dtype=np.int64)          # READPH: SAVE IPHT
_save_readph_iend = np.zeros(MPHOT + 1, dtype=np.int64)          # READPH: SAVE IEND
_save_readph_nelem = np.zeros(MPHOT + 1, dtype=np.int64)         # READPH: SAVE NELEM
_save_readph_index = np.zeros((MPHOT + 1, MPHOT + 1), dtype=np.int64)  # READPH: SAVE INDEX

# 无格式（二进制）文件的记录起始位置栈，供 BACKSPACE 回退用
_chunk08_urec_pos = {}


def _chunk08_backspace(unit):
    """BACKSPACE(unit)：回退一个记录。

    文本文件回退一行；二进制无格式文件回退一条记录（靠记录位置栈）。
    """
    fh = funits[unit]
    if "b" in getattr(fh, "mode", ""):
        stack = _chunk08_urec_pos.get(unit)
        if stack:
            fh.seek(stack.pop())
        return
    end = fh.tell()
    if end <= 0:
        return
    pos = end - 1
    fh.seek(pos)
    if fh.read(1) == "\n":
        pos -= 1
    while pos > 0:
        fh.seek(pos - 1)
        if fh.read(1) == "\n":
            break
        pos -= 1
    fh.seek(pos)


def _chunk08_read_urec(unit):
    """无格式顺序 READ：读取一条完整记录，返回记录载荷 bytes。

    TODO(port): 假定 gfortran 约定（4 字节 little-endian 记录首尾标记），
    记录内部布局参照 linelist/list2bin.f：先写全部 REAL*8，再写全部 INTEGER*4。
    调用方按需要从载荷中切片解析；读完整条记录后剩余未解析部分即被跳过
    （与 Fortran 无格式 READ 只取前几个量的语义一致）。
    """
    fh = funits[unit]
    pos = fh.tell()
    hdr = fh.read(4)
    if len(hdr) < 4:
        raise EOFError("unit %d: end of unformatted file" % unit)
    nbytes = int.from_bytes(hdr, "little", signed=True)
    if nbytes < 0:
        # 记录长度标记为负：文件不是 gfortran 无格式顺序格式（例如误当二进制
        # 打开的文本文件）。Fortran 中为错误条件：有 ERR= 走 ERR 分支。
        raise ValueError("unit %d: bad record length %d" % (unit, nbytes))
    payload = fh.read(nbytes)
    if len(payload) < nbytes:
        # 记录被截断：Fortran 错误条件（区别于干净 EOF 的 END 分支）。
        # 用 ValueError 而非 EOFError，使无 ERR= 的调用点按错误终止语义传播。
        raise ValueError("unit %d: truncated unformatted record" % unit)
    fh.read(4)  # 记录尾部长度标记
    _chunk08_urec_pos.setdefault(unit, []).append(pos)
    return payload


def iniset():
    """SELECTION OF LINES THAT MAY CONTRIBUTE,
    SET UP AUXILIARY FIELDS CONTAINING LINE PARAMETERS,
    SET UP THE SET OF FREQUENCY POINTS

    对应 synspec54.f 行 8074–8427
    """
    global _save_iniset_illast, _save_iniset_aprev
    # DATA CNM,CAS /2.997925D17,2.997925D18/
    cnm = 2.997925e17
    cas = 2.997925e18
    # DATA C1,C2,C3 /2.3025851, 4.2014672, 1.4387886/（原代码已注释）
    # 局部变量显式初始化（Fortran 静态存储；带 TODO 的原代码可能先于赋值引用）
    alact = 0.0
    frmax = 0.0     # TODO(port): FRMAX 首次经过标号 130 前理论上未定义
    ext = 0.0
    spac = 0.0
    dista0 = 0.0
    distan = 0.0    # TODO(port): IMODE=2 直接 GO TO 105 时 DISTAN 未初始化
    alamcu = 0.0
    cutoff = 0.0    # TODO(port): ifwin>0 时在标号 20 循环内才赋值
    dopstd = 0.0
    istr = 0        # TODO(port): IMODE=2 跳过 8126-8139 的初始化（Fortran 静态残值）
    ijmax = 0
    imod1l = 0

    for i in range(1, MFRQ + 1):            # DO 10 I=1,MFRQ
        C.W[i] = 0.0
        C.IJCTR[i] = 0
    # 10 CONTINUE

    il0 = 0
    iprset = 0
    C.NLIN = 0
    ireadp = 1
    C.IRLIST = 0
    if C.IBLANK <= 1 or C.IMODE == 1 or C.IMODE == -1:
        ireadp = 0
    if C.IBLANK <= 1:
        _save_iniset_aprev = 0.0
    C.FRMIN = cnm / C.ALAM0
    frm = C.FRMIN
    if C.IFWIN <= 0:
        ij0 = 3
    else:
        ij0 = 1
    ij = ij0
    C.FREQ[ij0] = frm
    space = C.SPACE0
    if C.ALAMC > 0.0:
        space = C.SPACE0 * C.ALAM0 / C.ALAMC
    if C.SPACE0 < 0.0:
        space = -C.SPACE0
    if C.IMODE == 2:
        nfrp = C.NFREQS + 1
        w0 = space
        _label = 105                        # GO TO 105
    else:
        istr = 0
        ijmax = 0
        imod1l = 0
        if C.IFWIN <= 0:
            cutoff = C.CUTOF0
            dopstd = 1.0e7 / C.ALAM0 * C.DSTD
            distan = 0.15 * dopstd
            spac = 3.0e16 / C.ALAM0 / C.ALAM0 * space
            dista0 = 0.14 * spac
            astd = 1.0
            avab = C.ABSTD[C.IDSTD] * C.RELOP
        C.FRLI0 = C.FRMIN
        if C.IBLANK >= 2 and C.IMODE == -1:
            il0 = _save_iniset_illast
        _label = 20

    # GO TO 密集，按约定用 _label 状态机直译，保留原标号
    while True:
        # ---------------- 标号 20：取下一根谱线 ----------------
        if _label == 20:
            # set up indices of lines
            # IL0 - is the current index of line in the numbering of all lines
            if ireadp == 1:
                iprset = iprset + 1
                il0 = C.INDLIP[iprset]
                if C.FREQ0[il0] < C.FRMIN:
                    ireadp = 0
                    il0 = C.INDLIP[iprset - 1] + 1
            else:
                il0 = il0 + 1
            if il0 > C.NLIN0:
                _label = 210                # GO TO 210
                continue
            C.FRLIM = C.FRLI0
            fr0 = C.FREQ0[il0]
            alam = cnm / fr0
            if C.IFWIN > 0:
                if C.ALAMC > 0.0:
                    space = C.SPACE0 * alam / C.ALAMC
                if C.SPACE0 < 0.0:
                    space = -C.SPACE0
                cutoff = C.CUTOF0 * alam / C.ALAMC
                dopstd = 1.0e7 / alam * C.DSTD
                distan = 0.15 * dopstd
                spac = space
                if imod(C.IFREQ, 10) > 0:
                    spac = 3.0e16 / alam / alam * space
                dista0 = 0.14 * spac
            # set up a different starting wavelength for IMODE=1
            if not (C.IMODE != 1 or istr == 1 or ij != 3
                    or alam < C.ALAM0 + 2.0 * cutoff):
                C.ALAM0 = alam - cutoff + 0.0001
                C.FRMIN = cnm / C.ALAM0
                frm = C.FRMIN
                ij = ij0
                C.FREQ[ij0] = frm
            # 45 CONTINUE
            if alam < C.ALAM0 - cutoff:
                continue                    # GO TO 20
            if ij >= C.NFREQS + 1:
                if alam > C.ALAM1 + cutoff:
                    _label = 210            # GO TO 210
                    continue
            # SECOND SELECTION : FOR LINE STRENGHTS
            # 50 CONTINUE
            istr = 0
            if C.IMODE >= 1:
                istr = 1
            else:
                ext = C.EXTIN[il0]
                C.FRLI0 = fr0 - ext - spac
                if C.FRLI0 > C.FRLIM:
                    C.FRLI0 = C.FRLIM
                frmiv = C.FRMIN
                if C.IFWIN > 0:
                    frmiv = frmiv * (1.0 + C.VINF / 2.997925e10)
                if alam < C.ALAM0 and fr0 - frmiv > ext + spac:
                    continue                # GO TO 20
                istr = 1
                frmav = frmax
                if C.IFWIN > 0:
                    frmav = frmav * (1.0 - C.VINF / 2.997925e10)
                if ij >= C.NFREQS + 1 and frmav - fr0 > ext + spac:
                    continue                # GO TO 20
            C.NLIN = C.NLIN + 1
            if C.NLIN > MLIN:
                quit(' too many lines in a set')
            C.INDLIN[C.NLIN] = il0
            alamcu = alam + cutoff
            # FREQUENCY POINTS AND WEIGHTS
            if ij >= C.NFREQS + 1:
                continue                    # GO TO 20
            if fr0 > C.FRMIN:
                continue                    # GO TO 20
            _label = 100
            continue

        # ---------------- 标号 100：该谱线的频率点 ----------------
        if _label == 100:
            delt = abs(frm - fr0)
            if delt < dista0 and C.IMODE != 1:
                _label = 20                 # GO TO 20
                continue
            dfrel = cnm * (1.0 / fr0 - 1.0 / frm) / space
            nfrp = int(dfrel) + 1           # Fortran INT 截断
            if nfrp <= 2:
                nfrp = 2
            w0 = cnm * (1.0 / fr0 - 1.0 / frm) / nfrp
            frm = fr0
            _label = 105
            continue

        # ---------------- 标号 105 ----------------
        if _label == 105:
            fract = C.FREQ[ij]
            alact = cnm / fract
            _next = None
            for k in range(1, nfrp + 1):    # DO 110 K=1,NFRP
                fract = fract - w0
                alact = alact + w0
                if not (C.IMODE >= 1 or nfrp == 2):     # 否则 GO TO 107
                    if fract < C.FRLIM and fract > fr0 + ext + spac:
                        continue            # GO TO 110（继续循环）
                # 107
                ij = ij + 1
                if ij > C.NFREQS:
                    _next = 130             # GO TO 130
                    break
                C.FREQ[ij] = cnm / alact
                C.W[ij] = C.W[ij] + (C.FREQ[ij - 1] - C.FREQ[ij]) * 0.5
                C.W[ij - 1] = C.W[ij - 1] + (C.FREQ[ij - 1] - C.FREQ[ij]) * 0.5
                # IF(FREQ(IJ).LT.FRLAST) GO TO 220（原代码已注释）
                if C.IMODE == 1 and alact > alamcu:
                    _next = 140             # GO TO 140
                    break
            # 110 CONTINUE
            if _next is not None:
                _label = _next
                continue
            C.IJCTR[ij] = il0
            if imod1l == 1:
                _label = 210                # GO TO 210
                continue
            dista0 = distan
            _label = 20                     # GO TO 20
            continue

        # ---------------- 标号 130 ----------------
        if _label == 130:
            frmax = C.FREQ[C.NFREQS]
            C.ALAM1 = cnm / frmax
            C.NFREQ = C.NFREQS
            if C.IMODE == 2:
                _label = 210                # GO TO 210
                continue
            if imod1l == 1:
                _label = 210                # GO TO 210
                continue
            _label = 20                     # GO TO 20
            continue

        # ---------------- 标号 140 ----------------
        if _label == 140:
            ijmax = ij
            ijmax = min(ijmax, C.NFREQS)
            C.NFREQ = ijmax
            if il0 < C.NLIN0:
                C.NBLANK = C.IBLANK + 1
            else:
                C.NBLANK = C.IBLANK
            _label = 240                    # GO TO 240
            continue

        # ---------------- 标号 210 ----------------
        if _label == 210:
            C.NBLANK = C.IBLANK + 1
            if ij >= C.NFREQS + 1:
                _label = 230                # GO TO 230
                continue
            ijmax = ij
            ijmax = min(ijmax, C.NFREQS)
            C.NFREQ = ijmax
            if C.IMODE != 1:
                _label = 240                # GO TO 240
                continue
            if imod1l == 1:
                _label = 240                # GO TO 240
                continue
            # FR0=MAX(CNM/(ALAM+CUTOFF),FRLAST*0.99999999D0)（原代码已注释）
            fr0 = C.FRLAST * 0.99999999
            alam = cnm / fr0
            imod1l = 1
            _label = 100                    # GO TO 100
            continue

        # ---------------- 标号 230 ----------------
        if _label == 230:
            ijmax = C.NFREQS
            C.NFREQ = C.NFREQS
            _label = 240
            continue

        # ---------------- 标号 240：收尾 ----------------
        if _label == 240:
            if C.FREQ[ijmax] <= C.FRLAST:
                C.NBLANK = C.IBLANK
            if C.ALM00 > 0.0:
                if (C.FREQ[ijmax] >= 0.999999 * cnm / C.ALM00
                        and C.IBLANK > 1):
                    C.NBLANK = C.IBLANK
            # correction for molecular lines
            if C.NMLIST > 0 and C.IFMOL > 0:
                for ilist in range(1, C.NMLIST + 1):
                    if C.ALASTM[ilist] > 0.0 and C.ALASTM[ilist] <= alact:
                        C.NBLANK = C.IBLANK
                        C.IRLIST = 1
                        # write(*,*) 'iniset mol',ilist,alastm(ilist),alam
                        # （原代码已注释）
            if C.IFWIN <= 0:
                C.FREQ[1] = C.FREQ[3]
                C.FREQ[2] = C.FREQ[ijmax]
                C.W[1] = 0.5 * (C.FREQ[1] - C.FREQ[2])
                C.W[2] = C.W[1]
            # truncate the interval if the required end is reached
            ijmx = 2
            if C.IFWIN > 0:
                ijmx = ijmax
            if C.FREQ[ijmx] < C.FRLAST:
                C.FREQ[ijmx] = C.FRLAST
                if C.IFWIN <= 0:
                    C.W[1] = 0.5 * (C.FREQ[1] - C.FREQ[2])
                    C.W[2] = C.W[1]
                for ij in range(ij0, C.NFREQ + 1):  # DO 245 IJ=IJ0,NFREQ
                    if C.FREQ[ij] < C.FRLAST:
                        break               # GO TO 247
                    ijmax = ij
                # 245 CONTINUE
                # 247
                C.NFREQ = ijmax + 1
                C.FREQ[C.NFREQ] = C.FRLAST
                C.W[C.NFREQ] = 0.5 * (C.FREQ[C.NFREQ - 1] - C.FREQ[C.NFREQ])
                C.W[C.NFREQ - 1] = (C.W[C.NFREQ]
                                    + 0.5 * (C.FREQ[C.NFREQ - 2]
                                             - C.FREQ[C.NFREQ - 1]))
            # frequency interpolation coefficients
            if C.IMODE != -1:
                if C.IFWIN <= 0:
                    xx = C.FREQ[2] - C.FREQ[1]
                    for ij in range(1, C.NFREQ + 1):
                        C.WLAM[ij] = 2.997925e18 / C.FREQ[ij]
                        C.FRX1[ij] = (C.FREQ[ij] - C.FREQ[1]) / xx
                        C.FRX2[ij] = (C.FREQ[2] - C.FREQ[ij]) / xx
                else:
                    for ij in range(1, C.NFREQ + 1):
                        C.WLAM[ij] = cas / C.FREQ[ij]
                        C.FRQOBS[ij] = C.FREQ[ij]
                        C.WLOBS[ij] = C.WLAM[ij]
                        fr = C.FREQ[ij]
                        C.BNUE[ij] = BN * fr * fr * fr
                        for ijci in range(1, C.NFREQC):  # DO IJCI=1,NFREQC-1
                            if C.WLAM[ij] <= C.WLAMC[ijci]:
                                break       # GO TO 248
                        else:
                            # 循环正常结束：Fortran 循环变量保留为 终值+步长
                            ijci = C.NFREQC
                        # 248 CONTINUE
                        ijc = ijci
                        C.IJCINT[ij] = max(ijc - 1, 1)
                        ijci = C.IJCINT[ij]
                        C.FRX1[ij] = ((C.FREQ[ij] - C.FREQC[ijci + 1])
                                      / (C.FREQC[ijci] - C.FREQC[ijci + 1]))
                    C.NFROBS = C.NFREQ
                    xx = C.FREQ[C.NFREQ] - C.FREQ[1]
                # frequency indices of the line centers
                C.DFRCON = C.NFREQ - ij0
                C.DFRCON = -C.DFRCON / xx
                ifrcon = int(C.DFRCON)      # Fortran INT 截断
                for il in range(1, C.NLIN + 1):     # DO 255 IL=1,NLIN
                    fr0 = C.FREQ0[C.INDLIN[il]]
                    xjc = 3.0 + C.DFRCON * (C.FREQ[1] - fr0)
                    ijc = int(xjc)                  # Fortran INT 截断
                    C.IJCNTR[il] = ijc
                    if ijc <= ij0 or ijc >= C.NFREQ:
                        continue                    # GO TO 255
                    if fr0 < C.FREQ[ijc]:
                        ijc0 = ijc
                        dfr0 = C.FREQ[ijc0] - fr0
                        while True:                 # 标号 252
                            ijc0 = ijc0 + 1
                            dfr = abs(C.FREQ[ijc0] - fr0)
                            if dfr < dfr0:
                                ijc = ijc0
                                ijc0 = ijc0 + 1
                                dfr0 = dfr
                                # GO TO 252
                            else:
                                break
                    elif fr0 > C.FREQ[ijc]:
                        ijc0 = ijc
                        dfr0 = fr0 - C.FREQ[ijc0]
                        while True:                 # 标号 254
                            ijc0 = ijc0 - 1
                            dfr = abs(C.FREQ[ijc0] - fr0)
                            if dfr < dfr0:
                                ijc = ijc0
                                ijc0 = ijc0 - 1
                                dfr0 = dfr
                                # GO TO 254
                            else:
                                break
                    C.IJCNTR[il] = ijc
                # 255 CONTINUE
            if C.IFWIN > 0:
                # set up switches for hydrogen and He II line opacity
                for ij in range(1, C.NFREQ + 1):    # DO IJ=1,NFREQ
                    hylsew(ij)              # CALL HYLSEW(IJ)，不改标量哑元
                    he2sew(ij)              # CALL HE2SEW(IJ)，不改标量哑元
            nsp = 0
            for il in range(1, C.NLIN + 1):         # DO 260 IL=1,NLIN
                il0 = C.INDLIN[il]
                isp = C.ISPRF[il0]
                if isp > 5:
                    nsp = nsp + 1
                    C.ISP0[nsp] = isp
                C.INDLIP[il] = C.INDLIN[il]
            # 260 CONTINUE
            if C.IFWIN <= 0:
                _save_iniset_illast = C.INDLIN[C.NLIN]
            else:
                _save_iniset_illast = 0
                if C.NLIN > 0:
                    _save_iniset_illast = C.INDLIN[C.NLIN]
            readph()                        # CALL READPH
            if C.ALAM0 <= _save_iniset_aprev + 0.001:
                C.NBLANK = C.IBLANK
            _save_iniset_aprev = C.ALAM0
            C.ALAM0 = C.ALAM1
            C.ALM00 = cnm / C.FREQ[C.NFREQ]
            # write(6,611) iblank,nblank,irlist,aprev*10.,alam0*10.（原代码已注释）
            # 611  format('inis ',2i6,i3,3f10.3)（原代码已注释）
            return


def readph():
    """Auxiliary routine for LINSET - read table of detailed
    photoinization cross-section from unit IPHT1,
    and interpolate to the set of current wavelengths (WLAM)

    对应 synspec54.f 行 8432–8581
    """
    global _save_readph_numfil
    # PARAMETER (IPHT0=57)
    ipht0 = 57
    # SAVE IPHT,IEND,NELEM,INDEX,NUMFIL → 模块级 _save_readph_*
    # DIMENSION PHT0(MPHOT),PHT1(MPHOT),IPHT(MPHOT),IEND(MPHOT),
    #           IFILE(MPHOT),NELEM(MPHOT),INDEX(MPHOT,MPHOT)
    pht0 = np.zeros(MPHOT + 1)
    pht1 = np.zeros(MPHOT + 1)
    ifile = np.zeros(MPHOT + 1, dtype=np.int64)
    indx = 0

    def _read_vals(unit, n):
        # 列表定向 READ：连续读行直到凑足 n 个值（Fortran 允许一个 READ 跨行，
        # 读满后本记录剩余部分被跳过）
        vals = []
        while len(vals) < n:
            vals.extend(read_line(unit).replace(',', ' ').split())
        return vals[:n]

    # initialization - read basic information about files where the
    #                  cross-sections are stored,
    #                  and basic parameters for starting levels
    if C.IBLANK <= 1:
        C.NPHT = 0
        ipht1 = 0
        _save_readph_numfil = 0
        for ij in range(1, MFRQ + 1):       # DO 10 IJ=1,MFRQ
            for i in range(1, MPHOT + 1):   # DO 10 I=1,MPHOT
                C.PHOT[ij, i] = 0.0
        # 10 CONTINUE
        try:
            # READ(IPHT0,*,END=50,err=50) NPHT
            C.NPHT = int(float(read_line(ipht0).replace(',', ' ').split()[0]))
        except (EOFError, ValueError, IndexError):
            pass                            # END=50 / err=50 → 标号 50
        else:
            if C.NPHT <= 0:
                return
            npht1 = C.NPHT
            try:
                _v = _read_vals(ipht0, C.NPHT)  # READ ... (IPHT(I),I=1,NPHT)
                for i in range(1, C.NPHT + 1):
                    _save_readph_ipht[i] = int(float(_v[i - 1]))
                _v = _read_vals(ipht0, C.NPHT)  # (APHT(I),I=1,NPHT)
                for i in range(1, C.NPHT + 1):
                    C.APHT[i] = float(_v[i - 1])
                _v = _read_vals(ipht0, C.NPHT)  # (EPHT(I),I=1,NPHT)
                for i in range(1, C.NPHT + 1):
                    C.EPHT[i] = float(_v[i - 1])
                _v = _read_vals(ipht0, C.NPHT)  # (GPHT(I),I=1,NPHT)
                for i in range(1, C.NPHT + 1):
                    C.GPHT[i] = float(_v[i - 1])
                _v = _read_vals(ipht0, C.NPHT)  # (JPHT(I),I=1,NPHT)
                for i in range(1, C.NPHT + 1):
                    C.JPHT[i] = int(float(_v[i - 1]))  # JPHT 为 INTEGER 数组
            except EOFError:
                pass                        # END=50 → 标号 50
            else:
                # determination of the number of files (NFILE) and the
                # partitioning of the individual cross-section to the
                # corresponding files
                _save_readph_numfil = 1
                ifile[1] = 1
                _save_readph_nelem[1] = 1
                _save_readph_index[1, 1] = 1
                if C.NPHT > 1:
                    for i in range(2, C.NPHT + 1):      # DO 30 I=2,NPHT
                        _found = False
                        for j in range(1, i):           # DO 20 J=1,I-1
                            if _save_readph_ipht[i] == _save_readph_ipht[j]:
                                ifile[i] = ifile[j]
                                _save_readph_nelem[ifile[i]] += 1
                                _save_readph_index[ifile[i],
                                                   _save_readph_nelem[ifile[i]]] = i
                                _found = True
                                break           # GO TO 30
                        # 20 CONTINUE
                        if _found:
                            continue
                        _save_readph_numfil = _save_readph_numfil + 1
                        ifile[i] = _save_readph_numfil
                        _save_readph_nelem[_save_readph_numfil] = 1
                        _save_readph_index[_save_readph_numfil, 1] = i
                    # 30 CONTINUE
                for ifil in range(1, _save_readph_numfil + 1):  # DO 40
                    _save_readph_iend[ifil] = 0
                # 40 CONTINUE
    # 50
    if _save_readph_numfil <= 0:
        return

    # loop over individual files containing the photoionization data
    for ifil in range(1, _save_readph_numfil + 1):  # DO 300 IFIL=1,NUMFIL
        if _save_readph_iend[ifil] == 2:
            continue                        # GO TO 300
        _to200 = (_save_readph_iend[ifil] == 1)     # GO TO 200
        if not _to200:
            npht1 = _save_readph_nelem[ifil]
            ipht1 = _save_readph_ipht[_save_readph_index[ifil, 1]]
            try:
                if C.IBLANK <= 1:
                    while True:             # 110
                        # READ(IPHT1,*,END=200) WPHT1,(PHT1(I),I=1,NPHT1)
                        _v = _read_vals(ipht1, 1 + npht1)
                        C.WPHT1 = float(_v[0])
                        for i in range(1, npht1 + 1):
                            pht1[i] = float(_v[i])
                        if C.WPHT1 >= C.WLAM[1]:
                            break
                        # GO TO 110
                    _chunk08_backspace(ipht1)       # BACKSPACE(IPHT1)
                    _chunk08_backspace(ipht1)       # BACKSPACE(IPHT1)
                    # READ(IPHT1,*,END=200) WPHT0,(PHT0(I),I=1,NPHT1)
                    _v = _read_vals(ipht1, 1 + npht1)
                    C.WPHT0 = float(_v[0])
                    for i in range(1, npht1 + 1):
                        pht0[i] = float(_v[i])
                else:
                    _chunk08_backspace(ipht1)       # BACKSPACE(IPHT1)
                    _chunk08_backspace(ipht1)       # BACKSPACE(IPHT1)
                    # READ(IPHT1,*,END=200) WPHT0,(PHT0(I),I=1,NPHT1)
                    _v = _read_vals(ipht1, 1 + npht1)
                    C.WPHT0 = float(_v[0])
                    for i in range(1, npht1 + 1):
                        pht0[i] = float(_v[i])
                    # READ(IPHT1,*,END=200) WPHT1,(PHT1(I),I=1,NPHT1)
                    _v = _read_vals(ipht1, 1 + npht1)
                    C.WPHT1 = float(_v[0])
                    for i in range(1, npht1 + 1):
                        pht1[i] = float(_v[i])
            except EOFError:
                _to200 = True               # END=200 → 标号 200
        if not _to200:
            dw = C.WPHT1 - C.WPHT0
            a1 = (C.WPHT1 - C.WLAM[3]) / dw
            a2 = (C.WLAM[3] - C.WPHT0) / dw
            for i in range(1, npht1 + 1):   # DO 130 I=1,NPHT1
                indx = _save_readph_index[ifil, i]
                C.PHOT[1, indx] = 0.0
                C.PHOT[2, indx] = 0.0
                C.PHOT[3, indx] = (a1 * pht0[i] + a2 * pht1[i]) * 1.0e-18
                for ij in range(4, MFRQ + 1):       # DO 130 IJ=4,MFRQ
                    C.PHOT[ij, indx] = 0.0
            # 130 CONTINUE
            for ij in range(4, MFRQ + 1):   # DO 190 IJ=4,MFRQ
                if C.WLAM[ij] <= C.WPHT1:
                    a1 = (C.WPHT1 - C.WLAM[ij]) / dw
                    a2 = (C.WLAM[ij] - C.WPHT0) / dw
                    for i in range(1, npht1 + 1):   # DO 140 I=1,NPHT1
                        indx = _save_readph_index[ifil, i]
                        C.PHOT[ij, indx] = (a1 * pht0[i] + a2 * pht1[i]) * 1.0e-18
                    # 140 CONTINUE
                else:
                    C.WPHT0 = C.WPHT1
                    for i in range(1, npht1 + 1):   # DO 150 I=1,NPHT1
                        pht0[i] = pht1[i]
                    # 150
                    ifsml = 0
                    _eof = False
                    while True:             # 160
                        try:
                            # READ(IPHT1,*,END=180) WPHT1,(PHT1(I),I=1,NPHT1)
                            _v = _read_vals(ipht1, 1 + npht1)
                        except EOFError:
                            _eof = True     # END=180
                            break
                        C.WPHT1 = float(_v[0])
                        for i in range(1, npht1 + 1):
                            pht1[i] = float(_v[i])
                        if C.WPHT1 < C.WLAM[ij]:
                            ifsml = 1
                            continue        # GO TO 160
                        break
                    if not _eof and ifsml == 1:
                        _chunk08_backspace(ipht1)   # BACKSPACE(IPHT1)
                        _chunk08_backspace(ipht1)   # BACKSPACE(IPHT1)
                        try:
                            # READ(IPHT1,*,END=180) WPHT0,(PHT0(I),I=1,NPHT1)
                            _v = _read_vals(ipht1, 1 + npht1)
                            C.WPHT0 = float(_v[0])
                            for i in range(1, npht1 + 1):
                                pht0[i] = float(_v[i])
                            # READ(IPHT1,*,END=180) WPHT1,(PHT1(I),I=1,NPHT1)
                            _v = _read_vals(ipht1, 1 + npht1)
                            C.WPHT1 = float(_v[0])
                            for i in range(1, npht1 + 1):
                                pht1[i] = float(_v[i])
                        except EOFError:
                            _eof = True     # END=180
                    if _eof:
                        # 180
                        _save_readph_iend[ifil] = 1
                        for i in range(1, npht1 + 1):       # DO 185 I=1,NPHT1
                            indx = _save_readph_index[ifil, i]
                            C.PHOT[ij, indx] = 0.0
                        # 185 CONTINUE
                    else:
                        dw = C.WPHT1 - C.WPHT0
                        a1 = (C.WPHT1 - C.WLAM[ij]) / dw
                        a2 = (C.WLAM[ij] - C.WPHT0) / dw
                        for i in range(1, npht1 + 1):       # DO 170 I=1,NPHT1
                            indx = _save_readph_index[ifil, i]
                            C.PHOT[ij, indx] = (a1 * pht0[i]
                                                + a2 * pht1[i]) * 1.0e-18
                        # 170 CONTINUE
                # GO TO 190
            # 190 CONTINUE
            C.PHOT[1, indx] = C.PHOT[3, indx]
            C.PHOT[2, indx] = C.PHOT[MFRQ, indx]
            # GO TO 300
        if _to200:
            # 200
            _save_readph_iend[ifil] = 2
            for ij in range(1, MFREQ + 1):          # DO 210 IJ=1,MFREQ
                for i in range(1, _save_readph_nelem[ifil] + 1):  # DO 210 I=...
                    indx = _save_readph_index[ifil, i]
                    C.PHOT[ij, indx] = 0.0
            # 210 CONTINUE
        # 300 CONTINUE
    return


def inilin():
    """read in the input line list,
    selection of lines that may contribute,
    set up auxiliary fields containing line parameters,

    Input of line data - unit 19:

    For each line, one (or two) records, containing:

   ALAM    - wavelength (in nm)
   ANUM    - code of the element and ion (as in Kurucz-Peytremann)
             (eg. 2.00 = HeI; 26.00 = FeI; 26.01 = FeII; 6.03 = C IV)
   GF      - log gf
   EXCL    - excitation potential of the lower level (in cm*-1)
   QL      - the J quantum number of the lower level
   EXCU    - excitation potential of the upper level (in cm*-1)
   QU      - the J quantum number of the upper level
   AGAM    = 0. - radiation damping taken classical
           > 0. - the value of Gamma(rad)

    There are now two possibilities, called NEW and OLD, of the next
    parameters:
    a) NEW, next parameters are:
   GS      = 0. - Stark broadening taken classical
           > 0. - value of log gamma(Stark)
   GW      = 0. - Van der Waals broadening taken classical
           > 0. - value of log gamma(VdW)
   INEXT   = 0  - no other record necessary for a given line
           > 0  - a second record is present, see below

   The following parameters may or may not be present,
   in the same line, next to INEXT:
   ISQL   >= 0  - value for the spin quantum number (2S+1) of lower level
           < 0  - value for the spin number of the lower level unknown
   ILQL   >= 0  - value for the L quantum number of lower level
           < 0  - value for L of the lower level unknown
   IPQL   >= 0  - value for the parity of lower level
           < 0  - value for the parity of the lower level unknown
   ISQU   >= 0  - value for the spin quantum number (2S+1) of upper level
           < 0  - value for the spin number of the upper level unknown
   ILQU   >= 0  - value for the L quantum number of upper level
           < 0  - value for L of the upper level unknown
   IPQU   >= 0  - value for the parity of upper level
           < 0  - value for the parity of the upper level unknown
   (by default, the program finds out whether these quantum numbers
    are included, but the user can force the program to ignore them
    if present by setting INLIST=10 or larger

   If INEXT was set to >0 then the following record includes:
   WGR1,WGR2,WGR3,WGR4 - Stark broadening values from Griem (in Angst)
                  for T=5000,10000,20000,40000 K, respectively;
                  and n(el)=1e16 for neutrals, =1e17 for ions.
   ILWN    = 0  - line taken in LTE (default)
           > 0  - line taken in NLTE, ILWN is then index of the
                  lower level
           =-1  - line taken in approx. NLTE, with Doppler K2 function
           =-2  - line taken in approx. NLTE, with Lorentz K2 function
   IUN     = 0  - population of the upper level in LTE (default)
           > 0  - index of the lower level
   IPRF    = 0  - Stark broadening determined by GS
           < 0  - Stark broadening determined by WGR1 - WGR4
           > 0  - index for a special evaluation of the Stark
                  broadening (in the present version inly for He I -
                  see procedure GAMHE)
     b) OLD, next parameters are
    IPRF,ILWN,IUN - the same meaning as above
    next record with WGR1-WGR4 - again the same meaning as above
    (this record is automatically read if IPRF<0

    The only differences between NEW and OLD is the occurence of
    GS and GW in NEW, and slightly different format of reading.

    对应 synspec54.f 行 8586–9192
    """
    global _save_inilin_inlset
    # PARAMETER 局部常量
    c1 = 2.3025851
    c2 = 4.2014672
    c3 = 1.4387886
    cnm = 2.997925e17
    anumin = 1.9
    anumax = 99.31
    ahe2 = 2.01
    ext0 = 3.17
    un = 1.0
    ten = 10.0
    hund = 1.0e2
    tenm4 = 1.0e-4
    tenm8 = 1.0e-8
    op4 = 0.4
    agr0 = 2.4734e-22
    xeh = 13.595
    xet = 8067.6
    xnf = 25.0
    r02 = 2.5
    r12 = 45.0
    vw0 = 4.5e-9
    enhe1 = 198310.76
    enhe2 = 438908.85
    # CHARACTER*1000 CADENA
    # DATA INLSET /0/ → 模块级 _save_inilin_inlset（随后被修改，隐含 SAVE）
    wgr1 = 0.0
    wgr2 = 0.0
    wgr3 = 0.0
    wgr4 = 0.0
    ab0 = 0.0
    # TODO(port): 量子数标志在读表前未定义时 Fortran 取静态残值，这里取 -1
    # （按 INILIN 头注释 -1 表示 unknown）
    isql = -1
    ilql = -1
    ipql = -1
    isqu = -1
    ilqu = -1
    ipqu = -1
    ilsearch = 0
    ilfound = 0
    ilfail = 0
    ilmult = 0
    ilmatch = 0

    if C.IBIN[0] == 0:
        # open(unit=19,file=amlist(0),status='old')
        open_unit(19, C.AMLIST[0].strip(), 'r')
    else:
        # open(unit=19,file=amlist(0),form='unformatted',status='old')
        open_unit(19, C.AMLIST[0].strip(), 'rb')
        _chunk08_urec_pos.pop(19, None)
    if C.IMODE < -2:
        inilin_grid()
        return

    if C.NDSTEP == 0:
        # 621 format(/' lines are rejected based on opacities at the',
        # ' standard depth:'/' ID =',i4,'  T = ',f10.1,',   DENS = ',1pe10.3/)
        print("\n lines are rejected based on opacities at the standard depth:\n"
              " ID =%4d  T = %10.1f,   DENS = %10.3e\n"
              % (C.IDSTD, C.TEMP[C.IDSTD], C.DENS[C.IDSTD]))
    else:
        # 622 format(/' lines are rejected based on opacities at depths:'/)
        print("\n lines are rejected based on opacities at depths:\n")
        for id_ in range(1, C.ND + 1, C.NDSTEP):
            # 623 format(' ID =',i4,'  T = ',f10.1,',   DENS = ',1pe10.3/)
            print(" ID =%4d  T = %10.1f,   DENS = %10.3e"
                  % (id_, C.TEMP[id_], C.DENS[id_]))

    il = 0
    innlt0 = 0
    igrie0 = 0
    if C.NXTSET == 1:
        C.ALAM0 = C.ALM00
        alast = C.ALST00
        C.FRLAST = cnm / alast
        C.NXTSET = 0
        rewind_unit(19)                     # REWIND 19
        _chunk08_urec_pos.pop(19, None)
    alam00 = C.ALAM0
    alast = cnm / C.FRLAST
    alast0 = alast
    dopstd = 1.0e7 / C.ALAM0 * C.DSTD
    doplam = C.ALAM0 * C.ALAM0 / cnm * dopstd
    avab = C.ABSTD[C.IDSTD] * C.RELOP
    astd = 1.0
    # IF(GRAV.GT.6.) ASTD=0.1（原代码已注释）
    cutoff = C.CUTOF0
    alast = cnm / C.FRLAST
    iat = 0     # TODO(port): 下方 afac 计算引用 IAT，此处先于赋值（Fortran 静态残值）
    ion = 0
    if C.INLTE >= 1 and _save_inilin_inlset == 0:
        # CALL NLTSET(0,...)：NLTSET 会改写 ILMATCH、INNLT0 等标量哑元，
        # 按约定返回全部标量哑元并逐个接收
        # TODO(port): 初始化调用时 EXCL..IPQU 等实参在原代码中未定义
        (_mode, il, iat, ion, C.ALAM0, excl, excu, ql, qu,
         isql, ilql, ipql, isqu, ilqu, ipqu, ieven, innlt0,
         ilmatch) = nltset(0, il, iat, ion, C.ALAM0, 0.0, 0.0, 0.0, 0.0,
                           0, 0, 0, 0, 0, 0, 0, innlt0, 0)
        _save_inilin_inlset = 1
        ilmatch = 0
        ilsearch = 0
        ilfound = 0
        ilfail = 0
        ilmult = 0

    # Check whether any ion needs to compare quantum number limits
    maxilimits = 0
    for i in range(1, C.NION + 1):
        if C.ILIMITS[i] == 1:
            maxilimits = 1
    if maxilimits == 0 and C.INLIST > 0:
        C.INLIST = 20

    # If INLIST=0 or 10, the program checks for the number of words
    # present in the first line of the file to determine if quantum
    # numbers are included. If  INLINST=11, they will be ignored anyway
    iadqn = 0
    if C.IBIN[0] == 0:
        cadena = ' '
        cadena = read_line(19)              # READ(19,'(1000a)')CADENA
        _chunk08_backspace(19)              # BACKSPACE(19)
        # CALL COUNT_WORDS(CADENA,NOW)：COUNT_WORDS 给 N 赋值 → 返回全部标量哑元
        cadena, now = count_words(cadena, 0)
        if now < 12:
            write_line(11, 'INILIN: NO quantum numbers given in linelist')
        else:
            iadqn = 1
        if C.INLIST >= 10:
            write_line(11, 'INILIN: if present, quant. num. limits are ignored')
    else:
        # 二进制线列表：试探性读取（read(19,err=4) ...）
        # TODO(port): 无格式记录布局假定与 linelist/list2bin.f 一致：
        # 10 个 REAL*8 后跟 1 或 7 个 INTEGER*4；记录太短视为 err=4。
        # 该 READ 无 END=：Fortran 中 EOF 也属错误条件 → 同样走 err=4 分支，
        # 故此处同时捕获 EOFError
        try:
            _payload = _chunk08_read_urec(19)
            if len(_payload) < 10 * 8 + 7 * 4:
                raise ValueError("record too short")    # → err=4
            _r = np.frombuffer(_payload[:80], dtype=np.float64)
            _ii = np.frombuffer(_payload[80:80 + 28], dtype=np.int32)
            alam = float(_r[0])
            anum = float(_r[1])
            gf = float(_r[2])
            excl = float(_r[3])
            ql = float(_r[4])
            excu = float(_r[5])
            qu = float(_r[6])
            agam = float(_r[7])
            gs = float(_r[8])
            gw = float(_r[9])
            inext = int(_ii[0])
            isql = int(_ii[1])
            ilql = int(_ii[2])
            ipql = int(_ii[3])
            isqu = int(_ii[4])
            ilqu = int(_ii[5])
            ipqu = int(_ii[6])
            # BACKSPACE(19)（原代码已注释 —— 成功试探后不回退，首条记录被跳过）
            iadqn = 1
            # GO TO 5
        except (ValueError, EOFError):
            # 4 CONTINUE
            _chunk08_backspace(19)          # backspace(19)
            # read(19) ALAM,ANUM,GF,EXCL,QL,EXCU,QU,AGAM,GS,GW,INEXT
            # （无 ERR=/END=：此读再失败对应 Fortran 报错终止，异常向上传播）
            _payload = _chunk08_read_urec(19)
            _r = np.frombuffer(_payload[:80], dtype=np.float64)
            alam = float(_r[0])
            anum = float(_r[1])
            gf = float(_r[2])
            excl = float(_r[3])
            ql = float(_r[4])
            excu = float(_r[5])
            qu = float(_r[6])
            agam = float(_r[7])
            gs = float(_r[8])
            gw = float(_r[9])
            inext = int(np.frombuffer(_payload[80:84], dtype=np.int32)[0])
            _chunk08_backspace(19)          # backspace(19)
        # 5 CONTINUE
        if iadqn == 0:
            write_line(11, 'INILIN: no quantum numbers in binary linelist')
        if C.INLIST >= 10:
            write_line(11, 'INILIN: if present, quant. num. limits are ignored')

    rstd = 1.0e4
    if C.RELOP > 0.0:
        rstd = 1.0 / C.RELOP
    afac = 10.0
    if iat > 15 and iat != 26:
        afac = 1.0
    afac = afac * rstd * astd

    # first part of reading line list - read only lambda, and
    # skip all lines with wavelength below ALAM0-CUTOFF
    alam = 0.0
    ijc = 2
    while True:                             # 标号 7
        if C.IBIN[0] == 0:
            # READ(19,510) ALAM
            # 510 FORMAT(F10.4)
            alam = float(read_line(19)[:10])
        else:
            # read(19) alam（无格式：整条记录读出，只取第一量）
            _payload = _chunk08_read_urec(19)
            alam = float(np.frombuffer(_payload[:8], dtype=np.float64)[0])
        if alam >= C.ALAM0 - cutoff:
            break
        # GO TO 7
    _chunk08_backspace(19)                  # BACKSPACE(19)
    # GO TO 10

    # read the line list
    while True:                             # 标号 10：主循环
        # 8 CONTINUE（err=8 重新进入点，直接落入 10）
        ilwn = 0
        iun = 0
        iprf = 0
        gs = 0.0
        gw = 0.0
        if C.IBIN[0] == 0:
            if iadqn == 0:
                try:
                    # READ(19,*,END=100,err=8) ALAM,...,GS,GW,INEXT
                    _tok = read_line(19).replace(',', ' ').split()
                    alam = float(_tok[0])
                    anum = float(_tok[1])
                    gf = float(_tok[2])
                    excl = float(_tok[3])
                    ql = float(_tok[4])
                    excu = float(_tok[5])
                    qu = float(_tok[6])
                    agam = float(_tok[7])
                    gs = float(_tok[8])
                    gw = float(_tok[9])
                    inext = int(float(_tok[10]))
                except EOFError:
                    break                   # END=100 → 标号 100
                except (ValueError, IndexError):
                    continue                # err=8 → 标号 8
                if inext != 0:
                    # READ(19,*) WGR1,WGR2,WGR3,WGR4,ILWN,IUN,IPRF
                    _tok = read_line(19).replace(',', ' ').split()
                    wgr1 = float(_tok[0])
                    wgr2 = float(_tok[1])
                    wgr3 = float(_tok[2])
                    wgr4 = float(_tok[3])
                    ilwn = int(float(_tok[4]))
                    iun = int(float(_tok[5]))
                    iprf = int(float(_tok[6]))
            else:
                try:
                    # READ(19,*,END=100,err=8) ALAM,...,INEXT,ISQL,...,IPQU
                    _tok = read_line(19).replace(',', ' ').split()
                    alam = float(_tok[0])
                    anum = float(_tok[1])
                    gf = float(_tok[2])
                    excl = float(_tok[3])
                    ql = float(_tok[4])
                    excu = float(_tok[5])
                    qu = float(_tok[6])
                    agam = float(_tok[7])
                    gs = float(_tok[8])
                    gw = float(_tok[9])
                    inext = int(float(_tok[10]))
                    isql = int(float(_tok[11]))
                    ilql = int(float(_tok[12]))
                    ipql = int(float(_tok[13]))
                    isqu = int(float(_tok[14]))
                    ilqu = int(float(_tok[15]))
                    ipqu = int(float(_tok[16]))
                except EOFError:
                    break                   # END=100
                except (ValueError, IndexError):
                    continue                # err=8
        else:
            # 二进制（无格式）读
            try:
                _payload = _chunk08_read_urec(19)
            except EOFError:
                break                       # END=100
            _r = np.frombuffer(_payload[:80], dtype=np.float64)
            alam = float(_r[0])
            anum = float(_r[1])
            gf = float(_r[2])
            excl = float(_r[3])
            ql = float(_r[4])
            excu = float(_r[5])
            qu = float(_r[6])
            agam = float(_r[7])
            gs = float(_r[8])
            gw = float(_r[9])
            if iadqn != 0:
                # ...,INEXT,ISQL,ILQL,IPQL,ISQU,ILQU,IPQU
                _ii = np.frombuffer(_payload[80:80 + 28], dtype=np.int32)
                inext = int(_ii[0])
                isql = int(_ii[1])
                ilql = int(_ii[2])
                ipql = int(_ii[3])
                isqu = int(_ii[4])
                ilqu = int(_ii[5])
                ipqu = int(_ii[6])
        if C.INLIST >= 10:
            if C.ISPICK == 0:
                isql = -1
                isqu = -1
            if C.ILPICK == 0:
                ilql = -1
                ilqu = -1
            if C.IPPICK == 0:
                ipql = -1
                ipqu = -1
            if inext != 0:
                # READ(19,*) WGR1,WGR2,WGR3,WGR4,ILWN,IUN,IPRF
                # TODO(port): 原代码在 IADQN=0 时可能重复读此记录，直译保留
                _tok = read_line(19).replace(',', ' ').split()
                wgr1 = float(_tok[0])
                wgr2 = float(_tok[1])
                wgr3 = float(_tok[2])
                wgr4 = float(_tok[3])
                ilwn = int(float(_tok[4]))
                iun = int(float(_tok[5]))
                iprf = int(float(_tok[6]))

        # change wavelength to vacuum for lambda > 2000
        if alam > 200.0 and C.vaclim > 2000.0:
            wl0 = alam * 10.0
            alm = 1.0e8 / (wl0 * wl0)
            xn1 = 64.328 + 29498.1 / (146.0 - alm) + 255.4 / (41.0 - alm)
            wl0 = wl0 * (xn1 * 1.0e-6 + un)
            alam = wl0 * 0.1

        # first selection : for a given interval a atomic number
        if alam > alast + cutoff:
            break                           # GO TO 100
        if anum < anumin or anum > anumax:
            continue                        # GO TO 10
        if abs(anum - ahe2) < tenm4 and C.IFHE2 > 0:
            continue                        # GO TO 10

        # second selection : for line strenghts
        fr0 = cnm / alam
        iat = int(anum)                     # INT 截断
        fra = (anum - float(iat) + tenm4) * hund
        ion = int(fra) + 1
        if ion > C.IONIZ[iat]:
            continue                        # GO TO 10
        ieven = 1
        excl = abs(excl)
        excu = abs(excu)
        if excl > excu:
            fra = excl
            excl = excu
            excu = fra
            fra = ql
            ql = qu
            qu = fra
            ieven = 0
            if C.INLIST >= 10:
                ifra = isql
                isql = isqu
                isqu = ifra
                ifra = ilql
                ilql = ilqu
                ilqu = ifra
                ifra = ipql
                ipql = ipqu
                ipqu = ifra
        gfp = c1 * gf - c2
        epp = c3 * excl

        if C.NDSTEP == 0 and C.IFWIN == 0:
            # old procedure for rejecting lines
            gx = gfp - epp / C.TSTD
            ab0 = 0.0
            if gx > -30:
                ab0 = (math.exp(gfp - epp / C.TSTD)
                       * C.RRR[C.IDSTD, ion, iat] / dopstd / avab)
            if ab0 < un:
                continue                    # GO TO 10
        else:
            # new procedure for rejecting lines
            dopstd = 1.0e7 / alam * C.DSTD
            doplam = alam * alam / cnm * dopstd
            for ijcn in range(ijc, C.NFREQC + 1):   # do ijcn=ijc,nfreqc
                if fr0 >= C.FREQC[ijcn]:
                    break                   # GO TO 12
            else:
                # 循环正常结束：Fortran 循环变量保留为 终值+步长
                ijcn = C.NFREQC + 1
            # 12 CONTINUE
            ijc = ijcn
            if ijc > C.NFREQC:
                ijc = C.NFREQC
            tkm = 1.65e8 / C.AMAS[iat]
            dp0 = 3.33564e-11 * fr0
            _keep = False
            for id_ in range(1, C.ND + 1, C.NDSTEP):  # do id=1,nd,ndstep
                td = C.TEMP[id_]
                gx = gfp - epp / td
                ab0 = 0.0
                if gx > -30:
                    dops = dp0 * math.sqrt(tkm / td + C.VTURB[id_])
                    ab0 = (math.exp(gx) * C.RRR[id_, ion, iat]
                           / (dops * C.ABSTDW[ijc, id_] * C.RELOP))
                if ab0 >= un:
                    _keep = True
                    break                   # GO TO 15
            if not _keep:
                continue                    # GO TO 10

        # 15 CONTINUE
        # truncate line list if there are more lines than maximum allowable
        # (given by MLIN0 - see include file LINDAT.FOR)
        il = il + 1
        if il > MLIN0:
            # 601 FORMAT(' **** MORE LINES THAN MLIN0, LINE LIST TRUNCATED '/
            # '       AT LAMBDA',F15.4,'  NM'/)
            print(" **** MORE LINES THAN MLIN0, LINE LIST TRUNCATED \n"
                  "       AT LAMBDA%15.4f  NM\n" % alam)
            il = MLIN0
            alast = cnm / C.FREQ0[il] - cutoff
            C.FRLAST = cnm / alast
            C.NXTSET = 1
            break                           # GO TO 100

        # =============================================
        # line is selected, set up necessary parameters
        # =============================================
        # store parameters for selected lines
        C.FREQ0[il] = fr0
        C.EXCL0[il] = float(epp)            # real(EPP)
        C.EXCU0[il] = float(excu * c3)      # real(EXCU*C3)
        C.GF0[il] = float(gfp)              # real(GFP)
        C.INDAT[il] = 100 * iat + ion

        # indices for corresponding excitation temperatures of the lower
        # and upper levels
        # (for winds)
        if C.IFWIN > 0:
            C.IJCONT[il] = ijc
            if excl >= enhe2:
                C.IPOTL[il] = 3
            elif excl >= enhe1:
                C.IPOTL[il] = 2
            else:
                C.IPOTL[il] = 1

        # ****** line broadening parameters *****
        # 1) natural broadening
        if agam > 0.0:
            C.GAMR0[il] = float(math.exp(c1 * agam))    # real(EXP(C1*AGAM))
        else:
            C.GAMR0[il] = float(agr0 * fr0 * fr0)       # real(AGR0*FR0*FR0)

        # if Stark or Van der Waals broadenig assumed classical,
        # evaluate the effective quantum number
        if gs == 0.0 or gw == 0.0:
            z = float(ion)
            xneff2 = z ** 2 * (xeh / (C.ENEV[iat, ion] - excu / xet))
            if xneff2 <= 0.0 or xneff2 > xnf:
                xneff2 = xnf

        # 2) Stark broadening
        if gs != 0.0:
            C.GS0[il] = float(math.exp(c1 * gs))
        else:
            C.GS0[il] = float(tenm8 * xneff2 * xneff2 * math.sqrt(xneff2))

        # 3) Van der Waals broadening
        if gw != 0.0:
            C.GW0[il] = float(math.exp(c1 * gw))
        else:
            if iat < 21:
                r2 = r02 * (xneff2 / z) ** 2
            elif iat < 45:
                r2 = (r12 - float(iat)) / z
            else:
                r2 = 0.5
            C.GW0[il] = float(vw0 * r2 ** op4)

        # evaluation of EXTIN0 - the distance (in delta frequency) where
        # the line is supposed to contribute to the total opacity
        # CALL PROFIL(IL,IAT,IDSTD,AGAM)：PROFIL 改写 AGAM → 返回全部标量哑元
        il, iat, C.IDSTD, agam = profil(il, iat, C.IDSTD, agam)
        if iat <= 2:
            ext = math.sqrt(10.0 * ab0)
        elif iat <= 14:
            ex0 = ab0 * astd * 10.0
            ext = ext0
            if ex0 > ten:
                ext = math.sqrt(ex0)
        else:
            ex0 = ab0 * astd
            ext = ext0
            if ex0 > ten:
                ext = math.sqrt(ex0)
        extin0 = ext * dopstd
        C.EXTIN[il] = float(extin0)

        # 4) parameters for a special profile evaluation:
        # a) special He I and He II line broadening parameters
        isprff = 0
        if iat <= 2:
            isprff = ispec(iat, ion, alam)  # FUNCTION ISPEC
        if iat == 2:
            # CALL HESET(...)：HESET 改写 IPRF0、ILWN、IUPN → 返回全部标量哑元
            il, alam, excl, excu, ion, iprf, ilwn, iun = heset(
                il, alam, excl, excu, ion, iprf, ilwn, iun)
        C.ISPRF[il] = isprff
        C.IPRF0[il] = iprf

        # b) parameters for Griem values of Stark broadening
        if iprf < 0:
            igrie0 = igrie0 + 1
            C.IGRIEM[il] = igrie0
            if igrie0 > MGRIEM:
                # 603 FORMAT(' **** MORE LINES WITH GRIEM PROFILES THAN MGRIEM'/
                # '       FOR LINES WITH LAMBDA GREATER THAN',F15.4,'  NM'/)
                print(" **** MORE LINES WITH GRIEM PROFILES THAN MGRIEM\n"
                      "       FOR LINES WITH LAMBDA GREATER THAN%15.4f  NM\n"
                      % alam)
                # GO TO 20（跳过 WGR0 存储）
            else:
                C.WGR0[1, igrie0] = float(wgr1)
                C.WGR0[2, igrie0] = float(wgr2)
                C.WGR0[3, igrie0] = float(wgr3)
                C.WGR0[4, igrie0] = float(wgr4)
        # 20 CONTINUE

        # implied NLTE option
        if C.INLTE == -2 or C.INLTE == 12:
            if iat <= 20 and excl <= 1000.0:
                qu = -abs(qu)
        elif C.INLTE == -3:
            if excl <= 1000.0:
                qu = -abs(qu)
        elif C.INLTE == -4:
            qu = -abs(qu)

        # NLTE lines initialization
        C.INDNLT[il] = 0
        if qu < 0.0 or ql < 0.0:
            ilwn = -1
            qu = abs(qu)
            ql = abs(ql)
        if ilwn < 0 and C.INLTE != 0:
            innlt0 = innlt0 + 1
            C.INDNLT[il] = innlt0
            if innlt0 > MNLT:
                # 604 FORMAT(' **** MORE LINES IN NLTE OPTION THAN MNLT'/
                # '       FOR LINES WITH LAMBDA GREATER THAN',F15.4,'  NM'/)
                print(" **** MORE LINES IN NLTE OPTION THAN MNLT\n"
                      "       FOR LINES WITH LAMBDA GREATER THAN%15.4f  NM\n"
                      % alam)
                break                       # GO TO 100
            gi = 2.0 * ql + un
            gj = 2.0 * qu + un
            nlte(il, ilwn, iun, gi, gj)     # CALL NLTE，不改标量哑元
            C.ILOWN[il] = ilwn
            C.IUPN[il] = iun
        if ilwn > 0 and C.INLTE != 0:
            innlt0 = innlt0 + 1
            C.INDNLT[il] = innlt0
            if innlt0 > MNLT:
                # 604 FORMAT（同上）
                print(" **** MORE LINES IN NLTE OPTION THAN MNLT\n"
                      "       FOR LINES WITH LAMBDA GREATER THAN%15.4f  NM\n"
                      % alam)
                break                       # GO TO 100
            gi = 2.0 * ql + un
            gj = 2.0 * qu + un
            nlte(il, ilwn, iun, gi, gj)     # CALL NLTE
            C.ILOWN[il] = ilwn
            C.IUPN[il] = iun
        if ilwn == 0 and C.INLTE >= 1:
            ilmatch = -1
            # CALL NLTSET(1,...)：改写标量哑元 → 返回全部并逐个接收
            (_mode, il, iat, ion, alam, excl, excu, ql, qu,
             isql, ilql, ipql, isqu, ilqu, ipqu, ieven, innlt0,
             ilmatch) = nltset(1, il, iat, ion, alam, excl, excu, ql, qu,
                               isql, ilql, ipql, isqu, ilqu, ipqu, ieven,
                               innlt0, ilmatch)

            # Success accounting for nlte lines matched with quantum numbers
            # and energy limits

            # nlte lines searched  matching energies and quantum numbers
            if ilmatch >= 0:
                ilsearch = ilsearch + 1
                # nlte lines not found matching
                if ilmatch == 0:
                    ilfail = ilfail + 1
                # nlte lines with multiple matches
                elif ilmatch == 2:
                    ilmult = ilmult + 1
                # nlte lines uniquely matched
                elif ilmatch == 1:
                    ilfound = ilfound + 1

            if C.INDNLT[il] > 0:
                if C.INDNLT[il] > MNLT:
                    # 604 FORMAT（同上）
                    print(" **** MORE LINES IN NLTE OPTION THAN MNLT\n"
                          "       FOR LINES WITH LAMBDA GREATER THAN%15.4f  NM\n"
                          % alam)
                    break                   # GO TO 100
                gi = 2.0 * ql + un
                gj = 2.0 * qu + un
                ilwn = C.ILOWN[il]
                iun = C.IUPN[il]
                if ilwn == iun and gi == gj:
                    C.INDNLT[il] = 0
                    C.ILOWN[il] = 0
                    C.IUPN[il] = 0
                else:
                    nlte(il, ilwn, iun, gi, gj)     # CALL NLTE
        # GO TO 10

    # 100
    C.NLIN0 = il
    C.NNLT = innlt0
    C.NGRIEM = igrie0
    alm1 = cnm / C.FREQ0[1]
    if C.ALAM0 < alm1 and C.IMODE != 1:
        C.ALAM0 = alm1 - 4.0 * doplam
        if C.ALAM0 < alam00:
            C.ALAM0 = alam00
    alm2 = cnm / C.FREQ0[C.NLIN0]
    if C.NLIN0 > 1:
        alm2 = cnm / C.FREQ0[C.NLIN0 - 1]
    if alast > alm2 and C.IMODE != 1:
        alast = alm2 - 4.0 * doplam
        if alast > alast0:
            alast = alast0
        C.FRLAST = cnm / alast
    C.IBLANK = 0

    # WRITE(11,*) 列表定向输出：原输出带前导空格，这里近似
    write_line(11, 'INILIN: NLTE matches using Energies and SLP limits --')
    write_line(11, '%d lines searched' % ilsearch)
    write_line(11, '%d lines unmatched -- set to LTE' % ilfail)
    write_line(11, '%d lines with multiple matches' % ilmult)
    write_line(11, '%d lines uniquely matched' % ilfound)
    write_line(11, '----------------------------------------------------')

    print('----------------------------------------------------')       # WRITE(*,*)
    # 611 FORMAT(/' LINES - TOTAL        :',I10
    #       /' LINES - NLTE         :',I10/)
    print("\n LINES - TOTAL        :%10d\n LINES - NLTE         :%10d\n"
          % (C.NLIN0, C.NNLT))
    # 601 FORMAT（见上）
    # 603 FORMAT（见上）
    # 604 FORMAT（见上）
    return


def inilin_grid():
    """read in the input line list,
    selection of lines that may contribute,
    set up auxiliary fields containing line parameters,

    Input of line data - unit 19:

    For each line, one (or two) records, containing:

   ALAM    - wavelength (in nm)
   ANUM    - code of the element and ion (as in Kurucz-Peytremann)
             (eg. 2.00 = HeI; 26.00 = FeI; 26.01 = FeII; 6.03 = C IV)
   GF      - log gf
   EXCL    - excitation potential of the lower level (in cm*-1)
   QL      - the J quantum number of the lower level
   EXCU    - excitation potential of the upper level (in cm*-1)
   QU      - the J quantum number of the upper level
   AGAM    = 0. - radiation damping taken classical
           > 0. - the value of Gamma(rad)

    There are now two possibilities, called NEW and OLD, of the next
    parameters:
    a) NEW, next parameters are:
   GS      = 0. - Stark broadening taken classical
           > 0. - value of log gamma(Stark)
   GW      = 0. - Van der Waals broadening taken classical
           > 0. - value of log gamma(VdW)
   INEXT   = 0  - no other record necessary for a given line
           > 0  - next record is read, which contains:
   WGR1,WGR2,WGR3,WGR4 - Stark broadening values from Griem (in Angst)
                  for T=5000,10000,20000,40000 K, respectively;
                  and n(el)=1e16 for neutrals, =1e17 for ions.
   ILWN    = 0  - line taken in LTE (default)
           > 0  - line taken in NLTE, ILWN is then index of the
                  lower level
           =-1  - line taken in approx. NLTE, with Doppler K2 function
           =-2  - line taken in approx. NLTE, with Lorentz K2 function
   IUN     = 0  - population of the upper level in LTE (default)
           > 0  - index of the lower level
   IPRF    = 0  - Stark broadening determined by GS
           < 0  - Stark broadening determined by WGR1 - WGR4
           > 0  - index for a special evaluation of the Stark
                  broadening (in the present version inly for He I -
                  see procedure GAMHE)
     b) OLD, next parameters are
    IPRF,ILWN,IUN - the same meaning as above
    next record with WGR1-WGR4 - again the same meaning as above
    (this record is automatically read if IPRF<0

    The only differences between NEW and OLD is the occurence of
    GS and GW in NEW, and slightly different format of reading.

    对应 synspec54.f 行 9197–9579
    """
    # PARAMETER 局部常量
    c1 = 2.3025851
    c2 = 4.2014672
    c3 = 1.4387886
    cnm = 2.997925e17
    anumin = 1.9
    anumax = 99.31
    ahe2 = 2.01
    ext0 = 3.17
    un = 1.0
    ten = 10.0
    hund = 1.0e2
    tenm4 = 1.0e-4
    tenm8 = 1.0e-8
    op4 = 0.4
    agr0 = 2.4734e-22
    xeh = 13.595
    xet = 8067.6
    xnf = 25.0
    r02 = 2.5
    r12 = 45.0
    vw0 = 4.5e-9
    bnc = 1.4743e-2
    hkc = 4.79928e-11
    enhe1 = 198310.76
    enhe2 = 438908.85
    # DATA INLSET /0/ —— 本子程序中未再引用，仅保留注释
    wgr1 = 0.0
    wgr2 = 0.0
    wgr3 = 0.0
    wgr4 = 0.0

    if C.irelin == 0:
        return

    relop0 = C.RELOP
    C.RELOP = 1.0e-3 * C.RELOP
    if C.RELOP > 1.0e-4:
        C.RELOP = 1.0e-4
    if C.RELOP < 1.0e-5:
        C.RELOP = 1.0e-5
    C.plalin = 0.0
    ijcon = 2
    il = 0
    innlt0 = 0
    igrie0 = 0
    if C.NXTSET == 1:
        C.ALAM0 = C.ALM00
        alast = C.ALST00
        C.FRLAST = cnm / alast
        C.NXTSET = 0
        rewind_unit(19)                     # REWIND 19
        _chunk08_urec_pos.pop(19, None)
    alam00 = C.ALAM0
    alast = cnm / C.FRLAST
    alast0 = alast
    dopstd = 1.0e7 / C.ALAM0 * C.DSTD
    doplam = C.ALAM0 * C.ALAM0 / cnm * dopstd
    avab = C.ABSTD[C.IDSTD] * C.RELOP
    id_ = C.IDSTD
    dstdid = math.sqrt(1.4e7 * C.TEMP[C.IDSTD])
    astd = 1.0
    # IF(GRAV.GT.6.) ASTD=0.1（原代码已注释）
    cutoff = C.CUTOF0
    alast = cnm / C.FRLAST
    absta = C.absoc[1]
    # 630 format(/' read line list with alam0, alast',2f10.3,1p3e11.3/)
    print("\n read line list with alam0, alast%10.3f%10.3f%11.3e%11.3e\n"
          % (C.ALAM0, alast, C.ABSTD[C.IDSTD], absta))

    # TODO(port): afac 计算中 IAT 先于任何赋值被引用（Fortran 静态残值），取 0
    iat = 0
    ion = 0     # TODO(port): inlist<0 分支中 ION 先于赋值被引用，取 0
    gfp = 0.0   # TODO(port): 同上
    epp = 0.0   # TODO(port): 同上
    rstd = 1.0e4
    if C.RELOP > 0.0:
        rstd = 1.0 / C.RELOP
    afac = 10.0
    if iat > 15 and iat != 26:
        afac = 1.0
    afac = afac * rstd * astd

    afac = afac * rstd * astd               # 原代码重复执行一次，直译保留
    afilin = alast

    # first part of reading line list - read only lambda, and
    # skip all lines with wavelength below ALAM0-CUTOFF
    alam = 0.0
    while True:                             # 7 CONTINUE
        if C.IBIN[0] == 0:
            # read(19,510) alam
            # 510 FORMAT(F10.4)
            alam = float(read_line(19)[:10])
        else:
            # read(19) alam（无格式：整条记录读出，只取第一量）
            _payload = _chunk08_read_urec(19)
            alam = float(np.frombuffer(_payload[:8], dtype=np.float64)[0])
        if alam >= C.ALAM0 - cutoff:
            break
        # GO TO 7
    _chunk08_backspace(19)                  # BACKSPACE(19)
    # GO TO 10

    while True:                             # 标号 10：主循环
        # 8 CONTINUE（err=8 重新进入点）
        ilwn = 0
        iun = 0
        iprf = 0
        gs = 0.0
        gw = 0.0
        if C.IBIN[0] == 0:
            try:
                # READ(19,*,END=100,err=8) ALAM,...,GS,GW
                _tok = read_line(19).replace(',', ' ').split()
                alam = float(_tok[0])
                anum = float(_tok[1])
                gf = float(_tok[2])
                excl = float(_tok[3])
                ql = float(_tok[4])
                excu = float(_tok[5])
                qu = float(_tok[6])
                agam = float(_tok[7])
                gs = float(_tok[8])
                gw = float(_tok[9])
            except EOFError:
                break                       # END=100 → 标号 100
            except (ValueError, IndexError):
                continue                    # err=8 → 标号 8
        else:
            try:
                # read(19,end=100) ALAM,...,GS,GW
                _payload = _chunk08_read_urec(19)
            except EOFError:
                break                       # END=100
            _r = np.frombuffer(_payload[:80], dtype=np.float64)
            alam = float(_r[0])
            anum = float(_r[1])
            gf = float(_r[2])
            excl = float(_r[3])
            ql = float(_r[4])
            excu = float(_r[5])
            qu = float(_r[6])
            agam = float(_r[7])
            gs = float(_r[8])
            gw = float(_r[9])

        # change wavelength to vacuum for lambda > 2000
        if alam > 200.0 and C.vaclim > 2000.0:
            wl0 = alam * 10.0
            alm = 1.0e8 / (wl0 * wl0)
            xn1 = 64.328 + 29498.1 / (146.0 - alm) + 255.4 / (41.0 - alm)
            wl0 = wl0 * (xn1 * 1.0e-6 + un)
            alam = wl0 * 0.1

        # first selection : for a given interval a atomic number
        if alam > alast + cutoff:
            break                           # GO TO 100

        # second selection : for line strengths
        fr0 = cnm / alam
        if C.INLIST >= 0:
            iat = int(np.float32(anum))     # ifix(real(ANUM,4))
            fra = (anum - float(iat) + tenm4) * hund
            ion = int(fra) + 1
            if ion > C.IONIZ[iat]:
                continue                    # GO TO 10
            ieven = 1
            excl = abs(excl)
            excu = abs(excu)
            if excl > excu:
                fra = excl
                excl = excu
                excu = fra
                fra = ql
                ql = qu
                qu = fra
                ieven = 0
            gfp = c1 * gf - c2
            epp = c3 * excl
        else:
            if ion > C.IONIZ[iat]:
                continue                    # GO TO 10

        if fr0 < C.FREQC[ijcon]:
            ijcon = ijcon + 1
            absta = 0.5 * (C.absoc[ijcon] + C.scatc[ijcon]
                           + C.absoc[ijcon - 1] + C.scatc[ijcon - 1])
        C.ABSTD[id_] = absta

        dop = 1.0e7 / alam * dstdid
        abct = math.exp(gfp - epp / C.TEMP[id_]) * C.RRR[id_, ion, iat]
        abid = abct / dop / absta
        ext = math.sqrt(abid * afac) * dop

        # line part of the Planck mean opacity（原代码整段已注释）
        #      if(alam.ge.alam0.and.alam.le.alast) then
        #      if(abid.ge.relop) then
        #        xx=exp(-hkc*fr0/temp(id))
        #        pln=bnc*(fr0*1.e-15)**3*xx/(un-xx)
        #        abct=abct*(un-xx)
        #        plalin=plalin+pln*abct
        #        write(16,643) iat,ion,alam*10.,abct,dop,absta,abid
        # 643    format(2i4,0pf12.3,1p6e12.4)
        #     end if

        alax0 = 12.0
        # alax0=0（原代码已注释）

        if C.IMODE == -6:
            continue                        # GO TO 10
        if alam < afilin:
            if abid >= C.RELOP:
                afilin = alam
            else:
                if abid < C.RELOP * 1.0e-6:
                    continue                # GO TO 10
        elif alam < 9500.0:
            if abid < C.RELOP:
                continue                    # GO TO 10
        elif alam < 9950.0:
            if abid < C.RELOP * 1.0e-9:
                continue                    # GO TO 10
        else:
            if abid < C.RELOP * 1.0e-19:
                continue                    # GO TO 10

        # if(abid.lt.relop.and.alam.gt.alax0) go to 10（原代码已注释）
        # if(abid.lt.1.e-10*relop.and.alam.lt.alax0) go to 10（原代码已注释）
        if anum < anumin or anum > anumax:
            continue                        # GO TO 10
        if anum > anumax:                   # 原代码重复判断，直译保留
            continue                        # GO TO 10
        if abs(anum - ahe2) < tenm4 and C.IFHE2 > 0:
            continue                        # GO TO 10

        extin0 = ext

        # truncate line list if there are more lines than maximum allowable
        # (given by MLIN0 - see include file LINDAT.FOR)
        il = il + 1
        if il > MLIN0:
            # 601 FORMAT('0 **** MORE LINES THAN MLIN0, LINE LIST TRUNCATED '/
            # '       AT LAMBDA',F15.4,'  NM'/)
            print("\n **** MORE LINES THAN MLIN0, LINE LIST TRUNCATED \n"
                  "       AT LAMBDA%15.4f  NM\n" % alam)
            il = MLIN0
            alast = cnm / C.FREQ0[il] - cutoff
            C.FRLAST = cnm / alast
            C.NXTSET = 1
            break                           # GO TO 100

        # =============================================
        # line is selected, set up necessary parameters
        # =============================================
        # evaluation of EXTIN0 - the distance (in delta frequency) where
        # the line is supposed to contribute to the total opacity

        # store parameters for selected lines
        C.FREQ0[il] = fr0
        C.EXCL0[il] = float(np.float32(epp))        # real(EPP,4)
        C.EXCU0[il] = float(np.float32(excu * c3))  # real(EXCU*C3,4)
        C.GF0[il] = float(np.float32(gfp))          # real(GFP,4)
        C.EXTIN[il] = float(np.float32(extin0))     # real(EXTIN0,4)
        C.INDAT[il] = 100 * iat + ion

        # ****** line broadening parameters *****
        # 1) natural broadening
        if agam > 0.0:
            C.GAMR0[il] = float(np.float32(math.exp(c1 * agam)))
        else:
            C.GAMR0[il] = float(np.float32(agr0 * fr0 * fr0))

        # if Stark or Van der Waals broadening assumed classical,
        # evaluate the effective quantum number
        if gs == 0.0 or gw == 0.0:
            z = float(ion)
            xneff2 = z ** 2 * (xeh / (C.ENEV[iat, ion] - excu / xet))
            if xneff2 <= 0.0 or xneff2 > xnf:
                xneff2 = xnf

        # 2) Stark broadening
        if gs != 0.0:
            C.GS0[il] = float(np.float32(math.exp(c1 * gs)))
        else:
            C.GS0[il] = float(np.float32(tenm8 * xneff2 * xneff2
                                         * math.sqrt(xneff2)))

        # 3) Van der Waals broadening
        if gw != 0.0:
            C.GW0[il] = float(np.float32(math.exp(c1 * gw)))
        else:
            if iat < 21:
                r2 = r02 * (xneff2 / z) ** 2
            elif iat < 45:
                r2 = (r12 - float(iat)) / z
            else:
                r2 = 0.5
            C.GW0[il] = float(np.float32(vw0 * r2 ** op4))

        # 4) parameters for a special profile evaluation:
        # a) special He I and He II line broadening parameters
        isprff = 0
        if iat <= 2:
            isprff = ispec(iat, ion, alam)  # FUNCTION ISPEC
        if iat == 2:
            # CALL HESET(...)：HESET 改写 IPRF0、ILWN、IUPN → 返回全部标量哑元
            il, alam, excl, excu, ion, iprf, ilwn, iun = heset(
                il, alam, excl, excu, ion, iprf, ilwn, iun)
        C.ISPRF[il] = isprff
        C.IPRF0[il] = iprf

        # b) parameters for Griem values of Stark broadening
        if iprf < 0:
            igrie0 = igrie0 + 1
            C.IGRIEM[il] = igrie0
            if igrie0 > MGRIEM:
                # 603 FORMAT('0 **** MORE LINES WITH GRIEM PROFILES THAN MGRIEM'/
                # '       FOR LINES WITH LAMBDA GREATER THAN',F15.4,'  NM'/)
                print("\n **** MORE LINES WITH GRIEM PROFILES THAN MGRIEM\n"
                      "       FOR LINES WITH LAMBDA GREATER THAN%15.4f  NM\n"
                      % alam)
                # GO TO 20（跳过 WGR0 存储）
            else:
                C.WGR0[1, igrie0] = float(np.float32(wgr1))
                C.WGR0[2, igrie0] = float(np.float32(wgr2))
                C.WGR0[3, igrie0] = float(np.float32(wgr3))
                C.WGR0[4, igrie0] = float(np.float32(wgr4))
        # 20 CONTINUE
        # GO TO 10

    # 100
    C.NLIN0 = il
    C.NNLT = innlt0
    C.NGRIEM = igrie0
    alm1 = cnm / C.FREQ0[1]
    if C.ALAM0 < alm1 and C.IMODE != 1:
        C.ALAM0 = alm1 - 4.0 * doplam
        if C.ALAM0 < alam00:
            C.ALAM0 = alam00
    alm2 = cnm / C.FREQ0[C.NLIN0]
    if C.NLIN0 > 1:
        alm2 = cnm / C.FREQ0[C.NLIN0 - 1]
    if alast > alm2 and C.IMODE != 1:
        alast = alm2 - 4.0 * doplam
        if alast > alast0:
            alast = alast0
        C.FRLAST = cnm / alast
    C.IBLANK = 0
    C.RELOP = relop0

    # 611 FORMAT(/' ATOMIC LINES        :',I10/)
    print("\n ATOMIC LINES        :%10d\n" % C.NLIN0)
    # WRITE(6,611) NLIN0,NNLT,NGRIEM（原代码已注释）
    # 611 FORMAT(/' LINES - TOTAL        :',I10
    #       /' LINES - NLTE         :',I10
    #       /' LINES - GRIEM        :',I10/)（原代码已注释）
    # 601 FORMAT（见上）
    # 602 FORMAT('0 **** MORE LINES WITH SPECIAL PROFILES THAN MPRF'/...)（原代码已注释）
    # 603 FORMAT（见上）
    # 604 FORMAT('0 **** MORE LINES IN NLTE OPTION THAN MNLT'/...)（原代码已注释）
    return


def inibla():
    """driving procedure for treating a partial line list for the
    current wavelength region

    对应 synspec54.f 行 9586–9631
    """
    # PARAMETER (DP0=3.33564E-11, DP1=1.651E8,
    #            VW1=0.42, VW2=0.45,TENM4=1.E-4)
    # （注意原代码中 VW2 有注释掉的旧值 0.3）
    dp0 = 3.33564e-11
    dp1 = 1.651e8
    vw1 = 0.42
    vw2 = 0.45
    tenm4 = 1.0e-4
    # PARAMETER (UN=1.)
    un = 1.0

    if C.NLIN == 0:
        return
    xx = C.FREQ[1]
    if C.NFREQ >= 2:
        xx = 0.5 * (C.FREQ[1] + C.FREQ[2])
    if C.IFWIN > 0:
        xx = 0.5 * (C.FREQC[1] + C.FREQC[C.NFREQC])
    bnu = BN * (xx * 1.0e-15) ** 3
    hkf = HK * xx
    if C.IFWIN > 0:
        xx = un
    for id_ in range(1, C.ND + 1):          # DO 20 ID=1,ND
        t = C.TEMP[id_]
        ane = C.ELEC[id_]
        exh = math.exp(hkf / t)
        C.EXHK[id_] = un / exh
        C.PLAN[id_] = bnu / (exh - un)
        C.STIM[id_] = un - C.EXHK[id_]
        if C.IATH > 0:
            anp = C.POPUL[C.NKH, id_]
            ah = C.DENS[id_] / C.WMM[id_] / C.YTOT[id_] - anp
        else:
            ah = C.RRR[id_, 1, 1]
        ahe = C.RRR[id_, 1, 2]
        C.VDWC[id_] = (ah + vw1 * ahe + 0.85 * C.anh2[id_]) * (t * tenm4) ** vw2
        for iat in range(1, MATOM + 1):       # DO 10 IAT=1,MATOM
            if C.AMAS[iat] > 0.0:
                C.DOPA1[iat, id_] = un / (xx * dp0 * math.sqrt(
                    dp1 * t / C.AMAS[iat] + C.VTURB[id_]))
        # 10 CONTINUE
    # 20 CONTINUE
    return


def idtab():
    """output of selected line parameters (identification table)

    对应 synspec54.f 行 9636–9732
    """
    # PARAMETER (C1=2.3025851, C2=4.2014672, C3=1.4387886)
    c1 = 2.3025851
    c2 = 4.2014672
    c3 = 1.4387886
    # CHARACTER*4 TYPION(30)
    # DATA TYPION /' I  ',' II ',' III',' IV ',' V  ',
    #        ' VI ',' VII','VIII',' IX ',' X  ',
    #        ' XI ',' XII','XIII',' XIV',' XV ',
    #        ' XVI','XVII',' 18 ',' XIX',' XX ',
    #        ' XXI','XXII',' 23 ','XXIV','XXV ',
    #        'XXVI',' 27 ',' 28 ','XXIX',' XXX'/  （不再修改，直接初始化）
    typion = ['',
              ' I  ', ' II ', ' III', ' IV ', ' V  ',
              ' VI ', ' VII', 'VIII', ' IX ', ' X  ',
              ' XI ', ' XII', 'XIII', ' XIV', ' XV ',
              ' XVI', 'XVII', ' 18 ', ' XIX', ' XX ',
              ' XXI', 'XXII', ' 23 ', 'XXIV', 'XXV ',
              'XXVI', ' 27 ', ' 28 ', 'XXIX', ' XXX']
    # DATA APB,AP0,AP1,AP2,AP3,AP4 /'    ','   .','   *','  **',' ***','****'/
    apb = '    '
    ap0 = '   .'
    ap1 = '   *'
    ap2 = '  **'
    ap3 = ' ***'
    ap4 = '****'

    if C.NLIN == 0:
        pass                                # GO TO 100
    else:
        alm0 = 2.997925e18 / C.FREQ[1]
        alm1 = 2.997925e18 / C.FREQ[2]
        if C.IFWIN > 0:
            alm0 = 2.997925e18 / C.FRQOBS[1]
        if C.IFWIN > 0:
            alm1 = 2.997925e18 / C.FRQOBS[C.NFREQ]
        if C.IPRIN <= -2:
            return
        if C.IPRIN >= 2:
            # IF(IMODE.GE.0.OR.(IMODE.EQ.-1.AND.IBLANK.EQ.1)) WRITE(6,602)
            # （原代码已注释）
            pass

        for il0 in range(1, C.NLIN + 1):    # DO IL0=1,NLIN
            il = C.INDLIN[il0]
            alam = 2.997925e18 / C.FREQ0[il]
            id_ = C.IDSTD
            ijcn = C.IJCNTR[il0]
            id0 = 0
            if 1 <= ijcn <= C.NFREQS:
                id0 = C.IREFD[ijcn]
            if 0 < id0 < C.ND:
                id_ = id0
            iat = idiv(C.INDAT[il], 100)    # Fortran 整数除法
            ion = imod(C.INDAT[il], 100)
            # CALL PROFIL(IL,IAT,ID,AGAM)：PROFIL 改写 AGAM → 返回全部标量哑元
            # TODO(port): AGAM 实参在调用前未赋值（PROFIL 立即覆写），传 0.0
            il, iat, id_, agam = profil(il, iat, id_, 0.0)
            abcnt = (math.exp(C.GF0[il] - C.EXCL0[il] / C.TEMP[id_])
                     * C.RRR[id_, ion, iat] * C.STIM[id_])
            absta = min(C.CH[1, C.IDSTD], C.CH[2, C.IDSTD])
            if C.IFWIN <= 0:
                dop1 = C.DOPA1[iat, id_]
                str0 = abcnt * dop1 / absta
            else:
                dop1 = C.DOPA1[iat, id_] / C.FREQ0[il]
                str0 = abcnt * dop1 / C.ABSTDW[C.IJCONT[il], id_]
            gf = (C.GF0[il] + c2) / c1
            excl = C.EXCL0[il] / c3
            if str0 <= 1.2:
                ww1 = 0.886 * str0 * (1.0 - str0 * (0.707 - str0 * 0.577))
            else:
                ww1 = math.sqrt(math.log(str0))
            if str0 > 55.0:
                ww2 = 0.5 * math.sqrt(3.14 * agam * str0)
                if ww2 > ww1:
                    ww1 = ww2
            eqw = alam / C.FREQ0[il] * 1.0e3 / dop1 * ww1
            str_ = eqw * 10.0
            apr = apb
            if 1.0 <= str_ < 1.0e1:
                apr = ap0
            if 1.0e1 <= str_ < 1.0e2:
                apr = ap1
            if 1.0e2 <= str_ < 1.0e3:
                apr = ap2
            if 1.0e3 <= str_ < 1.0e4:
                apr = ap3
            if str_ >= 1.0e4:
                apr = ap4
            if alm0 <= alam < alm1:
                ill = C.ILOWN[il]
                ilu = C.IUPN[il]
                if ill > 0:
                    ill = ill - C.NFIRST[C.IEL[ill]] + 1
                if ilu > 0:
                    ilu = ilu - C.NFIRST[C.IEL[ilu]] + 1
                # 603 FORMAT(F11.3,2X,A4,A3,F7.2,F12.3,1PE11.2,0PF8.1,1X,A4,
                #       3i4)
                write_line(12, "%11.3f  %s%s%7.2f%12.3f%11.2e%8.1f %s%4d%4d%4d"
                           % (alam, C.TYPAT[iat], typion[ion][:3], gf, excl,
                              str0, eqw, apr, ill, ilu, id_))
        # END DO
    # 602 FORMAT（原代码已注释）
    # 100 CONTINUE
    return


def iniblh():
    """output information about hydrogen lines

    对应 synspec54.f 行 9737–9861
    """
    # PARAMETER (C1=2.3025851, C2=4.2014672, C3=1.4387886)
    c1 = 2.3025851
    c2 = 4.2014672
    c3 = 1.4387886
    # PARAMETER (DP0=3.33564E-11, DP1=1.651E8,
    #            VW1=0.42, VW2=0.45,TENM4=1.E-4)
    dp0 = 3.33564e-11
    dp1 = 1.651e8
    vw1 = 0.42
    vw2 = 0.45
    tenm4 = 1.0e-4
    # PARAMETER (UN=1.)
    un = 1.0

    # DATA TYPION（不再修改，直接初始化；数据同 IDTAB）
    typion = ['',
              ' I  ', ' II ', ' III', ' IV ', ' V  ',
              ' VI ', ' VII', 'VIII', ' IX ', ' X  ',
              ' XI ', ' XII', 'XIII', ' XIV', ' XV ',
              ' XVI', 'XVII', ' 18 ', ' XIX', ' XX ',
              ' XXI', 'XXII', ' 23 ', 'XXIV', 'XXV ',
              'XXVI', ' 27 ', ' 28 ', 'XXIX', ' XXX']
    # DATA APB,AP0,AP1,AP2,AP3,AP4 /'    ','   .','   *','  **',' ***','****'/
    apb = '    '
    ap0 = '   .'
    ap1 = '   *'
    ap2 = '  **'
    ap3 = ' ***'
    ap4 = '****'

    if C.IPRIN <= -2 or C.IHYL < 0:
        return
    alm0 = 2.997925e18 / C.FREQ[1]
    alm1 = 2.997925e18 / C.FREQ[2]
    xx = C.FREQ[1]
    if C.NFREQ >= 2:
        xx = 0.5 * (C.FREQ[1] + C.FREQ[2])
    bnu = BN * (xx * 1.0e-15) ** 3
    hkf = HK * xx

    iat = 1
    ion = 1
    izz = 1
    id_ = C.IDSTD
    t = C.TEMP[id_]
    ane = C.ELEC[id_]
    exh = math.exp(hkf / t)
    C.EXHK[id_] = un / exh
    C.PLAN[id_] = bnu / (exh - un)
    C.STIM[id_] = un - C.EXHK[id_]
    C.DOPA1[iat, id_] = un / (xx * dp0 * math.sqrt(
        dp1 * t / C.AMAS[iat] + C.VTURB[id_]))
    iserl = C.ILOWH
    iseru = C.ILOWH
    if alm0 > 17000.0 and alm1 < 21000.0:
        iserl = 3
        iseru = 4
    elif alm0 > 22700.0:
        iserl = 4
        iseru = 5
        if alm0 > 32800.0:
            iseru = 6
        if alm0 > 44660.0:
            iseru = 7

    for i in range(iserl, iseru + 1):       # DO I=ISERL,ISERU
        ii = i * i
        xii = un / ii
        m1 = C.M10
        if i < C.ILOWH:
            m1 = C.ILOWH - 1
        m2 = m1 + 1
        if m1 < i + 1:
            m1 = i + 1
        m1 = m1 - 1
        m2 = C.M20 + 3
        if m1 < i + 1:
            m1 = i + 1
        if C.GRAV > 3.0:
            m2 = m2 + 5
            m1 = m1 - 3
            if m1 > i + 6:
                m1 = m1 - 3
        if C.GRAV > 6.0:
            m2 = m2 + 2
            m1 = m1 - 1
            if m1 > i + 6:
                m1 = m1 - 1
        if m1 < i + 1:
            m1 = i + 1
        if m2 > 20:
            m2 = 20
        ilinh = 0
        for j in range(m2, m1 - 1, -1):     # DO J=M2,M1,-1
            # CALL STARK0(I,J,izz,XKIJ,WL0,FIJ,FIJ0)：STARK0 改写
            # XKIJ/WL0/FIJ/FIJ0 → 按约定返回全部标量哑元
            # TODO(port): XKIJ/WL0/FIJ/FIJ0 实参在首次调用前未赋值
            # （STARK0 全部覆写），传 0.0
            i, j, izz, xkij, wl0, fij, fij0 = stark0(i, j, izz,
                                                     0.0, 0.0, 0.0, 0.0)
            alam = wl0
            if alm0 <= alam < alm1:
                ilinh = ilinh + 1
                gh = 2.0 * ii
                gf = math.log10(fij * gh)
                excl = 109679.0 * (1.0 - xii)
                excl0h = excl * c3
                gf0h = gf * c1 - c2
                abcnt = (math.exp(gf0h - excl0h / C.TEMP[id_])
                         * C.RRR[id_, ion, iat]
                         * C.DOPA1[iat, id_] * C.STIM[id_])
                str0 = abcnt / C.ABSTD[id_]
                if str0 <= 1.2:
                    ww1 = 0.886 * str0 * (1.0 - str0 * (0.707 - str0 * 0.577))
                else:
                    ww1 = math.sqrt(math.log(str0))
                if str0 > 55.0:
                    agam = 0.01
                    ww2 = 0.5 * math.sqrt(3.14 * agam * str0)
                    if ww2 > ww1:
                        ww1 = ww2
                eqw = alam * alam / 3.0e18 * 1.0e3 / C.DOPA1[iat, id_] * ww1
                str_ = eqw * 10.0
                apr = apb
                if 1.0 <= str_ < 1.0e1:
                    apr = ap0
                if 1.0e1 <= str_ < 1.0e2:
                    apr = ap1
                if 1.0e2 <= str_ < 1.0e3:
                    apr = ap2
                if 1.0e3 <= str_ < 1.0e4:
                    apr = ap3
                if str_ >= 1.0e4:
                    apr = ap4
                # if(iprin.ge.2) WRITE(6,601) ...（原代码已注释）
                # 601 FORMAT(F10.3,2X,2A4,F7.2,F12.3,1PE11.2,0PF8.1,1X,A4,2i3)
                write_line(14, "%10.3f  %s%s%7.2f%12.3f%11.2e%8.1f %s%3d%3d"
                           % (alam, C.TYPAT[iat], typion[ion], gf, excl,
                              str0, eqw, apr, i, j))
        # END DO
    # END DO

    # 601 FORMAT（见上）
    return
