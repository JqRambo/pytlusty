# -*- coding: utf-8 -*-
"""
driver.py — teddy/synspec 驱动: 用 Python 版 SYNSPEC 合成光谱

用户在含有同名 .5 和 .7 的目录下工作, 只需给出文件名前缀和路径:
  - <名>.5  TLUSTY 格式的设置文件(与 TLUSTY 输入相同; 第三行 nst 文件名
            由本驱动按 nst 参数重写, 原文件不动)
  - <名>.7  模型大气(TLUSTY 的输出模型)
  - .5 与 .7 前缀必须相同, 代表同一个模型; 前缀纯粹是文件名, 与模型种类无关

nst=None → 不设非标准参数(.5 第三行置 ''); nst=dict → 生成 nst 文件
(KEY=VALUE)并令 .5 指向它。

输出(对照原版 RSynspec 脚本的约定):
  <名>.spec  合成光谱(fort.7)    <名>.cont  连续谱流量(fort.17)
  <名>.id    谱线证认表(fort.12)  <名>.eqw   等值宽度(fort.16)
  <名>.log   运行日志(unit 6)     pyerr.log  Python 报错(应为空)
  另保留 fort.* 全套(含 fort.5 = 实际使用的修补版输入);
  不保留 data 链接(运行期间临时建立, 结束后删除)。
"""
import os
import shutil
import subprocess
import sys

PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))
SYNSPEC_PY = os.path.join(PACKAGE_DIR, "synspec54.py")
DATA_DIR = os.path.normpath(os.path.join(PACKAGE_DIR, os.pardir,
                                         "tlusty", "data"))


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


def write_fort55(path, imode=0, idstd=0, iprin=1,
                 inmod=1, intrpl=0, ichang=0, ichemc=0,
                 iophli=0, nunalp=0, nunbet=0, nungam=0, nunbal=0,
                 ifreq=0, inlte=1, icontl=1, inlist=0, ifhe2=0,
                 ihydpr=0, ihe1pr=0, ihe2pr=0,
                 alam0=4000., alast=7000., cutof0=10., cutofs=0.,
                 relop=1.e-4, space=2.,
                 nmlist=0, iunitm=20):
    """生成 SYNSPEC 附加输入 fort.55(格式与 ivan.py 的 create_fort55_lin 一致)。

    imode  0=正常合成谱 / 1=谱线轮廓细节 / 2=纯连续谱(不含线, 不需要线列表)
           -1=只出线证认表 / -2=iron-curtain 单色不透明度
    inmod  1=输入模型是 TLUSTY 模型(fort.8), 默认即可
    inlist 线列表格式: 0=文本(官方算例约定, ibin=mod(inlist,10)=0) /
           1=二进制无格式; 文本线列表必须用 0
    alam0/alast  合成波段 [Å](alast<0 表示全用真空波长)
    """
    with open(path, 'w') as f:
        f.write(f"{imode:8d} {idstd:7d} {iprin:7d}                                \n")
        f.write(f"{inmod:8d} {intrpl:7d} {ichang:7d} {ichemc:7d}                        \n")
        f.write(f"{iophli:8d} {nunalp:7d} {nunbet:7d} {nungam:7d} {nunbal:7d}                \n")
        f.write(f"{ifreq:8d} {inlte:7d} {icontl:7d} {inlist:7d} {ifhe2:7d}                \n")
        f.write(f"{ihydpr:8d} {ihe1pr:7d} {ihe2pr:7d}                                \n")
        f.write(f"    {alam0:.0f}    {alast:.0f}       {cutof0:.0f}       {cutofs:.0f}  {relop:g}    {space:g}\n")
        f.write(f"{nmlist:8d}{iunitm:8d}                                        ! nnlist\n")


def _patched_fort5(src5, dst, nst_name):
    """把 <名>.5 复制为 fort.5, 并按 nst 设置重写第三行(nst 文件名行)。"""
    with open(src5) as f:
        lines = f.readlines()
    if len(lines) < 3:
        raise ValueError(f"{src5} 行数不足, 不是合法的 TLUSTY 格式 .5 文件")
    if nst_name:
        lines[2] = f" '{nst_name}'                  ! non-standard parameter file ('' = none)\n"
    else:
        lines[2] = " ''                  ! no change of general optional parameters\n"
    with open(dst, 'w') as f:
        f.writelines(lines)


