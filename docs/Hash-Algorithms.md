---
tags: [hash, fnv1a, SV, ZA, Lua]
---

# Lua Hash 计算方法

## 已确认的算法

通过对 SV/ZA 八份 Lua Hashlist 中 **17,797 条已知名称**逐字节重算，全部与仓库原始值相同；随后将本轮新增匹配回填。此处已验证的是 **Lua 符号名称** 的哈希，不是 FileSystem 路径哈希。

| 参数 | 值 |
| --- | --- |
| 算法 | 64 位 FNV-1a 变体 |
| 初始值（offset basis） | `0xCBF29CE484222645` |
| FNV prime | `0x00000100000001B3` |
| 计算单位 | 原始名称 UTF-8 字节序列 |
| 运算 | XOR 字节，乘 prime，模 `2^64` |
| 大小写 | **敏感**；不做路径规范化 |
| 输出格式 | 16 位十六进制数字、前缀 `0x` |

公式（每个字节 `b`）：

```text
h = 0xCBF29CE484222645
for b in UTF8(symbol):
    h = ((h XOR b) * 0x100000001B3) & 0xFFFFFFFFFFFFFFFF
```

注意：标准 FNV-1a 64 位 offset basis 为 `0xCBF29CE484222325`，而这里的已验证初始值为 **`...2645`**。若直接使用标准库的默认 FNV-1a，就会得到**错误**的 Lua Hash。

## 对账用例

| 原字符串 | 输出 |
| --- | --- |
| `SetCursorPos` | `0x0170EA75A6880AF5` |
| `GetMenu` | `0x00D5938E012F68A8` |
| `onComplete` | `0x0085F7055F019927` |
| `getListSize` | `0x01D67550130FC696` |
| `main.event.ik.CoroutineExecutor` | `0x051A4F1726DB4DE1` |

例子：

```powershell
python scripts/lua_hash.py calc SetCursorPos GetMenu
python scripts/lua_hash.py verify
python -m unittest discover -s tests -v
```

实现以 UTF-8 编码所有字符，不强制转小写，不补 `\0` 终止字节，也不做字符规范化。

## 可以恢复哪些 Hash？

FNV-1a 是多对一的非加密 Hash，不存在可普遍恢复唯一原名的逆函数。实际可行的是：从其他版本的名称、Lua 字符串/函数名、数字序号和命名规则生成候选，再比对完整 64 位结果。**相邻 Hash 的数值规律是候选线索，不是命名证明。**

恢复标准见 [[Hash-Evidence-Standards]]；具体脚本见 [[Hash-Recovery-Workflow]]。

## 不能混用的算法

目前已通过五组 ZA TRPAK **内部资源路径** 对账：它们与 Lua 符号采用相同的 64 位 FNV-1a 变体、offset basis 和 UTF-8 编码，但必须以原始路径字符串作为输入。外层 `@arc` 归档键的预处理方式，以及 `GFPAKHashCache.bin` 的二进制序列化格式，尚未完成验证。工具为 `scripts/trinity_path_hash.py`，细节见 [[FileSystem-Hashes]]。
