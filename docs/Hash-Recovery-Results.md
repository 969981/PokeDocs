# Lua Hash 恢复报告（2026-11-05）

> [!IMPORTANT] 以下名称都经过完整 64 位 Hash 精确验证，但不代表已通过游戏运行时调用链核对其语义。

## 统计

| 文件 | 已有名称 | 原空白 | 本次回填 | 剩余空白 |
| --- | ---: | ---: | ---: | ---: |
| `SV/Hashlists/Lua/lua_c_hashes.txt` | 1911 | 1375 | 29 | 1346 |
| `SV/Hashlists/Lua/lua_e_hashes.txt` | 215 | 2 | 0 | 2 |
| `SV/Hashlists/Lua/lua_f_hashes.txt` | 8348 | 116 | 9 | 107 |
| `SV/Hashlists/Lua/lua_s_hashes.txt` | 5793 | 830 | 17 | 813 |
| `ZA/Hashlists/Lua/lua_c_hashes.txt` | 1202 | 0 | 0 | 0 |
| `ZA/Hashlists/Lua/lua_e_hashes.txt` | 0 | 3 | 3 | 0 |
| `ZA/Hashlists/Lua/lua_f_hashes.txt` | 127 | 138 | 2 | 136 |
| `ZA/Hashlists/Lua/lua_s_hashes.txt` | 201 | 632 | 7 | 625 |

- 本轮恢复 65 个唯一 Hash、67 行映射；余下 3029 行。
- 现有 17797 行已命名记录全部通过重算。

## 逐项命中与来源

