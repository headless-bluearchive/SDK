# 好友、社团、活动、Raid、小游戏等页面数据

本页按游戏里能看到的页面来整理 SDK 方法：好友页、社团页、活动页、活动商店、总力战/大决战排行、制约解除决战、WorldRaid、活动小游戏、装备仓库、道具仓库、编队、记忆大厅等。这里的内容都属于“打开页面看状态”，不会领奖、购买、进入战斗、提交成绩、抽卡、发送好友申请、加入社团或选择票券。

调用前需要先完成 `client.login(...)`，或用已持久化的 `session/profile` 调用 `client.restore_session(...)`。示例只展示方法形态，不包含账号凭据、session、profile 或 token 输出。

## 游戏功能速查

| 游戏里看到的功能 | SDK 入口 |
| --- | --- |
| 头像框/附件/Emblem | `client.attachment.get()` / `client.attachment.emblem_list()` |
| 编队、装备、道具、爱用品 | `client.echelon.list()` / `client.equipment.list()` / `client.item.list()` / `client.character_gear.list()` |
| 记忆大厅、剧情回放、学院交流会 | `client.memory_lobby.list()` / `client.scenario.list()` / `client.school_dungeon.list()` |
| 活动列表、永久化活动、活动关卡、活动商店 | `client.event.list()` / `client.event_content.*` |
| 招募页面状态，不抽卡 | `client.shop.gacha_recruit_list()` / `client.shop.beforehand_gacha_get()` / `client.shop.pickup_selection_gacha_get()` |
| 好友列表、好友搜索、玩家名片 | `client.friend.*` |
| 社团大厅、社团搜索、成员、助战 | `client.clan.*` |
| 总力战/大决战/制约解除决战/WorldRaid | `client.raid.*` / `client.eliminate_raid.*` / `client.permanent_raid.*` / `client.world_raid.*` |
| 活动小游戏大厅和任务 | `client.mini_game.*` |
| 战斗通行证、制造、公告、协议锁 | `client.battle_pass.*` / `client.craft.list()` / `client.management.*` |

## 阅读方式

每个小节先说明它对应游戏里的哪个页面或功能，再列出 SDK 方法、参数和返回结构。所有方法都是异步方法，返回值统一是 `dict`。列表里的单条记录通常仍是服务端原始 DB dict，SDK 不会把每个嵌套对象再拆成复杂模型。

返回结构通常长这样：

```python
{
    "业务字段": ...,
    "count": 0,          # 列表类常见
    "extra": {},         # 未显式整理的顶层返回字段
}
```

`extra` 不是错误。服务端经常会附带 `ServerTime`、版本、活动期信息等额外字段，SDK 会保留它们但不把它们当稳定 API 承诺。

参数说明里写成 `int` 的字段会经过 SDK 的整数校验；写成 `list[int]` 的字段会逐项转成整数。涉及活动、赛季、招募、社团、好友的 ID 必须来自当前账号能看到的页面数据或游戏数据配置，不能随便硬填。

## 老师资料、仓库和编队页面

这一组对应游戏里的账号基础状态、头像框/Emblem、装备仓库、道具仓库、爱用品、编队、记忆大厅、剧情回放和学院交流会页面。

### `client.account.tutorial()`

对应新号开局教程流程。读取账号已经完成或触发过的教程步骤，用来判断外部界面是否还需要提示用户完成教程。

| 项 | 内容 |
| --- | --- |
| 协议 | `Account_GetTutorial` |
| 参数 | 无 |
| 返回 | `tutorial_ids`, `count`, `extra` |
| live | 已通过 |

```python
result = await client.account.tutorial()
print(result["tutorial_ids"], result["count"])
```

返回示例：

```python
{
    "tutorial_ids": [100, 101],
    "count": 2,
    "extra": {},
}
```

### `client.attachment.get()`

对应个人资料里的头像框、称号附件等装饰挂载状态。

| 项 | 内容 |
| --- | --- |
| 协议 | `Attachment_Get` |
| 参数 | 无 |
| 返回 | `account_attachment`, `extra` |
| live | 已通过 |

```python
attachment = await client.attachment.get()
```

### `client.attachment.emblem_list()`

对应个人资料/成就展示里可选择的 Emblem 列表。

| 项 | 内容 |
| --- | --- |
| 协议 | `Attachment_EmblemList` |
| 参数 | 无 |
| 返回 | `emblems`, `count`, `extra` |
| live | 已通过 |

```python
emblems = await client.attachment.emblem_list()
print(emblems["count"])
```

### `client.character_gear.list()`

对应学生详情里的爱用品页面。返回账号已经拥有和培养过的角色装备/爱用品记录。

| 项 | 内容 |
| --- | --- |
| 协议 | `CharacterGear_List` |
| 参数 | 无 |
| 返回 | `character_gears`, `count`, `extra` |
| live | 已通过 |

```python
gears = await client.character_gear.list()
```

### `client.equipment.list()`

对应装备仓库。返回账号持有的装备道具记录。

| 项 | 内容 |
| --- | --- |
| 协议 | `Equipment_List` |
| 参数 | 无 |
| 返回 | `equipment_items`, `count`, `extra` |
| live | 已通过 |

```python
equipment = await client.equipment.list()
```

### `client.item.list()`

对应道具仓库。一次返回普通物品、限时物品、装备物品和爱用品数据，适合做仓库页初始化。

| 项 | 内容 |
| --- | --- |
| 协议 | `Item_List` |
| 参数 | 无 |
| 返回 | `items`, `expiry_items`, `equipment_items`, `character_gears`, `count`, `expiry_count`, `equipment_count`, `character_gear_count`, `extra` |
| live | 已通过 |

