# 局部选择对话框与全局安装
Triage: ready-for-agent
Status: resolved

## 目标
修复当前 Blender 5.1.1 点击设置局部选择不弹窗，并更新当前用户的 Blender 5.1 全局扩展及安装包。保持用户未保存工程、对象与科学数据。

## 验收
在原 PID 13284、P06-single 实例复现；实际按钮点击在记忆 CLEAR、RECOMPUTE、INVERT 后仍打开可选择 Mode 的对话框。独立清除/重新计算入口保持语义；源码、安装包和全局安装字节一致，已有 wheel 与资产保持。GUI 点击、原生回调、安装核对、独立人工验收分别记录。不得启动第二个 Blender 或擅自保存/关闭用户工程，不新增依赖。

## 任务
[01 修复、原生回归与全局安装](issues/01-fix-install.md)

## Answer
原窗口三种记忆模式的真实点击回归、模式与距离控件、4项原子选择测试、102个安装文件及偏好保全 Passed；全局安装与当前ZIP均已更新。当前未保存工程、对象和节点布局保留。完整后台重建、冷重开及独立人工验收 Not Run。验证时源码尚未提交，身份记录保留当时基线及文件摘要。证据见 validation/agent/acceptance/local-selection-dialog.md。
