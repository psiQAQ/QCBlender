# M5 发布与工程验收

Status: ready-for-human
Execution: in_progress
Owner: root
Blocked by: 01, 02, 03, 04, 05

## 工作

完成科学数据持久化、冷重开/移动/恢复、离线扩展安装、资源释放、渲染导出、性能和用户文档。

## 验收

2026-09-23 M7 技术候选：包 `outputs/dist/qcblender-0.0.1.zip`，50,416,340 bytes，SHA-256 `89af04ad4f5ed975a60d3e981c85b9cd285ee201af7b09afd5a8f9fc7e95570d`。可组合节点、相位透明度、多种样式、体积曲线、裁剪与游标采样技术验收 Passed；节点、渲染、振动/IR、冷重开与 GUI 证据纳入 `outputs/qualification.json`。独立用户认可与发布仍未完成。

主设计V01–V08技术验收均通过；交付ZIP和可复现证据。独立用户认可另行记录，Agent不能代签。

## Comments

2026-09-23：M6 新增公共等值面/体积雾与完整显示层管理后，原生离线安装、字段采样/冷重开、体积渲染/冷重开、独立材质与模式/IR 复制、GUI 撤销/重做 Passed；面板截图已检查。当前 ZIP 50,406,906 字节，SHA-256 `ac799835e4a9292ec5b6a6a08bc5a5700a73c277caced0cb391c7c9123ef56b7`。`outputs/qualification.json` 已核对工作区源码及 11 个随包 wheel，并纳入三份新增报告。独立用户复做、VMD/VESTA 外部图像对照和发布复核仍未完成。

2026-09-22：从已提交源码的独立复建揭示 Blender 宿主的 Win32 长路径限制：289 字符缓存数组存在但读取失败，实际重复场缓存未命中。现于科学存储/复制/归档层采用扩展 Windows 路径，对外路径保持原格式。原失败配置的缓存、冷重开、保存失败回滚与恢复复验 Passed；新增 tools/verify_storage_paths.py 在 Blender 中验证真实长路径，20 项科学回归 Passed。当前 ZIP 50,401,929 bytes，SHA-256 e2edbd8aff841a9a491f8e0ab093b1c7247d03e138c041ff054064f3a0a927b0；资格汇总 Passed。复建条件和失败定位记入 docs/CHANGELOG.md。独立用户认可及外部视觉对照继续未完成。

2026-09-22：已有开发已按逻辑单元本地提交：01ca63f 仓库约定与参考子模块、a19d2d5 设计与路线、7e9c29a 科学数据层与求值、21e4221 Blender 功能与工程持久化、91d8257 离线构建与验收。核对 Git HEAD 中 17 个科学样本原始字节，SHA-256 全部匹配来源记录；tools/qualify_package.py 对当前 ZIP 的源码、wheel 校验和与已记录技术验收汇总 Passed。未推送；M5 剩余验收边界保持不变。

2026-09-22：继续验收发现并修复保存失败的索引回滚；旧索引/首次无索引两种实际 Blender 失败场景 Passed。模式、IR、能量列表及动画参数冷重开通过，双场色标/文字图例冷渲染通过。11 个随包 wheel 的 RECORD/许可材料/来源核对 Passed，GPL/LGPL 上游声明差异保留。最新 ZIP 50,401,654 bytes，SHA-256 e1e0dae81c362aca6e0900c8a91d6ea07fd53e3a64bf304c68835caf10bb8070。VESTA 对照 Cube 已生成并按原数值回读；官方程序下载因 TLS/EOF 失败，外部渲染尚未执行。

2026-09-22：用户新增授权：已有开发分批本地提交，后续开发持续提交；推送与对外发布仍未授权。

2026-09-22：技术候选已交付，M5 保持 in_progress。50,401,050 字节 ZIP 的 SHA-256 为 4cbefb6fd3027ebc088fc2ff7ea736da804af687dd3cbd77686a078d8c3afe16；源码/包一致、wheel 摘要与报告汇总 Passed（outputs/qualification.json）。新配置离线安装、取消/缓存、移动后冷开、恢复、静态图/动画及用户/构建文档完成。独立用户复做、VMD/VESTA 同场景视觉比较、对外发布许可复核仍未完成；Agent 未签署人工认可，不宣称 M0–M5 全部发布完成。无提交或推送。

2026-09-22：.blend+.qcdata 原子保存、ZIP 打包、中文/空格目录冷重开、科学数组一致、缺失 VDB 重建及按 manifest 身份重定位 Passed。离线扩展安装、宿主库来源、生命周期和静态渲染 Passed。证据：outputs/acceptance/extension.json、recovery.json、mo8.png。首版 V01–V08 尚未整体完成；最终用户文档、发布材料、完整成图/动画和独立用户认可继续保留为未完成。

2026-09-22：由已确认设计路线建立；实施、启动/安装 Blender 和下载公开样例已获用户授权。未授权提交、推送或发布。
