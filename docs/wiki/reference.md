# 参数取值参考（枚举值 & 需要自己填的字段）

很多写操作的参数是游戏内部的**枚举**或**结构体**，SDK 没有内置常量。本页列出所有“必须自己填写、且无法从 SDK 直接获取”的取值：枚举的整数值、复杂对象的来源与结构。

> 枚举值来自客户端反编译，随游戏版本可能增删，最终以服务端为准；这里的值用于在没有现成数据来源时手填。

---

## 一、枚举型参数（填整数值）

### ContentType — 内容类别
用于 `sweep.request(content=)`、`content_save.discard(content_type=)`、`world_raid.lobby/boss_list(content_type=)`、`clear_deck.list(clear_deck_key=)`。

| 值 | 名称 | 值 | 名称 | 值 | 名称 |
| ---: | --- | ---: | --- | ---: | --- |
| 0 | None | 9 | TimeAttackDungeon | 17 | WorldRaid |
| 1 | CampaignMainStage | 10 | Raid | 18 | EliminateRaid |
| 2 | CampaignSubStage | 11 | Conquest | 19 | Chaser |
| 3 | WeekDungeon | 12 | EventContentStoryStage | 20 | FieldContentStage |
| 4 | EventContentMainStage | 13 | CampaignExtraStage | 21 | MultiFloorRaid |
| 5 | EventContentSubStage | 14 | StoryStrategyStage | 22 | MinigameDefense |
| 6 | CampaignTutorialStage | 15 | ScenarioMode | 23 | InteractiveWorldRaid |
| 7 | EventContentMainGroundStage | 16 | EventContent | 24 | PermanentRaid |
| 8 | SchoolDungeon | | | | |

> 扫主线普通关：`content=1`（CampaignMainStage）；扫日常副本：`content=3`（WeekDungeon）。

### StageDifficulty — 关卡难度（主线/占领）
用于 `campaign.chapter_clear_reward(stage_difficulty=)`、`conquest.manage_base/upgrade_base/normalize_echelon/receive_calculate_rewards(difficulty=)`。

`0 None`、`1 Normal`、`2 Hard`、`3 VeryHard`、`4 VeryHard_Ex`

### Difficulty — 总力战难度（注意与上面不同！）
用于 `raid.list(raid_difficulty=)`。

`0 Normal`、`1 Hard`、`2 VeryHard`、`3 Hardcore`、`4 Extreme`、`5 Insane`、`6 Torment`、`7 Lunatic`

> ⚠️ `Difficulty` 的 `Normal=0`，而 `StageDifficulty` 的 `Normal=1`，两套枚举不要混用。

### ShopCategoryType — 商店分类
用于 `shop.refresh(shop_category_type=)`、`shop.list(category_list=)`、`event_content.shop_refresh/shop_list`。

| 值 | 名称 | 值 | 名称 | 值 | 名称 |
| ---: | --- | ---: | --- | ---: | --- |
| 0 | General | 14 | EventContent_1 | 28 | SchoolDungeonTicket |
| 1 | SecretStone | 15 | EventContent_2 | 29 | AcademyTicket |
| 2 | Raid | 16 | EventContent_3 | 30 | Special |
| 3 | Gold | 17 | EventContent_4 | 31 | Care |
| 4 | Ap | 18 | _Obsolete | 32 | BeforehandGacha |
| 5 | PickupGacha | 19 | LimitedGacha | 33 | EliminateRaid |
| 6 | NormalGacha | 20 | MasterCoin | 34 | GlobalSpecialGacha |
| 7 | PointGacha | 21 | SecretStoneGrowth | 35 | SelectPickupGacha |
| 8 | EventGacha | 22 | TicketGacha | 36 | GemDaily |
| 9 | ArenaTicket | 23 | DirectPayGacha | 37 | GemWeekly |
| 10 | Arena | 24 | FesGacha | 38 | CafeSummonTicket |
| 11 | TutoGacha | 25 | TimeAttack | 39 | SelectPickupFesGacha |
| 12 | RecruitSellection | 26 | Chaser | 40 | SelectPickupLimitedGacha |
| 13 | EventContent_0 | 27 | ChaserTicket | | |

### CafePresetType
用于 `cafe.apply_preset / clear_preset / rename_preset / preset_detail`。 `0 None`、`1 Preset`、`2 CopyPreset`

### ClanJoinOption
用于 `clan.create / search / setting`。 `0 Free`、`1 Permission`、`2 All`

