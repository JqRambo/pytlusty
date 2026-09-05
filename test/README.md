# test — 测试算例与比较结果

同一套 H-He 太阳丰度算例(Teff=22500, logg=4.0, ND=50, NFREAD=2000,
FF 即 NLTE/L 模式)在三个实现下的结果, 以及 SYNSPEC 光谱合成的
Fortran/Python 对照。

## TLUSTY 模型大气(22500K, logg=4.0)

```
tlusty_22500_fortran/      Fortran TLUSTY 原版计算结果(参照)
tlusty_22500_py_serial/    teddy/tlusty  串行 Python 版计算结果
tlusty_22500_py_parallel/  teddy/tlusty2 并行 Python 版计算结果
                           (TLUSTY_NPAR=48)
```

每个目录含: FF.5(输入)、FF.6(日志)、FF.7(模型)、FF.9(收敛历史)、
nst 及全部 fort.*; py_serial 目录另有 old.5/old.7(起始模型, 三个
算例用同一起始模型)。

比较程序(在 test/compare/ 下):
- `compare_all.py`    双方比较(任意两个 .7 模型) -> combined_comparison.pdf
- `compare3.py`      三方比较, 横轴质量深度 M -> comparison3_22500.pdf
- `compare3_tau.py`  三方比较, 横轴 Rosseland 光深
                     (TAUROSS 取自各自 FF.6) -> comparison3_tau_22500.pdf

结果: 三者同为 23 次迭代收敛, 每次迭代最大相对变化完全一致
(0.776 -> 3.76e-4); Python 串行与并行相对 Fortran 的差异完全相同:
T 中位 1.4e-3、ne 1.9e-3、rho 2.0e-3(各自收敛精度内)。

## SYNSPEC 光谱合成(3000-9000 Å, gfATO 线列表)

```
synspec_fortran/  Fortran SYNSPEC 原版计算结果(参照)
synspec_python/   teddy/synspec Python 版计算结果
```

两个目录用完全相同的输入: FF.5(同上 22500K 模型的设置)、FF.7
(tlusty_22500_fortran 的模型)、fort.55 参数
(imode=0, idstd=50, iprin=1, ifreq=1, inlte=1, icontl=0,
cutof0=10, relop=1e-4, space=0.5)。synspec_fortran 中的 fort.55.lin
即 Fortran 运行使用的附加输入。

比较程序: `test/compare/compare_spec.py`(只读 .spec)
-> comparison_spec.pdf

结果: 波长点完全相同(20200 点), 流量中位相对差 1.3e-7,
最大 7.4e-4(4481 Å 深线心); 谱线证认 847 条, 线数 TOTAL 8909 /
NLTE 734 两侧一致。
