# 05 流式摘要与同口径实验

Triage: ready-for-agent
Status: resolved
Blocked by: 01, 02, 03, 04

## 范围与验收

遵循spec第三批。先固化改动前候选，后流式摘要候选同机1预热5正式测64³/128³/256³冷/热，逐数组摘要及缓存命中一致。明确峰值/时间指标与门槛，不把历史P2数据当当前候选基线，不改变数组加载或求值策略。

## Comments

2026-10-05：01至04技术前置已resolved；固定改前产品982e339及prehash-candidate.json候选。开始同机64/128/256、1预热5正式冷热基线；实施范围仅data.py三处大文件摘要与worker写后VDB摘要。

2026-10-05：流式摘要实现已提交供同口径候选验证，状态保持claimed，待主Agent判断性能与综合科学身份。`data.py` 的内部 `_file_sha256` 使用已有 `filesystem_path`、二进制文件上下文及标准库 `hashlib.file_digest`；替换保存.npy后摘要、读取.npy校验摘要、VDB缓存校验摘要，`worker.py` 的VDB写后摘要复用相同实现。未修改小manifest/输入摘要、数组加载、mmap、数组物化和求值块策略。

纯Python验证：

- **Passed**：Blender附带 `python.exe -m unittest discover -s tests -p test_streaming_digests.py`，6项测试，覆盖完整字节参考摘要、空/多块文件、数组content-addressed路径及manifest记录保持、保存/读取数组和dtype精确相等、数组损坏在 `np.load` 前拒绝、VDB损坏拒绝、无摘要的可选VDB契约，以及大文件摘要不调用 `Path.read_bytes`。
- **Passed**：同一解释器运行 `test_science_project.py`，2项既有PortableProject测试，覆盖中文/长路径复制和归档、并发复制身份及损坏拒绝。
- **Passed**：`py_compile qcblender/data.py qcblender/worker.py tests/test_streaming_digests.py`；`git diff --check`。
- **Not Run**：本任务子Agent未启动Blender或运行性能测量。改前候选 `outputs/candidates/baseline/reliability-prehash-982e339/qcblender-0.0.1.zip`（SHA-256 `d18652e5ee4f4c2a224628769b391a9c53d593297e9c00ba89a5dab12506633a`）及改后候选的73worker同机冷热测量，由主Agent串行完成；尚未作出32MiB/10%门槛判定，不据单元测试宣称性能收益。

2026-10-05实验完成：改前982e339候选与改后94b99f5候选在同一桌面用户环境、全新隔离配置下完成64³/128³/256³、1预热5正式、冷/热共146个worker。两批测量与科学数组/摘要/缓存命中核对Passed，报告见benchmark-before-desktop/report.json、benchmark-after-desktop/report.json及streaming-hash-comparison.json。256³冷运行中位40.219→39.516秒、820.6→805.4MiB；热运行3.292→3.242秒、451.9→436.0MiB。32MiB或10%增益门槛Failed（未达到）；其他指标无明显回退，因此保留本次有限范围的流式摘要实现，停止扩大数组/求值重构。128³冷峰值约增加4.1MiB，完整范围见原始报告。首轮sandbox基线因progress.json替换WinError5失败，原报告保留；原因未确认，不将其部分结果用于比较。最终多场导入预检另有原生验证，未纳入上述性能时序，不宣称UI或视口加速。
