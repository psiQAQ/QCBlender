# 13 Actions 官方运行库下载失败

Triage: ready-for-agent
Status: resolved
Blocked by: 03, 12

## 工作与验收

定位并修复 run 37305838293 下载 Blender 官方 SHA-256 清单时的 HTTP 403。保持 Windows x64、Blender 5.1.1、科学依赖和锁及严格资格门禁。使用真实失败请求建立复现，验证修复及完整远端候选 CI。用户已授权提交和 push 解决问题；发布标签、草稿与公开批准仍单独维护。

## Comments

2026-10-06：失败提交 da187c8；本机相同 urllib 请求复现 HTTP 403，科学回归/构建尚未开始。按请求头、URL/文件名、网络出口三项假设逐项探测，日志保存在 outputs/evidence/2026-10-06/actions-fix/。

2026-10-06：同 URL/出口探测默认 Python UA 返回 403/error 1010，QCBlender-CI 标识返回 200。为清单和 ZIP 添加明确客户端标识；真实请求清单及 ZIP 头均 200，保留原 SHA-256 和安全解包门禁。两个真实本地 HTTP 下载回归修复前错误 403，修复后与 129 项显式标准库集合一起 Passed（0 skip），含下载字节篡改拒绝。科学代码及全部锁文件未变；完整远端候选验证待运行。

## Answer

Passed：f8b1115 正常 push main 后，run 37414740265 全部候选步骤通过，生成 artifact 11390153636；下载原始 artifact 后核对 GitHub 摘要、run/提交、清单、10 份报告、源码/wheels 及公开材料均 Passed。原失败请求及回归验证闭环完成；报告见 `docs/acceptance/actions-download-fix.md`。版本标签、草稿、公开发布与独立人工门禁 Not Run，留在 09/10。
