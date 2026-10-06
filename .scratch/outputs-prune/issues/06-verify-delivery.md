# 06 整合验证与本地交付

Triage: ready-for-agent
Status: resolved
Blocked by: 05
Owner: main agent

## Scope

运行清理后基础/科学测试和真实离线打包、安装、生成、保存重开；核对当前引用、文档路由、保护对象和用户原有修改。更新维护规则、ARTIFACTS、CHANGELOG，保全子任务证据，创建注释归档标签并正常移除本批工作树与分支。

## Acceptance

实际检查按 Passed/Failed/Not Run 记录，未处理文件与原因完整交付；main 含已验证本地提交，原有三处修改保留，无 push。历史产物可用性由新摘要和退役清单统一说明。

## Answer

Passed：151项基础测试、124项完整科学测试、5项重建入口测试；真实离线构建/安装、MO8与MO9生成、摘要/渲染、保存及中文路径冷重开；外部计算入口、复杂输入、节点布局与NOCV有符号Cube关联/保存/冷重开。NOCV检查显式使用候选节点资产，先前缺资产失败和成功复验分别留存。产品源码与依赖锁未变。

Passed：5,500个保护摘要、210个补充保护对象、用户工程11个原数组读回、最终删除/剩余文件对账；当前候选及集中输入保持一致。权限受限的5,039文件/739,869,148字节原位保留，retry脚本与准确命令已交付并使用自有样本验证身份保护。GUI点击、真实NOCV科研样本、checkpoint复算与独立人工/科研签署为Not Run。

历史归纳为67份Markdown；维护规则、ARTIFACTS和CHANGELOG已统一当前状态。原有三处未提交修改由精确diff核对保留。最终本地快进提交、注释归档标签、工作树/分支及任务临时副本处置以validation/agent/reports/2026-10-06/outputs-prune/delivery.json为准；无push。
