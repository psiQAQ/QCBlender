# Gaussian 优化轨迹技术记录

2026-09-27，Windows x64 / Blender 5.1.1，分支 `feat/result-browser`。本页记录 Agent 技术验证；独立人工验收和外部视觉对照仍为 **Not Run**，排在本轮开发之后。ORCA、`.mwfn`、周期体系和新分析类型按后续需求另行立项。

## 使用与边界

导入 Gaussian Log/Out、选择计算段后，通过 **Optimization Trajectory → Create Optimization View** 创建独立轨迹视图；Previous、Next 和 Choose Step 浏览离散构型。面板显示该步能量、收敛值/阈值、计算状态和原文行号，Source Details 中的 Optimization step 提供完整来源。具体操作见[用户指南](USER_GUIDE.md#gaussian-优化轨迹浏览)。

复用 cclib 1.8.1 的构型序列，逐步与 Gaussian 明确打印的步号、orientation 表、原子编号和坐标核对。仅将同一步范围内唯一可选择的目标方法能量关联到该步；缺失或歧义不补值。优化收敛和整个计算的终止状态分别记录，最终重复打印的 orientation 不新增步。

- 当前支持有明确、从 1 开始连续步号的单段优化，最多 10000 步。扫描、重启、QST2/QST3、IRC、ONIOM 和 counterpoise 等路径显示不可用及原因；普通导入仍执行其既有校验。
- 坐标保存为 Å，能量为 Hartree。收敛表保留原文的内部单位声明及行号，各指标未单独打印的单位记为空，不猜测或换算。
- 轨迹视图只携带构型与轨迹记录；最终构型的电荷、偶极、振动和场保留在原视图。默认空间填充显示；球棍连接固定为第 1 步按距离推断的连接。
- 优化步不表示物理时间；没有插值、播放或能量曲线。旧工程可打开，需重新导入原 Log 才能补入逐步数据；不迁移 `.qcdata` 格式。
- 显示切步前检查 manifest 绑定、顶点数、原子编号/元素及所需属性，错误输入在更新几何前拒绝。读取来源详情只加载 metadata，切步按需读取已有数组。

## 独立候选与工程

候选：[qcblender-0.0.1.zip](../outputs/optimization-trajectory/dist/qcblender-0.0.1.zip)，50,450,451 字节。

SHA-256：`04b1fec4736f0f837b68b59e0e687e0aca2507b0f5d3d5a094bbc8b6fc587c8e`。

[候选核对](../outputs/optimization-trajectory/candidate.json)确认 40 个 Python 文件在源码、ZIP 和已安装扩展中逐字节一致。既有 SOP 候选 `outputs/dist/` 和结果浏览候选 `outputs/result-browser/dist/` 的摘要保持不变。本轮没有新增依赖。

- [可查看工程](../outputs/optimization-trajectory/GUI-optimization.blend)及同目录 `GUI-optimization.qcdata/`，保存于第 4 步；两者一起搬移。
- [移动副本](../outputs/optimization-trajectory/gui-moved/GUI-optimization.blend)及同目录配套数据；已由新进程打开并渲染。
- [第 1 步 PNG](../outputs/optimization-trajectory/step-1.png)、[第 4 步 PNG](../outputs/optimization-trajectory/step-4.png)、[冷重开 PNG](../outputs/optimization-trajectory/gui-moved/step-4-reopened.png)。
- [轨迹面板截图](../outputs/optimization-trajectory/gui-final-step4.png)、[当前步来源截图](../outputs/optimization-trajectory/gui-final-source-details.png)。

真实输入沿用 [local-log-downloads.json](../tests/data/local-log-downloads.json) 中 cclib-data 固定提交的 Gaussian 16 `water_neutral_nbo_opt_freq.out`，SHA-256 为 `9493d24655fb261a2c945d292ad517567f3024996594a25f678199df74017519`。优化段含 4 步，后续频率段分别处理。截断、失败状态、缺能量、歧义和身份冲突使用该真实输入的明确修改作为边界测试，不冒充新增真实计算。

## 验证结果

| 检查 | 状态 | 证据与范围 |
| --- | --- | --- |
| 科学回归 | Passed | [science.json](../outputs/optimization-trajectory/science.json)，25/25；新增 4 项覆盖逐步原文、失败/截断、能量歧义、重复/缺失构型、身份变化及持久数据校验 |
| 全新配置离线安装 | Passed | [extension.json](../outputs/optimization-trajectory/offline-ui-final/extension.json)：真实 worker 导入/求值、取消、生命周期、缓存、表面 PNG 和移动冷重开 |
| 轨迹导入与隔离 | Passed | [checks.json](../outputs/optimization-trajectory/verification-final/checks.json)：真实 worker、4 步坐标/能量/来源、独立复制、越界与损坏绑定/原子属性的无部分更新拒绝 |
| 保存与移动冷重开 | Passed | [cold-reopen.json](../outputs/optimization-trajectory/verification-final/cold-reopen.json)：原视图、轨迹及复制层的步号、位置、来源、数组摘要和相对路径 |
| GUI 与 MCP | Passed | [gui-checks.json](../outputs/optimization-trajectory/gui-checks.json)：Computer Use 创建、Next、取消、指定步与来源详情；MCP 逐步数值/数组核对和原生撤销/重做。最终候选复验指定步及窄侧栏文字 |
| GUI 工程冷重开与渲染 | Passed | [gui-cold-reopen.json](../outputs/optimization-trajectory/gui-cold-reopen.json)：新进程打开移动副本，核对第 4 步、科学数组、来源身份并渲染；代表图已检查 |
| 既有结果浏览回归 | Passed | [checks.json](../outputs/optimization-trajectory/result-browser-final/checks.json)及 [cold-reopen.json](../outputs/optimization-trajectory/result-browser-final/cold-reopen.json)：预览、选段、源文件变化拒绝、同名不同源、只读来源、旧工程及 C04/C07–C13 来源兼容 |
| 新候选完整 SOP 重跑 | Not Run | 本轮执行相关回归，未将旧候选完整 C01–C13/N01–N18 证据转记为新候选全量通过 |
| 独立人工验收、VMD/VESTA 外部视觉对照 | Not Run | 后置任务；Agent 技术结果不代签 |

## 复验入口

在仓库根目录使用 PowerShell，保留现有 `outputs/science`、固定样本和构建依赖。下面命令不下载或安装新依赖。每条成功后再执行下一条；重建会产生新 ZIP 摘要，须重新记录。

```powershell
$blender = 'C:/Program Files/Blender Foundation/Blender 5.1/blender.exe'
$blenderPython = 'C:/Program Files/Blender Foundation/Blender 5.1/5.1/python/bin/python.exe'
& $blenderPython -I tools/run_science_tests.py
& $blenderPython -I tools/build_extension.py --blender $blender --output-dir outputs/optimization-trajectory/dist
```

使用新的隔离配置安装候选，再执行实际轨迹导入：

```powershell
$env:BLENDER_USER_RESOURCES = "$PWD/outputs/optimization-trajectory/recheck-profile"
& $blender --background --factory-startup --offline-mode --python-exit-code 1 `
  --python tools/verify_extension.py -- `
  --candidate outputs/optimization-trajectory/dist/qcblender-0.0.1.zip `
  --output-dir outputs/optimization-trajectory/recheck-install
& $blender --background --offline-mode --python-exit-code 1 `
  --python tools/verify_optimization.py -- --output-dir outputs/optimization-trajectory/recheck
& $blender --background outputs/optimization-trajectory/recheck/moved/optimization.blend `
  --offline-mode --python-exit-code 1 --python tools/verify_optimization.py -- `
  --output-dir outputs/optimization-trajectory/recheck --reopen
```

## 评审与修复记录

### Standards

Passed。评审发现切步前未完整校验原子属性/身份及保存时的 manifest 绑定；已集中到切步前置校验和已有来源绑定校验中。实际 Blender 检查证明这类失败保持几何与当前步记录不变，复审关闭两项问题。

### Spec

Passed。范围、科学关联、原视图隔离、数据持久性及后置验收边界符合本轮规格。窄侧栏的收敛值和单位改为分行显示，最终候选经可见窗口确认。

读取旧 C04/C07 工程仍出现既有 Blender `VFont -> Node` 诊断；本轮对应来源读取和冷重开断言通过，未将日志描述为零告警。首次结果浏览回归因沙箱文件读取权限失败，在授权的可读环境重跑通过。
