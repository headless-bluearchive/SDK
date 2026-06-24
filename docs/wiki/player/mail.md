# 邮件

对应游戏里的邮箱。能看邮箱红点 / 数量、普通邮件列表、半永久（特殊保管）邮件列表；能做的是领取普通邮件和领取半永久邮件。查看是只读的；领取会改变账号资源，属于写操作。

邮件模块没有 `confirm` 守卫，领取动作由 `validate`（默认先重新核对邮箱）把关。

## SDK 入口

所有方法均为异步方法。

| 方法 | 用途 | 类型 |
| --- | --- | --- |
| `check()` | 读邮箱红点 / 普通邮件数量 | 只读 |
| `list(is_read_mail=…, pivot_time=…, pivot_index=…, is_descending=…, sorting_rule=…)` | 读普通邮件列表（支持翻页游标） | 只读 |
| `receive(mail_server_ids, validate=True)` | 领取普通邮件（按列表里的 `ServerId`） | 写（`validate` 守卫） |
| `list_semi_permanent(…)` | 读半永久邮件列表（参数同 `list`） | 只读 |
| `receive_semi_permanent(mail_db_id, product_id=…, validate=True)` | 领取半永久邮件（按 `MailDBId`） | 写（`validate` 守卫） |

`list` / `list_semi_permanent` 的参数都是可选的：`is_read_mail` 控制是否看已读邮件（`False` 更接近游戏里优先看未读 / 未领取），`pivot_time` / `pivot_index` 是来自上一页的翻页游标，`is_descending` 控制时间倒序，`sorting_rule` 一般不用手动传。

```python
check = await client.mail.check()
if check["count"] > 0:
    mails = await client.mail.list(is_read_mail=False)
    server_ids = [m["ServerId"] for m in mails["mails"]]
    result = await client.mail.receive(server_ids)
```

## 返回说明

所有方法都经 `format_*` 整理，返回整理后的 dict：

- `check`：`count`（普通邮件 / 未读数量，按当前网关语义）+ `extra`。
- `list` / `list_semi_permanent`：`mails` 列表 + `count` + `extra`。列表项仍是服务端原始邮件 DB dict，通常含 `ServerId` / `MailDBId`、标题、时间、领取状态和奖励包信息。
- `receive`：已处理的 `mail_server_ids`、`parcel_result`（领取后的资源 / 物品变化）、可能的 `battle_pass_info`，以及 `extra`。
- `receive_semi_permanent`：`mail_db_id`、`parcel_result`，若干 `applied_*` 应用结果（月卡 / 每日记录 / 通行证等）和 `extra`。

具体键名以服务端返回为准，这里只描述形状。

## 注意

- 邮件模块没有 `confirm` 守卫；写操作由 `validate`（默认 `True`）把关：领取前会先重新读取对应邮箱列表，确认目标 `ServerId` / `MailDBId` 还在当前邮箱里，否则抛 `UnsafeOperationError` 且不发包。只有你已从同一账号、同一会话的邮箱列表里拿到 ID 并确认安全，才考虑 `validate=False`。
- 普通邮件用列表里的 `ServerId`；半永久邮件用 `MailDBId`（带 `ProductId` 时一并传）。两者是不同的领取入口，不要混用。
- 邮件 ID 一律来自当前邮箱列表，不要手填。当前账号没有半永久邮件时，SDK 不会盲发领取请求。

---

逐协议接入状态见 [协议总表](../../protocols.md)。
