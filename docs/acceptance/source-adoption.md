# 源码借鉴技术验收

> 产物状态更新（2026-09-29）：本页是历史技术验收记录。候选 ZIP、生成工程及图像已纳入用户批准的清理范围；日志、摘要和历史 Passed 保留，二进制可用性以 [清理记录](storage-cleanup.md) 为准。本文中“可重开”“保留候选”等描述只代表验收当时状态。当前可用的用户工程单独保存，后续演示从集中输入重建。

本记录由 Agent 执行；独立人工验收、外部视觉对照及发布批准为 Not Run。共同开发基线为 `ee9b8d6250a69786711403bbcc28905e10b78846`（main）。参考依据见 [研究记录](../research/source-adoption.md)。各候选和证据独立保存在 `outputs/source-adoption/`，既有候选不覆盖。

四批分别具有本地附注技术标签 `qa/source-adoption-20260927-01` 至 `04`；第 04 个指向验收提交 `b2c227c`。四个开发分支均已合入 main，工作树在保全 42 份有效输出并逐文件核对摘要后移除，分支和标签保留。归档清单见 `outputs/source-adoption/worktree-archive/manifest.json`。未推送或发布。

## 01 AIM

状态：**Passed**。源码集成 `1e1ea10`；资格检查源码提交 `03d5c19`。候选 `01-aim/dist/qcblender-0.0.1.zip`，SHA-256 `09d7c3b4ea99fe3d9f114bf3576cd91111c8c8dca19396e6782debff7b809000`。安装在 `01-aim/profile/extensions/user_default/qcblender`，Windows x64 / Blender 5.1.1 / 简体中文。

| 检查 | 状态 | 证据（相对批次目录） |
| --- | --- | --- |
| 源码、ZIP、安装副本、锁定 wheels | Passed | `qualification.json`、`evidence-index.json` |
| 科学回归 30/30 | Passed | `science.json` |
| 干净配置安装、worker、等值面、取消、保存及移动冷重开 | Passed | `offline/extension.json` |
| C09 59 CP、58 路径、59 条属性；冲突拒绝且场景不变 | Passed | `C09/aim.json` |
| 缺字段兼容及未核验诊断 | Passed | `C09/aim.json`、`GUI-diagnostics.png` |
| 点/路径显示切换渲染；保存与移动冷重开后数组及来源身份 | Passed | `C09/C09*.png`、`C09/C09.blend`、`C09/moved/`、`C09/aim.json` |
| GUI 按钮、三路径对话框、属性面板、错误提示、撤销/重做 | Passed | `gui.json`、`gui-undo.json`、`GUI-properties.png`、`GUI-type-error.png`、`GUI.blend` |

GUI 动作用 Computer Use 完成；重复导入、计数、数组摘要及便携保存用 MCP 或安装扩展的 Blender 脚本核对。Computer Use 发送 Ctrl+Shift+Z 未触发重做，改用原生 Edit > Redo 菜单恢复全部 59 CP；没有据此修改插件。缺字段诊断在窄面板中会截断，完整文本保存在 `gui.json`。

纯 Python 检查发现并修复同一 CP 重复字段覆盖错误值，以及无冒号坐标标签未被拒绝的问题，见任务 01 的复现与提交记录。

## 02 ETS-NOCV

状态：**Passed**。源码集成 `467798a`；资格检查源码提交 `f55710a`。候选 `02-nocv/dist/qcblender-0.0.1.zip`，SHA-256 `1373325a0a0306b5281668f6de947937ea0e47d8ad7737f4141bf4bf1ceb0650`。安装在 `02-nocv/profile/extensions/user_default/qcblender`。

| 检查 | 状态 | 证据（相对批次目录） |
| --- | --- | --- |
| 源码/ZIP/安装副本/wheels；科学回归 36/36 | Passed | `qualification.json`、`science.json` |
| 干净配置安装、worker、渲染及移动冷重开 | Passed | `offline/extension.json` |
| 真实九对；pair1 -77.88 kcal/mol；占位、零值及单位分支 | Passed | `C12-C13/nocv.json` |
| 错误表导入不增对象；错误 pair/自旋拒绝 | Passed | `C12-C13/nocv.json` |
| C13 源 Cube 数组、相位/阈值 PNG；原地/移动新进程重开 | Passed | `C12-C13/C13-*.png`、`C12-C13/C12-C13.blend`、`C12-C13/moved/` |
| GUI 表/Cube 导入、可读属性面板及占位错误提示 | Passed | `gui.json`、`GUI-pairs.png`、`GUI-field.png`、`GUI-placeholder-error.png`、`GUI.blend` |

