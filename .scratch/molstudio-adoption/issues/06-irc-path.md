# 06 IRC 能量路径

Status: needs-info
Execution: implemented_real_sample_pending
Blocked by: none

## Delivery

使用者明确排列多个 FCHK 步序；读取对应构型与电子总能量，选择步时同步结构和能量位置。

## Acceptance

- 真实 IRC 序列与手工顺序核对；原子身份变化、缺能量和重复/漏步报错。
- Blender 逐步显示、工程冷重开、GUI 顺序操作有证据。

## Comments

由真实 FCHK 数值派生的构型序列通过显式步序、错误输入、Blender 步骤切换、能量曲线、保存重开及 GUI 撤销/重做检查。缺真实 IRC 序列，科学验收 `Not Run`。
