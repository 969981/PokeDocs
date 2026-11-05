---
tags: [PokeDocs, ZA, Lua54, AArch64, ELF, Trinity, native, host-loader, provenance]
date: 2026-11-05
status: VERIFIED_NATIVE_ELF_XREF_RUNTIME_ENV_NOT_YET_PROVEN
source_repo: 969981/ZA_Resources
source_pr: 4
---

# ZA 2.0.2：Lua 宿主 ELF 初步精确定位

> [!IMPORTANT]
> 这一阶段取得的是 **ExeFS AArch64 ELF 原生字符串与地址引用证据**，不是 `lua_load` 已定位、`_ENV` 已由宿主绑定或方法接收类已证明。**Hash 原名新增恢复 0；运行时对象身份确认 0。**

## 从 Lua P0.U0 追到宿主 ELF 的调查线索

前一阶段的四份 Lua 5.4 字节码验证表明，926 条 `GETTABUP` 静态类键查找均可沿原生 `instack/idx/kind` 描述符回溯至对应根 Chunk 的 `P0.U0`。本阶段使用已验证 `main/sdk/rtld.elf`，逐份 SHA-256 对账后进行针对性的离线地址扫描。

- `main.elf`：**90** 条精筛 Lua/Trinity 字符串、**112** 条真实 AArch64 `ADR/ADRP+ADD` 字符串地址引用。
- `sdk.elf` 和 `rtld.elf`：在同一过滤词范围无命中，不代表不包含 Lua 相关代码。
- 10 个高信号字符串中 **13** 条精确寻址指令，导出 **533** 条 ±20 指令原始窗口，便于 Ghidra/IDA 跟踪。
- 三个模块未直接发现五个缺失 S Hash 或 `IkScriptCommand` C Hash 的 ASCII/LE/BE 固定字节模式；不能据此判断算法没有运行时构造。

## 直接使用的原生 VA（相对 main ELF 映像）

| 静态内容 | 字符串地址 | 已验证的原生指令地址 |
| --- | --- | --- |
| `_ENV` | `0x31F263F` | `0x17AD604`、`0x17AD6B8`、`0x17B9920`、`0x17B9F94` |
| `LUA_NOENV` | `0x31A540F` | `0x17CD58C` |
| `LUA_PATH` | `0x326AB1C` | `0x17CD434` |
| `LUA_CPATH` | `0x321E011` | `0x17CD454` |
| `lua_helper` | `0x32B6EDE` | `0x118ACDC` |
| `TrinityHeapType::Lua` | `0x31BBCE5` | `0x1B2430C`、`0x1B244D0`、`0x1B24610` |
| `arc/data.trpfs` | `0x326AE1B` | `0x1A809F0` |
| `data:/arc/data.trpfd` | `0x32EE619` | `0x1A80A24` |
| `script/lua/bin/release/` | `0x31B7C6E` | 当前未获得直接 ADR/ADRP+ADD |
| `.blua` | `0x32D7D84` | 当前未获得直接 ADR/ADRP+ADD |

请注意这些 PC 属于 **v2.0.2 的 `main.elf` 映像虚拟地址**，并非已确认的运行时绝对进程地址。对 GDB 运行时模块，需要结合实际模块加载基址换算。

该 ELF 的静态 `RELA` 包括 3323 条 `R_AARCH64_ABS64`、55 条 `GLOB_DAT` 和 919 条 `JUMP_SLOT`；对上述十个字符串 VA 仍未得到可绑定的精确指针位置。既不保证所有间接引用可被当前模型识别，也不能把邻近 BL 直接判断为加载调用。

## 验证、脚本和结果文件

已合并 [ZA_Resources PR #4](https://github.com/969981/ZA_Resources/pull/4)，[成功的原生研究分支 CI #42028778681](https://github.com/969981/ZA_Resources/actions/runs/42028778681) 包括 11 个合成测试和 SHA-256 对账。

- [原生 ELF 扫描与 AArch64 ADR/ADRP 解析器](https://github.com/969981/ZA_Resources/blob/master/scripts/Probe-ZA-Lua-Host-ELF.py)
- [Lua 宿主字符串、分支提示、ELF RELA 追踪](https://github.com/969981/ZA_Resources/blob/master/scripts/Trace-ZA-Lua-Host-Callsites.py)
- [地址及静态结果 TSV](https://github.com/969981/ZA_Resources/tree/master/Unpack/v2.0.2/romfs/arc/data.trpfs/_index/lua-native)
- [Obsidian 原生调查笔记](https://github.com/969981/ZA_Resources/blob/master/docs/research/v2.0.2/za-lua-host-elf.md)

~~~powershell
py -3 scripts/Probe-ZA-Lua-Host-ELF.py
py -3 scripts/Trace-ZA-Lua-Host-Callsites.py --window 20
~~~

后续优先证明哪一个宿主函数读取 `script/lua/bin/release/` 和 `.blua`，它如何调用 Lua Chunk 加载接口并设置根 `P0.U0`，以及 `IkScriptCommand` 对应的类表值是如何在同一运行时环境内注册的。只有闭合这条因果链，才能将“静态 Hash 类键”提高为真正的运行时对象证明。

关联：[[ZA-Lua-Upvalue-Captures-2026-11-05]]、[[ZA-Lua-Closure-Receiver-2026-11-05]]、[[ZA-Lua-Register-Flow-2026-11-05]]。