评审修复了较早的“未计算”声明识别、多个单位声明冲突，以及单位注释清除同一表未计算状态的问题。全部场景在修复后候选复验。GUI 使用 Computer Use；路径预填、来源核对和保存用 MCP；独立进程脚本验证数值与冷重开。

## 03 自动取景

第三批 **03 自动取景 Passed**，源码集成 `63080f2`、UI `8593411`，资格检查提交 `8924b74`。候选 `03-camera/dist/qcblender-0.0.1.zip`，SHA-256 `f48c53e7de332994bf7cd226b4301ed6b08e1c996d0971e1f826e9038b55e603`；安装路径 `03-camera/profile/extensions/user_default/qcblender`。

`03-camera/qualification.json` 核对源码、ZIP、安装副本和 wheels；`science.json` 40/40 Passed；`offline/extension.json` 干净安装及离线回归 Passed。`framing/camera.json` 和逐场景 PNG 记录原子、等值面、雾、多视图、变换、横竖画幅及像素比例的原生投影检查，全部顶点在默认 5% 边距内；隐藏对象及内部源排除、旧相机/灯光/变换保留。空几何与不一致的修改器开关明确拒绝。`framing/camera.blend` 及 `framing/moved/` 分别在新进程重开并渲染，相机和数组身份保持一致。`gui.json`、`GUI-camera.png`、`GUI-camera-error.png` 保存 Computer Use 按钮/撤销/错误提示，以及 MCP 重做和状态核对的证据。

## 04 线剖面与最终完整 SOP

状态：**Passed**。D 集成 `64ace83`、配对字段来源修复 `8e0e022`；最终产品源码提交 `268dfaadcc1dec14e85ff23d4314c0d63b5b77ac`。候选为 `outputs/source-adoption/04-profile/dist/qcblender-0.0.1.zip`，50,459,351 字节，SHA-256 `52e485b4c4b6df4afc02b372d8ed18e6622f45dc931ba9bd210f583d3b02139c`。安装在同批 `profile/extensions/user_default/qcblender`。

| 检查 | 状态 | 证据（相对 `04-profile/`） |
| --- | --- | --- |
| 45/45 科学回归，源码/ZIP/安装副本和锁定 wheels 一致 | Passed | `science.json`、`qualification.json`、`evidence-index.json` |
| 全新配置离线安装、运行库、worker、取消、缓存及工程迁移 | Passed | `offline/extension.json` |
| A/B/C 在最终安装包上的功能及原地/移动冷重开回归 | Passed | `regression/aim/aim.json`、`regression/nocv/nocv.json`、`regression/camera/camera.json` |
| 解析斜轴场、真实 MO、几何/色场、端点和源坐标距离 | Passed | `line/profile.json`；MO 31 点最大误差 2.50e-16，世界缩放后源距离保持 6 Å |
| 无效区域断线、CSV 留空、错误输入不增加对象 | Passed | `line/profile.json`、`line/profile-gaps.png`；五点掩码 TTFTT 生成两个独立线段 |
| 复制独立、移动仅改变排版、两次冷重开后 CSV 逐字节一致 | Passed | `line/profile.blend`、`line/moved/`、`line/profile.json` |
| 真实 IGMH 几何场/色场来源身份、101 点、9.979805946 Å | Passed | `paired-profile/paired.json`、`paired-profile/paired.blend`、`paired-profile/color.csv`、`paired-profile/geometry.csv` |
| 新 GUI、来源详情、Ctrl+Z、MCP 原生重做、配对场两次冷重开 | Passed | `gui.json`、`paired-profile/undo.json`、`paired-profile/saved.json`、`paired-profile/moved.json`、`paired-profile/GUI-*.png` |
| 35 个 SOP 源文件摘要 | Passed | `final-sop/replay/source-check.json` |
| C01–C13 六栏与 N01–N18 | Passed | `final-sop/final-sop-summary.json`、`final-sop/final-sop-summary.md` |

Computer Use 实际确认了 Color 选择、101 点创建、来源详情、撤销和记录面板；已确认且未变化的入口按用户约定用 MCP 重复操作。数值、节点、数组摘要和保存由 MCP/安装扩展脚本验证。最终 SOP 为当前候选重新执行，工程在两个独立新 Blender 进程中分别原地打开和移动打开并渲染，共 26 次；同一案例两个 PID 不同，不要求操作系统在不同案例间永不复用 PID。

先在空配置完成安装检查，再复用通过源数据、网格、参数、求值器和运行库身份核验的数值场缓存，清单为 `cache-reuse.json`。当前候选的导入、视图/节点、渲染、保存及冷重开均实际重新执行。

