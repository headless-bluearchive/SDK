# 学生、主线、日常副本和扫荡

对应游戏里最基础的战斗准备页面：学生名册、主线关卡地图、悬赏通缉/日常副本历史，以及扫荡。

这一页的查询只读取账号当前状态；扫荡是会消耗资源的写操作，必须显式确认。

## SDK 入口

| 方法 | 游戏里对应 | 参数 | 需 confirm |
| --- | --- | --- | :--: |
| `client.character.list()` | 学生名册 | 无 | |
| `client.campaign.list()` | 主线关卡进度/章节奖励历史 | 无 | |
| `client.week_dungeon.list()` | 悬赏通缉、日常副本历史 | 无 | |
| `client.sweep.preset_list()` | 多扫荡预设列表 | 无 | |
| `client.sweep.skip_history_list()` | 扫荡历史 | 无 | |
| `client.sweep.request(...)` | 单关扫荡（消耗 AP/票券） | 见下 | 是 |
| `client.sweep.multi_sweep(...)` | 多扫荡（消耗 AP/票券） | 见下 | 是 |

学生培养（升级、升星、技能、装备、爱用品等）和扫荡预设的保存/改名都是写操作，全部要求 `confirm=True`，放在 [显式确认变更页面](state-changing.md)。学院交流会在另一个入口，见 [扩展只读页面](readonly-extended.md) 的 `client.school_dungeon.list()`。扫荡的完整页面另见 [扫荡页面](sweep.md)。

## 返回说明

上面五个只读方法源码里都有 `format_*`，返回**整理后的 dict**：业务字段加列表类的 `count`，未整理的顶层字段归入 `extra`。下面只描述返回形状，不逐一列出键名（键名可能随服务端数据变化）。

### 学生名册

```python
characters = await client.character.list()
for character in characters["characters"]:
    print(character.get("UniqueId"), character.get("Level"))
```

返回持有学生列表（`characters`）、特殊同步学生数据，以及 `count`。单条学生记录仍是服务端原始 DB dict。

### 主线关卡进度

```python
campaign = await client.campaign.list()
cleared_stage_ids = {
    item.get("StageUniqueId")
    for item in campaign["stage_history"]
    if item.get("Clear") is True
}
```

返回的是“这个账号打过哪些关卡、章节奖励领取历史、战略地图对象历史”，不是战斗中的存档，也不能用于伪造结算。

### 悬赏通缉和日常副本

```python
week = await client.week_dungeon.list()
```

返回当前额外开放的关卡 ID、悬赏通缉/日常副本历史和 `count`。

### 扫荡预设和历史

```python
presets = await client.sweep.preset_list()
history = await client.sweep.skip_history_list()
```

`preset_list()` 返回用户保存过的多扫荡预设；`skip_history_list()` 返回保存的扫荡历史。两者都只读，不消耗 AP/票券、不改变掉落。

## 执行扫荡（需 `confirm=True`）

对应游戏里点“扫荡”按钮，会消耗 AP/票券并改变账号资源，因此 SDK 要求显式确认。

单关扫荡：

```python
result = await client.sweep.request(
    content=content_type,
    stage_id=stage_id,
    count=1,
    event_content_id=0,
    confirm=True,
)
```

多扫荡：

```python
result = await client.sweep.multi_sweep(
    [
        {
            "content_type": content_type,
            "stage_id": stage_id,
            "sweep_count": 1,
            "event_content_id": 0,
        }
    ],
    confirm=True,
)
```

参数说明：

| 参数 | 游戏含义 |
| --- | --- |
| `content` / `content_type` | 关卡所属内容类型（主线、活动、日常副本等）。 |
| `stage_id` | 要扫荡的关卡 ID，必须是账号已满足扫荡条件的关卡。 |
| `count` / `sweep_count` | 扫荡次数，必须大于 0。 |
| `event_content_id` | 活动关卡使用的活动内容 ID；普通关卡通常为 `0`。 |
| `confirm=True` | 明确告诉 SDK 这是资源消耗操作。 |

两者都返回整理后的 dict：基础掉落、额外掉落、活动加成掉落、账号物品/资源变动结果，以及关卡历史更新（`request()` 是单条，`multi_sweep()` 是列表），其余字段归入 `extra`。

## 注意

- `request()` / `multi_sweep()` 不传 `confirm=True` 会抛 `UnsafeOperationError` 且不发包。
- 调用扫荡前，应先用账号资源、关卡历史和自己的用户授权逻辑确认 AP、次数和扫荡条件；关卡/活动 ID 一律来自当前账号可见数据，不要手填。
- 逐协议接入状态见仓库根 [`docs/protocols.md`](../../protocols.md)。
