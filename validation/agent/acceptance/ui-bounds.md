# 空场景按钮与编号范围

日期：2026-10-11。Windows x64 / Blender 5.1.1。产品源码 `50f1f3b1e82a358cd2a4c0e5d3843d1f7cb4186a`，产品树 `ed6e9553d865e55b3a7c5e5433b168b5d99f3bac`。基础测试及保存重开工具提交 `05aa1186901fc01837fb7b8e5224f3004ae30004` 的产品树相同。

没有导入对象时，直接 QC 对象菜单返回空菜单，科学预检按钮按数据前置条件禁用。对象与材质属性入口继续提示先选择对象。轨道编号按当前自旋的源轨道数限制，优化步、XYZ 帧、距离/平面原子、模式/能量索引、外部结果行及显示节点按当前数据限制；来源刷新为旧工程更新范围并归一化过界值。源 Pair 编号和 Last Atom=0 的全部原子语义保持有效。

NOCV 从当前自旋实际存在的 Pair 编号中选择。NBO 首个对话框选择日志并异步检查，随后对话框根据真实 Job/block 数限制输入；无 NBO block 时禁用其选择，日志在检查后变化时拒绝导入。

## 安装交付

当前入口 `validation/shared/install/qcblender-0.1.0.zip`，50,660,488 字节，SHA-256 `dcd413f902e1bbff9495b878a2ab83442dcb2db02bb8e57643b2159fcacfd9c6`。完整候选为 `outputs/candidates/current/ui-bounds-50f1f3b/qcblender-0.1.0.zip`。82 个产品文件与固定源码核验一致，manifest 仅由构建器填写 wheel 清单；11 个 wheel 与上一候选逐字节相同，依赖锁和 backend 记录一致。

报告目录：`validation/agent/reports/2026-10-11/ui-bounds/`；交付身份和报告摘要见 `delivery.json`。旧候选及其报告保留，现存产物由 [ARTIFACTS](../../../docs/ARTIFACTS.md) 定位。

## 验证结果

| 检查 | 状态 | 证据与范围 |
| --- | --- | --- |
| 基础测试 | Passed | `stdlib.json`，162 tests、0 failures/errors/skipped；合入 main 后执行 |
| 相关科学解析 | Passed | `science.json`，Gaussian Log、外部筛选及 NOCV 状态共 26 tests、0 failures/errors/skipped；复用已有安装依赖 |
| 空场景及默认 Cube | Passed | `installed-empty-background.json`，180 项真实 Operator poll 和面板/菜单 draw 检查；draw 使用 layout 记录器 |
| 属性编辑器 | Passed | `installed-properties-window.json`，10 项真实窗口 Operator 回归 |
| 编号及联动 | Passed | `installed-index-background.json`、`installed-index-window.json`，各 11 项真实 RNA 检查；范围元数据为隔离 fixture，不代替科研样本核算 |
| 共享绑定及冷重开 | Passed | `bound-reload.json`，两个共享源绑定分别更新范围、外层节点隔离、Last Atom=0 保留、自包含工程新进程读回 |
| NBO worker 边界 | Passed | `bound-reload.json`，真实日志检查得到各 Job 的 block 数 `[2, 1]`，来源摘要变化拒绝 |
| 离线安装/计算/渲染/保存 | Passed | `extension.json`，实际 worker 导入/求值、缓存、取消、注册/注销、几何与相位更新、归档及中文路径冷读 |
| Computer Use 实际操作 | Passed | `computer-use.json` 和五张原始截图；空场景属性入口与刷新、真实 CH4 轨道编号上下限、NBO 两步选择和 Job/block 联动 |
| 包源码、依赖及 ZIP CRC | Passed | `delivery.json`，源码、wheel、锁文件及交付路径摘要 |
| 完整科学套件 | Not Run | 本次执行 26 项受影响解析测试及实际 MO 安装资格 |
| 独立人工/科研验收 | Not Run | Agent 技术验证不代替独立使用者与科研签署 |

Computer Use 在零对象工程中实际点击“查看对象属性”，看到“请先选择一个对象”，属性页保持且无 traceback。真实 CH4 有 34 个 Alpha 与 34 个 Beta 轨道；输入 1999 和 −25 后分别显示 34 与 1。真实水 NBO 日志有两个 Job，输入 Job 999 后回到 2，其 block 上限同步为 1；输入 block 999 后回到 1。NBO 对话框随后取消，本批鼠标验证没有执行最终 NBO 关联导入。窗口脚本和鼠标操作分别记录。

修复前复现报告 `empty-red-native-ready.json` 为 Failed：直接 QC 菜单对 `None` 调用 `get`。`index-red.json` 记录原编号缺少范围。中间失败报告保留；当前验收使用上述最终 Passed 报告。

## 复验与保留

自包含范围验证工程为 `outputs/runs/ui-bounds/install/qa/bounded.blend` 及同名 `.qcdata/`；实际 MO 工程在该目录的 `moved 中文 path/mo8.blend`。独立配置见 `outputs/runs/ui-bounds/install/environment.json`，保留运行脚本见 `outputs/runs/ui-bounds/scripts/`。每次运行前按 [交互规则](../../../docs/agents/blender-interaction.md)确认无其他 Blender 进程，沿用隔离环境变量，逐个执行：

```powershell
$blender = 'C:/Program Files/Blender Foundation/Blender 5.1/blender.exe'
& $blender --background --factory-startup --offline-mode --disable-autoexec --python-exit-code 1 --python tools/verify_empty_buttons.py -- --module bl_ext.user_default.qcblender --report outputs/runs/ui-bounds-repeat/empty.json --quit
& $blender --factory-startup --offline-mode --disable-autoexec --python-exit-code 1 --python tools/verify_ui_bounds.py -- --module bl_ext.user_default.qcblender --report outputs/runs/ui-bounds-repeat/index.json --quit
```

共享绑定与保存冷读入口为 `tools/verify_bound_ranges.py`，其运行参数见文件内 argparse。构建按 [DEVELOPMENT](../../../docs/DEVELOPMENT.md#打包与离线安装)复用现有 wheels。本批安装环境和验证工程留在主检出；用户截图及 `validation/human/未命名.blend` 保留。三个任务分支的本地快进整合、注释标签及工作树收尾结果见 `closing.json`，不包含远端发布。
