# 当前构型关联与共享 mesh 切步 P1 修复

Triage: ready-for-agent
Status: resolved
Type: task

## 目标与授权

实施基线main@d76aa4cd1390fa5704e8378c0adcff07bf38d415。修复AUDIT-01动态构型关联与AUDIT-04共享mesh切步污染；用户确认保留IRC/优化当前步骤关联、切步失效，拒绝共享mesh切步，并批准验证、提交、ff-only合入main、注释归档、本批清理与普通HTTPS推送main。不新增依赖，不改变Dataset科学数组，不开放多帧XYZ关联，不发布版本或推送标签。

## 行为契约

- 关联读取current_geometry/scientific_geometry提供的源Å坐标；compare_sources保留四个既有位置参数，新增仅关键字reference_kind/reference_step/moving_kind/moving_step，默认source/None。
- 新关联记录版本2，保留已有字段，增加reference_geometry/moving_geometry完整科学来源身份；QCViewSettings增加association_reference对象指针。无有效指针、legacy、stale、损坏记录不得授权跨源刚体关联。
- require_current_association(moving, expected_reference)明确核对对象指针、状态及两端当前科学身份；切片/着色以实际绑定的原子父对象定位reference，不按名称/source哈希猜测。派生场Dataset摘要不要求等于父原子Dataset，但source/job/原子身份/场的静态构型必须与当前原子构型一致。动态原子着色也读取当前构型。
- prepare_association_invalidation(changed_obj, next_geometry)在所有写入前准备受影响记录的stale JSON；apply_association_invalidation(prepared)在切步成功后仅提交预先准备的字符串。受影响损坏记录取消切步；无关坏记录不阻塞。改步时自身及指向该reference的关联失效，同一步不失效，切回旧步不自动恢复。
- 旧工程可打开/显示，旧关联提示重新关联；插件复制/创建当前版本视图清除继承关联与reference指针，保留显示矩阵；原生复制仍须由消费端逐次验证。失效不自动回退显示位置。
- IRC/优化在current_geometry校验后、任意geometry/step/cache/annotation/association写入前检查目标根mesh.users>1并取消。提示先使mesh独立；IRC子对象入口检查parent根对象，不改变优化入口或公共只读current_geometry。GUI确认Blender单用户操作路径，不将不支持IRC的插件复制作为通用提示。

## 验证与交付

先记录基线真实原生operator失败断言，再修复。P04第1步对照成功、第3步与第1步约0.0707267Å的差异必须在0.001Å容差拒绝；P02优化同/异步骤、reference/moving角色均覆盖。验证切步失效、重命名/删除/同源不同副本/复制/旧记录/损坏记录/原子身份/Undo/Redo/保存及移动冷重开。共享mesh通过原生Alt+D创建，拒绝必须保持两侧全部状态和科学数组，独立mesh后成功且原件不变。XYZ共享mesh拒绝为对照。

运行科学回归、相关测试、六固定视觉基线；新候选真实GUI验证操作结果和失效提示。主Agent串行持有Blender、候选、文档和证据索引，子Agent不启动Blender。Standards/Spec分别评审并修复复审后交付，历史失败字节保留，独立人工/科研签署Not Run。

## Comments

- 2026-10-04：用户确认计划并要求实施，支持子代理。

- 2026-10-04：实施、50份候选证据及双轴复审Passed；main@747ae8d已合并并推送回读。三个注释标签、三个工作树/分支清理Passed，16,801文件/812,107,170字节按摘要清理，600保护文件复核Passed。最终身份与文档提交推送回读见docs/acceptance/audit-p1-delivery.json；独立人工/科研签署Not Run。
