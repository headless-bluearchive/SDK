# 账号资源和教程进度

对应游戏主界面顶部的资源栏、新号开局教程，以及账号等级奖励页。

## SDK 入口

`client.account` 下的只读方法：

| 方法 | 游戏里对应 | 参数 | 返回 |
| --- | --- | --- | --- |
| `client.account.currency()` | 资源栏货币同步（AP、青辉石、信用点、各类票券、活动货币等） | 无 | 整理后的 dict |
| `client.account.tutorial()` | 新号开局教程进度 | 无 | 整理后的 dict |
| `client.account.check_level_reward()` | 账号等级奖励页的已领取状态 | 无 | 整理后的 dict |
| `client.account.verify_adult_agree()` | 成人确认状态 | 无 | 服务端原始负载 |

`client.account` 还有一批会改账号状态的写操作（领取账号等级奖励、设置成人确认、设置老师称呼/代表学生/简介、领取绑定奖励、请求生日邮件、关闭可重复购买弹窗）。它们全部要求 `confirm=True`，统一放在 [显式确认变更页面](state-changing.md)，本页不展开。

## 返回说明

- `currency()` / `tutorial()` / `check_level_reward()` 源码里都有对应的 `format_*`，返回**整理后的 dict**：业务字段加上列表类的 `count`，未单独整理的顶层字段归入 `extra`。
- `verify_adult_agree()` 是只读握手，源码里没有 `format_*`，直接返回**服务端原始负载**（PascalCase 键）。

`extra` 不是错误。服务端经常附带 `ServerTime`、版本、活动期等额外字段，SDK 会保留但不当作稳定 API 承诺。字段名由服务端数据决定，不同区服或版本可能有差异。

### 资源栏货币

```python
currency = await client.account.currency()
ap = currency["currency"].get("ActionPoint")
credit = currency["currency"].get("Gold")
print(ap, credit)
```

`currency` 字段是服务端的 `CurrencyDict`（各资源数量），此外还可获取刷新时间和过期货币信息；未单独命名的顶层字段归入 `extra`。外部 GUI/API 启动后通常先获取一次，用于判断后续能否执行扫荡、课程表、商店购买等操作。

### 新号教程进度

```python
tutorial = await client.account.tutorial()
print(tutorial["tutorial_ids"], tutorial["count"])
```

返回已完成/已记录的教程步骤 ID 列表，常用于判断账号是否完成开局引导。该方法仅读取教程状态，不推进教程、不设置昵称、不跳过引导。

### 账号等级奖励状态

```python
state = await client.account.check_level_reward()
print(state["account_level_reward_ids"], state["count"])
```

返回当前可领取的账号等级奖励 ID 列表。这页只看状态，真正领取（`client.account.receive_level_reward(confirm=True)`）在 [显式确认变更页面](state-changing.md)。

## 注意

- 需要 `confirm=True` 的写操作必须显式传 `confirm=True`，否则抛 `UnsafeOperationError` 且不发包。
- 资源、教程、奖励 ID 一律以当前账号实际返回的数据为准，不要硬填。
- 逐协议接入状态见仓库根 [`docs/protocols.md`](../../protocols.md)。
