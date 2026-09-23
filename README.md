# UT 规范与 Workflow Skill

这是独立的 UT Skill 项目，不属于原来的 base-agent-sdk-eval 仓库。当前版本为 1.0.2。

- [Skill 入口](skill/SKILL.md)：生成、维护、运行和审查 UT 的执行流程。
- [UT 质量规范](skill/references/testing-standard.md)：23 条可独立阅读的质量规则。
- [测试方法](skill/references/test-techniques.md)与[结果记录](skill/references/result-recording.md)：按需读取。
- [脚本测试](skill/tests/test_gate_report.py)：验证汇总脚本的行为。

使用方法：在支持 Agent Skills 的客户端安装 `skill/` 目录；已安装的个人副本位于 `~/.codex/skills/ut-workflow/`。

本项目没有配置远端仓库，不会向原仓库推送。目录中以日期命名的压缩包、清单与旧设计说明是先前版本的历史产物，不属于本次提交。