```python
items = await client.item.list()
print(items["count"], items["expiry_count"])
```

### `client.echelon.list()`

对应编队页面和预设编队页面。返回当前编队以及预设编队数据。

| 项 | 内容 |
| --- | --- |
| 协议 | `Echelon_List` |
| 参数 | 无 |
| 返回 | `echelons`, `presets`, `count`, `preset_count`, `extra` |
| live | 已通过 |

```python
echelons = await client.echelon.list()
```

### `client.memory_lobby.list()`

对应记忆大厅设置页。返回已解锁、可设置为大厅的记忆大厅条目。

| 项 | 内容 |
| --- | --- |
| 协议 | `MemoryLobby_List` |
| 参数 | 无 |
| 返回 | `memory_lobbies`, `count`, `extra` |
| live | 已通过 |

```python
memory_lobbies = await client.memory_lobby.list()
```

### `client.scenario.list()`

对应剧情回放/故事收藏页面。返回已读剧情、剧情组进度和收藏状态。

| 项 | 内容 |
| --- | --- |
| 协议 | `Scenario_List` |
| 参数 | 无 |
| 返回 | `scenario_history`, `scenario_group_history`, `scenario_collections`, `count`, `group_count`, `collection_count`, `extra` |
| live | 已通过 |

```python
scenario = await client.scenario.list()
```

### `client.school_dungeon.list()`

对应学院交流会页面。返回关卡历史和最佳队伍；小号没开放该功能时会返回开放条件错误。

| 项 | 内容 |
| --- | --- |
| 协议 | `SchoolDungeon_List` |
| 参数 | 无 |
| 返回 | `stage_history`, `best_teams`, `stage_count`, `best_team_count`, `extra` |
| live | 大号通过；小号未开放时会返回 `OpenConditionClosed` |

```python
school = await client.school_dungeon.list()
```

### `client.system.version()`

对应客户端版本检查。通常用于确认当前 SDK 配置的客户端版本是否仍被服务端接受。

| 项 | 内容 |
| --- | --- |
| 协议 | `System_Version` |
| 参数 | 无 |
| 返回 | `current_version`, `minimum_version`, `is_development`, `extra` |
| live | 已通过 |

```python
version = await client.system.version()
```

### `client.toast.list()`

对应服务端下发的轻量提示/Toast 列表，通常用于打开大厅或页面时展示提示。

| 项 | 内容 |
| --- | --- |
| 协议 | `Toast_List` |
| 参数 | 无 |
| 返回 | `toasts`, `count`, `extra` |
| live | 已通过 |

```python
toasts = await client.toast.list()
```

## 活动页、活动关卡和活动商店

这一组对应游戏里的活动入口、活动 Banner、永久化活动、活动关卡、活动商店、箱式商店、活动收藏、DiceRace、Treasure、ClueSearch 等活动页面。活动页面数据最依赖当前开放内容，`event_content_id` 必须来自当前账号能看到的活动或永久化活动。

### `client.event.list()`

对应活动入口/活动列表。返回当前账号能看到的活动摘要。

| 项 | 内容 |
| --- | --- |
| 协议 | `Event_GetList` |
| 参数 | 无 |
| 返回 | `events`, `count`, `extra` |
| live | 已通过 |

```python
events = await client.event.list()
```

### `client.event.image(event_id)`

对应活动 Banner、活动图片资源信息。通常用于 GUI 展示当前活动图。

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| `event_id` | `int` | 活动 ID。通常应来自活动配置或 `event.list()` 可见活动。 |

返回结构：

```python
{
    "event_image": {...},
    "images": [{...}],
    "count": 1,
    "extra": {},
}
```

```python
images = await client.event.image(event_id)
```

### `client.event_content.permanent_list()`

对应常驻化/永久化活动列表。这个列表常用来寻找后续活动内容方法需要的 `event_content_id`。

| 项 | 内容 |
| --- | --- |
| 协议 | `EventContent_PermanentList` |
| 参数 | 无 |
| 返回 | `permanent`, `count`, `extra` |
| live | 已通过 |

```python
permanent = await client.event_content.permanent_list()
```

### 活动内容 ID 怎么取

下面这些活动内容方法都需要 `event_content_id`。这个 ID 必须来自当前账号可见、当前开放或永久化且类型匹配的活动内容；不要随便硬填。活动类型不匹配时，服务端会返回 `DataEntityNotFound`、`DataClassNotFound` 或玩法专属错误。

常见取法：

```python
permanent = await client.event_content.permanent_list()
event_content_id = permanent["permanent"][0]["EventContentId"]
```

### `client.event_content.adventure_list(event_content_id)`

对应活动关卡页面。返回关卡历史、地图策略对象、额外奖励状态和活动点数。

| 项 | 内容 |
| --- | --- |
| 协议 | `EventContent_AdventureList` |
| RequestClass | `EventContentAdventureListRequest` |
| 参数 | `event_content_id: int` |
| live | 已通过 |

返回结构：

```python
{
    "stage_history": [{...}],
    "strategy_object_history": [{...}],
    "bonus_rewards": [{...}],
    "already_receive_reward_ids": [1, 2],
    "stage_point": {...},
    "stage_count": 1,
    "extra": {},
}
```

示例：

```python
adventure = await client.event_content.adventure_list(event_content_id)
stages = adventure["stage_history"]
```

### `client.event_content.shop_list(event_content_id, category_list=None)`

