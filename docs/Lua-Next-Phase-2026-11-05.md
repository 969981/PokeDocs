---
tags: [PokeDocs, SV, ZA, Lua, hash-recovery, H2, Obsidian]
status: HASH_EXACT_CANDIDATES_NATIVE_IDENTITY_UNCONFIRMED
date: 2026-11-05
---
# Lua Hash 下一阶段：SV C 命名空间 / ZA S、F 精确候选

> [!IMPORTANT] **本次是 8 条新增完整 64 位 Hash 精确匹配（H2）**，不是原生 Lua 源码名字复原或游戏内运行时确认。命名空间与函数动词是已命名表中的组成词，组合后仍须逐项原生验证；不要把 H2 当成 H3。

## 基线、结果

前一轮 [[SV-Resources-Research-Sync-2026-11-05]] 记录未命名 SV C 1,338、ZA F 43、ZA S 116，全部 SV/ZA 未命名合计 2,402。此轮通过严格 64 位复算新增 **SV C 4、ZA F 2、ZA S 2**。回填后对应 **SV C 1,334、ZA F 41、ZA S 114**，全表未命名 **2,394**。其余类型均未修改；旧阶段报告保留历史基线。

## SV C：已知命名空间 × 已知类尾名

| 原始 C 行 | 64 位 Hash | 新增 H2 候选 | 命名空间证据 / 类尾名证据 |
| ---: | --- | --- | --- |
| 1,443 | 70015E8033B89DAE | dll_danbattle.ai.danpokemon.IDanPokemonTransitionModel | 109 / 459 |
| 3,252 | FC3ACA6C64B990C2 | dll_danbattle.ai.danpokemon.IDanPokemonController | 109 / 1,952 |
| 2,916 | E3A24AF074805F8B | dll_stadium.BattleSpotRankData | 1,368 / 748 |
| 2,057 | 9EB6F0A209502CC5 | dll_stadium.RankUtil | 1,368 / 2,204 |

- **完整搜索空间：** 从 develop 当时的 1,948 条已命名 SV C 提取 604 个已知命名空间与 1,940 个不同的类尾名，交叉枚举 1,171,760 个组合，仅有上述四个此前空白 Hash 完整命中。
- 类尾名确实源自其它已命名完整 C，命名空间确实源自已命名完整 C，但**不能由此断言候选所属程序集、类的真实业务职责、实例化或注册时机**。
- 详细源行和算法：[[evidence/lua-next-phase-2026-11-05.json]]。原有 C→F 的 23,727 条静态归属和 C→S/全局注册证据见 [[SV-Library-BLua-CF-Assignments]]、[[SV-Resources-Research-Sync-2026-11-05]]。本轮没有声称逐条验证这四个 C 的原生注册链。

## ZA S/F：基于已命名动词的严格 Hash 变换

| 目标文件 / 行 | Hash | H2 候选 | 已知源名称与行号 |
| --- | --- | --- | --- |
| F:32 | 1E99CC9E5F95EAB9 | ExecuteBirthday | S:56 SaveBirthday |
| F:71 | 513FE6669D290F42 | GetRivalText | S:379 CreateRivalText |
| S:694 | D3B4BEF35117C82F | RemoveBousouAuraTag | S:264 AddBousouAuraTag |
| S:51 | 0EA2B6C4A18DBEE5 | RemoveChrAccessorForEventHandles | S:741 CreateChrAccessorForEventHandles |

检索对当前 ZA S/F 已命名记录进行动词替换、大小写与若干有界词形变换，约 88,438 个尝试；仅这四项命中当前空白。**这不是从 ZA 原生字节码取得的函数定义和方法调用**，即使第三方 ZAScripts 中有相似单词，也不能作为原生原名已证实的依据。

## 后续真正的原生归属闭合

1. SV C：重新在本机输入两份已知 SHA-256 的 original main.blua 和 main_dynamic.blua，输出 C→prototype→F 的完整 TSV.gz，按高信息量已命名 F 方法签名分组，筛出 1,334 条 C 的近邻与可疑命名空间；结合 C→S 静态定义和全局注册 PC 双向核对。本轮只有命名组合 H2，不能把类同名视为同一个运行时实例。
2. ZA：利用 pinned ZAScripts 的 Haxe 类/函数名作为**候选产生器**，独立读取对应版本原生 Lua 5.4 chunk，先确认 C/F/S/E 常量和 SETFIELD/SELF/CALL、闭包赋值的字节偏移，再核对每条候选的具体对象表来源。
3. 入表原则：只回填无歧义的 H2 精确匹配并保留审计原行；H3 必须有独立的原生字符串、注册关系或真实消费者证据，不自动提升等级。对缺失原始字节码的 ZA，不使用旧 SV 字节码替代。

## 核查

参照 [[Hash-Evidence-Standards]]、[[Hash-Recovery-Workflow]]，在仓库中运行：

~~~powershell
python scripts/lua_hash.py verify
python scripts/verify_sv_resources_import.py
python -m unittest discover -s tests -v
~~~

原始研究的 main.blua、main_dynamic.blua 不提交入仓库；此页仅提交精确候选和可追溯的行号证据。
