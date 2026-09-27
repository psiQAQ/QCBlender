# 源码借鉴技术验收

本记录由 Agent 执行；独立人工验收、外部视觉对照及发布批准为 Not Run。共同开发基线为 `ee9b8d6250a69786711403bbcc28905e10b78846`（main）。参考依据见 [研究记录](../research/source-adoption.md)。各候选和证据独立保存在 `outputs/source-adoption/`，既有候选不覆盖。

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

## 后续批次

| 批次 | 技术验收 |
| --- | --- |
| 03 自动取景 | Not Run |
| 04 线剖面及最终完整 SOP | Not Run |
