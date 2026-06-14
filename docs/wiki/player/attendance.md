# 签到

签到不是 `Attendance_List` / `Attendance_Check` 直接硬发。那两个 live 下会给你甩脸色，SDK 现在走的是客户端真实用法：登录时从 `Account_Auth` 缓存里拿 `AttendanceBookRewards` 和 `AttendanceHistoryDBs`，再推导今天该领哪一天。

## 状态

```python
status = client.attendance.status()
```

返回重点：

| 字段 | 说明 |
| --- | --- |
| `available` | 当前 session 里有没有签到缓存。 |
| `attendance_book_rewards` | 签到簿。普通签到、活动签到都在这里。 |
| `attendance_history` | 已签到历史。 |
| `claimable_rewards` | SDK 推导出的当前可领取签到。 |

如果 `available=False`，别硬发包。重新登录，把新的 `session` 保存下来。

## 领取

```python
result = await client.attendance.claim()
```

如果同时有普通签到和活动签到，外部可以按 `claimable_rewards` 里的字段逐个指定：

```python
for item in client.attendance.status()["claimable_rewards"]:
    await client.attendance.claim(
        attendance_book_unique_id=item["AttendanceBookUniqueId"],
        day=item["Day"],
        day_by_book_unique_id=item["DayByBookUniqueId"],
    )
```

live 验证：

```text
普通签到 Day=1 ok
活动签到 UniqueId=90026 Day=5 ok
```

领取成功后 SDK 会更新当前 `Client` 内存里的 attendance cache，但不会替你写回 `session.json`。要持久化就保存 `client.session`，不然下次你读的还是旧缓存。
