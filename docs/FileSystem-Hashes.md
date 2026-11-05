---
tags: [filesystem, gfpak, hashes, unknown]
---

# FileSystem / GFPAK Hash 边界

本仓库的 `SV/Hashlists/FileSystem`、`ZA/Hashlists/FileSystem` 包含容器路径和文件内部 Hash 数据；各自与 Lua 符号表不同。现阶段只证明了 **Lua Hashlist 的 64 位 FNV-1a 变体**，不把这个结论自动外推到 GFPAK、TRPAK、TRPFD 或 `GFPAKHashCache.bin`。

## 路径 Hash 的验证顺序

1. 从目标游戏/版本提供至少三个同时具备**原始完整路径字符串和存储 Hash** 的独立实例。
2. 检查路径分隔符 `/` / `\\`、前导 `@arc`、大小写、UTF-8/UTF-16、扩展名以及是否加终止字节。
3. 使用实测样例分辨位宽、初始值、大小端和算法；不能仅凭一个巧合匹配定论。
4. 重算全量已知路径，统计匹配率；再用同一算法枚举有限模板补足缺失路径。
5. `GFPAKHashCache.bin` 还需要单独确认文件头、记录数、键值顺序、字节序与具体版本格式，不等同于简单把 .txt 文件改成 .bin。

对于缺失资源名，优先从实际资源归档/游戏字符串/上游证据中取得候选，再做 Hash 校验。路径 Hash 研究成果请另开专门脚本，不要混在 `lua_hash.py` 中，以免污染已验证的算法。

参考：[[Hash-Algorithms]]、[[Hash-Evidence-Standards]]。
