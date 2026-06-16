# 账号资源和教程进度

这一页对应游戏主界面顶部资源栏、仓库里的资源数量，以及新号教程进度。它只读取账号当前状态，不修改账号，不保存会话凭证，也不会把 session/profile/token 等敏感值写到日志里。

## 资源栏和货币同步

对应游戏里能看到的 AP、青辉石、信用点、课程表票、活动货币等资源状态。外部 GUI/API 启动后通常先拉一次，用来判断后续是否能执行扫荡、课程表、商店购买等操作。

```python
currency = await client.account.currency()
```

不需要参数。

返回结构：

```python
{
    "account_currency": {...},  # 原始 AccountCurrencyDB
    "currency": {...},          # CurrencyDict，AP/信用点/票券等资源数量
    "update_time": {...},       # UpdateTimeDict，各资源刷新时间
    "expired_currency": {...},  # 已过期或即将过期货币信息
    "extra": {...},             # SDK 尚未单独命名的其它字段
}
```

常见用法：

```python
currency = await client.account.currency()
ap = currency["currency"].get("ActionPoint")
credit = currency["currency"].get("Gold")
print(ap, credit)
```

字段名由服务端数据决定，不同区服或版本可能存在差异；没被 SDK 单独整理出来的顶层字段会保留在 `extra`。

live 验证：

```text
Account_CurrencySync ok
```

## 新号教程进度

对应新账号进入游戏时的教程步骤。这个状态常用于判断账号是否已经走完开局引导，或者外部工具是否应该提示用户先在游戏里完成教程。

```python
tutorial = await client.account.tutorial()
```

返回结构：

```python
{
    "tutorial_ids": [...],  # 已完成或已记录的教程步骤 ID
    "count": 0,
    "extra": {},
}
```

这个方法只读取教程状态，不推进教程、不设置昵称、不跳过引导。
