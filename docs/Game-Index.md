---
tags: [SV, ZA, LA, SWSH, LGPE, files]
---

# 资源索引

| 游戏 | 现有路径 | 内容 |
| --- | --- | --- |
| SV（朱／紫） | `SV/Hashlists/Lua/` | Lua 名称哈希 c/e/f/s |
| SV（朱／紫） | `SV/Hashlists/FileSystem/` | TRPAK／FD 相关文件哈希与缺失列表 |
| SV（朱／紫） | `SV/Flatbuffers/` | 归档、场景、模型等 FlatBuffers schema |
| ZA | `ZA/Hashlists/Lua/` | Lua 名称哈希 c/e/f/s |
| ZA | `ZA/Hashlists/FileSystem/` | 文件哈希 |
| ZA | `ZA/Flatbuffers/` | 如仓库现有则保留其原始结构 |
| LA（阿尔宙斯） | `LA/Flatbuffers/` | 数据结构 schema |
| SWSH（剑盾） | `SWSH/Flatbuffers/` | 数据结构 schema |
| LGPE | `LGPE/Flatbuffers/` | 数据结构 schema |

表中 c/e/f/s 依据来源文件名区分；其“类/枚举/函数/字符串”的具体语义需要结合实际 Lua 结构验证，不能单凭文件名确定全部类别。

恢复数据遵循 [[Hash-Recovery-Workflow]]；文件系统路径另见 [[FileSystem-Hashes]]。

已确认 ZA TRPAK **内部**路径哈希计算，见 [[FileSystem-Hashes]]；这不等同于外层归档 Hash 或缓存文件格式。
