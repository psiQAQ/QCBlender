Triage: ready-for-agent
Status: claimed
Blocked by: 01

# 原子身份与有效域

扩展实际节点求值验证，逐点核对源编号、坐标、元素、电荷；补无效域实际覆盖缺口。仅发现实际缺陷才修产品。Blender运行交主Agent串行执行。

## Comments

- 2026-10-11 实现代理领取，前置 01 已 resolved。只维护两个原生验证脚本；产品未修改。

## Answer

实现：`tools/verify_node_helpers.py` 保留 v1 五个固定 socket、标识符复用、math 输入与空选择断言，新增六个非对称源点、原序/交叉/反序输入及非连续元素与范围交集。27 组真实 Geometry Nodes 求值按每个输出点的 `qc_atom_id` 回查位置、元素、电荷、`qc_charge_valid`，并验证缺失电荷属性仍缺失。`--report` 保持兼容，`--output` 是同义参数，`--module` 可指定已安装扩展；JSON 保存逐点证据及实际模块路径，失败写 Failed 并重新抛出异常。

新增 `tools/verify_upstream_validity.py` 复用现有合成场/VDB 与 GN 采样 helper，联系物理零、内部 mask、网格外、有效正值；读取真实图例顶点与材质，使用同一产品材质的现有图例发光支路渲染线性 EXR 并读取像素，同时断言表面 Base Color 使用相同颜色输出。正反转均检查缺失洋红与有效色带颜色；同源剖面经实际 Dataset 导出 CSV/metadata，核对无效留空与来源摘要。合成输入只证明工程行为，不代表独立科研验收。

集成入口：`check(output, module, configure=None)` 的可选回调接收 `(slice_view, material)`，供主 Agent 应用批准的色带预设；回调前后比较 GN 值、mask、fraction，之后完成相同颜色/图例/CSV 检查。CLI 默认验证现有色带，不声明预设入口已经运行。

| 检查 | 状态 | 证据 |
| --- | --- | --- |
| 纯 Python 剖面测试 | Passed | Blender 自带 Python 3.13，复用主仓 `outputs/science`；`-m unittest discover -s tests -p test_science_profile.py -v`，5 tests OK |
| 纯 Python 有效域/范围测试 | Passed | 同环境；`-m unittest discover -s tests -p test_science_field_ranges.py -v`，3 tests OK |
| CSV 无效值导出测试 | Passed | 同环境，PYTHONPATH 额外包含本工作树 tests；`-m unittest test_science_data_export.DataExport.test_profile_invalid_empty_and_imaginary_raw_frequency -v`，1 test OK |
| 两个脚本 AST 与 diff | Passed | `ast.parse`；`git diff --check` |
| 真实 GN、材质渲染与本轮 CSV 集成 | Not Run | 主 Agent 持有唯一 Blender；本代理未启动或连接 Blender |
| 预设回调、GUI、工程冷重开与独立科研接受 | Not Run | 由任务 05/06 集成候选分别验收 |

原生运行前提为隔离 Blender 环境与可用的 QC 科学运行依赖，输出选择新的批次目录。无需真实化学输入。命令由主 Agent 串行执行：

```powershell
& $blender --background --factory-startup --offline-mode --disable-autoexec --python-exit-code 1 --python tools/verify_node_helpers.py -- --module bl_ext.user_default.qcblender --output "$batch/node-helpers.json"
& $blender --background --factory-startup --offline-mode --disable-autoexec --python-exit-code 1 --python tools/verify_upstream_validity.py -- --module bl_ext.user_default.qcblender --output "$batch/validity"
```

预期分别打印 `NODE_HELPERS_PASSED`、`UPSTREAM_VALIDITY_PASSED`，JSON 为 Passed。有效域输出包含两张线性 EXR、GN 属性记录、图例/材质颜色像素、源文件摘要和 profile CSV/metadata。待主 Agent 核实原生运行后再将任务设为 resolved。
