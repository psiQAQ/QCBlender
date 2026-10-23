# 调整局部选择教程表格

Triage: ready-for-agent
Status: resolved

## Acceptance

按网页批注调整分子专题第 4 步表格：按内容分配列宽，第三列表头括号说明移到表后，保持步骤和参数不变，验证桌面和窄屏排版。

## Comments

- 2026-10-23：仅调整原始教程和这张表的专用样式；复用现有网站环境。当前主干新增 Mayer 教程第 6 步，网站库存检查仍是旧计数；核对新增 1 步、1 图和 1 个 details 后同步基线。

## Answer

- Passed：原始教程和专用列宽已调整，A–E 行操作与参数保持不变。英文表头及编号起点移到表后。
- Passed：生产构建及校验（17 页、1132 个内部引用、80 步、29 图、87 个 details、63 个公开文件哈希）。
- Passed：1591×884 桌面排版；390×844 手机视口页面宽度与滚动宽度均为 375px，表格 608px 在 343px 容器内独立滚动，键盘右方向键实际滚动 40px。
- 截图：[桌面](../../../validation/agent/reports/2026-10-23/website/selection-table-desktop.png)、[手机](../../../validation/agent/reports/2026-10-23/website/selection-table-mobile.png)。
- 用户已授权与 Mayer 相关提交一并推送上线；发布结果见 [CI 与部署跟进](03-ci-followup.md)。
