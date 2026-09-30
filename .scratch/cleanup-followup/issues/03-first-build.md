# 修订并复验首次构建

Triage: ready-for-agent
Status: claimed
Type: task
Blocked by: 01, 02

## 目标与验收

- 首次路径：输入检查 → prepare_build → fetch_dependencies → build_science_backend → 隔离科学测试环境 → 科学检查 → 打包 → 安装及专项检查 → evidence-index.json → qualification.json。
- 增量路径显式核对现有环境和 wheels；不隐式读取旧报告或旧工程。
- 给出标准库索引生成示例，核对同批报告状态、摘要及候选身份；保存固定输出位置的报告和每次冷重开日志。
- 在新输出目录复验完整路径；必要样本缺失在输入检查阶段直接阻塞。用户已授权隔离安装固定依赖。
- 先提交被验证文档与测试，再记录准确提交、环境及本轮结果；锁文件无改动。

## Comments

- 2026-09-30：01、02 已 resolved，领取任务。首次/增量路径分开，九个 PowerShell 示例通过语法检查；首次脚本由正文代码块直接提取，不添加构建框架。候选和资格使用本次提交身份。

- 首批 qcf1：104 项输入、首次工具与后端准备、69 项科学回归、11 项单测、节点辅助、离线安装/资产、双冷重开和恢复 Passed。图例命令未打开 MO 前置工程，StopIteration，Failed；完整日志保留在 outputs/qcf1。文档修正为打开同批 mo8.blend，并保留图例阶段 Not Run 快照，仅最终双冷重开 Passed 报告进入资格。科学源码锁重写仅有 CRLF 差异；首次流程增加内容核对后恢复原字节，不改依赖语义。

- qcf2 的首次准备、全部科学/单测/安装/工程检查及图例双冷重开 Passed。资格调用将 .user 下的运行数据目录误作安装源码目录，Failed；现场核对源码实际位于 profile/extensions/user_default/qcblender。修正文档参数及入口存在性检查，保留原始失败收据后继续同批资格，不重复已经通过且未受影响的检查。
