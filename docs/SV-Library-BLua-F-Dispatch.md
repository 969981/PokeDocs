---
tags: [SV, Lua, bytecode, function-call, original-evidence, F-hash]
status: STATIC_DISPATCH_CONFIRMED_RUNTIME_UNCONFIRMED
---

# SV 未知 F 的真实字段对象与 SELF → CALL 静态关系

> [!IMPORTANT] 分析的确是 Library 原始 **`main.blua` / `main_dynamic.blua`** 的 Lua 5.4 字节码；文件头不能单独验证游戏是 SV 4.0.0。**`SELF→CALL` 表示字节码存在静态可达方法调用路径**，不表示运行时已实际走到该路径，也不能把被调用 Hash 自动改写为原始函数名。

## 重新审计后的计数

| 指令证据 | 总位置 | 不同未知 F |
| --- | ---: | ---: |
| `GETFIELD` | 13 | 11 |
| `SETFIELD` | 20 | 16 |
| 新补充 `SELF` | **16** | **14** |
| **总位置** | **49** | **16** |

这次的前 33 处 `GETFIELD/SETFIELD` 与旧版 TSV 逐条比较，**33/33** 的文件、Proto ID、PC、Hash、操作码完全相同；新增 16 处 `SELF`，全部接到保持函数寄存器未被覆写的 `CALL`，16 次 `SELF` 的表对象均为**未覆写的首形参 R0**。

所有 13 个先出现 `GETFIELD` 的调用点，还在紧邻的 `EQK → JMP` 中验证出 **JMP 的真实跳转目标恰好是 CALL 后一条指令**。因此这些是字段检查后按分支条件选择是否调用的模式；另外 3 个直接使用 `SELF`。

- 16 个 `SELF` 调用点覆盖 **14 个不同**的未知 F Hash。
- 另外 **2 个未知 F Hash** 在本轮只观察到 `SETFIELD`，并未发现其 `SELF→CALL`。
- `main_dynamic.blua` 在这批 107 个 F 未知 Hash 中没有新增上述三类直接常量索引字段指令。
- 107 个未命名 F Hash 的其余 91 个未在这两份字节码中发现编码常量，但不能据此证明其他版本和脚本中不存在。

## 表对象的来源

| 指令 | 表对象证据 |
| --- | --- |
| `GETFIELD` 13/13 | R0，第一个形参 |
| `SELF` 16/16 | R0，第一个形参 |
| `SETFIELD` 11/20 | 直接写 R0 |
| `SETFIELD` 9/20 | 写入由 `GETI` 取得的 R0 子表：8 次 `R0[8/9]`、1 次 `R0[20]` |

20 个 `SETFIELD` 的**写入值**进一步分为 18 次 `CALL` 返回结果、1 次 `CLOSURE`、1 次常量。对于 `CALL` 返回值，来源只能标为 `CALL_RESULT_UNRESOLVED`，不能把返回值当成已有明确实现地址的函数。

### 一个更强的闭包写入实例

`main.blua` Proto 5432 中：

- PC 86：`GETI R8, R0, 20`
- PC 87：`CLOSURE R9, Child[5]`，该子原型实际是 **Proto 5438**
- PC 88：`SETFIELD R8, K[FD309DBFD9F0B2057], R9`

因此可直接证明这段代码**把 Proto 5438 的闭包赋给 R0[20] 中以未知 F Hash 为键的字段**。但其他 Proto 对同一 F Hash 的 `R0:F(...)` 动态调用能否命中这一闭包，需要额外的**对象身份/别名链**，不能仅凭 Hash 相等就跨对象连边。

## 静态调用关系按包含方法分类

下表的类名来自已有精确 Hash 名称映射；**它们是调用指令所在方法的类，不是动态调用目标对象的确证类型**。

| 包含方法所属类 | 静态 `SELF→CALL` | 不同未知 F | 示例 Proto / SELF PC → CALL PC |
| --- | ---: | ---: | --- |
| `main.ajito.system.rush.AjitoPokemonPopPointModel` | 1 | 1 | 395 / 1→2 |
| `main.battle.simple_auto.SimpleAutoBattle` | 3 | 1 | 7196 / 543→544 |
| `main.field.behaviour.base.UpdateFrequencyRequester` | 2 | 2 | 14745 / 4→6 |
| `main.gem.setting_tool.GemSettingModelWindow` | 3 | 3 | 17942 / 9→11 |
| `main.ui.btl_team.view.BattleTeamSelectUIInputModule` | 5 | 5 | 26659 / 3→4 |
| `main.ui.msg_doctor.effect.MsgDoctorNoiseffect` | 2 | 2 | 29923 / 59→60 |
| **合计** | **16** | **14** | |

例如 `main.battle.simple_auto.SimpleAutoBattle` 的 Proto 7196：

```text
PC 540  GETFIELD R32, R0, K[FD309DBFD9F0B2057]
PC 541  EQK      ...
PC 542  JMP      +2        ; 不调用时跳至 PC 545
PC 543  SELF     R32, R0, K[FD309DBFD9F0B2057]
PC 544  CALL     R32, 2, 1 ; R33 为 SELF 准备的 receiver
PC 545  ...
```

这证明了**字段读取 → 条件分支 → 动态方法装载 → CALL**，但没有证明 F 的明文名称，也没有证明 `R0` 在运行时一定具备该方法。

## 证据文件和复现

- [可执行追踪器](../scripts/trace_sv_lua_f_dispatch.py)：复用已有的完整 Lua 5.4 Proto 解析和 C→F 闭包归属表，增加局部寄存器写入/别名、`GETFIELD/SETFIELD/SELF`、控制流跳转检查。
- [合成测试](../tests/test_trace_sv_lua_f_dispatch.py)：覆盖相同寄存器 CALL、额外实参、被覆写的函数寄存器、跨 JMP 的假阳性、嵌套 R0 表和纯 Hash 常量。
- [逐调用点 JSON](sv-f-dispatch-2026-11-05.json)：16 处可审核的 `SELF→CALL` 位置和摘要。

```powershell
python scripts/trace_sv_lua_f_dispatch.py "D:\\SV\\main.blua" "D:\\SV\\main_dynamic.blua" --repo . --game SV --output sv-unknown-f-dispatch.json
python -m unittest discover -s tests -v
python scripts/lua_hash.py verify
```

完整 JSON 输出记录全部 49 个字段位置，分别附上接收者来源、写入值来源、所在闭包的 C→F 方法、文件、Proto ID、字节 PC 和文件物理偏移，不含游戏原始字节码。

**未完成**：跨函数的对象构造、R0 实际实例类型、字段别名及运行时被调用的确切闭包目标；以及 2,945 行未知名称的明文恢复。本轮**不回填任何 Hashlist**。

依据：[Lua 5.4 官方 Opcode 格式](https://www.lua.org/source/5.4/lopcodes.h.html) · [[SV-Library-BLua-CF-Assignments]] · [[Hash-Evidence-Standards]]。
