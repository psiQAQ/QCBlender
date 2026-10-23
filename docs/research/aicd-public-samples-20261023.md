# AICD 公开样例核查（2026-10-23）

## 结论与下一步

已查阅 MolStudio 当前 CNB 源码、GitHub 镜像、Zenodo 源码归档、三个运行包的完整 ZIP 中央目录，以及下文列出的 AICD 开发者和教程作者来源。**在这些公开入口中，未取得完整的苯 all/π 原始结果包。** 已取得修改版 AICD 源码、独立提取器及苯输入；这些可用于后续格式核对和计算准备，不能解除 [04 材料前置](../../.scratch/scientific-displays-20261023/issues/04-aicd-reference.md)。

仍缺同一构型/方法下的 all 与 π 原始张量、各自完整日志和轨道身份，以及可独立核对的点值参照。现有本地材料的兼容性限制沿用[原材料盘点](scientific-display-reference-inventory-20261023.md)，本次不重复生成科学数据。用户随后明确允许其他分子，检索范围据此扩大，见下一节；苯不再是验收限定。本次没有启动计算、安装依赖或联系作者。

## 放宽分子限制后的补查

2026-10-23 追加：首期案例改为至少一种闭壳层平面分子，不限化学式。数据完整性与同源 all/π 身份要求不变；若先取得单套真实转储，可以先核对解析，但不能据此宣称成对科学验收完成。非平面及开壳层材料可以收作参考，不自动扩大首期实现范围。

### 教程作者的非苯案例与关联附件

