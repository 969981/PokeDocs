---
tags: [evidence, reverse-engineering, audit]
---

# Hash 证据级别与复核规范

| 等级 | 证据 | 允许结论 |
| --- | --- | --- |
| H0 | 仅有 Hash 值，无原字符串 | UNKNOWN |
| H1 | 发现命名规律，但尚未得到精确哈希匹配 | 候选，仅放报告 |
| H2 | 对原样 UTF-8 字符串计算的完整 64 位 Hash 等于目标、且唯一 | Hash 已匹配，可标注算法与来源 |
| H3 | H2 且有游戏脚本、字符串、函数注册或加载行为的独立证据 | 对象/功能语义已验证 |

本轮 67 行恢复属于 H2：其中有跨列表同名映射、序号或前缀推导，并且所有结果重新计算完整 Hash。只有回溯 Lua 字符串源或游戏实际消费者后才升级到 H3。

建议每条记录留存 `game`、`version`、`hash`、`candidate`、`hash_algorithm`、`source_file`、`source_line`、`method`、`commit_sha`、`confidence`。大规模匹配时保留原始 UTF-8 名称，检查同一 Hash 对应多个候选的碰撞。未知值不可用猜测冒充已恢复值。

本轮证据：[[Hash-Recovery-Results]] 和 `hash-recovery-2026-11-05.json`。