# GitHub Actions 运行库下载修复

2026-10-06，失败基线 `da187c866f80bbfed5ef351d219bc850ce666be2`，修复提交 `f8b111549e34b7ad995139d09042ca912661d352`。修复仅涉及 CI 下载工具及标准库回归，产品树保持 `5db4996cbb456f52529c86219d85f0db0541ae49`；Blender 5.1.1、manifest 0.1.0、科学实现及依赖锁不变。

## 原因与修复

[失败运行 37305838293](https://github.com/psiQAQ/QCBlender/actions/runs/37305838293) 在 Fetch official Blender 5.1.1 portable runtime 阶段请求官方 `blender-5.1.1.sha256` 时返回 HTTP 403，尚未进入科学测试和打包。本机相同 urllib 请求也返回 403，响应为 `error code: 1010`；同 URL/出口仅更换为 QCBlender-CI 客户端标识即返回 200，排除了文件名错误及该次出口不可达。

`tools/fetch_ci_blender.py` 为官方校验清单和 ZIP 请求统一设置明确的 `User-Agent: QCBlender-CI (+https://github.com/psiQAQ/QCBlender)`，保留 HTTPS、超时、官方 SHA-256、下载字节核对及安全解包。两个新增回归在真实本地 HTTP 服务器边界执行完整下载流程；布局 fixture 不作为 Blender 安装或科学验证。修复前两个测试因 403 失败，修复后验证清单与 ZIP 请求均成功，篡改 ZIP 在解包前拒绝。

## 验证与候选

| 检查 | 状态与实际范围 |
| --- | --- |
| 原失败复现 | Passed；原请求返回 HTTP 403，响应 1010 |
| 官方请求修复 | Passed；清单和 ZIP 请求 200，ZIP 头为 PK；完整下载由实际 CI 执行 |
| 显式标准库集合 | Passed；129 项、0 failure/error/skip；本地预提交与远端同批分别保存报告 |
| GitHub 完整候选 CI | Passed；[run 37414740265](https://github.com/psiQAQ/QCBlender/actions/runs/37414740265)，push/f8b1115，作业耗时 1 分 55 秒 |
| 公开科学与原生资格 | Passed；67 公开科学、构建、离线安装、注册/注销、节点、原地/移动冷读及 P01/MO9 复现；10 份候选报告均 Passed |
| 下载后身份检查 | Passed；run/workflow/提交、artifact 原始 ZIP 摘要、清单/SHA256SUMS、报告、扩展源码/wheels、公开输入及复现材料 |
| GUI 操作与完整本地科学重跑 | Not Run；本次未改产品，旧批次证据保留原身份，见 Alpha 本地验证 |
| 许可、独立试装、版本标签、草稿及公开发布 | Not Run；本次 push 授权用于 Actions 修复，既定发布门禁单独维护 |

GitHub artifact ID 为 `11390153636`，名称为 `qcblender-candidate-0.1.0-f8b111549e34b7ad995139d09042ca912661d352`。下载的原始 artifact ZIP SHA-256 为 `aa9086a6531c58114bae020592a708bf55473a244ecb5b2223ddb15e29d74bd1`，与 GitHub 元数据一致。

扩展 ZIP 为 50,656,040 字节，SHA-256 `6f25cbaf2df9a41137bfef74abbb7c3b365905370bd70bc77327a9cabeb0dfd8`；样本 ZIP SHA-256 `b4bc3e0ebbdf29ccb3905b16eeb898c94b9f16f209baae3c3ae1a8646b0348dd`。CI 原文件已下载到 `outputs/candidates/current/alpha-ci-0.1.0-f8b1115/`，未重新打包。

原始失败日志、请求探测、成功运行元数据/日志、artifact ZIP 和下载后验证在 `outputs/evidence/2026-10-06/actions-fix/`。成功运行记录位于 `run-37414740265/`；本次脚本/报告保全及本地归档见该目录下的收据。后续选择发布候选时仍需检查该 artifact 未过期，以及精确注释版本标签与候选提交的一致性；本次身份检查没有代替版本标签或人工门禁。
