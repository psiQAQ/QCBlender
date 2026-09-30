# 01 样本准备

Triage: ready-for-agent
Status: resolved
Blocked by: 无

## 验收

样本与许可/获取方法、manifest、真实解析检查和交接值可复核。

## Comments

- 2026-09-30：按用户已批准实施计划建立任务；尚未领取或运行验收。

## Answer

- Delivery: 样本准备验收 Passed；公开包分发覆盖 partial（P02 原站独立获取，数据再分发许可 unverified）。所有 C01–C13 科学输入可在本机真实解析，不把未知许可文件放入包。
- 新计算 P01/P03/P04/P05 的数据 CC BY 4.0；P04 为现有 geomeTRIC 1.1.1 原生 TS/两方向 IRC，两方向收敛、1 个虚频、61 个接受帧，取跨 TS 三个连续帧，完整真实 SCF FCHK/Mayer。未安装/更新依赖，未修改产品科学接口。
- 固定交接：`docs/v1-acceptance/tutorial-samples.json`，schema 1，28 个文件条目（27 包内数据 + 1 外部 Gaussian/NBO 日志）、C01–C13/N01–N18、实测值、原子/Job/block/pair、单位和显示建议。解压根相对路径以 archive_path 为准。
- 当前公开包：`outputs/runs/public-tutorial/samples/qcblender-public-tutorial-samples-v1.zip`，SHA-256 `a4ccfc3ef91921817d17284196ba23ccfb7cce7b1643cdfa41af8e8a6103f85b`。ZIP 全文件 CRC/数据 SHA/许可排除 Passed；没有 P02 原件、旧未知许可 IRC/COBH3 示例或程序二进制。
- S08 原站真实下载 SHA/92,872 bytes Passed；job2/block1 7 NBO/2 E(2)、job1 4 优化步 Passed；不宣称原站公开可见等于可再分发。
- `tools/verify_tutorial_samples.py --reference-root D:/workspace/QCBlender --package D:/workspace/QCBlender/outputs/runs/public-tutorial/samples/qcblender-public-tutorial-samples-v1.zip --report D:/workspace/QCBlender/outputs/evidence/2026-09-30/public-tutorial/samples/final-validation.json`：Passed（28 文件、真实自旋恒等式、双场网格、ESP/AIM、优化/NBO、真实 TS/双向 IRC、原 CHK 与 FCHK 密度互校、Mayer、ETS/NOCV、公开 ZIP）。
- 既有 adapter/log/optimization/cube/AIM/NOCV 六组 31 测试 Passed，无失败/错误/跳过；为避免复制历史输入，运行于集中主检出，验证报告明确 source_root。本任务未修改对应产品代码。
- `git diff --check` Passed。GUI、渲染、保存/冷重开/移动重开和独立人工签署 Not Run，归任务05；显示默认值未作为视觉验收。
- 必要证据/原始计算日志/生成和核查脚本：`outputs/evidence/2026-09-30/public-tutorial/samples/`。大 Cube 新增于主检出唯一 `tests/data/local/public-tutorial/` 并记入集中索引；小型可分发样本在 `tests/data/tutorial/`。
