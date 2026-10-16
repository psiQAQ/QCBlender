# 圆弧中点引线与创建时朝向相机
Triage: ready-for-agent
Status: resolved

键角和二面角引线的起点放在所显示圆弧的角度二分点，保持文字位置与偏移规则。圆弧采样包含精确中点，避免引线落在弦内或偏离半角；正负二面角、180°、修改半径和构型更新均覆盖。零长/未定义圆弧保留现有无弧行为，不制造虚假几何。

四类文字创建时若存在活动场景相机，复用现有一次性朝向规则；仅转动本次新文字，之后相机移动、编辑及构型更新不自动重置朝向。无相机仍可创建。既有文字不在打开文件时批量旋转。

单一工作树 `fix/annotation-anchor`。先做实际路径回归，再最小实现、规定测试、真实Blender几何/GUI/保存冷读。用户已批准保全当前工程、关闭后验证和更新插件，最后恢复。沿用本地提交、快进与归档流程，不push、不新增依赖。证据入口 `validation/agent/acceptance/annotation-anchor.md`。

## Answer

技术验收通过，见 `validation/agent/acceptance/annotation-anchor.md`。按用户后续澄清恢复原保存工程，不以恢复草稿为目标。以后涉及 Blender 的任务先请用户关闭当前 Blender，确认退出后再开始，完成后打开原保存工程。