真实配对场的 COLOR 剖面记录 `sl2r.cub`，SHA-256 为 `ec9afd0600e60144281a5ba9e6fdae626dbe9f6d5f180702d28c75053a214514`；几何剖面记录 `dg_inter.cub`，SHA-256 为 `3d8c044dbbac7a08f18f7bb6a4fa1a71628157c24d3b781bcb0da993bcc99695`。两个来源在 Source Details、复制、撤销/重做及移动冷重开后保持正确。

## 最终候选技术 SOP 矩阵

各例证据位于 `04-profile/final-sop/cases/CNN/`：`CNN.png`、`CNN.blend`、`CNN.qcdata/`、源值/节点报告、`saved-final.json`、`candidate-run.json` 和两次重开报告。移动副本在 `04-profile/final-sop/moved/CNN/`。C06、C08、C09、C11、C12 的固定 PNG 包含实际可读面板；另存纯渲染图。具体节点前后值和逐项证据映射见本地完整矩阵（`outputs/source-adoption/04-profile/final-sop/final-sop-summary.md`）。

| 案例 | 导入 | 源数值/单位 | 节点前后 | PNG | 保存重开 | 移动冷重开 | 关键实测 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| C01 | Passed | Passed | Passed | Passed | Passed | Passed | 20 原子、69 电子；总/自旋密度恒等式误差 2.49e-14；FCH 别名一致 |
| C02 | Passed | Passed | Passed | Passed | Passed | Passed | 27 原子坐标最大差 4.99e-7 Å；54 模式，45 号 3396.4292 cm^-1、98.3271 km/mol |
| C03 | Passed | Passed | Passed | Passed | Passed | Passed | Cube/CUB 相同；100×sign(λ₂)ρ 倍率明确；同网格颜色误差 3.72e-7 |
| C04 | Passed | Passed | Passed | Passed | Passed | Passed | E=-673.5905711573 Eh；ESP/密度、原子电荷、Debye 偶极及无效域核对 |
| C05 | Passed | Passed | Passed | Passed | Passed | Passed | 原子显隐 20→10→11（保留 H6）→20；复制层独立 |
| C06 | Passed | Passed | Passed | Passed | Passed | Passed | job2/block1；7 NBO、2 E(2)，原文行与 LOG 别名一致 |
| C07 | Passed | Passed | Passed | Passed | Passed | Passed | IGMH/IRI 各 122×66×66；48,312 散点；错误网格拒绝 |
| C08 | Passed | Passed | Passed | Passed | Passed | Passed | 19 极值逐项核对 PDB；40 面积分箱，总面积 228.2405 Å² |
| C09 | Passed | Passed | Passed | Passed | Passed | Passed | 59 CP、58 路径、59 属性；CP 类型和坐标关联通过 |
| C10 | Passed | Passed | Passed | Passed | Passed | Passed | 真实 3 步 IRC，逐步 FCHK 构型/能量和游标一致；坏步号/原子拒绝 |
| C11 | Passed | Passed | Passed | Passed | Passed | Passed | 3 步×6 原子对 Mayer；切步/切对/撤销通过；缺步与原子对冲突拒绝 |
| C12 | Passed | Passed | Passed | Passed | Passed | Passed | 9 行×8 数值列与原文一致；pair1 Total -77.88 kcal/mol |
| C13 | Passed | Passed | Passed | Passed | Passed | Passed | pair1 Total Cube 数组一致；独立正负阈值；错误 pair/自旋拒绝 |

N01–N18 **全部 Passed**。检查涵盖原子选择/三种样式、氢显隐、双相/三种表面样式、独立阈值/透明度、同网格/异网格采样、颜色与图例、切片、平面/盒裁剪、雾、偶极、振动/IR、分析点、散点、显示层复制/排序/显隐/删除、撤销/重做、游标有效域与工程迁移。完整矩阵逐项保存“原值→新值→可见变化”，关联源数组保持不变。

## 缺陷处理与证据范围

最终验收修复了无节点图的记录/曲线视图误报缺失 QC graph 的问题：仅对预期含 Geometry Nodes 的视图显示图控件，真实缺失图仍明确报错。修复提交 `2ed78f0`、`268dfaa`；最终包重建、重装后重新执行专项、科学回归、干净安装及完整 SOP。先前候选保存在 `04-profile/prior-r1/` 和 `prior-r2/`，其报告不计入最终候选通过结果。

Blender 5.1.1 冷重开 String to Curves 时可能输出 `VFont -> Node` 依赖图警告。无 QCBlender、无其他扩展的 factory 配置亦可复现，原生文本仍求值得到 1,200 顶点/1,176 面；本轮图例、渲染和冷重开检查通过。复现和限制记录在 `04-profile/native-font/diagnosis.json`，不据此声称已修复 Blender 本身。

固定 SOP、结果浏览、优化轨迹三个既有候选及证据继续保留。独立人工签署、外部视觉对照和发布批准仍为 **Not Run**。
