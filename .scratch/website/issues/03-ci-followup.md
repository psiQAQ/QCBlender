# 修复候选 CI 并部署网站更新

Triage: ready-for-agent
Status: resolved

## Acceptance

按用户授权提交并推送网站表格修改和 Mayer 相关提交；精确 main HEAD 的网站部署成功，并修复仍存在的候选 CI 失败，不绕过门禁。

## Comments

- 2026-10-23：原 3 项断言失败仍可复现，新增 Mayer 产生另 2 项同类失败。真实运行时已加载 translations_output / translations_mayer，旧提示测试仅查 translations_tooltips；菜单预期未包含 apply_output。空场景与普通对象保护通过。修正测试为核对实际合并翻译表和完整菜单顺序。
- 本地定向 8 项与 CI 同入口的 273 项标准库测试 Passed（0 failures/errors/skipped）；证据位于 `validation/agent/reports/2026-10-23/website/ci-followup/`。初次定向调用误填不存在的 test_ui_navigation，已改为实际失败模块 test_empty_button_guards 后重跑；原始失败日志保留。
- `ac3c0ba` 的 Website 构建与部署成功。候选 run `39899032058` 的标准库、科学数值、构建、安装、节点、原位/搬移冷读、公开复现和样本检查均通过；最终资格核验拒绝构建器生成的 4 个中英文节点资产。加入明确的完整资产成员清单，由候选和发布核验共用；补充缺失语言库及安装字节不一致的回归测试，未放宽未知成员拒绝。定向候选/发布测试 Passed。

## Answer

- Passed：网站更新在 `ac3c0ba` 的 [Website run 39899032100](https://github.com/psiQAQ/QCBlender/actions/runs/39899032100) 完成构建与部署；线上新表头、表后说明和两份 CSS 与本地验收构建一致。
- Passed：`93e8b36` 的 [Qualified extension candidate run 39899574889](https://github.com/psiQAQ/QCBlender/actions/runs/39899574889) 完成全部资格验证与候选上传。原 3 项失败、新 Mayer 同类失败及后续发现的多语言资产清单缺口均已修复。
- 本地定向测试：提示/菜单 8 项、候选/发布边界 48 项 Passed；远端完成标准库、科学数值、真实构建、隔离安装、节点、原位和搬移冷读、公开复现、样本及完整包核验。
- 最新远端提交、工作流与 artifact 身份见 [最终状态](../../../validation/agent/reports/2026-10-23/website/ci-followup/final-status.json)。本轮线上浏览器连接超时，保留上一轮桌面/手机截图并实际核对线上 HTML 与 CSS；未冒称新一轮浏览器点击验收。
- Not Run：公开 Release 发布、独立人工/科研验收。本轮没有操作日常 Blender 或覆盖已安装插件；原有研究和子模块改动保留。
