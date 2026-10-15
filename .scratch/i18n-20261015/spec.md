# QCBlender 全界面双语与全局安装
Triage: ready-for-agent
Status: resolved

## 目标
按 Blender 界面与工具提示翻译设置显示简体中文或英文，覆盖全部插件界面、原生对象自定义属性中的已知 QC 行、节点接口与资产目录。统一 SOP 数学术语：并集、交集、差集。

## 约束
不改科学数据、操作 ID、属性键、asset ID、catalog UUID 或 socket identifier；保护用户改名与外部属性，旧工程映射有歧义时明确报告。英文为规范消息；其它语言回退英文。不得新增依赖、push、发布或删除旧包/用户工程。

## 用户批准的交付
独立工作树分工与本地整合归档；将当前工程另存自包含副本后串行冷重开；构建并验收双语候选后备份更新全局 Blender 5.1 插件与当前 ZIP，恢复原语言并打开保全工程副本。单 Blender 进程。

## 验收
词条与占位符、SOP、稳定映射、注册生命周期、语言切换、七种局部选择模式、原生属性悬停、节点/资产、用户改名和旧工程、科学数组与连接参数不变；真实 GUI、自动化及独立人工验收分开记录。

## 任务
- [01 翻译基础与原生属性](issues/01-core.md)
- [02 节点与资产兼容](issues/02-nodes.md)
- [03 界面与动态文案](issues/03-ui.md)
- [04 教程同步](issues/04-docs.md)
- [05 整合与全局安装](issues/05-integration.md)
- [06 空目录清理残留](issues/06-cleanup-residue.md)：产品任务完成后单独跟踪权限拒绝，不阻塞已完成的全局安装。

## Answer

实现与本批验收完成；证据与边界见 [双语验收](../../validation/agent/acceptance/i18n.md)。独立人工及科研签署 Not Run。
