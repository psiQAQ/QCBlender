# 标注窗口宽度验收

2026-10-17，Blender 5.1.1 / Windows。添加和编辑标注的宽度参数均从 760 改为 380，产品只改两行；横排 XYZ、来源编号同行元素/全局坐标和现有保存值继续使用原逻辑。源码提交 `0c082190be0b79255a751e41133fb206fa28460e`。

当前包 50,940,876 字节，SHA-256 `8c23eaff5af4509b2a05ac4f45cf8a79464db06038a56fa013f7be60f48596c4`。完整[机器结果](../reports/2026-10-17/annotation-width/acceptance.json)及[候选身份](../current-install.json)绑定本次包。

| 检查 | 结果 |
| --- | --- |
| 定向测试 | Passed：35 项，标注几何、核心和编号输入；使用现有 Blender Python 和 `outputs/science`，无依赖安装 |
| 完整构建与安装 | Passed：重建节点资产，复用 11 个锁定 wheel，隔离和日常安装各 123 成员与同一 ZIP 逐字节一致 |
| Computer Use | Passed：原生 invoke 打开已安装的原子/二面角添加、原子编辑窗口；观察 380 宽度布局，实际点击编号步进得到新元素/坐标，X 偏移从 0.20 调到 0.23 后取消；四个来源行、横排偏移和底部按钮可见。截图只保留[二面角添加](../reports/2026-10-17/annotation-width/add-380.png)及[原子编辑](../reports/2026-10-17/annotation-width/edit-380.png)窗口区域，不声称通过 GUI 点击了入口按钮 |
| 原生与冷读 | Passed：复用八原子输入验证四类标注、字号/前缀/坐标和换帧；隔离原生工程、GUI 保存工程、日常配置 GUI 工程副本分别在新进程读回一致 |
| 日常 GUI、其他测量编辑窗口、完整科学套件复跑、独立人工/科研接受 | Not Run：其余种类共享相同宽度参数与布局；本批科学数据和计算逻辑未改 |

初次通用 Python 无 NumPy，改用既有 Blender Python 和科学 site 后通过。原生验证首次选用四原子公开输入，触发旧验证器夹具的占用编号断言；随后从已验证归档取回原先八原子输入并记录摘要，再次实际验证通过。失败报告和完整日志均保留，不改写历史 Failed。

旧当前 ZIP、日常旧插件与偏好备份、本批原生工程、GUI `gui/verified.blend + .qcdata`、输入和脚本均在 `outputs/runs/annotation-width-20261017/`；所有本批 Blender 进程已退出。用户此前明确保存关闭且无需恢复工程，本批没有修改用户原工程。

新候选稳定副本在 `outputs/candidates/current/annotation-width-20261017/`，旧候选仍保留。主干本地 ff-only 整合，注释标签 `archive/2026-10-17/fix/annotation-dialog-width` 与保全/正常移除收据由[产物入口](../../../docs/ARTIFACTS.md#annotation-width-20261017)定位。不 push。
