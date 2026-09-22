# 开发演进

## 2026-09-22 工程保存与发行材料核查

真实 Blender 保存失败实验发现配套场景索引在失败后被新索引替换，现于异常路径恢复先前索引及对象/体文件引用；首次保存失败删除未提交的新索引。模式/IR/动画及双场色标冷重开分别验收。

发行包携带 GBasis 构建 wheel 记录，覆盖全部 11 个依赖的版本及摘要。随包声明精确区分 GBasis 的纯 Python 路径和 SciPy/OpenBLAS 自带的 GCC runtime 许可文本；依赖材料事实核查单独保存，不把材料齐备当作上游许可矛盾已经消除。

## 2026-09-22 科学后端资格收敛

固定 GBasis 源码的 Python/NumPy 基函数与库仑积分实现通过 CH4 Cubegen/Fortran 独立参考、UHF/ROHF/DFT、矩形 MO、网格收敛与带电远场检查。

同一上游版本的可选 libcint 原生包装器在本机 Windows 高角动量研究中触发 `0xc0000374` 堆损坏，位置为 `CBasis.overlap()`。该路径未被 QCBlender 的 MO、密度或 ESP 求值调用。发行构建改为 `qc-gbasis 0.1.0+qcblender.071969c.pure1`，排除该包装器和 native 代码；原生构建脚本/许可材料保留在忽略的 outputs 中作为实验记录。当前构建无需 C/C++ 编译器。

高角动量纯 Python 的真实水 cc-pV5Z 不变量通过：球/笛卡尔 CᵀSC 最大误差约 7.15e-8 / 6.50e-7；独立 native 积分对照没有通过。产品仍显式拒绝 h 及以上，不能把上述研究写成 h 完整产品资格。
