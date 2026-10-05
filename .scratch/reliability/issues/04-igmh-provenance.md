# 04 IGMH来源声明

Triage: ready-for-agent
Status: claimed
Blocked by: 01

## 范围与验收

遵循spec第二批。P03 inter及[[1,2,3],[4,5,6]]经界面、manifest、CSV metadata、原地/移动冷读一致；三分量仅改声明，科学数组不变；片段非法输入拒绝，交叠保留提示，旧工程和缺失信息显示未声明。不扩展分析算法或依赖。

## Comments

2026-10-05：任务01已集成后领取。负责IGMH分量/片段声明、metadata展示及导出相关测试；原生脚本交主Agent串行运行，使用真实显示层与P03导入检查。

2026-10-05：实现`analysis.igmh_declaration`，保存inter/intra/total/unknown、可选片段成员、可选来源说明、`user_assigned`性质、声明状态及交叠提示。成员严格使用源Cube顺序1基整数，片段内重复拒绝，片段间交叠保留，不要求全覆盖。导入对话框及对象属性“IGMH 来源声明”面板显示声明；来源详情包含相同记录。CSV metadata沿用既有完整`scientific_metadata`导出，科学数组、单位、仿射与有效掩码保持一致。缺失旧记录通过展示helper标为unknown/unverified。

验证：

- Passed：先运行`tests/test_science_igmh_declaration.py`红测试，真实P03 import新参数及旧记录helper缺失，4 tests / 15 errors。
- Passed：首次实现后同脚本4 tests通过，包括四分量仅metadata变化、非法片段拒绝、交叠保留、manifest和CSV metadata持久化；随后扩展了声明参数边界测试。
- Passed：声明、真实Multiwfn metadata、CSV导出、静态参考、capability及当前科学关联共26 tests定向回归，24.684秒。命令以Blender 5.1内置`python.exe -B -c`显式设置本树源码/测试及主库`outputs/science`路径，用`unittest.defaultTestLoader.loadTestsFromNames`加载`test_science_igmh_declaration`、`test_science_multiwfn_metadata`、`test_science_data_export`、`test_science_static_reference`、`test_static_reference_capabilities`、`test_science_current_association`；`QCBLENDER_REFERENCE_ROOT=D:/workspace/QCBlender`。
- Passed：`git diff --check`与5个相关源码/脚本AST解析。
- Not Run：候选原生及原地/移动冷读。`tools/verify_igmh_provenance.py`交主Agent串行运行：隔离CONFIG需位于主库outputs；参数`--root <候选树> --sample D:/workspace/QCBlender --out <证据目录> --zip <候选ZIP>`；脚本安装并核对候选源码，以注册operator和真实Job worker导入P03及普通静态Log/FCHK/Cube参考，读取实际atom_view优化/IRC/XYZ步骤并检查动态祖先拒绝。静态Log/FCHK正例使用真实源核坐标生成的8 voxel合成Cube；P03 Cube正例使用校验过的`public-tutorial/P03/igmh/dg_inter.cub`和`sl2r.cub`，inter、`[[1,2,3],[4,5,6]]`、来源`P03 Multiwfn fragment setup`。
- Not Run：`<out>/P03-IGMH-portable.blend`通过Save Portable QC Project operator保存，加载此工程后同脚本加`--reopen`检查原地或移动冷读。GUI提示、导入对话框和Undo/Redo由任务06统一验证；本子任务未启动Blender。
