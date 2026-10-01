Triage: ready-for-agent
Status: resolved
Type: task
Blocked by: none

# 规范化 Dataset 绑定路径

## 验收
修复路径表示假不匹配，保留不同 Dataset/hash/source/metadata 拒绝条件；纯 Python 回归通过后交主 Agent GUI/冷重开复验。

## Comments
- 主 Agent 提供真实 GUI 错误 Field volume differs from the selected view；qc_field、source 和 Dataset hash 一致，qc_dataset 路径表示不同。
- 已领取；不启动或连接 Blender。

## Answer
binding_key 在 bpy.path.abspath 解析 Blender 相对路径后，用 data.dataset_path_key 规范化平台分隔符和点段，复用 unprefixed_path 去 Windows 存储前缀，再按平台 normcase 规则比较。Dataset hash 保留为键的第二项；bound_field 与 read_metadata 守卫函数未修改。缓存写入、查询、点击探针的身份记录和复制前置检查均复用同一 binding_key，因此使用统一身份。

## Validation
- Passed: bundled Python 路径回归 4 passed、1 POSIX-only skipped；覆盖空值、不同 Dataset 路径、混合分隔符/大小写/点段、超过 260 字符扩展路径和 UNC。
- Passed: test_science_project.py 2 passed，真实长路径数组读取、copy/reuse/archive 及损坏拒绝。
- Passed: test_science_planes.py 3 passed，ij/jk/ki、atoms 及配置身份拒绝的纯几何检查。
- Passed: 四个产品/测试/工具文件 AST parse 与 compile（不导入 bpy、不运行工具）。
- Passed: AST 对比 bound_field/read_metadata 原守卫函数与基线完全相同；已有源码 BOM/换行保留；git diff --check。
- Passed: 主Agent在e26d22a同一候选完成原生prepare/reopen/中文移动reopen、四平面混合路径以及不同Dataset/hash/source/metadata拒绝守卫；实际GUI新建切片后ij/jk/ki/atoms及FREE/Gizmo/探针/等值线通过。独立21点参考误差小于2e-6；旧源3 Dataset/154数组不变。新工程6 Dataset/172数组与95文件保全，新可见PID52600原路径冷读/CSV复导出Passed。原生证据 outputs/evidence/2026-10-01/tutorial-cu/slice-plane/；GUI与保全索引 outputs/evidence/2026-10-01/tutorial-cu/full/C04/slice-retest/preservation.json。完整C04及独立签署另保持Not Run。
- Not Run: 完整 C04 教程和独立人工签署。

## 原生工具交接
加强 tools/verify_multiwfn_interaction.py 的既有 reopen 路径：加载已保存工程后，对相对路径 volume 新建绝对路径 slice，验证 binding_key/cache 一致、ij/jk/ki/atoms 成功；分别破坏 volume 的 Dataset 路径、manifest hash、source hash 和 field metadata，确认 bound_field 精确拒绝、operator 取消且切片状态不变；确认科学数组摘要未变。
沿用该工具现有 --mode prepare / --mode reopen / --fixture / --out 和独立安装配置约束；主 Agent 负责串行运行。此子 Agent 未运行或连接 Blender。

## Comments
- 首次 miniforge Python 3.13 无 numpy，测试导入 Failed；随后使用宿主已提供的 bundled Python（numpy 2.3.5）执行上述检查，没有安装或更新依赖。
- 规范化不调用 realpath，不读取文件，不合并符号链接/junction 别名；路径被删除或实际 manifest 损坏时，既有读取/摘要守卫继续失败。
