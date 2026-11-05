---
tags: [PokeDocs, ZA, Lua54, Trinity, Upvalue, CLOSURE, native-evidence, Obsidian]
date: 2026-11-05
status: VERIFIED_LEXICAL_CAPTURE_RUNTIME_ENV_UNKNOWN
source_repo: 969981/ZA_Resources
source_pr: 3
---

# ZA 2.0.2：926 条类 Hash 查找的原生 Upvalue 捕获链

> [!IMPORTANT]
> 原生 Lua 5.4 捕获描述符 `instack/idx/kind` 已逐字节解析；**本轮没有确认新增原始 Lua Hash 名，也没有证明动态接收者所属类。** 不能把根 Chunk 外部 Upvalue 无条件称为已确定的 `_ENV` 表。

## 实证结果

ZA_Resources 四份 SHA-256 固定的 Lua 已重新解码检验；此前 1,488 条 CALL 中有 **926 条** C Hash 作为 `GETTABUP` 类表查找键。对这 926 条的 512 个不同 Prototype，沿父原型 `CLOSURE Bx` 创建指令及每一层三字节 Upvalue 捕获描述符得到：

| 验证项 | 数量 |
| --- | ---: |
| 查找指令及类 Hash 常量精确匹配 | **926** |
| 回溯终点 `P0.U0=EXTERNAL_CHUNK_UPVALUE` | **926** |
| 仅跨 1 层捕获 | 919 |
| 跨 2 层捕获 | 6 |
| 跨 5 层捕获 | 1 |
| 运行时接收者类确证 | **0** |
| 新恢复原始 Hash 名称 | **0** |

最长的已验证路径出现在 `event_ik`：`P88.U0 → P87.U0 → P86.U1 → P85.U1 → P83.U0 → P0.U0`，中间经过的每个 `CLOSURE Bx` 均有原生创建 PC 证据。**所有 926 条路径的捕获边都是父 Upvalue 传递（`instack=0`），不是被猜测的父栈局部寄存器。**

类键分布仍为：`IkScriptCommand` 908、`CafeEvent` 8、`CharacterCommand` 7、`ObjectTemplateDataManager` 2、`FadeCommand` 1。上述可读名称来自 develop 当前已有的 C Hashlist，不是本轮发现的原名。

## 7 条嵌套与 20 条未归属 CALL

- 7 条有词法 owner 的内层 CALL，已找到对应内层 Prototype 的父级 `CLOSURE`。
- 20 条未找到已验证 C→F/C→S 注册 owner 的 CALL 均属于 `main`，集中在 11 个 Prototype：80、104、125、139、141、142、143、151、156、163、172。
- **27 条全部恰好找到 1 个父级原生 `CLOSURE` 创建位置**，并导出子原型 Upvalue 描述符；这是创建位置的确认，不表示存在实际运行调用，或已经找到了原始类归属。

## 复现与后续使用

已合并 [ZA_Resources PR #3](https://github.com/969981/ZA_Resources/pull/3)，[主分支原生 CI #42026366711](https://github.com/969981/ZA_Resources/actions/runs/42026366711) 成功（8 个合成测试及四份原生 Lua SHA-256 校验）。

- [Trace-ZA-Lua-Upvalue-Captures.py](https://github.com/969981/ZA_Resources/blob/master/scripts/Trace-ZA-Lua-Upvalue-Captures.py)
- [native-upvalue-capture-lookups.tsv](https://github.com/969981/ZA_Resources/blob/master/Unpack/v2.0.2/romfs/arc/data.trpfs/_index/lua-native/native-upvalue-capture-lookups.tsv)
- [native-closure-unresolved-sites.tsv](https://github.com/969981/ZA_Resources/blob/master/Unpack/v2.0.2/romfs/arc/data.trpfs/_index/lua-native/native-closure-unresolved-sites.tsv)
- [native-upvalue-capture-summary.json](https://github.com/969981/ZA_Resources/blob/master/Unpack/v2.0.2/romfs/arc/data.trpfs/_index/lua-native/native-upvalue-capture-summary.json)
- [技术说明](https://github.com/969981/ZA_Resources/blob/master/docs/research/v2.0.2/za-lua-upvalue-captures.md)

~~~powershell
py -3 -m unittest discover -s tests -p test_za_lua_upvalue_captures.py -v
py -3 scripts/Trace-ZA-Lua-Upvalue-Captures.py --max-window 16
~~~

## 后续真正的阻塞

静态捕获关系已经闭合到 `P0.U0`，下一个关键证据在宿主加载器：找到如何创建 Lua Chunk、向其根 Upvalue 注入表、将 `IkScriptCommand` 的 C Hash 类名键映射到表值，再追踪字段函数调用。若没有实际 ExeFS 或运行时宿主链，不把 PokeDocs 名称映射提升为原生执行时的对象身份。

关联：[[ZA-Lua-Closure-Receiver-2026-11-05]]、[[ZA-Lua-Register-Flow-2026-11-05]]。
