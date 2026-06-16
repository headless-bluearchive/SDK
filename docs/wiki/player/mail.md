# 邮件

这一页对应游戏里的邮箱。SDK 支持查看普通邮件、查看半永久邮件，以及领取邮件奖励。查看邮件只读；领取邮件会改变账号资源，所以 SDK 会先校验当前邮箱里确实有这封邮件。

SDK 不保存邮件内容、请求包、响应包或奖励 dump，也不会把邮件奖励写成额外文件。

## 邮箱红点和数量

对应游戏主界面邮箱红点/邮箱入口上的数量提示。

```python
check = await client.mail.check()
```

不需要参数。

返回结构：

```python
{
    "count": 0,   # 服务端返回的普通邮件数量/未读数量，按当前网关语义为准
    "extra": {},
}
```

常见用法：

```python
check = await client.mail.check()
if check["count"] > 0:
    print("邮箱里有可查看邮件")
```

## 普通邮件列表

对应游戏邮箱里的普通邮件列表。列表项里通常会包含邮件的 `ServerId`、标题、时间、领取状态和奖励包信息，具体字段以服务端返回为准。

```python
mails = await client.mail.list()
```

可选参数：

```python
mails = await client.mail.list(
    is_read_mail=False,
    pivot_time=None,
    pivot_index=None,
    is_descending=True,
)
```

参数说明：

| 参数 | 游戏含义 |
| --- | --- |
| `is_read_mail` | 是否查看已读邮件；`False` 更接近游戏里优先看未读/未领取邮件。 |
| `pivot_time` | 翻页游标时间，通常来自上一页返回。 |
| `pivot_index` | 翻页游标序号，通常来自上一页返回。 |
| `is_descending` | 是否按时间倒序。 |
| `sorting_rule` | 服务端排序规则；一般不需要手动传。 |

返回结构：

```python
{
    "mails": [...],  # 邮件列表，对应 MailDBs
    "count": 0,      # 服务端 Count，缺省时用 mails 长度
    "extra": {},
}
```

常见用法：

```python
mails = await client.mail.list(is_read_mail=False)
for mail in mails["mails"]:
    print(mail.get("ServerId"), mail.get("Title"))
```

## 领取普通邮件

对应游戏里选中普通邮件后点击领取。需要使用邮件列表里的 `ServerId`。

```python
result = await client.mail.receive([mail_server_id])
```

参数说明：

| 参数 | 游戏含义 |
| --- | --- |
| `mail_server_ids` | 要领取的普通邮件 `ServerId` 列表。 |
| `validate` | 默认 `True`，SDK 会先重新读取邮箱列表，确认这些邮件还在当前邮箱里。 |

返回结构：

```python
{
    "mail_server_ids": [...],   # 服务端确认处理的邮件 ServerId
    "parcel_result": {...},     # 奖励领取后的资源/物品变化
    "battle_pass_info": [...],  # 如果邮件影响战斗通行证，会出现在这里
    "extra": {},
}
```

默认校验能挡住“拿过期邮件 ID 直接发领取”的误用。只有在你已经从同一账号、同一会话的邮箱列表里拿到 ID，并确认业务逻辑安全时，才考虑 `validate=False`。

## 半永久邮件列表

对应游戏邮箱里的半永久/特殊保管邮件页面。它和普通邮件不是同一个领取入口。

```python
mails = await client.mail.list_semi_permanent()
```

可选参数与普通邮件列表一致。

返回结构：

```python
{
    "mails": [...],  # 半永久邮件列表
    "count": 0,
    "extra": {},
}
```

## 领取半永久邮件

对应游戏里领取半永久邮件。这里使用的是半永久邮件里的 `MailDBId`，不是普通邮件的 `ServerId`。如果该邮件带 `ProductId`，可以一起传入。

```python
result = await client.mail.receive_semi_permanent(
    mail_db_id,
    product_id=product_id,
)
```

返回结构：

```python
{
    "mail_db_id": 0,
    "parcel_result": {...},
    "applied_monthly_product_purchase": {...},
    "applied_daily_record": {...},
    "applied_battle_pass_product_purchase": {...},
    "applied_battle_pass_info": {...},
    "battle_pass_info": [...],
    "extra": {},
}
```

默认会先调用 `list_semi_permanent()` 确认邮件存在。当前账号没有半永久邮件时，SDK 不会盲发领取请求。
