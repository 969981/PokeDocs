---
aliases: [SV_Resources 同步, 2026-11-05 Lua Hash 证据合并]
tags: [PokeDocs, SV, ZA, Lua, evidence, Obsidian]
status: HASH_EXACT_RECONCILED
source_revision: a0c7905204ffd87421d3e9009f88d58822f5bb94
---
# SV_Resources 研究同步：SV / ZA Lua 与文件系统（2026-11-05）

> [!IMPORTANT] 本次写入的是可追溯、全 64 位精确匹配的**候选名称**，不是游戏原始源码文本的最终确认。第三方 Haxe 重建代码和原生 Lua 5.4 字节码有不同证据等级；原始字节码中出现调用链也不等于实际游戏运行时执行。

## 固定来源与对账

- 来源仓库：[SV_Resources 固定提交](https://github.com/969981/SV_Resources/tree/a0c7905204ffd87421d3e9009f88d58822f5bb94)，不使用会漂移的 master 内容作静态证据。
- ZA 名称源：[ZA Lua 第三轮](https://github.com/969981/SV_Resources/blob/a0c7905204ffd87421d3e9009f88d58822f5bb94/docs/research/za-lua-hash-recovery.md)；第三方重建代码 [ZAScripts 固定提交](https://github.com/Reisyukaku/ZAScripts/tree/c7bc243ac4d28356dff9f06b6723330ea92247d5)。
- SV 原生源：[4.0.0 C/F 原始字节码分析](https://github.com/969981/SV_Resources/blob/a0c7905204ffd87421d3e9009f88d58822f5bb94/docs/research/sv-lua-native-4.0.0.md) 与 [C→S/F 第三轮](https://github.com/969981/SV_Resources/blob/a0c7905204ffd87421d3e9009f88d58822f5bb94/docs/research/sv-lua-native-4.0.0-followup.md)。
- 初始 PokeDocs/develop：`8c69c4f2162bfa641ffed085de10ba2618d8a5fa`；保留原有 Hashlist 的哈希值、次序、行号及历史研究快照；只在空名行增加名称。
- 审计与原始行号：[[evidence/sv-resources/import-report-2026-11-05.json|import-report.json]]、[ZA 全候选](evidence/sv-resources/za-lua-recovered.tsv)、[ZA 行号及证据等级](evidence/sv-resources/za-lua-source-line-index.tsv)、[ZA 重建源码 Blob/行号](evidence/sv-resources/za-lua-source-evidence.tsv)、[SV 新 F 候选](evidence/sv-resources/sv-lua-f-new-exact-candidates.tsv)、[SV F 原生字段赋值 PC](evidence/sv-resources/sv-lua-f-native-bindings.tsv)。

### 合并校验

| 对账项目 | 结果 |
| --- | ---: |
| ZA 来源候选行 | 611 |
| ZA 全 64 位 Hash 重算成功 | 611 / 611 |
| ZA 已在 develop 中同名存在 | 72 |
| ZA 新填入空白 | **539**（F 79、S 460） |
| ZA 冲突、缺失目标 | **0** |
| ZA 第三方具名重建源码交叉证据 | 599 |
| ZA 仅 Hash 精确匹配、无具名重建源码交叉证据 | 12 |
| SV 新增 F 精确候选且有字节码回调赋值上下文 | **4** |
| 本次总新增 Hashlist 名称 | **543** |

### 更新后的未命名数量

| 列表 | 变更前空白 | 本次填入 | 当前空白 |
| --- | ---: | ---: | ---: |
| SV C | 1,338 | 0 | **1,338** |
| SV E | 2 | 0 | **2** |
| SV F | 107 | 4 | **103** |
| SV S | 800 | 0 | **800** |
| ZA C | 0 | 0 | **0** |
| ZA E | 0 | 0 | **0** |
| ZA F | 122 | 79 | **43** |
| ZA S | 576 | 460 | **116** |
| **合计** | **2,945** | **543** | **2,402** |

> [!NOTE] SV_Resources 的 ZA 表是另一份**未修改上游快照**，报告 E=3 未命名；PokeDocs/develop 先前已通过跨列表全 Hash 匹配命名这 3 项，因此本仓库 ZA E=0。两边的基线不同，不能把原始候选总数直接视为本次新增。此前第一轮 67 行和第二轮 84 行报告是历史快照，不改写其数字。

## 四个 SV F 精确候选（本轮实际回填）

| Hashlist 中 64 位值 | 候选名称 | 静态证据 |
| --- | --- | --- |
| `0x1DE5A53079D877CE` | `onModelModeChangedButton` | `GemSettingManager.Setup` 的 `OnModeChangedButton` → PC 211/214，1 处 |
| `0x3BCF72E1EF9938D6` | `onEulerAnglesValueChanged` | Model / Effect 两份回调注册，2 处 |
| `0x7E0CF8AE53062734` | `onOffsetPosValueChanged` | Model / Effect 两份回调注册，2 处 |
| `0xA1A67080A3235772` | `onLocatorNameValueChanged` | Model / Effect 两份回调注册，2 处 |

在 BLUA 常量中这些键以 `F` 前缀编码，如 `F1DE5A...`；TXT 采用 `0x1DE5A...`，**不能把 `F` 当作十六进制值的一部分**。四项由源处理函数命名变换生成并精确 Hash 复算；字段赋值位置真实存在，最终原名仍待更多原生字符串/消费者证据。四项保持 H2（附带原生上下文），不自动升 H3。

## 同步的 SV 4.0.0 结构研究（不等于新增名称）

- 原始 `main.blua` / `main_dynamic.blua` SHA-256：`c1a4f4e2625912cf0b739a642a79ba3357df0557a544b92da22a6cb139de2815` / `ae4a7d0168751f53af11746ac5ae7771cb1a5bfa580bcc0f79e2b9ee85acb572`。
- Lua 5.4 完整解出 37,743 / 7,036 个 Proto；验证 `C.prototype[F]=CLOSURE` **23,727 条**直接赋值，不能误称运行时调用次数。
- 针对原始 1,375 个未命名 C：1,076 个存在直接 `prototype[F]` 定义；余下 299 中 103 个存在 `Class[S]=CLOSURE` 静态定义（共 **281 条**），213 个存在类全局注册（交集 97）；两类严格定义至少覆盖原始 **1,179** 个 C。
- 281 条静态 C→S 中 269 个 S 有当前已知名称、12 个仍为 Hash。S 字段是静态函数键，**不可直接等同 F 方法**；全局注册及方法赋值证明关系，不证明未知 C 原名。
- 原始 116 个未知 F 的字节码使用范围已进一步分类为字段读取、实例写入、条件 `SELF→CALL` 与回调赋值；旧分析记录 16 个不同 F 的 49 处直接字段指令位置。历史旧文的“107 个未命名 F”是本次回填前的快照。

## 补充的文件系统 / 事件证据（只同步文档，不填未知路径）

- [TRPFD 索引研究](https://github.com/969981/SV_Resources/blob/a0c7905204ffd87421d3e9009f88d58822f5bb94/docs/unpack-roadmap.md)：Violet 4.0.0 **23,589 个包 / 408,641 个文件索引**；这是描述符覆盖，不代表所有 TRPFS 已解包完毕。
- [TREVT/TRPRE 原生研究](https://github.com/969981/SV_Resources/blob/a0c7905204ffd87421d3e9009f88d58822f5bb94/docs/research/sv-event-prefetch-native-links.md)：17,760 个 prefetch 64 位值中，17,678 个与 TRPFD 路径及哈希双向匹配，另用 PokeDocs 文件路径恢复 36 个，合计 **17,714**；剩余 **46** 保持未知。
- TREVT 已找到 688 个事件、746 条条件引用，字段 3 的数值 2 和隐式 End 语义**尚未由实际消费者证明**；不得填入未经核验的条件类型。
- SV 4.0.0 原生程序中的哈希常量与指令指向 offset basis `0xCBF29CE484222645` / prime `0x100000001B3`。本项目仍区分 Lua 名称、TRPFD/TRPAK 路径与缓存文件读写格式，不能据此把所有哈希族合并解释；参见 [[FileSystem-Hashes]]。

## 下一轮优先研究

1. **SV C 1,338**：利用已经验证的 C→F、C→S 赋值、全局注册和完整名字符串，寻找原始类命名空间；不得把调用方直接认定为被调用者所属类。
2. **SV F 103 / E 2 / S 800**：沿 Gem Setting / 战斗队伍输入／消息效果实例的实际字段写入与动态调用追踪，补齐对象身份和独立原名证据。
3. **ZA F 43 / S 116**：优先找 ZA 对应版本原生 Lua / consumer 指令，用第三方 Haxe 索引做检索入口，而不是宣称已完成原生证明。ZA E 在本分支已命名，但仍需逐项语义复核。
4. **路径 Hash 46**：从实际预取消费者或构造算法取得新路径来源后再回填；单纯整数同现不等于字符串路径匹配。

## 复现

```powershell
python scripts/verify_sv_resources_import.py
python scripts/lua_hash.py verify
python -m unittest discover -s tests -v
```

上述命令只读校验，绝不覆盖 Hashlist、拆分 BLUA 或重新提取游戏资源。完整外部重算可在固定源版本运行 SV_Resources 的 `Recover-ZA-Lua-Hashes.py --verify-only --min-recovered 611` 和 `Verify-SV-Lua54-Followup.py`；原始 `.blua` 留在本机。参见 [[Hash-Evidence-Standards]]、[[SV-Library-BLua-CF-Assignments]]、[[SV-Library-BLua-F-Dispatch]]。
