---
aliases: [PokeDocs 知识库, Hash 知识库]
tags: [PokeDocs, Obsidian, reverse-engineering]
---

# PokeDocs · 技术知识库

此文件夹可直接使用 **Obsidian → Open folder as vault（打开文件夹作为仓库）** 管理。采用 Markdown、相对路径和双向 Wiki 链接，无需第三方插件。

## 阅读入口

- [[Hash-Algorithms|Hash 计算方法与校验向量]]
- [[Hash-Recovery-Workflow|未知 Hash 的候选恢复和回填操作]]
- [[Hash-Recovery-Results|2026-11-05 已恢复 Hash 审计报告]]
- [[Hash-Evidence-Standards|技术证据级别与可信度]]
- [[FileSystem-Hashes|FileSystem/GFPAK 哈希的研究边界]]
- [[Game-Index|SV / ZA / 其他游戏的资源入口]]

## 研究基线

- 当前算法已核验：`SV/Hashlists/Lua/lua_{c,e,f,s}_hashes.txt` 与 `ZA/Hashlists/Lua/lua_{c,e,f,s}_hashes.txt`。
- 本轮源数据恢复：65 个不同 64 位 Hash，合计 67 行；源记录与详细来源见 [[Hash-Recovery-Results]] 和 `hash-recovery-2026-11-05.json`。
- 仍空白的 Lua 行数：3,029（2026-11-05 快照），不是已经反推成功的值。
- ZA TRPAK 内部文件路径已有五组样本验证为同一 FNV-1a 64 变体；外层归档键与 GFPAKHashCache.bin 仍需独立验证。

## 代码与证据

- 实现：`../scripts/lua_hash.py`
- 测试：`../tests/test_lua_hash.py`
- CI：`../.github/workflows/lua-hash-validation.yml`
- 审计 JSON：`hash-recovery-2026-11-05.json`

所有实际文件内容以对应 Git 提交为准；此目录的记录可以随着新证据增量更新。
