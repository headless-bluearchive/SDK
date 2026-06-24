"""完成 Blue Archive 每日任务 —— 可直接运行的示例脚本。

演示「能用 SDK 自动完成的每日任务」整套流程，每一步都用当前 SDK 真实存在的方法：

    每日签到 · 扫图 · 咖啡厅摸头/领币/邀请 · 课程表 · 悬赏通缉扫荡 ·
    制造 · 社团领体力(进社团→邮箱领) · 总力战扫荡+领奖 · 战术考试扫荡 ·
    学园交流会扫荡 · 最后领取已完成的每日任务奖励

**不做（公平边界，必须自己上号实战）**：活动关卡、总力战开荒、竞技场——
这些是战斗进入/结算，SDK 不提供（竞技场是确定性 seeded 战斗 + 服务器 HashKey 校验，
绕不开战斗引擎）。脚本里这几项只打印提示。

────────────────────────────────────────────────────────────────────
运行方式（脚本自带登录，内置了 cli-api/login_instance.py 的流程）
  - 首次：设 HLBA_NX_ID / HLBA_NX_PASSWORD（Nexon 账号密码），脚本会登录并把 session/profile
    落盘到 SESSION_PATH/PROFILE_PATH，然后自动跑每日任务。
  - 之后：已有 session 文件时直接 restore 恢复（快，且不必再过 Nexon 登录关卡）；
    会话过期或设了 HLBA_FORCE_LOGIN=1 时自动改用账号密码重新登录。
  - 按需设 HLBA_PROXY（所有请求都会走它）、HLBA_REGION（要与账号所在服一致）。
  - ⚠️ 本脚本会对账号执行真实操作（消耗 AP/扫荡券、领取奖励等）。
  - 注意：全新登录可能被 Nexon 安全校验（ProofToken 等）拦截；若被拦，可先手动登录拿到
    session 文件，再让脚本走 restore 路径。

约定（贯穿整个 SDK）
  - 会改状态/消耗资源的写操作都必须显式 `confirm=True`，否则抛 UnsafeOperationError 且不发包。
  - 关卡/槽位/角色等 ID 一律从对应的 list()/get() 读出来，绝不手填。
  - 扫荡只对**已通关**的关卡有效（困难图通常要 3 星才解锁扫荡）。
  - content 枚举值见 docs/wiki/reference.md：主线=1、悬赏(日常副本)=3、学园交流会=8。
────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
from getpass import getpass
from pathlib import Path

# 让脚本能 import 到 SDK 根：docs/wiki/example/ 往上 3 层就是 SDK 根目录
SDK_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(SDK_ROOT))

from HLBA import Client  # noqa: E402
from core.error import DailyResetSessionExpiredError  # noqa: E402
from utils.proxy import redact_proxy_url  # noqa: E402

# ── 配置 ───────────────────────────────────────────────────────────
_DEFAULT_DIR = SDK_ROOT.parent
SESSION_PATH = os.environ.get("HLBA_SESSION", str(_DEFAULT_DIR / "session.json"))
PROFILE_PATH = os.environ.get("HLBA_PROFILE", str(_DEFAULT_DIR / "profile.json"))
REGION = os.environ.get("HLBA_REGION", "auto")  # auto=自动探测区服（首次全新登录会逐个区服试、较慢；知道就直接填 tw/global/kr/asia/na 更快、不会卡）
PROXY = os.environ.get("HLBA_PROXY", "")  # 例如 "http://127.0.0.1:60808 或者 127.0.0.1:60808"，留空则直连，可能会因为神秘原因导致超时或无法登录，建议使用代理。
TIMEOUT = float(os.environ.get("HLBA_TIMEOUT", "30"))
NX_ID = os.environ.get("HLBA_NX_ID", "")            # Nexon 邮箱（没有会话文件时用来登录）
NX_PASSWORD = os.environ.get("HLBA_NX_PASSWORD", "")  # Nexon 密码
FORCE_LOGIN = os.environ.get("HLBA_FORCE_LOGIN", "").strip().lower() in {"1", "true", "yes", "on"}
DEBUG = os.environ.get("HLBA_DEBUG", "").strip().lower() in {"1", "true", "yes", "on"}  # 打印 [HLBA] 每步日志
# 显式指定客户端版本可跳过登录时从 Galaxy Store 在线取版本号那一步（代理到不了 Samsung 时会卡在那）
CLIENT_VERSION = os.environ.get("HLBA_CLIENT_VERSION", "").strip()

# ContentType 枚举（SDK 未内置常量，取值见 docs/wiki/reference.md）
CONTENT_CAMPAIGN_MAIN = 1   # 主线（普通/困难由 stage_id 区分）
CONTENT_WEEK_DUNGEON = 3    # 悬赏通缉 / 日常副本
CONTENT_SCHOOL_DUNGEON = 8  # 学园交流会


# ── 小工具：让单个任务失败不影响整体流程 ──────────────────────────
async def run_task(name: str, coro):
    """运行一个每日任务；失败（关卡未通关/功能未开放/无可领项等）只跳过、不中断。"""
    try:
        await coro
        print(f"[完成] {name}")
    except Exception as exc:  # noqa: BLE001 - 示例里统一兜底，打印原因即可
        print(f"[跳过] {name} —— {type(exc).__name__}: {exc}")


# ── 各每日任务 ─────────────────────────────────────────────────────
async def daily_attendance(client: Client) -> None:
    """每日签到：领取当前所有可领的签到。

    account 可能同时有多本签到簿可领，不带参的 claim() 会因歧义拒绝；这里从
    status() 的 claimable_rewards 里逐本按 (book_id, day) 显式领取。
    """
    claimable = client.attendance.status().get("claimable_rewards") or []
    if not claimable:
        raise RuntimeError("当前没有可领的签到")
    for r in claimable:
        await client.attendance.reward(
            attendance_book_unique_id=r["AttendanceBookUniqueId"],
            day=r["Day"],
        )


async def sweep_campaign(client: Client, times: int = 1) -> None:
    """扫图：对已通关的主线关卡执行扫荡（消耗扫荡券/AP）。"""
    campaign = await client.campaign.list()
    # stage_history 里每条是关卡记录；Star1Flag 表示已通关（可扫荡的前提）
    cleared = [s for s in campaign["stage_history"] if s.get("Star1Flag")]
    if not cleared:
        raise RuntimeError("没有可扫荡的已通关主线关卡")
    stage_id = cleared[-1]["StageUniqueId"]  # 取最后一条（通常是进度最高的关）
    await client.sweep.request(
        content=CONTENT_CAMPAIGN_MAIN,
        stage_id=stage_id,
        count=times,
        confirm=True,  # 扫荡消耗资源 → 必须确认
    )


async def cafe_daily(client: Client) -> None:
    """咖啡厅：对所有可互动角色摸头 + 领取产出货币 +（尽力）邀请一名学生。"""
    # 1) 摸头：有多个可互动角色时 interact() 不带参会因歧义拒绝，所以从 cafe.get() 的
    #    interaction_targets 逐个用显式 (cafe_db_id, character_id) 摸头。
    state = await client.cafe.get()
    for t in state.get("interaction_targets") or []:
        await client.cafe.interact(cafe_db_id=t["CafeDBId"], character_id=t["CharacterId"])
    # 2) 领取咖啡厅产出的货币
    await client.cafe.receive_currency(confirm=True)
    # 3) 邀请学生（账号相关，尽力而为）：character_server_id 来自 character.list()
    try:
        chars = await client.character.list()
        owned = chars.get("characters") or chars.get("students") or []
        if owned:
            server_id = owned[0].get("ServerId")
            if server_id is not None:
                # 不传 cafe_db_id 时服务器用默认咖啡厅；用邀请券则改 summon_character_ticket_use
                await client.cafe.summon_character(character_server_id=server_id, confirm=True)
    except Exception as exc:  # noqa: BLE001
        # 已在咖啡厅/无空位/该角色不可邀请等都很常见，邀请失败不影响前两步
        print(f"        （咖啡厅邀请略过：{type(exc).__name__}）")


async def academy_schedule(client: Client) -> None:
    """课程表：在可见区域执行一次日程。"""
    info = await client.academy.get_info()
    zones = info.get("available_zone_ids") or info.get("AvailableZoneIds") or []
    if not zones:
        raise RuntimeError("当前没有可执行的课程表区域")
    # validate=True 会先校验该区域今天还能执行，否则抛错且不发包；无需 confirm
    await client.academy.attend_schedule(zone_id=zones[0], validate=True)


async def sweep_week_dungeon(client: Client, times: int = 1) -> None:
    """悬赏通缉（日常副本）扫荡。"""
    week = await client.week_dungeon.list()
    # additional_stage_ids 直接是一组可扫荡的 stage id；没有就退回 stage_history
    stage_ids = list(week.get("additional_stage_ids") or [])
    if not stage_ids:
        history = week.get("stage_history") or []
        stage_ids = [s.get("StageUniqueId") for s in history if s.get("StageUniqueId")]
    if not stage_ids:
        raise RuntimeError("没有可扫荡的悬赏通缉关卡")
    await client.sweep.request(
        content=CONTENT_WEEK_DUNGEON, stage_id=stage_ids[0], count=times, confirm=True
    )


async def sweep_school_dungeon(client: Client, times: int = 1) -> None:
    """学园交流会扫荡。"""
    school = await client.school_dungeon.list()
    history = school.get("stage_history") or []
    stage_ids = [s.get("StageUniqueId") for s in history if s.get("StageUniqueId")]
    if not stage_ids:
        # 未开放该功能的账号会返回 OpenConditionClosed，属账号状态而非报错
        raise RuntimeError("没有可扫荡的学园交流会关卡（或功能未开放）")
    await client.sweep.request(
        content=CONTENT_SCHOOL_DUNGEON, stage_id=stage_ids[-1], count=times, confirm=True
    )


async def craft_daily(client: Client) -> None:
    """制造：开始一次制造（消耗材料）。需要账号已配置制造节点/槽位。"""
    info = await client.craft.list()
    slots = info.get("craft_slots") or []
    if not slots:
        raise RuntimeError("没有可用的制造槽位")
    slot_id = slots[0].get("SlotId") or slots[0].get("Id")
    if slot_id is None:
        raise RuntimeError("制造槽位里取不到 slot_id")
    # 开始制造；完成后可再调用 complete_process(slot_id=..., confirm=True) 和 reward(...)
    await client.craft.begin_process(slot_id=slot_id, confirm=True)


async def clan_stamina_to_mail(client: Client) -> None:
    """社团领每日体力：进社团触发服务器把体力发到邮箱，再从邮箱领取。"""
    # 1) "进社团" —— login + lobby，服务器据此把每日体力下发到邮箱
    await client.clan.login()
    await client.clan.lobby()
    # 2) 读邮箱，拿到可领邮件的 ServerId（体力邮件 / 普通邮件）
    mails = await client.mail.list()
    ids = [m["ServerId"] for m in mails["mails"] if "ServerId" in m]
    if not ids:
        raise RuntimeError("邮箱里没有可领邮件")
    # 3) 领取（validate=True 默认会先复核这些邮件还在邮箱里，避免领空）
    await client.mail.receive(ids)


async def raid_sweep_and_reward(client: Client) -> None:
    """总力战：对已通关房间扫荡 + 一键领奖（不开荒，不进战斗）。"""
    rooms = await client.raid.complete_list()
    # complete_list 给出可领奖励的房间；具体可扫荡房间字段以返回为准
    receivable = rooms.get("receive_reward_ids") or []
    if receivable:
        # 一键领取已完成总力战的奖励（validate=True 先查可领项）
        await client.raid.reward_all(confirm=True)
    else:
        raise RuntimeError("当前没有可领的总力战奖励（可能没开荒/没开放）")
    # 若有已通关、可扫荡的房间，按其 unique_id 扫荡：
    #   await client.raid.sweep(unique_id=<房间id>, sweep_count=1, confirm=True)


async def time_attack_sweep(client: Client, times: int = 1) -> None:
    """综合战术考试扫荡（已通关后可扫）。"""
    await client.time_attack_dungeon.sweep(sweep_count=times, confirm=True)


async def claim_daily_missions(client: Client) -> None:
    """领取已完成的每日任务奖励（一键领整类）。

    已知限制：任务领奖等部分写协议需要 Nexon NGS-X/NGSM 风控证明，SDK 未内置真实
    provider，会返回 ErrorCode=1032 NexonNgsmValidateFail。这是 SDK 限制，不是示例问题。
    """
    # mission.multiple_reward 接受分类名字符串；"daily"=每日。validate=True 会先确认确有已完成项
    await client.mission.multiple_reward("daily")


# ── 登录 / 恢复会话（内置 cli-api/login_instance.py 的流程）────────────
def _save_session(client: Client) -> None:
    """把登录得到的 session/profile 落盘，供下次直接 restore（不必再过 Nexon 登录关卡）。
    注意：session/profile 含登录凭证，自行妥善保存，别提交到公开仓库。"""
    result = client.result
    if result is None:
        return
    Path(SESSION_PATH).parent.mkdir(parents=True, exist_ok=True)
    if result.session is not None:
        Path(SESSION_PATH).write_text(
            json.dumps(result.session, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    if result.profile is not None:
        Path(PROFILE_PATH).write_text(
            json.dumps(result.profile, ensure_ascii=False, indent=2), encoding="utf-8"
        )


async def _fresh_login(client: Client) -> None:
    """用 Nexon 账号密码全新登录，并把 session/profile 落盘（等价于 login_instance.py）。"""
    nx_id = NX_ID or input("Nexon 邮箱: ").strip()
    nx_password = NX_PASSWORD or getpass("Nexon 密码: ")
    await client.login(nx_id, nx_password)  # 走完整登录链路（TOYSDK/Nexon/网关），所有请求经 PROXY
    _save_session(client)
    print(f"登录成功，已保存会话到 {SESSION_PATH}")


async def ensure_logged_in(client: Client) -> None:
    """让传入的 client 进入"已登录"状态（在已构造好的 client 上操作，不在这里建 Client）。

    优先用已保存的 session 恢复（快，且不必再过 Nexon 登录关卡）；
    没有 session 文件、会话已过每日刷新、或设了 HLBA_FORCE_LOGIN=1 时，改用账号密码全新登录。
    """
    session_file = Path(SESSION_PATH)
    if session_file.exists() and not FORCE_LOGIN:
        try:
            await client.restore_session(json.loads(session_file.read_text(encoding="utf-8")))
            print(f"已用现有会话恢复：{session_file}")
            return
        except DailyResetSessionExpiredError:
            # 会话跨过了每日刷新（19:00 UTC / 北京时间 03:00）——自动改为重新登录
            print("会话已过每日刷新，改为重新登录…")
        except Exception as exc:  # noqa: BLE001 - 会话损坏/字段缺失等也退回登录
            print(f"恢复会话失败（{type(exc).__name__}），改为重新登录…")

    print("正在全新登录…（首次较慢：要在线取版本号 + 过 Nexon 安全校验；卡住时开 HLBA_DEBUG=1 看到哪步）")
    await _fresh_login(client)


# ── 主流程 ─────────────────────────────────────────────────────────
async def main() -> None:
    # 推荐用法：先显式初始化一个 Client，配好代理/区服/超时/调试，之后所有调用都用它。
    # proxy 会同时用于：登录链路、游戏网关发包、官方数据/学生名同步——一处配置全程生效。
    client = Client(
        region=REGION,
        proxy=PROXY,        #填 "system" 可自动识别 Clash/V2Ray 系统代理
        timeout=TIMEOUT,
        debug=DEBUG,        # HLBA_DEBUG=1 时会实时打印 [HLBA] 每步日志，卡住时最后一行就是卡住的那步
        **({"client_version": CLIENT_VERSION} if CLIENT_VERSION else {}),
    )
    print(f"使用代理: {redact_proxy_url(PROXY) or '(直连)'} | region={REGION} | timeout={TIMEOUT}s")

    try:
        await ensure_logged_in(client)
    except Exception as exc:  # noqa: BLE001 - 登录/恢复失败时给出原因并收尾，不留下挂起的连接
        print(f"登录/恢复失败：{type(exc).__name__}: {exc}")
        await client.aclose()
        return

    print("=== 开始执行每日任务（能自动的部分）===")
    # 顺序：先签到/扫荡/日常，再社团→邮箱，最后统一领每日任务奖励
    await run_task("每日签到", daily_attendance(client))
    await run_task("咖啡厅摸头/领币/邀请", cafe_daily(client))
    await run_task("课程表", academy_schedule(client))
    await run_task("悬赏通缉扫荡", sweep_week_dungeon(client, times=1))
    await run_task("制造", craft_daily(client))
    await run_task("社团领每日体力(进社团→邮箱领)", clan_stamina_to_mail(client))
    await run_task("总力战扫荡+领奖", raid_sweep_and_reward(client))
    await run_task("综合战术考试扫荡", time_attack_sweep(client, times=1))
    await run_task("学园交流会扫荡", sweep_school_dungeon(client, times=1))
    await run_task("扫图（主线扫荡）", sweep_campaign(client, times=1))
    # 所有产出做完后，统一领取已完成的每日任务奖励
    await run_task("领取每日任务奖励", claim_daily_missions(client))

    # 这些是战斗/PvP，必须自己上号，SDK 不代打：
    print("\n=== 需自己上号完成（SDK 不提供战斗）===")
    print("  - 活动关卡（如有当期活动）")
    print("  - 总力战开荒（开荒要实战；已通关房间才可上面的扫荡/领奖）")
    print("  - 竞技场（确定性 seeded 战斗 + 服务器 HashKey 校验，绕不开战斗引擎）")

    await client.aclose()
    print("\n完成。")


if __name__ == "__main__":
    asyncio.run(main())
