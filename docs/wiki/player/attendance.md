# 签到页面

这一页对应游戏登录时弹出的普通签到 / 活动签到奖励页。SDK 不单独请求签到列表协议，而是复刻客户端流程：登录时 `Account_Auth` 已带回签到簿和签到历史缓存，`status()` 据此推导当天是否有可领签到，`claim()` 负责领取。

能看什么：当前会话里有没有签到缓存、有哪些签到簿、已签到历史、SDK 推导出的当前可领项。
能做什么：领取一项可领签到（会改账号资源和签到历史）。

## SDK 入口

| 方法 | 用途 | confirm |
| --- | --- | --- |
| `client.attendance.status()` | 读当前会话内存里的签到缓存并推导可领项；不发包、不需 `await`。 | 否 |
| `client.attendance.claim(...)` | 领取一项可领签到；改账号资源和签到历史。`reward` 是同一方法的别名。 | 否（守卫是缓存+可领项，见下） |

`claim` 与 `reward` 指向同一个函数，签名为 `reward(*, attendance_book_unique_id=None, day=None, day_by_book_unique_id=None)`。

## 查看签到状态

```python
status = client.attendance.status()
```

`status()` 读取当前 `Client` 内存里的登录缓存，不需要 `await`。

返回 SDK 整理后的 dict：业务字段（`available` / `source` / 签到簿 / 签到历史 / SDK 推导出的 `claimable_rewards`）。缓存缺失时 `available=False` 并附带 `reason`，签到相关列表为空。

```python
status = client.attendance.status()
for item in status["claimable_rewards"]:
    print(item["AttendanceBookUniqueId"], item["Day"])
```

`available=False` 表示当前 session 没有签到缓存。此时不要发起领取请求，应重新登录或恢复包含签到缓存的 session。

## 领取签到奖励

对应在签到弹窗点击领取，会修改账号资源和签到历史。

```python
result = await client.attendance.claim()
```

同时存在普通签到和活动签到时，逐项按 `claimable_rewards` 指定，避免 SDK 无法判断要领哪一本签到簿：

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
| `day_by_book_unique_id` | 服务端需要的"签到簿到天数"映射，直接用 `claimable_rewards` 里的值。 |

返回 SDK 整理后的 dict：更新后的签到簿、签到历史、`parcel_result`（奖励领取结果）和 `extra`（其余原始字段）。领取成功后 SDK 会更新当前 `Client` 内存里的 attendance 缓存，但不会替调用方写回 `session.json`；如需持久化，由调用方自行保存更新后的 `client.session`。

## 注意

- `claim()` 没有 `confirm` 参数，安全守卫是 `status()` 缓存加可领项匹配：缓存不可用、或没有与请求字段匹配的可领项时直接抛 `UnsafeOperationError` 且不发包。多本签到簿同时可领且未指定具体 `attendance_book_unique_id` + `day` 时，同样拒绝执行。
- 签到簿 ID、天数等一律来自 `status()["claimable_rewards"]`，不要手填。
- 逐协议接入状态见仓库根 `docs/protocols.md`。