- [薁（azulene）教程第 2–4 节](http://sobereva.com/294)给出 C₁₀H₈ 的 B3LYP/6-31G(d) 全电子输入，以及该例 π 轨道 `26,31–34` 的选择说明。示例分子位于 YZ 平面，绘图磁场为 +X；这也说明更换分子后不能机械沿用苯案例的 +Z 取向。已读取正文与全部链接，未见 `azulene.out/test.txt` 原始结果附件；正文提到这些文件是运行后生成的输出，并非已发布下载。
- [修改版程序作者原帖](http://bbs.keinsci.com/thread-13577-1-1.html)公开页面仅列出 `AICD-2.0.0-modified.tar.gz` 程序附件，没有非苯样例结果附件。未重复下载同名程序包，也未登录。
- [C₁₈ 研究作者介绍](http://sobereva.com/524)展示另一类案例，并链接 [ChemRxiv 预印本](https://doi.org/10.26434/chemrxiv.11320130)。作者说明坐标位于补充材料，页面未给出原始 AICD 张量直链。本次 DOI 页面获取失败，旧 Figshare API 返回 `403`，因此其补充材料内容仍未核实，不能记为“不含原始数据”。
- 沿薁教程进入[轨道分解教程](http://sobereva.com/670)，发现并完整下载作者的 [`file.zip`](http://sobereva.com/attach/670/file.zip)：`165,837` 字节，SHA-256 `0f4c97aeb734c02f46425bbb9c3c7768200116198c8629d8312969fd42ce6362`。13 个归档成员含苯 fchk、all/π/σ 输入与输出、NICS 表和脚本；逐成员检查未发现 `Gitterpunkte`，也没有教程命名的 `nouse.txt` 张量转储。它补充了可用波函数/输入/日志材料，仍不是完整 AICD 原始结果包；未执行包内脚本。

新增原件位于 [`tutorial-followup/`](../../submodules/AICD/reference-public-20261023/tutorial-followup/)，来源与成功/失败请求的身份见其 `sources.json`，ZIP 全部成员见 `sobereva-670-file.members.json`。薁原文复用前轮已保存的 `official/sobereva-294.html`，不重复下载。访问论坛时按响应声明的 GBK 解码，原始字节保持不变。文件和目录检查 Passed；Gaussian 与 AICD 执行 Not Run。

### 其他分子论文的数据附件

[Ramji 等的共轭聚合物研究](https://pubs.acs.org/doi/10.1021/acs.jpcb.5c02849)说明使用 Gaussian 和所选 π 轨道生成 AICD 等值面，并链接[作者 Zenodo 数据集 15284080](https://zenodo.org/records/15284080)。记录自述为参数化所用的 Q-Chem 数据。本次以 HTTP 206 Range 取得四个 ZIP 的完整中央目录：

| 包 | 平台声明整包字节数 | 目录成员数 |
| --- | ---: | ---: |
| `ptb7in.zip` | 16,221,497 | 2,547 |
| `p3ht.zip` | 26,495,153 | 5,270 |
| `ptb7out.zip` | 13,112,559 | 1,098 |
| `pndit.zip` | 32,693,672 | 4,762 |

合计 13,677 项没有 AICD/ACID 命名，也没有 `.com/.gjf/.fchk/.icd/.cube/.txt`；日志位于 LAMMPS 目录，`.out` 多为能量/扭转扫描。抽取 `p3ht/E_conjugation/Methylthiophene_Improper_Bend_Methyl_Phi_0.out`（22,033 字节）核对首行确为 Q-Chem 5.4.0，全文无 `Gaussian/Gitterpunkte`；实际 SHA-256 为 `d7b5c5a31732bd6b5501960d12c5ee5996b92e6e8d2b903c64c6006077aa3039`。没有取得可用于当前解析器的真实张量。未下载整包或扫描全部成员正文，嵌套的 `p3ht_mol2_files.tar.gz` 未展开，不能声称所有文件内部均无目标数据。

论文所列[交互展示](https://chemcompute.org/simulations/submit/Energy+Displacement+of+Electron+Delocalization)当前返回 2,133 字节维护页；[作者代码仓库](https://github.com/atlas-nano/aromodel)在已连接 GitHub 工具中返回 `404`。搜索缓存仍显示旧介绍，不能证明应用和样例目前可取得。当前没有下载到其交互表面网格。

[三钍簇磁响应论文](https://www.nature.com/articles/s41467-026-74403-3)的 Source Data ZIP 已完整下载并逐文件读取：仅有 `5K_Gaussian_Data.txt` 与 `5K_ORCA_Data.txt`，内容是优化坐标和总能量；Gaussian 文件声明该几何用于振动分析，没有 AICD 张量。ZIP 为 `6,149` 字节，SHA-256 `1fef13cb371ba106c2d16895d377b1d7e236cdcae2d6c25f07cc43ce200c18e9`。

另一个[非苯发光分子论文附件线索](https://pmc.ncbi.nlm.nih.gov/articles/PMC13427141/)只从搜索索引确认列有数据 ZIP；实际正文遇人机检查，附件请求失败，内容未核实。该条保留为访问缺口，不记为无数据。

原件保存在 [`other-molecules/`](../../submodules/AICD/reference-public-20261023/other-molecules/)；`zenodo-15284080.json` 记录作者数据说明，四个 `*.zip.inventory.json` 记录完整目录与 Range 哈希，`p3ht-representative.json` 记录代表输出，`nature-74403-inventory.json` 记录完整附件，`local-files-sha256.json` 汇总实际取得字节的身份。本次目录、代表输出及 Nature 附件检查 Passed；全部 ZIP 正文扫描、嵌套归档展开及科学计算 Not Run。

扩大范围后仍未取得任意分子的合格原始张量。当前限制已改为数据完整性而非苯；04 保持 pending。未核实或暂不可访问的公开线索保留，不将“本轮未取得”写成“公开数据不存在”。

## MolStudio 上游公开入口

原件与索引位于 Git 忽略目录 [`submodules/AICD/reference-public-20261023/molstudio/`](../../submodules/AICD/reference-public-20261023/molstudio/)。[`sources.json`](../../submodules/AICD/reference-public-20261023/molstudio/sources.json) 记录页面、API 和完整下载的 URL、日期、字节及 SHA-256；三个 `*.inventory.json` 分别记录运行包原始 URL、总大小、每次 Range 的起止位置/原始字节哈希和完整成员清单。网页快照及其页面状态仅本地保留，不纳入 Git。

### 源码、镜像与归档

| 入口 | 实际读取范围 | 结果 |
| --- | --- | --- |
| [CNB 主仓库](https://cnb.cool/chem311/GXNU-MolStudio) | 公开页面显示 `427e6cca72fc43837949d0cee234bfc083279775`，与现有源码检出一致；145 个跟踪文件的既有盘点仍适用 | 有苯 all/π 展示图和解析代码，没有配套原始转储。`.gitignore` 明确将测试数据等开发材料放在被忽略的 `_dev/` 下；这解释其不在跟踪树中，但不能推断该目录实际内容。 |
| [作者 GitHub 镜像](https://github.com/houcheng-gxnu/GXNU-MolStudio) | GitHub API 主分支树 `0da9acb3ce2de902890d565d623173b1b9a2f1c9`，`truncated=false`，139 项；分支列表仅 main；issues 列表只有无关的已关闭 IRC 文件选择器 PR | 该树比 CNB 旧，未发现 AICD 样例。树、分支和 issue 响应已保存为 `github-*.json`。 |
| [作者 Zenodo V1.0.0 记录](https://zenodo.org/records/22821586) | 2026-09-18 创建的记录，完整下载唯一源码 ZIP；83 个成员 | 未发现 AICD、苯输入或响应结果。ZIP 为 `5,228,638` 字节，SHA-256 `1d656a54750d802ee76a471e6797473ba7db9c50c4d887fad9adc1a9ebb60cca`；MD5 `1df782b0990848988192beb152048b45` 与记录一致。 |

CNB `molstudio/core/aicd.py` 开头自述曾用 1470 个块及 `AICD-extract.pl` 核对解析；本次取得的独立提取器可供后续检查，但没有取得该自述所指的原始输入和计算身份，仍不能将上游声明当成本项目的实际数值验收。

### 运行包附件

通过 HTTP `206` Range 读取 ZIP 尾部及完整中央目录，逐次核对 `Content-Range` 和字节长度；三个包共读取 `2,627,678` 字节。未下载整包、未启动软件，也未解包或反编译 EXE 内部资源。下表的 SHA-256 来自发布平台元数据，**不是本地完整文件哈希验证**；实际收到的各段字节哈希保存在对应 inventory 中。

| 发布来源及文件 | 发布大小 | ZIP 成员数 | 目录检查结果 | 平台声明的整包 SHA-256 |
| --- | ---: | ---: | --- | --- |
| [CNB v1.0.0](https://cnb.cool/chem311/GXNU-MolStudio/-/releases/tag/v1.0.0)：`MolStudio-2026-10-21.zip` | 141,687,582 | 3,317 | 外层为 EXE、配置和 `debug.log`；其余是运行库。无单独附带的苯输入或 AICD 张量/结果 | `3a6e45043be0e7bba6e4cfe2c4336ad6e105c1f0377bfec73b3735bc8922e536` |
| 同一 CNB 发布：`MolStudio-2026-9-30.zip` | 391,608,112 | 11,626 | 外层为 EXE 与配置；其余是运行库，无目标样例成员 | `863a87eadebe4b8b42b229dbf58fe6333fb922169b56889bbe317833a1a40668` |
| [GitHub V1.0.0](https://github.com/houcheng-gxnu/GXNU-MolStudio/releases/tag/V1.0.0)：`MolStudio-2026-9-7.zip` | 140,884,595 | 3,306 | 外层为 EXE；其余是运行库，无目标样例成员 | `8cf8ac5ff3c1eb7e8cd6d5a560f9480563a1aaa9c86f1f45012866301cc1a3bd` |

检查覆盖完整文件名清单、AICD/ACID/benzene/benzol 关键词、常见科学输入与结果后缀，以及运行库目录之外的全部成员。命中的 `.txt/.dat` 属于许可证、包元数据、语言资源和通用库样例；不能把 matplotlib 样例当成化学结果。此检查足以说明这些 ZIP 没有单独附带的目标文件，不声称证明 EXE 内绝无嵌入数据。

CNB 匿名 API 请求返回 `401`，本次改从正常公开发布页的服务端页面状态读取附件元数据，没有登录或绕过鉴权。Zenodo、CNB 页面与附件通过标准库 HTTPS 获取；GitHub 元数据优先使用已连接的 GitHub 工具。

`Passed`：上述公开入口和完整中央目录查阅、Zenodo 下载校验、保存字节身份核对。`Not Run`：MolStudio/AICD 程序执行、Gaussian 重算、独立科学验收。目标结果包尚未取得，任务 04 继续 pending，05 不启动。

## AICD 官方与原作者来源

检索日期：2026-10-23。目标是取得可核对身份的苯 all/π 原始电流密度张量及相应 Gaussian 输入、日志、轨道选择；只读检索和下载，不安装、编译或执行 AICD，不运行 Gaussian，不联系作者。

本节核查结果：**取得了公开软件包和一个苯输入，未取得完整苯 all/π 原始结果包**。这一结论限定于以下已实际读取的页面和归档，不能推断互联网上不存在其他公开结果。

所有原件位于 Git 忽略目录 [`submodules/AICD/reference-public-20261023/official/`](../../submodules/AICD/reference-public-20261023/official/)。机器可读身份及访问记录见 [`sources.json`](../../submodules/AICD/reference-public-20261023/official/sources.json)，归档成员清单见该目录中的 `archive-members.json`、`archive-1.5.7.1-members.json`。下面的字节数与 SHA-256 均来自本次实际下载。

### 来源与访问结果

| 来源 | 本次访问 | 实际内容及完整性 |
| --- | --- | --- |
| [Herges 课题组 ACID 官方页面](https://www.otto-diels-institut.de/herges/pages_en/projects_acid.html) | HTTPS `200`；web 工具超时后，Python urllib 成功读取 | 软件方法介绍、文献和示意图；页面要求邮件索取软件包。已检查完整 HTML 链接，没有公开软件包或样例下载入口。**未取得官方结果包**。 |
| [Berkeley MGCF 软件页面 AICD 节](https://glab.cchem.berkeley.edu/mgcf/software.html#AICD) | HTTPS `200`；web 工具和 urllib 均可读 | 说明机构工作站安装了 AICD 3.0.3，Gaussian 示例和教程位于工作站文件系统。页面没有提供这些文件的 HTTP 下载。**仅确认机构内存在输入/教程，无法确认其样例结果内容**。 |
| [Sobereva《使用 AICD 2.0 绘制磁感应电流图》](http://sobereva.com/294) | 原站 HTTP `200`；HTTPS TLS 握手失败 | 原作者教程明确链接修改版 2.0 包；教程演示的主体是薁，包含轨道选择方法。**教程和公开源码包来源已确认；不是苯 all/π 结果包**。 |
| [修改版 AICD 2.0 包](http://sobereva.com/soft/AICD-2.0.0-modified.tar.gz) | 原站 HTTP `200`，实际下载并读取 tar 的全部 `121` 个成员（含目录） | `VERSION` 为 `2.0.0`。有源码、编译产物、模板、`TUTORIAL.TXT` 和一个苯输入；无预计算苯日志、张量或 all/π 配对结果。**部分材料**。 |
| [Sobereva《使用 AICD 程序研究电子离域性和磁感应电流密度》](http://sobereva.com/147) | 原站 HTTP `200` | 正文给出苯的输入和 π 轨道选择说明；另列出旧版软件包地址。已检查正文及链接，未找到苯原始输出附件。**方法与输入说明，非完整结果**。 |
| [教程所列 AICD 1.5.7.1 包](http://sobereva.com/usr/uploads/file/20150609/20150609160036_17152.bz2) | 原站 HTTP `200`，实际下载并读取 tar.bz2 的全部 `98` 个成员（含目录） | 包内为源码、Gaussian 补丁、模板和安装说明，无苯输入、日志、张量结果或嵌套样例归档。**不含目标结果**。 |

Herges 页属于 AICD 开发者官方来源；Berkeley 属于软件使用机构官方来源；Sobereva 页及其包是教程作者本人发布的来源，**不能将其修改版包标成 Herges 官方发行包**。

### 实际取得文件的身份

| 本地文件名 | 字节数 | SHA-256 |
| --- | ---: | --- |
| `herges-projects_acid.html` | 6767 | `c0f2805cd4c45729ba0dacc56bd24f4b7efae8b5719b4bc40c690d115b985590` |
| `berkeley-software.html` | 130729 | `bacf96f64b563b5cf7497f15fe9faeb0d2bd65b627cfc68b9b826805d9ed5453` |
| `sobereva-294.html` | 34829 | `2444fc1b897fa74a88ecf4ef209623b4239c8feb29d64751a1bbac5e0957f6bd` |
| `AICD-2.0.0-modified.tar.gz` | 428846 | `973fe03e63a688a9ab9180bd8eb136d9179d2fb7ebfdddebfc316de9ea4ee4ad` |
| `sobereva-147.html` | 38121 | `52d66c7046f18b236516bdd827f077f3ee767596bcc8b961a97ad58e3af9dba5` |
| `20150609160036_17152.bz2` | 80196 | `8923b1d3120f2efa6206e7ef2e2be5793bf74bc69c3d5f6f70dc941276fc9df0` |

原件仅供本地查阅；本节未据公开下载链接推断再分发许可。

### 苯输入与目标结果之间仍缺什么

修改版 2.0 归档中 `tutorial-data/` 的唯一文件是 [`benzol.nmr.com`](../../submodules/AICD/reference-public-20261023/official/selected-members/tutorial-data/benzol.nmr.com)，`752` 字节，SHA-256 `13ff47ca1943a2cf457518001a80bd6f11959a2944464cd44acf89932da3a5fc`。文件声明 `%nproc=4`、`%mem=2gb`，路由为：

```text
#HF/6-31G* scf=tight nmr=csgt iop(10/93=1)
```

它提供中性单重态苯的 12 原子坐标及张量输出文件名 `test.txt`，没有 π 轨道选择列表。归档里的 [`TUTORIAL.TXT`](../../submodules/AICD/reference-public-20261023/official/selected-members/TUTORIAL.TXT)（`1127` 字节，SHA-256 `17a1efc18368c527adb8281bdf428912e438ab3e8c4f83e5e3240f12b074ebff`）要求使用者先运行 Gaussian，再处理产生的日志；文件名出现在教程中不等于对应结果已打包。

完整成员清单确认没有 `benzol.nmr.log`、`test.txt`、`AICD.txt`、`.icd` 或 `.icd-raw` 结果，没有 all/π 结果配对。包内 `AICD-extract.pl` 和 `AICD-extract.cpp` 是提取器实现，不是可用于科学验证的原始数据。此输入和教程可作为后续计算的来源材料，不能作为已经完成计算的证据。

旧教程 `/147` 的苯示例采用 B3LYP/6-31G*，说明 π 轨道选择为 `17,20,21`。这属于**该示例的身份**，不宜未经波函数检查直接套用到修改版包的 HF/6-31G* 输入或其他苯任务。旧包本身也没有这个示例的完整计算输出。[来源：原作者旧教程第 4 节](http://sobereva.com/147)。

### 失败记录与本次核查边界

- Herges 官方 HTTPS 页：web 工具返回获取超时；同一地址 Python urllib 成功，原始页面已保存。
- Sobereva `/294`、修改版包以及 `bbs.keinsci.com` 相关 HTTPS 地址：Python 返回 TLS 内部错误；带 `www` 的 Sobereva HTTPS 地址返回 TLS EOF。失败不证明文件不存在。
- 原站 HTTP 最初在沙箱内返回 `WinError 10013`；经宿主批准的只读 HTTP 请求后，`/294`、`/147` 及两个明确下载地址均返回 `200`。没有改系统网络或 TLS 配置，没有依赖不明镜像。
- 未访问 Berkeley 工作站文件系统，未登录、未索取软件、未发邮件；未将第三方论坛分享版 3.0.4 当成官方样例。
- `Passed`：六个原件下载及字节/SHA-256 记录、两个归档全部成员查阅、2.0 苯输入和教程内容检查。
- `Not Run`：AICD 编译/执行、Gaussian 计算、渲染及独立科学验收。本节未产生新的科学结果。

官方及原作者公开路径仍缺：苯 all 和 π 两套原始张量、与两套张量逐一对应的完整 Gaussian 日志和轨道身份。是否启动重算，应结合上游 MolStudio 检索结果再决定。
