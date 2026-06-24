# 登录鉴权

本页对应“打开游戏并登录到大厅”这一步：使用 Nexon 账号密码登录，获取玩家摘要、设备 `profile` 和会话 `session`。后续所有游戏功能页都依赖该 `session`。

`SDK` 是纯 Python SDK。外部项目先实例化 `Client`，再调用实例方法。

## SDK 入口

| 入口 | 用途 |
| --- | --- |
| `Client(region="tw", **defaults)` | 创建客户端；`defaults` 透传给登录链路（常用 `proxy` / `timeout` / `android_mobile_profile`），`debug=True` 打开底层日志，`language=` 控制报错语言（默认按系统语言） |
| `await client.login(account, password)` | Nexon 账号密码登录，返回 `LoginResult` 并在内部恢复网关会话 |
| `await client.restore_session(session, profile=None)` | 用已保存的 `session` 恢复会话，免重新登录 |
| `client.profile` / `client.session` | 读取当前 `profile` / `session`，未登录时抛 `LoginRequiredError` |
| `await client.refresh_student_data()` | 刷新学生名表缓存，返回 `{学生ID: 名称}` |
| `await client.aclose()` | 关闭底层网关连接，用完建议调用 |

> `clie nt.credentials` 不暴露任何凭证，访问会直接抛 `LoginRequiredError`。

## 登录

```python
from HLBA import Client

client = Client(region="tw")
result = await client.login("account@example.com", "password")
```

`region` 取账号所在服：`kr` / `tw` / `asia` / `na` / `global`。填错区服登录会卡在排队队列（错误区服通常会快速抛 `GatewayError`），所以填对很重要。

**自动探测区服**：`region` 留空或填 `"auto"` 时，全新登录会**逐个区服尝试**，第一个登录成功的即为该账号所在服。错误区服在排队步骤会快速抛 `GatewayError`、立即换下一个；凭证错误、ProofToken 等非区服错误会直接抛出（不被掩盖）。尝试顺序按系统语言把最可能的区服排到最前。

```python
client = Client(region="auto")   # 不确定区服时让它自己试（首个成功的即为该号所在服）
```

> 为什么不并发：Nexon 对**同一账号的并发登录**会回 `errorCode=2001 (ID/password error)`，所以只能串行。好在错误区服是快速报错、不死等，整体不慢。**知道区服就直接显式填**最快。`restore_session(...)` 不需要探测——区服信息已在 `session` 的网关 URL 里（`region_from_session()` 可反推）。

需要代理时只传一个 `proxy`，TOYSDK 和主游戏网关共用同一配置（登录链路、网关发包、官方数据/学生名同步都会走它）：

```python
client = Client(region="tw", proxy="http://127.0.0.1:60808")   # 显式 host:port
client = Client(region="tw", proxy="socks5://127.0.0.1:7891")  # 也支持 socks（需 requests[socks]）
```

**自动探测系统代理**：传 `proxy="system"`（或 `"auto"`），由 SDK 读取系统/环境中的代理配置——
覆盖环境变量 `HTTPS_PROXY`/`HTTP_PROXY`/`ALL_PROXY`、系统代理设置（Windows 注册表，
即 **Clash / V2Ray 开启「系统代理 / Set as system proxy」时写入的 host:port**），以及
「自动配置脚本」(PAC) 的尽力解析。本地代理统一按 `http://host:port` 连接。

```python
client = Client(region="tw", proxy="system")   # Clash/V2Ray 开了系统代理就自动识别
```

> 探测不到时（未开启系统代理，或只配置了 PAC 且脚本取不到固定 host:port）会抛 `ConfigurationError`
> 并给出处理提示；PAC 仅尽力解析，必要时设置环境变量 `HLBA_PAC_URL` 指定脚本地址，或直接显式传 `proxy=host:port`。

需要保留底层调试结果时启用 `debug`：

```python
client = Client(region="tw", debug=True)
```

启用后会在登录过程中打印 `[HLBA] ...` 日志，并把同样的日志放到 `result.logs`。

## 报错语言（多语言）