对应活动商店页面。返回活动商店货架和兑换历史，只看状态，不购买道具。

| 项 | 内容 |
| --- | --- |
| 协议 | `EventContent_ShopList` |
| RequestClass | `EventContentShopListRequest` |
| 参数 | `event_content_id: int`, `category_list: list[int] \| tuple[int, ...] \| None` |
| live | 已封装；本轮账号缺少匹配活动商店上下文 |

返回结构：

```python
{
    "shop_infos": [{...}],
    "eligma_history": [{...}],
    "count": 1,
    "extra": {},
}
```

示例：

```python
shops = await client.event_content.shop_list(event_content_id)
filtered = await client.event_content.shop_list(event_content_id, category_list=[1, 2])
```

### `client.event_content.box_gacha_shop_list(event_content_id)`

对应活动里的箱式商店/Box Gacha 页面。只读取箱池状态，不抽取、不重置。

| 项 | 内容 |
| --- | --- |
| 协议 | `EventContent_BoxGachaShopList` |
| RequestClass | `EventContentBoxGachaShopListRequest` |
| 参数 | `event_content_id: int` |
| live | 已封装；本轮账号缺少匹配 Box Gacha 活动上下文 |

返回结构：

```python
{
    "box_gacha": {...},
    "box_gacha_group_id_by_count": {...},
    "extra": {},
}
```

示例：

```python
box_state = await client.event_content.box_gacha_shop_list(event_content_id)
```

### `client.event_content.collection_list(event_content_id, group_id=None)`

对应活动收藏/CG 回收页面。返回已解锁收藏条目。

| 项 | 内容 |
| --- | --- |
| 协议 | `EventContent_CollectionList` |
| RequestClass | `EventContentCollectionListRequest` |
| 参数 | `event_content_id: int`, `group_id: int \| None` |
| live | 已通过 |

返回结构：

```python
{
    "collections": [{...}],
    "count": 1,
    "extra": {},
}
```

示例：

```python
collections = await client.event_content.collection_list(event_content_id)
group_collections = await client.event_content.collection_list(event_content_id, group_id=1)
```

### `client.event_content.collection_for_mission(event_content_id)`

对应活动任务页里的收藏类任务进度，用来判断收藏相关任务状态。

| 项 | 内容 |
| --- | --- |
| 协议 | `EventContent_CollectionForMission` |
| RequestClass | `EventContentCollectionForMissionRequest` |
| 参数 | `event_content_id: int` |
| live | 已通过 |

返回结构：

```python
{
    "collections": [{...}],
    "count": 1,
    "extra": {},
}
```

示例：

```python
mission_collections = await client.event_content.collection_for_mission(event_content_id)
```

### `client.event_content.location_get_info(event_content_id)`

对应 Location 类型活动页面。只有当前活动确实是 Location 类型时才会成功。

| 项 | 内容 |
| --- | --- |
| 协议 | `EventContent_LocationGetInfo` |
| RequestClass | `EventContentLocationGetInfoRequest` |
| 参数 | `event_content_id: int` |
| live | 已封装；本轮账号缺少匹配 Location 活动上下文 |

返回结构：

```python
{
    "location": {...},
    "extra": {},
}
```

示例：

```python
location = await client.event_content.location_get_info(event_content_id)
```

### `client.event_content.sub_event_lobby(event_content_id)`

对应活动里的 SubEvent 子活动大厅，返回当前是否处于子活动状态。

| 项 | 内容 |
| --- | --- |
| 协议 | `EventContent_SubEventLobby` |
| RequestClass | `EventContentSubEventLobbyRequest` |
| 参数 | `event_content_id: int` |
| live | 已封装；本轮账号缺少匹配 SubEvent 活动上下文 |

返回结构：

```python
{
    "event_content_change": {...},
    "is_on_sub_event": False,
    "extra": {},
}
```

示例：

```python
sub_event = await client.event_content.sub_event_lobby(event_content_id)
```

### `client.event_content.dice_race_lobby(event_content_id)`

对应活动里的 DiceRace 骰子赛跑页面。

| 项 | 内容 |
| --- | --- |
| 协议 | `EventContent_DiceRaceLobby` |
| RequestClass | `EventContentDiceRaceLobbyRequest` |
| 参数 | `event_content_id: int` |
| live | 已通过 |

返回结构：

```python
{
    "dice_race": {...},
    "extra": {},
}
```

示例：

```python
dice_race = await client.event_content.dice_race_lobby(event_content_id)
```

### `client.event_content.treasure_lobby(event_content_id)`

对应活动里的 Treasure 寻宝/翻图页面，返回棋盘历史、隐藏图和变体 ID。

| 项 | 内容 |
| --- | --- |
| 协议 | `EventContent_TreasureLobby` |
| RequestClass | `EventContentTreasureLobbyRequest` |
| 参数 | `event_content_id: int` |
| live | 已封装；本轮账号缺少匹配 Treasure 活动上下文 |

返回结构：

```python
{
    "board_history": {...},
    "hidden_image": {...},
    "variation_id": 0,
    "extra": {},
}
```

示例：

```python
treasure = await client.event_content.treasure_lobby(event_content_id)
```

### `client.event_content.clue_search_get_info(event_content_id)`

对应活动里的 Clue Search 线索搜索页面。它通常会展示当前轮次、线索面板、进度和已领取的集合奖励。只要活动内容 ID 对得上，这个接口就能把页面状态整理出来给 UI 直接用。

