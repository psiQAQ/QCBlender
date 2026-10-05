# 05 精确候选推广工作流

Triage: ready-for-agent
Status: resolved
Blocked by: 03, 04

## 工作与验收

实施spec第6–7项及约定release-manifest交接，严格默认dry-run，复用确切artifact，异常停止和幂等附件补齐。覆盖错误run/tag/version、过期artifact、篡改包/wheel/报告、缺许可、重复/额外成员和重试冲突。许可复核/人工试装状态不伪造。无远端写入。

## Comments

2026-10-05：核对canonical alpha-core@4c26f2bee1ac0a65fb8c1d39db86c310b374fb47的03已resolved，04研究于本分支5d6ab9b完成后领取。候选接口以已验收03实现为准；发布核验、草稿推广及独立门禁记录归本任务，远端执行交09/10。

## Answer

已实施仅默认分支手动调度、dry_run=true 的 extension-release.yml。技术核验检查直接指向commit的注释tag及main可达性、manifest/tag/run版本与提交、成功同仓workflow、唯一未过期artifact、完整附件/报告SHA及tag源码和锁定wheels。写权限单独置于release环境的draft job，复核后只上传原始五份附件，永不自动公开；环境reviewer配置仍须管理员另行确认。

独立qcblender.release-gates.v1绑定确切run/artifact/commit/ZIP，Passed需真实reviewer、日期、说明及实际证据SHA。许可复核记录未通过时允许只读技术dry-run并明确draft_readiness Failed，禁止草稿写入；人工试装/公开批准保持真实状态，Agent不代签。重试仅补缺失附件，已有摘要冲突或公开后不完整直接失败；上传中断保存release Failed与实际错误，保留已核验技术范围。

候选及推广共用public_reproduction.py的scene→Dataset→数组/VDB精确成员与摘要核验，拒绝未引用qcdata文件/未知许可原件；qualify同步扩展全成员清单。候选顶层dependencies绑定锁SHA、host-provided版本、各bundled wheel元数据/SHA及qualification backend，推广端逐项复核。两份锁与build-requirements.txt原字节未改。

Passed：43项候选/发布边界测试；整合显式stdlib集合114项（0 errors/failures/skips，-I -S -B），报告outputs/ci/stdlib-release-integration.json；8份相关Python文件py_compile、git diff --check、原锁内容比对、两CLI --help。测试中的合成科学/Blender字节与HTTP mock只隔离打包、记录和API边界，不代替原生/数值或真实远端证据。真实Git fixture验证轻量/嵌套tag拒绝、版本/main可达性。

只读窄审查确认并修复额外未知许可文件漏检，拒绝回归已覆盖；修复后的独立复审因模型capacity未执行，交07最终Standards/Spec分轴复审。实际候选CI、GitHub草稿上传、release环境reviewer配置、许可判定、独立人工Alpha试装、公开批准/下载摘要及Blender Extensions均Not Run，保留09/10和正式v1既有门禁。未推送、未运行Blender、未发布。
