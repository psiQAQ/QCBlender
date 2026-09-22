# 单 Blender 扩展的运行与依赖打包边界

核对日期：2026-09-22。状态：架构与依赖候选研究；未下载、安装或构建依赖，未生成扩展安装包。本文依据 Blender 官方文档、固定版本源码、PyPI 发布元数据与本机只读探测；候选版本不等于已通过集成验收。用户已确认首版必须内置波函数求值，选择轨道即可生成场；展示 MO、电子密度、自旋密度、ESP、电荷、偶极、振动和 IR。优化/IRC、差分密度、WFN/WFX 进入后续版本。

## 1. 推荐的交付方式

QCBlender 交付为一个 Blender 扩展 ZIP：插件自身包含通用量子化学数据模型、格式适配、缓存和节点映射；必需的成熟科学库以 wheels 随包提供。用户安装该 ZIP 后即可离线导入和显示，不配置系统 Python、conda、venv、pip 或另一个科学处理程序。`cbq_core` 仅用于参考数据契约和实现经验，插件内模块自行维护版本与测试，不把该外部项目作为运行依赖。

耗时读取和波函数求值由插件管理的本地后台任务完成，使用**当前 Blender 安装的运行时**；后台任务不是另一个需要用户安装的产品。主线程只接收经校验的结果并创建 Blender 数据、节点和界面。该部署结构可行，但**Windows 下完整波函数后端的依赖组合尚未合格**，GBasis 的发布版本约束是当前必须解决的具体问题，见第 3 节。

