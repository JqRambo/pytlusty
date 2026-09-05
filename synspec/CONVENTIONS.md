# SYNSPEC Fortran → Python 直译移植约定

本文件是**所有翻译分块必须严格遵守的统一约定**。目标：将 `synspec54.f`（固定格式 Fortran 77）
直译为 Python，功能不变。禁止意译重构、禁止省略任何代码、禁止运行程序。

## 目录结构

```
teddy/synspec/
  params.py        # 全部 PARAMETER 常量（已存在，import 即用）
  commons.py       # 全部 COMMON 块变量（已存在，懒分配；用法 import commons as C）
  fortran.py       # Fortran 运行时辅助函数（已存在，from fortran import *）
  synspec54.py     # 最终组装的主模块（由所有分片拼接而成）
  fragments/chunkNN.py   # 各分片：只含函数定义，禁止写 import 语句
```

## 分片规则

- 每个分片最终被拼进同一个模块 `synspec54.py`，模块头部已有：
  ```python
  import math, sys
  import numpy as np
  from params import *
  import commons as C
  from fortran import *
  ```
  因此**分片内禁止出现任何 import**；直接使用 `np`、`math`、`C`、params 常量和 fortran 辅助函数。
- 跨子程序调用直接写函数名（所有子程序最终都在同一模块内）。

## 命名

- 子程序/函数名 → 小写 Python 函数名，如 `SUBROUTINE RESOLV` → `def resolv():`。
- Fortran 标识符**大小写不敏感**，Python 敏感。统一规则：
  - COMMON 变量：一律使用 `commons.py` 中声明的规范拼写访问（`C.TEFF`、`C.POPUL`…），
    翻译时把源码中的任何大小写变体（如 `Teff`、`tEfF`）都归一到规范拼写。
  - PARAMETER：用 `params.py` 中的规范拼写。
  - 局部变量：以该变量在代码中第一次出现的拼写为准，全函数保持一致。
- 局部变量不得遮蔽 `params.py` 常量名；若冲突，局部变量加后缀 `_l` 并加注释说明。

## 类型与数组（关键：保持 Fortran 1 基索引）

- `IMPLICIT REAL*8 (A-H,O-Z), LOGICAL*1 (L)`：
  - 首字母 I–N → `int`；A–H、O–Z → `float`；L 开头 → `bool`；显式声明优先。
- 数组**保持 Fortran 的 1 基索引**：分配时每个维度 +1，索引 0 不用。
  局部数组：`a = np.zeros(n + 1)`；二维：`a = np.zeros((n1 + 1, n2 + 1))`，访问 `a[i, j]`。
- COMMON 数组已由 `commons.py` 按声明维度 +1 预分配好，直接用 `C.XXX[i, j]`，不要自己再分配。
- 整型局部数组 `np.zeros(n+1, dtype=np.int64)`；逻辑数组 `dtype=bool`；字符数组用 list 或 `np.empty(n+1, dtype=object)` 并填 `''`。
- **整数除法**：Fortran `I/J` 是向零截断 → 一律写 `idiv(i, j)`（fortran.py 提供），禁止用 `//` 或 `/`。
- `MOD(I,J)` → `imod(i, j)`；`DINT(X)` → `dint(x)`；`DNINT(X)` → `dnint(x)`；
  `DSIGN(A,B)` → `dsign(a, b)`；`DABS`→`abs`、`DFLOAT`→`float`、`SNGL`→`float`、`IABS`→`abs`。
- 数学函数用 `math.`：`DEXP`→`math.exp`、`DLOG`→`math.log`、`DLOG10`→`math.log10`、
  `DSQRT`→`math.sqrt`、`DSIN/DCOS/DTAN/DATAN/DATAN2`→`math.sin/cos/tan/atan/atan2`。
- `DMAX1/DMIN1/MAX0/MIN0/AMAX1...` → `max`/`min`。
- 常量字面量：`1.D0`→`1.0`、`2.3D-15`→`2.3e-15`、`.TRUE.`→`True`、`.FALSE.`→`False`。
- 运算符：`.EQ.`→`==`、`.NE.`→`!=`、`.LT.`→`<`、`.LE.`→`<=`、`.GT.`→`>`、`.GE.`→`>=`、
  `.AND.`→`and`、`.OR.`→`or`、`.NOT.`→`not`、`.EQV.`→`==`、`.NEQV.`→`!=`、`**`→`**`。
- 字符串比较忽略尾部空格：用 `feq(a, b)`（fortran.py 提供）。

## 子程序参数与返回值约定（跨分片一致性关键）

Fortran 哑元是引用传递。Python 规则：

- **数组哑元**：numpy 数组天然按引用共享，就地修改，**不要返回**。
- **标量哑元**：若子程序体内对任何标量哑元赋值，则该函数 `return` **全部标量哑元**
  （按哑元声明顺序，不管是否被修改）；调用点必须重新接收：
  ```python
  # Fortran: CALL STATE(MODE,ID,T,ANE)，且 STATE 内修改 T、ANE
  mode, id, t, ane = state(mode, id, t, ane)
  ```
