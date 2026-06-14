# 基础只读接口

这些接口只读取账号当前状态，不会改账号、不领奖、不花资源。说白了就是安全看一眼，适合外部程序做页面初始化。

## 学生列表

```python
characters = await client.character.list()
```

返回：

| 字段 | 说明 |
| --- | --- |
| `characters` | 持有学生列表，对应 `CharacterDBs`。 |
| `tss_characters` | `TSSCharacterDBs`。 |
| `count` | `characters` 数量。 |

## 主线关卡状态

```python
campaign = await client.campaign.list()
```

返回：

| 字段 | 说明 |
| --- | --- |
| `chapter_clear_reward_history` | 章节奖励领取历史。 |
| `stage_history` | 关卡历史。 |
| `strategy_object_history` | 战略地图对象历史。 |
| `stage_count` | `stage_history` 数量。 |

## 日常副本状态

```python
week = await client.week_dungeon.list()
```

返回：

| 字段 | 说明 |
| --- | --- |
| `additional_stage_ids` | 额外开放关卡 ID。 |
| `stage_history` | 悬赏通缉/日常副本历史。 |
| `stage_count` | `stage_history` 数量。 |

live 验证：

```text
Character_List ok
Campaign_List ok
WeekDungeon_List ok
```

只读接口一般最适合先接到 GUI 里。真要做状态变更，先从这些状态里判断条件，别上来就发包赌服务端心情。
