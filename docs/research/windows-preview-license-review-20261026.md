# Windows 首个预览版：材料与组件许可核对

核查日期：2026-10-26。对应[发布任务](../../.scratch/alpha-readiness/issues/14-windows-preview.md)。本页记录取得的材料与尚缺的依据，不将公开下载、自产计算结果或 Agent 技术检查视作第三方素材的自动再分发授权。

## 专题 10：表面距离投影

历史案例由 Multiwfn 2026.9.20 官方 `Ru(bpy3)2+.gjf` 构型生成，61 原子，源文件未改朝向。本次结果和逐文件身份见[原生成及数值核验](scientific-display-reference-inventory-20261023.md#本次实际运行及数值验收)。本机材料为 `validation/shared/data/local/scientific-displays/ru-vdw-20261023/`。

已读本地官方分发包的 `submodules/Multiwfn/Multiwfn_2026.9.20_bin_Win64/LICENSE.txt`，条款 (a)/(b) 说明程序代码的免费使用、开源与分发，(c) 要求引用原始论文。该文本未单独说明官方示例输入文件的许可范围。本次尚未取得明确覆盖上述构型及随教程再分发的依据；保留本地限定状态，不将其统一改标为 CC BY 4.0。

## 专题 11：AICD 全电子与 π 结果

历史两套张量由本项目实际计算生成，但固定构型取自 [Sobereva 文章 670](http://sobereva.com/670) 的 `file/benzene_NICS.gjf`，去除 Bq 探针。科学条件、转换及身份见[实际计算记录](scientific-display-reference-inventory-20261023.md#aicd-本次实际运行及数值契约)。

原始来源快照位于 `submodules/AICD/reference-public-20261023/tutorial-followup/`，原获取记录为同目录 `sources.json`：

| 原件 | 获取时间（UTC） | SHA-256 | 核查范围 |
| --- | --- | --- | --- |
| `sobereva-670.html` | 2026-10-23 08:04:42 | `59a5f365495cc135b2e85528871f83c050eaa723b171505d148bd277fa1b1a27` | 本次重算摘要与获取记录一致；UTF-8 正文及页面版权声明 |
| `sobereva-670-file.zip` | 2026-10-23 08:05:14 | `0f4c97aeb734c02f46425bbb9c3c7768200116198c8629d8312969fd42ce6362` | [原始附件](http://sobereva.com/attach/670/file.zip)成员清单，没有独立 LICENSE/NOTICE 文件 |

页面明确禁止转载文章内容并欢迎转发链接；这不能被改写为附件许可，也不能据此断言所有科学数值均受同一限制。现有证据不足以确认该附件素材及其派生文件可按公开教程的许可分发。本次线上访问失败，以上结论基于已经保全且身份核对的原始快照。

## 随扩展组件

已检查锁定 IOData 1.0.1 wheel 和当前 GBasis wheel：两者包元数据声明 `GPL-3.0-or-later`，所附根许可证均为 LGPLv3 文本。后者文本明确以 GPLv3 为基础增加权限；原始声明应一并保留，不以直接改写上游许可消除差异。

已核对锁定的 11 个 wheel，逐项 SHA-256 与锁文件及后端记录一致。许可文件、元数据声明及 GBasis 构建说明的精确身份保存在[组件清单](../../validation/agent/reports/2026-10-26/windows-preview/component-license-inventory.json)。原始文本仍在各 wheel 内；没有修改、补写或移除上游许可。

| 组件 | 本次读取的许可材料及处理 |
| --- | --- |
| cclib 1.8.1 | dist-info/LICENSE，BSD-3-Clause；完整保留版权、条件与免责声明 |
| IOData 1.0.1 / GBasis 固定源码 wheel | GPL-3.0-or-later 元数据和源码声明与 LGPLv3 根文件并存；完整保留两种原始声明、Python 源码及本项目 GPLv3 文本，不声称上游已经澄清差异 |
| SciPy 1.16.3 | dist-info/LICENSE.txt 同时包含 SciPy、OpenBLAS、LAPACK、GCC runtime 等声明；原始 wheel 与其二进制不变，保留 GPL-3.0-or-later WITH GCC-exception-3.1 文本 |
| packaging 25.0 | LICENSE、LICENSE.APACHE、LICENSE.BSD 三份文本均保留 |
| periodictable 2.0.2 / pyparsing 3.2.3 / attrs 25.3.0 / importlib-resources 6.5.2 | 各 dist-info 的原始许可证完整存在，按原文件分发 |
| SymPy 1.14.0 / mpmath 1.3.0 | 原始 LICENSE 与 SymPy AUTHORS 完整保留 |

GBasis 随包的是 Python 实现，`gbasis/QCBLENDER_BUILD.md` 记录去除可选 libcint 包装器及原生代码的构建边界；逐成员检查没有 DLL、PYD、SO、LIB 或 A 文件。IOData 和 GBasis 的可修改 Python 源码随 wheel 保留，固定上游来源由 `science-sources.lock.json` 和 `dependencies.lock.json` 定位。Blender 提供的 Python、NumPy、OpenVDB 和字体不作为额外 wheel 打包。

QCBlender 中采用的 MolecularNodes 半径、Viridis/Cividis 数值表沿用 `THIRD_PARTY.md` 的作者、固定 commit 和 GPL-3.0-or-later 归属；本批不改其数值或来源。教程中的旧 Ru/外部苯素材不纳入新公开附件。

`Passed`：锁定组件身份与原始许可材料的技术核对。`Not Run`：最终 CI 候选的包内字节复核，因此尚不记录最终 `license_review=Passed`。这份记录不代表独立法律审查或上游许可声明的修订。版本及来源继续以两份锁和 `THIRD_PARTY.md` 为准，不更换依赖。

## 本批处理边界

2026-10-26 用户明确答复“我没有额外授权，改用自建公开案例”。专题 10 改用项目自有 Gaussian-v2 P03 水二聚体构型，旋转后重新计算 vdW 投影；专题 11 从解析正六边形苯构型新算 CSGT all/π，不复用上述附件坐标。原本机输入、旧截图与历史验收保留原身份。新的公开分发依据及逐文件摘要由 `validation/agent/acceptance/tutorial-public-extras.json` 记录；未知许可原件不进入公开包，不联系作者。

## 当前公开案例与实际检查

公开清单中的水二聚体投影和苯 all/π 已生成并保留逐文件摘要。苯使用解析正六边形固定构型，B3LYP/6-31G(d)、CSGT；两套各 240,630 点，π 轨道 17、20、21 由 Multiwfn 实际识别。独立提取参照的九分量和单位磁场响应完全一致，Aniso 最大绝对误差不超过 2.23e-16。该检查验证数据解析与定义，不代表独立科研签署。

两个案例均已通过真实 MCP 导入、Computer Use 观察和自包含工程冷重开。公共日志仅规范化运行环境路径，原始科学字段和软件声明保留；规范化范围见各组 NOTICE.md。技术证据由[产物入口](../ARTIFACTS.md#windows-preview-20261026)定位，最终 CI 候选仍需另行绑定与安装验收。
