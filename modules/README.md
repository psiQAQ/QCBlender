# 本地模块与构建输入

本目录存放仓库工具使用的共用依赖；依赖版本和来源分别以根目录 `dependencies.lock.json`、`science-sources.lock.json` 及 `tools/build-requirements.txt` 为准。当前位置和迁移证据见 [产物入口](../docs/ARTIFACTS.md)。

| 子目录或文件 | 用途 |
| --- | --- |
| `build-site/` | 现有构建工具的 Python 包；通过目标 Python 的 `-m` 入口使用 |
| `science/` | 现有科学 Python 包；配合 Blender 自带 Python 使用 |
| `wheels/`、`backend-wheel.json` | 已核验的打包输入及当前后端身份 |
| `sources/` | 必要依赖源码原件，按软件分类；保留来源和摘要 |
| `tools/` | 辅助插件和外部工具归档，按软件分类 |
| `licenses/` | 保留的完整许可文本 |

安装内容、二进制和源码归档保持本地 Git 忽略；本页和许可文本可跟踪。移动目录不代表重新安装或升级依赖；原安装元数据保留原始来源，不改写历史绝对路径。依赖缺失时明确报告，安装或下载仍须授权。

缓存和临时工作放 `.tmp/`，本机配置放 `.local/`，成品放 `outputs/`。本目录不是可任意清空的缓存。
