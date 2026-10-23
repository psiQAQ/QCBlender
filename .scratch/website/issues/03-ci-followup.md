# 修复候选 CI 并部署网站更新

Triage: ready-for-agent
Status: claimed

## Acceptance

按用户授权提交并推送网站表格修改和 Mayer 相关提交；精确 main HEAD 的网站部署成功，并修复仍存在的候选 CI 失败，不绕过门禁。

## Comments

- 2026-10-23：原 3 项断言失败仍可复现，新增 Mayer 产生另 2 项同类失败。真实运行时已加载 translations_output / translations_mayer，旧提示测试仅查 translations_tooltips；菜单预期未包含 apply_output。空场景与普通对象保护通过。修正测试为核对实际合并翻译表和完整菜单顺序。
- 本地定向 8 项与 CI 同入口的 273 项标准库测试 Passed（0 failures/errors/skipped）；证据位于 `validation/agent/reports/2026-10-23/website/ci-followup/`。初次定向调用误填不存在的 test_ui_navigation，已改为实际失败模块 test_empty_button_guards 后重跑；原始失败日志保留。
