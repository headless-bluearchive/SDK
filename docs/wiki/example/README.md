# 示例代码

可直接运行或复制使用的完整示例。

- [complete_daily_tasks.py](complete_daily_tasks.py) — **完成每日任务的整套流程**：每日签到、扫图、咖啡厅摸头/领币/邀请、课程表、悬赏通缉扫荡、制造、社团领体力（进社团→邮箱领）、总力战扫荡+领奖、综合战术考试扫荡、学园交流会扫荡，最后统一领取已完成的每日任务奖励。每一步都使用当前 SDK 中真实存在的方法，并附逐步注释。涉及实战的部分（活动关卡、总力战开荒、竞技场）按公平边界不代打，仅打印“自己上号”提示。

## 运行方式
脚本**自带登录**（内置了 `cli-api/login_instance.py` 的流程），无需先手动登录。

首次（用账号密码登录，会自动将 session/profile 落盘，之后复用）：
```bash
set HLBA_NX_ID=你的Nexon邮箱
set HLBA_NX_PASSWORD=你的Nexon密码
set HLBA_REGION=tw                         # 默认 auto 自动探测；知道区服就直接填(tw/global/kr/asia/na)，更快、不卡
set HLBA_PROXY=http://127.0.0.1:60808      # 按需，留空则直连；设 system 自动识别 Clash/V2Ray 系统代理
python docs/wiki/example/complete_daily_tasks.py
```
之后再次运行：已有 session 文件会**直接 restore 恢复**（更快，且无需再次通过 Nexon 登录校验）；会话过期或设置 `HLBA_FORCE_LOGIN=1` 时自动重新登录。可用 `HLBA_SESSION` / `HLBA_PROFILE` 自定义会话文件路径。

推荐用法：脚本中**先显式创建 `client = Client(region=, proxy=, timeout=, debug=)`，再用该 client 贯穿全流程**——代理只需一处配置，登录链路 / 游戏网关 / 数据同步全程复用。复制使用时建议沿用此结构。

注意：
- ⚠️ 脚本会对账号执行**真实操作**（消耗 AP/扫荡券、领取奖励等），所有写操作内部已 `confirm=True`。
- 全新登录可能被 Nexon 安全校验（ProofToken 等）拦截；若被拦截，先手动登录获取 session 文件，脚本会走 restore 路径。
- session/profile 含登录凭证，请妥善保存，请勿提交到公开仓库。

## 登录卡住或长时间无响应
排查顺序：
1. **区服（region）**：本示例默认 `HLBA_REGION=auto`，会逐个区服尝试、第一个成功的即为正确区服（错误区服会快速报错、不死等，按系统语言把最可能的排前面）。知道区服就直接显式填 `tw/global/kr/asia/na`，更快。
2. **开启调试定位卡点**：`set HLBA_DEBUG=1` 后运行，会实时打印 `[HLBA] ...` 每步日志；**最后一行即为卡住的步骤**（卡在 `Queuing_*` 多半就是区服不对）。
3. **确认代理可用**：脚本启动会打印“使用代理: ...”。确认该端口的代理**正在运行**且端口正确（Clash 常为 `7890`、V2Ray 常为 `10809`，若不是 `60808` 则相应修改，或直接用 `HLBA_PROXY=system` 自动识别）。代理未开启或端口错误时，每一步都会等待至超时。
4. **卡在获取版本号**：登录第一步会从 **Samsung Galaxy Store** 在线获取最新客户端版本；代理无法连通 Samsung 时会卡在此处。可设置 `HLBA_CLIENT_VERSION=<版本号>` 跳过该在线获取步骤。
5. **`TIMEOUT` 不要设得过小**：默认示例中 `HLBA_TIMEOUT` 较小，网络较慢时会过早超时；可适当调大（如 120）。
6. **出现“已用现有会话恢复”即表示登录已成功**（走的是 restore 快路径，不会打印“登录成功”），随后会依次打印每个任务的 `[完成]/[跳过]`。
7. 全新登录被 Nexon ProofToken 拦截时会**报错**（而非卡住）；此时先手动登录获取 session，让脚本走 restore 路径。

参数取值（content 枚举、各 ID 来源）见 [参数取值参考](../reference.md)；逐任务说明见 [显式确认变更页](../player/state-changing.md) 与 [扫荡页](../player/sweep.md)；代理与 `proxy="system"` 见 [登录鉴权页](../base/auth.md)。
