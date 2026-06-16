# 好友申请、制造完成、关卡确认和剧情跳过

本页记录游戏里会真正点下去、并改变账号状态的操作：好友页的申请/接受/拒绝/取消，制造页的一键领取，以及主线/剧情流程里的关卡结果确认或剧情跳过。这些不是“打开页面看一眼”，调用时必须传 `confirm=True`，否则会抛 `UnsafeOperationError`。

默认 `validate=True` 会先读取当前页面状态做前置校验。只有调用方已经从游戏流程里确认前置条件时，才应该传 `validate=False`。SDK 仍然是纯库，不新增 CLI，不自动保存请求包、响应包或 dump，也不输出会话凭证。

## 好友申请

对应游戏里的好友页面：发送申请、接受申请、拒绝申请、取消自己发出的申请。

### `client.friend.send_request(target_account_id, confirm=True, validate=True)`

- 游戏里对应：在好友搜索或玩家详情页点击“申请好友”。
- 前置：目标不在好友列表、已发送申请、已收到申请、屏蔽列表中。
- 开发者定位：`Friend_SendFriendRequest` / `FriendSendFriendRequestRequest`
- live：已通过。

参数：

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `target_account_id` | `int` | 是 | 目标玩家账号 ID。 |
| `confirm` | `bool` | 是 | 必须显式传 `True`。 |
| `validate` | `bool` | 否 | 默认 `True`，会先调用 `friend.list()` 校验当前好友状态。 |

返回结构沿用 `friend.list()`：

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
    "sent_count": 1,
    "blocked_count": 0,
    "extra": {},
}
```

示例：

```python
search = await client.friend.search(friend_code="ABCDEF")
target_account_id = search["friends"][0]["AccountId"]
result = await client.friend.send_request(target_account_id, confirm=True)
```

### `client.friend.accept_request(target_account_id, confirm=True, validate=True)`

- 游戏里对应：在收到的好友申请列表里点击“接受”。
- 前置：目标账号必须在 `friend.list()["received_requests"]` 中。
- 开发者定位：`Friend_AcceptFriendRequest` / `FriendAcceptFriendRequestRequest`
- live：已通过。

参数同 `send_request()`。

返回结构沿用 `friend.list()`。

示例：

```python
state = await client.friend.list()
target_account_id = state["received_requests"][0]["AccountId"]
result = await client.friend.accept_request(target_account_id, confirm=True)
```

### `client.friend.decline_request(target_account_id, confirm=True, validate=True)`

- 游戏里对应：在收到的好友申请列表里点击“拒绝”。
- 前置：目标账号必须在 `friend.list()["received_requests"]` 中。
- 开发者定位：`Friend_DeclineFriendRequest` / `FriendDeclineFriendRequestRequest`
- live：已通过。

参数同 `send_request()`。

返回结构沿用 `friend.list()`。

示例：

```python
state = await client.friend.list()
target_account_id = state["received_requests"][0]["AccountId"]
result = await client.friend.decline_request(target_account_id, confirm=True)
```

### `client.friend.cancel_request(target_account_id, confirm=True, validate=True)`

- 游戏里对应：在已发送申请列表里取消自己发出的好友申请。
- 前置：目标账号必须在 `friend.list()["sent_requests"]` 中。
- 开发者定位：`Friend_CancelFriendRequest` / `FriendCancelFriendRequestRequest`
- live：已通过。

参数同 `send_request()`。

返回结构沿用 `friend.list()`。

示例：

```python
state = await client.friend.list()
target_account_id = state["sent_requests"][0]["AccountId"]
result = await client.friend.cancel_request(target_account_id, confirm=True)
```

## 制造完成

对应游戏里的制造页面：一键领取普通制造或转化制造的完成结果。它会改变账号物品状态，所以必须显式确认。

### `client.craft.complete_process_all(confirm=True, validate=True)`

- 游戏里对应：在制造页面领取全部已完成的普通制造结果。
- 前置：`client.craft.list()["craft_infos"]` 中存在可处理的普通制造记录。
- 开发者定位：`Craft_CompleteProcessAll` / `CraftCompleteProcessAllRequest`
- live：已封装；本轮账号没有普通制造候选，因此未发送真实领取请求。

参数：

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `confirm` | `bool` | 是 | 必须显式传 `True`。 |
| `validate` | `bool` | 否 | 默认 `True`，会先调用 `craft.list()` 检查是否存在普通制造记录。 |

返回结构：

```python
{
    "craft_infos": [{...}],
    "ticket_item": {...},
    "count": 1,
    "extra": {},
}
```

示例：

```python
craft = await client.craft.list()
if craft["craft_infos"]:
    result = await client.craft.complete_process_all(confirm=True)
