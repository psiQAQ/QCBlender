# 日常开发流程

在已授权实施的任务中使用本页；任务目标和状态仍在 `.scratch/`，当前安装身份仍由 `validation/agent/current-install.json` 维护，产物仍从 [ARTIFACTS](../ARTIFACTS.md) 查找。统一入口负责调用现有工具、查询和留下必要执行收据，不建立另一套任务或验收状态。

## 1. 查询现有操作，确定改动范围

在任务工作树根目录运行 `python -m tools.dev_workflow --help`。使用已准备的目标 Python；环境缺依赖时报告缺项，安装仍须用户授权。

```powershell
python -m tools.dev_workflow query "annotation"
python -m tools.dev_workflow plan --kind geometry --base main --module test_annotation_geometry
```

`query` 按关键词返回操作 ID、适用身份及证据指针，再按需读取命中的记录；不把登记表全文输出到对话，脚本本地读取并筛选。`plan` 按改动类型生成建议，人工结合 diff 确认影响范围。类型为 `docs / logic / geometry / ui / install`；参数及实际工具映射以各子命令 `--help` 为准。

只改文档时检查受影响链接、材料与 diff。产品改动先选已有定向测试及一个实际相关案例；新增测试用于原缺陷或新的行为边界。修改通用接口、依赖或科学定义时才扩大到受影响集合。已有测试和历史验收资产继续保留。

完成条件：任务写明目标行为、受影响入口、定向测试和实际案例；需要 Computer Use 的步骤有具体变化依据。

## 2. 实施并定向验证

```powershell
$run = 'outputs/runs/my-task/1'
python -m tools.dev_workflow --run-dir $run check --module test_annotation_geometry
```

批次使用短且未占用的路径；同一条检查失败后根据真实错误修复，重试参数查 `check --help`。命令输出默认给出状态、关键结果和报告路径，完整日志按需读取；不为包装命令而每批复制 bootstrap、快照或安装脚本。

测试结果的复用条件是：对应源码、测试/输入、运行环境和所绑定候选身份相同，原报告可读取并能核对结果。记录复用报告及依据，保留原执行提交和工具身份。仅合入 main、提交文档或整理证据不自动重跑相同检查。相关源码、输入或环境变化时，只重跑受影响检查；新 ZIP 的安装检查绑定新 ZIP。

Computer Use 用于首次入口确认，以及 UI 输入、弹窗、布局或交互行为改变后的受影响入口复验。纯内部实现变更通过定向测试和实际案例核验；只有发现可见结果或交互受影响、证据不足，或用户明确要求时，才补对应 Computer Use。几何变化按需要检查实际渲染。具体顺序见 [Blender 交互](blender-interaction.md)。

完成条件：定向检查和实际案例有真实结果，原失败场景已复验；尚未执行的范围明确为 `Not Run`。

## 3. 构建最终候选并安装冒烟

产品变更收敛后完整重建产品包，包括节点资产；复用锁定环境和 wheels。中间迭代先做定向验证，避免每次小改动都重跑整套打包检查。

```powershell
$blender = 'C:/Program Files/Blender Foundation/Blender 5.1/blender.exe'
python -m tools.dev_workflow --run-dir $run build --blender $blender
```

从构建输出取得实际候选 ZIP 路径，然后执行隔离安装：

```powershell
$candidate = '<本次构建输出的 ZIP 路径>'
python -m tools.dev_workflow --run-dir $run install --candidate $candidate --blender $blender
```

核对候选身份与安装文件，运行实际插件冒烟案例。保存、持久化、数据引用或工程兼容性受影响时执行必要冷读；最终整包冒烟仍核对所生成工程能在新进程读取。源码不变但重建的 `.blend` 资产内容改变时，新包需要自己的安装/资产结果；旧实现测试保持其原身份。

安装到用户日常配置前核对授权、原保存工程及旧安装保全。全局安装使用 `install --global-profile --installed-dir <旧安装目录>`，必须提供旧安装目录用于备份，并与隔离安装结果分别记录。全局配置和隔离配置均加载各自已保存的偏好。安装细节与完整发布级构建见 [DEVELOPMENT](../DEVELOPMENT.md)。

完成条件：最终包已完整重建，隔离安装和必要冷读实际执行；任务要求的日常安装已核对，失败候选不会覆盖当前有效入口。

## 4. 串行使用 Blender，恢复原工程

需要 Blender 的任务先请用户保存并关闭当前 Blender。记录用户确认的原保存工程，查询进程并确认已退出，随后启动本批实例。较新的恢复文件只有在用户明确选为目标时才使用；恢复草稿本身不是本流程目标。

```powershell
python -m tools.dev_workflow session list
python -m tools.dev_workflow session start --help
python -m tools.dev_workflow session wait --help
```

主 Agent 独占 Blender，后台、GUI 与冷重开串行。MCP 接入现有 HTTP 服务，先只读核对 PID、版本、工程和未保存状态；调用入口为 `op --request <请求文件> --transport mcp`，接入方法查 `mcp --help`。服务不可用时明确记录原因，选择 `--transport cli` 调用真实 CLI/Blender 工具；报告如实记录执行工具。

完成验证、保存本批工程并关闭本批 PID 后，打开原保存工程：

```powershell
$originalProject = '<用户确认的原保存工程路径>'
python -m tools.dev_workflow --run-dir $run restore --blender $blender --project $originalProject
```

有基线时用 `--baseline` 核对原工程、数据与偏好；没有基线时只报告实际核对范围。仅打开文件不代表恢复验收通过。完成时保留恢复后的用户窗口；不把试验工程或草稿当作原工程。

## 5. 交付与本地归档

主 Agent 复核最终 diff、候选身份、定向结果及未完成项，更新已有任务、验收记录和产物入口。`Passed / Failed / Not Run` 对应真实执行；脚本退出 0 不替代插件行为、GUI 或独立科研验收。

提交与合并按已获授权执行：串行以 `git merge --ff-only` 合入 main，核对产品身份相同即可引用已完成结果；main 带入相关新改动时复验受影响内容。为任务最终提交创建注释归档标签，保全必要产物后正常移除工作树和已合并分支；统一收尾入口为 `finish`，先查其 `--help`。遇到权限拒绝或未知文件原位保留，按 [存储维护规则](storage-maintenance.md) 报告。

发布继续使用现有候选 CI、精确 artifact 核验、许可及独立人工门禁。日常定向验证不代替发布资格；本地完成不包含 push 或发布授权。流程精简的观察依据见 [近期开发复盘](development-retrospective.md)。
