# 空场景属性入口修复

日期：2026-10-10。Blender 5.1.1 / Windows x64。产品源码提交 `2989bd63377a71627d509f8febfde5591cd609c2`，产品树 `ca6c8e5600ae90fe44d3001baf4a84713e3b9548`。

没有活动对象时，`OBJECT` 不在属性编辑器的动态 RNA 枚举中。对象和材质属性入口现在先检查活动对象，缺失时报告“请先选择一个对象”并返回 CANCELLED，保持属性编辑器原有上下文与固定状态。

## 当前安装包

`validation/shared/install/qcblender-0.1.0.zip`：50,656,108 字节，SHA-256 `988048e2e8fa15cf891b7538c00b5d607eb9f791fbb6d09287c7da1b322c371e`。候选副本为 `outputs/candidates/current/empty-properties-2989bd6/qcblender-0.1.0.zip`，当前身份见 [current-install.json](../current-install.json)。

从当前源码通过 `tools/build_extension.py` 重建，79 个产品文件与工作树逐字节一致；manifest 由构建器填写 wheel 列表。11 个 wheel 与上一份 CI 候选逐字节相同，依赖和科学源码锁内容不变。构建时共用 GBasis wheel 读取被拒绝，使用已核验的旧安装包内 wheel 及其原始 backend-wheel 记录；不改动共用环境或依赖版本。旧候选保持在 `outputs/candidates/current/alpha-ci-0.1.0-190e11e/`。

## 验证

本批机器报告在 `validation/agent/reports/2026-10-10/empty-properties/`；交付收据为 `delivery.json`。

| 检查 | 状态 | 证据与范围 |
| --- | --- | --- |
| 原错误复现 | Passed | `gui-red.json`，窗口进程产生与用户相同的 TypeError；后台模式未触发动态上下文限制 |
| 修复后原生窗口回归 | Passed | `gui-green.json`，10 项检查：空场景对象/材质、渲染/输出、有对象、无材质、已有固定对象、无活动对象、无属性编辑器 |
| 安装后窗口及后台回归 | Passed | `installed-window.json`、`installed-background.json`，各 10 项，加载隔离安装的真实扩展 |
| 基础测试 | Passed | `stdlib.json`，152 tests、0 failures/errors/skipped |
| 离线安装/真实计算/渲染/保存/冷重开 | Passed | `extension.json`，实际 worker 导入/求值、缓存、取消、注册/注销、渲染、归档及中文路径冷读 |
| 包内容与替换摘要 | Passed | `delivery.json`，源码、wheel、ZIP CRC 与交付路径摘要核验 |
| Computer Use 鼠标点击 | Not Run | helper 连续返回 `Computer Use helper already has an active request`；轻量重试及重置 JS kernel 后仍失败，无成功点击记录 |
| 独立人工验收 | Not Run | Agent 检查不代替使用者验收 |

安装资格脚本来自主检出 `9653d12`，其报告的 `source_commit` 表示脚本检出；实际被测代码从新 ZIP 安装加载，ZIP 摘要和产品成员另由交付收据绑定到 `2989bd6`。原生窗口脚本在窗口进程中调用真实 Operator，并非鼠标点击。Computer Use 操作登记表不新增成功记录。

验证工程及配套科学数据保留在 `outputs/runs/empty-properties/install/qa/`。用户原 Blender 会话由用户自行关闭；本批隔离 GUI 进程均已退出，用户安装目录未修改。

## 复验命令

在仓库根目录 PowerShell 中，先确认没有其他 Blender 进程。以下命令验证源码，窗口模式由 timer 等待 GUI 初始化并主动 redraw：

```powershell
$blender = 'C:/Program Files/Blender Foundation/Blender 5.1/blender.exe'
& $blender --factory-startup --offline-mode --disable-autoexec --python tools/verify_open_properties.py -- --report outputs/runs/empty-properties-repeat/window.json --quit
```

已安装隔离候选时，沿用对应 `BLENDER_USER_RESOURCES`、`BLENDER_USER_CONFIG`、`BLENDER_USER_EXTENSIONS` 与 `BLENDER_USER_DATAFILES`，附加 `--module bl_ext.user_default.qcblender`。脚本报告必须为 Passed；GUI 进程退出码不能单独充当验收结果。

构建复用现有环境和 wheels，按 [DEVELOPMENT](../../../docs/DEVELOPMENT.md#打包与离线安装) 执行；当前共用 wheel 的权限限制及同版本 ZIP 字节差异以本节构建说明为准。没有新增或更新依赖。
