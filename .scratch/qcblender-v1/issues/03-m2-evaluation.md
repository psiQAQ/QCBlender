# M2 内置波函数求值

Status: ready-for-agent
Execution: complete
Owner: root
Blocked by: 01, 02

## 工作

实现轨道选择、MO/总及自旋密度/ESP、网格控制、分块与取消、科学缓存；后台运行时复用同一 Blender。

## 验收

闭壳层/开壳层及受支持基组约定通过独立数值参考与收敛测试；取消和过时结果不损坏已有成功数据。

## Comments

2026-09-22：本阶段完成。HOMO/LUMO 使用各自自旋通道实际占据和能量，ROHF Alpha/Beta 不同前线编号及矩形 MO 边界有回归；元数据记录编号/占据/能量。固定 Python 后端与独立参考一致，h 及以上和 ECP 等边界显式拒绝。新版 256³ 任务观测 76.65 s、缓存 3.22 s、峰值 827 MiB；同机渲染争用使其不是隔离基准，详见 docs/VALIDATION.md。

2026-09-22：MO/总/Alpha/Beta/自旋密度/ESP 已实现；真实 UB3LYP、LiH+ 和 38 AO/37 MO 通过不变量检查。分块进度、重复场缓存、取消、中文路径迁移恢复通过 Blender 检查。LiH+ 步长/范围收敛和 r×ESP→+1 Passed。CH4 的 64³/128³/256³ 首次完整任务约 2.51/6.33/37.48 s，缓存复用 1.51/1.71/3.22 s；256³ 峰值工作集约 828 MiB。证据：outputs/scientific-convergence.json、field-performance.json。继续轨道选择信息、支持矩阵与高角动量边界验收。

2026-09-22：作为 M0 验证实现的核心已支持 MO/总密度/自旋/ESP、显式 Å→Bohr、分块、预算检查和近核掩码。独立参考及取消回调检查 Passed。完整科学支持矩阵、收敛、交互取消和显示仍待本阶段验收。

2026-09-22：由已确认设计路线建立；实施、启动/安装 Blender 和下载公开样例已获用户授权。未授权提交、推送或发布。
