# 移除二维绘图并导出数据

Triage: ready-for-agent
Status: resolved
Blocked by: 无

## Acceptance

五类绘图移除、优化记录导出、完整CSV/来源文件和原子结果目录；空间显示保留。

## Answer

专属源码实施完成。新建IR sticks及选择着色、IRC能量/Mayer曲线与游标、剖面曲线/轴、paired散点和ESP面积柱图已移除。剖面、paired和ESP面积使用绑定Dataset的空mesh记录对象，标记`qc_data_record=True`；保留三维振动、IRC构型和Mayer pair记录浏览、AIM paths、空间切片contours、palettes。旧工程图形不会自动删除。

显式导出`qcblender.export_data`通过Job运行；数据类型IR、optimization、IRC、Mayer、profile、paired、ESP_AREA，支持paired和ESP_AREA当前筛选，默认全量。CSV使用UTF-8及确定来源顺序；完整metadata保存来源和manifest SHA、方法/job/frame与单位、筛选、掩码记录、CSV行数/SHA。paired输出真实全部有效体素的flat index、grid index、affine Å坐标和值，不使用展示抽样上限；profile invalid值留空；ESP保留源百分比。唯一结果子目录先暂存后原子rename，失败和取消只清理本次staging，不覆盖结果。默认目录为偏好路径、已保存.blend父目录或Windows Documents Known Folder。

- Passed: 7项数据导出测试（真实频率/优化日志、P04 IRC/Mayer、P03 ESP、64820个有效paired体素及筛选、profile invalid、虚频、取消/中途取消/磁盘失败/防覆盖、来源校验、系统目录）。
- Passed: 原有5项profile与5项result_filters科学回归；69个源码AST解析；git diff --check。
- Not Run: Blender注册和native/可见GUI、保存/移动冷重开；主Agent在共享UI/worker整合后串行验证。
- Not Run: 独立人工签署。

证据：`outputs/evidence/2026-10-02/display-xyz-export/export-pure-python.json`及`export-pure-python.log`。

## Comments

2026-10-02: 用户批准计划；03专属模块及测试由实施Agent完成，本地提交不push。共享入口整合由主Agent完成：注册`data_export.QCBLENDER_OT_export_data`和`irc.QCBLENDER_OT_select_irc_mayer_pair`，移除已删除绘图class；worker action `export_data`调用`data_export.export_report(request,directory,cancelled)`，request含dataset/dataset_sha256/output_directory/kind/scope/filters/export_token；取消卸载后调用Operator `cleanup_export()`；识别analysis role profile/paired/esp_area及qc_data_record标记，更新受影响验证工具。
