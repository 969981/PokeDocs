---
tags: [filesystem, Trinity, TRPAK, hash, GFPAK]
---

# FileSystem / TRPAK Hash

## 新增验证：TRPAK 内部资源路径

现已使用 ZA 资源目录中的多条完整路径／Hash 对进行检验：内部文件路径采用与 Lua 符号相同的 **UTF-8、64 位 FNV-1a 变体和初始值** `0xCBF29CE484222645`。计算对原字符串直接进行，当前已验证样例使用正斜杠 `/`，不含额外 `arc/`。

| 原始路径 | 64 位 Hash |
| --- | --- |
| `avalon/data/personal_array.bin` | `0x68AB38E2CF1281ED` |
| `avalon/data/growTable.bin` | `0x6E640887C479E026` |
| `avalon/data/waza_array.bin` | `0xA90026235522C2F0` |
| `avalon/data/tokusei_array.bin` | `0xACD40B49C2F91CCD` |
| `ai_influence/ba_battle_area_0003_01_00_00.imap` | `0x05AFD1BF8BA6BBF9` |

校验样例参考：ZA 内部 TRPAK 文件清单（PokeDocs）及其对应的资源目录资料。记录了 5 组完整输入与输出，已加入 Python 单元测试。这里确认的是**内部路径的直接 Hash**，不是外层 `@arc\\...trpak` 名称字符串的处理方式。

```powershell
python scripts/trinity_path_hash.py calc "avalon/data/personal_array.bin"
python scripts/trinity_path_hash.py calc "ai_influence/ba_battle_area_0003_01_00_00.imap"
python scripts/trinity_path_hash.py verify ZA/Hashlists/FileSystem/hashes_inside_trpak.txt
```

其中 `verify` 只会核对输入里确实具备 `0xHASH path` 的条目；遇到原始容器清单、复合头或不同层级的 Hash，可能需要提取其中的路径条目再测，不应据此宣称整个归档算法错误。

## 用候选路径匹配未知 Hash

将未知值（每行一个 `0x????????????????`）存为 `unknown.txt`，将原样路径候选（每行一个）存为 `path_candidates.txt`：

```powershell
python scripts/trinity_path_hash.py recover --targets unknown.txt --dictionary path_candidates.txt --output matched_paths.tsv
```

只将完整 64 位 Hash 精确命中的候选写到报告，不修改原始数十 MB 的源 Hashlist。候选来源优先是真实 RomFS／TRPFD／脚本中提取的路径，不能根据数字邻接而直接伪造路径名称。

## 仍需研究的不同层级

1. 外层 TRPFD/TRPFS/TRPAK 的 `@arc` 归档键：其文件名预处理、转义与 Hash 输入字符串应另取样验证。
2. `GFPAKHashCache.bin`：需要确认其头部、条目排序、键值结构、字节序以及实际消费者版本；不能将内部路径 Hash 算法等同于缓存文件序列化协议。
3. 不具备原始字符串的未知 Hash：保持 UNKNOWN；Lua 相关方法详见 [[Hash-Recovery-Workflow]]。
4. `hashes_inside_fd.txt` 与 `hashes_inside_trpak.txt` 是否每一节均使用同样的输入约定，仍需分别批量验算。

计算核心见 [[Hash-Algorithms]]，证据标准见 [[Hash-Evidence-Standards]]。