- 若子程序不修改任何标量哑元，则隐式返回 None，调用点直接写 `sub(...)`。
- **翻译 CALL 语句前，必须先用 Grep 在 `synspec54.f` 中查被调子程序的定义**，
  检查它是否给标量哑元赋值，据此决定是否解包接收。在两个文件中保持一致。
- `FUNCTION` → `return` 函数值；若它还修改标量哑元（罕见），返回 `(值, *标量)` 并在 docstring 注明。
- 传数组元素作为数组基址（`CALL X(A(5))`，对方 `B(1)` 起用）→ 传切片 `a[5:]` 并加注释。
- 调用点实参是字面量但被调方修改该哑元 → 用临时变量接收，加注释说明。

## 控制流

- `DO 10 I=1,N` → `for i in range(1, n + 1):`；步长 `,2` → `range(1, n + 1, 2)`；
  倒序 `DO I=N,1,-1` → `range(n, 0, -1)`。**注意终值要 ±1 调整**。
- 循环变量在循环结束后被使用（Fortran 中循环变量保留为 终值+步长）→ 循环后显式赋值并注释。
- `DO WHILE (...)` → `while ...:`。
- `GO TO`：优先最小化重构为 while/if/break/continue；无法干净重构时用一个
  `_label` 状态变量 + `while True` 分发，并保留原标号注释，例如：
  ```python
  _label = 10                    # 对应 Fortran 标号 10
  while True:
      if _label == 10:
          ...
          _label = 20            # GO TO 20
          continue
      if _label == 20:
          ...
          break                  # 到达子程序末尾 / RETURN
  ```
  无论哪种方式，都要在附近注释原标号和 `GO TO` 的去向。
- 算术 `IF (X) 10,20,30` → `if x < 0: ... elif x == 0: ... else: ...`。
- `RETURN` → `return`（若有标量哑元约定则 `return 标量们`）；`STOP` → `raise SystemExit`；
  `PAUSE` → 注释说明并 `pass`。

## DATA / SAVE / EQUIVALENCE

- `DATA` 初始化局部数组且之后不再修改 → 函数顶部直接赋值，注释 `# DATA ...`。
- `DATA` 且会被修改（Fortran 隐含 SAVE）→ 提升为模块级变量 `_save_<routine>_<name>`，注释说明。
- `BLOCK DATA` → `def block_data():` 给 `C.XXX` 赋值；在 main 中首先调用。
- `EQUIVALENCE`：同形数组 → 直接起别名 `a = b` 并注释；形状不同 → 用 numpy 视图
  （注意 `reshape(..., order='F')`），无法表达时保留两个变量并写清注释说明假设。

## I/O

- `WRITE(6,...)` / `WRITE(*,...)` → `print(...)`；FORMAT 翻译成 f-string，
  原 FORMAT 语句保留为注释。`1H0`/`/` → 空行；`X` → 空格。
- 文件：`OPEN(UNIT=n,FILE='...',...)` → `open_unit(n, '...', mode)`（fortran.py）。
  `WRITE(n, fmt)` → `write_line(n, f"...")`；`READ(n, fmt)` 按上下文解析，用 `read_line(n)`。
- 无格式临时文件（`STATUS='SCRATCH'`，单元 91/92/93）：用 `scratch[91]`（ScratchFile），
  `WRITE(91) A,B` → `scratch[91].write(a, b)`；`READ(91) A,B` → `a, b = scratch[91].read()`；
  `REWIND 91` → `scratch[91].rewind()`。数组记录会自动快照，语义与 Fortran 一致。
- `READ(5,...)`/`READ(*,...)` → `read_stdin_line()` 后解析；解析逻辑按原 FORMAT/自由格式直译。
- `CLOSE(n)` → `close_unit(n)`；`ENDFILE n` / `BACKSPACE n` → 注释说明 + 对应辅助调用。

## 注释要求

- 每个函数开头写 docstring：原 Fortran 头部注释（保留英文原文）+ `对应 synspec54.f 行 X–Y`。
- 原代码中的 `C`/`!` 注释尽量保留（英文原文即可）。
- 对**翻译决策**加中文注释：如 `# GO TO 100 → 跳出循环`、`# Fortran 整数除法`、
  `# DATA 语句，隐含 SAVE` 等。难懂的物理/数值逻辑也可加简短中文说明。
- 拿不准的语义，按最合理方式翻译并用 `# TODO(port):` 注释标注疑点，**禁止省略代码**。

## 禁止事项

- 禁止省略任何可执行语句；禁止用 `...` 或“以下类似从略”。
- 禁止运行翻译后的程序（允许 `python3 -m py_compile fragments/chunkNN.py` 检查语法）。
- 禁止改动本约定文件、`params.py`、`commons.py`、`fortran.py`。
