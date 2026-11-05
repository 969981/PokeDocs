---
tags: [SV, Lua, bytecode, 5.4, Library, hash-recovery]
status: NATIVE_BYTECODE_READ
---

# SV 原生 Lua 字节码：Library 两份文件实测（2026-11-05）

> [!IMPORTANT] 两份文件**实际从用户 Library 的根目录读取**，不是只查看 TRPFD 索引。识别为 Lua 5.4 预编译字节码，并且都能按标准 5.4 原型结构解析到文件末尾。**Lua 文件头不能独立证明游戏版本一定为 4.0.0**；应与对应 RomFS 的 SHA-256 清单比对。

## 实测来源、Hash 和结构

| 检查项 | `main.blua` | `main_dynamic.blua` |
| --- | ---: | ---: |
| Library 路径 | `/main.blua` | `/main_dynamic.blua` |
| 文件大小 | 12,912,264 B | 5,342,713 B |
| SHA-256 | `c1a4f4e2625912cf0b739a642a79ba3357df0557a544b92da22a6cb139de2815` | `ae4a7d0168751f53af11746ac5ae7771cb1a5bfa580bcc0f79e2b9ee85acb572` |
| Lua 头部 | `1B 4C 75 61 54`（5.4） | 同左 |
| 完整解析出的 Proto | 37,743 | 7,036 |
| 最大原型嵌套深度 | 8 | 3 |
| 常量总数 | 332,220 | 119,617 |
| 全量 C/F/S/E Token 出现次数（含重复） | 139,711 | 37,277 |
| 不同 C/F/S/E Token（含种类） | 22,447 | 2,902 |
| 非根 Proto 中同时含 C、F 编码常量 | 7,355 | 1,021 |

两文件均能完整读取 `Code → Constants → Upvalues → Nested Protos → Debug`，没有尾部遗留数据。参考 Lua 5.4 官方 `lundump.c` 的相应读取顺序。

## Token 种类（不同 Hash 数）

| 文件 | C | F | S | E |
| --- | ---: | ---: | ---: | ---: |
| `main.blua` | 4,229 | 10,199 | 7,764 | 255 |
| `main_dynamic.blua` | 971 | 432 | 1,488 | 11 |

注意以上数字是**该字节码包含的不同编码 Token 数**，不是 PokeDocs 的新增命名数，不能直接算作 Hash 恢复。

## 本轮匹配实际结论

- 对两文件中约 79,088 个不同的可打印 ASCII 字符片段计算原样 64-bit FNV-1a Hash，仅有 307 个名字能命中**同文件现有 C/F/S/E 编码 Token**；与目前的 `PokeDocs/develop` 未命名表对账，**没有得到新名称**。
- 与此不同，已确认的原始 Token 现在可以建立具体 `file → Proto → 字符串常量索引／物理偏移` 证据；这比单纯枚举名称更有价值。
- 例如 `CFD9B049511E682DA`（历史候选 `main.ui.hud_info.HudInfoPlayer`）在 `main.blua` 中的多个原型常量表实际出现，包括非根 Proto 29002 与 29016；这能证明当前字节码包含此类 Token，**尚不能仅凭出现判定方法归属与行为**。
- 原来的 `2,945` 条未知名称仍保持未知；字节码包含它们的 Hash Token 也并不能凭空给出原始字符串。

## 可复现脚本

仓库新增 `scripts/inspect_sv_blua.py`：纯 Python 解析 Lua 5.4 字节码、按原型统计 C/F/S/E 编码常量、将真实普通字符串常量的完整 Hash 与 SV 或 ZA 未知项匹配，**只有精确匹配才输出候选**。

```powershell
python scripts/inspect_sv_blua.py "D:\\ROM\\main.blua" "D:\\ROM\\main_dynamic.blua" --game SV --output docs/sv-blua-native-audit.json
python -m unittest discover -s tests -v
python scripts/lua_hash.py verify
```

该脚本不执行 Lua，不上传或提交原始 `.blua`，也不会自动覆盖 Hashlist。运行结果 JSON 只保留 Hash、常量索引、位置和摘要。

## 下一段需要闭合的 C→F 关系

1. 结合标准 Lua 5.4 Opcode（`GETFIELD` / `SETFIELD` / `SETTABLE` / `CLOSURE` 等）对实际常量引用进行 PC 级追踪，区分 **定义**、**调用** 和 **普通引用**。
2. 将 `C...` 注册／prototype 字段赋值关联到对应的 `F...`，记录 `Proto ID`、常量索引、字节码 PC、调用者、被调者，验证后才升级语义证据等级。
3. 在补充真实源码字符串词典后，对剩余未映射 Hash 做精确匹配。单纯存在于字节码的 `C...` 或 `F...` 十六进制 Token 不等于恢复原名。

关联：[[Lua-Source-Evidence]]、[[Hash-Recovery-Round2]]、[[Hash-Evidence-Standards]]。
