# -*- coding: utf-8 -*-
"""
syn.py — teddy/synspec: 光谱合成设置与入口
==========================================

设置好下面的参数后运行:   python3 syn.py

前提: 工作目录 WORK_DIR 下已有同名前缀的设置文件和模型大气文件
(NAME.5 和 NAME.7, 由 teddy/tlusty 或 Fortran TLUSTY 算出)。
前缀纯粹是文件名, 与模型种类(TT/TF/FF)无关; 两个文件同名才合成,
代表同一个模型。

输出在 WORK_DIR 中: NAME.spec(合成光谱), NAME.cont(连续谱),
NAME.id(谱线证认表), NAME.eqw(等值宽度), NAME.log(日志)及全部
fort.* 文件; 不保留 data 链接。
"""

from driver import run_synspec

# ------------------------- 模型与工作路径 -------------------------
NAME = 'FF'                     # 文件名前缀: 用 FF.5 + FF.7 合成
WORK_DIR = '/home/ubuntu/transform/teddy/test/synspec_python'

# ------------------------- 波段与模式 -------------------------
IMODE = 0               # 0=正常合成谱 / 1=谱线轮廓 / 2=纯连续谱(不需线列表)
IDSTD = 0               # 标准深度序号(fort.55 第一行第二列): 在该深层处
                        # 打印电离分布并取标准多普勒宽度; 0=自动取 2*ND/3,
                        # 也可直接给深度序号(如 ND=50 的模型写 50=最深层)
IPRIN = 1               # 输出详细程度, >=1 才有谱线证认表(NAME.id)
ALAM0 = 3000.0          # 起始波长 [Å]
ALAST = 9000.0          # 结束波长 [Å](写负数表示全用真空波长)
CUTOF0 = 10.0           # 谱线截断参数 [Å], 推荐 5-10
RELOP = 1.0e-4          # 线心/连续不透明度比值下限
SPACE = 0.5             # 相邻频率点最大间隔 [Å]

# ------------------------- 其它开关 -------------------------
IFREQ = 1               # 0=SPACE 以 Å 计; >0=以频率间隔计(标准算例用 1)
INLTE = 1               # 0=所有谱线按 LTE; 1=允许 NLTE 谱线
ICONTL = 0              # 连续谱频率点的线不透明度处理(标准算例用 0)

# ------------------------- 线列表 -------------------------
# 'gfATO'/'gfMOL'/'gfTiO' 选内置线列表, 或直接写文件路径;
# IMODE=2(纯连续谱)时写 None
LINELIST = 'gfATO'
# LINELIST = '/home/ubuntu/transform/tlusty/linelist/lines.dat'

# ------------------------- nst 非标准参数 -------------------------
# 不需要就写 None; 需要就按 KEY=VALUE 给(如 VTB=2. 湍流速度 [km/s])
NST = None
# NST = {'VTB': 2.}

# ------------------------- 执行 -------------------------
if __name__ == '__main__':
    ok, outdir = run_synspec(
        NAME, workdir=WORK_DIR, nst=NST, linelist=LINELIST,
        imode=IMODE, idstd=IDSTD, iprin=IPRIN,
        ifreq=IFREQ, inlte=INLTE, icontl=ICONTL,
        alam0=ALAM0, alast=ALAST,
        cutof0=CUTOF0, relop=RELOP, space=SPACE,
        run=True)
    raise SystemExit(0 if ok else 1)