```

### `client.craft.shifting_complete_process_all(confirm=True, validate=True)`

- 游戏里对应：在制造页面领取全部已完成的转化制造结果。
- 前置：`client.craft.list()["shifting_craft_infos"]` 中存在可处理的转化制造记录。
- 开发者定位：`Craft_ShiftingCompleteProcessAll` / `CraftShiftingCompleteProcessAllRequest`
- live：已封装；本轮账号没有转化制造候选，因此未发送真实领取请求。

参数同 `complete_process_all()`。

返回结构：

```python
{
    "craft_infos": [{...}],
    "parcel_result": {...},
    "count": 1,
    "extra": {},
}
```

示例：

```python
craft = await client.craft.list()
if craft["shifting_craft_infos"]:
    result = await client.craft.shifting_complete_process_all(confirm=True)
```

## 主线关卡确认和剧情跳过

这三项对应主线/剧情流程里的“确认关卡结果”或“跳过剧情”。它们需要活跃关卡流程中的 `StageUniqueId` 和服务端 SaveData 上下文，不是从历史列表随便取一个 ID 就能发。

`Campaign_List.stage_history` 和 `Scenario_List.scenario_history` 是历史状态，不是可确认关卡的前置条件。live 验证中，直接拿历史关卡 ID 调用 `Campaign_ConfirmMainStage` 会返回 `ErrorCode=6003 CampaignStageInvalidSaveData`。

因此这三项默认 `validate=True` 会本地拦截。只有调用方已经从活跃关卡流程拿到对应 SaveData 和 `StageUniqueId`，才应该显式传 `validate=False` 发送请求。

### `client.campaign.confirm_main_stage(stage_unique_id, confirm=True, validate=False)`

- 游戏里对应：主线关卡流程结束后确认关卡结果。
- 前置：必须有活跃主线关卡 SaveData。
- 开发者定位：`Campaign_ConfirmMainStage` / `CampaignConfirmMainStageRequest`
- live：误用历史 ID 时服务端返回 `CampaignStageInvalidSaveData`；SDK 默认阻止这种误用。

参数：

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `stage_unique_id` | `int` | 是 | 活跃主线关卡流程中的 `StageUniqueId`。 |
| `confirm` | `bool` | 是 | 必须显式传 `True`。 |
| `validate` | `bool` | 否 | 默认 `True` 会本地拦截。确认已有活跃 SaveData 后才传 `False`。 |

返回结构：

```python
{
    "parcel_result": {...},
    "save_data": {...},
    "stage_info": {...},
    "extra": {},
}
```

示例：

```python
result = await client.campaign.confirm_main_stage(
    stage_unique_id,
    confirm=True,
    validate=False,
)
```

### `client.scenario.confirm_main_stage(stage_unique_id, confirm=True, validate=False)`

- 游戏里对应：剧情主线关卡流程结束后确认结果。
- 前置：必须有活跃剧情关卡 SaveData。
- 开发者定位：`Scenario_ConfirmMainStage` / `ScenarioConfirmMainStageRequest`
- live：SDK 默认阻止从历史列表误用 ID。

参数同 `campaign.confirm_main_stage()`。

返回结构：

```python
{
    "parcel_result": {...},
    "save_data": {...},
    "scenario_ids": [1, 2],
    "scenario_count": 2,
    "extra": {},
}
```

示例：

```python
result = await client.scenario.confirm_main_stage(
    stage_unique_id,
    confirm=True,
    validate=False,
)
```

### `client.scenario.skip_main_stage(stage_unique_id, confirm=True, validate=False)`

- 游戏里对应：剧情主线流程里点击跳过。
- 前置：必须有活跃剧情关卡 SaveData。
- 开发者定位：`Scenario_SkipMainStage` / `ScenarioSkipMainStageRequest`
- live：SDK 默认阻止从历史列表误用 ID。

参数同 `campaign.confirm_main_stage()`。

返回结构：

```python
{
    "extra": {},
}
```

示例：

```python
result = await client.scenario.skip_main_stage(
    stage_unique_id,
    confirm=True,
    validate=False,
)
```
