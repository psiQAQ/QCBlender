# 01 修复与安装
Triage: ready-for-agent
Status: resolved

## Comments
原 PID 13284，未保存工程 P06-single；实际点击进入 invoke，Mode=CLEAR、mode_explicit=false，直接返回 FINISHED。失败检查 outputs/runs/local-selection-dialog-20261014/assert_dialog.py 已执行并返回 1。证据：validation/agent/reports/2026-10-14/local-selection-dialog/initial-state.json、red-event.json。

## Answer
原窗口三种记忆模式的真实点击回归、模式与距离控件、4项原子选择测试、102个安装文件及偏好保全 Passed；全局安装与当前ZIP均已更新。当前未保存工程、对象和节点布局保留。完整后台重建、冷重开及独立人工验收 Not Run。验证时源码尚未提交，身份记录保留当时基线及文件摘要。证据见 validation/agent/acceptance/local-selection-dialog.md。