### ClanSocialGrade — 社团职级
用于 `clan.confer(confering_grade=)`。 `1 President`、`2 Manager`、`3 Member`、`8 VicePredisident`（`4 Applicant`/`5 Refused`/`6 Kicked`/`7 Quit` 为状态，非可授予职级）

### EchelonType — 编队类型
用于 `clan.set_assist / all_assist_list(echelon_type=)`。常用：`1 Adventure`、`2 Raid`、`6 Scenario`、`16 WorldRaid`、`17 Conquest`、`23 Field`、`24 MultiFloorRaid`、`26 PermanentRaid`（完整 0–26：Adventure/Raid/ArenaAttack/ArenaDefence/WeekDungeonChaserA/Scenario/WeekDungeonBlood/WeekDungeonChaserB/WeekDungeonChaserC/WeekDungeonFindGift/EventContent/SchoolDungeonA/B/C/TimeAttack/WorldRaid/Conquest/ConquestManage/StoryStrategyStage/EliminateRaid01/02/03/Field/MultiFloorRaid/MinigameDefense/PermanentRaid）

### EchelonExtensionType
用于 `echelon.preset_list / preset_group_rename`。 `0 Base`、`1 Extension`

### CraftNodeTier
用于 `craft.update_node_level(craft_node_type=)`。 `0 Base`、`1 Node01`、`2 Node02`、`3 Node03`、`4 Max`

### SkillSlot — 技能槽
用于 `character.update_skill_level(skill_slot=)`。共 0–109，按组分布：

- 普通攻击 `NormalAttack01..10` = 1–10
- EX 技能 `ExSkill01..10` = 11–20
- 被动 `Passive01..10` = 21–30
- 额外被动 `ExtraPassive01..10` = 31–40
- 辅助 `Support01..10` = 41–50
- 装备/公共/其它见 dump（51+）

> 升 EX 技能一般用 `skill_slot=11`（ExSkill01），普通技能 21（Passive01）等，按该角色技能页对应槽位。

### MissionCategory — 任务分类
用于 `mission.multiple_reward`、`battle_pass.mission_multiple_reward`、`mini_game.mission_multiple_reward`。

`0 Challenge`、`1 Daily`、`2 Weekly`、`3 Achievement`、`4 GuideMission`、`5 All`、`6 MiniGameScore`、`7 MiniGameEvent`、`8 EventAchievement`、`9 DailySudden`、`10 DailyFixed`、`11 EventFixed`

> ✅ `mission.multiple_reward` 可以直接传字符串名（如 `"daily"`、`"weekly"`、`"achievement"`），SDK 内置映射，无需记数字。

### ParcelType — 奖励/物品类别
用于 `item.auto_synth`、`sweep.set_multi_sweep_preset` 的 `ParcelKeyPair.Type`，以及 `SelectTicketReplaceInfo.MaterialType`。常用：`1 Character`、`2 Currency`、`3 Equipment`、`4 Item`、`13 Furniture`、`16 Recipe`、`17 CharacterWeapon`、`19 CharacterGear`、`21 Emblem`、`22 Sticker`、`23 Costume`（完整 0–31 见 dump）

### 筛选 / 排序类（可选，默认 None 可省）
| 枚举 | 用于 | 值 |
| --- | --- | --- |
| `RaidRoomSortOption` | `raid.list(raid_room_sort_option=)` | 0 HPHigh、1 HPLow、2 RemainTimeHigh、3 RemainTimeLow |
| `RankingSearchType` | `raid/eliminate_raid.opponent_list(search_type=)` | 0 None、1 Rank、2 Score |
| `MailSortingRule` | `mail.list / list_semi_permanent(mail_sorting_rule=)` | 0 ReceiptDate、1 ExpireDate |
| `FriendSearchLevelOption` | `friend.search(level_option=)` | 0 Recommend、1 All、2 Level1To30 … 9 Level91To100 |

---

## 二、复杂对象 / 字典 / 列表参数

### 有读接口可作来源（读出来、改了再传回）
| 参数 | 方法 | 从哪读 |
| --- | --- | --- |
| `SkipHistoryDB` | `sweep.save_skip_history` | `sweep.skip_history_list()` |
| `EchelonDB` / `EchelonPresetDB` | `echelon.save` / `echelon.preset_save` | `echelon.list()`（取一条改字段再传） |
| `OpenConditionDB`（`condition_db`） | `open_condition.set` | `open_condition.list()` |
| `CraftPresetSlotDB` | `craft.save_preset` | `craft.list()` |
| `MultiSweepParameters` | `sweep.multi_sweep` | 见 [扫荡页](player/sweep.md)（或 `sweep.preset_list()`） |
| `Dictionary<Int64,…>` 里的 ID 键 | `character.favor_growth`(`consume_item_db_ids_and_counts`) / `set_favorites`(`activate_by_server_ids`) / `weapon_exp_growth`(`consume_unique_id_and_counts`) | 道具/角色 ServerId 从 `item.list()` / `character.list()` 取；值是数量(int)或布尔 |

