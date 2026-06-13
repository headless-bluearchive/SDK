# 登录鉴权

`backend` 是纯 Python SDK。外部项目先实例化 `Client`，再调用实例方法。

```python
from HLBA import Client

client = Client(region="tw")
result = await client.login("account@example.com", "password")
```

需要代理时只传一个 `proxy`，TOYSDK 和主游戏网关共用同一配置：

```python
client = Client(region="tw", proxy="http://127.0.0.1:60808")
```

需要保留底层调试结果时启用 `debug`：

```python
client = Client(region="tw", debug=True)
```

启用后会在登录过程中打印 `[HLBA] ...` 日志，并把同样的日志放到 `result.logs`。

`result` 默认就是完整字段摘要，可以直接打印：

```python
print(result)
```

输出：

```text
[AccountId: 17817937, Nickname: fqka, Level: 2, Exp: 2, FriendCode: AKWWMTWQ, PublisherAccountId: 20790000036661420]
```

也可以直接读取字段：

```python
result.account_id
result.nickname
result.level
result.exp
result.friend_code
result.publisher_account_id
result.credentials
```

需要字典时：

```python
result.to_dict()
```

## 当前流程

1. 调用方只提供 Nexon 账号和密码。
2. Android TOYSDK HTTP 直登获取 `npSN`、`npToken`、`npaCode` 等凭证。
3. 主游戏网关执行 `Queuing_GetTicket` 和 `Account_CheckNexon`。
4. 应用 1014 后的 SessionKey、O22 key/iv 语义和请求体 AES 层。
5. 执行 ProofToken、`Account_Auth`、`Account_LoginSync`。

## SDK 边界

- 不解析 CLI 参数。
- 不启动 REST 服务。
- 不弹窗。
- 不调用 `input()`。
- 不保存请求、响应、packet、payload 等调试产物。
- 仅持久化 Android 设备 profile，用于保持设备身份稳定。
- 不暴露调试期入口参数。
- 异常直接抛出，由调用方决定如何处理。