| Hash | 名称 | 方法 | 源模板／来源 | 位置（原行号） |
| --- | --- | --- | --- | --- |
| `0x09A82F76179381A5` | `main.util.tween.TweenPathType` | cross-hashlist | `existing verified Lua name` | `ZA/Hashlists/Lua/lua_e_hashes.txt:1` |
| `0x132D1C4DB569CA6C` | `main.env.ground_effect.control.CitySmokeControl` | cross-hashlist | `existing verified Lua name` | `SV/Hashlists/Lua/lua_c_hashes.txt:196` |
| `0x13A53B75C424EC5B` | `main.env.ground_effect.control.generator.CameraEffectGenerator` | cross-hashlist | `existing verified Lua name` | `SV/Hashlists/Lua/lua_c_hashes.txt:200` |
| `0x1B31858F892D5657` | `main.env.ground_effect.control.generator.EffectGeneratorBase` | cross-hashlist | `existing verified Lua name` | `SV/Hashlists/Lua/lua_c_hashes.txt:298` |
| `0x2007C313B2A115BE` | `SetWorldPosition` | prefix | `GetWorldPosition` | `ZA/Hashlists/Lua/lua_s_hashes.txt:108` |
| `0x24A0EE9DA3D20C83` | `main.env.ground_effect.control.SmokeFogControl` | cross-hashlist | `existing verified Lua name` | `SV/Hashlists/Lua/lua_c_hashes.txt:405` |
| `0x27CDAABC4F71901C` | `main.env.ground_effect.control.SnowSmokeControl` | cross-hashlist | `existing verified Lua name` | `SV/Hashlists/Lua/lua_c_hashes.txt:450` |
| `0x2A471B048BC98EF4` | `main.env.ground_effect.control.WindGrassControl` | cross-hashlist | `existing verified Lua name` | `SV/Hashlists/Lua/lua_c_hashes.txt:468` |
| `0x2C0CB2A899B13B3E` | `StepLoadCommonBg01` | numeric | `StepLoadCommonBg00` | `SV/Hashlists/Lua/lua_s_hashes.txt:1205` |
| `0x34151E5FC1F4190A` | `CHR_S_CHILDM_03` | numeric | `CHR_S_CHILDM_02` | `SV/Hashlists/Lua/lua_s_hashes.txt:1425` |
| `0x39CF03F7ED22975F` | `main.env.ground_effect.GroundEffectSmokeFogConfig` | cross-hashlist | `existing verified Lua name` | `SV/Hashlists/Lua/lua_c_hashes.txt:711` |
| `0x3BB535305A9A1B98` | `main.env.field_effect._FieldEffectSwitcher.Impl` | cross-hashlist | `existing verified Lua name` | `SV/Hashlists/Lua/lua_c_hashes.txt:732` |
| `0x3E2CCD54ED5431DE` | `main.env.ground_effect.control.generator.WindGrassEffectGenerator` | cross-hashlist | `existing verified Lua name` | `SV/Hashlists/Lua/lua_c_hashes.txt:762` |
| `0x4265B71F82A4D3BA` | `POKE_DERUBIRU10` | numeric | `POKE_DERUBIRU04` | `SV/Hashlists/Lua/lua_s_hashes.txt:1789` |
| `0x42691C1F82A7B530` | `POKE_DERUBIRU01` | numeric | `POKE_DERUBIRU04` | `SV/Hashlists/Lua/lua_s_hashes.txt:1790` |
| `0x42691E1F82A7B896` | `POKE_DERUBIRU03` | numeric | `POKE_DERUBIRU04` | `SV/Hashlists/Lua/lua_s_hashes.txt:1791` |
| `0x42691F1F82A7BA49` | `POKE_DERUBIRU02` | numeric | `POKE_DERUBIRU04` | `SV/Hashlists/Lua/lua_s_hashes.txt:1792` |
| `0x4269201F82A7BBFC` | `POKE_DERUBIRU05` | numeric | `POKE_DERUBIRU04` | `SV/Hashlists/Lua/lua_s_hashes.txt:1793` |
| `0x4269221F82A7BF62` | `POKE_DERUBIRU07` | numeric | `POKE_DERUBIRU04` | `SV/Hashlists/Lua/lua_s_hashes.txt:1795` |
| `0x4269231F82A7C115` | `POKE_DERUBIRU06` | numeric | `POKE_DERUBIRU04` | `SV/Hashlists/Lua/lua_s_hashes.txt:1796` |
| `0x4269241F82A7C2C8` | `POKE_DERUBIRU09` | numeric | `POKE_DERUBIRU04` | `SV/Hashlists/Lua/lua_s_hashes.txt:1797` |
| `0x4269251F82A7C47B` | `POKE_DERUBIRU08` | numeric | `POKE_DERUBIRU04` | `SV/Hashlists/Lua/lua_s_hashes.txt:1798` |
| `0x47FC22BE531BAE18` | `main.env.ground_effect.GroundEffectSnowSmokeConfig` | cross-hashlist | `existing verified Lua name` | `SV/Hashlists/Lua/lua_c_hashes.txt:885` |
| `0x4C726895FF1578F9` | `main.env.ground_effect.control.SandSmokeControl` | cross-hashlist | `existing verified Lua name` | `SV/Hashlists/Lua/lua_c_hashes.txt:965` |
| `0x4FD6A1AC26499C16` | `main.env.ground_effect.control.SmokeControlBase` | cross-hashlist | `existing verified Lua name` | `SV/Hashlists/Lua/lua_c_hashes.txt:1017` |
| `0x508E73DD9108DF26` | `onObjPokeModelScaleValueChanged` | case | `OnObjPokeModelScaleValueChanged` | `SV/Hashlists/Lua/lua_f_hashes.txt:2633` |
| `0x52DB4EAAAD6AC29B` | `SetScale` | prefix | `GetScale` | `ZA/Hashlists/Lua/lua_s_hashes.txt:262` |
| `0x5918BECABEC63037` | `main.system.coroutine.InternalState` | cross-hashlist | `existing verified Lua name` | `ZA/Hashlists/Lua/lua_e_hashes.txt:2` |
| `0x5E2B25200DF7A0A6` | `onObjAnimTimeScaleValueChanged` | case | `OnObjAnimTimeScaleValueChanged` | `SV/Hashlists/Lua/lua_f_hashes.txt:3061` |
| `0x64B8D3715D09DA74` | `main.env.ground_effect.GroundEffectWindGrassConfig` | cross-hashlist | `existing verified Lua name` | `SV/Hashlists/Lua/lua_c_hashes.txt:1329` |
| `0x6B775BB7672636C6` | `SCENE_STEP4` | numeric | `SCENE_STEP1` | `SV/Hashlists/Lua/lua_s_hashes.txt:2873` |
| `0x6B775DB767263A2C` | `SCENE_STEP2` | numeric | `SCENE_STEP1` | `SV/Hashlists/Lua/lua_s_hashes.txt:2874` |
| `0x6B775EB767263BDF` | `SCENE_STEP3` | numeric | `SCENE_STEP1` | `SV/Hashlists/Lua/lua_s_hashes.txt:2875` |
| `0x6F3E782FAF30D435` | `main.env.ground_effect.GroundEffectControlConfig` | cross-hashlist | `existing verified Lua name` | `SV/Hashlists/Lua/lua_c_hashes.txt:1435` |
| `0x7E4DD1EBE21A85CC` | `main.env.ground_effect.control.RaindropsControl` | cross-hashlist | `existing verified Lua name` | `SV/Hashlists/Lua/lua_c_hashes.txt:1629` |
| `0x81B0D46CE16C5B54` | `main.env.ground_effect.GroundEffectRainDropConfigs` | cross-hashlist | `existing verified Lua name` | `SV/Hashlists/Lua/lua_c_hashes.txt:1683` |
| `0x82E517173EC4A7A7` | `onMonsNoValueChanged` | case | `OnMonsNoValueChanged` | `SV/Hashlists/Lua/lua_f_hashes.txt:4244` |
| `0x84E01EC2D62ED7DB` | `onSexTypeValueChanged` | case | `OnSexTypeValueChanged` | `SV/Hashlists/Lua/lua_f_hashes.txt:4312` |
| `0x8BA3B4518741A17F` | `onEditPickupDataValueChanged` | case | `OnEditPickupDataValueChanged` | `SV/Hashlists/Lua/lua_f_hashes.txt:4530` |
| `0x8F7AE2638186E74F` | `main.env.ground_effect.control.generator.GroundEffectGenerator` | cross-hashlist | `existing verified Lua name` | `SV/Hashlists/Lua/lua_c_hashes.txt:1885` |
| `0x8FAB716DB9C67174` | `GetIsFinish` | prefix | `SetIsFinish` | `ZA/Hashlists/Lua/lua_f_hashes.txt:146` |
| `0x93A0ED567E185F6C` | `main.env.ground_effect.GroundEffectConfig` | cross-hashlist | `existing verified Lua name` | `SV/Hashlists/Lua/lua_c_hashes.txt:1936` |
| `0x967F1FA48596AFC5` | `main.env.ground_effect.GroundEffectGenerate` | cross-hashlist | `existing verified Lua name` | `SV/Hashlists/Lua/lua_c_hashes.txt:1967` |
| `0x969791696476F097` | `onObjOffsetPosXValueChanged` | case | `OnObjOffsetPosXValueChanged` | `SV/Hashlists/Lua/lua_f_hashes.txt:4903` |
| `0x9B3EF6CCB56B42E7` | `OnSkip` | case | `onSkip` | `ZA/Hashlists/Lua/lua_f_hashes.txt:163` |
| `0xA5EA85D96A5EBA15` | `main.util._PSTableAccessor.PSTableAccessor_Impl_` | cross-hashlist | `existing verified Lua name` | `SV/Hashlists/Lua/lua_c_hashes.txt:2131` |
| `0xAE477FE8B7B2F7D4` | `main.util.tween.TweenLoopType` | cross-hashlist | `existing verified Lua name` | `ZA/Hashlists/Lua/lua_e_hashes.txt:3` |
| `0xAEECD2EE6996A886` | `onIsDefultModeValueChanged` | case | `OnIsDefultModeValueChanged` | `SV/Hashlists/Lua/lua_f_hashes.txt:5741` |
| `0xAF981B669D917580` | `main.event.general.area_script.AreaEnter_a_sch_room03` | numeric | `main.event.general.area_script.AreaEnter_a_sch_room02` | `SV/Hashlists/Lua/lua_c_hashes.txt:2247` |
| `0xAF981D669D9178E6` | `main.event.general.area_script.AreaEnter_a_sch_room01` | numeric | `main.event.general.area_script.AreaEnter_a_sch_room02` | `SV/Hashlists/Lua/lua_c_hashes.txt:2249` |
| `0xB0F3F0CD7D326D7F` | `main.env.ground_effect.GroundEffectSandSmokeConfig` | cross-hashlist | `existing verified Lua name` | `SV/Hashlists/Lua/lua_c_hashes.txt:2263` |
| `0xB2DBA92A12482E2B` | `SetWorldRotation` | prefix | `GetWorldRotation` | `ZA/Hashlists/Lua/lua_s_hashes.txt:579` |
| `0xB335988BD2FD4FC6` | `onStateTypeValueChanged` | case | `OnStateTypeValueChanged` | `SV/Hashlists/Lua/lua_f_hashes.txt:5867` |
| `0xBB0ACA2D0182E28F` | `main.env.ground_effect.control.generator.IEffectGenerator` | cross-hashlist | `existing verified Lua name` | `SV/Hashlists/Lua/lua_c_hashes.txt:2352` |
| `0xC15087309BCBB48E` | `onFormNoValueChanged` | case | `OnFormNoValueChanged` | `SV/Hashlists/Lua/lua_f_hashes.txt:6339` |
| `0xC706B7C02933B741` | `main.env.ground_effect.control.GroundEffectControlBase` | cross-hashlist | `existing verified Lua name` | `SV/Hashlists/Lua/lua_c_hashes.txt:2500` |
| `0xD03C4F2A038DF506` | `main.env.ground_effect.control.generator.MidRangeBirdEffectGenerator` | cross-hashlist | `existing verified Lua name` | `SV/Hashlists/Lua/lua_c_hashes.txt:2611` |
| `0xD9491972A59BD708` | `SetTurn` | prefix | `GetTurn` | `ZA/Hashlists/Lua/lua_s_hashes.txt:709` |
| `0xEBE66699E5CF6917` | `IsSick` | prefix | `GetSick` | `ZA/Hashlists/Lua/lua_s_hashes.txt:755` |
| `0xEF683BA4C71BC8EC` | `OPEN_WAY_02` | numeric | `OPEN_WAY_01` | `SV/Hashlists/Lua/lua_s_hashes.txt:6182` |
| `0xF139E60DDE5354B2` | `main.env.ground_effect.control.MidRangeBirdNightControl` | cross-hashlist | `existing verified Lua name` | `SV/Hashlists/Lua/lua_c_hashes.txt:3110` |
| `0xF55159DC26CADF9E` | `main.env.ground_effect.control._GroundEffectControlType.GroundEffectControlTypeFunc_Impl_` | cross-hashlist | `existing verified Lua name` | `SV/Hashlists/Lua/lua_c_hashes.txt:3174` |
| `0xF667EB15F51B1829` | `IterativeLerpVec2` | numeric | `IterativeLerpVec3` | `SV/Hashlists/Lua/lua_s_hashes.txt:6374`, `ZA/Hashlists/Lua/lua_s_hashes.txt:797` |
| `0xF667ED15F51B1B8F` | `IterativeLerpVec4` | numeric | `IterativeLerpVec3` | `SV/Hashlists/Lua/lua_s_hashes.txt:6375`, `ZA/Hashlists/Lua/lua_s_hashes.txt:798` |
| `0xFCC532A987EEAC69` | `main.env.ground_effect.CameraEffectGenerate` | cross-hashlist | `existing verified Lua name` | `SV/Hashlists/Lua/lua_c_hashes.txt:3257` |

## 证据定义

- `cross-hashlist`：现有已知名称与空白 Hash 相同。
- `numeric`：从现有名字只替换一个数字区段（±8）。
- `prefix` / `case`：Get/Set/Is/get_/set_ 或 on/On 前缀替换。
- 只回填唯一命中；碰撞或无法匹配者保持未知，不猜测。
- 运行 `python scripts/lua_hash.py verify` 核验全部已命名行；下次运行 `recover` 仅统计当时剩余的未知行。
