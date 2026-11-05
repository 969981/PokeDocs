---
aliases: [PokeDocs 知识库, Hash 知识库]
tags: [PokeDocs, Obsidian, reverse-engineering]
---

# PokeDocs · 技术知识库

此文件夹可直接使用 **Obsidian → Open folder as vault（打开文件夹作为仓库）** 管理。采用 Markdown、相对路径和双向 Wiki 链接，无需第三方插件。

## 阅读入口

- [[Hash-Algorithms|Hash 计算方法与校验向量]]
- [[Hash-Recovery-Workflow|未知 Hash 的候选恢复和回填操作]]
- [[Hash-Recovery-Results|第一轮：67 行 Hash 恢复]]
- [[Hash-Recovery-Round2|第二轮：84 行新增候选与来源审计]]
- [[SV-Resources-Research-Sync-2026-11-05|第三轮：同步 SV_Resources 的 543 条新映射与原生分析证据]]
- [[Lua-Next-Phase-2026-11-05|下一阶段：SV C 及 ZA S/F 新增 8 条精确候选]]
- [[Lua-Native-Join-2026-11-05|SV C 原生结构及 ZA S/F 证据调查队列]]
- [[Lua-Closure-Evidence-2026-11-05|新增：SV 95 条双重结构类和 ZA 四包原生 Opcode 的当前 Hashlist 对账]]
- [[ZA-Lua-Register-Flow-2026-11-05|ZA 2.0.2：原生 Lua 新增 922 条局部调用关系及五条缺失常量]]
- [[ZA-Lua-Closure-Receiver-2026-11-05|ZA 2.0.2：1,468 条已关联词法闭包及 926 条五类 C Hash 查找]]
- [[ZA-Lua-Upvalue-Captures-2026-11-05|ZA 2.0.2：926 条类键查找均回溯到根 Chunk Upvalue U0，27 条 CLOSURE 创建位置确认]]
- [[ZA-Lua-Host-ELF-2026-11-05|ZA 2.0.2：ExeFS main ELF Lua 环境与脚本路径的 13 个静态地址引用]]
- [[Lua-Proto-Owner-Join-2026-11-05|新增：ZA 1,461 条根级闭包归属及 27 条未匹配调用，SV 95 类接收者闭合边界]]
- [[SV-Lua-Factory-Metatable-2026-11-05|SV 95 类原生工厂、共享元表与 __name__ Hash 元数据核查]]
- [[Lua-Source-Evidence|Lua 源码与原生字节码审计]]
- [[SV-Library-BLua-Audit|Library 两份原生 BLUA 完整结构读取与对账]]
- [[Hash-Evidence-Standards|技术证据级别与可信度]]
- [[FileSystem-Hashes|FileSystem/GFPAK 哈希的研究边界]]
- [[Game-Index|SV / ZA / 其他游戏的资源入口]]

## 研究基线

- 当前算法已核验：`SV/Hashlists/Lua/lua_{c,e,f,s}_hashes.txt` 与 `ZA/Hashlists/Lua/lua_{c,e,f,s}_hashes.txt`。
- 第一轮恢复 67 行，第二轮再恢复 84 行；全部是精确 Hash 候选，证据见 [[Hash-Recovery-Results]] 与 [[Hash-Recovery-Round2]]。
- 第二轮历史快照剩余 2,945 行；SV_Resources 同步后新增 543 条候选，**该阶段剩余 2,402 行**（SV 2,243 / ZA 159）；下一阶段 8 条 H2 匹配后**当前剩余 2,394 行**，详见 [[Lua-Next-Phase-2026-11-05]]。Hash 精确匹配的名称仍按 H2 标识，见 [[SV-Resources-Research-Sync-2026-11-05]]。
- ZA TRPAK 内部文件路径已有五组样本验证为同一 FNV-1a 64 变体；外层归档键与 GFPAKHashCache.bin 仍需独立验证。

## 代码与证据

- 实现：`../scripts/lua_hash.py`
- 测试：`../tests/test_lua_hash.py`
- CI：`../.github/workflows/lua-hash-validation.yml`
- 审计 JSON：`hash-recovery-2026-11-05.json`

所有实际文件内容以对应 Git 提交为准；此目录的记录可以随着新证据增量更新。

- [[SV-Library-BLua-CF-Assignments|SV 字节码 C→prototype→F 的指令级关系与证据]]

- [[SV-Library-BLua-F-Dispatch|SV 16 处未知 F 的 SELF→CALL 调用链与对象来源]]
