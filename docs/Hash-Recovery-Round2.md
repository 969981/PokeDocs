---
tags: [PokeDocs, SV, ZA, Lua, hash-recovery, evidence]
status: PARTIAL
---
# 第二轮 Lua Hash 映射（2026-11-05）

> [!IMPORTANT] 84 行是完整 64-bit Hash 精确匹配的**候选原名**，并未通过 SV 4.0.0 / ZA 的原生运行时调用链验证。

## 结果

| 类别 | 回填行数 | 证据 |
| --- | ---: | --- |
| SV C | 8 | 已验证道馆词替换 + 旧版 Lua header 对应关系 |
| SV S | 13 | 数字模板严格 Hash 对账 |
| ZA F | 14 | ZA 名称语法字典完整 Hash 对账 |
| ZA S | 49 | ZA 名称语法字典完整 Hash 对账 |
| **合计** | **84** | **84 个唯一目标 Hash** |

- 进入本轮时，SV/ZA 八份 Lua Hashlist 总计 3,029 行空白。
- 第二轮恢复 84 行；**剩余 2,945 行**。
- 第一轮的 67 行及其审计报告保留不变，参见 [[Hash-Recovery-Results]]。
- 来源补充映射共 118 条，已有 35 条由第一轮覆盖，剩下 83 条；另外从历史原始名称头文件恢复 1 条。

## 来源与版本

- [SV_Resources 固定提交](https://github.com/969981/SV_Resources/commit/d51a8134029e9504cf8a6911f7b37b8a47f54385) 的 `PokeDocs-Supplement/SV` 和 `PokeDocs-Supplement/ZA`：先前规则生成的 Hash 精确候选，仍为 H2。
- [SV-Script-RE 固定提交](https://github.com/Martmists-GH/SV-Script-RE/commit/1f843bd2517c707fbb47491dad58856eaa2c2cc7) 的 `data/lua_names.h:1902`：`main.ui.hud_info.HudInfoPlayer` 与 `0xFD9B049511E682DA` 精确对应；属于 SV 3.0.1 时期源码，不是 4.0.0 的直接证据。
- 对该历史 header 的完整 14,251 条记录进行了与当前 SV 已命名条目的比较，发现 4 条同 Hash 不同名的冲突；它们保留当前名字、不参与覆写（附见审计说明）。
- 4.0.0 的 `.blua` 已经在 TRPFD 索引定位，但尚未提取到仓库；只有索引不能证明 C/F 的实际调用和归属。

## 源码 Hash 恢复的优先级

1. 从 SV 4.0.0 的两个 Lua 包抽取原始 `script/lua/bin/release/main/main.blua` 和 `main_dynamic/main_dynamic.blua`，记录 SHA-256。
2. 验证字节码格式、版本、哈希 token 的实际存在性；再解析或反编译函数定义、原型对象与调用者。
3. 将直接来源于 Lua 源字符串的候选使用 `lua_hash.py` 对完整 64-bit 值检验，只有唯一匹配才入表。
4. ZA 也需要同版本 `.blua` / 字符串表才能进一步突破 C/E/F/S，而不是继续无条件造词。

## 完整逐项审计

`hash-recovery-round2-2026-11-05.json` 保留每一行候选的完整来源网址、证据版本、匹配策略、源文件与回填前行号。

## 名称示例

| Hash | 名称 | 来源 |
| --- | --- | --- |
| `0x31AF09FF3A7DA909` | `main.event.general.battle_talk.BattleTalk_mizu_leader_01` | gym_token_substitution |
| `0xFD9B049511E682DA` | `main.ui.hud_info.HudInfoPlayer` | historical_lua_names_header_encoded_identity |
| `0x002C3D9701768959` | `OBJECT_NAME_1090` | numeric_substitution |
| `0x11E7D6A8C52B3861` | `CreateFood` | dictionary_grammar_full64_match |
| `0xEFE8984381B69CBF` | `GetRewardItem` | dictionary_grammar_full64_match |
| `0xDF93F6D53E9597E3` | `ShowMessageWindow` | dictionary_grammar_full64_match |

对运行时身份与行为请遵循 [[Hash-Evidence-Standards]]。
