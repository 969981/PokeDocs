---
aliases: [Lua Hash 3.09亿次暴力候选验证, SV ZA Lua Bruteforce]
tags: [PokeDocs, SV, ZA, Lua54, FNV1a64, Hash, H2, native-evidence, Obsidian]
date: 2026-11-05
status: EXACT_HASH_H2_CANDIDATES_NATIVE_ORIGINAL_UNCONFIRMED
---

# SV / ZA Lua：3.09 亿候选计算，新命中 24 条完整 64 位 Hash

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
