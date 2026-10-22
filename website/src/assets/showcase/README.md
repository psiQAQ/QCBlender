# 宣传图来源与显示条件

三图均于 2026-10-23 从本仓库公开教程数据对应的工程副本在 Blender 5.1.1 中实际渲染，未使用生成式图像。安装候选源码为 `8d2f83f20c0eb251e10f02c81faae176c636ca46`，完整包 SHA-256 为 `e73797010178657da9b950817f25a79786f2251832c9d04736c56b0dc00fa590`。原科学数组、Dataset 身份与对象变换保持一致；三份保存工程均在新进程冷读通过。独立科研验收未由本次出图替代。

| 图像 | 公开输入与显示条件 | 输出 |
| --- | --- | --- |
| `orbital.png` | P01 `o2-uhf.fchk`；UHF α 轨道 9，occupation 1，能量 −0.411434861 hartree；等值 ±0.045 bohr⁻³ᐟ²，正负阈值联动；31 × 31 × 37 网格，步长 0.2 Å | 1600 × 1360，透明背景；红蓝表示两种轨道相位 |
| `esp.png` | P03 `water-dimer.fchk`；RHF 总电子密度 0.004 electron/bohr³ 等值面，映射 ESP −0.05～0.05 hartree/e；39 × 31 × 49 网格，步长 0.2 Å | 1600 × 1200，白底；保留紫至黄的定量色标 |
| `igmh.png` | P03 `igmh/dg_inter.cub` 与 `igmh/sl2r.cub`；δg = 0.005 electron/bohr⁴，sign(λ₂)ρ 色标 ±0.04 electron/bohr³；91 × 38 × 156 网格，步长约 0.02874808114 Å | 1600 × 1200，白底；保留分子结构与图例 |

IGMH 使用工程中已有的 Multiwfn 片段声明：inter 分量，源 Cube 的 1-based 原子组 `[1,2,3]` 与 `[4,5,6]`，声明来源为 `P03 Multiwfn fragment setup`。标量类型和片段为导入时显式声明，本次未重新计算 IGMH，也不从配色单独推断相互作用性质。

统一使用插件“QC 出图”的标准档：Cycles 128 samples、自适应阈值 0.02、降噪、Standard 色彩变换、三点柔光、9% 留白。禁用场景合成后处理。轨道与 ESP 用主轴方向；IGMH 从分子主轴方向绕相机局部 Y 轴偏转 35° 后重新取景，避免表面侧对镜头。主题切换只改变网页背景，不重新映射科学颜色。

## 输入身份

| 输入 | SHA-256 |
| --- | --- |
| `P01/o2-uhf.fchk` | `ef562c4b210e7c380219282d7684370cca1f0e8349dffa1d4388af5831472e36` |
| `P03/water-dimer.fchk` | `02ffc555ac7bda6e263e8461481914db3a2576582f71b6b9ea97fa05df610d6a` |
| `P03/igmh/dg_inter.cub` | `daf5a7e79c7dcc67b244f3dc1d2d314795c9f318c931e4f25d36e72ea168a28e` |
| `P03/igmh/sl2r.cub` | `18a33c308c868c9f7747128f1a23c04fc69df37fd5b9681aa5dd35ef20997958` |

输入位于 `validation/shared/data/public/`；其中部分文件从已跟踪的冻结公开样本包恢复。样本来源与许可见该包的 LICENSE、NOTICE 和 manifest。图像作为这些公开教程输入的派生成果，以 CC BY 4.0 提供，归属 QCBlender contributors；请保留原输入归属。

## 成图与复现

| 文件 | SHA-256 |
| --- | --- |
| `orbital.png` | `04127c8b34a03163a7b7668134e8d0fb1432565b2039cff40e2f621dc04b7814` |
| `esp.png` | `6afdb1a74e1a69f21671c363a7174954735dbc0c336e20dc518daaa9ce015fa3` |
| `igmh.png` | `9e87d85cc64bf5fa79e30e897eaf00ffdbd4c39c09ed854b5f676cb526e4ce5c` |

复用脚本为 [`scripts/render-showcase.py`](../../../scripts/render-showcase.py)。先按仓库 Blender 交互规则保存并关闭用户会话，复制 `.blend + .qcdata`；在副本中通过已核对 PID 的真实 MCP 调用 `prepare` 与 `render`。脚本不会启动 Blender、安装依赖或修改原教程。`reopen` 在另一个 Blender 进程比较科学数组和相机，并核对 VDB 可读性。

本地工程位于 `outputs/projects/website-showcase/{orbital,esp,igmh}/`，执行参数与数组摘要在 `validation/agent/reports/2026-10-23/website/renders/`，会话收据在同批 `runs/`。上述本地工程和技术报告不随网站部署。网页构建只从这里的三张 PNG 生成响应式图像；完整结果见[网站验收](../../../../validation/agent/acceptance/website.md)。
