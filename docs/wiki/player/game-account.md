# 账号资源

账号资源接口只读。它只告诉你现在账号里有什么，不负责持久化，也不会把会话凭证这种要命的东西吐出来给你日志污染环境。

## 同步货币

```python
from HLBA import Client

client = Client()
await client.restore_session(session, profile)

currency = await client.account.currency()
```

返回字段：

| 字段 | 说明 |
| --- | --- |
| `account_currency` | 原始 `AccountCurrencyDB`。 |
| `currency` | `CurrencyDict`，用于读取 AP、信用点、课程表票等资源数量。 |
| `update_time` | `UpdateTimeDict`。 |
| `expired_currency` | 已过期货币信息。 |
| `extra` | SDK 尚未单独命名的其它返回字段。 |

live 验证：

```text
Account_CurrencySync ok
```

这接口适合在外部 API/GUI 启动后先拉一遍，用来判断 AP、信用点、课程表票这些资源够不够。别把它当成资产审计系统，字段没单独整理出来的就先看 `extra`。
