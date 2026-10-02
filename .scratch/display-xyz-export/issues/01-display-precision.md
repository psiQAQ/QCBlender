# 展示精度

Triage: ready-for-agent
Status: resolved
Blocked by: 无

## Acceptance

新原子Quality=3，切片201/轴，公共资产实现不变；相关参数检查通过。

## Answer

实施范围完成；resolved 仅覆盖本任务源码修改和纯 Python 静态验收。原生 Blender、Computer Use、保存及冷重开验收由主 Agent 执行，当前均为 Not Run。

- 新建原子外层 Quality=3；新建切片操作 resolution=201。已有工程参数不迁移。
- 实体等值面的 Adaptivity=0、Smooth Normals=True、Quality=2 保持不变。原子 Quality 改善球体细分；实体场精度由原始空间场决定。切片201/轴增加显示采样，不能据此声称来源场更精细。
- 九个公共资产的实现、接口和默认值保持基线 071a71703482a191393b4dde0a7483e1a5ca093b。assets.py、资产目录、输入文件未修改。
- 新增 tools/verify_display_precision.py：静态模式核对两处默认值、实体面参数及公共资产实现 AST 摘要；原生模式使用已安装扩展，核对新建原子源数量/原子身份/来源摘要、Quality=3 的球体几何数量、切片操作默认201及原始显示网格201×201、既有场参数保留、九资产签名和实现摘要，保存 JSON。

验证：

- Passed：纯 Python 静态检查；outputs/runs/display-xyz-export/precision-static/static.json。
- Passed：tools/verify_asset_catalog.py（ASSET_CATALOG_PASSED）。
- Passed：三个修改源码文件 compile()；git diff --check。
- Not Run：原生 Blender 网格检查、已安装扩展运行、Computer Use、保存/移动/冷重开、独立人工验收。

主 Agent 原生运行入口：在已安装候选扩展且已有场视图的原生 Blender 验收场景中运行 tools/verify_display_precision.py，传入 --output-dir outputs/evidence/2026-10-02/display-xyz-export/precision-native；必要时 --field-object 指定现有场对象。输出目录应为新目录；脚本新增技术验收对象与合成原子 Dataset，不自动保存工程。原生结果为 native.json。

## Comments

2026-10-02: 用户批准计划；各项初始pending，领取与证据在本任务记录。

2026-10-02: 子 Agent 领取并完成展示精度源码及静态验收；未启动或连接 Blender。任务状态 resolved 不代表原生或独立人工验收通过。
