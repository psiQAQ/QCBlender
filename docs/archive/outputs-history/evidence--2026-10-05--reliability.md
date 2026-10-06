# 2026-10-05 reliability

2026-10-05可靠性最终固定a3ed8264：105科学/40单测、六视觉、GUI/Undo/Redo及冷读Passed。静态参考、VDB非破坏失败、IGMH声明、取消最终化和流式SHA-256分别验证。GUI运行中CSV取消及独立签署Not Run。64³/128³/256³冷/热摘要实验科学数组一致；256³未达到32 MiB或10%收益门槛，停止扩大优化；耗时不含随后导入预检。

原目录：`outputs/evidence/2026-10-05/reliability/`。

本摘要记载历史执行结果。历史工程、数组、渲染、安装副本和原始报告的实际可用性，以本批 `validation/agent/reports/2026-10-06/outputs-prune/` 逐文件清单和删除收据为准；摘要不承诺旧二进制仍存在或可以逐字节恢复。

关联工程与运行目录：`outputs/projects/reliability/`、`outputs/runs/rel/`。

## 历史身份

| 原记录 | 字段 | 值 |
| --- | --- | --- |
| `docs/acceptance/reliability-validation.json` | `date` | `2026-10-05` |
| `docs/acceptance/reliability-validation.json` | `source_commit` | `a3ed8264aad860f25c922dd7c91efce3f6f078d3` |
| `docs/acceptance/reliability-validation.json` | `product_tree` | `0cec91ad2ed7804e78a01c39105d49e3d39150d8` |
| `docs/acceptance/reliability-validation.json` | `candidate.path` | `outputs/candidates/current/reliability-final-a3ed826/qcblender-0.0.1.zip` |
| `docs/acceptance/reliability-validation.json` | `candidate.sha256` | `8094278edf08a2e6d54640e4f0cd376d8cbb98568c92464720f963dff4bb8c71` |
| `docs/acceptance/reliability-validation.json` | `candidate.bytes` | `50645094` |
| `outputs/evidence/2026-10-05/reliability/qualification-main.json` | `source_commit` | `42a11beda82bf37928a6b82d40c21219aacd9b76` |

## 结果与条件

版本控制中的汇总索引：

