# 子模块更新与插件增量筛选

批准日期：2026-10-23。主仓库基线：`6c3545dd72bce8d897d5826b22ca0ac973b0763e`。

## 目标与边界

更新 MolecularNodes、GXNU-MolStudio、VTK 到本批核实的默认主干提交，并在一份研究报告中记录完整增量范围、重点源码、QCBlender 现有能力及采用建议。

本批在当前干净的 main 检出串行执行；保留 MolecularNodes 浅克隆、VTK 浅克隆/partial clone/sparse checkout，fetch 使用 `--no-tags`，不初始化嵌套子模块。保留历史研究的原始身份。

不修改插件功能、API、科学数据格式或运行依赖，不构建安装包，不操作 Blender，不提交、推送或发布。采用建议不构成功能实施授权。

2026-10-23 后续授权：用户要求提交全部未提交内容并推送；本研究记录和三个已核验的子模块指针纳入该次提交。以上边界保留原研究执行时的范围。

## 固定目标

实施前再次查询三个 origin 的 HEAD 和默认分支，均与规划快照相同：

| 子模块 | 基线 | 目标 | 分支 |
| --- | --- | --- | --- |
| MolecularNodes | `f88961b28828dfb32697748b575298dec20af3af` | `6cc280ff7002e46e6977cc2ab337cf9a34adac7a` | main |
| GXNU-MolStudio | `a030398b75e62bd10905c52d04c3f884e0b07fb6` | `427e6cca72fc43837949d0cee234bfc083279775` | main |
| VTK | `4b0325a981d1f5cfad9d4da4909a8230881b2bf4` | `be385f1c26ca5699f5b17578c690a0d83eed9ec5` | master |

## 验收与交付

- 子模块 HEAD 与固定目标一致，内部工作区干净；原远端、tag 集合、浅克隆及 VTK 稀疏配置保留。
- 完整增量清单可复核，分页与浅历史的限制写清楚。
- 交付 `docs/research/upstream-20261023-review.md`，更新研究索引及本批任务；产品代码和依赖锁保持不变。
- 检查受影响链接及 `git diff --check`；插件运行、GUI、渲染和独立科学验收均为 `Not Run`。

任务入口：[01 更新参考与整理建议](issues/01-references-and-review.md)。
