# 战斗通行证

对应游戏里的战斗通行证（Battle Pass）：赛季总览、任务页和领取状态。能看当前赛季的等级 / 经验 / 奖励分层、任务进度，以及有没有待领奖励；能做的是领取赛季奖励、领取任务奖励、购买等级（这三类都要 `confirm=True`）。

赛季 ID 必须来自当前活动、配置或登录链路：登录时可以传 `session_bootstrap_battle_pass_id`，让登录阶段顺带同步一次；否则从当前活动或配置里取。`client.battle_pass.*` 不会自行假定通用赛季号。

## SDK 入口

所有方法均为异步方法。

| 方法 | 用途 | 需 `confirm=True` |
| --- | --- | :--: |
| `get_info(battle_pass_id)` | 读赛季总览（等级 / 经验 / 奖励分层 / 领取状态） | 否 |
| `mission_list(battle_pass_id)` | 读赛季任务进度与历史任务 ID | 否 |
| `check(battle_pass_id)` | 看有没有未领奖励、有没有已完成任务可领 | 否 |
| `receive_reward(battle_pass_id, confirm=True)` | 领取赛季奖励 | 是 |
| `mission_single_reward(battle_pass_id, mission_unique_id, confirm=True)` | 领取单项任务奖励 | 是 |
| `mission_multiple_reward(battle_pass_id, mission_category, confirm=True)` | 按分类批量领取任务奖励 | 是 |
| `buy_level(battle_pass_id=…, battle_pass_buy_level_count=…, confirm=True)` | 花费货币购买通行证等级 | 是 |

```python
info = await client.battle_pass.get_info(battle_pass_id)
missions = await client.battle_pass.mission_list(battle_pass_id)
check = await client.battle_pass.check(battle_pass_id)
```

写操作默认还带 `validate=True`：`receive_reward` 会先 `check()` 确认 `has_not_receive_reward`，`mission_single_reward` / `mission_multiple_reward` 会先确认 `has_complete_mission`，无可领项时直接抛 `UnsafeOperationError` 且不发请求。

```python
check = await client.battle_pass.check(battle_pass_id)
if check["has_not_receive_reward"]:
    result = await client.battle_pass.receive_reward(battle_pass_id, confirm=True)
```

## 返回说明

- 只读方法（`get_info` / `mission_list` / `check`）经 `format_*` 整理，返回整理后的 dict：业务字段 +（列表方法附）`count` + `extra`。`get_info` 给赛季总览主体（赛季不开放或 ID 不对时可能是 `None`）；`mission_list` 给任务进度列表和 `count`；`check` 给两个布尔（`has_not_receive_reward` / `has_complete_mission`）。服务端其余原始字段都收进 `extra`。
- 写方法（`receive_reward` / `mission_single_reward` / `mission_multiple_reward` / `buy_level`）不经 `format_*`，直接返回服务端原始负载。

具体键名以服务端返回为准，此处仅描述结构。

## 注意

- 四个写方法都需显式 `confirm=True`，不传则抛 `UnsafeOperationError` 且不发包。
- `buy_level` 会消耗货币（属养成 / 消耗类），SDK 不做余额预检，购买前请自行确认资源。
- `battle_pass_id` / `mission_unique_id` / `mission_category` 一律来自当前账号可见数据，不要手填。

---

逐协议接入状态见 [协议总表](../../protocols.md)。
