---
aliases: [Lua Hash 3.09亿次暴力候选验证, SV ZA Lua Bruteforce]
tags: [PokeDocs, SV, ZA, Lua54, FNV1a64, Hash, H2, native-evidence, Obsidian]
date: 2026-11-05
status: EXACT_HASH_H2_CANDIDATES_NATIVE_ORIGINAL_UNCONFIRMED
---

# SV / ZA Lua：三轮 1,167,121,655 次计算，累计 28 个 H2 精确 Hash 候选

> [!IMPORTANT]
> 这是一轮**真实 GitHub Actions C++ 枚举 + Python 独立 Hash 复算**，不是任意字符串的通用 2^64 逆向求解。已命中的都是**原先空白行的 H2 精确名称候选**；没有游戏原生 UTF-8 原名证明时不得宣称 H3。此轮未修改任何正式 Hashlist，未知基线仍为 SV C **1,334**、ZA S **114**、ZA F **41**。

## 1. 实际计算、工具、输入

- [成功的原生 C++ CI](https://github.com/969981/PokeDocs/actions/runs/42029953436)，合成回归测试及 SV、ZA 两个矩阵作业全部通过，候选结果在同一成功运行中发布。
- [C++ 枚举引擎](../scripts/hash_bruteforce.cpp)：依据 SV/ZA 已命名 Lua Hashlist 生成“命名空间 × 类名词根、前后缀、Haxe 嵌套类”和“动词 × 已有 S/F 词根、2/3 个 CamelCase 词”的可解释候选；采用 UTF-8 FNV-1a 64，`basis 0xCBF29CE484222645`。
- [合成测试](../tests/test_hash_bruteforce.py)，包含至少一个能够由词根+类后缀还原的 C、由动词+词根还原的 ZA S/F，以及错误已命名映射直接拒绝的测试。
- [Python 独立复算](../scripts/verify_hash_bruteforce.py)：不仅比较完整 64 位 Hash，还检查命中是否仍对应目标 Hashlist 的原始空白行、唯一性、原生证据索引、候选来源。独立复算已对 24/24 条完全匹配（核对的最终 CI 结果见下文）。
- 搜索使用当前 `PokeDocs/develop` 八张 Lua Hash 表；原始字节码无须上传/重新拆分，计算输出只包含衍生 TSV/JSON。具体源文件与 Hash 校验由独立报告记录。

| 项目 | 实际枚举次数 | 新 H2 候选 | 耗尽预算？ |
| --- | ---: | ---: | --- |
| SV C | 146,759,001 | **12** | 否 |
| ZA S/F | 162,271,660 | **12**（S 7 / F 5） | 否 |
| 合计 | **309,030,661** | **24** | 否 |

每个游戏的预算为 300,000,000 次，本轮实际完整枚举所有已设定规则。**不等于穷举全部字符串**，FNV-1a 64 位原像搜索空间为 2^64；没有命中的未知项应继续保持空白。

## 2. SV C：12 个精确字符串

| 行 | 目标 Hash | H2 精确名称 | 原生结构状态 |
| ---: | --- | --- | --- |
| 24 | `016904F481BF082D` | `main.system.prohibit._Prohibit.Prohibit_Impl_` | C→S + 全局注册（1/1） |
| 1050 | `5177E949076BBE48` | `main.system.game_event.IGameEventScript` | 全局注册 |
| 1438 | `6F7A8CF2CB565DD3` | `main.ui.xmenu.xmenu_state_machine.XMenuStateBase` | 直接 C→F |
| 1657 | `7FA9D0451CA273B7` | `main.ui.hyper_training.SceneHyperTraining` | 直接 C→F |
| 1706 | `837BB966ECC5B849` | `dll_danbattle.ai.partner.DanPartnerPokemonController` | 当前主两份 BLUA 无索引 C 字面量 |
| 1911 | `91B78F1802B84B80` | `dll_danbattle.ai.partner.DanPartnerManagerModel` | 嵌套引用 |
| 2277 | `B2DCC287A7876860` | `main.ui.ymap.npc_navi.YmapNpcNavigationDataAccessor` | 直接 C→F |
| 2427 | `C19222E56D8434C9` | `main.field.behaviour.base._FieldObject.FieldObject_Impl_` | C→S + 全局注册（4/1） |
| 2625 | `D1AB2595B97752F1` | `main.field.behaviour.out_of_range.FieldOutOfRangeData` | C→S + 全局注册（8/1） |
| 2657 | `D3A213C7225B68B3` | `main.playables.free_move.ctrl._ActorControl.ActorControl_Impl_` | C→S + 全局注册（6/1） |
| 2867 | `E0D511325372F946` | `main.system.game_event.base.BaseGameEvent` | 全局注册 |
| 3189 | `F67A67452D018ECC` | `main.system.game_event.base.GameEventManager` | 全局注册 |

- **4/12** 同时有原生 C→S、全局注册，是 [[Lua-Closure-Evidence-2026-11-05]] 的 95 类重点。
- **3/12** 有直接 C→prototype→F 定义。
- **3/12** 只有全局注册；另外 **1/12** 嵌套引用，**1/12** 未在支持的 BLUA 常量模式中出现。
- C 结构反查证据是**不同维度**：它证明目标 Hash 在原生指令中具备的行为，不是直接证明 H2 候选字符串就是原版源码的可读名称。

[SV 候选明细与来源 TSV](evidence/hash-bruteforce-2026-11-05/sv-matches.tsv) / [枚举统计 JSON](evidence/hash-bruteforce-2026-11-05/sv-summary.json)

## 3. ZA：7 个 S + 5 个 F

| 类型 | 行 | Hash | H2 精确名称 | 原生 Opcode 次数 |
| --- | ---: | --- | --- | ---: |
| S | 23 | `062729EC443620C2` | `Get_BossName` | **0** |
| F | 28 | `1C7588256778C880` | `CalcLerpAngle` | 2 |
| F | 31 | `1E8047C2B6ED610E` | `WaitObserveMessageAndLipSync` | 3 |
| S | 199 | `40ACEF14A8745A74` | `CreateObjectTemplate` | 14 |
| S | 260 | `522136910C73A819` | `Wait_CompleteTurn` | **744** |
| S | 394 | `80725197C3054FB8` | `StopRequestPauseEventDisable` | 6 |
| F | 132 | `86C2CE59EBF934B7` | `UpdateBattleWinCount` | 2 |
| F | 134 | `88788E4CF0D59CA6` | `StartTrainingMenu` | 2 |
| S | 597 | `B813B84CBD506E19` | `TrySetMenuData` | 2 |
| F | 195 | `B990C212EC51628E` | `GetRewardCard` | 2 |
| S | 714 | `DC6EBFBAD25B5CC2` | `IsNeedTurn` | 3 |
| S | 819 | `FD08022F733C742C` | `GetTalkMessageData` | 2 |

- ZA 11/12 已有原生 Opcode 常量引用，**但原生指令只含 Hash，不含上述可读候选的原始字符串**。
- `Wait_CompleteTurn` 的 744 条引用和 1 条 C→S 闭包归属，最适合下一阶段集中追踪真正的闭包与接收对象；`StopRequestPauseEventDisable` 有 5 条相邻字段调用证据。
- `Get_BossName` 刚好命中此前 **五个目标 Pack 常量池缺失 S** 之一。它的 H2 候选来自原有 `Boss` / `Name` 词根组合，不能因为精确 Hash 命中就假称 ZA 2.0.2 四份原生 BLUA 存在这个符号，更不能将第三方 Haxe 引用升级为原版命名。
- 这些数量来自当前 PokeDocs 的 155 条剩余 S/F 和固定原生索引，和 ZA_Resources 旧的 162 条 unresolved 基线不能混算。

[ZA 候选与来源 TSV](evidence/hash-bruteforce-2026-11-05/za-matches.tsv) / [ZA 枚举统计](evidence/hash-bruteforce-2026-11-05/za-summary.json)

## 4. 验收边界与接下来的推进

1. **名称等级：** 精确完整 Hash + 明确命名语法及来源，为 H2；没有独立原名来源，H3 数量仍为 0。正式 `lua_*_hashes.txt` 原空白行保持不动，避免将研究候选当成官方映射。
2. **原生归属：** SV 优先处理这四个新命中的 95 类（总静态 S 闭包 19 条），向工厂、元表、`__name__` 和具体方法消费者关联；ZA 优先 `Wait_CompleteTurn` 和 `StopRequestPauseEventDisable`。
3. **继续穷举：** 可以采用这 24 条 H2 作为独立标记的二轮种子，扩展同 namespace 的组合词及更大 CamelCase 文法，记录新增命中并继续做完整 Hash 复算，但不得递归把 H2 种子冒充已知 H3。
4. **工具边界：** 搜索全程只读 Hashlist，输出含 `method / prefix_source / leaf_or_stem_source`，每条命中都能重新生成。可复现的 C++ 程序及 CI 入口已提交，可独立用 `--budget` 调整计算规模。

关联：[[Hash-Evidence-Standards]]、[[Lua-Proto-Owner-Join-2026-11-05]]、[[SV-Lua-Factory-Metatable-2026-11-05]]、[[ZA-Lua-Closure-Receiver-2026-11-05]]。


## 5. 第二轮：H2 种子 + 局部命名语法扩展（已成功）

第二轮在**不修改 Hashlist**的情况下，将第一轮 24 条完整匹配作为 H2-only grammar seeds，新增命名空间局部 prefix×stem×suffix 与 top-150 高频 CamelCase 三词组合。所有 H2 种子先重新计算完整 64 位 Hash，错误种子直接失败；合成测试包含篡改种子拒绝。执行结果：[GitHub Actions 42031392850](https://github.com/969981/PokeDocs/actions/runs/42031392850) 全部成功。

| 统计 | SV C | ZA S/F |
| --- | ---: | ---: |
| 本轮计算候选 | 152,216,932 | 388,577,622 |
| 本轮所有命中（含第一轮重现） | 12 | 15 |
| **相对第一轮新增** | **0** | **3** |
| 最大预算 | 650,000,000 | 650,000,000 |
| 预算耗尽 | 否 | 否 |

第二轮 **540,794,554** 次计算，累计两轮 **849,825,215** 次候选计算（不是 8.498 亿个完全去重后的字符串）。最终去重 H2 候选 **27 条**：SV C 12、ZA S 9、ZA F 6。

| ZA 原始行 | Hash | 本轮新增 H2 精确字符串 | 原生范围 |
| ---: | --- | --- | --- |
| S 72 | `1463948047021356` | `Get_BossNameIndex` | 2.0.2 四包目标常量池仍没有该 Hash |
| F 151 | `931F8A64586A46A6` | `ShowMessageNpcEvent` | 待与具体函数/接收对象结合 |
| S 616 | `BE4399F61C307041` | `WaitCreateObjectTemplate` | 待沿关联 C→S 原型追踪 |

尤其是 `Get_BossNameIndex` 是从上一轮 `Get_BossName` H2 种子扩展的第二个精确命中，两者对应原来 5 个四包缺失 S Hash 中的 **2 个**。这是候选字符串间的相关性及 Hash 验证，仍然不能声称它们实际存在于这四个 BLUA 的字节码或已经拿到原版 UTF-8 符号。

- [SV 第二轮统计](evidence/hash-bruteforce-2026-11-05/sv-round2-summary.json) / [逐行结果](evidence/hash-bruteforce-2026-11-05/sv-round2-matches.tsv)
- [ZA 第二轮统计](evidence/hash-bruteforce-2026-11-05/za-round2-summary.json) / [逐行结果](evidence/hash-bruteforce-2026-11-05/za-round2-matches.tsv)

后续已不建议继续扩大第一轮同类 namespace×suffix 枚举：SV 此次未新增匹配。应转向 **ZA megarematch 事件的第三方 Haxe 上下文词汇** 与 SV 结构化类语义的原生来源。全部正式未知基线仍未修改。


## 6. 第三轮：ZA Mega Rematch 事件上下文定向算尽（已成功）

使用 ZA_Resources 已固定的第三方 Haxe 重建代码 `Ev_sys_megarematch` / `Ev_sys_megarematch_lose` / `Ev_sys_megarematch_win` 中实际调用、选择菜单、消息和 `spn_boss` 关联关系，为**仅剩五个四包未收录的 S Hash**建立**明确限定的上下文词汇文法**。

- 实现：[高性能前缀状态 FNV C++ 搜索](../scripts/brute_za_megarematch_context.cpp)，每个前缀先计算一次，后续逐候选只追加字段词根和后缀字节；**不重复哈希完整字符串，也不引入通用 2^64 穷举**。
- [成功的 GitHub Actions 42032644286](https://github.com/969981/PokeDocs/actions/runs/42032644286)，C++ 全量运行并由独立 Python 用现有 S Hashlist 的原始空白行重新计算全部结果。
- 本轮实际计算 **317,296,440** 个候选，指定语法完全覆盖、未触及 400,000,000 预算。
- 五个目标 Hash 中**精确命中 3 个**（前两轮已有的两条 + 本轮新一条）。新增 `S34AD86B7E5BB1526 = Get_BossBattleID`，原始 S 第 164 行。

| 以前缺少原生 Lua 常量的 S 行 | Hash | 当前 H2 精确候选 | 2.0.2 原生常量仍缺失？ |
| ---: | --- | --- | --- |
| 23 | `062729EC443620C2` | `Get_BossName` | 是 |
| 72 | `1463948047021356` | `Get_BossNameIndex` | 是 |
| 164 | `34AD86B7E5BB1526` | `Get_BossBattleID` | 是 |
| 403 | `81E0610BF8B9337C` | **仍未知**，Haxe 重建为消息标签数组 | 是 |
| 685 | `D0F61B3481E43C08` | **仍未知**，Haxe 重建为 Boss SPN 数组 | 是 |

上述 Haxe 中数组用途只帮助构造字符串候选，**不证明原版变量名**。尤其后三项在当前四份 2.0.2 BLUA 常量池中仍未找到字面 Hash，不能把 “H2 精确候选” 写成“原生 Lua 调用链原名已恢复”。前面三项名字虽然语义相互支撑，但还没有 H3 身份证据。

- [第三轮匹配结果](evidence/hash-bruteforce-2026-11-05/za-megarematch-matches.tsv)
- [原生 CI 完整预算统计](evidence/hash-bruteforce-2026-11-05/za-megarematch-summary.json)

三轮累计 **1,167,121,655** 次候选计算（含重复）；去重 **28 条 H2**，按游戏及类型：**SV C 12、ZA S 10、ZA F 6**。

## 7. 供工具使用的安全 Overlay（不覆盖正式 Hashlist）

已生成唯一的衍生映射：[H2 候选 Overlay TSV](evidence/hash-bruteforce-2026-11-05/h2-candidate-overlay.tsv) / [来源、类别、内容哈希审计](evidence/hash-bruteforce-2026-11-05/h2-overlay-summary.json)。

- 工具：[build_lua_h2_overlay.py](../scripts/build_lua_h2_overlay.py)，[验证通过的 GitHub Actions 42033011221](https://github.com/969981/PokeDocs/actions/runs/42033011221)。
- 对五份源 TSV 再次计算完整 FNV64，严格校验 28 条原始空白行仍存在、候选冲突为零、H2/H3 字段未混淆。输出按类别和 Hash 确定性排序，并附输入 SHA-256。
- 为方便解析，字段包含 `game`、`kind`、`hash`、`lua_token`、`candidate_name`、`evidence_grade`、`native_structure`、`native_opcode_refs`、`matching_stages` 等；所有记录 `native_original_name_confirmed=NO`、`hashlist_updated=NO`。
- ZA 28 个 H2 中未出现于原生四包 Opcode 索引的恰好是 `Get_BossName`、`Get_BossNameIndex` 和 `Get_BossBattleID` 对应的三个 S 哈希；其余 ZA 13 个匹配有原生 Opcode 证据，但**这些证据只支持哈希使用，不会自动证明名称来自游戏**。

当前正式未知行数仍为 **SV C 1,334、ZA S 114、ZA F 41**。如果未来项目明确决定采纳 H2 为“增强候选”，应当对照 Overlay 做**独立、可撤销的二次映射**，而不是抹掉原始 Hashlist 的未知状态。

## 8. 后续目标

- **ZA：** 再研究剩余两个数组 Hash 的**命名来源**，不再沿已经穷举的 317M 事件文法无限重复。优先比较更多游戏版本、静态表实际构造和编译前的标识符来源。
- **ZA：** 本轮 H2 中 `Wait_CompleteTurn` 有原生 Opcode 744 条，`ShowMessageNpcEvent` 有 78 条；可以沿已建立的原生 CALL 和 Prototype 归属先处理这两条的真实消费者与接收表身份。
- **SV：** 本轮 12 个 C 中有 4 个已取得 C→S + 全局注册双证据；围绕已验证工厂 `R15` 与 `__name__` 继续证明动态对象赋值与最终类型，而不是仅增加不受约束的 C 类名枚举。