| 项 | 内容 |
| --- | --- |
| 协议 | `EventContent_ClueSearchGetInfo` |
| RequestClass | `EventContentClueSearchGetInfoRequest` |
| 参数 | `event_content_id: int` |
| live | 已封装；本轮账号缺少匹配 ClueSearch 活动上下文时会返回 `ErrorCode=16 DataEntityNotFound` |

返回结构：

```python
{
    "clue_search": {...},
    "round": {...},
    "progress": {...},
    "collections": [{...}],
    "already_receive_reward_ids": [1, 2],
    "event_content_id": 30051,
    "collection_count": 1,
    "extra": {},
}
```

字段说明：

- `clue_search`：线索搜索页面主状态。
- `round`：当前轮次/回合信息。
- `progress`：当前搜索进度。
- `collections`：线索相关集合或已解锁条目。
- `already_receive_reward_ids`：已经领过的奖励 ID。
- `event_content_id`：当前活动内容 ID。
- `collection_count`：集合数量，常用于页面角标或列表长度。
- `extra`：服务端额外带回、但 SDK 还没单独整理的字段。

示例：

```python
clue = await client.event_content.clue_search_get_info(event_content_id)
print(clue["collection_count"])
print(clue["already_receive_reward_ids"])
```

## 招募页面状态

这一组对应招募页面、预抽卡页面和自选 Pickup 状态。只读招募列表和状态，不购买、不抽卡、不保存结果。

### `client.shop.gacha_recruit_list()`

对应招募列表页面。返回当前开放卡池、免费招募历史和账号货币摘要。

| 项 | 内容 |
| --- | --- |
| 协议 | `Shop_GachaRecruitList` |
| 参数 | 无 |
| 返回 | `shop_recruits`, `free_recruit_history`, `account_currency`, `count`, `free_history_count`, `extra` |
| live | 已通过 |

```python
recruits = await client.shop.gacha_recruit_list()
```

### `client.shop.beforehand_gacha_get()`

对应预抽卡/Beforehand Gacha 页面。只读取当前状态和历史，不保存结果。

| 项 | 内容 |
| --- | --- |
| 协议 | `Shop_BeforehandGachaGet` |
| 参数 | 无 |
| 返回 | `beforehand_gacha`, `beforehand_gacha_history`, `extra` |
| live | 已通过 |

```python
beforehand = await client.shop.beforehand_gacha_get()
```

### `client.shop.pickup_selection_gacha_get(shop_recruit_id)`

对应自选 Pickup 招募页面。只读取当前选择状态，不抽卡、不购买。

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| `shop_recruit_id` | `int` | 当前开放自选 Pickup 招募的 ID，应来自招募列表。 |

返回结构：

```python
{
    "pickup_selection_gacha": {...},
    "shop_recruit": {...},
    "extra": {},
}
```

```python
recruits = await client.shop.gacha_recruit_list()
shop_recruit_id = recruits["shop_recruits"][0]["ShopRecruitId"]
state = await client.shop.pickup_selection_gacha_get(shop_recruit_id)
```

本轮 live 账号没有有效自选 Pickup 招募，错误为 `ShopInfoNotFound`。

## 好友页和玩家名片

这一组对应好友页面、好友搜索、玩家详情和自己的名片。这里只做查看，不发送、接受、拒绝或取消好友申请。好友申请操作见 [好友申请、制造完成、关卡确认和剧情跳过](state-changing.md)。

### `client.friend.list()`

对应好友列表页。返回好友、收到的申请、已发送申请、屏蔽列表和名片背景。

返回结构：

```python
{
    "id_card_backgrounds": [{...}],
    "friends": [{...}],
    "received_requests": [{...}],
    "sent_requests": [{...}],
    "blocked_friends": [{...}],
    "friend_id_card": {...},
    "count": 1,
    "received_count": 0,
    "sent_count": 0,
    "blocked_count": 0,
    "extra": {},
}
```

```python
friends = await client.friend.list()
print(friends["count"], friends["received_count"])
```

### `client.friend.detailed_info(friend_account_id)`

对应点击好友/玩家后打开的玩家详情页。

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| `friend_account_id` | `int` | 好友或目标账号 ID。 |

返回结构：

```python
{
    "detailed_account_info": {...},
    "friend": {...},
    "extra": {},
}
```

```python
friends = await client.friend.list()
friend_account_id = friends["friends"][0]["AccountId"]
info = await client.friend.detailed_info(friend_account_id)
```

### `client.friend.id_card()`

对应自己的好友名片页面。

返回结构：

```python
{
    "id_card": {...},
    "extra": {},
}
```

```python
id_card = await client.friend.id_card()
```

### `client.friend.search(friend_code=None, level_option=None)`

对应好友搜索页面，可按好友码或等级筛选搜索玩家。

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| `friend_code` | `str \| None` | 好友码。不传则按服务端默认搜索行为。 |
| `level_option` | `int \| None` | 等级筛选枚举值。 |

返回结构：

```python
{
    "friends": [{...}],
    "count": 1,
    "extra": {},
}
```

```python
result = await client.friend.search(friend_code="ABCDEF")
```

### `client.friend.list_by_ids(target_account_ids)`

对应外部程序已持有账号 ID 时批量查玩家信息。

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| `target_account_ids` | `list[int] \| tuple[int, ...]` | 目标账号 ID 列表，不能为空。 |

返回结构：

```python
{
    "friends": [{...}],
    "count": 1,
    "extra": {},
}
```

```python
result = await client.friend.list_by_ids([target_account_id])
```

## 社团页和社团助战

