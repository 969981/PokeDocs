---
tags: [PokeDocs, SV, Lua54, native-bytecode, class-factory, metatable, Obsidian]
date: 2026-11-05
status: LOCAL_NATIVE_SHA_VERIFIED_RUNTIME_INSTANCE_IDENTITY_UNCONFIRMED
source: user-Library-original-SV-main.blua
---

# SV 4.0.0：95 个未知 C 的共用工厂、元表与 `__name__` 原生证据

> [!IMPORTANT]
> 以下是**原始 4.0.0 `main.blua` 字节码的结构验证**，不是游戏运行时实例或原始可读类名的确认。当前未知 SV C **1,334**、ZA S **114**、ZA F **41** 不变；本轮新确认名字 **0**，Hashlist 更改 **0**。

## 原生输入及校验

- 原始 `main.blua` 长度：12,912,264 字节
- SHA-256：`c1a4f4e2625912cf0b739a642a79ba3357df0557a544b92da22a6cb139de2815`
- 根 Prototype：429,034 条 Lua 5.4 指令
- 95 个 C：当前 Hashlist **未知且同时有全局注册与 C→S 静态闭包**；对应注册 95，静态 S 闭包 252。
- 解析器：`Analyze-SV-Lua54.py`（原生 Lua 5.4）。
- 复验代码：[`scripts/trace_sv_factory_metatable.py`](../scripts/trace_sv_factory_metatable.py)，同时保留 [`scripts/audit_sv_dual_global_slot.py`](../scripts/audit_sv_dual_global_slot.py)。

## 根 Prototype 的工厂结构已闭合

原生指令确认：

| 位置 | 字节码结构 | 可证明事项 |
| --- | --- | --- |
| PC 42 | `CLOSURE R12` | 构建后续元表方法（写入 `__newindex`） |
| PC 43 | `NEWTABLE R13` | 创建共享元表候选 |
| PC 45 | `SETFIELD R13["__newindex"]=R12` | 使用实际原生字段字符串 |
| PC 46–47 | `GETTABUP _hx_tostring`、`SETFIELD R13["__tostring"]` | 同一元表两个字段 |
| PC 49 | `CLOSURE R15` | 对应根子 Prototype 19 |
| Proto 19 | Upvalues `[(0,0,0),(1,13,0)]` | 第 1 个 Upvalue 捕获根栈 `R13` |
| Proto 19 PC 0–7 | `GETTABUP(setmetatable)`、`NEWTABLE`×2、`SETFIELD(__fields__)`、`GETUPVAL(1)`、`TAILCALL` | 工厂调用 `setmetatable(new_table_with_fields, captured_metatable)` |

`R15` 从根 PC 49 到最后一条相关全局注册期间，**没有发现本轮覆盖的直接或可能的寄存器覆盖指令**；95 条 `_ENV[C]` 全局注册均取 `R15` 并调用该工厂，证据共 **95/95**。

重要限制：`TAILCALL` 返回的是 `setmetatable` 的调用结果，不应将其简化为“直接返回 `NEWTABLE` 的裸表”；后续代码可能改变 _ENV 表键内容，故不能证明运行时实例身份不变。

## 新证据：95/95 个类均有 `__name__ = C_TOKEN`

除 95 条注册、252 条静态 S 方法写入外，根原型中每个 C 都具有**唯一一条**严格指令匹配：

~~~lua
-- 原生指令的等价表示，非原始可读 Lua 源码
_ENV[C_HASH].__name__ = C_HASH
~~~

严格指令形态为 `GETUPVAL → LOADK(C) → GETTABLE → LOADK("__name__") → LOADK(C) → SETTABLE`，两个 C 常量逐字节相等，均操作根 Upvalue 0 的同一键。

- **95 个 C，95 条写入，0 条模式错误。**
- 这是 *C Hash 作为类表标识符元数据* 的原生证据。
- `__name__` 字段存储仍是 `Cxxxxxxxxxxxxxxxx`，**不是可读的 Haxe/Lua 原始类名**，不能据此将 95 个 Unknown 改成“已恢复”。

对这 95 个 C 的根原型全部 `LOADK(C)` 共发现 652 处直接引用：其中 95 处全局注册写入、95 处 `__name__` 值写入，另有 462 处随后对相关类键进行 `GETTABLE` 查找（包括 252 条 S 闭包赋值和其它查找）。这些数量是字节码引用次数，不是 652 个不同类或执行次数。

## 再下一步的必要证据

1. 从注册调用到 `__name__` 赋值再到 S 闭包写入，逐类检查可能覆盖 `_ENV[C]` 的显式写入，以及调用引入的间接副作用；只可称为“当前支持模式内未观察到”，不能声称完全不存在。
2. 对 Proto 19 的 `setmetatable` 返回值，必要时在游戏运行时采样对象引用，验证 `_ENV[C]` 在注册后和方法赋值时是否仍指向同一对象。
3. 对原名须找到独立 UTF-8 命名、反射/注册字符串或其他明确来源，不因 `__name__ = C_HASH` 自动升级 H3。

## 本地复验

~~~powershell
python scripts/trace_sv_factory_metatable.py `
  --main "D:\SV\main.blua" `
  --parser "D:\SV\Analyze-SV-Lua54.py" `
  --registrations "D:\SV\followup-c-global-registrations.tsv" `
  --static "D:\SV\followup-c-static-s-closures.tsv" `
  --unknown "SV/Hashlists/Lua/lua_c_hashes.txt" `
  --out "D:\SV\factory-audit"
~~~

输出 `sv-95-factory-summary.json` 与 `sv-95-factory-registers.tsv`；**不会修改 BLUA 或 Hashlists**。原始游戏文件不提交 GitHub。此阶段采用真实本地输入执行验证，**未将缺少原始 BLUA 的 GitHub Actions 冒充原生 CI**。

关联：[[Lua-Proto-Owner-Join-2026-11-05]]、[[Lua-Closure-Evidence-2026-11-05]]、[[Hash-Evidence-Standards]]。
