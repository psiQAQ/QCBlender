# 保存可复核验证索引

Triage: ready-for-agent
Status: resolved
Type: task
Blocked by: 03, 04

## 目标与验收

- 在 docs/acceptance/cleanup-validation.json 保存唯一精简索引：提交、产品源码树与文件摘要、候选摘要、环境、命令、范围、报告摘要、保存位置和重建方法。
- 上轮证据和本轮复验分别记录；上轮 source-hashes 的 69 个文件已逐项匹配基线提交。
- VALIDATION 引用索引，当前状态不再描述为基线加未提交修改；CHANGELOG 记录本轮变化和保留情况。
- 全部引用可定位；不提交大文件或受限样本，不以历史 Passed 填补本轮 Not Run。

## Comments

- 2026-09-30：索引核对 Passed：固定提交 a7f9b43、69 个产品文件、产品树、候选 ZIP、33 项报告/收据、6 张实际 GUI 截图及 CSV 摘要；上轮 69 文件独立匹配 47fd82c。VALIDATION 引用唯一索引，CHANGELOG 记录追加修复与实际界面检查。归档位置显式等待任务 06 收据核对，不假定已复制。独立科研签署等范围 Not Run。

- 2026-09-30：03、04 均 resolved，领取任务。索引绑定 a7f9b43 及 qcf3，旧批和原始失败另记历史，不继承旧通过状态。

- 2026-09-30：尚未领取；04 仍 pending。独立准备的草稿位于 outputs/cleanup-followup/validation-index-draft.json，实际源码身份在 source-identity.json。69 个受跟踪产品文件（68 个 Python 文件和扩展清单）逐字节匹配 47fd82c、850163e、87b5316，旧 source-hashes 也逐项匹配。草稿已计算候选、22 份资格相关报告/收据及额外证据的摘要，覆盖范围和 Not Run 项分别记录。人工结果及最终归档路径确认后才保存受跟踪索引并改写 VALIDATION。
