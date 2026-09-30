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
