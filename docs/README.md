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
- [[Lua-Source-Evidence|Lua 源码与原生字节码审计]]
- [[SV-Library-BLua-Audit|Library 两份原生 BLUA 完整结构读取与对账]]
- [[Hash-Evidence-Standards|技术证据级别与可信度]]
- [[FileSystem-Hashes|FileSystem/GFPAK 哈希的研究边界]]
- [[Game-Index|SV / ZA / 其他游戏的资源入口]]

## 研究基线

- 当前算法已核验：`SV/Hashlists/Lua/lua_{c,e,f,s}_hashes.txt` 与 `ZA/Hashlists/Lua/lua_{c,e,f,s}_hashes.txt`。
- 第一轮恢复 67 行，第二轮再恢复 84 行；全部是精确 Hash 候选，证据见 [[Hash-Recovery-Results]] 与 [[Hash-Recovery-Round2]]。
- 第二轮历史快照剩余 2,945 行；SV_Resources 同步后新增 543 条候选，**当前剩余 2,402 行**（SV 2,243 / ZA 159）。Hash 精确匹配的名称仍按 H2 标识，见 [[SV-Resources-Research-Sync-2026-11-05]]。
- ZA TRPAK 内部文件路径已有五组样本验证为同一 FNV-1a 64 变体；外层归档键与 GFPAKHashCache.bin 仍需独立验证。

## 代码与证据

- 实现：`../scripts/lua_hash.py`
- 测试：`../tests/test_lua_hash.py`
- CI：`../.github/workflows/lua-hash-validation.yml`
- 审计 JSON：`hash-recovery-2026-11-05.json`

所有实际文件内容以对应 Git 提交为准；此目录的记录可以随着新证据增量更新。

- [[SV-Library-BLua-CF-Assignments|SV 字节码 C→prototype→F 的指令级关系与证据]]

- [[SV-Library-BLua-F-Dispatch|SV 16 处未知 F 的 SELF→CALL 调用链与对象来源]]
