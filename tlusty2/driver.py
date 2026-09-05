# -*- coding: utf-8 -*-
"""
driver.py — teddy 包的驱动逻辑: 生成 TLUSTY 输入并运行 Python 版 TLUSTY

用户在 basic.py 中给出配置(元素/丰度/mode/modpf/TEFF/LOGG/NFREAD/NST/
输出路径等), 这里负责:
  1. 自动生成 .5 标准输入文件(包括显式离子的完整离子表)
  2. 可选生成 nst 非标准参数文件
  3. 在输出目录中运行 Python 版 TLUSTY
  4. 运行期间临时建立 data 链接, 结束后删除
     (输出目录里不保留 data 链接, 其余 fort.* 与 MOD.* 文件全部保留)
"""
import os
import shutil
import subprocess
import sys

import atoms

PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))
TLUSTY_PY = os.path.join(PACKAGE_DIR, "tlusty208.py")
DATA_DIR = os.path.join(PACKAGE_DIR, "data")

# 三种计算模式 (与 ivan.py / TLUSTY 文档一致):
#   'TT'  LTE       : LTE=T, LTGRAY=T, 所有线细致辐射平衡 (ilvlin=100)
#   'TF'  NLTE/C    : 仅连续谱 NLTE, 线细致辐射平衡 (ilvlin=100)
#   'FF'  NLTE/L    : 完整 NLTE, 显式谱线 (ilvlin=0)
MODEL_TYPES = {
    'TT': {'lte': True,  'ltgray': True,  'ilvlin': 100},
    'TF': {'lte': False, 'ltgray': False, 'ilvlin': 100},
    'FF': {'lte': False, 'ltgray': False, 'ilvlin': 0},
    # 别名
    'LTE':    {'lte': True,  'ltgray': True,  'ilvlin': 100},
    'NLTEC':  {'lte': False, 'ltgray': False, 'ilvlin': 100},
    'NLTEL':  {'lte': False, 'ltgray': False, 'ilvlin': 0},
}


# ---------------------------------------------------------------------------
# .5 输入文件生成
# ---------------------------------------------------------------------------

def _fmt_abn(abn):
    """丰度格式化为 Fortran 浮点写法, 8 位小数不足补零, 如 1.00000000e-01
    (与 create.py 的 format_abundance 一致; 所有数值长度固定为 14 字符,
    保证 .5 文件第二列对齐)。"""
    if isinstance(abn, str):
        return abn                      # 允许直接给字符串(特殊写法)
    if abn == 0:
        return "0.00000000e+00"
    return f"{abn:.8e}"


def atoms_section(elements, model_type='FF'):
    """根据用户元素设置生成 NATOMS 记录和 ion 记录。

    elements: {符号: {'mode': m, 'abn': a, 'modpf': p}}, 支持元素 H..Es(Z<=99)
    model_type: 'TT'/'TF'/'FF' (或其别名 'LTE'/'NLTEC'/'NLTEL')

    离子表随模式变化(与 ivan.py 一致):
      FF (NLTE/L): 所有显式离子 ilvlin=0, 完整能级
      TT/TF:       每个元素第一个带数据文件的离子保持完整能级,
                   其后的普通离子压缩为一能级(ilast=1, 保留数据文件),
                   ODF 离子(如 Fe)保持完整; 带文件离子 ilvlin=100,
                   一能级裸核离子 ilvlin=0
    返回 (natoms, atom_lines, ion_lines)
    """
    mt = MODEL_TYPES[model_type]
    for sym in elements:
        if sym not in atoms.Z_OF:
            raise ValueError(f"未知元素符号: {sym!r} (支持 H 到 Es)")
    natoms = max(atoms.Z_OF[sym] for sym in elements)

    atom_lines = []
    for z in range(1, natoms + 1):
        sym = atoms.SYMBOLS[z - 1]
        cfg = elements.get(sym)
        if cfg is None:
            atom_lines.append((0, 0.0, 0))
        else:
            atom_lines.append((int(cfg.get('mode', 0)),
                               cfg.get('abn', 0.0),
                               int(cfg.get('modpf', 0))))

    ion_lines = []
    for sym, cfg in sorted(elements.items(),
                           key=lambda kv: atoms.Z_OF[kv[0]]):
        if int(cfg.get('mode', 0)) != 2:
            continue
        if sym not in atoms.EXPLICIT_IONS:
            raise ValueError(
                f"元素 {sym} 没有现成的显式原子数据配置, "
                f"请改用 mode=1 (隐式), 或在 atoms.py 的 EXPLICIT_IONS 中补充")
        z = atoms.Z_OF[sym]
        ions = cfg.get('ions') or atoms.EXPLICIT_IONS[sym]
        first_file_ion_done = False
        for iz, nlevs, filei, odf in ions:
            ilast = 1 if filei is None else 0
            ilvlin = 0
            nonstd = -1 if odf else 0
            if model_type in ('TT', 'TF', 'LTE', 'NLTEC'):
                if filei is not None:
                    ilvlin = mt['ilvlin']
                    if first_file_ion_done and odf is None:
                        # 后续普通离子压缩为一能级(与 ivan.py 的 TT/TF 一致)
                        nlevs = 1
                        ilast = 1
                    first_file_ion_done = True
            typion = f"{sym:>2s} {iz + 1}"
            ion_lines.append((z, iz, nlevs, ilast, ilvlin, nonstd,
                              typion, filei or ' ', odf))
    return natoms, atom_lines, ion_lines


