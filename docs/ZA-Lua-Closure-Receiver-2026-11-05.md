---
tags: [PokeDocs, ZA, Lua54, Trinity, C-F, C-S, caller, receiver, native-evidence]
date: 2026-11-05
status: NATIVE_LEXICAL_OWNER_VERIFIED_RUNTIME_RECEIVER_UNKNOWN
source_repo: 969981/ZA_Resources
source_commit: 11c693369fb07fc4566c5b57bcf5bb1a256fbb55
---

# ZA 2.0.2：Lua 原生调用者类关联、SELF 接收者与五类静态键

> [!IMPORTANT]
> 本轮从实际 ZA .blua 恢复了 **CALL 所在注册闭包（caller lexical owner）** 与部分**接收寄存器的静态类键查找（receiver static key）**。调用者类和被调用对象类并非同一概念，不能将静态键当作实例类型确认。实际恢复原始符号名称 **0**；ZA S/F Hashlist 未修改，未知基线仍为 PokeDocs 当前 **S 114 / F 41**。

## 固定原生输入与复验

ZA_Resources 四份完整、SHA-256 固定的 Lua 5.4 字节码，3,064 C→F 直接闭包、878 C→S 静态闭包以及 1,488 条局部字段→CALL 记录。

- [闭包归属与接收寄存器分析器](https://github.com/969981/ZA_Resources/blob/master/scripts/Join-ZA-Lua-Closure-Callers.py)
- [逐条原生证明 TSV](https://github.com/969981/ZA_Resources/blob/master/Unpack/v2.0.2/romfs/arc/data.trpfs/_index/lua-native/native-closure-caller-receiver.tsv)
- [原生核验统计 JSON](https://github.com/969981/ZA_Resources/blob/master/Unpack/v2.0.2/romfs/arc/data.trpfs/_index/lua-native/native-closure-caller-receiver-summary.json)
- [原生 CI](https://github.com/969981/ZA_Resources/actions/runs/42021695658)：合成测试 14/14、实际四包 SHA256 与字节码指令验证通过；[PR #2](https://github.com/969981/ZA_Resources/pull/2) 已合并。

## 已验证的 CALL 词法归属

| 关系 | 条数 |
| --- | ---: |
| 直接位于 C→F/C→S 注册闭包内部 | **1,461** |
| 词法嵌套在已注册闭包内部 | **7** |
| 不能联系到支持的注册闭包 | **20** |
| 有歧义/冲突归属 | **0** |

直接匹配的 1,461 条调用涉及 606 个不同的调用者类 Hash。7 条嵌套关联不等价于直接 C→F/S 注册，更不能视为 receiver 身份证据。

## 原生接收寄存器的 C Hash 查找：五个已有名字

1,488 条调用中，**926 条**有可复核的 GETTABUP 类 Hash 查找。这些键与 develop 当前完整 Lua C Hash 表中的已有名字对应：

| C Hash（不含 C 前缀） | 已命名符号 | 原生使用次数 | 被调用字段 Hash 去重 |
| --- | --- | ---: | ---: |
| 0C062DE5AED06885 | main.event.ik.command.IkScriptCommand | **908** | 57 |
| 3F97C0C63E0F98D5 | event_ik.CafeEvent | 8 | 5 |
| 08B9C9B723383177 | main.event.ik.command.CharacterCommand | 7 | 2 |
| E3A3A45F0BDA7426 | main.event.ik.ObjectTemplateDataManager | 2 | 2 |
| 0B6B8AD001243AFE | main.event.ik.command.FadeCommand | 1 | 1 |

名称核对：[ZA/Hashlists/Lua/lua_c_hashes.txt](https://github.com/969981/PokeDocs/blob/develop/ZA/Hashlists/Lua/lua_c_hashes.txt)；每行都是当前已存在的 C 映射，本轮未新增任何名称。

五类静态键查找的 Upvalue 槽编号分布为 0:922、1:2、2:2；无法仅凭槽编号无条件认定表必为 _ENV。IkScriptCommand 的 908 条调用涉及 457 个不同的直接/嵌套调用者类，而非 457 个 IkScriptCommand 实例。

## 保守接收寄存器回溯覆盖

| 类型 | 记录 |
| --- | ---: |
| UPVALUE_KEY_LOOKUP | 926 |
| UNKNOWN_OPCODE_BARRIER | 496 |
| SOURCE_OUTSIDE_WINDOW | 57 |
| TABLE_VALUE_FROM_DIRECT_UPVALUE_SLOT | 5 |
| CONTROL_FLOW_BOUNDARY | 2 |
| DIRECT_UPVALUE_SLOT | 2 |

所有记录 receiver_class_confirmed=NO，original_name_confirmed=NO。需要沿上层 CLOSURE、Upvalue 捕获指令、全局赋值以及对象构造路径建立实例身份；不从同现 Hash、Haxe 命名或静态 C 键直接升级 H3。

## 剩余五条缺失 S：范围已缩小

[完整 Trinity Pack 审计](https://github.com/969981/ZA_Resources/blob/master/Unpack/v2.0.2/romfs/arc/data.trpfs/_index/lua-native/native-lua-pack-coverage.json) 确认本版本 13,181 个资源包中只有四个 .blua.trpak（12145–12148）；四份字节码的目标常量池覆盖 157/162 个原始未解决 Hash。另五个 S 在该范围内不存在：原始 S 行 23、72、164、403、685，对应 062729EC443620C2、1463948047021356、34AD86B7E5BB1526、81E0610BF8B9337C、D0F61B3481E43C08。第三方线索集中于 Ev_sys_megarematch 与 Ev_sys_megarematch_lose，不能视作原版源码标识符。

下一轮建议：优先追踪 IkScriptCommand 静态键使用的真实 Upvalue 值来源及赋值生命周期；处理 7 条嵌套闭包的捕获链、20 条无归属调用；五条缺失 S 则需要额外游戏版本、其他二进制或独立消费者证据。

关联：[[ZA-Lua-Register-Flow-2026-11-05]]、[[Lua-Closure-Evidence-2026-11-05]]、[[Lua-Native-Join-2026-11-05]]、[[Hash-Evidence-Standards]]。
