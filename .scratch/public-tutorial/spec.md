# QCBlender 公共教程与节点可读性改进

Baseline: 0ae854140846ff8283baec00d61256342d3fecca
Date: 2026-09-30

## 目标与边界

将现有 SOP 扩展为安装插件并取得样本后可跟随的教程，保留 C01-C13/N01-N18，补齐入口、参数、截图引用占位和验收身份。使用 GPT-6.1 SOL / medium 子 Agent 独立工作树并行；主 Agent 串行合并、构建、可见 Blender 操作和收尾。不改变公共接口、九个公共节点资产、科学契约、依赖或锁文件，不 push 或发布。

## 任务与文件归属

01 样本：chore/tutorial-samples，来源记录、输入索引、样本和必要生成/验证脚本。
02 节点：chore/node-layout，graph/views/scalars/atomic_properties/properties 外层布局和专项检查。
03 教程草稿：docs/public-tutorial，SOP/USER_GUIDE/README。
04 教程定稿：依赖 01、03，同教程 Agent；具体参数来自已核验 manifest。
05 综合验证：依赖 02、04，主 Agent。
06 证据与归档：依赖 05，主 Agent。

共享的 AGENTS、spec、CHANGELOG、ARTIFACTS、验证索引由主 Agent 维护。每个 Agent 只领取并更新所属任务文件。三个子分支按样本、节点、教程顺序合入 main；未合入分支 rebase 到当前 main 并复验。协调分支在三个子分支合入后 fast-forward 到 main。

## 样本交接契约

能力组 P01 开壳层轨道；P02 多 Job/振动/NBO；P03 场与外部分析；P04 真实 IRC/Mayer；P05 ETS-NOCV/pair 密度。manifest 逐文件记录样本 ID、规范路径或原站获取步骤、字节数、SHA-256、许可及依据、来源、producer/version、计算条件、用途 C/N、预期值与容差。Job/block/pair、源原子编号、单位、片段和匹配网格必须明确。未知结果不可沿用旧样本常量。

公开包仅包含许可允许分发的文件。其他样本保留原站、许可、获取步骤及摘要；未知许可不得仅靠教学说明加入公开包。自行计算且拥有分发权的数据 CC BY 4.0，第三方保留原许可。必要输入沿用集中 tests/data 规则，不向各工作树复制大型数据。未能取得真实必要材料时记录阻塞，不伪造 Gaussian/NBO/IRC 数据。

## 节点边界

仅对新建外层原子/等值面视图及新增着色/切片/电荷/振动分支添加单层 Frame 和布局。保留已有节点坐标、parent、自定义分支、功能性 label、socket 和 qc_*。不新增子组，不改 assets/asset_library 公共内容或签署。不整理保存工程中的既有全图。

## 验证与证据

使用 Windows / Blender 5.1.1、现有工具及锁定 wheels。新批次输出，不复用旧候选或旧报告。先固定提交，再资格验证并绑定同一候选/输入摘要。可见独立 Blender 进程用 Computer Use 实际点击 C01-C13/N01-N18，MCP只核对数据或记录明确辅助准备。Log -> Job 2 -> 新 FCHK 对话框重置及导入为必查。保存截图、工程、独立冷重开及移动重开证据。

用户实际操作、Agent点击、MCP核对、独立科研签署分别记录；Agent不代签。结果只用 Passed / Failed / Not Run。Computer Use 不可用时 GUI 保持 Not Run，其他工作继续。

## 收尾

本轮精简索引记录源码提交、文件身份、候选与报告摘要、命令、范围、保存及重建路径；保留 cleanup-validation.json 为历史批次引用。索引不引用自身提交。必要产物迁入 outputs/evidence/<日期>/public-tutorial，临时数据 outputs/runs；更新 ARTIFACTS/CHANGELOG，按既有安全策略清理已结束环境和缓存。验收后创建 archive/<日期>/<完整分支名> 注释标签，再正常移除工作树、branch -d。权限或占用阻塞原位保留；主检出保存清理收据和收尾提交。
