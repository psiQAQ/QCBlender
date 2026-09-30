# 修订并复验首次构建

Triage: ready-for-agent
Status: resolved
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

- 资格续跑脚本遗漏 candidate 变量，索引生成 Failed；修正任务脚本后 Passed，失败收据位于 outputs/qcf2/failures/index-resume。增量环境在沙箱读取宿主生成的后端 wheel 时访问拒绝，qci1 为 Failed；按既有授权在宿主核对，qci2 为 Passed。均保留真实错误，不修改权限或依赖。

## Answer

Passed：首次路径在新工作树的新 outputs/qcf2 目录完成输入检查、工具/依赖/后端准备、科学测试、打包、离线安装、工程及专项检查、索引和 qualification.json。显式复制并逐项核对 104 项本地输入及锁定依赖缓存；科学后端重新构建，没有复用旧候选、工程或中间报告。必要输入缺失的前置失败检查 Passed，证据 outputs/cleanup-followup/missing-input-preflight.json。

本批科学回归 69/69（failures/errors/skipped 均为 0），四组非科学单测合计 11/11，七种原子选择和固定接口、安装/生命周期、节点资产、原地与中文路径冷重开、恢复、图例及双冷重开均 Passed；日志和独立报告快照保留在 outputs/qcf2。证据索引有 19 项报告/命令收据。增量准备示例也实际执行并通过，见 outputs/qci2/environment-command.json。

最终资格绑定提交 87b5316e95552929bda8f0f7e74129ea84ab49bd；候选 SHA-256 为 48ca845e1d0f7be7bdc1300d962f733c89958fb89add2ff763aee24ebee5c760（50,632,937 字节）。前置检查执行于 850163ec678173df982629cf88d5a9c3d12233b3，随后仅修正文档安装路径和任务记录；最终资格再次逐字节核对相同的产品源码、ZIP、安装副本及锁定 wheels。两个提交之间产品和测试无差异。

实际查看 default、signed-mo 和 moved_cold_open 三张专项渲染，均包含对应场和图例；这是渲染检查，不是 04 的点击操作证据。全量历史 SOP、完整网格收敛实验、性能、GUI 人工点击、独立科研签署和其他平台均 Not Run。
