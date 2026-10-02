# 展示精度、XYZ 与数据导出

Baseline: d47abe3b29ef8cc8d284b8d8be1a08a30728a9a5

## Accepted behavior

- 新建原子显示 Quality=3；切片显示201/轴；教程生成网格0.2 Å、延伸3 Å、512 MiB。保留九个公共资产的实现、签名、接口和既有工程参数；P03/P05原始Cube不变。
- 标准XYZ：元素/原子序数和三个有限坐标，Å；单帧及同原子数/元素顺序的多帧离散查看。不支持扩展属性、晶胞/PBC、播放或插值。保留原始来源摘要和逐帧身份；连接仅为距离推断。
- 移除新建IR谱图、IRC/Mayer曲线/游标、剖面曲线/轴、paired场散点、ESP面积柱图。保留三维动画、构型、场/切片/等值线/图例、AIM空间路径和已有表格浏览。旧工程图形不自动删除，来源Dataset仍可导出。
- 显式导出IR、优化/收敛、IRC、Mayer、剖面、paired场全量/筛选体素及ESP面积；UTF-8 CSV和metadata.json。未设置输出目录时用.blend父目录或系统Documents。跨工程偏好可设绝对目录，本次可覆盖目录。唯一结果子目录，不覆盖旧结果；暂存完整成功后提交。
- 来源/单位/掩码/筛选条件不能丢失；.qcdata继续是工程持久化，导出目录不取代worker缓存或Dataset。
- 不更新依赖/锁，不push/发布。仅主Agent串行操作一个Blender PID；新/变更入口Computer Use，未变入口复用已登记MCP。独立人工签署Not Run。

## Ownership and integration

01 precision: qcblender/blender/views.py, scalars.py；tools/verify_display_precision.py。
02 xyz: qcblender/readers.py, data.py, geometry.py, blender/geometry.py；新xyz/trajectory模块、测试和XYZ来源样本。不得编辑views.py/ui.py/editor_ui.py/source_browser.py。
03 export: 移除二维实现的properties.py/profile.py/irc.py/external_fields.py/external_results.py/result_browser.py/charts.py/layers.py/camera.py；新数据导出模块与测试。不得编辑ui.py/editor_ui.py/source_browser.py、根文档或公共assets.py。
主Agent: ui.py/editor_ui.py/source_browser.py、worker/shared调用集成、工具中受影响检查、README/指南/SOP/样本清单和证据。
不增加内部通用框架。共享文件交接通过消息明确API，主Agent最后串行整合。

## Acceptance

科学回归、严格XYZ解析/构型身份、CSV逐值/单位/完整性、取消/无覆盖/默认目录、无新二维图、公共资产一致、旧工程兼容、同候选可见GUI及保存/移动冷重开。仅本批实际通过写Passed。
证据outputs/evidence/2026-10-02/display-xyz-export/，临时outputs/runs/display-xyz-export/；完成更新ARTIFACTS/CHANGELOG。源码固定后构建验证，再提交索引。按precision→xyz→export串行ff-only合并，最后主Agent集成分支；本地archive标签及正常工作树/分支清理，权限阻塞保留。
