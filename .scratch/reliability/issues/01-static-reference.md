# 01 外部分析静态参考

Triage: ready-for-agent
Status: claimed
Blocked by: none

## 范围与验收

遵循spec第一批1。保存真实P04默认比较/当前步骤不一致的失败证据；入口拒绝动态Dataset和绑定祖先，静态P03/普通静态Log不回退。begin后换绑定、删除对象、切换构型在accept前拒绝且无新增对象。AIM/NBO/ETS/IGMH/IRI以及相关外部入口共享最小守卫，不改手动关联语义。单元与原生脚本先红后绿；主Agent串行原生和GUI验证。

## Comments

2026-10-05：领取。文件归属为静态参考helper、external_fields/external_results/nbo/capabilities及worker必要入口、相关专属测试脚本；不修改jobs/ui/project/views。