这一组对应社团大厅、社团搜索、社团成员列表和社团助战页面。这里只查看社团信息，不申请加入、不退出、不解散。

### `client.clan.lobby()`

对应社团大厅。返回当前账号社团、成员摘要、IRC 配置和默认展示社团。

返回结构：

```python
{
    "irc_config": {...},
    "account_clan": {...},
    "default_exposed_clans": [{...}],
    "account_clan_member": {...},
    "clan_members": [{...}],
    "member_count": 1,
    "default_exposed_count": 1,
    "extra": {},
}
```

```python
lobby = await client.clan.lobby()
```

### `client.clan.search(...)`

对应社团搜索页面。只返回搜索结果，不申请加入。

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| `clan_join_option` | `int \| None` | 加入条件筛选。 |
| `clan_unique_code` | `str \| None` | 社团唯一码。 |
| `search_string` | `str \| None` | 搜索文本。 |

返回结构：

```python
{
    "clans": [{...}],
    "count": 1,
    "extra": {},
}
```

```python
clans = await client.clan.search(search_string="test")
```

### `client.clan.member(clan_db_id, member_account_id)`

对应社团成员详情页。

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| `clan_db_id` | `int` | 社团 DB ID。 |
| `member_account_id` | `int` | 成员账号 ID。 |

返回结构：

```python
{
    "clan": {...},
    "clan_member": {...},
    "detailed_account_info": {...},
    "extra": {},
}
```

```python
lobby = await client.clan.lobby()
clan_db_id = lobby["account_clan"]["ServerId"]
member_account_id = lobby["clan_members"][0]["AccountId"]
member = await client.clan.member(clan_db_id, member_account_id)
```

### `client.clan.member_list(clan_db_id)`

对应社团成员列表页。

返回结构：

```python
{
    "clan": {...},
    "clan_members": [{...}],
    "count": 1,
    "extra": {},
}
```

```python
members = await client.clan.member_list(clan_db_id)
```

### `client.clan.my_assist_list()`

对应自己的社团助战设置页。

返回结构：

```python
{
    "assist_slots": [{...}],
    "count": 1,
    "extra": {},
}
```

```python
my_assists = await client.clan.my_assist_list()
```

### `client.clan.all_assist_list(...)`

对应社团助战选择页。只读取可用助战和租借历史，不借用。

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| `echelon_type` | `int` | 编队/玩法类型枚举，必填。 |
| `is_practice` | `bool` | 是否练习模式。默认 `False`。 |
| `pending_assist_use_info` | `list[dict] \| tuple[dict, ...] \| None` | 待使用助战信息。通常传空列表。 |

返回结构：

```python
{
    "assist_characters": [{...}],
    "assist_character_rent_history": [{...}],
    "clan_db_id": 123,
    "count": 1,
    "extra": {},
}
```

```python
assists = await client.clan.all_assist_list(
    echelon_type=0,
    is_practice=False,
    pending_assist_use_info=[],
)
```

## 总力战、大决战、制约解除决战和 WorldRaid

这一组对应总力战/大决战大厅、房间列表、排名列表、最佳队伍、制约解除决战、常驻 Raid 和 WorldRaid 页面。这里只看大厅、排行和队伍数据，不进入战斗、不提交成绩、不领奖。

### `client.raid.list(...)`

对应 Raid 房间列表页。

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| `raid_boss_group` | `str \| None` | Boss 组筛选。 |
| `raid_difficulty` | `int \| None` | 难度筛选。 |
| `raid_room_sort_option` | `int \| None` | 排序选项。 |

返回结构：

```python
{
    "create_raids": [{...}],
    "enter_raids": [{...}],
    "list_raids": [{...}],
    "count": 1,
    "extra": {},
}
```

```python
raids = await client.raid.list()
```

### `client.raid.complete_list()`

对应已完成 Raid 记录和赛季摘要。

返回结构：

```python
{
    "raids": [{...}],
    "stacked_damage": 0,
    "receive_reward_ids": [1, 2],
    "current_season_unique_id": 0,
    "count": 1,
    "extra": {},
}
```

```python
completed = await client.raid.complete_list()
```

### `client.raid.search(secret_code=None, tags=None)`

对应按房间码或标签搜索 Raid 房间。

返回结构：

```python
{
    "raids": [{...}],
    "count": 1,
    "extra": {},
}
```

```python
result = await client.raid.search(secret_code=None, tags=[])
```

### `client.raid.lobby()`

对应总力战/大决战大厅。返回赛季类型、大厅信息、放弃状态和货币摘要。

返回结构：

```python
{
    "season_type": 0,
    "raid_give_up": {...},
    "raid_lobby_info": {...},
    "account_currency": {...},
    "parcel_result": {...},
    "extra": {},
}
```

```python
lobby = await client.raid.lobby()
```

### `client.raid.opponent_list(...)`

对应 Raid 排行榜邻近玩家列表。

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| `is_first_request` | `bool \| None` | 是否首次请求。 |
| `is_upper` | `bool \| None` | 是否查询上方排名。 |
| `rank` | `int \| None` | 基准排名。 |
| `score` | `int \| None` | 基准分数。 |
| `search_type` | `int \| None` | 搜索类型。 |

返回结构：

```python
{
    "opponents": [{...}],
    "count": 1,
    "extra": {},
}
```

```python
opponents = await client.raid.opponent_list(
    is_first_request=True,
    is_upper=False,
    rank=0,
    score=0,
    search_type=0,
)
```

### `client.raid.get_best_team(search_account_id)`

对应排行榜里查看某个玩家最佳队伍。

