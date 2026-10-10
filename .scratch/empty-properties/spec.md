# 空场景属性入口修复

修复没有活动对象时调用 `qcblender.open_properties` 引发的动态 RNA 枚举报错，保持有效对象的属性跳转及渲染、输出入口可用。依赖与版本不变。

验收：真实 Blender 5.1.1 窗口复现原错误；对象缺失时返回 CANCELLED、提示选择对象且不改变属性页或固定对象；有效对象及渲染、输出跳转通过；重新构建、安装并核验 `validation/shared/install/qcblender-0.1.0.zip`。
