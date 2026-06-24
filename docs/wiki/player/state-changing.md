# 显式确认变更（confirm）

本页汇总会改变账号状态的操作：领取奖励、设置/偏好、养成/消耗、破坏性/社团管理，以及好友申请、制造领取、主线/剧情关卡确认等带前置校验的确认操作。

- 能做：在显式确认后发出对应的状态变更请求。
- 不做：方法不会自动执行；必须显式传 `confirm=True`，否则抛 `UnsafeOperationError` 且不发包。

公平边界见[总览](../README.md#公平边界)。

> 需要自行填写的参数——枚举（`StageDifficulty`/`ShopCategoryType`/`EchelonType`/`SkillSlot`/`ClanJoinOption`…）的整数值，以及 `ConsumeRequestDB`/`OptionDB`/`ParcelKeyPair` 等复杂对象的结构与来源——均列在 [参数取值参考](../reference.md)。

## 总览

按操作性质分两类：

- **批量 confirm 守卫（C1–C4）**：以 `confirm=True` 作为唯一安全闸。下面按风险分四档列出方法清单，方法名以各 `service.py` 当前代码为准。
  - C1 领取奖励 · C2 设置/偏好（不消耗资源）· C3 养成/消耗（消耗石/材料/次数）· C4 破坏性/社团（不可逆）
- **带前置校验的确认操作**：除 `confirm=True` 外，默认 `validate=True` 会先读取当前页面状态做前置校验；只有调用方已从游戏流程确认前置条件时才应传 `validate=False`。这类有独立小节：[好友申请](#好友申请)、[制造完成](#制造完成)、[主线关卡确认和剧情跳过](#主线关卡确认和剧情跳过)、[账号等级奖励领取](#账号等级奖励领取)、[头像框和-emblem](#头像框和-emblem)。

通用约定：

- 字段按服务端协议透传——标量自动转换，复杂对象/列表（如 `EchelonDB` / `OptionDB` / `ConditionDB` / 家具布局）以 `dict` / `list` 原样传入。
- 活动/赛季/关卡/队伍/角色等 ID 一律来自当前账号可见数据，不要手填。
- 返回值：源码里带 `format_*` 的返回整理后的 `dict`（业务字段 + 部分 `count` + `extra`）；其余直接返回服务端原始负载。
- 逐协议接入状态见仓库根 [`docs/protocols.md`](../../protocols.md)。

## C1 领取奖励（需 confirm=True）

领取已完成奖励的接口，覆盖总力战系、通行证、每日记录、小游戏任务、占领结算等。全部 `confirm=True` 必填；有"可领状态"可查的（通行证、总力战、占领）默认 `validate=True` 会先查状态，无可领项时抛 `UnsafeOperationError` 且不发领取请求。

| SDK 入口 | 领什么 | 协议 | 前置校验 |
| --- | --- | --- | --- |
| `client.battle_pass.receive_reward(bp_id, confirm=True)` | 通行证奖励 | `BattlePass_ReceiveReward` | `check().has_not_receive_reward` |
| `client.battle_pass.mission_single_reward(bp_id, mission_id, confirm=True)` | 通行证单项任务奖励 | `BattlePass_MissionSingleReward` | `check().has_complete_mission` |
| `client.battle_pass.mission_multiple_reward(bp_id, category, confirm=True)` | 通行证批量任务奖励 | `BattlePass_MissionMultipleReward` | `check().has_complete_mission` |
| `client.raid.reward(raid_server_id, confirm=True)` | 总力战房间奖励 | `Raid_Reward` | `complete_list().receive_reward_ids` |
| `client.raid.reward_all(confirm=True)` | 一键领总力战奖励 | `Raid_RewardAll` | `complete_list().receive_reward_ids` |
| `client.raid.season_reward(confirm=True)` / `ranking_reward(confirm=True)` | 赛季/排行奖励 | `Raid_SeasonReward` / `Raid_RankingReward` | 仅 confirm |
| `client.eliminate_raid.season_reward / ranking_reward / limited_reward(confirm=True)` | 大决战赛季/排行/限时奖励 | `EliminateRaid_*Reward` | 仅 confirm |
| `client.multi_floor_raid.receive_reward(reward_difficulty=, season_id=, confirm=True)` | 多层总力战奖励 | `MultiFloorRaid_ReceiveReward` | 仅 confirm |
| `client.world_raid.receive_reward(phase_id=, season_id=, confirm=True)` | 世界 Raid 奖励 | `WorldRaid_ReceiveReward` | 仅 confirm |
| `client.daily_record.reward(daily_record_id, confirm=True)` | 每日记录奖励 | `DailyRecord_Reward` | 仅 confirm |
| `client.mini_game.mission_reward(event_content_id=, mission_unique_id=, progress_server_id=, confirm=True)` | 小游戏任务奖励 | `MiniGame_MissionReward` | 仅 confirm |
| `client.mini_game.mission_multiple_reward(event_content_id=, mission_category=, confirm=True)` | 小游戏批量任务奖励 | `MiniGame_MissionMultipleReward` | 仅 confirm |
| `client.conquest.receive_calculate_rewards(event_content_id=, difficulty=, step=, confirm=True)` | 占领战结算奖励 | `Conquest_ReceiveCalculateRewards` | `check().CanReceiveCalculateReward` |
| `client.campaign.chapter_clear_reward(campaign_chapter_unique_id=, stage_difficulty=, confirm=True)` | 主线章节通关奖励 | `Campaign_ChapterClearReward` | 仅 confirm |
| `client.event_content.receive_stage_total_reward(event_content_id, confirm=True)` | 活动关卡累计奖励 | `EventContent_ReceiveStageTotalReward` | 仅 confirm |
| `client.event_content.dice_race_lap_reward(event_content_id, confirm=True)` | DiceRace 圈数奖励 | `EventContent_DiceRaceLapReward` | 仅 confirm |

> "仅 confirm" 表示当前没有现成的"可领状态"查询用作前置校验，安全完全依赖 `confirm=True`——调用方需自行从游戏流程确认确有可领项再传 `confirm=True`。
> live：已用真实账号验证这批方法的 `confirm` 守卫（无 `confirm` 一律抛 `UnsafeOperationError`、不发请求）；通行证 `check(1)`、`raid.complete_list()` 的前置校验源已确认可读取真实状态。**未对真实账号触发任何领取**（当前账号这些类别均无可领项）。
> 未接入的边角：`Event_UseCoupon`（需外部兑换码）、`Event_RewardIncrease`（语义不明确）、`Account_LinkReward` / `Account_RequestBirthdayMail`（账号特殊/需输入），留待后续。

## C2 设置/偏好（需 confirm=True）

改"展示 / 预设 / 历史 / 标志"等状态，**不消耗石/材料**。全部 `confirm=True` 必填（confirm 即守卫，无前置查询）。复杂字段（如 `EchelonDB` / `OptionDB` / `ConditionDB` / 家具布局）以 `dict` / `list` 原样传入。

- `client.account.*`: `set_represent_character_and_comment`, `call_name`, `dismiss_repurchasable_popup`, `set_check_adult_agree`, `set_tutorial`
- `client.character.*`: `set_favorites`, `set_costume`
- `client.echelon.*`: `save`, `preset_save`, `preset_group_rename`
- `client.memory_lobby.*`: `set_main`, `update_lobby_mode`, `interact`
- `client.scenario.*`: `group_history_update`, `skip`, `select`, `account_student_change`, `lobby_student_change`, `special_lobby_change`, `enter`
- `client.friend.*`: `set_id_card`
- `client.clan.*`: `setting`, `set_assist`
- `client.cafe.*`: `ack`, `rename_preset`, `clear_preset`, `update_preset_furniture`, `apply_preset`, `apply_template`, `open`, `travel`, `update_copy_preset_furniture`
- `client.option.*`: `save`
- `client.sweep.*`: `set_multi_sweep_preset`, `set_multi_sweep_preset_name`, `save_skip_history`
- `client.content_save.*`: `discard`
- `client.open_condition.*`: `set`
- `client.field.*`: `scene_changed`, `end_date`
- `client.world_raid.*`: `update_carrier_skill`

## C3 资源消耗/养成（需 confirm=True）

会**消耗青辉石 / 材料 / 货币 / 次数**，或永久改变角色/装备/物品状态。全部 `confirm=True` 必填；SDK 不做余额/库存预检，调用前请自行确认目标与资源。

- `client.character.*`: `transcendence`, `exp_growth`, `favor_growth`, `update_skill_level`, `unlock_weapon`, `weapon_exp_growth`, `weapon_transcendence`, `batch_skill_level_update`, `potential_growth`
- `client.character_gear.*`: `unlock`, `tier_up`
- `client.equipment.*`: `sell`, `equip`, `level_up`, `tier_up`, `lock`, `batch_growth`
- `client.item.*`: `sell`, `consume`, `lock`, `bulk_consume`, `select_ticket`, `auto_synth`
- `client.craft.*`: `select_node`, `update_node_level`, `begin_process`, `complete_process`, `reward`, `shifting_begin_process`, `shifting_complete_process`, `shifting_reward`, `auto_begin_process`, `reward_all`, `shifting_reward_all`, `save_preset`, `save_preset_name`
- `client.recipe.*`: `craft`
- `client.shop.*`: `buy_merchandise`, `refresh`, `buy_refresh_merchandise`, `buy_eligma`（用神名精髓 Eligma 兑换，非抽卡）
- `client.battle_pass.*`: `buy_level`
- `client.event_content.*`: `purchase_play_count_hard_stage`, `shop_refresh`, `shop_buy_merchandise`, `shop_buy_refresh_merchandise`, `scenario_group_history_update`, `location_attend_schedule`
- `client.conquest.*`: `manage_base`, `upgrade_base`, `take_event_object`, `normalize_echelon`
- `client.campaign.*`: `purchase_play_count_hard_stage`, `confirm_tutorial_stage`
- `client.cafe.*`: `rank_up`, `give_gift`, `summon_character`, `summon_character_ticket_use`
- `client.sticker.*`: `use_sticker`
- `client.mini_game.*`: `dream_maker_attend_schedule`
- 扫荡（消耗扫荡券/次数，对**已通关**关卡/房间）: `client.raid.sweep(unique_id=, sweep_count=)`、`client.eliminate_raid.sweep(unique_id=, sweep_count=)`、`client.time_attack_dungeon.sweep(sweep_count=)`、`client.mini_game.shooting_sweep(event_content_id=, unique_id=, sweep_count=)`、`client.mini_game.ccg_sweep(event_content_id=, sweep_count=)`、`client.mini_game.table_board_sweep(event_content_id=, preserve_item_effect_unique_ids=)`；通用扫荡（主线/悬赏/交流会/活动）见[扫荡页](sweep.md)的 `sweep.request`/`multi_sweep`。各形参从哪来怎么填见[扫荡页](sweep.md)

## C4 破坏性/社团管理（需 confirm=True）

**不可逆**操作，请格外谨慎。全部 `confirm=True` 必填。

- `client.clan.*`: `create`, `join`, `quit`, `permit`, `kick`, `confer`, `dismiss`, `auto_join`, `cancel_apply`
- `client.friend.*`: `remove`, `block`, `unblock`

> C2/C3/C4 全部方法统一 `confirm=True` 守卫：不传则抛 `UnsafeOperationError` 且不发包。
> live 已验证 `confirm=True` 路径端到端：`memory_lobby.interact`、`account.set_check_adult_agree` 实发成功；`sticker.use_sticker`（47000 StickerDataNotFound）、`recipe.craft`（11000 RecipeCraftNoData）、`shop.refresh`（10005 ShopInfoNotFound）等以无效 ID 探测被对应协议处理器正确受理并按语义拒绝，证明协议路由正确（未对账号造成实质改动）。
> 回归测试 `tests/test_state_change_c234.py` 固化这些方法的 confirm 守卫与 RequestClass 发送。

## 好友申请

对应游戏里好友页的发送申请、接受申请、拒绝申请、取消自己发出的申请。这四个方法默认 `validate=True`，会先调用 `friend.list()` 校验当前好友状态。

| SDK 入口 | 游戏里对应 | 前置（`validate=True`） | 协议 |
| --- | --- | --- | --- |
| `client.friend.send_request(target_account_id, confirm=True, validate=True)` | 申请好友 | 目标不在好友/已发送/已收到/屏蔽列表 | `Friend_SendFriendRequest` |
| `client.friend.accept_request(target_account_id, confirm=True, validate=True)` | 接受收到的申请 | 目标在 `received_requests` 中 | `Friend_AcceptFriendRequest` |
| `client.friend.decline_request(target_account_id, confirm=True, validate=True)` | 拒绝收到的申请 | 目标在 `received_requests` 中 | `Friend_DeclineFriendRequest` |
| `client.friend.cancel_request(target_account_id, confirm=True, validate=True)` | 取消已发出的申请 | 目标在 `sent_requests` 中 | `Friend_CancelFriendRequest` |

返回整理后的 `dict`，形状沿用 `friend.list()`（好友/收发申请/屏蔽列表 + 各自 `count` + `extra`）。live 均已通过。

```python
search = await client.friend.search(friend_code="ABCDEF")
target_account_id = search["friends"][0]["AccountId"]
await client.friend.send_request(target_account_id, confirm=True)

state = await client.friend.list()
if state["received_requests"]:
    await client.friend.accept_request(state["received_requests"][0]["AccountId"], confirm=True)
```

## 制造完成

对应游戏里制造页的一键领取已完成结果，会改变物品状态。默认 `validate=True` 会先调用 `craft.list()` 检查是否存在可处理的制造记录。

| SDK 入口 | 游戏里对应 | 前置（`validate=True`） | 协议 |
| --- | --- | --- | --- |
| `client.craft.complete_process_all(confirm=True, validate=True)` | 领取全部普通制造结果 | `craft.list()["craft_infos"]` 有记录 | `Craft_CompleteProcessAll` |
| `client.craft.shifting_complete_process_all(confirm=True, validate=True)` | 领取全部转化制造结果 | `craft.list()["shifting_craft_infos"]` 有记录 | `Craft_ShiftingCompleteProcessAll` |

两者均返回整理后的 `dict`（制造信息等业务字段 + `count` + `extra`）。live 已封装；本轮账号无候选，因此未发送真实领取请求。

```python
craft = await client.craft.list()
if craft["craft_infos"]:
    await client.craft.complete_process_all(confirm=True)
if craft["shifting_craft_infos"]:
    await client.craft.shifting_complete_process_all(confirm=True)
```

## 主线关卡确认和剧情跳过

对应主线/剧情流程里的"确认关卡结果"或"跳过剧情"。它们需要活跃关卡流程中的 `StageUniqueId` 和服务端 SaveData 上下文，**不能从历史列表任取一个 ID 发送**。

`Campaign_List.stage_history` 和 `Scenario_List.scenario_history` 是历史状态，不是可确认关卡的前置条件。live 验证中，直接拿历史关卡 ID 调用 `Campaign_ConfirmMainStage` 会返回 `ErrorCode=6003 CampaignStageInvalidSaveData`。因此这三项默认 `validate=True` 会**本地拦截**，只有调用方已从活跃关卡流程拿到对应 SaveData 和 `StageUniqueId` 时，才应显式传 `validate=False` 发送请求。

| SDK 入口 | 游戏里对应 | 协议 |
| --- | --- | --- |
| `client.campaign.confirm_main_stage(stage_unique_id, confirm=True, validate=False)` | 主线关卡结束后确认结果 | `Campaign_ConfirmMainStage` |
| `client.scenario.confirm_main_stage(stage_unique_id, confirm=True, validate=False)` | 剧情主线关卡结束后确认结果 | `Scenario_ConfirmMainStage` |
| `client.scenario.skip_main_stage(stage_unique_id, confirm=True, validate=False)` | 剧情主线流程里点击跳过 | `Scenario_SkipMainStage` |

三者均返回整理后的 `dict`（含 `parcel_result` / `save_data` 等业务字段 + `extra`，剧情侧另含 scenario 相关字段）。`stage_unique_id` 必须是活跃关卡流程中的 `StageUniqueId`。

```python
result = await client.campaign.confirm_main_stage(
    stage_unique_id,
    confirm=True,
    validate=False,  # 仅在确认已有活跃 SaveData 后才传
)
```

## 账号等级奖励领取

对应账号成长里"等级奖励"页面的领取按钮，会改账号状态。默认 `validate=True` 会先读取等级奖励状态，无可领项时拒绝发送。

| SDK 入口 | 游戏里对应 | 前置（`validate=True`） | 协议 |
| --- | --- | --- | --- |
| `client.account.receive_level_reward(confirm=True, validate=True)` | 账号等级奖励页的"领取" | `check_level_reward()["account_level_reward_ids"]` 非空 | `Account_ReceiveAccountLevelReward` |

返回整理后的 `dict`（已领取的等级奖励 ID 等业务字段 + `count` + `extra`）。配套只读：`client.account.check_level_reward()` 看当前可领状态。live 已封装；当前账号 `check_level_reward()` 返回空列表，因此未发领取请求。

```python
state = await client.account.check_level_reward()
if state["account_level_reward_ids"]:
    await client.account.receive_level_reward(confirm=True)
```

## 头像框和 Emblem

对应个人资料里的头像框/Emblem 页面。`emblem_acquire()` 把已解锁头像框领取出来，`emblem_attach()` 把可用头像框装配到资料页。默认 `validate=True` 会先读 `emblem_list()` 校验 ID。

| SDK 入口 | 游戏里对应 | 前置（`validate=True`） | 协议 |
| --- | --- | --- | --- |
| `client.attachment.emblem_acquire(unique_ids, confirm=True, validate=True)` | 头像框页的"获取"/领取 | `unique_ids` 来自当前 `emblem_list()` | `Attachment_EmblemAcquire` |
| `client.attachment.emblem_attach(unique_id, confirm=True, validate=True)` | 头像框页的"装配" | `unique_id` 来自当前 `emblem_list()` | `Attachment_EmblemAttach` |

`emblem_acquire` 返回整理后的 `dict`（emblems 列表 + `count` + `extra`）；`emblem_attach` 返回整理后的 `dict`（装配后的 attachment 业务字段 + `extra`）。配套只读：`client.attachment.emblem_list()`。live 已封装；当前账号 `emblem_attach()` 已成功返回 `attachment` 数据。

```python
state = await client.attachment.emblem_list()
unique_id = state["emblems"][0]["UniqueId"]
await client.attachment.emblem_acquire([unique_id], confirm=True)
await client.attachment.emblem_attach(unique_id, confirm=True)
```
