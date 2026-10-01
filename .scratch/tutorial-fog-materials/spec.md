# 体积雾材质槽与显示参数同步

## 目标

新建体积雾将实际 GN Material 输入材质同时绑定到载体 mesh 材质槽，使 MATERIAL 视口响应 Opacity Scale 与 Opacity multiplier 编辑。

## 范围

- 保持 GN 接口、显示传递函数、依赖和科学数组不变。
- 复制显示参数时同步目标 fog 已有的同材质槽及 GN 输入，并在失败时恢复全部引用。
- 无材质槽的已有工程仍可复制参数。加载工程及启用扩展时，仅对本地可编辑 fog Mesh 的唯一明确 QC fog GN 材质补齐同指针槽，保留已有槽并避免重复；linked/read-only 对象及数据跳过。保存回调不执行迁移，卸载完整移除加载 hook 与一次处理 timer。
- 扩充现有 Python 策略测试和 Blender fog / 参数复制验证。

## 验收

- 新 fog 的材质槽与 GN Material 指向同一材质；复制层保持引用一致并拥有独立材质。
- 复制显示参数保持材质槽与 GN 引用一致，保留目标裁剪及无关材质槽；失败回滚引用。
- 现有非科学 Python 测试 Passed。
- 安装候选的 MATERIAL 视口即时响应、渲染及冷重开由主 Agent 串行验收；未执行时记录 Not Run。