def write_model5(path, teff, logg, model_type, nst_name, nfread, elements):
    """写出 TLUSTY 标准输入文件 MODEL.5。

    model_type: 'TT'/'TF'/'FF' (或别名 'LTE'/'NLTEC'/'NLTEL')
    """
    mt = MODEL_TYPES[model_type]
    natoms, atom_lines, ion_lines = atoms_section(elements, model_type)

    with open(path, 'w') as f:
        f.write(f" {teff:.0f}  {logg}      ! TEFF, GRAV\n")
        f.write(f" {'T' if mt['lte'] else 'F'}  "
                f"{'T' if mt['ltgray'] else 'F'}"
                f"                ! LTE,  LTGRAY\n")
        f.write(f" '{nst_name or ''}'                  ! non-standard "
                f"parameter file ('' = none)\n")
        f.write("*" + "-" * 64 + "\n")
        f.write("* frequencies\n*\n")
        f.write(f" {nfread:3d}                  ! NFREAD\n")
        f.write("*" + "-" * 64 + "\n")
        f.write("* data for atoms\n*\n")
        f.write(f" {natoms:2d}                   ! NATOMS\n")
        f.write("* mode abn modpf\n")
        for mode, abn, modpf in atom_lines:
            f.write(f"   {mode:2d}  {_fmt_abn(abn):>14s}      {modpf:2d}\n")
        f.write("*" + "-" * 64 + "\n")
        f.write("* data for ions\n*\n")
        f.write("*iat   iz   nlevs  ilast ilvlin  nonstd typion  filei\n*\n")
        for z, iz, nlevs, ilast, ilvlin, nonstd, typion, filei, odf \
                in ion_lines:
            f.write(f" {z:3d} {iz:4d} {nlevs:5d} {ilast:6d} {ilvlin:6d}"
                    f" {nonstd:6d}    '{typion}' '{filei}'\n")
            if odf:
                gam, lin, rap = odf
                f.write(f"   0    0                                      "
                        f"'{gam}'\n")
                f.write(f"                                               "
                        f"'{lin}'\n")
                f.write(f"                                               "
                        f"'{rap}'\n")
        f.write("   0    0     0     -1      0      0    '    ' ' '\n")
        f.write("*\n* end\n")
    return natoms


def write_nst(path, nst):
    """写出 nst 非标准参数文件(KEY=VALUE, 逗号分隔, 70 列折行)。"""
    def fmt(v):
        if isinstance(v, bool):
            return 'T' if v else 'F'
        return str(v)
    line = ""
    with open(path, 'w') as f:
        for key, value in nst.items():
            item = f"{key}={fmt(value)},"
            if len(line) + len(item) > 70:
                f.write(line.rstrip().rstrip(',') + "\n")
                line = item
            else:
                line += item
        if line:
            f.write(line.rstrip(','))


# ---------------------------------------------------------------------------
# 运行
# ---------------------------------------------------------------------------

