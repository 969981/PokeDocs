---
tags: [hash-recovery, script, provenance, SV, ZA]
---

# Lua Hash 恢复流程

## 0. 初始条件

Python 3.10+，仓库中的 SV/ZA Lua Hashlist 已存在。不需要 pip 依赖。原始未知值通常是一行 `0x????????????????`，后面没有名称；支持哈希后有空格和无空格两种输入形式。

## 1. 验证计算方式

```powershell
python scripts/lua_hash.py calc SetCursorPos onComplete
python scripts/lua_hash.py verify
python -m unittest discover -s tests -v
```

`verify` 校验每条已命名记录；一旦不一致，以非 0 退出，禁止无条件继续写回。

## 2. 执行干运行

```powershell
python scripts/lua_hash.py recover --numeric-radius 8
```

候选来源依次包括：同仓库已知名称的跨游戏/跨类别精确复用；已知名称中单个数字段的 ±8 枚举；有限的 `Get/Set/Is`、`get_/set_`、`On/on` 前缀变体。数字只是帮助生成候选，最终必须把候选的**完整 Hash 算出并匹配**。

可加入外部文本字典，每行一个未经转义的原样 Lua 名称：

```powershell
python scripts/lua_hash.py recover --dictionary .\my_lua_symbols.txt --json-out .\candidate-audit.json
```

避免给字典批量做不受约束的大小写替换；标注原名称从何而来。运行时能取得的 Lua 字符串和原生解包文本比随机猜测更有价值。

## 3. 审阅和唯一匹配写回

```powershell
python scripts/lua_hash.py recover --numeric-radius 8 --markdown-out docs/New-Candidates.md --json-out docs/new-candidates.json
python scripts/lua_hash.py recover --numeric-radius 8 --apply
python scripts/lua_hash.py verify
git diff -- SV/Hashlists/Lua ZA/Hashlists/Lua
```

- 不覆盖已有名字；只对空白且唯一命中的 Hash 写入。
- 只改命中行，保留原大小写、未知记录和其他文件。
- 多个不同名字匹配同一 Hash 时保留空白，写到歧义报告。
- 自动匹配仅属于“Hash 等值验证”；高价值条目应继续从实际 Lua 脚本或原生调用链确认语义。

**注意：** `--apply` 后再运行 `recover`，已填充项不再算空白。对应提交前的历史统计请查看 [[Hash-Recovery-Results]] 的快照。

## 4. 持续恢复建议

优先从已解包 Lua 字节码、运行时函数名、完整脚本、枚举、跨版本差异与真实资源路径收集 **可引用的字典**。增量保留字典来源和版本、验证差异、提交 SHA，再将高可信候选回填。不要通过相邻数字的直接推断绕过完整 64 位验证。

参见 [[Hash-Algorithms]]、[[Hash-Evidence-Standards]]。

## 外部研究证据的已审计导入

SV_Resources 的固定提交候选已在 `develop` 的第三轮核验，并保留完整来源 TSV；详见 [[SV-Resources-Research-Sync-2026-11-05]]。执行 `python scripts/verify_sv_resources_import.py` 只读核对已回填行、完整 Hash、原始行号、重复冲突和证据文件，不会再自动写回。后续外部快照变更必须重新审阅来源和冲突后才能更新，不能仅运行 `recover --apply` 就把第三方重建符号当作原生语义确认。
