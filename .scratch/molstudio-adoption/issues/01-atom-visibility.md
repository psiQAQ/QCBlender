# 01 显示快捷控制

Triage: ready-for-human
Status: resolved
Blocked by: none

## Delivery

在现有原子节点视图中隐藏氢、保留指定氢、恢复显示；仅更改视图选择，不改科学数组，复制显示层后可独立控制。

## Acceptance

- 实际 Blender 中验证氢/非氢原子及相连键的显隐、无氢分子、非法编号。
- GUI 撤销/重做、保存重开和原科学数组摘要一致。

## Answer

Blender 5.1.1 的 `tools/verify_atom_visibility.py` 与 `tools/verify_visibility_gui.py` 通过氢/非氢、无氢、非法编号、独立复制、源数据摘要、保存重开和 GUI 撤销/重做检查。独立用户验收另行进行。
