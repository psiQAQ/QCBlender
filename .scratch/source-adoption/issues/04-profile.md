# D 场值线剖面、曲线和 CSV

Triage: ready-for-agent
Status: claimed
Type: task
Blocked by: 01

## 实施

提取现有 inspection.sample_point 到无 bpy 的 `qcblender/sampling.py`，保留原单点接口兼容。新 `qcblender/profile.py` 保存采样逻辑；新 `qcblender/blender/profile.py` 实现 `qcblender.mark_profile_start`、`qcblender.create_line_profile`、`qcblender.export_line_profile`。UI 由主代理接入。

在同一活动 field/slice 视图记录世界游标起点，再移动游标创建剖面。默认几何场；存在可核对的色场绑定时提供 COLOR。两个世界端点转换为所选体积源局部 Å，距离按源局部 Å 计算；101 点默认，2–1001，含端点，拒绝零长度。

复用三线性采样：域外和无效样本使用显式 valid，不当作零。派生 Dataset 保存 float64 距离、采样位置、数值与有效掩码（无效数值仅有限存储占位），附字段快照、原 manifest 摘要、源记录、局部/世界端点、插值方式。标为本插件派生结果，不调用会标为 external_analysis 的 analysis_dataset。

曲线按连续有效段生成，横轴保留真实距离，空缺断线；至少须有连续两个有效点。复用 bind/material/qc_chart 约定，不修改只支持连续 IRC 的 curve_view，不新增通用绘图库。视图为一次采样快照，移动仅影响排版。CSV 从保存数组生成，列包含距离/位置/值/单位/valid；无效值留空。冷重开可重导 CSV，不改变归档契约携带外部 CSV。

## 验收

纯 Python：斜轴线性解析场、端点、距离、零长、域外和掩码、CSV。主代理：真实几何场/色场、变换、断线、源身份、复制、原生撤销/重做、数组不变、渲染、保存移动冷重开后 CSV 一致。

## Comments

2026-09-27：用户选择曲线＋CSV；A 集成通过后启动，避免共享基线冲突。

2026-09-27：A 已 resolved；D 在 `feat/adopt-profile` 工作树领取，纯 Python 开发与验证中，Blender 验收由主代理执行。

2026-09-27：实现提取共享三线性采样，新增派生线剖面、独立断线曲线和从保存数组导出的 CSV。Passed：纯 Python 斜轴线性场、端点/距离、几何和色场源坐标、域外/无效掩码、相邻有效段、Dataset 冷加载 CSV，3/3 专用测试与 2/2 项目存储回归；`compileall`、`git diff --check`。Not Run：Blender 安装场景、真实几何/色场、图像、原生撤销/重做和移动冷重开，由主代理验收后改为 resolved。