返回结构：

```python
{
    "team_settings": [{...}],
    "count": 1,
    "extra": {},
}
```

```python
team = await client.raid.get_best_team(search_account_id)
```

### `client.raid.ranking_index()`

对应 Raid 排行榜分段索引，用于分页或定位排名区间。

返回结构：

```python
{
    "rank_brackets": [{...}],
    "count": 1,
    "extra": {},
}
```

```python
index = await client.raid.ranking_index()
```

### `client.eliminate_raid.lobby()`

对应制约解除决战大厅。返回大厅信息、放弃状态、赛季类型和货币摘要。

| 项 | 内容 |
| --- | --- |
| 协议 | `EliminateRaid_Lobby` |
| RequestClass | `EliminateRaidLobbyRequest` |
| 参数 | 无 |
| live | 已通过 |

返回结构：

```python
{
    "lobby_info": {...},
    "give_up": {...},
    "season_type": 0,
    "account_currency": {...},
    "parcel_result": {...},
    "extra": {},
}
```

示例：

```python
lobby = await client.eliminate_raid.lobby()
```

### `client.eliminate_raid.opponent_list(...)`

对应制约解除决战排行榜邻近玩家列表。

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| `boss_group_index` | `int \| None` | Boss 组索引。 |
| `is_first_request` | `bool \| None` | 是否首次请求。 |
| `is_upper` | `bool \| None` | 是否查询上方排名。 |
| `rank` | `int \| None` | 基准排名。 |
| `score` | `int \| None` | 基准分数。 |
| `search_type` | `int \| None` | 搜索类型。 |

返回结构：

```python
{
    "opponents": [{...}],
    "count": 1,
    "extra": {},
}
```

示例：

```python
opponents = await client.eliminate_raid.opponent_list(
    boss_group_index=0,
    is_first_request=True,
    is_upper=False,
    rank=0,
    score=0,
    search_type=0,
)
```

### `client.eliminate_raid.get_best_team(search_account_id)`

对应制约解除决战排行榜里查看某个玩家最佳队伍。

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| `search_account_id` | `int` | 目标账号 ID，通常来自排名、好友或搜索结果。 |

返回结构：

```python
{
    "team_settings_by_key": {"key": [{...}]},
    "team_settings": [{...}],
    "count": 1,
    "extra": {},
}
```

示例：

```python
team = await client.eliminate_raid.get_best_team(search_account_id)
```

### `client.eliminate_raid.ranking_index()`

对应制约解除决战排行榜分段索引。

返回结构：

```python
{
    "rank_brackets": [{...}],
    "count": 1,
    "extra": {},
}
```

示例：

```python
ranking = await client.eliminate_raid.ranking_index()
```

### `client.permanent_raid.lobby()`

对应常驻 Raid 大厅和赛季列表。

返回结构：

```python
{
    "lobby_infos": [{...}],
    "seasons": [{...}],
    "account_currency": {...},
    "count": 1,
    "season_count": 1,
    "extra": {},
}
```

```python
permanent_raid = await client.permanent_raid.lobby()
```

### `client.world_raid.lobby(content_type, season_id)`

对应 WorldRaid 大厅。返回清除历史、本地 Boss 和 Boss 组信息。WorldRaid 需要当前开放的 `content_type` 和 `season_id`，本轮 live 没有拿到候选参数。

| 项 | 内容 |
| --- | --- |
| 协议 | `WorldRaid_Lobby` |
| RequestClass | `WorldRaidLobbyRequest` |
| 参数 | `content_type: int`, `season_id: int` |
| live | 已封装；本轮无当前开放 WorldRaid 参数 |

返回结构：

```python
{
    "clear_history": [{...}],
    "local_bosses": [{...}],
    "boss_groups": [{...}],
    "clear_history_count": 1,
    "local_boss_count": 1,
    "boss_group_count": 1,
    "extra": {},
}
```

示例：

```python
lobby = await client.world_raid.lobby(content_type, season_id)
```

### `client.world_raid.boss_list(content_type, season_id, request_only_world_boss_data=False)`

对应 WorldRaid Boss 列表。`request_only_world_boss_data=True` 时只请求 WorldBoss 数据。

| 项 | 内容 |
| --- | --- |
| 协议 | `WorldRaid_BossList` |
| RequestClass | `WorldRaidBossListRequest` |
| 参数 | `content_type: int`, `season_id: int`, `request_only_world_boss_data: bool = False` |
| live | 已封装；本轮无当前开放 WorldRaid 参数 |

返回结构：

```python
{
    "boss_list_info": [{...}],
    "count": 1,
    "extra": {},
}
```

示例：

```python
bosses = await client.world_raid.boss_list(content_type, season_id)
world_only = await client.world_raid.boss_list(
    content_type,
    season_id,
    request_only_world_boss_data=True,
)
```

## 战斗通行证、制造、公告和指南任务

这一组对应战斗通行证、咖啡厅奖杯历史、占领战、制造页、公告横幅、协议锁和指南任务赛季。

### `client.battle_pass.get_info(battle_pass_id)`

对应战斗通行证页面的基础信息。

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| `battle_pass_id` | `int` | BattlePass ID。需要来自当前活动/配置。 |

返回结构：

```python
{
    "battle_pass_info": {...},
    "extra": {},
}
```

```python
info = await client.battle_pass.get_info(battle_pass_id)
```

### `client.battle_pass.mission_list(battle_pass_id)`

对应战斗通行证任务页。

返回结构：