def run_synspec(name, workdir='.', nst=None, linelist=None,
                run=True, verbose=True, **kw):
    """在 workdir 中用 <name>.5 + <name>.7 合成光谱。

    name      文件名前缀(如 'FF'; 要求 workdir 下同时存在 FF.5 和 FF.7)
    workdir   工作路径
    nst       None=不设非标准参数; dict=写入 nst 文件并启用
    linelist  线列表: 'gfATO'/'gfMOL'/'gfTiO' 选内置线列表
              (teddy/synspec/data/<名>.dat, 复制为 fort.19);
              也可直接给文件路径; imode=2 纯连续谱时可为 None
    **kw      fort.55 的全部参数, 见 write_fort55(imode/alam0/alast/...)
    返回 (ok, workdir)
    """
    workdir = os.path.abspath(workdir)
    src5 = os.path.join(workdir, name + '.5')
    src7 = os.path.join(workdir, name + '.7')
    for src in (src5, src7):
        if not os.path.exists(src):
            raise FileNotFoundError(
                f"缺少输入文件: {src}(.5 和 .7 必须同名前缀同时存在)")

    # 内置线列表名 → teddy/synspec/data/<名>.dat
    if linelist and not os.path.sep in linelist and not os.path.exists(linelist):
        builtin = os.path.join(PACKAGE_DIR, 'data', linelist + '.dat')
        if not os.path.exists(builtin):
            raise FileNotFoundError(
                f"未知内置线列表: {linelist}(可选 gfATO/gfMOL/gfTiO, 或给文件路径)")
        linelist = builtin

    if nst:
        write_nst(os.path.join(workdir, 'nst'), nst)
    _patched_fort5(src5, os.path.join(workdir, 'fort.5'),
                   'nst' if nst else None)
    write_fort55(os.path.join(workdir, 'fort.55'), **kw)
    shutil.copy(src7, os.path.join(workdir, 'fort.8'))
    if linelist:
        shutil.copy(linelist, os.path.join(workdir, 'fort.19'))

    if verbose:
        print(f"[teddy/synspec] 模型 {name}  工作目录 {workdir}")
        print(f"[teddy/synspec]   输入: {name}.5 + {name}.7"
              f"  nst: {'有 ' + str(nst) if nst else '无'}"
              f"  线列表: {linelist if linelist else '无'}")
        print(f"[teddy/synspec]   fort.55: imode={kw.get('imode', 0)} "
              f"波段 {kw.get('alam0', 4000.):.0f}-{kw.get('alast', 7000.):.0f} Å")

    if not run:
        return True, workdir

    # data 链接: 运行前建立, 结束后删除
    link = os.path.join(workdir, 'data')
    made_link = False
    if not os.path.exists(link):
        os.symlink(DATA_DIR, link)
        made_link = True

    log = os.path.join(workdir, name + '.log')
    errlog = os.path.join(workdir, 'pyerr.log')
    try:
        with open(os.path.join(workdir, 'fort.5')) as fin, \
                open(log, 'w') as fout, open(errlog, 'w') as ferr:
            proc = subprocess.run(
                [sys.executable, '-u', SYNSPEC_PY],
                stdin=fin, stdout=fout, stderr=ferr,
                cwd=workdir)
        ok = proc.returncode == 0
        for unit, ext in ((7, 'spec'), (17, 'cont'), (12, 'id'), (16, 'eqw')):
            src = os.path.join(workdir, f'fort.{unit}')
            if os.path.exists(src):
                shutil.copy(src, os.path.join(workdir, f'{name}.{ext}'))
    finally:
        if made_link and os.path.islink(link):
            os.unlink(link)

    if verbose:
        if ok:
            print(f"[teddy/synspec] {name} 合成完成, 输出在 {workdir}")
            print(f"[teddy/synspec]   {name}.spec 合成光谱   {name}.cont 连续谱")
            print(f"[teddy/synspec]   {name}.id 谱线证认表   {name}.log 运行日志")
        else:
            print(f"[teddy/synspec] {name} 合成失败, 请查看 {log} 和 {errlog}")
    return ok, workdir
