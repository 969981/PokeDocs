---
tags: [SV, Lua, bytecode, reverse-engineering, C-F, native-evidence]
status: ASSIGNMENT_CHAIN_VERIFIED
source: user-Library
---

# SV Lua C → prototype → F：实际指令级归属证据

> [!IMPORTANT] 本文基于 Library 实际保存的 `main.blua` 与 `main_dynamic.blua`，不是仅凭 Hash 同时出现。已逐条校验 Lua 5.4 的寄存器、常量索引、闭包子原型，且两文件均读到末尾。**能够确认的是字节码赋值链，不是运行时函数调用，也不是未命名 Hash 的明文还原**。文件头只能证明 Lua 5.4，不能独立确认 SV 4.0.0。

## 实测摘要

| 项目 | `main.blua` | `main_dynamic.blua` |
| --- | ---: | ---: |
| SHA-256 | `c1a4f4e2625912cf0b739a642a79ba3357df0557a544b92da22a6cb139de2815` | `ae4a7d0168751f53af11746ac5ae7771cb1a5bfa580bcc0f79e2b9ee85acb572` |
| 实际解出 Proto | 37,743 | 7,036 |
| **完整 C→prototype→F 闭包赋值** | **18,991** | **4,736** |
| 不同 C Hash | 2,705 | 744 |
| 不同 F Hash | 9,917 | 369 |
| 无法对应的 CLOSURE 子原型 | 0 | 0 |

两份文件共有 **23,727 条**不同的（C Hash、F Hash）直接赋值，涉及 **3,449** 个不同 C Hash 和 **10,260** 个不同 F Hash；这些结果均来自根原型的 8 条连续指令链，不依赖猜测父类或函数名。

## 原生指令链：严格识别

```text
GETUPVAL   Rbase, Upvalue[0]
LOADK      Rkey,  K[C...]
GETTABLE   Rbase, Rbase, Rkey
LOADK      Rkey,  K["prototype"]
GETTABLE   Rbase, Rbase, Rkey
LOADK      Rkey,  K[F...]
CLOSURE    Rvalue, ChildProto[Bx]
SETTABLE   Rbase, Rkey, Rvalue    ; k=0
```

解析器还核对了每一步 Rbase/Rkey/Rvalue 的 A/B/C 寄存器号、不允许 `SETTABLE k=1` 被错误地当作写入 `Rvalue`，并将 `CLOSURE Bx` 映射到真实直属子 Proto ID。

这是关于 `Upvalue[0][C...].prototype[F...] = closure(ChildProto)` 的**静态赋值证据**；其 Upvalue 的语义解释仍需要上下文或运行时确认。原始操作码位置与格式采用 [Lua 5.4 官方 lopcodes.h](https://www.lua.org/source/5.4/lopcodes.h.html)。

## 逐字节证据示例：HudInfoPlayer.Setup

- 已命名 C：`CFD9B049511E682DA` → `main.ui.hud_info.HudInfoPlayer`
- 已命名 F：`F7C68FEDB79AB6396` → `Setup`
- 来源 `main.blua` 根 Proto 0，`PC 342676–342683`
- 类名常量加载 `PC 342677`，`prototype` 读取 `PC 342680`，函数键加载 `PC 342681`
- `CLOSURE PC 342682` 的 child index `24320` 实际映射到 **Proto 29004**
- `SETTABLE PC 342683`，文件原始偏移 **1,370,773（0x14EAB5）**（偏移以十进制字段为准）

同一个 C 类的直接赋值共 6 条，分别位于根 Proto 的 PC 342683、342691、342699、342707、342715、342723；可以继续到这些子 Proto 分析方法内部实际字段与调用。

## 剩余 107 个未知 F 的精确分流

- 107 个当前 SV F Hash 仍为空白。
- 其中 **16 个**在两份原生字节码中作为 F 常量出现（全部位于 `main.blua`），但本轮严格 `C.prototype[F] = closure` 链 **命中 0 个**。
- 另外 **91 个**在这两份文件的 F 编码常量中未出现；这**不证明**其不存在于其他数据或版本。
- 对 16 个已出现的 F 的进一步原始 Opcode 统计：`GETFIELD` 13 处、`SETFIELD` 20 处，合计 **33 个字段引用位置**。其中 29 个位置的所在 Proto 能映射回上述已验证的类方法闭包；这只是调用者/字段访问上下文，不代表 F 原名、目标实现或运行时调用已确认。

下一轮直接以这 33 个字段引用点的对象来源寄存器为入口，先恢复 **被读写的表对象**及 `GETFIELD/SETFIELD` 的语义，再判断是否存在 CALL 路径。不要将未知 F 与其所在方法所属 C 强行绑定为 **F 的所有者**。

## 可复现

仓库新增 `scripts/trace_sv_lua_c2f.py`，标准库 Python 3.10+。在已拥有原始文件的机器上运行：

```powershell
python scripts/trace_sv_lua_c2f.py "D:\\SV\\main.blua" "D:\\SV\\main_dynamic.blua" --repo . --game SV --report docs/sv-c2f-native-report.json --assignments sv_c2f_assignments.tsv.gz

python -m unittest discover -s tests -v
python scripts/lua_hash.py verify
```

TSV.gz 会记录所有 23,727 条：文件、Proto ID、类 Hash、函数 Hash、Closure Proto ID、PC、物理字节偏移、K 索引和寄存器；**源文件本身不会提交到 GitHub**，只输出可核查的派生证据。

技术限制：本轮是一个严谨的、可复核的 **连续 8 指令模式识别器**，不是覆盖所有可能的 Lua 编译形式的通用控制流分析器。没有匹配不代表不存在其他形式的赋值关系。

关联：[[SV-Library-BLua-Audit]]、[[Lua-Source-Evidence]]、[[Hash-Evidence-Standards]]。
