# 随包 wheel 许可材料事实核查

核查日期：2026-09-22。对象为本地 `outputs/dist/qcblender-0.0.1.zip` 的实际字节，不是安装目录，也不是拟议依赖列表。本报告只描述制品、元数据、许可文本及来源记录的一致性；不判断法律适用性或是否允许发布。

## 制品快照及方法

- ZIP：50,401,654 bytes，SHA-256 `e1e0dae81c362aca6e0900c8a91d6ea07fd53e3a64bf304c68835caf10bb8070`。
- 内含 11 个 wheel。10 个原样上游 wheel 由 `dependencies.lock.json` 描述；第 11 个为本地构建的 `qc_gbasis-0.1.0+qcblender.071969c.pure1-py3-none-any.whl`。
- 对所有 wheel 读取 `METADATA`、`RECORD`、全部以 LICENSE/LICENCE/COPYING/NOTICE/AUTHORS 命名的文件，核对每个 RECORD 数据文件的哈希和大小，并检查声明的 `License-File` 是否实际存在。
- 以已下载固定源码核对 GBasis 和 IOData 的 Python 文件、原始许可文件。未运行依赖安装、联网联系上游、修改锁文件或产品代码。
- 可重跑脚本：[`outputs/audit-bundled-licenses.py`](../../outputs/audit-bundled-licenses.py)。完整文件名、wheel 哈希、原始许可文本、元数据及对比字段：[`outputs/bundled-license-audit.json`](../../outputs/bundled-license-audit.json)。这些 outputs 制品为本地审计证据。

复核命令，工作目录为仓库根目录：

```powershell
& 'C:/Program Files/Blender Foundation/Blender 5.1/5.1/python/bin/python.exe' outputs/audit-bundled-licenses.py
```

## 状态与可修复缺项

|核查项|状态|事实及处置|
|---|---|---|
|11 个 wheel 的 RECORD 内容哈希、大小、文件覆盖|Passed|无哈希错误，无未登记的数据文件；SciPy ZIP 的目录项不属于数据文件。|
|10 个上游 wheel 的版本、规范化包名及 SHA-256|Passed|全部与 `dependencies.lock.json` 一致。下载 URL 与文件名均在该锁文件中。|
|10 个上游 wheel 的依赖声明|Passed|在目标 Windows CPython 3.13 和每个已声明 extra 上语义一致；attrs 的括号/引号、pyparsing 的空格有字符串差异，`importlib_resources` 与锁中的连字符拼法属于名称规范化差异。|
|11 个 wheel 的声明许可文件是否遗漏|Passed|所有 `License-File` 声明均有实体；未声明此字段的 SciPy、pyparsing 也含许可文件。|
|ZIP 的根 LICENSE、THIRD_PARTY、两份锁文件|Passed|均存在且与本次核查时的工作区内容逐字节一致。|
|GBasis 数值 Python 源码是否未经说明修改|Passed|wheel 的 36 个 `.py` 与固定源码逐字节相同；唯一被排除的上游 Python 模块是 `gbasis/integrals/libcint.py`，与构建说明一致。|
|GBasis 是否带 native 代码|Passed|无 `.pyd/.dll/.so/.a`；源码锁只列 GBasis，不含 qcint。|
|GBasis wheel 构建制品是否有随包哈希记录|Passed|实际 wheel 与 `backend-wheel.json` 一致，该记录已随 ZIP 保存；与依赖锁一起覆盖 11 个 wheel。|
|GCC runtime 说明|Passed|THIRD_PARTY 精确区分 GBasis wheel 没有 native runtime，SciPy 原样内含 OpenBLAS 与静态 GCC runtime，并列出 GCC exception。|
|THIRD_PARTY 的 SymPy 许可概括|Passed|表格已写 BSD-3-Clause 及 SymPy wheel 内第三方声明；SymPy 原样 LICENSE 含 latex2sympy MIT 文本并完整保留。|
|GPL/LGPL 上游声明差异的事实记录|Passed|差异确实存在；说明已准确区分 IOData 源码头及元数据、GBasis 上游元数据。该状态不表示上游差异已消除。|
|解决 GPL/LGPL 声明差异、法律适用性及发布许可结论|Not Run|本次没有获取上游澄清或作法律判断。|
|所有二进制的链接对象/作者来源重建|Not Run|审计实际 wheel 文件和其附带清单；没有重新构建 SciPy 或反向重建静态链接内容。|

## 各 wheel 许可材料清单