### 须按服务端结构构造（无现成来源）—— 结构来自反编译

**`ConsumeRequestDB`**（`character.exp_growth`、`equipment.level_up`、`craft.update_node_level/shifting_begin_process`、`cafe.rank_up/give_gift`）— 「消耗什么」：
```python
consume_request_db = {
    "ConsumeItemServerIdAndCounts": {item_server_id: count, ...},        # 道具 ServerId(来自 item.list) -> 数量
    "ConsumeEquipmentServerIdAndCounts": {equipment_server_id: count},   # 装备(来自 equipment.list)
    "ConsumeFurnitureServerIdAndCounts": {furniture_server_id: count},   # 家具
}
```

**`ParcelKeyPair`**（`item.auto_synth.target_parcels`、`sweep.set_multi_sweep_preset.parcel_ids`）：
```python
{"Type": ParcelType值(如 4=Item), "Id": 物品配置 Id}
```

**`SelectTicketReplaceInfo`**（`character.update_skill_level/potential_growth`、`character_gear.tier_up`、`equipment.tier_up` 的 `replace_infos`，仅在用自选券替代材料时填，普通成长留空）：
```python
{"MaterialType": ParcelType值, "MaterialId": 材料Id, "TicketItemId": 自选券Id, "Amount": 数量}
```

**批量成长 DB**（按需，多为高级批量接口）：
- `EquipmentBatchGrowthRequestDB`：`{TargetServerId, ConsumeRequestDBs:[…], AfterTier, AfterLevel, AfterExp, ReplaceInfos:[…]}`
- `GearTierUpRequestDB`：`{TargetServerId, AfterTier, ReplaceInfos:[…]}`
- `SkillLevelBatchGrowthRequestDB`：`{SkillSlot, Level, ReplaceInfos:[…]}`
- `Dictionary<SkillSlot,Int32>`（`world_raid.update_carrier_skill.carrier_skills`）：`{SkillSlot值: 等级}`
- `ClanAssistUseInfo`（`clan.all_assist_list`、`echelon.save`）：`{CharacterDBId, EchelonType, SlotNumber, CombatStyleIndex, …}`

### `option.save` 的 `OptionDB` — 来自登录响应
`OptionDB` 是账号偏好设置，**随登录 `Account_Auth` 响应顶层下发**（不是独立读协议——只有 `Option_Save`）。SDK 已在登录时捕获它，用 `client.option.current()` 取当前值的副本，改一项再 `save`：

```python
opt = client.option.current()              # {"ArenaIsAnonymous":…, "CafeAllowCopy":…, "MainScenarioForceEnterSeriesId":…} 或 None
opt["ArenaIsAnonymous"] = True
await client.option.save(option_db=opt, confirm=True)
```

字段：`ArenaIsAnonymous: bool`（竞技场匿名）、`CafeAllowCopy: CafeAllowCopyPreset`（`All=0`/`None=1`/`CircleAndFriend=10`/`CircleOnly=11`/`FriendOnly=12`）、`MainScenarioForceEnterSeriesId: int`（主线强制进入系列 ID）。

`current()` 返回 `None` 表示**没有可读的非默认设置**——全默认设置的账号，BA 的 FlatBuffer 会省略默认字段、OptionDB 解码成空对象。这种情况直接构造只含你要改的字段的 dict 传给 `save` 即可：

```python
await client.option.save(option_db={"ArenaIsAnonymous": True}, confirm=True)
```

---

## 三、通用原则
- **ID 类参数**（StageUniqueId、各 ServerId/DBId、MissionUniqueId、ShopUniqueId、EventContentId…）一律来自对应读接口的返回（如 `campaign.list()`、`item.list()`、`mission.list()`、`event_content.permanent_list()`），不要手填。
- **枚举类参数**用上表的整数值；优先用有现成来源的路径（如扫荡用 `preset_list()` 自带组合）。
- **复杂对象**优先"读出来改了再传"（如 `OptionDB` 用 `client.option.current()`、`EchelonDB` 用 `echelon.list()`）；确实没有读来源的才手工构造。
