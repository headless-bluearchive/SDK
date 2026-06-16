# Attendance 协议

签到模块相关协议。

字段结构仅作为 SDK DTO 与发包实现参考；实际可用性以真实网关返回为准。

## SDK 接入方式

签到状态不再通过 `Attendance_List` / `Attendance_Check` 直发获取。当前 live 验证中这两个协议会返回错误，SDK 只从登录链路 `Account_Auth` 返回缓存里读取：

| 字段 | 说明 |
| --- | --- |
| `AttendanceBookRewards` | 签到簿奖励状态。 |
| `AttendanceHistoryDBs` | 签到历史。 |

```python
status = client.attendance.status()
```

`status()` 不发包，只读取当前登录结果或 session 中的 Attendance 缓存。旧 session 如果没有 `Account_Auth` 缓存，会返回 `available=False` 和原因说明。

```python
reward = await client.attendance.reward()
```

`reward()` / `claim()` 对应游戏签到弹窗里的领取按钮，会改变签到历史和账号资源。当前 live 结构里 `AttendanceBookRewards` 实际是签到簿数据，`AttendanceHistoryDBs.AttendedDay` 是已签到天数记录；SDK 会根据签到簿 `UniqueId / BookSize` 与历史中的最后签到日期推导今天应领取的 `Day`，再调用 `Attendance_Reward`。如果无法推导出可领取天数，SDK 会拒绝发包。

真实请求字段示例：

```python
{
    "AttendanceBookUniqueId": 1,
    "Day": 6,
    "DayByBookUniqueId": {1: 6},
}
```

## 当前结论

`Attendance_List` 与 `Attendance_Check` 目前不能作为独立发包入口直接调用。

已用持久化 session 做过 live 探针：

| 方案 | 结果 |
| --- | --- |
| session API + post-1014 AES + 默认字段 | `Protocol=-1 / ErrorCode=1` |
| session API + post-1014 AES + base defaults | `Protocol=-1 / ErrorCode=1` |
| session API + post-1014 AES + 显式 `AccountId` | `Protocol=-1 / ErrorCode=1` |
| session API + 不加请求体 AES | `Protocol=-1 / ErrorCode=500` |
| 不带 `SessionKey` | `Protocol=-1 / ErrorCode=500` |
| `Account_LoginSync.SyncProtocols` 加入 `9000/9001/9002` | 不返回 Attendance 子响应 |

因此当前判断是：封包和 post-1014 AES 通道没有问题，`Attendance_List/Check` 缺的是客户端真实 RequestClass、前置状态或当前版本入口。不要把它们封装成稳定 SDK API。

已知可用数据源是首次 `Account_Auth` 响应中的 `AttendanceBookRewards` 与 `AttendanceHistoryDBs`。后续签到模块应优先从登录结果缓存这些字段，再基于这些状态评估 `Attendance_Reward` 是否可领取。

## 协议列表

| 协议名 | 协议号 | 作用 | RequestClass | ResponseClass |
| --- | ---: | --- | --- | --- |
| `Attendance_List` | `9000` | 签到：获取列表数据 | `` | `` |
| `Attendance_Check` | `9001` | 签到：检查状态 | `` | `` |
| `Attendance_Reward` | `9002` | 签到：奖励 | `AttendanceRewardRequest` | `AttendanceRewardResponse` |

## 字段结构参考

### Attendance_List

- 协议号：`9000`
- 作用：签到：获取列表数据
- RequestClass：``
- ResponseClass：``
- 状态：待确认。当前文档无 RequestClass；live 探针返回 `Protocol=-1 / ErrorCode=1`。

#### Request 字段

无字段或未匹配到结构。

#### Response 字段

无字段或未匹配到结构。

### Attendance_Check

- 协议号：`9001`
- 作用：签到：检查状态
- RequestClass：``
- ResponseClass：``
- 状态：待确认。当前文档无 RequestClass；live 探针返回 `Protocol=-1 / ErrorCode=1`。

#### Request 字段

无字段或未匹配到结构。

#### Response 字段

无字段或未匹配到结构。

### Attendance_Reward

- 协议号：`9002`
- 作用：签到：奖励
- RequestClass：`AttendanceRewardRequest`
- ResponseClass：`AttendanceRewardResponse`
- 状态：SDK 已做安全封装和单元测试；live 领取验证通过。领取依赖 `Account_Auth` 中缓存的 `AttendanceBookRewards` 与 `AttendanceHistoryDBs`。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `DayByBookUniqueId` | `Dictionary<long, long>?` | DayByBook唯一 ID。 |
| `AttendanceBookUniqueId` | `long` | AttendanceBook唯一 ID。 |
| `Day` | `long` | 签到天数。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `AttendanceBookRewards` | `List<AttendanceBookReward>?` | 签到簿奖励。 |
| `AttendanceHistoryDBs` | `List<AttendanceHistoryDB>?` | 签到历史数据。 |
| `ParcelResultDB` | `ParcelResultDB?` | 奖励或道具变更结果。 |
