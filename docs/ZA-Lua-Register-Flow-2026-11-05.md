---
tags: [PokeDocs, ZA, Lua54, native-opcode, register-flow, Obsidian]
date: 2026-11-05
status: VERIFIED_NATIVE_REGISTER_FLOW_NAMES_UNCONFIRMED
source_commit: 302311f0c732266dba5347f0e4f4ff9508d28509
---

# ZA 2.0.2：原生 Lua 寄存器数据流与新增 922 条调用关系

> [!IMPORTANT]
> 本轮新增的 **922 条**是实际 Lua 5.4 字节码中验证的局部字段→CALL 指令关系，而不是 922 个原始函数名。原始标识符新增确认数仍为 **0**。当前 PokeDocs/develop 的未命名基线为 ZA S 114/F 41；ZA_Resources 原始索引研究基线为 S 116/F 43/E 3，二者不可混算。

## 已验证的原生基础

从 ZA 2.0.2 Trinity 的四个 Pack（12145–12148）已解出 dll_util、event_ik、main、main_dynamic 四份原始 .blua。逐一 SHA-256 校验并完整解析，共 9,222 个 Prototype；未知目标 Hash 常量出现 1,365 次、原生 Opcode 引用 2,140 次；根原型 C→F 闭包 3,064、C→S 静态闭包 878。

证据：[ZA 原生提取报告](https://github.com/969981/ZA_Resources/blob/master/docs/research/v2.0.2/za-lua-native-opcode-evidence.md)。

## 本轮真实执行结果

新分析器在局部直线代码段中追踪 LOADK/LOADKX → GETTABLE、SETTABLE、SELF，及 MOVE → CALL/TAILCALL。对分支入口、未知指令和副作用清空状态，限定 16 指令窗口；四个原生输入逐项对照 SHA-256。

[原生 Actions 42019295407](https://github.com/969981/ZA_Resources/actions/runs/42019295407) 成功，合成测试 10/10 通过；[master 发布 Actions 42019519024](https://github.com/969981/ZA_Resources/actions/runs/42019519024) 已发布结果。

| 指标 | 实际结果 |
| --- | ---: |
| 原相邻字段调用边保留 | 566/566 |
| 新增非相邻/寄存器键调用边 | **922** |
| 所有局部字段调用边 | **1,488** |
| 不同未知 Hash 涉及调用 | 100 |
| 寄存器键表操作 | 30 |
| 不同寄存器键 Hash | 6 |
| 原生确认原始名称 / receiver 类 | **0 / 0** |

来源：[源码分析器](https://github.com/969981/ZA_Resources/blob/master/scripts/Trace-ZA-Lua-RegisterFlow.py)、[调用 TSV](https://github.com/969981/ZA_Resources/blob/master/Unpack/v2.0.2/romfs/arc/data.trpfs/_index/lua-native/native-unknown-register-flow-calls.tsv)、[键操作 TSV](https://github.com/969981/ZA_Resources/blob/master/Unpack/v2.0.2/romfs/arc/data.trpfs/_index/lua-native/native-unknown-register-key-uses.tsv)、[统计 JSON](https://github.com/969981/ZA_Resources/blob/master/Unpack/v2.0.2/romfs/arc/data.trpfs/_index/lua-native/native-unknown-register-flow-summary.json)。

## 仍不存在于四份目标常量池的五条 S

这五项是原始 unresolved S 行号；均有第三方 Haxe 参考，但在四份原生 Lua 当前目标常量 TSV 中未出现，不能仅扩大 CALL 扫描补齐，更不能把第三方源码名称当成原生原名。

| S 原始行 | Hash |
| ---: | --- |
| 23 | 062729EC443620C2 |
| 72 | 1463948047021356 |
| 164 | 34AD86B7E5BB1526 |
| 403 | 81E0610BF8B9337C |
| 685 | D0F61B3481E43C08 |

第三方定位集中于 event_ik/Ev_sys_megarematch.hx 与 Ev_sys_megarematch_lose.hx；应扩大原生事件/Lua 资产和版本覆盖。

## 下一阶段

优先将已证实的 C→F、C→S 闭包的 child_proto_id 与新调用 TSV 的 proto_id 关联，再沿表寄存器、SELF 接收者和 upvalue 的创建及赋值路径证明对象身份。只有原始 UTF-8 名称和完整 64 位 Hash 复算都获得可独立审计的证据时，才确认原名；其余继续保持 H2 或 UNKNOWN。

关联：[[Lua-Closure-Evidence-2026-11-05]]、[[Lua-Native-Join-2026-11-05]]、[[Hash-Evidence-Standards]]。
