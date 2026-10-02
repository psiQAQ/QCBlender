# 标准XYZ接入

Triage: ready-for-agent
Status: resolved
Blocked by: 无

## Acceptance

严格单/多帧解析、独立帧身份、切帧/测量/注释、公开小样本及科学层测试。

## Answer

已实现标准XYZ单帧和同原子数、同元素顺序多帧导入。严格预检拒绝扩展Properties/Lattice/PBC、余列、截断、非有限坐标及未知/dummy元素；帧间空行只在传入IOData的内存副本中规范化。原始文件SHA、逐帧SHA、UTF-8注释及来源行区间保留。采用锁定qc-iodata格式列适配器直接读取Å值，无再次单位换算。

多帧存入独立trajectory元数据及trajectory_positions(F,N,3)，scientific_geometry(kind='trajectory', step=1起帧号)返回不可写科学坐标及帧身份。current_geometry读取qc_trajectory_frame并拒绝缺失或冲突身份；XYZ Frame标签供测量/注释使用。无能量、波函数、优化或IRC推断。

新增blender/trajectory.py提供initialize_trajectory(obj,data)、set_frame(obj,data,frame)、CLASSES；qcblender.trajectory_frame操作支持PREV/NEXT/GOTO和frame字段。切帧准备注释后仅更新网格坐标与边，逐帧距离推断连接；保留POINT属性、原子顺序、选择、材质和节点。共享import accept、复制、注册/UI及外部科学来源关联由04集成；多帧关联须明确拒绝或显式固化当前帧，不能使用初始positions代替当前帧。

tests/data/xyz提供P03水二聚体单帧和P04三帧小样本；source.json记录CC-BY-4.0、贡献者归属、源FCHK及XYZ摘要，17位有效数字保留坐标。

Passed：22项纯Python测试（test_science_xyz 6、geometry 1、measurements 5、project 2、adapter 8），0 failures/0 errors；新XYZ模块及Blender模块AST检查、git diff --check通过。解释器C:/Program Files/Blender Foundation/Blender 5.1/5.1/python/bin/python.exe，-X utf8；sys.path显式包含本工作树、tests及D:/workspace/QCBlender/outputs/science，运行上述unittest模块。证据outputs/evidence/2026-10-02/display-xyz-export/xyz-science.json。

Not Run：工作树缺未跟踪local样本的优化完整回归；GUI、切帧可见操作、保存/移动冷重开、MCP/Computer Use及独立人工签署。由04/05在整合后候选验证，本任务的Passed仅代表上述科学层及语法检查。

## Comments

2026-10-02: 用户批准计划；各项初始pending，领取与证据在本任务记录。

2026-10-02: 按约定领取02并完成独占文件。主Agent追加授权measurements.py中trajectory帧标签的小改动。共享调用API及外部关联边界已消息交接；无新增依赖，无Blender启动/连接，无push。
