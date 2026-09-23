# UT 项目配置与首次适配

规范保持跨项目稳定，模块路径、命令、预算与特例由项目配置决定。先读项目已有约定，能推断的从实际代码/配置确认，不为填表打断用户。仅在项目需要长期复用时新增 项目测试配置文档 或采用项目已有等价文件；禁止改写既有 AGENTS 来强行启用本规范。

## 最小配置形状

```yaml
profile_version: 1
standard_version: "1.0.2"
project_root: "."
modules: [] # 每项：path、language、runtime_version、test_framework
commands: [] # 每项：id、cwd、argv、purpose、external_effects、evidence
required_checks: [] # 当前项目/改动类别的必需检查；空不等于无须验收
coverage:
  mode: "not_configured" # disabled/report/enforce；enforce 必须有口径和阈值
  metric: null
  threshold: null # 比例 0..1，不猜测默认值
  exclusions: []
budgets:
  test_timeout_seconds: null
  task_time_minutes: null
external_execution:
  environments: []
  authorization: "follow_current_task"
exceptions: [] # 规则、范围、原因、批准记录、有效期/撤销条件、补偿措施
```

这是配置示意，不是能直接运行的配置。未确定字段写 unknown/not_configured，不用假命令填满。argv 优先数组，路径含空格时保持单独参数；执行前读取项目脚本内容，识别外部副作用。

## 发现顺序

目标模块配置/锁文件与脚本 → 相邻真实测试 → 模块 README/CI → 根目录文档。失效链接记录，不把缺失文件当已读；配置冲突以实际使用入口和项目约定核验。

先确认哪些测试会访问网络、模型、云资源、持久化数据或计费服务。默认离线 UT 应使用可控替身；真实调用是单独的集成/评测任务，不通过命名为 test 绕过授权。

## 适配检查

- 同一仓库可有多个模块、运行时和测试框架，不能用根目录命令覆盖所有模块的语义。
- REQUIRED 检查按变化风险选择；UNKNOWN 阈值、命令或版本不能被自动补成已确认。
- 项目需要独立 UT 审查时遵守；没有要求时不额外发明审批步骤。
- 缺少配置不阻止纯静态阅读与规划，但阻止声称对应执行门禁已完成。
- 以项目惯用命令为准，不把某个框架专用 flag 推广为所有语言规则。
