# 局部选择对话框修复

当前安装包与 Blender 5.1 全局扩展已更新；候选 SHA-256：`58db0ade27053e9e22387e6c92de1acbe6bdfc35ff368244082eab33a3c8f590`。验证时源码基线为 `7b98127`，产品修改尚未提交；current-install.json 的 source_dirty 与 source_file_sha256 保留当时源码身份，不表示当前 Git 工作区状态。

| 检查 | 状态 | 证据 |
| --- | --- | --- |
| 原实例复现 | Failed（修复前） | 原 PID 13284 的 invoke 收到隐式 CLEAR，返回 FINISHED，无对话框；red/dialog.json |
| 原窗口三个记忆模式回归 | Passed | CLEAR、RECOMPUTE、INVERT 后均显式 REPLACE，返回 RUNNING_MODAL；三份 green-*/dialog.json |
| 模式列表、半径与种子控件 | Passed | 原窗口真实点击；distance-controls.jpg、mode-options.jpg |
| 原子选择相关回归 | Passed | 4 项 tests/test_science_atom_selection.py |
| 源码、ZIP、全局安装及既有 wheel | Passed | package.json、global-install.json；83 源码、11 wheel、102 安装文件一致 |
| 未保存工程与布局 | Passed | live-final.json；场景快照相同，原节点编辑器恢复，偏好文件未修改 |
| 完整后台重建、冷重开、独立人工验收 | Not Run | 本次复用字节不变的节点资产与 wheel，保持用户未保存进程 |

证据目录：`validation/agent/reports/2026-10-14/local-selection-dialog/`。旧安装包、全局插件与偏好文件备份保存在 `outputs/runs/local-selection-dialog-20261014/`。没有保存、关闭用户工程或启动第二个 Blender。

“设置局部选择”明确指定 Replace 后打开可切换 Mode 的对话框；独立的“清除局部限制”和“按当前步重新计算”继续执行其指定模式。
