# M6 可组合节点与显示层

Status: ready-for-agent
Execution: complete
Owner: root
Blocked by: 04

## 工作

1. 提取不绑定具体对象的公共节点，体积数据与材质通过接口传入；保留科学数据单位、有效域和符号。
2. 显示层管理提供增删、复制、排序、可见性与独立样式控制；侧栏读取真实节点输入，节点编辑器允许自由组合，新增层保留用户连接。
3. 支持体积雾、正负等值面和标量颜色映射；显示透明度变换与物理量本身区分，原始科学数组不改写。
4. 验证多个源之间不串数据、样式可独立编辑、操作撤销与保存重开、已有采样/振动功能及原生离线安装；逐单元本地提交。

## 验收

几何与标量检查、实际界面/渲染检查、工程冷启动分别记录 Passed / Failed / Not Run。公共节点从源码生成，支持 Blender 5.1.1，不引入 MolecularNodes 5.2 的运行时依赖。排序表示显示层组织顺序；三维遮挡遵循 Blender 深度和材质规则。

## Comments

2026-09-23：追加范围技术验收完成。显示层增删/排序/视口与渲染可见性、网格/外层节点/材质独立复制、子对象变换保留 Passed；冷重开与 GUI 撤销/重做 Passed，窄侧栏控件调整后已检查面板截图。真实 Gaussian 水分子振动样本重新导入后，复制层的模式选择和 IR 高亮独立 Passed。等值面冷重开及标量采样回归通过。运行入口见 DEVELOPMENT.md；独立用户认可与对外发布继续归 M5。

2026-09-23：体积雾真实 Cycles 渲染 Passed：不透明度为零时无可见体素，连续透明度和正负颜色均有效，场缓存摘要不变；保存配套工程后冷重开图像一致（outputs/fog-acceptance/report.json）。显示层增删、复制、排序/可见性和冷重开 Passed，GUI 复制撤销/重做 Passed；正在调整窄侧栏布局并补齐最终回归与包资格。

2026-09-23：公共等值面资产首个单元 Passed。真实 Blender 5.1.1 离线重装、阈值/双相、缓存不变、取消和生命周期 Passed；重构后网格仍为 2068 顶点/2060 面。两个外层视图共享无绑定资产，独立阈值和源平移、保留原分支、资产库导出/加载 Passed（outputs/node-assets/report.json）。迁移目录冷重开 Passed；斜轴采样误差 1.08e-6、对象变换误差 2.27e-6、域外掩码 Passed。显示层管理、体积雾及其视觉验收仍待实施。

2026-09-23：用户确认完整显示层界面；已确认科学量加外部 Cube，新增分析量内置计算后置；使用 Blender 原生相机/出图。开始公共节点提取，后续新增范围分歧继续询问。

参考源码：MolecularNodes 子模块 5ad56c9cf33c4f82ceb3ca507d26d0cab6f7203c，entities/base.py 的 MolecularTree 分支组合、nodes/geometry/style_ball_and_stick.py 的显式公共接口、ui/panel.py 的真实 socket 控制。保留 QCBlender 的科学数据契约和 JSON/NPY 工程存储。
