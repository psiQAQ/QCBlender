# M0 科学后端与安装资格验证

Triage: ready-for-agent
Status: resolved
Owner: root
Blocked by: none

## 工作

固定科学依赖及全部传递依赖、来源哈希和许可证；构建兼容 Windows x64 / CPython3.13 / NumPy2.3.4 的后端。取得有来源的 Gaussian FCHK 和独立场参考，验证 AO/MO/密度/自旋/ESP。以扩展原生 ZIP 安装到独立 Blender5.1.1 配置，验证离线加载、后台任务入口及注册/注销。

## 验收

可复现构建/安装命令；真实单轨道与独立参考数值一致；宿主 NumPy/OpenVDB 未被替换；所需 wheels 均来自扩展安装目录。

## Comments

2026-09-22：发行后端改为 qc-gbasis 0.1.0+qcblender.071969c.pure1，只包含现用 Python 数值模块。在全新 outputs/blender-pure-acceptance 配置中离线安装/后台求值/取消/生命周期 Passed，原生绑定不随包分发。相关设计沿革见 docs/CHANGELOG.md；19 项科学回归 Passed。

2026-09-22 M0 关闭：原生离线安装、后台导入/求值/取消、生命周期及重复缓存均 Passed；独立科学参考保持通过。可复现准备、编译、打包与验证命令已写入 `docs/DEVELOPMENT.md`；固定构建工具在 `tools/build-requirements.txt`。当前运行无需外部 Python、编译器或网络。整体首版验收继续由 M1–M5 管理。

2026-09-22 实施证据：

- Passed：GBasis 固定源码编译 CPython3.13 Windows wheel；delvewheel 封装 libquadmath/libgcc/libwinpthread，移除编译器 PATH 后可加载。
- Passed：Blender 原生扩展构建/安装；NumPy2.3.4/OpenVDB 来自宿主，其余科学库来自扩展 `.local`。
- Passed：同一 Blender 可执行文件启动离线后台诊断；GUI 不加载 SciPy/GBasis/IOData；启停扩展无 DLL 清理错误。
- Passed：Gaussian cubegen 密度/ESP 最大误差 8.44e-7 / 4.61e-6；独立 Fortran MO8/9 最大误差 4.85e-9。来自同一 CH4 UHF/cc-pVDZ FCHK。
- Passed：内部数据保存/恢复后重复独立参考；CH3 UHF/ROHF 非零自旋，O2 pure/cart cc-pVTZ 的 CᵀSC 与 Tr(PS) 不变量。
- 运行记录：`outputs/science-reference.json`、`worker-runtime.json`、`extension-lifecycle.json`；独立数据及哈希在 `tests/data/`。
- 当前继续：完整后台导入/求值回传与取消生命周期；构建复现说明。发行对应源码许可材料和完整目标平台干净安装留待 M5。

2026-09-22：由已确认设计路线建立；实施、启动/安装 Blender 和下载公开样例已获用户授权。未授权提交、推送或发布。
