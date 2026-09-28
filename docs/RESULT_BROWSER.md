# 结果浏览开发候选技术记录

> 产物状态更新（2026-09-29）：本页是历史技术验收记录。候选 ZIP、生成工程及图像已纳入用户批准的清理范围；日志、摘要和历史 Passed 保留，二进制可用性以 [清理记录](acceptance/storage-cleanup.md) 为准。本文中“可重开”“保留候选”等描述只代表验收当时状态。当前可用的用户工程单独保存，后续演示从集中输入重建。

2026-09-27，Windows x64 / Blender 5.1.1，开发分支 `feat/result-browser`，工作目录 `D:\workspace\QCBlender`。Gaussian 计算段选择、按来源分组及只读详情已通过本轮 Agent 技术验证；独立人工验收和发布批准为 **Not Run**。

## 候选与操作

安装独立候选 `outputs/result-browser/dist/qcblender-0.0.1.zip`，SHA-256：

`239cd7c447a2d4caec07646d4d3fdad832f1b5f1b6d5fc9b3c0a33e0bc8539c7`

GUI 导入 Log/Out 后等待预览，选择计算段并确认；每段保留状态、route、原文行区间和能量摘要。失败、未完成或缺少显式几何会如实显示，实际导入继续完整校验。预览不创建 Dataset 或对象，确认时重新核对源摘要。显式脚本段号导入以及 FCHK/Cube 导入保持兼容。

**Display Layers → Refresh Sources / Source Details** 提供来源分组和只读记录。**Source record** 选择几何、计算段、量/单位、着色或外部关联记录；计算段编号从 1 开始。分组身份使用完整源摘要与计算段，组内上下排序保持可见顺序；IR 谱图和偶极通过父原子对象关联。着色源沿实际节点采样连接查找。旧工程不迁移格式，缺失信息显示“未记录”，损坏关联明确显示错误。操作细节见[使用指南](USER_GUIDE.md)。

固定 SOP 候选 `outputs/dist/qcblender-0.0.1.zip` 保持不变，SHA-256 为 `03311fdeb0c83a38a546ebddedee1fe05e8dcb7260b53c889dd9fee3fa7ee231`；旧人工验收证据未覆盖。

## 验证结果

以下路径均相对仓库根目录，完整本地证据在 `outputs/result-browser/`。

| 检查 | 结果 | 证据 |
| --- | --- | --- |
| 主分支工具登记、参考源码固定、路线更新 | Passed | `6691533`、`2f98c39`、`690f9d5` |
| 7 份研究记录迁移、原文摘要不变 | Passed | `maintenance/preservation.json`、`final-receipt.json` |
| 工作树及研究分支移除，9 个独有不可达对象定向清理，Git 无损坏 | Passed | `maintenance/retirement.json`、`git-fsck.log` |
| VTK 固定提交及稀疏/部分克隆保留 | Passed | `submodules/VTK`：`23f0a095621e91bbdbeace8451e22b950c8e5f46` |
| 真实两段 Log 预览、选择与直接解析一致 | Passed | `verification-final-role/checks.json`、`gui-checks.json` |
| 失败/未完成/无显式几何、源摘要变化拒绝 | Passed | `result-browser-science-final.log`、`verification-final-role/checks.json` |
| GUI 选择、取消、能量摘要与来源记录切换 | Passed | `gui-preview-second.png`、`gui-preview-final.png`、`gui-source-final.png`、`gui-calculation-final.png` |
| 同源多视图、同名异源、不同段、谱图父对象、缺失/畸形关联 | Passed | `verification-final-role/checks.json` |
| C04、C07–C13 的几何/着色/外部来源兼容与断链提示 | Passed | `verification-final-role/checks.json`、`gui-external-records.png`、`gui-color-source.png` |
| 元数据按需读取，不加载科学数组 | Passed | `tools/verify_result_browser.py` 对 `numpy.load` 的隔离边界检查 |
| 复制独立节点、显隐、组内排序、撤销/重做，数组摘要不变 | Passed | `lifecycle.json` |
| 保存、移动后新进程冷重开，来源身份和数组不变 | Passed | `verification-final-role/cold-reopen.json`、`gui-cold-reopen.json` |
| 科学回归、中文材质检查 | Passed | 21/21；`science-reference.json`、`result-browser-localized-final.log` |
| 最终候选全新配置离线安装、worker、场求值、渲染和冷重开 | Passed | `offline-final-role/extension.json`、`offline-final-role/mo8.png` |
| 源码、ZIP 和安装目录一致，旧候选摘要不变 | Passed | `final-receipt.json`，38 个 Python 文件逐字节一致 |
| 独立人工签署、发布批准 | Not Run | 继续由用户单独维护 |

Computer Use 完成真实导入确认、计算段下拉选择/取消、来源详情与记录切换；MCP 负责重复调用、数值比较、节点/关联核对、复制与撤销重做。源样本是已登记的 `outputs/log-examples/water_neutral_nbo_opt_freq.out`；第二段原文第 1091–1726 行，唯一目标能量为 -74.9659011806 Hartree。

可重开的工程包括 `GUI-result-browser.blend` 与配套 `.qcdata/`、`gui-moved/`、`verification-final-role/moved/sources.blend` 和 `offline-final-role/moved 中文 path/mo8.blend`。GUI 的复制对象可独立编辑；完整科学数组保存在配套目录。

## 复现命令

在仓库根目录使用 PowerShell，复用已有科学依赖与 wheels，不安装依赖。为重跑选择新的输出目录，保留现有证据。

```powershell
$blender = 'C:/Program Files/Blender Foundation/Blender 5.1/blender.exe'
python tools/build_extension.py --blender $blender --output-dir outputs/result-browser/dist
$env:BLENDER_USER_RESOURCES = 'D:/workspace/QCBlender/outputs/result-browser/recheck-profile'
& $blender --background --offline-mode --python-exit-code 1 --python tools/verify_result_browser.py -- --output-dir outputs/result-browser/recheck
& $blender --background outputs/result-browser/recheck/moved/sources.blend --offline-mode --python-exit-code 1 --python tools/verify_result_browser.py -- --output-dir outputs/result-browser/recheck --reopen
```

安装回归使用 `tools/verify_extension.py -- --candidate <新ZIP> --output-dir <新目录>`；冷重开该目录下的 `moved 中文 path/mo8.blend` 时传相同 `--output-dir` 和 `--reopen`。科学回归为 Blender 自带 Python 执行 `tools/run_science_tests.py`。

## 评审与修复记录

### Standards

着色源按实际采样节点追踪，manifest 及对象 JSON 的嵌套结构在读取边界校验。畸形记录返回清晰错误；来源读取不加载数组。最终只读复核无残留阻断项。

### Spec

外部分析单位、旧工程未刷新及关联丢失时的保守分组均已覆盖。IR/偶极父对象来源和分条详情符合既定范围。最终只读复核无残留阻断项。

GUI 复验修复了 Blender 动态枚举回调不能保存 Python 实例属性的问题，枚举字符串由模块缓存保留；IGMH/IRI 合并数据集的着色文件名按字段角色读取 `analysis.color_source`，并核对真实摘要。开发期失败日志与最终通过记录分别保留；最终候选未发现未解决的本轮缺陷。

旧工程重开仍可能产生 Blender 的 `VFont -> Node` 关系诊断，旧 SOP 重开日志亦有该诊断；本轮来源操作和数据断言通过。技术通过不等于日志完全无诊断，也不替代完整 SOP 的独立人工复做。