Blender 官方扩展机制支持随 ZIP 带入 wheels、在 manifest 中列出相对路径，并按目标平台拆分 ZIP。这里的“一个插件”指用户一次安装一个适合其平台的 ZIP，不要求把所有操作系统的二进制放进同一个文件。[Blender 5.1 Python Wheels](https://docs.blender.org/manual/id/5.1/advanced/extensions/python_wheels.html)

## 2. 已核实的 Blender 运行时

本机使用 `C:/Program Files/Blender Foundation/Blender 5.1/blender.exe`，以 `--background --factory-startup --disable-autoexec` 读取版本和模块来源，退出码 0。

| 项目 | 本机实测 | 设计约束 |
| --- | --- | --- |
| Blender | 5.1.1，构建 hash `b70da489d7f4` | 当前资格验证基线；其它版本逐个验证 |
| Python | CPython 3.13.9，Windows AMD64 | 二进制扩展须匹配实际解释器、ABI 与平台 |
| NumPy | 2.3.4，来自 Blender 自带 `python/Lib/site-packages` | 优先使用宿主 NumPy；不在运行时降级或替换 |
| OpenVDB | 13.0.0，`openvdb.cp313-win_amd64.pyd` | 使用 Blender 已带版本；不另带不同 ABI 的 OpenVDB |
| VDB Python API | `FloatGrid`、`createLinearTransform`、`write`、`read`、`FloatGrid.copyFromArray` 存在 | 仍须测数组轴顺序、符号、仿射变换、有效域和保存重开 |
| `bpy.app.binary_path` | 指向当前 `blender.exe` | 后台 Blender 的可执行入口由运行时取得 |
| `sys.executable` | 指向该 Blender 的 `5.1/python/bin/python.exe` | 本机可用的较轻后台 Python 入口，不硬编码全平台路径 |

Blender v5.1.1 的官方构建文件也固定 Python 3.13.9、NumPy 2.3.4 和 OpenVDB 13.0.0，与本机相符。[v5.1.1 `versions.cmake`](https://github.com/blender/blender/blob/v5.1.1/build_files/build_environment/cmake/versions.cmake)

另外直接执行该自带解释器的 `-I -c`，成功导入 NumPy 和 OpenVDB。`-I` 用于隔离用户 Python 路径；该结果证明本机存在无需外部 Python 的子进程路径，不证明其它平台或已安装科学 wheels 在子进程中自动可见。相同探测没有发现 `cclib`、`iodata`、`gbasis`、`scipy`、`periodictable`；不能借用用户另一个环境中的包作为发布验收证据。

项目已有 [体数据探测脚本](../../tools/probe_volume_nodes.py) 对有符号网格、轴顺序、剪切变换与原生等值面提供局部验证；该实验不能代替真实 Gaussian、ESP 采样或完整扩展安装验收。

## 3. 发布候选与实际依赖冲突

以下来自指定版本的 PyPI JSON 元数据和发布文件列表。`py3-none-any` 表示该 wheel 本身不含特定平台扩展；它的传递依赖仍可能包含二进制。源码分发包 `.tar.gz` 不是可直接随扩展使用的 wheel，纯 Python wheel 也不等于无需依赖。

| 发布候选 | 已发布 wheel / 日期（UTC） | 基础运行依赖 | 当前判断 |
| --- | --- | --- | --- |
| `cclib==1.8.1` | `cclib-1.8.1-py3-none-any.whl`，2024-03-18 | NumPy、SciPy ≥1.2.0、packaging ≥19、periodictable；Python ≥3.7 | 日志解析候选；元数据未限制 NumPy 2，但实际 Gaussian 解析仍须测 |
| `qc-iodata==1.0.1` | `qc_iodata-1.0.1-py3-none-any.whl`，2026-02-03 | NumPy ≥1.26.4、SciPy ≥1.13.1、attrs ≥21.3.0；Python ≥3.10 | 首版 FCHK 候选，后续可评估 WFN/WFX；与基线的版本范围相容，未实测运行 |
| `qc-gbasis==0.1.0` | `qc_gbasis-0.1.0-py3-none-any.whl`，2024-10-02 | SciPy ≥1.11.1、importlib-resources、SymPy；Windows 为 NumPy ≥1.22 且 **<2.0.0**；Python ≥3.9 | **不满足本机 Blender 5.1.1 的 NumPy 2.3.4 约束，不能直接选为合格运行包** |
| `scipy==1.16.3` | `scipy-1.16.3-cp313-cp313-win_amd64.whl`，2025-10-28 | NumPy ≥1.25.2 且 <2.6；Python ≥3.11 | 满足此基线的元数据范围与 wheel 标签；二进制加载和数值测试待做 |

来源：[cclib 1.8.1 元数据](https://pypi.org/pypi/cclib/1.8.1/json)、[IOData 1.0.1 元数据](https://pypi.org/pypi/qc-iodata/1.0.1/json)、[GBasis 0.1.0 元数据](https://pypi.org/pypi/qc-gbasis/0.1.0/json)、[SciPy 1.16.3 元数据](https://pypi.org/pypi/scipy/1.16.3/json)。以上为固定发布候选，不声称它们是所有项目的最新版本。

### 3.1 cclib 与 IOData 的候选依赖闭包

在复用 Blender NumPy 的前提下，已核查具有合适发布文件的候选集合为：

| 包 | 候选版本 | Windows / CPython 3.13 发布文件 | 继续带入的基础依赖 |
| --- | --- | --- | --- |
| cclib | 1.8.1 | `py3-none-any` | NumPy、SciPy、packaging、periodictable |
| qc-iodata | 1.0.1 | `py3-none-any` | NumPy、SciPy、attrs |
| SciPy | 1.16.3 | `cp313-cp313-win_amd64` | NumPy |
| packaging | 25.0 | `py3-none-any` | 无 |
| periodictable | 2.0.2 | `py3-none-any` | NumPy、pyparsing |
| pyparsing | 3.2.3 | `py3-none-any` | 无 |
| attrs | 25.3.0 | `py3-none-any` | 无 |

辅助包依据：[packaging 25.0](https://pypi.org/pypi/packaging/25.0/json)、[periodictable 2.0.2](https://pypi.org/pypi/periodictable/2.0.2/json)、[pyparsing 3.2.3](https://pypi.org/pypi/pyparsing/3.2.3/json)、[attrs 25.3.0](https://pypi.org/pypi/attrs/25.3.0/json)。这里只选择基础依赖，不启用 `all`、`bridges`、`dev`、`test`、`pyscf` 等 extras；是否需要额外桥接能力须由真实调用决定。

这一集合解决的是解析候选的部署，不足以完成 MO/密度/ESP 的求值目标。Blender 自带 NumPy 作为宿主依赖必须写入支持矩阵并校验版本；build 时不能简单让依赖下载器再取一个不受控的 NumPy wheel。

### 3.2 GBasis 的具体未决门槛

`qc-gbasis==0.1.0` 在 Windows 上的 NumPy 上界与基线冲突；把该 wheel 强行解包后跳过依赖检查，不能消除冲突。NumPy 1.26.4 的 PyPI 发布文件也没有 CPython 3.13 wheel，不能用“顺便带一个旧 NumPy”解决。[NumPy 1.26.4 发布元数据](https://pypi.org/pypi/numpy/1.26.4/json)

固定开发提交 `071969c900d6d7a9fbbdfe193c65ba3be177fbdf`（2026-09-16）已经声明 NumPy ≥2.0，但改为 `scikit-build-core` / CMake 构建；Windows 配置强制 gcc/MinGW，构建从上游获取并编译 libcint/qcint v6.1.2。它是新的原生构建与分发工作，不能把 0.1.0 的纯 Python wheel 可用性套在这个提交上。[固定提交 `pyproject.toml`](https://github.com/theochem/gbasis/blob/071969c900d6d7a9fbbdfe193c65ba3be177fbdf/pyproject.toml)、[固定提交 `CMakeLists.txt`](https://github.com/theochem/gbasis/blob/071969c900d6d7a9fbbdfe193c65ba3be177fbdf/CMakeLists.txt)

推荐先在 M0 资格验证该固定来源是否能由维护者预构建为目标 wheel，并完成 NumPy 2、AO 约定和真实波函数数值验收。所有编译工具仅存在于开发/构建环境，不向插件用户提出安装要求。若需要修改第三方源码或自行分发 wheel，须记录准确补丁、来源、许可证和构建过程，并重新核对分发渠道要求；不能修改 wheel 的 NumPy 约束后直接声称兼容。若固定源码构建或科学验收失败，再比较能够随插件分发的成熟兼容求值后端，以同一组 FCHK/MO/密度/自旋/ESP 用例选定一个；内置求值是首版发布门槛，不能后移。

这项门槛未通过前，设计保留完整轨道/密度/ESP 目标及其待实现状态；不能用仅导入 Cube 的结果宣称完整首版已完成，也不为绕开依赖问题重写整套量化解析器或求值器。

IOData v1.0.1 `pyproject.toml` 的许可证声明是 GPL-3.0-or-later，根 `LICENSE.txt` 为 LGPLv3，`formats/fchk.py` 文件头为 GPLv3+；本次已经核对到此不一致。最终打包需要核查实际 wheel 内容和上游声明，保留对应通知及来源材料，不能只读仓库自动识别标签。[固定发布元数据源码](https://github.com/theochem/iodata/blob/v1.0.1/pyproject.toml)、[固定发布 LICENSE](https://github.com/theochem/iodata/blob/v1.0.1/LICENSE.txt)、[固定发布 FCHK 文件头](https://github.com/theochem/iodata/blob/v1.0.1/iodata/formats/fchk.py)

## 4. 扩展打包约束

`blender_manifest.toml` 应声明实际通过验收的 Blender 范围和 `platforms`，列出 `./wheels/` 下确实随 ZIP 提供的文件。`platforms` 是扩展支持平台，wheel 文件名另有解释器、ABI 和平台标签，两者都须匹配；未验证的平台不写入支持列表。用户已确定首发 Windows x64 + Blender 5.1.1，其它平台逐个验证后发布。[Blender 5.1 manifest 字段](https://docs.blender.org/manual/sl/5.1/advanced/extensions/getting_started.html)

打包应满足：

1. 使用准确 wheel 文件名与 SHA-256；包含全部未由宿主提供的基础传递依赖。`cp313`、`cp313t`、`cp312` 不能互换；不同 CPU 架构或操作系统的二进制不能混装。
2. NumPy 与 OpenVDB 由已认证 Blender 提供；wheel 的 Python 标签匹配并不自动保证 NumPy C ABI 或原生 DLL 相容。不得把外部环境的 `site-packages` 整目录复制进扩展。
3. manifest 的 wheels 不会替代维护者在构建时解析依赖；安装后逐个核对实际导入版本和 `module.__file__`，确认没有借到用户已有的其它包。
4. 运行时只加载已随包提供的能力，不执行 pip/uv、联网补装、下载编译器或构建 wheel。若缺失包/不兼容，应在相关能力入口报告准确原因。
5. 读写计算文件、缓存和导出产物需要说明 `files` 权限。首版离线导入与显示不需要 `network` 权限。发布到 Blender 官方平台与本地 Install from Disk 是不同交付检查。

Blender 文档要求捆绑未修改的 PyPI wheels 及其依赖，官方平台另要求遵守扩展审核规范；自行构建或修改过的第三方分发包不可直接假定符合官方平台要求。[Blender Wheels 要求](https://docs.blender.org/manual/id/5.1/advanced/extensions/python_wheels.html)、[官方平台审核规范](https://developer.blender.org/docs/features/extensions/moderation/guidelines/)

### 共享依赖并非每个插件一个虚拟环境

Blender v5.1.1 `wheel_manager.py` 把扩展 wheels 安装到扩展目录下的共享 `.local/lib/python3.13/site-packages`，同名 wheel 版本会去重；`addon_utils.py` 将该路径放到内置 site-packages 之前。因此一个插件声明了固定版本，不保证其它扩展共存后仍导入该版本；尤其不能随包替换 NumPy 并认为只影响 QCBlender。[v5.1.1 wheel 管理源码](https://github.com/blender/blender/blob/v5.1.1/scripts/modules/_bpy_internal/extensions/wheel_manager.py)、[v5.1.1 路径初始化源码](https://github.com/blender/blender/blob/v5.1.1/scripts/modules/addon_utils.py)

首版采用官方 wheel 机制，启动时核对科学后端实际版本/来源，并把“干净安装”与“多扩展共存”分开验收；不预先建立另一套依赖管理器。若实际共存测试暴露不可满足的版本冲突，再决定是否将科学后端隔离到插件自有命名空间或独立子进程的专用库路径，并单独验证打包及许可证要求。

## 5. 后台计算仍属于单插件

Blender 官方明确说明 Python 线程不能随意与 Blender 主循环并发，后台线程即使看似只做下载也可能导致崩溃；并指出 `multiprocessing.Queue` 本身可能使用线程。科学任务采用进程隔离，主线程使用 Blender timer / modal 回调读取进度，避免后台线程接触 `bpy`。[Blender Python Threads 限制](https://docs.blender.org/api/5.0/info_gotchas_threading.html)

推荐首个实现通过 `bpy.app.binary_path` 启动当前 Blender 的 headless 子进程，参数包括 `--background --factory-startup --disable-autoexec --python-exit-code 1 --python <插件内入口脚本> -- <请求文件>`。这条路径复用同一 Blender 与原生库，入口脚本只加载插件科学模块，不注册 UI、不递归启动任务、不读取用户场景。

插件用参数列表和 `shell=False` 启动进程；Windows 隐藏控制台窗口。启动后保存句柄和 PID，取消、超时、扩展禁用和主场景切换都只处理本插件启动的任务。stdout/stderr 写入任务日志，状态文件由 timer 读取，避免无人消费的管道填满导致挂起。返回码、结构化结果与日志分别保留，不能把“没异常文本”当作成功。[Python 3.13 subprocess](https://docs.python.org/3.13/library/subprocess.html)

任务输入包含请求版本、任务 ID、源文件哈希、数据集与网格参数；输出先写入该任务目录，校验完成后再发布。主线程只接收仍属于当前请求的结果，取消或失败不得覆盖已有成功数据。JSON 元数据和禁止 pickle 的 NumPy 数组足够完成首版进程边界，无需网络服务或跨环境 RPC。

`--factory-startup` 不等于一个完整的空用户扩展目录。后台启动须显式说明插件模块与 wheel 搜索路径的来源，只让经核验的扩展包和依赖可见；不能继承任意 `PYTHONPATH` 后获得偶然成功。路径设置必须在所有支持平台实测，确认不启用其它用户扩展、不修改用户 preferences。

本机已证实 bundled Python 也能直接工作；若 headless Blender 启动开销成为可测瓶颈，可改用经过资格验证的 `sys.executable` 入口。届时须重新证明 wheel 路径、原生库搜索、OpenVDB 和取消行为一致。这是内部实现替换，不增加外部 Python 安装要求。

Gaussian `formchk` / `cubegen` 仍仅作为用户已有的可选工具：二进制 CHK 转换与独立参考数据生成可使用它们，但插件在导入已提供的 Log/FCHK/Cube 并求值时不得依赖其存在。插件不分发 Gaussian 可执行程序。

## 6. 资格验证与发布验收

| 检查 | 判定依据 | 当前状态 |
| --- | --- | --- |
| Blender 运行时 | 实际二进制版本、Python/NumPy/OpenVDB 版本及模块来源与官方构建配置一致 | **Passed**：本机 Windows x64 / Blender 5.1.1 |
| 自带 Python 独立进程 | `-I` 导入 NumPy、OpenVDB 并输出实际版本 | **Passed**：本机直接解释器调用；生产后台任务未实现 |
| 发布文件可获得性 | 固定发布文件、标签、依赖元数据存在 | **Passed**：本表已列候选；只证明存在 |
| GBasis 0.1.0 Windows 依赖一致性 | Windows NumPy 约束应允许宿主 2.3.4 | **Failed**：要求 NumPy <2.0 |
| cclib / IOData / SciPy 集成 | 固定 wheels 在 Blender 中实际导入并解析真实文件 | **Not Run** |
| GBasis 固定源码构建 | 对目标平台构建、导入、AO/MO/密度/ESP 数值验收 | **Not Run** |
| 扩展构建与安装 | manifest 校验、ZIP 内容、离线 Install from Disk、启停与冷启动 | **Not Run** |
| 后台任务生命周期 | 成功、失败、取消、过时结果、重开和资源释放 | **Not Run** |
| 多扩展共存 | 实际版本来源不被不兼容共享 wheel 改变，卸载不破坏其它扩展 | **Not Run** |

发布前必须用新的用户资源目录完成安装，而不是在开发机现有 profile 上只检查 `import`。Blender 官方支持用 `BLENDER_USER_RESOURCES` 指向自定义用户目录；任务测试目录应放在仓库已忽略的 `outputs/` 下，不能覆盖用户正常配置。[Blender 5.1 目录布局](https://docs.blender.org/manual/sr/5.1/advanced/blender_directory_layout.html)

干净安装验收至少包括：断网安装 ZIP；没有外部 Python/conda/PATH 依赖；中文和空格路径；所选输入格式真实样本；MO/密度/ESP 与独立参考数值比较；取消大型网格任务；保存和冷启动重开；缺失缓存恢复；卸载/升级后的现有数据可用性。包内依赖可导入只是其中一项，不能覆盖科学正确性和节点视觉结果的验收。

## 7. 当前交付边界

- 首发 Windows x64 + Blender 5.1.1 已由用户确认；新增平台时，二进制 wheel、后台入口和离线安装都要增加证据。
- 必需科学依赖随 ZIP 分发已由用户确认；开发者预构建兼容后端，具体构建方案以 M0 证据选定，不向用户转嫁环境配置。
- 当前交付为可离线 Install from Disk 的 ZIP。用户未要求发布到官方平台，官方平台审核与实际发布另行处理。

单插件约束和轨道、密度、ESP 的科学验收要求适用于每个平台。
