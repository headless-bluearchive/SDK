# 登录鉴权

`SDK` 是纯 Python SDK。外部项目先实例化 `Client`，再调用实例方法。

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
result.profile
result.session
```

`profile` 是 Android 设备和运行态信息，调用方可以保存后下次传回 `Client`，避免每次都生成新设备特征：

```python
client = Client(region="tw", android_mobile_profile=saved_profile)
```

`session` 是后续游戏内发包需要的会话状态，包含 `SessionKey`、`AccountId`、网关 URL、AES/O22 key material 和 cookies。SDK 只返回这份数据，不负责保存，也不要把它完整打到日志里。

SDK 会在 `session` 中写入 `session_lifecycle`，用于记录本次登录所在的每日刷新日。国际服每日刷新时间按 `19:00 UTC` 计算，等同于北京时间 `03:00`。如果调用方在跨过每日刷新后继续 `restore_session()` 或调用游戏内 API，SDK 会抛出 `DailyResetSessionExpiredError`，调用方应重新登录并保存新的 `session`。

调用方自行持久化示例：

```python
import json
from pathlib import Path

runtime = Path("runtime")
runtime.mkdir(exist_ok=True)
runtime.joinpath("profile.json").write_text(json.dumps(result.profile, ensure_ascii=False, indent=2), encoding="utf-8")
runtime.joinpath("session.json").write_text(json.dumps(result.session, ensure_ascii=False, indent=2), encoding="utf-8")
```

需要字典时：

```python
result.to_dict()
```

## 当前流程

1. 调用方提供 Nexon 账号和密码，也可以额外传入已持久化的 `android_mobile_profile`。
2. Android TOYSDK HTTP 直登获取 `npSN`、`npToken`、`npaCode` 等凭证。
3. 主游戏网关执行 `Queuing_GetTicket` 和 `Account_CheckNexon`。
4. 应用 1014 后的 SessionKey、O22 key/iv 语义和请求体 AES 层。
5. 执行 ProofToken、`Account_Auth`、`Account_LoginSync`。
6. 返回玩家摘要、`profile` 和 `session`，由调用方决定是否持久化。
