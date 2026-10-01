# 切片场绑定路径身份

## 目标与范围
修复同一 Dataset 的 Windows 路径分隔符、大小写和普通/扩展长度路径表示差异导致 bound_field 拒绝切片平面操作。仅修改 data.py 的纯路径规范化、source_browser.py 的 binding_key、专项纯 Python 回归测试、既有原生交互工具及本任务记录；保留 Dataset manifest hash、source identity 和 field metadata 守卫。

## 验收
真实纯 Python 回归测试覆盖混合分隔符、点段、Windows 大小写、长路径与 UNC 表示，并确认不同目录仍不同。主 Agent 在新候选上串行执行 ij/jk/ki/atoms 与冷重开；本 Agent 不启动或连接 Blender、MCP 或 GUI。实际 GUI 通过前状态保持 claimed。

## 基线与证据
- Base: b7090967e6618c15449efec278bcd47a0f018d54
- Branch: fix/tutorial-slice-plane
- 原失败：D:/workspace/QCBlender/outputs/evidence/2026-10-01/tutorial-cu/full/C04/atomic/slice-plane-GUI-failure.json
- Python os.path 官方说明：normpath 规范化分隔符和点段，normcase 在 Windows 规范化字符大小写。https://docs.python.org/3.13/library/os.path.html
- 身份规范化仅处理路径文本，不调用 realpath 或读取文件；保持绘制/缓存查询无科学数据 I/O。符号链接或 junction 指向关系不新增合并语义。
