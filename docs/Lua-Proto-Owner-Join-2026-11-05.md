---
tags: [PokeDocs, SV, ZA, Lua54, native-evidence, proto-owner, Obsidian]
date: 2026-11-05
status: ROOT_CLOSURE_CONTEXT_JOIN_VERIFIED_RECEIVER_IDENTITY_UNCONFIRMED
---

# ZA 原生 Lua：1,488 条局部调用与类闭包 Prototype 归属对账

> [!IMPORTANT] 这里的 `source + proto_id` 是**调用所在的函数闭包上下文**，不是函数调用目标的运行时接收对象。没有恢复任何新的原始符号名，没有证明任意 C 类实例就是被调用字段的持有者。SV C 未知 **1,334**；ZA S 未知 **114**、F 未知 **41**，保持不变。

## 本轮实际完成

从 ZA_Resources v2.0.2 的四份 SHA-256 已验证原生 Lua 提取数据，按文件独立的 Prototype ID 对接：

- `native-c-f-method-edges.tsv` 的 `(source, child_proto_id)` 与 `native-unknown-register-flow-calls.tsv` 的 `(source, proto_id)`；
- `native-c-s-static-edges.tsv` 的 `(source, closure_proto_id)` 与相同调用索引；
- 对映射到同一个 Prototype 的多个 C/F/S 归属**直接报错**，绝不任选一项；
- 仅允许来自根级父原型 `parent_proto_id=0` 的直接闭包。跨文件相同数字 ID 不相等，也不会把子原型的后代自动归属为同一个类。

CI [42021388766](https://github.com/969981/ZA_Resources/actions/runs/42021388766) **成功**；脚本与合成测试：[Join-ZA-Lua-ClosureCalls.py](https://github.com/969981/ZA_Resources/blob/master/scripts/Join-ZA-Lua-ClosureCalls.py)、[test_za_lua_closure_join.py](https://github.com/969981/ZA_Resources/blob/master/tests/test_za_lua_closure_join.py)。

## 原生结果（ZA_Resources master 发布数据）

| 指标 | 本轮结果 |
| --- | ---: |
| 根级 C→F 赋值 | 3,064 |
| 根级 C→S 赋值 | 878 |
| 唯一的根级闭包 Prototype 键 | 3,942（无歧义冲突） |
| 局部字段→CALL 边 | 1,488 |
| 可关联到已知根级闭包的调用边 | **1,461** |
| 涉及的已关联 Prototype | **654** |
| F 方法闭包上下文内调用 | **1,414** |
| S 静态闭包上下文内调用 | **47** |
| 涉及不同 C Hash | **606** |
| 具体 `(source, C, owner-field, called-field)` 组合 | **906** |
| 未关联调用 | **27**（嵌套 Prototype 9，未归属根级/其它 18） |
| 确认运行时 receiver 对象 / 原始名称 | **0 / 0** |

可独立核对：

- [原生逐调用归属 TSV](https://github.com/969981/ZA_Resources/blob/master/Unpack/v2.0.2/romfs/arc/data.trpfs/_index/lua-native/native-unknown-call-closure-context.tsv)
- [类方法→被调字段优先队列](https://github.com/969981/ZA_Resources/blob/master/Unpack/v2.0.2/romfs/arc/data.trpfs/_index/lua-native/native-unknown-class-call-priority.tsv)
- [输入 SHA-256 与 27 项未关联明细](https://github.com/969981/ZA_Resources/blob/master/Unpack/v2.0.2/romfs/arc/data.trpfs/_index/lua-native/native-unknown-call-closure-summary.json)

在 **PokeDocs/develop 当前未知 S 114 / F 41** 集合中，1,488 条旧未知基线的调用有 **1,470 条**仍涉及当前未知 Hash，其中 **1,443 条**落在已匹配根级闭包中；这组过滤数量不可与 ZA_Resources 初始 S 116/F 43/E 3 的基线混为一谈。

## 下一步：接收对象而不是闭包归属

1. ZA：以 **1,443 条当前未知且闭包上下文已匹配**的调用为入口，抽取调用 `field_pc` 处 `GETFIELD/GETTABUP/SELF/GETTABLE` 的接收者寄存器或 Upvalue 编号。将指令 `B` 寄存器的来源追溯到 `MOVE`、形参、闭包 `GETUPVAL`、表创建/全局加载；分支交汇和不可解析写回必须标为 UNKNOWN。
2. ZA：优先回溯剩余 **9 条嵌套子原型**的 parent→child CLOSURE 关系；其余 **18 条非直属归属**单独定位，不借用相邻方法的类名。沿寄存器流证明实例建表→字段赋值→方法调用后才能把“类上下文”升级为“接收者绑定”。
3. SV：对 [[Lua-Closure-Evidence-2026-11-05]] 的 **95 条双重结构 C**，必须分别追踪全局注册 `root_pc`、C→S `root_pc` 中所读取的表值及同一原型内的寄存器/表别名。相同 C Hash 对应的 252 条 S 闭包与 95 条全局注册只是静态双重证据，**不是**已经证明注册对象等于方法写入对象；这些 95 个 C 也没有严格的 C→prototype→F 直接赋值证据。
4. 五条四包常量池缺失的 S Hash 继续保持缺失；需调查其它原生 Lua/事件和版本，不得用 Haxe 反推确认。

## 自动化复核

在 ZA_Resources 仓库（**无需重新提取 4 份 .blua**）运行：

```powershell
python -m unittest discover -s tests -p test_za_lua_closure_join.py -v
python scripts/Join-ZA-Lua-ClosureCalls.py --check
# 如上游 TSV 更新，可显式重建并审核差异
python scripts/Join-ZA-Lua-ClosureCalls.py --write
```

关联：[[Lua-Closure-Evidence-2026-11-05]]、[[ZA-Lua-Register-Flow-2026-11-05]]、[[Hash-Evidence-Standards]]。
