# 签到

这一页对应游戏登录时弹出的普通签到、活动签到奖励页面。SDK 不直接硬发签到列表/检查协议，而是复刻客户端实际流程：登录后从 `Account_Auth` 返回的签到缓存里读取签到簿和签到历史，再推导今天是否有可领取奖励。

## 签到弹窗状态

对应游戏里今天能不能领签到、当前是第几天、有哪些活动签到簿。

```python
status = client.attendance.status()
```

不需要 `await`，因为它读取的是当前 `Client` 内存里的登录缓存。

返回结构：

```python
{
    "available": True,                 # 当前会话里是否有签到缓存
    "source": "Account_Auth",          # 数据来源
    "attendance_book_rewards": [...],  # 签到簿，普通签到和活动签到都在这里
    "attendance_history": [...],       # 已签到历史
    "claimable_rewards": [...],        # SDK 推导出的当前可领取签到
}
```

如果 `available=False`，说明当前 session 没有签到缓存。不要盲发领取请求；重新登录或恢复包含签到缓存的 session。

常见用法：

```python
status = client.attendance.status()
for item in status["claimable_rewards"]:
    print(item["AttendanceBookUniqueId"], item["Day"])
```

## 领取签到奖励

对应游戏里在签到弹窗点击领取。它会改变账号资源和签到历史。

```python
result = await client.attendance.claim()
```

如果同时存在普通签到和活动签到，建议按 `claimable_rewards` 逐个指定，避免 SDK 无法判断你想领哪一本签到簿：

```python
for item in client.attendance.status()["claimable_rewards"]:
    result = await client.attendance.claim(
        attendance_book_unique_id=item["AttendanceBookUniqueId"],
        day=item["Day"],
        day_by_book_unique_id=item["DayByBookUniqueId"],
    )
```

参数说明：

| 参数 | 游戏含义 |
| --- | --- |
| `attendance_book_unique_id` | 签到簿 ID，来自 `claimable_rewards`。 |
| `day` | 要领取的签到天数。 |
| `day_by_book_unique_id` | 服务端需要的签到簿到天数映射，直接使用 `claimable_rewards` 里的值。 |

返回结构：

```python
{
    "attendance_book_rewards": [...],  # 更新后的签到簿
    "attendance_history": [...],       # 更新后的签到历史
    "parcel_result": {...},            # 奖励领取结果
    "extra": {},
}
```

领取成功后 SDK 会更新当前 `Client` 内存里的 attendance cache，但不会替调用方写回 `session.json`。如果调用方要持久化，需要保存更新后的 `client.session`。

live 验证：

```text
普通签到 Day=1 ok
活动签到 UniqueId=90026 Day=5 ok
```
