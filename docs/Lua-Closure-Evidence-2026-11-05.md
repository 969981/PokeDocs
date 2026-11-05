---
tags: [SV, ZA, Lua, native-opcode, audit, Obsidian]
date: 2026-11-05
status: NATIVE_STRUCTURE_CROSSWALK_ORIGINAL_NAMES_UNCONFIRMED
---

# SV / ZA Lua 原生证据闭合：95 类与四个 ZA Pack

> [!IMPORTANT] 本文为**固定 Git 提交交叉复核**，不是新增原名恢复，也不意味着已证明运行时接收者的类型。当前未知 **SV C 1,334、ZA S 114、ZA F 41**，均保持不变。任何重建 Haxe 名称不因关联相同 Hash 自动提升为原生已验证名称。

## 已取得的关键更新：ZA 四包已真实提取

ZA_Resources master 当前已公布 [四个原生 Pack 的校验证明](https://github.com/969981/ZA_Resources/blob/bd2dd71af077b39e7c5d844c57bc1081710e3fdd/Unpack/v2.0.2/romfs/arc/data.trpfs/_index/lua-native/lua-target-publish-proof.json) 与 [完整 Lua 5.4 结构分析](https://github.com/969981/ZA_Resources/blob/bd2dd71af077b39e7c5d844c57bc1081710e3fdd/Unpack/v2.0.2/romfs/arc/data.trpfs/_index/lua-native/native-lua-summary.json)：

| Pack | 文件 | 原生 SHA-256 | Proto |
|---:|---|---|---:|
| 12145 | dll_util.blua | cc77b9440afeef775baf29aeeae381c37458a38e2920e2a162b0679c4d1b8af2 | 98 |
| 12146 | event_ik.blua | f238160475095b02e8c5302d907adbd1b48b2fd793a4a8c72ee8c9689fdfd698 | 7,388 |
| 12147 | main.blua | d9677f20ab3dfe350eec746d06769cf244bf316ee27fbd73a4bc208e5ff1b8a8 | 1,638 |
| 12148 | main_dynamic.blua | cc77b9440afeef775baf29aeeae381c37458a38e2920e2a162b0679c4d1b8af2 | 98 |

上游分析记录 **2,140 条**当时未知 S/F/E 的真实 Opcode 引用、**3,064 条** C→F 闭包、**878 条** C→S 闭包和 **566 条**严格相邻的字段加载→CALL/TAILCALL 边。其原始未知基线为 S 116/F 43/E 3；**以下报告重新依据 PokeDocs/develop 当前空白 S 114/F 41 过滤**，两套数量不可混用。

## SV：95 条双重结构未知类

- 从当前 1,334 条未知 C 严格按 `STATIC_C_TO_S_PLUS_GLOBAL` 筛出 **95 条**，每条均有原生 C→S 静态赋值与全局注册记录。
- 这 95 个 C 对应 **252 条 C→S 静态闭包边**、**95 条全局注册边**；[详细逐类表](evidence/lua-closure-2026-11-05/sv-dual-95.tsv) 附当前 Hashlist 行号、每条原始 PC 与闭包 Proto ID。
- **这 95 个 C 属于旧的「未命中严格 8-opcode C→prototype→F」集合**。不能因为另一批 1,047 个 C 有 C→F，就把其方法归到这 95 个 C；应先证明真正的同一构造对象或其它赋值形式。
- 优先检查 C `0x7F881F5D9B6F6009`（14 个 S）、`0xC924006D5C703655`（11 个 S）、`0x0BA32C14E3E6BD60`（10 个 S），并将 **global root/assignment PC → 表对象别名 → C→S root/settable PC → child closure** 串接。只因为相同 C Hash 就能配对记录，不等于跨 PC 的对象身份已证实。
- 待补原始字符串来源、全局注册时被存储的对象值、闭包字段写入时的表别名与实际消费者。

## ZA：当前 114 S / 41 F 的原生筛选

| 指标 | 重新筛选后的数量 |
|---|---:|
| 未命名 S 中具有原生 Opcode 引用 | **109/114** |
| 未命名 F 中具有原生 Opcode 引用 | **41/41** |
| S 中具有相邻字段加载→调用边 | **27** |
| F 中具有相邻字段加载→调用边 | **26** |
| 当前 155 个未知 S/F 合计相邻调用边 | **559** |
| S 中关联原生 C→S 闭包 | **101** |
| S 中同时具有原生 Opcode + Haxe 引用 | **109** |
| S 在现有 Opcode 索引中未出现 | **5** |

- [当前 155 条逐 Hash 对账表](evidence/lua-closure-2026-11-05/za-current-155.tsv) 保留 Hashlist 行号、原生 Opcode 和相邻调用数、示例 Proto/PC、C→S 静态边数、Haxe 引用数及验证状态，**不填任何推测名字**。
- 优先核查直接调用最多的 F：`0xE3D21257A15678CA`、`0xECCD6BC3CF2CA19B`、`0xCA4AB983F3B7598B`。这些是高调用频率目标，**不是原名证据**；下一步沿调用前接收对象的寄存器来源、闭包建表与字段写入关系作跨 Proto 追踪。
- 5 个未观察到指定 Opcode 引用的 S 见 [summary.json](evidence/lua-closure-2026-11-05/summary.json)。未命中仅表示当前支持的直接常量索引形式不足，不代表资源中不存在。

## 固定证据与可审计边界

- PokeDocs 输入提交：[779b9ba896ba4c8adf375008e5b71e62243f65ea](https://github.com/969981/PokeDocs/tree/779b9ba896ba4c8adf375008e5b71e62243f65ea)。
- ZA_Resources 原生输入提交：[bd2dd71af077b39e7c5d844c57bc1081710e3fdd](https://github.com/969981/ZA_Resources/tree/bd2dd71af077b39e7c5d844c57bc1081710e3fdd)。
- 固定输出统计：[summary.json](evidence/lua-closure-2026-11-05/summary.json)。
- 原生 Opcode / Haxe 的「同 Hash」不能替代原始 UTF-8 名称。**H2 精确名称候选**与**原生 Opcode 关系**分列管理，不自动产生 H3；目前新增原名 **0**，Hashlist 更改 **0**。

相关：[[Lua-Native-Join-2026-11-05]]、[[Lua-Next-Phase-2026-11-05]]、[[Hash-Evidence-Standards]]、[[SV-Library-BLua-CF-Assignments]]。
