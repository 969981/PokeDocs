---
tags: [SV, ZA, Lua, bytecode, Haxe, Obsidian]
status: NATIVE_STATIC_RELATIONS_JOINED_NAMES_UNCONFIRMED
---
# SV / ZA Lua 原生证据关联队列

原生 SV 4.0.0 的两份完整 Lua 5.4 文件的 SHA-256 已再次确认；严格 C→prototype→F 指令链重新得到 **23,727 条**不同赋值关系（main 18,991，main_dynamic 4,736）。这是实际字节码的静态赋值，不是运行时调用次数，也不意味着未知 C 名称已经恢复。

## SV：当前 1,334 个未知 C 的分组

| 队列 | 数量 | 下一步 |
| --- | ---: | --- |
| 直接 C→prototype→F 定义 | **1,047** | 用完整 method-closure TSV 追踪 F / child Proto |
| 无直接 F、存在 C→S 静态闭包（可能同时全局注册） | **101** | 对照 S 赋值和 child Proto |
| 无直接 F/S，仅全局类注册 | **110** | 追踪注册对象创建链 |
| 只有其它原生字段引用 | **24** | 继续核对 receiver 和字段来源 |
| 支持的模式未定位 | **52** | 扩展来源范围，不宣称文件中不存在 |

上述按当前 Hashlist 与旧原生 299 条“无直接 F”集合对账，其中 **12 条已命名**，余下 287。其余 1,047 具有严格 C→F 方法定义。原始 299 条研究中的 C→S **281 条边**、全局注册 **213 条边**、phase4 残留 **80 条**；这些是旧基线的边数，不是目前 287 的全部边数。本轮逐 C 索引保留原始 PC，**但尚未附上全部 23,727 条 F 的 PC 细表**，后者可用本仓库 trace_sv_lua_c2f.py 从完整原文件重算。

## ZA：当前 114 S / 41 F 的待查优先级

固定版 Haxe 重建索引中的 **256 条引用**涉及全部 114 个未知 S。其余 41 个 F 在此索引中没有引用。排行按 CALL / WRITE / READ / DECLARATION 的数量排序，**分数不代表原名的可信度**。

ZA 2.0.2 的 12145–12148 四个 Lua 包已在 TRPFD 定位，但本次固定源尚未发布四份经校验的 Lua 内容和 Opcode crosswalk。必须先实际解码四包并验证 SHA-256、Lua Header、指令 PC、字段接收对象，再交叉比对这些 Haxe 引用；任何第三方可读名称都不能仅因 Hash 相同而升级为原生确认。

## 可复核文件

- [SV 未知 C 原生证据队列](evidence/lua-join-2026-11-05/sv-native-class-queue.tsv)
- [ZA 未知 S/F Haxe 优先级队列](evidence/lua-join-2026-11-05/za-haxe-queue.tsv)
- [固定版本及统计](evidence/lua-join-2026-11-05/summary.json)
- [六份 pinned 原始 TSV](evidence/lua-join-2026-11-05/upstream-sv-unknown-c.tsv)（该目录内保留全部固定输入）

SV 来源：[SV_Resources 固定提交](https://github.com/969981/SV_Resources/tree/4619e7da6d2d9c6faab4eb0d5f3a2d6c8ef0e046)；ZA 来源：[ZA_Resources 固定提交](https://github.com/969981/ZA_Resources/tree/30bd7b29277844bfe41c5efe54739471bed12766)。没有把任何未知 Hash 自动回填成猜测名称。

关联：[[SV-Library-BLua-CF-Assignments]]、[[Lua-Next-Phase-2026-11-05]]、[[Hash-Evidence-Standards]]。