def run_model(teff, logg, elements, nfread=2000,
              model_type='FF', nst=None,
              model='FF', output_dir='.', start_model=None,
              run=True, verbose=True, npar=None):
    """生成输入并(可选)运行 Python 版 TLUSTY。

    model_type  'TT'(LTE) / 'TF'(NLTE/C) / 'FF'(NLTE/L)
    npar        频率循环的并行进程数; None=串行(与原版逐位一致),
                建议 os.cpu_count()。并行只改变浮点求和顺序,
                与串行的差异在 1e-16 量级。
    输出目录内容: MODEL.5, MODEL.6(日志), nst(若设置), fort.* 全套,
                  MODEL.7/.9/.69/.14; 不保留 data 链接。
    返回 (ok, output_dir)
    """
    if model_type not in MODEL_TYPES:
        raise ValueError(f"model_type 必须是 {sorted(MODEL_TYPES)} 之一")
    if not model:
        model = model_type           # 文件名默认跟随模式: TT/TF/FF
    output_dir = os.path.abspath(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    nst_name = None
    if nst:
        nst_name = 'nst'
        write_nst(os.path.join(output_dir, 'nst'), nst)

    mod5 = os.path.join(output_dir, model + '.5')
    natoms = write_model5(mod5, teff, logg, model_type, nst_name,
                          nfread, elements)
    if verbose:
        nexp = sum(1 for c in elements.values()
                   if int(c.get('mode', 0)) == 2)
        print(f"[teddy] 已生成 {mod5}")
        print(f"[teddy] {model_type} 模式  TEFF={teff:.0f} logg={logg}  "
              f"NATOMS={natoms}  显式元素数={nexp}  NFREAD={nfread}")
        if nst:
            print(f"[teddy] nst 参数: {nst}")

    # 起始模型 -> fort.8
    if start_model:
        # 依次尝试: 直接路径 / 路径+.7 / OUTPUT_DIR下 / OUTPUT_DIR下+.7
        cands = [start_model, start_model + '.7',
                 os.path.join(output_dir, start_model),
                 os.path.join(output_dir, start_model + '.7')]
        src = next((c for c in cands if os.path.exists(c)), None)
        if src is None:
            raise FileNotFoundError(
                f"起始模型不存在: 已尝试 {cands}")
        shutil.copy(src, os.path.join(output_dir, 'fort.8'))
        if verbose:
            print(f"[teddy] 起始模型: {src} -> fort.8")

    if not run:
        return True, output_dir

    # data 链接: 运行前建立, 结束后删除
    link = os.path.join(output_dir, 'data')
    made_link = False
    if not os.path.exists(link):
        os.symlink(DATA_DIR, link)
        made_link = True

    log6 = os.path.join(output_dir, model + '.6')
    errlog = os.path.join(output_dir, 'pyerr.log')
    env = None
    if npar is not None:
        env = dict(os.environ, TLUSTY_NPAR=str(int(npar)))
        if verbose:
            print(f"[teddy] 频率循环并行进程数 TLUSTY_NPAR={int(npar)}"
                  " (仅浮点求和顺序不同, 差异 1e-16 量级)")
    try:
        with open(mod5) as fin, open(log6, 'w') as fout, \
                open(errlog, 'w') as ferr:
            proc = subprocess.run(
                [sys.executable, '-u', TLUSTY_PY],
                stdin=fin, stdout=fout, stderr=ferr,
                cwd=output_dir, env=env)
        ok = proc.returncode == 0
        for unit in (7, 9, 69, 14):
            src = os.path.join(output_dir, f'fort.{unit}')
            if os.path.exists(src):
                shutil.copy(src, os.path.join(output_dir,
                                              f'{model}.{unit}'))
    finally:
        if made_link and os.path.islink(link):
            os.unlink(link)

    if verbose:
        if ok:
            print(f"[teddy] 模型 {model} 计算完成, 输出在 {output_dir}")
            print(f"[teddy]   {model}.7  模型大气   {model}.9  收敛历史")
            print(f"[teddy]   {model}.6  运行日志   {model}.14 模型摘要")
        else:
            print(f"[teddy] 模型 {model} 计算失败, 请查看 {log6} 和 {errlog}")
    return ok, output_dir


def run_chain(teff, logg, elements, nfread=2000, nst=None,
              output_dir='.', verbose=True, npar=None):
    """完整的 TT -> TF -> FF 三步链式计算(与 ivan.py 的工作流程一致):

      TT (LTE)     从头计算 -> TT.7
      TF (NLTE/C)  以 TT.7 为起始模型 -> TF.7
      FF (NLTE/L)  以 TF.7 为起始模型 -> FF.7  (最终模型)

    nfread 可以是:
      - 整数: 三步共用同一 NFREAD
      - {'TT': n1, 'TF': n2, 'FF': n3}: 每一步各自的频率点数
    nst 可以是:
      - 普通 dict: 三步共用同一组 nst 参数
      - {'TT': {...}, 'TF': {...}, 'FF': {...}}: 每一步各自的 nst 参数
        (某一步缺省则该步不用 nst)
    npar 为频率循环并行进程数(None=串行), 三步共用, 透传给 run_model。
    返回 (ok, output_dir); ok 表示三步全部成功。
    """
    def per_stage(x):
        if isinstance(x, dict) and all(k in ('TT', 'TF', 'FF') for k in x):
            return lambda stage: x.get(stage)
        return lambda stage: x

    nfr = per_stage(nfread)
    nstf = per_stage(nst)

    ok, _ = run_model(teff, logg, elements, nfread=nfr('TT'),
                      model_type='TT', nst=nstf('TT'), model='TT',
                      output_dir=output_dir, verbose=verbose, npar=npar)
    if not ok:
        return False, output_dir
    ok, _ = run_model(teff, logg, elements, nfread=nfr('TF'),
                      model_type='TF', nst=nstf('TF'), model='TF',
                      output_dir=output_dir, start_model='TT',
                      verbose=verbose, npar=npar)
    if not ok:
        return False, output_dir
    ok, outdir = run_model(teff, logg, elements, nfread=nfr('FF'),
                           model_type='FF', nst=nstf('FF'), model='FF',
                           output_dir=output_dir, start_model='TF',
                           verbose=verbose, npar=npar)
    return ok, outdir
