# 2026-09-30 external-results

外部分析结果的导入与来源检查。synthetic PDB属于解析边界数据，真实分析输出与其生成条件须另行保留。

原目录：`outputs/evidence/2026-09-30/history/external-results/`。 2026-09-30是证据迁移日期，原执行日期依下列原报告身份；迁移不构成重新验证。

本摘要记载历史执行结果。历史工程、数组、渲染、安装副本和原始报告的实际可用性，以本批 `validation/agent/reports/2026-10-06/outputs-prune/` 逐文件清单和删除收据为准；摘要不承诺旧二进制仍存在或可以逐字节恢复。

关联工程与运行目录：`outputs/external-results/`。

历史候选、源码提交或执行日期没有在本次可读机器摘要中取得完整绑定，保持未核定；不为目录补造身份。已知开发沿革另见 [CHANGELOG](../../CHANGELOG.md)。

## 结果与条件

已核对的原始专项报告（路径为历史来源身份，文件可能按本批收据退役）：

| 原报告 | 检查与条件 |
| --- | --- |
| `outputs/evidence/2026-09-30/history/external-results/gui.json` | `esp`=Passed；`aim`=Passed；`ets`=Passed |
| `outputs/evidence/2026-09-30/history/external-results/blender-datafiles/qcblender/analyses/17d88045c38f4b11bf001a11bee3a3bf/manifest.json` | `metadata.analysis.spatial_check.margin_angstrom`=10 |
| `outputs/evidence/2026-09-30/history/external-results/blender-datafiles/qcblender/analyses/635f81a79206498785473a0bd33f6f09/manifest.json` | `metadata.analysis.spatial_check.margin_angstrom`=10 |
| `outputs/evidence/2026-09-30/history/external-results/blender-datafiles/qcblender/analyses/ab8620c068bc4fce9a52984f60689de9/manifest.json` | `metadata.analysis.spatial_check.margin_angstrom`=10 |
| `outputs/evidence/2026-09-30/history/external-results/blender-datafiles/qcblender/analyses/dc8c95a11dd54ca483667c8c887e0fd8/manifest.json` | `metadata.analysis.spatial_check.margin_angstrom`=10 |

原报告未提供额外明确的 Failed/Not Run 判定，或本目录仅有运行材料；独立使用者操作、外部视觉对照、科研签署与本次重跑均为 Not Run，不能由上述技术结果代签。

## 当前输入与重建

当前输入从 [validation/shared/data](../../../validation/shared/data/README.md) 进入；本地 key、源文件和旧位置由 `local-inputs.json` 与 `migration-map.json` 定位。Gaussian原始日志、波函数、真实计算checkpoint、计算条件和许可证保留一份；同字节历史副本由逐文件清单确认后退役。

复跑按 [DEVELOPMENT](../../DEVELOPMENT.md) 和 [Agent检查流程](../../../validation/agent/README.md) 准备当前锁定环境与wheels，在新的工作目录从输入生成前置工程，执行相应 `tools/verify_*.py`、科学测试或渲染工具，保存新安装身份、参数和报告。历史源版本仅用于查阅当时设计；重建当前行为须重新资格验证，不运行含旧绝对路径的归档脚本覆盖材料。

本摘要整理未启动Blender、未运行本批产品测试、未重新复算科学输入，状态均为 Not Run。已确认用户工程、今天人工验收目录及未知恢复对象保持保护，历史安装/worker目录不能用来推断用户资产归属。