| 记录 | 检查 | 历史状态或参数 |
| --- | --- | --- |
| `docs/acceptance/reliability-validation.json` | `status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `candidate.status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `audit.status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `audit.independent_gui_preservation_byte_check.status` | `Not Run` |
| `docs/acceptance/reliability-validation.json` | `audit.gui_preservation_byte_recheck.status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `checks.science.status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `checks.science.tests` | `105` |
| `docs/acceptance/reliability-validation.json` | `checks.science.failures` | `0` |
| `docs/acceptance/reliability-validation.json` | `checks.science.errors` | `0` |
| `docs/acceptance/reliability-validation.json` | `checks.science.skipped` | `0` |
| `docs/acceptance/reliability-validation.json` | `checks.units.status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `checks.units.tests` | `40` |
| `docs/acceptance/reliability-validation.json` | `checks.units.failures` | `0` |
| `docs/acceptance/reliability-validation.json` | `checks.units.errors` | `0` |
| `docs/acceptance/reliability-validation.json` | `checks.units.skipped` | `0` |
| `docs/acceptance/reliability-validation.json` | `checks.native_volume.status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `checks.igmh.status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `checks.scripted_cancellation.status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `checks.scripted_cancellation.gui` | `Not Run` |
| `docs/acceptance/reliability-validation.json` | `checks.multi_field_regression.status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `checks.portable_cold_reads.status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `checks.visual.status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `checks.visual.reports[0].status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `checks.visual.reports[0].scientific_arrays_unchanged` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `checks.visual.reports[0].comparison.status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `checks.visual.reports[0].comparison.regions.full.status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `checks.visual.reports[0].comparison.regions.molecule.status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `checks.visual.reports[1].status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `checks.visual.reports[1].scientific_arrays_unchanged` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `checks.visual.reports[1].comparison.status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `checks.visual.reports[1].comparison.regions.full.status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `checks.visual.reports[1].comparison.regions.molecule.status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `checks.visual.reports[2].status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `checks.visual.reports[2].scientific_arrays_unchanged` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `checks.visual.reports[2].comparison.status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `checks.visual.reports[2].comparison.regions.full.status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `checks.visual.reports[2].comparison.regions.molecule.status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `checks.visual.reports[3].status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `checks.visual.reports[3].scientific_arrays_unchanged` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `checks.visual.reports[3].comparison.status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `checks.visual.reports[3].comparison.regions.full.status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `checks.visual.reports[3].comparison.regions.molecule.status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `checks.visual.reports[4].status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `checks.visual.reports[4].scientific_arrays_unchanged` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `checks.visual.reports[4].comparison.status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `checks.visual.reports[4].comparison.regions.full.status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `checks.visual.reports[4].comparison.regions.molecule.status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `checks.visual.reports[5].status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `checks.visual.reports[5].scientific_arrays_unchanged` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `checks.visual.reports[5].comparison.status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `checks.visual.reports[5].comparison.regions.full.status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `checks.visual.reports[5].comparison.regions.molecule.status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `checks.visual.reports[6].status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `checks.visual.reports[6].scientific_arrays_unchanged` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `checks.visual.reports[6].comparison.status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `checks.visual.reports[6].comparison.regions.full.status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `checks.visual.reports[6].comparison.regions.molecule.status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `checks.visual.reports[7].status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `checks.visual.reports[7].scientific_arrays_unchanged` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `checks.visual.reports[7].comparison.status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `checks.visual.reports[7].comparison.regions.full.status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `checks.visual.reports[7].comparison.regions.molecule.status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `checks.visual.reports[8].status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `checks.visual.reports[8].scientific_arrays_unchanged` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `checks.visual.reports[8].comparison.status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `checks.visual.reports[8].comparison.regions.full.status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `checks.visual.reports[8].comparison.regions.molecule.status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `checks.visual.reports[9].status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `checks.visual.reports[9].scientific_arrays_unchanged` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `checks.visual.reports[9].comparison.status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `checks.visual.reports[9].comparison.regions.full.status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `checks.visual.reports[9].comparison.regions.molecule.status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `checks.visual.reports[10].status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `checks.visual.reports[10].scientific_arrays_unchanged` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `checks.visual.reports[10].comparison.status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `checks.visual.reports[10].comparison.regions.full.status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `checks.visual.reports[10].comparison.regions.molecule.status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `checks.visual.reports[10].comparison.regions.legend.status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `checks.visual.reports[10].comparison.regions.legend_title.status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `checks.visual.reports[10].comparison.regions.annotation.status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `checks.visual.reports[11].status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `checks.visual.reports[11].scientific_arrays_unchanged` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `checks.visual.reports[11].comparison.status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `checks.visual.reports[11].comparison.regions.full.status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `checks.visual.reports[11].comparison.regions.molecule.status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `checks.visual.reports[11].comparison.regions.legend.status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `checks.visual.reports[11].comparison.regions.legend_title.status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `checks.visual.reports[11].comparison.regions.annotation.status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `checks.gui.import-before.status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `checks.gui.import-after.status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `checks.gui.import-undo.status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `checks.gui.import-redo.status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `checks.gui.declaration-panel.status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `checks.gui.dynamic-reference-disabled.status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `checks.gui.compute-esc.status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `checks.gui.volume-native-rejected.status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `checks.gui.csv-finished-before-escape.status` | `Not Run` |
| `docs/acceptance/reliability-validation.json` | `checks.gui.volume-relocate-rejected.status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `checks.gui.saved.status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `checks.gui.cold-original.status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `checks.gui.cold-moved.status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `checks.gui_portable_save.status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `checks.gui_project_cold_read.status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `checks.naturally_denied_permissions.status` | `Not Run` |
| `docs/acceptance/reliability-validation.json` | `checks.independent_human_review.status` | `Not Run` |
| `docs/acceptance/reliability-validation.json` | `checks.full_sop.status` | `Not Run` |
| `docs/acceptance/reliability-validation.json` | `performance.measurement_status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `performance.scientific_identity` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `performance.gate_status` | `Failed` |
| `docs/acceptance/reliability-validation.json` | `source_reports.final-candidate.json.reported_status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `source_reports.final/install.json.reported_status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `source_reports.final/science.json.reported_status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `source_reports.final/units.json.reported_status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `source_reports.closing-preserved/outputs/runs/rel/vf/report.json.reported_status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `source_reports.closing-preserved/outputs/runs/rel/igmhf/report.json.reported_status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `source_reports.final/cancel/d92f50f6d08f40c48c2dc47092fc88f8/cancel-finalization.json.reported_status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `source_reports.logs/final-install.json.reported_status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `source_reports.logs/final-science.json.reported_status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `source_reports.logs/final-units.json.reported_status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `source_reports.logs/final-volume.json.reported_status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `source_reports.logs/final-igmh.json.reported_status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `source_reports.logs/final-cancel.json.reported_status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `source_reports.logs/final-volume-cold-original.json.reported_status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `source_reports.logs/final-volume-cold-preserved.json.reported_status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `source_reports.logs/final-igmh-cold-original.json.reported_status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `source_reports.logs/final-igmh-cold-preserved.json.reported_status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `source_reports.closing-preserved/outputs/runs/rel/visualf/atoms/atoms.json.reported_status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `source_reports.logs/final-visual-atoms.json.reported_status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `source_reports.final/cold/atoms/atoms.json.reported_status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `source_reports.logs/final-visual-cold-atoms.json.reported_status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `source_reports.closing-preserved/outputs/runs/rel/visualf/signed-mo/signed-mo.json.reported_status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `source_reports.logs/final-visual-signed-mo.json.reported_status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `source_reports.final/cold/signed-mo/signed-mo.json.reported_status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `source_reports.logs/final-visual-cold-signed-mo.json.reported_status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `source_reports.closing-preserved/outputs/runs/rel/visualf/density-esp/density-esp.json.reported_status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `source_reports.logs/final-visual-density-esp.json.reported_status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `source_reports.final/cold/density-esp/density-esp.json.reported_status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `source_reports.logs/final-visual-cold-density-esp.json.reported_status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `source_reports.closing-preserved/outputs/runs/rel/visualf/slice-contours/slice-contours.json.reported_status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `source_reports.logs/final-visual-slice-contours.json.reported_status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `source_reports.final/cold/slice-contours/slice-contours.json.reported_status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `source_reports.logs/final-visual-cold-slice-contours.json.reported_status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `source_reports.closing-preserved/outputs/runs/rel/visualf/fog/fog.json.reported_status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `source_reports.logs/final-visual-fog.json.reported_status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `source_reports.final/cold/fog/fog.json.reported_status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `source_reports.logs/final-visual-cold-fog.json.reported_status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `source_reports.closing-preserved/outputs/runs/rel/visualf/legend-annotations/legend-annotations.json.reported_status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `source_reports.logs/final-visual-legend-annotations.json.reported_status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `source_reports.final/cold/legend-annotations/legend-annotations.json.reported_status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `source_reports.logs/final-visual-cold-legend-annotations.json.reported_status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `source_reports.final/cold/volume-original.json.reported_status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `source_reports.final/cold/volume-preserved.json.reported_status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `source_reports.final/cold/igmh-original/reopen-report.json.reported_status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `source_reports.final/cold/igmh-preserved/reopen-report.json.reported_status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `source_reports.gui-final/import-before.json.reported_status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `source_reports.gui-final/import-after.json.reported_status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `source_reports.gui-final/import-undo.json.reported_status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `source_reports.gui-final/import-redo.json.reported_status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `source_reports.gui-final/declaration-panel.json.reported_status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `source_reports.gui-final/dynamic-reference-disabled.json.reported_status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `source_reports.gui-final/compute-esc.json.reported_status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `source_reports.gui-final/volume-native-rejected.json.reported_status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `source_reports.gui-final/csv-finished-before-escape.json.reported_status` | `Not Run` |
| `docs/acceptance/reliability-validation.json` | `source_reports.gui-final/volume-relocate-rejected.json.reported_status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `source_reports.gui-final/saved.json.reported_status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `source_reports.gui-final/cold-original.json.reported_status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `source_reports.gui-final/cold-moved.json.reported_status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `source_reports.gui-final/moved-preservation.json.reported_status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `source_reports.logs/gui-final.json.reported_status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `source_reports.streaming-hash-comparison.json.reported_status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `source_reports.benchmark-before-desktop/report.json.reported_status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `source_reports.benchmark-after-desktop/report.json.reported_status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `source_reports.multi-red.json.reported_status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `source_reports.multi-green.json.reported_status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `source_reports.reviews.json.reported_status` | `Passed` |
| `docs/acceptance/reliability-validation.json` | `qualification.status` | `Passed` |

已核对的原始专项报告（路径为历史来源身份，文件可能按本批收据退役）：

| 原报告 | 检查与条件 |
| --- | --- |
| `outputs/evidence/2026-10-05/reliability/closing-preparation/cleanup-ready-01/summary.json` | `preservation_audit.status`=Passed；`skipped[0].reason`=[WinError 5] 拒绝访问。: 'D:\\workspace\\QCBlender\\outputs\\runs\\rel\\h0\\extensions\\.user\\user_default\\qcblender\\jobs\\cache\\datasets\\00b2e57e6dec2772ad46e81401eb9a92c220bfc2cd4161db73e927f55e3b6cf9'；`skipped[1].reason`=[WinError 5] 拒绝访问。: 'D:\\workspace\\QCBlender\\outputs\\runs\\rel\\h0\\extensions\\.user\\user_default\\qcblender\\jobs\\cache\\datasets\\00c6dfc3c9dc785e85381280bd4ddd885618beba0f98e5ccb6dc0b86c0cf48a7'；`skipped[2].reason`=[WinError 5] 拒绝访问。: 'D:\\workspace\\QCBlender\\outputs\\runs\\rel\\h0\\extensions\\.user\\user_default\\qcblender\\jobs\\cache\\datasets\\029f663a69055d30e0013d4ca20cbec2d85fb4ec647ff8ad9eaaa4a6647d7907'；`skipped[3].reason`=[WinError 5] 拒绝访问。: 'D:\\workspace\\QCBlender\\outputs\\runs\\rel\\h0\\extensions\\.user\\user_default\\qcblender\\jobs\\cache\\datasets\\0fdf5ec8309a6206e13a042ae9a67688d452163c486508329beb4cfca06042e4'；`skipped[4].reason`=[WinError 5] 拒绝访问。: 'D:\\workspace\\QCBlender\\outputs\\runs\\rel\\h0\\extensions\\.user\\user_default\\qcblender\\jobs\\cache\\datasets\\1288d1309a92e5758d36192fedb2dbd9eb713534a764c5e6d4979cc7bd5cd246'；`skipped[5].reason`=[WinError 5] 拒绝访问。: 'D:\\workspace\\QCBlender\\outputs\\runs\\rel\\h0\\extensions\\.user\\user_default\\qcblender\\jobs\\cache\\datasets\\495cc5677304d49a1dc4c1fb8d058fb51c9942b80b299dd915f05be56dd39da8'；`skipped[6].reason`=[WinError 5] 拒绝访问。: 'D:\\workspace\\QCBlender\\outputs\\runs\\rel\\h0\\extensions\\.user\\user_default\\qcblender\\jobs\\cache\\datasets\\53c866bbdf4f20affaada53ae06aec998fbdabf0ad47349f8182975fbefa9818'；`skipped[7].reason`=[WinError 5] 拒绝访问。: 'D:\\workspace\\QCBlender\\outputs\\runs\\rel\\h0\\extensions\\.user\\user_default\\qcblender\\jobs\\cache\\datasets\\57bc4c130d8c3770fa62d5ed09ce41bef82db2bdef2db8670fa1b51da49f761c'；`skipped[8].reason`=[WinError 5] 拒绝访问。: 'D:\\workspace\\QCBlender\\outputs\\runs\\rel\\h0\\extensions\\.user\\user_default\\qcblender\\jobs\\cache\\datasets\\601cd92295731e86cf06d63517bb8b3034408775bf2451fd7fb34a4cafad3ea3'；`skipped[9].reason`=[WinError 5] 拒绝访问。: 'D:\\workspace\\QCBlender\\outputs\\runs\\rel\\h0\\extensions\\.user\\user_default\\qcblender\\jobs\\cache\\datasets\\7da2ac359bdbbc554a35d83db00865e816ffbd8f3390aaa2c854289fdafe48cd'；`skipped[10].reason`=[WinError 5] 拒绝访问。: 'D:\\workspace\\QCBlender\\outputs\\runs\\rel\\h0\\extensions\\.user\\user_default\\qcblender\\jobs\\cache\\datasets\\9a93301d4b1944138e6b5a1fea9f2ad28881d70e416f138ad3215cca52e9c3aa'；`skipped[11].reason`=[WinError 5] 拒绝访问。: 'D:\\workspace\\QCBlender\\outputs\\runs\\rel\\h0\\extensions\\.user\\user_default\\qcblender\\jobs\\cache\\datasets\\9af13310b7c1c97ed072c0820265c7a928b5f9ec7673919c12463495b70672cf' |
| `outputs/evidence/2026-10-05/reliability/closing-preparation/cleanup-ready-02/summary.json` | `preservation_audit.status`=Passed；`skipped[0].reason`=[WinError 5] 拒绝访问。: 'D:\\workspace\\QCBlender\\outputs\\runs\\rel\\h0\\extensions\\.user\\user_default\\qcblender\\jobs\\cache\\datasets\\00b2e57e6dec2772ad46e81401eb9a92c220bfc2cd4161db73e927f55e3b6cf9'；`skipped[1].reason`=[WinError 5] 拒绝访问。: 'D:\\workspace\\QCBlender\\outputs\\runs\\rel\\h0\\extensions\\.user\\user_default\\qcblender\\jobs\\cache\\datasets\\00c6dfc3c9dc785e85381280bd4ddd885618beba0f98e5ccb6dc0b86c0cf48a7'；`skipped[2].reason`=[WinError 5] 拒绝访问。: 'D:\\workspace\\QCBlender\\outputs\\runs\\rel\\h0\\extensions\\.user\\user_default\\qcblender\\jobs\\cache\\datasets\\029f663a69055d30e0013d4ca20cbec2d85fb4ec647ff8ad9eaaa4a6647d7907'；`skipped[3].reason`=[WinError 5] 拒绝访问。: 'D:\\workspace\\QCBlender\\outputs\\runs\\rel\\h0\\extensions\\.user\\user_default\\qcblender\\jobs\\cache\\datasets\\0fdf5ec8309a6206e13a042ae9a67688d452163c486508329beb4cfca06042e4'；`skipped[4].reason`=[WinError 5] 拒绝访问。: 'D:\\workspace\\QCBlender\\outputs\\runs\\rel\\h0\\extensions\\.user\\user_default\\qcblender\\jobs\\cache\\datasets\\1288d1309a92e5758d36192fedb2dbd9eb713534a764c5e6d4979cc7bd5cd246'；`skipped[5].reason`=[WinError 5] 拒绝访问。: 'D:\\workspace\\QCBlender\\outputs\\runs\\rel\\h0\\extensions\\.user\\user_default\\qcblender\\jobs\\cache\\datasets\\495cc5677304d49a1dc4c1fb8d058fb51c9942b80b299dd915f05be56dd39da8'；`skipped[6].reason`=[WinError 5] 拒绝访问。: 'D:\\workspace\\QCBlender\\outputs\\runs\\rel\\h0\\extensions\\.user\\user_default\\qcblender\\jobs\\cache\\datasets\\53c866bbdf4f20affaada53ae06aec998fbdabf0ad47349f8182975fbefa9818'；`skipped[7].reason`=[WinError 5] 拒绝访问。: 'D:\\workspace\\QCBlender\\outputs\\runs\\rel\\h0\\extensions\\.user\\user_default\\qcblender\\jobs\\cache\\datasets\\57bc4c130d8c3770fa62d5ed09ce41bef82db2bdef2db8670fa1b51da49f761c'；`skipped[8].reason`=[WinError 5] 拒绝访问。: 'D:\\workspace\\QCBlender\\outputs\\runs\\rel\\h0\\extensions\\.user\\user_default\\qcblender\\jobs\\cache\\datasets\\601cd92295731e86cf06d63517bb8b3034408775bf2451fd7fb34a4cafad3ea3'；`skipped[9].reason`=[WinError 5] 拒绝访问。: 'D:\\workspace\\QCBlender\\outputs\\runs\\rel\\h0\\extensions\\.user\\user_default\\qcblender\\jobs\\cache\\datasets\\7da2ac359bdbbc554a35d83db00865e816ffbd8f3390aaa2c854289fdafe48cd'；`skipped[10].reason`=[WinError 5] 拒绝访问。: 'D:\\workspace\\QCBlender\\outputs\\runs\\rel\\h0\\extensions\\.user\\user_default\\qcblender\\jobs\\cache\\datasets\\9a93301d4b1944138e6b5a1fea9f2ad28881d70e416f138ad3215cca52e9c3aa'；`skipped[11].reason`=[WinError 5] 拒绝访问。: 'D:\\workspace\\QCBlender\\outputs\\runs\\rel\\h0\\extensions\\.user\\user_default\\qcblender\\jobs\\cache\\datasets\\9af13310b7c1c97ed072c0820265c7a928b5f9ec7673919c12463495b70672cf' |
| `outputs/evidence/2026-10-05/reliability/closing-preparation/inventory-01/summary.json` | `totals..worktrees\rel-volume\tests\__pycache__.bytes`=23717；`totals..worktrees\rel-hash\tests\__pycache__.bytes`=51001；`totals..worktrees\reliability\tests\__pycache__.bytes`=308941；`totals..worktrees\reliability\tests\data\local.bytes`=92872 |
| `outputs/evidence/2026-10-05/reliability/closing-preparation/preservation-04/summary.json` | `status`=Passed |
| `outputs/evidence/2026-10-05/reliability/closing-preparation/worktree-artifacts-02/summary.json` | `candidate.status`=Passed |
| `outputs/evidence/2026-10-05/reliability/qualification-main.json` | `status`=Passed；`installed_matches_archive`=Passed；`source_matches_archive`=Passed；`wheel_checksums`=Passed；`excluded_native_gbasis`=Passed；`evidence.install.report.status`=Passed；`evidence.science.report.status`=Passed；`evidence.units.report.status`=Passed；`evidence.native-volume.report.checks.ordinary.status`=Passed；`evidence.native-volume.report.checks.chinese.status`=Passed；`evidence.native-volume.report.checks.long_field_no_scene_writes.status`=Passed；`evidence.native-volume.report.checks.missing_native.status`=Passed；`evidence.native-volume.report.checks.missing_field_no_scene_writes.status`=Passed；`evidence.native-volume.report.checks.corrupt_field_no_scene_writes.status`=Passed；`evidence.native-volume.report.checks.missing_required_grid_no_scene_writes.status`=Passed；`evidence.native-volume.report.checks.long_rebind_preserves_original.status`=Passed；`evidence.native-volume.report.checks.long_relocate_operator_preserves_original.status`=Passed；`evidence.native-volume.report.checks.corrupt_rebind_preserves_original.status`=Passed；`scope`=Local automated technical qualification; independent user acceptance pending；`evidence.science.report.tests`=105；`evidence.science.report.failures`=0；`evidence.science.report.errors`=0；`evidence.science.report.skipped`=0；`evidence.science.report.metrics.density_max_abs_error`=8.440006539212064e-07；`evidence.science.report.metrics.esp_max_abs_error`=4.60872461194306e-06；`evidence.science.report.metrics.electron_count`=9.999999997365176；`evidence.units.report.tests`=40；`evidence.units.report.failures`=0；`evidence.units.report.errors`=0；`evidence.units.report.skipped`=0 |
| `outputs/evidence/2026-10-05/reliability/qualification.json` | `status`=Passed；`installed_matches_archive`=Passed；`source_matches_archive`=Passed；`wheel_checksums`=Passed；`excluded_native_gbasis`=Passed；`evidence.install.report.status`=Passed；`evidence.science.report.status`=Passed；`evidence.units.report.status`=Passed；`evidence.native-volume.report.checks.ordinary.status`=Passed；`evidence.native-volume.report.checks.chinese.status`=Passed；`evidence.native-volume.report.checks.long_field_no_scene_writes.status`=Passed；`evidence.native-volume.report.checks.missing_native.status`=Passed；`evidence.native-volume.report.checks.missing_field_no_scene_writes.status`=Passed；`evidence.native-volume.report.checks.corrupt_field_no_scene_writes.status`=Passed；`evidence.native-volume.report.checks.missing_required_grid_no_scene_writes.status`=Passed；`evidence.native-volume.report.checks.long_rebind_preserves_original.status`=Passed；`evidence.native-volume.report.checks.long_relocate_operator_preserves_original.status`=Passed；`evidence.native-volume.report.checks.corrupt_rebind_preserves_original.status`=Passed；`scope`=Local automated technical qualification; independent user acceptance pending；`evidence.science.report.tests`=105；`evidence.science.report.failures`=0；`evidence.science.report.errors`=0；`evidence.science.report.skipped`=0；`evidence.science.report.metrics.density_max_abs_error`=8.440006539212064e-07；`evidence.science.report.metrics.esp_max_abs_error`=4.60872461194306e-06；`evidence.science.report.metrics.electron_count`=9.999999997365176；`evidence.units.report.tests`=40；`evidence.units.report.failures`=0；`evidence.units.report.errors`=0；`evidence.units.report.skipped`=0 |
| `outputs/evidence/2026-10-05/reliability/benchmark-after-desktop/report.json` | `status`=Passed |

### 失败、未运行与限制

下表保留各报告中不同的非通过字段及对应原因。同字段、状态、原因的重复副本合并为一个来源；早期失败、故意负例与最终资格须按字段和任务范围解释。

| 原记录 | 字段 | 状态 | 原原因 |
| --- | --- | --- | --- |
| `outputs/evidence/2026-10-05/reliability/multi-red.json` | `checks[0].status` | Failed | checks[0].error=Blender cannot read volume cache "D:\workspace\QCBlender\outputs\runs\rel\multi-red\paired-second\job\dataset\field-1.vdb": IoError: not a VDB file. If the file exists, try a shorter project location and retry |
| `outputs/evidence/2026-10-05/reliability/multi-red.json` | `checks[1].status` | Failed | checks[1].error=Blender cannot read volume cache "D:\workspace\QCBlender\outputs\runs\rel\multi-red\import-second\job\dataset\field-1.vdb": IoError: not a VDB file. If the file exists, try a shorter project location and retry |
| `outputs/evidence/2026-10-05/reliability/multi-red.json` | `checks[2].status` | Failed | checks[2].error=Blender cannot read volume cache "D:\workspace\QCBlender\outputs\runs\rel\multi-red\import-first\job\dataset\field-0.vdb": IoError: not a VDB file. If the file exists, try a shorter project location and retry |
| `outputs/evidence/2026-10-05/reliability/document-drafts/reliability-validation.json` | `performance.gate_status` | Failed | 原字段未附原因 |
| `outputs/evidence/2026-10-05/reliability/benchmark-before/report.json` | `status` | Failed | error=RuntimeError: {'status': 'failed', 'error': "PermissionError: [WinError 5] 拒绝访问。: 'D:\\\\workspace\\\\QCBlender\\\\outputs\\\\runs\\\\rel\\\\h0\\\\extensions\\\\.user\\\\user_default\\\\qcblender\\\\jobs\\\\4ea17e7ad1474381a0f8a07f1823b410\\\\progress.pending.json' -> 'D:\\\\workspace\\\\QCBlender\\\\outputs\\\\runs\\\\rel\\\\h0\\\\extensions\\\\.user\\\\user_default\\\\qcblender\\\\jobs\\\\4ea17e7ad1474381a0f8a07f1823b410\\\\progress.json'", 'schema': 1, 'job_id': '4ea17e7ad1474381a0f8a07f1823b410'} |
| `outputs/evidence/2026-10-05/reliability/closing-preserved/outputs/runs/rel/multi-red/import-first/report.json` | `status` | Failed | error=Blender cannot read volume cache "D:\workspace\QCBlender\outputs\runs\rel\multi-red\import-first\job\dataset\field-0.vdb": IoError: not a VDB file. If the file exists, try a shorter project location and retry |
| `outputs/evidence/2026-10-05/reliability/closing-preserved/outputs/runs/rel/multi-red/import-second/report.json` | `status` | Failed | error=Blender cannot read volume cache "D:\workspace\QCBlender\outputs\runs\rel\multi-red\import-second\job\dataset\field-1.vdb": IoError: not a VDB file. If the file exists, try a shorter project location and retry |
| `outputs/evidence/2026-10-05/reliability/closing-preserved/outputs/runs/rel/multi-red/paired-second/report.json` | `status` | Failed | error=Blender cannot read volume cache "D:\workspace\QCBlender\outputs\runs\rel\multi-red\paired-second\job\dataset\field-1.vdb": IoError: not a VDB file. If the file exists, try a shorter project location and retry |
| `outputs/evidence/2026-10-05/reliability/gui/cancel-cold.json` | `status` | Failed | error=PermissionError(13, '拒绝访问。') |
| `outputs/evidence/2026-10-05/reliability/logs/benchmark-before.json` | `status` | Failed | exit_code=1 |
| `outputs/evidence/2026-10-05/reliability/closing-preparation/cleanup-ready-01/compatibility.json` | `apply` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-05/reliability/document-drafts/reliability-validation.json` | `audit.independent_gui_preservation_byte_check.status` | Not Run | audit.independent_gui_preservation_byte_check.reason=Subagent file access denied; original preservation receipt and cold snapshot parity remain separate evidence |
| `outputs/evidence/2026-10-05/reliability/document-drafts/reliability-validation.json` | `checks.full_sop.status` | Not Run | checks.full_sop.reason=Scoped reliability and six visual cases only |
| `outputs/evidence/2026-10-05/reliability/document-drafts/reliability-validation.json` | `checks.gui.csv-finished-before-escape.status` | Not Run | checks.gui.csv-finished-before-escape.scope=Computer Use running CSV cancellation; checks.gui.csv-finished-before-escape.reason=Native 539448-voxel export completed before Escape; completed export is retained |
| `outputs/evidence/2026-10-05/reliability/document-drafts/reliability-validation.json` | `checks.independent_human_review.status` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-05/reliability/document-drafts/reliability-validation.json` | `checks.naturally_denied_permissions.status` | Not Run | checks.naturally_denied_permissions.reason=Requires supplied naturally denied target; no ACL changes |
| `outputs/evidence/2026-10-05/reliability/closing-preserved/outputs/runs/rel/v-native2/report.json` | `checks.permission_denied.status` | Not Run | checks.permission_denied.reason=Requires supplied naturally denied target; no ACL changes |
| `outputs/evidence/2026-10-05/reliability/document-drafts/reliability-validation.json` | `checks.scripted_cancellation.gui` | Not Run | checks.scripted_cancellation.scope=Real workers and native timers; scripted ESC and controlled process fault injection |
| `outputs/evidence/2026-10-05/reliability/closing-preserved/outputs/runs/rel/v-native2/report.json` | `checks.ui_undo_redo_cold_reopen.status` | Not Run | checks.ui_undo_redo_cold_reopen.reason=Separate foreground/cold-process validation |
| `outputs/evidence/2026-10-05/reliability/closing-preparation/preservation-audit.json` | `cleanup` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-05/reliability/qualification-main.json` | `evidence.cancel-finalization.report.gui` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-05/reliability/qualification-main.json` | `evidence.cold-visual-atoms.report.independent_human_review` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-05/reliability/qualification-main.json` | `evidence.cold-visual-density-esp.report.independent_human_review` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-05/reliability/qualification-main.json` | `evidence.cold-visual-fog.report.independent_human_review` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-05/reliability/qualification-main.json` | `evidence.cold-visual-legend-annotations.report.independent_human_review` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-05/reliability/qualification-main.json` | `evidence.cold-visual-signed-mo.report.independent_human_review` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-05/reliability/qualification-main.json` | `evidence.cold-visual-slice-contours.report.independent_human_review` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-05/reliability/qualification-main.json` | `evidence.native-volume.report.checks.permission_denied.status` | Not Run | evidence.native-volume.report.checks.permission_denied.reason=Requires supplied naturally denied target; no ACL changes |
| `outputs/evidence/2026-10-05/reliability/qualification-main.json` | `evidence.native-volume.report.checks.ui_undo_redo_cold_reopen.status` | Not Run | evidence.native-volume.report.checks.ui_undo_redo_cold_reopen.reason=Separate foreground/cold-process validation |
| `outputs/evidence/2026-10-05/reliability/qualification-main.json` | `evidence.standards-and-spec-review.report.standards.runtime_tests` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-05/reliability/qualification-main.json` | `evidence.visual-atoms.report.independent_human_review` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-05/reliability/qualification-main.json` | `evidence.visual-density-esp.report.independent_human_review` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-05/reliability/qualification-main.json` | `evidence.visual-fog.report.independent_human_review` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-05/reliability/qualification-main.json` | `evidence.visual-legend-annotations.report.independent_human_review` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-05/reliability/qualification-main.json` | `evidence.visual-signed-mo.report.independent_human_review` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-05/reliability/qualification-main.json` | `evidence.visual-slice-contours.report.independent_human_review` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-05/reliability/cancel-native/ec6e3abeb076475087ad9e795c544b9f/cancel-finalization.json` | `gui` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-05/reliability/closing-preserved/outputs/runs/rel/visualf/atoms/atoms.json` | `independent_human_review` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-05/reliability/evidence-index.json` | `limitations.independent_human_scientific_signoff` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-05/reliability/evidence-index.json` | `limitations.natural_permission_denied_target` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-05/reliability/closing/final-document-check.json` | `push` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-05/reliability/closing-preparation/worktree-removal-readiness.json` | `rel-cancel.nonregenerable_files[0].cleanup` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-05/reliability/closing-preparation/worktree-removal-readiness.json` | `rel-cancel.removal` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-05/reliability/closing-preparation/worktree-removal-readiness.json` | `rel-hash.removal` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-05/reliability/closing-preparation/worktree-removal-readiness.json` | `rel-static.nonregenerable_files[0].cleanup` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-05/reliability/closing-preparation/worktree-removal-readiness.json` | `rel-static.nonregenerable_files[1].cleanup` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-05/reliability/closing-preparation/worktree-removal-readiness.json` | `rel-static.removal` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-05/reliability/closing-preparation/worktree-removal-readiness.json` | `rel-volume.nonregenerable_files[0].cleanup` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-05/reliability/closing-preparation/worktree-removal-readiness.json` | `rel-volume.nonregenerable_files[1].cleanup` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-05/reliability/closing-preparation/worktree-removal-readiness.json` | `rel-volume.removal` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-05/reliability/closing/final-document-check.json` | `release` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-05/reliability/closing-preparation/worktree-removal-readiness.json` | `reliability.nonregenerable_files[0].cleanup` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-05/reliability/closing-preparation/worktree-removal-readiness.json` | `reliability.nonregenerable_files[1].cleanup` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-05/reliability/closing-preparation/worktree-removal-readiness.json` | `reliability.nonregenerable_files[2].cleanup` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-05/reliability/closing-preparation/worktree-removal-readiness.json` | `reliability.nonregenerable_files[3].cleanup` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-05/reliability/closing-preparation/worktree-removal-readiness.json` | `reliability.nonregenerable_files[4].cleanup` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-05/reliability/closing-preparation/worktree-removal-readiness.json` | `reliability.removal` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-05/reliability/document-drafts/reliability-validation.json` | `source_reports.gui-final/csv-finished-before-escape.json.reported_status` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-05/reliability/reviews.json` | `standards.runtime_tests` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-05/reliability/document-drafts/preservation-byte-audit.json` | `status` | Not Run | 原字段未附原因 |
| `outputs/evidence/2026-10-05/reliability/gui-final/compute-finished-before-escape.json` | `status` | Not Run | reason=Worker completed before Computer Use Escape; this attempt does not qualify running cancellation |
| `outputs/evidence/2026-10-05/reliability/gui-final/csv-finished-before-escape.json` | `status` | Not Run | scope=Computer Use running CSV cancellation; reason=Native 539448-voxel export completed before Escape; completed export is retained |
| `outputs/evidence/2026-10-05/reliability/gui-final/compute-budget-rejected.json` | `result.status` | failed | result.error=MemoryError: Grid/backend exceeds 1024 MiB; reduce resolution or increase budget |

## 当前输入与重建

当前输入从 [validation/shared/data](../../../validation/shared/data/README.md) 进入；本地 key、源文件和旧位置由 `local-inputs.json` 与 `migration-map.json` 定位。Gaussian原始日志、波函数、真实计算checkpoint、计算条件和许可证保留一份；同字节历史副本由逐文件清单确认后退役。

复跑按 [DEVELOPMENT](../../DEVELOPMENT.md) 和 [Agent检查流程](../../../validation/agent/README.md) 准备当前锁定环境与wheels，在新的工作目录从输入生成前置工程，执行相应 `tools/verify_*.py`、科学测试或渲染工具，保存新安装身份、参数和报告。历史源版本仅用于查阅当时设计；重建当前行为须重新资格验证，不运行含旧绝对路径的归档脚本覆盖材料。

本摘要整理未启动Blender、未运行本批产品测试、未重新复算科学输入，状态均为 Not Run。已确认用户工程、今天人工验收目录及未知恢复对象保持保护，历史安装/worker目录不能用来推断用户资产归属。
