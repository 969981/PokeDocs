---
tags: [Lua, bytecode, source-evidence, SV, ZA, scripts]
status: TOOL_READY_SOURCE_NOT_EXTRACTED
---

# 从原生 Lua 源码与字节码收集 Hash 证据

## 已取得的进展

- [[Hash-Recovery-Round2|第二轮]] 已回填 84 个唯一 Hash，剩余 2,945 行（截至 2026-11-05）。
- SV-Script-RE 历史 3.0.1 版本 `data/lua_names.h` 内只新增一个与当前空白 C Hash 严格对应的名字：`main.ui.hud_info.HudInfoPlayer`。
- 此历史头文件与当前列表另有 4 个同 Hash 不同名，不能直接合并。保留原记录，报告冲突。
- SV 4.0.0 原生 `.blua` 目前只在 `SV_Resources` 的归档 **索引**中定位，不能宣称已经提取或解码。
- 上游真实参考：[SV-Script-RE](https://github.com/Martmists-GH/SV-Script-RE/tree/1f843bd2517c707fbb47491dad58856eaa2c2cc7)，其反编译代码主要对应 3.0.1 时代。

## 以源码／头文件生成带来源的匹配报告

```powershell
python scripts/scan_lua_evidence.py --game SV --source "D:\\Research\\SV-Script-RE\\data\\lua_names.h" --source-version "SV-Script-RE commit 1f843bd (3.0.1-era)" --output docs/lua-source-audit.json --names-out docs/lua-candidates.txt

# 加入全量 Lua 反编译目录
python scripts/scan_lua_evidence.py --game SV --source "D:\\Research\\SV-Script-RE\\decompiled" --source-version "SV 3.0.1-era historical" --output lua-decompiled-audit.json
```

本脚本提取：头文件显式编码与原名的配对、Lua 注释与 `function C..._prototype:F...` 的连续定义、函数定义名、原样字符串字面量。**所有候选都必须完整 64 位 Hash 匹配**；源文件保留 SHA-256、路径、行号、版本。

该工具仅产生候选及审计 JSON；不自动覆盖任何空白源列表。将 `--names-out` 输出用于已有的 `lua_hash.py recover --dictionary ...` 时，必须先审阅候选来源，才可以 `--apply`。

## SV 4.0.0 原生字节码位置

来源：[SV_Resources 原生 TRPFD 索引](https://github.com/969981/SV_Resources/blob/master/Unpack/4.0.0/romfs/arc/data.trpfd/_index/lua_pack_locations.json)。

| 虚拟路径 | Pack Index | 包大小 | 进度 |
| --- | ---: | ---: | --- |
| `script/lua/bin/release/main/main.blua` | 21977 | 2,966,760 bytes | 已定位，未取得原始字节码 |
| `script/lua/bin/release/main_dynamic/main_dynamic.blua` | 21978 | 1,028,024 bytes | 已定位，未取得原始字节码 |

拿到原始文件后在本地运行：

```powershell
python scripts/scan_lua_evidence.py --game SV --bytecode "D:\\SV\\main.blua" --bytecode "D:\\SV\\main_dynamic.blua" --source-version "SV 4.0.0 original bytecode" --output audit-sv-4.0.0.json
```

其中 `--bytecode` 只读原始 ASCII 编码 token（C/F/S/E + 16 位十六进制）并统计首次偏移、出现次数和 SHA-256；**在字节码中出现某个 Hash 不等于证明对应函数调用，也不能自动产生原名**。若无匹配，不代表不存在，可能是字节码压缩或字符串表示不同。

真正语义确认需要：解包原始 `.blua` → 验证字节码文件格式 → 分析对象构造、函数定义与调用点 → 将字段或方法回到可验证字符串 → 再匹配 Hash。没有原生证据，不升级 H3。

## 后续 QA

```powershell
python -m unittest discover -s tests -v
python scripts/lua_hash.py verify
```

参见 [[Hash-Evidence-Standards]]、[[Hash-Recovery-Workflow]]。

## 自动化审计工作流

[Audit historical SV Lua sources](https://github.com/969981/PokeDocs/actions/workflows/lua-source-audit.yml) 拉取固定 SHA 的上游 `data/`、`decompiled/` 和根目录 `main.dumped.lua`，在 GitHub Actions 运行来源匹配、生成 JSON 与候选字典 artifact（30 天保存），**不上传或提交上游 Lua 原文件**。这是旧版 3.0.1 时代资料审计，不是 4.0.0 的原生验证。

如果工作流未完成或报告无新候选，不要将未命名 Hash 视为已恢复。

历史源文件已通过第一次完整 Header＋decompiled 审计：新增 Hash 命中 **0**（因为上一轮已回填 1 条直接 Header 命中），记录 **7 条冲突**、现有 17,948 个非空 Lua 名称校验通过；现在将约 42 MB 的 `main.dumped.lua` 也纳入扫描，以覆盖拆分文件未出现的字符串。该大文件依然只在 CI 临时工作区分析，不提交原始内容。

## 已完成：历史完整版 Lua 实际扫描（2026-11-05）

已完成 [GitHub Actions #41989024093](https://github.com/969981/PokeDocs/actions/runs/41989024093)，结论为 **SUCCESS**；并在 [GitHub Actions #41989024151](https://github.com/969981/PokeDocs/actions/runs/41989024151) 通过代码与 Hash 校验。

| 检查项 | 实际结果 |
| --- | --- |
| 历史源码版本 | `SV-Script-RE@1f843bd2517c707fbb47491dad58856eaa2c2cc7` |
| 输入 | `data/lua_names.h`、完整 `decompiled/`、`main.dumped.lua` |
| 当前未知 Hash 的新增原名匹配 | **0** |
| 旧版名称与现有映射的冲突 | **7**（保留现有，不覆盖） |
| 当前已命名 Lua Hash 重算 | **17,948 / 17,948 匹配** |
| 当前 SV/ZA Lua 未命名行 | **2,945** |
| 导出审计 | Actions artifact：`SV-3.0.1-lua-hash-audit`，保留 30 天 |

因为旧版 header 的 1 条原名已在第二轮提前回填，**此处 0 是增量命中，不是表示整个历史源码没有任何已知名称**。

> [!IMPORTANT] **现有公开历史源码进一步挖掘已无新增**，而 SV 4.0.0 的 `main.blua` / `main_dynamic.blua` 在 `SV_Resources` 中仍只确认了 TRPFD 索引位置（21977、21978）。后续必须以实际原始字节码、场景/脚本字符串和调用上下文取得新来源，不能把原始 Hash 值对应的 C/F 文件名当作已经还原的可读符号名。

ZA 的对应原始 Lua 脚本尚未取得和验证，本次不虚报 ZA 原生恢复进度。