```python
{
    "mission_history_unique_ids": [1, 2],
    "progress": [{...}],
    "count": 1,
    "extra": {},
}
```

```python
missions = await client.battle_pass.mission_list(battle_pass_id)
```

### `client.cafe.trophy_history()`

对应咖啡厅奖杯历史页。

返回结构：

```python
{
    "trophy_history": [{...}],
    "count": 1,
    "extra": {},
}
```

```python
trophy = await client.cafe.trophy_history()
```

### `client.conquest.get_info(event_content_id)`

对应占领战活动页面。只有当前开放且账号可访问的占领战活动 ID 才会成功。

返回结构：

```python
{
    "conquest_info": {...},
    "conquered_tiles": [{...}],
    "echelons": [{...}],
    "event_objects": [{...}],
    "difficulty_to_step": {...},
    "is_first_enter": False,
    "display_infos": [{...}],
    "conquered_tile_count": 1,
    "echelon_count": 1,
    "event_object_count": 1,
    "extra": {},
}
```

```python
conquest = await client.conquest.get_info(event_content_id)
```

### `client.conquest.main_story_get_info(event_content_id)`

对应占领战主线活动页面。只有当前开放且账号可访问的占领战主线活动 ID 才会成功。

返回结构：

```python
{
    "main_stories": [{...}],
    "count": 1,
    "extra": {},
}
```

```python
story = await client.conquest.main_story_get_info(event_content_id)
```

### `client.craft.list()`

对应制造页面。这里只看普通制造、转化制造、制造节点和槽位状态，不领取完成结果。

返回结构：

```python
{
    "craft_infos": [{...}],
    "shifting_craft_infos": [{...}],
    "craft_nodes": [{...}],
    "craft_slots": [{...}],
    "count": 1,
    "shifting_count": 0,
    "node_count": 1,
    "slot_count": 1,
    "extra": {},
}
```

```python
craft = await client.craft.list()
```

### `client.management.banner_list()`

对应公告横幅/管理公告列表。

返回结构：

```python
{
    "banners": [{...}],
    "count": 1,
    "extra": {},
}
```

```python
banners = await client.management.banner_list()
```

### `client.management.protocol_lock_list()`

对应服务端协议开放限制列表，常用于判断某些页面或玩法是否被服务端锁定。

返回结构：

```python
{
    "protocol_locks": [{...}],
    "count": 1,
    "extra": {},
}
```

```python
locks = await client.management.protocol_lock_list()
```

### `client.mission.guide_season_list()`

对应指南任务/Guide Mission 的赛季列表。

返回结构：

```python
{
    "guide_mission_seasons": [{...}],
    "count": 1,
    "extra": {},
}
```

```python
seasons = await client.mission.guide_season_list()
```

## 活动小游戏页面

这一组对应活动小游戏页面，比如 Shooting、TableBoard、DreamMaker、Defense、RoadPuzzle、CCG。小游戏方法都需要 `event_content_id`，必须对应当前有效的小游戏活动。这里只读取大厅、关卡和任务状态，不进入小游戏、不结算、不提交成绩。

### `client.mini_game.stage_list(event_content_id)`

对应活动小游戏的关卡列表或游玩历史页面。

返回结构：

```python
{
    "stages": [{...}],
    "count": 1,
    "extra": {},
}
```

示例：

```python
stages = await client.mini_game.stage_list(event_content_id)
```

### `client.mini_game.mission_list(event_content_id)`

对应活动小游戏任务页面。

返回结构：

```python
{
    "mission_history_unique_ids": [1, 2],
    "progress": [{...}],
    "count": 1,
    "extra": {},
}
```

示例：

```python
missions = await client.mini_game.mission_list(event_content_id)
```

### `client.mini_game.shooting_lobby(event_content_id)`

对应 Shooting 类活动小游戏大厅，返回小游戏大厅状态、关卡历史和活动货币摘要。

返回结构：

```python
{
    "shooting_lobby": {...},
    "stage_history": [{...}],
    "account_currency": {...},
    "stage_count": 1,
    "extra": {},
}
```

示例：

```python
shooting = await client.mini_game.shooting_lobby(event_content_id)
```

### `client.mini_game.table_board_sync(event_content_id)`

对应 TableBoard 桌游/棋盘类活动小游戏页面，同步棋盘状态、关卡和活动货币摘要。

返回结构：

```python
{
    "table_board": {...},
    "stages": [{...}],
    "account_currency": {...},
    "stage_count": 1,
    "extra": {},
}
```

示例：

```python
table_board = await client.mini_game.table_board_sync(event_content_id)
```

### `client.mini_game.dream_maker_get_info(event_content_id)`

对应 DreamMaker 类活动小游戏页面，返回小游戏状态、日程和活动货币摘要。

返回结构：

```python
{
    "dream_maker": {...},
    "schedules": [{...}],
    "account_currency": {...},
    "schedule_count": 1,
    "extra": {},
}
```

示例：

```python
dream_maker = await client.mini_game.dream_maker_get_info(event_content_id)
```

### `client.mini_game.defense_get_info(event_content_id)`

对应 Defense 类活动小游戏页面，返回防守小游戏状态、关卡历史和活动货币摘要。

返回结构：

```python
{
    "defense": {...},
    "stage_history": [{...}],
    "account_currency": {...},
    "stage_count": 1,
    "extra": {},
}
```

示例：

```python
defense = await client.mini_game.defense_get_info(event_content_id)
```

### `client.mini_game.road_puzzle_get_info(event_content_id)`