SDK 面向用户的报错/提示会**按系统语言**自动切换：中文系统（简体中文 / 港澳台，即 `zh-*`）输出中文，其它地区输出英文。无需任何配置。

需要时可显式指定：

```python
client = Client(region="tw", language="zh")    # 强制中文
client = Client(region="tw", language="en")    # 强制英文
client = Client(region="tw", language="auto")  # 默认：按系统语言（等于不传）
```

也可用环境变量 `HLBA_LANG=zh|en` 覆盖，或在代码里：

```python
from core.i18n import set_language
set_language("en")   # 传 None / "auto" 恢复按系统自动判断
```

> 本地化覆盖的是 **SDK 自己产生的文本**（confirm 守卫、登录 / 区服 / 代理 / 协议等报错与提示）。游戏服务器返回的业务数据字段（如 `StageUniqueId`、`Nickname`）是游戏定义的，不在翻译范围内。

## 登录结果

`result` 是 `LoginResult`，默认包含完整字段摘要，可直接打印：

```python
print(result)
```

输出（下方为占位示例值，非真实账号）：

```text
[AccountId: 10000001, Nickname: Sensei, Level: 1, Exp: 0, FriendCode: ABCDEFGH, PublisherAccountId: 20790000000000000]
```

也可以直接读取字段：

```python
result.account_id
result.nickname
result.level
result.exp
result.friend_code
result.publisher_account_id
result.billing
result.profile
result.session
```

需要字典时：

```python
result.to_dict()
```

## profile 与 session

`profile` 是 Android 设备和运行态信息，调用方可以保存后下次传回 `Client`，避免每次都生成新设备特征：

```python
client = Client(region="tw", android_mobile_profile=saved_profile)
```

`session` 是后续游戏内发包需要的会话状态，包含 `SessionKey`、`AccountId`、网关 URL、AES/O22 key material 和 cookies。SDK 只返回这份数据，不负责保存。

如果当前登录链路带出了充值与购买状态快照，还会同步写入 `result.billing`，并在 `session["billing"]` 里保留同一份整理后的状态。它对应的是游戏里充值页、月卡页和购买记录页看到的内容，不是支付入口。

## 每日刷新与会话过期

SDK 会在 `session` 中写入 `session_lifecycle`，用于记录本次登录所在的每日刷新日。国际服每日刷新时间按 `19:00 UTC` 计算，等同于北京时间 `03:00`。如果调用方在跨过每日刷新后继续 `restore_session()` 或调用游戏内 API，SDK 会抛出 `DailyResetSessionExpiredError`，调用方应重新登录并保存新的 `session`。

## 持久化

`session` / `profile` 是否持久化由调用方决定，SDK 不负责落盘。落盘到文件示例：

```python
import json
from pathlib import Path

runtime = Path("runtime")
runtime.mkdir(exist_ok=True)
runtime.joinpath("profile.json").write_text(json.dumps(result.profile, ensure_ascii=False, indent=2), encoding="utf-8")
runtime.joinpath("session.json").write_text(json.dumps(result.session, ensure_ascii=False, indent=2), encoding="utf-8")
```

下次启动用 `restore_session()` 恢复，不必再次登录：

```python
session = json.loads(Path("runtime/session.json").read_text(encoding="utf-8"))
profile = json.loads(Path("runtime/profile.json").read_text(encoding="utf-8"))

client = Client(region="tw")
await client.restore_session(session, profile)
```

## 当前流程

1. 调用方提供 Nexon 账号和密码，也可以额外传入已持久化的 `android_mobile_profile`。
2. Android TOYSDK HTTP 直登获取 `npSN`、`npToken`、`npaCode` 等凭证。
3. 主游戏网关执行 `Queuing_GetTicket` 和 `Account_CheckNexon`。
4. 应用 1014 后的 SessionKey、O22 key/iv 语义和请求体 AES 层。
5. 执行 ProofToken、`Account_Auth`、`Account_LoginSync`。
6. 返回玩家摘要、`profile` 和 `session`，由调用方决定是否持久化。
