# Academy 协议

课程表/日程模块相关协议。

字段结构仅作为 SDK DTO 与发包实现参考；实际可用性以真实网关返回为准。

## 每日任务影响

`Academy_AttendSchedule` 与 `Academy_AttendFavorSchedule` 对应课程表执行，可覆盖“执行课程表”类每日任务。

## 协议列表

| 协议名 | 协议号 | 作用 | RequestClass | ResponseClass |
| --- | ---: | --- | --- | --- |
| `Academy_GetInfo` | `24000` | 课程表/日程：获取模块信息 | `AcademyGetInfoRequest` | `AcademyGetInfoResponse` |
| `Academy_AttendSchedule` | `24001` | 课程表/日程：执行日程课程 | `AcademyAttendScheduleRequest` | `AcademyAttendScheduleResponse` |
| `Academy_AttendFavorSchedule` | `24002` | 课程表/日程：执行可提升羁绊的日程 | `` | `` |

## 字段结构参考

### Academy_GetInfo

- 协议号：`24000`
- 作用：课程表/日程：获取模块信息
- RequestClass：`AcademyGetInfoRequest`
- ResponseClass：`AcademyGetInfoResponse`
- 状态：SDK 已封装并通过 live 只读验证。

#### SDK 方法

```python
academy = await client.academy.get_info()
```

返回结构：

| 字段 | 说明 |
| --- | --- |
| `academy` | 课程表账号状态数据。 |
| `locations` | 可用课程地点列表。 |
| `extra` | 服务端返回中的其他顶层字段。 |

#### Request 字段

无字段或未匹配到结构。

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `AcademyDB` | `AcademyDB?` | 课程表数据。 |
| `AcademyLocationDBs` | `List<AcademyLocationDB>?` | AcademyLocation 数据列表。 |

### Academy_AttendSchedule

- 协议号：`24001`
- 作用：课程表/日程：执行日程课程
- RequestClass：`AcademyAttendScheduleRequest`
- ResponseClass：`AcademyAttendScheduleResponse`
- 状态：SDK 已封装，调用前会先从 `Academy_GetInfo.AcademyDB.ZoneVisitCharacterDBs` 读取当天实际 `ZoneId`，并排除 `ZoneScheduleGroupRecords` 里已经执行过的 zone。当前 live：小号无可用 zone；大号有 95 个 zone、其中 7 个已执行，剩余候选 zone 调用返回 `ErrorCode=10 AccountCurrencyCannotAffordCost`，表示当前课程表票/资源不足。
#### SDK 方法

```python
result = await client.academy.attend_schedule(zone_id=zone_id)
```

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ZoneId` | `long` | 区域 ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ParcelResultDB` | `ParcelResultDB?` | 奖励或道具变更结果。 |
| `AcademyDB` | `AcademyDB?` | 课程表数据。 |
| `ExtraRewards` | `List<ParcelInfo>?` | 额外奖励列表。 |

### Academy_AttendFavorSchedule

- 协议号：`24002`
- 作用：课程表/日程：执行可提升羁绊的日程
- RequestClass：``
- ResponseClass：``
- 状态：当前 `core/data` 中没有可用 RequestClass/schema，不作为稳定 SDK API 接入。

#### Request 字段

无字段或未匹配到结构。

#### Response 字段

无字段或未匹配到结构。
