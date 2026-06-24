# 错误类型

所有异常继承自 `HeadlessBAError`。可按需捕获具体子类，或统一捕获基类 `HeadlessBAError` 做兜底。错误码以网关返回的 `ErrorCode` 为准，SDK 会尽量映射出对应的错误名称。

```python
from core.error import DailyResetSessionExpiredError, GameApiError, HeadlessBAError

try:
    result = await client.attendance.claim()
except DailyResetSessionExpiredError:
    # 跨过每日刷新点，重新登录并保存新 session
    ...
except GameApiError as exc:
    print(exc.error_code, exc.error_name, exc.protocol)
except HeadlessBAError as exc:
    print(str(exc))
```

## SDK 异常

| 异常 | 父类 | 含义 | 建议处理 |
| --- | --- | --- | --- |
| `HeadlessBAError` | `Exception` | SDK 所有自定义异常的基类。 | 统一兜底捕获。 |
| `LoginError` | `HeadlessBAError` | 登录链路相关错误基类。 | 根据子类决定是否重试或重新登录。 |
| `LoginRequiredError` | `LoginError` | 还没有登录或 restore session，就调用了需要会话的 API。 | 先 `login()` 或 `restore_session()`。 |
| `SessionRestoreError` | `LoginError` | 传入的 session 结构不可恢复，或 session 生命周期无效。 | 丢弃旧 session，重新登录。 |
| `DailyResetSessionExpiredError` | `SessionRestoreError` | session 已跨过 BA 国际服每日刷新点。默认刷新点是 `19:00 UTC`，北京时间 `03:00`。 | 必须重新登录，保存新的 `session`。 |
| `AuthenticationError` | `LoginError` | 账号认证失败或认证响应不符合预期。 | 检查账号密码、区服、网络环境。 |
| `GatewayError` | `LoginError` | 主网关登录阶段失败。 | 可重试；持续失败时检查登录链路。 |
| `ProofTokenError` | `LoginError` | ProofToken 问答或提交失败。 | 重新登录；如果持续失败，检查协议实现。 |
| `ConfigurationError` | `HeadlessBAError` | 配置缺失或配置值非法。 | 检查 `config/` 和调用参数。 |
| `RuntimeProfileError` | `HeadlessBAError` | Android runtime profile 构建或读取失败。 | 重新生成 profile，或传入合法 profile。 |
| `NetworkError` | `HeadlessBAError` | 网络请求失败。 | 检查代理、DNS、服务器状态后重试。 |
| `OfficialDataError` | `HeadlessBAError` | 官方 TableBundles / 学生数据准备失败的基类。 | 调用 `prepare_data()` 或查看子类。 |
| `OfficialDataDependencyError` | `OfficialDataError` | 本地缺少官方数据依赖，或版本不匹配。 | 登录后调用 `await client.prepare_data()`。 |
| `OfficialDataParseError` | `OfficialDataError` | 官方数据下载后解析失败。 | 检查 SQLCipher 配置、依赖库和下载完整性。 |
| `GameApiError` | `HeadlessBAError` | 网关返回 `Protocol=-1` 或业务 ErrorCode。 | 读取 `error_code` / `error_name` / `protocol` 分流处理。 |
| `ProtocolUnavailableError` | `GameApiError` | 当前协议不在 `core/data` 边界内，或没有 request 映射。 | 不要绕过 SDK 边界；确认该协议是否被项目排除。 |
| `UnsafeOperationError` | `GameApiError` | SDK 阻止了不安全或状态不足的操作。 | 先查询状态，按返回字段显式确认后再调用。 |

## GameApiError 字段

`GameApiError` 用于包装游戏网关返回的错误。

| 字段 | 说明 |
| --- | --- |
| `error_code` | 网关错误码，例如 `33004`。 |
| `error_name` | 从 `core/data/error_codes.json` 映射出的名称，例如 `SessionDuplicateLogin`。 |
| `protocol` | 响应中的协议号。错误响应常见为 `-1`。 |
| `response_keys` | 响应里出现过的字段名，只用于调试结构，不包含敏感值。 |

完整错误码名称由 `core/error_codes.py` 读取 `core/data/error_codes.json`。如果新版本出现未知错误码，`error_name` 可能为 `None`，调用方应保留原始 `error_code`。

## 常见错误码

| ErrorCode | 名称 | 常见场景 | 建议处理 |
| ---: | --- | --- | --- |
| `1` | `InvalidPacket` | 请求体字段、RequestClass、业务入口不匹配。`Attendance_List/Check` 曾在 live 下返回此错误。 | 不要盲发；检查协议文档和 SDK 封装。 |
| `500` | `ServerFailedToHandleRequest` | 请求未按 post-1014 AES/session 规则发送，或服务端无法处理。 | 检查 session、加密层、请求体结构。 |
| `1032` | `NexonNgsmValidateFail` | 需要 NGS 校验的协议未通过。live 测试中 `Mission_Reward` / `Mission_MultipleReward` 会返回此错误。 | 暂停封装为稳定可领奖入口；需要补齐 NGS 上下文后再重测。 |
| `9000` | `AttendanceInvalid` | 签到请求无效，例如当天已经领取、天数不匹配或 session 状态过旧。 | 重新 `status()`；跨日后重新登录。 |
| `22001` | `AcademyScheduleTableNotFound` | MomoTalk 羁绊剧情 schedule 不存在。 | 不要猜 schedule；使用 `client.momotalk.status()` 返回的候选。 |
| `22004` | `AcademyAlreadyAttendedFavorSchedule` | 羁绊剧情奖励已经领取。 | 刷新 `status()`，跳过该 schedule。 |
| `33004` | `SessionDuplicateLogin` | 同账号已有新登录，当前 session 被顶掉。 | 丢弃旧 session，重新登录。 |

## 处理建议

登录和会话：

```python
from core.error import DailyResetSessionExpiredError, LoginError

try:
    await client.restore_session(session, profile)
except DailyResetSessionExpiredError:
    result = await client.login(account, password)
except LoginError:
    raise
```

游戏内 API：

```python
from core.error import GameApiError, UnsafeOperationError

try:
    status = await client.momotalk.status()
except UnsafeOperationError:
    # 当前状态不足，先查询必要状态或让用户确认
    ...
except GameApiError as exc:
    if exc.error_code == 33004:
        # SessionDuplicateLogin
        ...
    elif exc.error_code == 8:
        # FailedToLockAccount
        ...
    else:
        raise
```
