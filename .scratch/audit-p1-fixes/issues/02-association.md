# 当前构型关联

Triage: ready-for-agent
Status: claimed
Type: task
Blocked by: 01

关联Agent负责科学compare_sources、Blender关联、properties、scalars、interaction、source_browser及专用单测/原生验证脚本；遵循spec接口。不得修改irc/optimization/layers/views模块，不启动Blender。交接已预检失效helper供主Agent串行接入。

## Comments

- 2026-10-04：关联Agent领取；前置01已resolved。先验证compare_sources当前步骤边界，再实现关联生命周期和消费者；原生Blender验收由主Agent执行。

## Answer

- 实现当前source/optimization/irc构型比较；compare_sources保留四个既有位置参数，新增仅关键字步骤选择，关联记录version=2。Blender记录绑定两端完整科学身份及association_reference对象指针。
- require_current_association验证具体reference、记录状态、当前两端身份及刚体变换。prepare_association_invalidation在切步写入前准备受影响stale记录；apply_association_invalidation只提交预先序列化文本。来源浏览为legacy、损坏或缺指针记录提示重新关联。
- 切片和着色使用真实atoms父对象核对场构型；派生Dataset摘要可不同。无atoms父或记录指向其他对象时，着色仍可独立执行无rigid精确构型比较；只有本次对象指针对应且当前验证通过的记录才能允许rigid。动态atoms着色比较当前步骤。
- `tools/verify_audit_p1_association.py --output-dir <目录>`使用已安装候选和真实P04/P02，覆盖双端当前步骤、记录生命周期、关联/切片/着色operator、复制、重命名/删除与自包含保存；`--reopen <blend>`核验完整Dataset数组摘要、当前构型及关联/指针。该脚本需要主Agent先接入切步失效helper和复制清除。
- Passed：新增纯科学测试先以缺少moving_kind接口出现RED，实施后GREEN；新增6项及既有adapter8、XYZ7、planes3，共24项，0失败/错误/跳过。证据为本工作树`outputs/p1-association/pure-tests.json`与`.log`。改动模块及原生脚本py_compile、git diff --check通过。
- Not Run：本Agent不启动Blender；原生脚本、实际GUI、Undo/Redo、原地/移动冷重开由主Agent集成后执行。任务保持claimed，待原生验收后由主Agent收口。
