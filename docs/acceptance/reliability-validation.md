# 可靠性、IGMH 声明与流式摘要验证

2026-10-05，Windows x64 / Blender 5.1.1。源码提交 `a3ed8264aad860f25c922dd7c91efce3f6f078d3`，产品树 `0cec91ad2ed7804e78a01c39105d49e3d39150d8`。最终候选位于 `outputs/candidates/current/reliability-final-a3ed826/qcblender-0.0.1.zip`，SHA-256 为 `8094278edf08a2e6d54640e4f0cd376d8cbb98568c92464720f963dff4bb8c71`。本地技术资格Passed；36份最终候选报告与ZIP、安装源码及11个锁定wheel一致。逐报告摘要见[机器索引](reliability-validation.json)，保留和重建位置见[ARTIFACTS](../ARTIFACTS.md)，本地归档状态见[交付收据](reliability-delivery.json)。

## 当前技术证据

证据根目录：`outputs/evidence/2026-10-05/reliability/`。下表路径均相对此目录。

| 检查 | 状态 | 证据及准确范围 |
| --- | --- | --- |
| 科学回归 | Passed | `final/science.json`：105项，0 failures/errors/skipped。数值误差及参考条件保留在原始报告和机器索引。 |
| 纯 Python 边界 | Passed | `final/units.json`：40项，涵盖取消、原生Volume边界、工程事务、静态参考、摘要与多场accept。 |
| 原生 VDB | Passed | `final/native-volume.json`：15项Passed、2项Not Run；普通/中文路径、缺失/损坏/缺网格、长路径实际加载失败、保存与重定位保全。天然权限拒绝另记Not Run。 |
| 多场导入事务 | Passed | `multi-red.json`重现旧产品部分场景写入；`multi-green.json`的普通首场/第二场和paired第二场三个真实VDB失败场景均保全场景，并保留原生诊断。red汇总Passed仅表示成功复现，各旧产品回归结果为Failed。 |
| IGMH/静态参考 | Passed | `final/igmh-and-static-reference.json`：15项；静态Log/FCHK/Cube、动态Dataset及绑定祖先拒绝、P03数组/声明/CSV与自包含保存。Log/FCHK的成对场使用真实核坐标及合成网格；P03使用真实外部Cube。 |
| 原生工程冷读 | Passed | `final/cold/volume-{original,preserved}.json`及`final/cold/igmh-{original,preserved}/reopen-report.json`：最终候选的新进程原地与保全位置读取。 |
| 六固定视觉场景 | Passed | atoms、signed-mo、density-esp、slice-contours、fog、legend-annotations；初建与新进程冷读均通过科学数组/图像阈值比较。初建报告位于`final/visual/`，冷读位于`final/cold/`，保全图像/工程位于`outputs/projects/reliability/visual/`。独立视觉签署Not Run。 |
| 实际 worker 取消 | Passed | `final/cancel/*/cancel-finalization.json`：真实worker、原生timer、脚本触发Escape和CSV staging取消；控制终止/等待/清理故障为显式注入边界。报告本身明确GUI Not Run。 |
| GUI 导入、Undo/Redo及声明面板 | Passed | `gui-final/import-{after,undo,redo}.json`、`declaration-panel.json`：Computer Use输入/确认及Undo/Redo，MCP核对完整场景、绑定、datablock及科学数组。 |
| GUI 动态参考禁用与VDB拒绝 | Passed | `gui-final/dynamic-reference-disabled.json`、`gui-final/volume-native-rejected.json`；后者为同manifest损坏VDB，保留路径、`IoError: not a VDB file`及原绑定。`volume-relocate-rejected.json`只覆盖manifest身份拒绝。 |
| GUI 运行中计算取消 | Passed | `gui-final/compute-esc.json`：Computer Use在真实ESP worker运行中按Escape，退出确认、原场景不变、jobs/operations均0。 |
| GUI 运行中CSV取消 | Not Run | `gui-final/csv-finished-before-escape.json`：539,448体素导出在按键前已完成；已完成CSV保留。脚本CSV取消证据不替代这一GUI项。 |
| GUI工程保存及双冷读 | Passed | `gui-final/saved.json`、`cold-original.json`、`cold-moved.json`、`moved-preservation.json`；13 Dataset、10 VDB、38绑定对象，新进程原地/中文移动快照与保存快照精确一致。源PID62104保存后dirty false并正常exit0；见`logs/gui-final.json`。 |
| Standards / Spec 复审 | Passed | `reviews.json`：已关闭多场原子性及报告状态P2；最终剩余发现0。评审者未代替运行资格。 |

GUI工程为 `outputs/projects/reliability/reliability-gui.blend` 及同名 `.qcdata`；中文移动副本保留在 `outputs/projects/reliability/中文移动/`。八张当前候选截图位于`docs/v1-acceptance/screenshot/reliability/`并紧接[SOP](../v1-acceptance/SOP.md)对应步骤。

## 性能实验边界

`streaming-hash-comparison.json` 的测量及科学数组身份为 **Passed**，扩大优化门槛为 **Failed**。固定比较改前`982e339`与改后`94b99f5`候选，同机64³/128³/256³、1次预热及5次正式重复。256³冷/热worker中位耗时分别改善1.75%/1.52%，峰值工作集分别减少15.18/15.98 MiB，均未达到32 MiB或10%门槛。128³冷峰值增加约4.07 MiB；不宣称显著性能改善。保留局部流式SHA-256改动，停止扩大数组加载、物化及求值重构。

冷测量指无求值缓存索引，未清空OS缓存；热测量为已有有效索引的全新worker。计时包含启动和VDB发布，内存使用Windows进程生命周期PeakWorkingSetSize。最终多场导入预检、GUI延迟和viewport FPS不在该实验计时范围。

## 审计与剩余限制

最终ZIP摘要、安装源码、命令收据/log、12份视觉报告/图像摘要、GUI Undo/Redo及保存/双冷读完整快照均已核对。`evidence-index.json`列36份绑定最终候选的通过报告；配套机器索引另外保存前置失败、独立性能候选与Not Run边界的读取摘要。

GUI工程149个文件的源/移动副本摘要复核Passed，见`gui-final/preservation-byte-recheck.json`。子Agent早期额外复核因身份权限差异有147项Not Run，原记录保留于`document-drafts/preservation-byte-audit.json`；主Agent使用创建工程的正常桌面身份重新读取，未更改ACL。

天然权限拒绝目标、完整SOP逐步复做、其他平台及独立人工/科研/视觉签署均为 **Not Run**。GUI运行中CSV取消也保持Not Run。本轮不push或发布；本地合并、归档和清理按[交付收据](reliability-delivery.json)记录实际结果。