下列路径均为对应 wheel **内部路径**。各 wheel 的具体下载 URL 与 SHA-256 见审计 JSON/依赖锁，属于本次直接读取的一手制品；链接为其元数据指向的上游项目。

|包及版本|实际许可声明和文本|许可文件位置|文件完整性|
|---|---|---|---|
|[attrs](https://github.com/python-attrs/attrs) 25.3.0|`License-Expression: MIT`|`attrs-25.3.0.dist-info/licenses/LICENSE`|Passed|
|[cclib](https://github.com/cclib/cclib) 1.8.1|BSD 3-Clause 正文和 BSD classifier|`cclib-1.8.1.dist-info/LICENSE`|Passed|
|[importlib_resources](https://github.com/python/importlib_resources) 6.5.2|Apache Software License classifier；Apache 2.0 正文|`importlib_resources-6.5.2.dist-info/LICENSE`|Passed|
|[mpmath](https://github.com/fredrik-johansson/mpmath) 1.3.0|BSD 字段、BSD 三条条件正文|`mpmath-1.3.0.dist-info/LICENSE`|Passed|
|[packaging](https://github.com/pypa/packaging) 25.0|Apache/BSD classifiers；根文本写二选一许可，附两份正文|`packaging-25.0.dist-info/licenses/LICENSE`、`LICENSE.APACHE`、`LICENSE.BSD`|Passed|
|[periodictable](https://github.com/python-periodictable/periodictable) 2.0.2|项目级 Public Domain 声明，同时列出单文件版权/许可证；`cromerman.py` 附 Columbia BSD 三条条件正文|`periodictable-2.0.2.dist-info/LICENSE.txt`|Passed|
|[pyparsing](https://github.com/pyparsing/pyparsing) 3.2.3|MIT classifier 及 MIT 正文|`pyparsing-3.2.3.dist-info/LICENSE`|Passed|
|[GBasis 固定源码](https://github.com/theochem/gbasis/tree/071969c900d6d7a9fbbdfe193c65ba3be177fbdf) `0.1.0+qcblender.071969c.pure1`|METADATA 为 GPL-3.0-or-later；原始 LICENSE 正文为 LGPLv3|`qc_gbasis-0.1.0+qcblender.071969c.pure1.dist-info/licenses/LICENSE`；另有 `gbasis/QCBLENDER_BUILD.md`|Passed，声明差异保留|
|[IOData](https://github.com/theochem/iodata) 1.0.1|METADATA 为 GPL-3.0-or-later；源码头 GPLv3+；原始 LICENSE 正文为 LGPLv3|`qc_iodata-1.0.1.dist-info/licenses/LICENSE.txt`|Passed，声明差异保留|
|[SciPy](https://github.com/scipy/scipy) 1.16.3|SciPy BSD；附 OpenBLAS、LAPACK、GCC runtime 及完整 GCC exception/GPLv3 文本|`scipy-1.16.3.dist-info/LICENSE.txt`；另有 `_pocketfft/LICENSE.md`、`arpack/COPYING`、`qhull_src/COPYING_QHULL.txt`、`_uarray/LICENSE`|Passed|
|[SymPy](https://github.com/sympy/sympy) 1.14.0|BSD 主许可；汇总 Diofant、multipledispatch、PyDy 版权，及 latex2sympy MIT 文本|`sympy-1.14.0.dist-info/licenses/LICENSE`、`AUTHORS`；另有 `sympy/parsing/latex/LICENSE.txt`|Passed|

这张表没有把项目级 Public Domain、BSD 或 GPL 声明扩张成全部内含文件的统一结论。

## IOData 与 GBasis：声明差异和源码证据

IOData 1.0.1 的 wheel `METADATA` 使用 `License-Expression: GPL-3.0-or-later`；82 个随包 Python 文件的头部带 `GNU General Public License` 文字，包含“version 3 or later”的声明。其 `dist-info/licenses/LICENSE.txt` 却是 LGPLv3 正文，且与已下载 [固定 IOData 源码 LICENSE.txt](https://github.com/theochem/iodata/blob/adab5813713ba64641565eb2a8c11803a4e9bba6/LICENSE.txt) 字节相同。已对应到本地源树的 Python 文件没有字节差异。元数据依据可核对[上游 pyproject.toml](https://github.com/theochem/iodata/blob/adab5813713ba64641565eb2a8c11803a4e9bba6/pyproject.toml)，源码头示例为 [fchk.py](https://github.com/theochem/iodata/blob/adab5813713ba64641565eb2a8c11803a4e9bba6/iodata/formats/fchk.py)。

GBasis 的上游 [pyproject.toml](https://github.com/theochem/gbasis/blob/071969c900d6d7a9fbbdfe193c65ba3be177fbdf/pyproject.toml) 用 GPL-3.0-or-later 文本和 classifier；其 [LICENSE](https://github.com/theochem/gbasis/blob/071969c900d6d7a9fbbdfe193c65ba3be177fbdf/LICENSE) 为 LGPLv3，构建后的 wheel 保留同一份原始字节。**该 wheel 的 36 个 `.py` 文件没有 IOData 那样的 GPL 头部**；现有 THIRD_PARTY 已分别陈述 IOData 的元数据和源码头、GBasis 的上游包元数据。

本地 GBasis wheel 的 `METADATA` 由 [`tools/build_science_backend.py`](../../tools/build_science_backend.py) 生成，包含 `GPL-3.0-or-later` 和运行依赖 `numpy>=2.0`、`scipy>=1.13.0`、`importlib_resources`、`sympy`；不应把它称为原样上游 wheel。变更说明 `gbasis/QCBLENDER_BUILD.md` 已随包，准确描述数值 Python 模块未改、排除可选 native wrapper。它给出 commit，但不含来源 URL；ZIP 的 `science-sources.lock.json` 提供固定 URL 和源归档哈希。

源归档 `outputs/m0-research/gbasis.zip` 的实际 SHA-256 为 `42c80656a3a744ad528d69c6cb5a7c805c1278ce3d560f822f8a3ca3848e43d4`，与源码锁一致。GBasis wheel 的实际 SHA-256 为 `ecff898a4c881661ead55c39b5b7e1e007394019d9cc32c21437ce28cf9a494e`，与随包 backend record 一致。

两个 wheel 自带的 LGPL 文件并未独立附一份名为 COPYING3 的 GPL 全文；本次发行 ZIP 根 `LICENSE` 已包含 GPLv3 全文，SciPy 的许可清单中也包含全文。这里仅记录文本存在位置，不判断不同文件之间如何满足许可要求。

## SciPy 内含运行库事实

wheel 有 `scipy.libs/libscipy_openblas-48c358d105077551cc9cc3ba79387ed5.dll`，并有 228 个 `.pyd`。`scipy-1.16.3.dist-info/LICENSE.txt` 直接列出：

- 第 38 行起：OpenBLAS，动态链接 DLL，BSD-3-Clause。
- 第 74 行起：LAPACK，包含于 OpenBLAS，BSD-3-Clause-Open-MPI。
- 第 129 行起：GCC runtime library，静态链接于该 DLL，声明 `GPL-3.0-or-later WITH GCC-exception-3.1`。
- 第 164 行起：GCC Runtime Library Exception 3.1 全文；后面附 GPLv3 全文。

这是原样 SciPy wheel 的一手清单，其文件哈希已与锁记录一致。没有独立 `libgfortran*.dll` 文件，不表示 GCC runtime 没有静态链接进去。当前 THIRD_PARTY 已准确记录 GBasis 无 native runtime、SciPy 原样 wheel 内含该 runtime 的范围。本次没有发现 qcint 或额外 MinGW 运行库文件；也没有通过二进制分析判断清单之外的内容。

## 当前完整性与未决项

1. 此次发现的材料遗漏和不准确说明均已修正，机械材料核验为 Passed。11 个 wheel 的哈希记录、许可证文本和实际源码边界可由随包材料复核。
2. 随包 GBasis backend record 已含版本、wheel 文件名、SHA-256、来源锁关系；运行依赖可在同一 wheel 的 METADATA 复核。
3. IOData/GBasis 的原始许可文本与 GPL 元数据差异仍然存在。对“元数据差异已澄清”的状态保持 Not Run，不把保留原文或机械完整性检查解释为发布许可结论。

本报告只核查上述 SHA-256 指定的制品。重建 ZIP 后应重跑脚本，以新哈希和实际内容验证修正，不能直接沿用本次 Passed 状态。

## 审计修正记录

初次快照 `4cbefb6fd3027ebc088fc2ff7ea736da804af687dd3cbd77686a078d8c3afe16`（50,401,050 bytes）存在 GCC runtime 描述错误、未随包带 GBasis backend record 两项缺项。主任务修正说明及构建流程后，中间快照 `ef351cc4e886e51a3556a9013f53de085f9c256ee1a3c7b06d8a4e3f7ed2dda0` 复核两项 Passed。随后补充 SymPy 第三方声明和 GBasis 声明来源归因，最终快照为本报告首节所列 `e1e0dae8…`；再次完整重跑核查通过。wheel 自身字节未改变。
