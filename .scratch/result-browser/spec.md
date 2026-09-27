# 结果浏览

Status: resolved

在主目录的 `feat/result-browser` 实现 Gaussian 计算段预览选择和只读来源浏览。沿用现有 Dataset、worker、显示层及显式段号导入；不新增依赖或数据格式，不覆盖固定 SOP 候选。

## 验收

- Log/Out GUI 导入先异步预览段号、route、状态、行区间、能量与显式几何提示；取消不创建对象；确认时核对源摘要。直接脚本/MCP 段号导入保持兼容。
- 来源按源 SHA 与计算段分组，展示完整摘要、解析器、量/单位、几何/色场及外部来源；未知值显示未记录，断裂关联明确报告。按需读取，不在重绘时加载数组。
- 多段、失败/未完成/无几何、源变化、同名异源、多视图、双场及外部结果均有检查；复制/撤销/重开保持身份和数组摘要。
- 新候选独立安装，Computer Use 确认 GUI，MCP 复验，科学与相关 SOP 技术检查 Passed；人工签署单独维护。

## 任务

1. [计算段选择](issues/01-job-selection.md)
2. [来源浏览](issues/02-provenance.md)
3. [集成验收](issues/03-qualification.md)

## 验收记录

Agent 技术验证 Passed，详见 [结果浏览技术记录](../../docs/RESULT_BROWSER.md)。独立人工验收与发布批准 Not Run。
