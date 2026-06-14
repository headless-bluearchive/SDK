# 邮件

邮件模块目前封装检查、列表和领取。不会保存邮件内容，也不会把奖励包落盘。

## 检查

```python
check = await client.mail.check()
```

返回：

| 字段 | 说明 |
| --- | --- |
| `count` | 未读或普通邮件数量，按服务端返回为准。 |
| `extra` | 其它顶层字段。 |

## 列表

```python
mails = await client.mail.list()
```

可选参数：

```python
await client.mail.list(
    is_read_mail=False,
    pivot_time=None,
    pivot_index=None,
    is_descending=True,
)
```

返回：

| 字段 | 说明 |
| --- | --- |
| `mails` | 邮件列表。 |
| `count` | 服务端返回数量，缺省时用 `mails` 长度。 |
| `extra` | 其它顶层字段。 |

## 领取

```python
result = await client.mail.receive([mail_server_id])
```

默认会先拉一次邮件列表，确认这些 `ServerId` 确实在当前列表里。你要跳过校验也能传 `validate=False`，但这就属于“我知道我在干什么”，别出错了再怪 SDK。