对应 RoadPuzzle 类活动小游戏页面，返回道路解谜状态、关卡历史和活动货币摘要。

返回结构：

```python
{
    "road_puzzle": {...},
    "stage_history": [{...}],
    "account_currency": {...},
    "stage_count": 1,
    "extra": {},
}
```

示例：

```python
road_puzzle = await client.mini_game.road_puzzle_get_info(event_content_id)
```

### `client.mini_game.ccg_lobby(event_content_id)`

对应 CCG 卡牌类活动小游戏大厅，返回 CCG 状态、卡组和活动货币摘要。这里只看大厅状态，不创建游戏、不进入关卡、不放弃游戏、不替换角色。

返回结构：

```python
{
    "ccg": {...},
    "decks": [{...}],
    "account_currency": {...},
    "deck_count": 1,
    "extra": {},
}
```

示例：

```python
ccg = await client.mini_game.ccg_lobby(event_content_id)
```

本轮 live 中 `stage_list`、`mission_list`、`shooting_lobby` 有成功样本；其它小游戏方法需要对应开放赛季。

## Live 验证

2026-06-16 使用小号优先、大号兜底做过 live 验证。验证过程只输出方法名、计数和错误码摘要，不保存请求包、响应包或 dump，不输出 session/profile/token。

已在至少一个账号上 live 通过的 54 个方法：

```text
account.tutorial
attachment.get
attachment.emblem_list
battle_pass.get_info
battle_pass.mission_list
cafe.trophy_history
character_gear.list
clan.lobby
clan.search
clan.member
clan.member_list
clan.my_assist_list
clan.all_assist_list
craft.list
echelon.list
eliminate_raid.lobby
eliminate_raid.opponent_list
eliminate_raid.get_best_team
eliminate_raid.ranking_index
equipment.list
event.list
event.image
event_content.adventure_list
event_content.collection_list
event_content.collection_for_mission
event_content.dice_race_lobby
event_content.permanent_list
friend.list
friend.detailed_info
friend.id_card
friend.search
friend.list_by_ids
item.list
management.banner_list
management.protocol_lock_list
memory_lobby.list
mini_game.stage_list
mini_game.mission_list
mini_game.shooting_lobby
mission.guide_season_list
permanent_raid.lobby
raid.list
raid.complete_list
raid.search
raid.lobby
raid.opponent_list
raid.get_best_team
raid.ranking_index
scenario.list
school_dungeon.list
shop.gacha_recruit_list
shop.beforehand_gacha_get
system.version
toast.list
```

当前账号或当前活动上下文不足，已封装但本轮 live 未得到成功响应的 16 个方法：

| 游戏功能/SDK 方法 | 本轮 live 结果 | 后续验证条件 |
| --- | --- | --- |
| `conquest.get_info(event_content_id)` | `ErrorCode=16 DataEntityNotFound` | 需要当前开放且账号可访问的占领战活动 ID。 |
| `conquest.main_story_get_info(event_content_id)` | `ErrorCode=16 DataEntityNotFound` | 需要当前开放且账号可访问的占领战主线活动 ID。 |
| `event_content.shop_list(event_content_id)` | `ErrorCode=16 DataEntityNotFound` | 需要带活动商店的有效活动内容 ID。 |
| `event_content.box_gacha_shop_list(event_content_id)` | `ErrorCode=15 DataClassNotFound` | 需要带箱式抽奖商店的有效活动内容 ID。 |
| `event_content.location_get_info(event_content_id)` | `ErrorCode=16 DataEntityNotFound` | 需要带地点玩法的有效活动内容 ID。 |
| `event_content.sub_event_lobby(event_content_id)` | `ErrorCode=15 DataClassNotFound` | 需要带 SubEvent 的有效活动内容 ID。 |
| `event_content.treasure_lobby(event_content_id)` | `ErrorCode=500 ServerFailedToHandleRequest` | 需要带 Treasure 玩法的有效活动内容 ID。 |
| `event_content.clue_search_get_info(event_content_id)` | `ErrorCode=16 DataEntityNotFound` | 需要带 ClueSearch 玩法的有效活动内容 ID。 |
| `mini_game.table_board_sync(event_content_id)` | `ErrorCode=37012 MiniGameTableBoardInvalidSeason` | 需要当前有效 TableBoard 小游戏赛季。 |
| `mini_game.dream_maker_get_info(event_content_id)` | `ErrorCode=500 ServerFailedToHandleRequest` | 需要当前有效 DreamMaker 小游戏活动。 |
| `mini_game.defense_get_info(event_content_id)` | `ErrorCode=15 DataClassNotFound` | 需要当前有效 Defense 小游戏活动。 |
| `mini_game.road_puzzle_get_info(event_content_id)` | `ErrorCode=16 DataEntityNotFound` | 需要当前有效 RoadPuzzle 小游戏活动。 |
| `mini_game.ccg_lobby(event_content_id)` | `ErrorCode=500 ServerFailedToHandleRequest` | 需要当前有效 CCG 小游戏活动。 |
| `shop.pickup_selection_gacha_get(shop_recruit_id)` | `ErrorCode=10005 ShopInfoNotFound` | 需要当前开放自选 Pickup 招募，并从招募列表取得有效 `ShopRecruitId`。 |
| `world_raid.lobby(content_type, season_id)` | 无候选参数 | 需要当前开放 WorldRaid 的 `ContentType` 和 `SeasonId`。 |
| `world_raid.boss_list(content_type, season_id)` | 无候选参数 | 需要当前开放 WorldRaid 的 `ContentType` 和 `SeasonId`。 |
