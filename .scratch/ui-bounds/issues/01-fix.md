Triage: ready-for-agent
Status: resolved

# 修复按钮前置条件与数据编号边界

## Comments

- 2026-10-11：原生180项空场景/默认Cube poll与draw审计，唯一失败为直接QC对象菜单访问None。范围审查发现轨道、步、帧、模式、原子、记录行及pair选择缺动态上限。

## Answer

- 空场景直接 QC 对象菜单及科学预检边界已修复；数据相关编号使用实时范围，刷新和冷重开保持约束。
- Passed：162 基础测试、26 相关科学解析、安装后 180 空场景检查、10 属性窗口检查、11 编号窗口/后台检查、共享绑定保存冷读及离线安装资格。
- Passed：Computer Use 实际空场景、轨道边界和 NBO 两步选择；独立人工/科研验收 Not Run。
- 当前 ZIP 已替换，源码 `50f1f3b`，82 产品文件及 11 个原有 wheel 核验；详见 `validation/agent/acceptance/ui-bounds.md` 和本批 `delivery.json`。
