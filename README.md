
<p align="center">
  <img src="logo.png" alt="deobf" width="500">
</p>

<p align="center">
  <a href="./LICENSE">
    <img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="License: MIT">
  </a>
  <a href="https://www.python.org/">
    <img src="https://img.shields.io/badge/python-3.10%2B-blue.svg" alt="Python Version">
  </a>
</p>

## 前提概要

Headless Bluearchive SDK 是 `headless-bluearchive` 的 SDK 包。在**不影响游戏公平性**的前提将 bluearchive 的登录和主网关发包封装成一个 Python 库，供 CLI、API 服务、GUI 或其他自动化程序复用。

调用方只需要引用库入口，不需要再处理协议构包和会话加密这些底层细节，项目中**不包含**战斗、提交成绩、竞技场、招募等影响游戏公平性的发包。

### **目前支持的区服：国际服(港澳台，北美，全球，韩服，亚服)。**
### **如果你不懂怎么用请你把一整个仓库丢给ai，让ai代替一下大脑思考就会了。**
### **部分新账号可能存在领取奖励时可能会出现NGS反作弊风控导致无法正常领取奖励。**

> ⚠️ 本仓库**仅供学习与研究目的发布** —— 基于BlueArchive的底层架构，一份由互联网爱好者学习研究而产生的产物，您应该遵守其官方使用协定，如产生任何法律后果责任自负⚠️

## 快速了解
- 文档：[架构](docs/architecture.md) | [开发规范](docs/development.md) | [调用教程](docs/wiki) | [错误对照](docs/error.md)

## 许可与声明
原始字节码未授予任何许可。本仓库中的所有逆向结果仅供研究与学习使用。如果在使用的过程中导致账号风控/封禁等后果应由**使用者自行承担**。

## 开挂死妈
本项目的初衷只是为了更好的服务ba玩家，而不是被拿去利用拿去翻牌透视和竞技场透视，除非你是 [本心先生](https://www.bilibili.com/opus/1053758758567542800) 做人做事，无愧于心。

## 细节

经过 claude fable 5 配合 x64dbg、IDA 和 Recaf 长达 5 秒的分析，claude 认为 BA 的主网关请求并不是补几个字段就能跑通的简单 HTTP replay。除了基础协议字段和请求体外，还叠加了 PacketCryptManager 外层封包、CRC、压缩、异或、1014 后 O22 会话语义、SessionKey 注入和请求体 AES 加密的组合流程。

此外，部分关键返回值还依赖经过 Themida 虚拟化保护的 NGS-X 服务组件。被 Themida 保护后的 blob 确实已经烂到不适合人类直接复用，因此我们顺手还原了游戏本体源码和调用链逻辑，并在完成 Themida 脱壳与 devirtualization 后接入 Codex，以较低的 Tokens 成本完成了这一份负责加密、封包、解包和发送请求的客户端封装。
## 目录结构

```text
SDK/
  HLBA.py            # SDK 对外入口
  core/              # 协议、schema、packet、crypto、gateway client、异常定义
  modules/
    auth/            # 登录服务
    runtime/         # Android profile、区域配置、运行态配置
    game/
      player/
        cafe/        
        ....         # 游戏发包
  config/            # 项目默认配置
  utils/             # 通用工具
  tests/             # 轻量测试
  docs/              # 架构、开发规范和调用文档
```

## 目前完成的部分

| 游戏功能/场景 | SDK 入口 | 游戏里对应什么 | 状态 |
| --- | --- | --- | --- |
| 登录和会话 | `client.login()` / `client.restore_session()` | 账号登录、恢复已登录会话 | 已完成 |
| 官方数据表 | `client.prepare_data()` | 拉取游戏配置表，用来识别学生、道具、活动、关卡等 ID | 已完成 |
| 账号主页和成长奖励 | `client.account.currency()` / `client.account.tutorial()` / `client.account.check_level_reward()` | 主界面资源栏、教程进度、账号成长里的等级奖励页 | 已完成；等级奖励 live 已验证当前账号暂无可领取项 |
| 个人资料和外观 | `client.attachment.get()` / `client.attachment.emblem_list()` | 头像框、Emblem、资料页附件 | 已完成；Emblem live 已验证可读取和装配 |
| 学生、编队、装备和物品仓库 | `client.character.list()` / `client.echelon.list()` / `client.equipment.list()` / `client.item.list()` / `client.character_gear.list()` | 学生列表、编队页面、装备仓库、道具仓库、爱用品 | 已完成 |
| 主线、剧情、交流会和扫荡预设 | `client.campaign.list()` / `client.scenario.list()` / `client.school_dungeon.list()` / `client.week_dungeon.list()` / `client.sweep.preset_list()` / `client.sweep.skip_history_list()` | 主线进度、已读剧情、学院交流会、悬赏通缉/日常副本、多扫荡预设、扫荡历史 | 已完成；扫荡历史 live 探针当前返回 500 / Protocol=-1 |
| 签到入口 | `client.attendance.status()` / `claim()` | 普通签到、活动签到页面 | 已完成 |
| 咖啡厅 | `client.cafe.get()` / `interact()` / `receive_currency()` / `trophy_history()` | 咖啡厅状态、摸头、收益领取、奖杯历史 | 已完成 |
| MomoTalk | `client.momotalk.status()` / `messages()` / `read()` / `advance_dialog()` | 未读消息、对话查看、对话推进、羁绊剧情 | 已完成 |
| 任务页面 | `client.mission.list()` / `reward()` / `multiple_reward()` / `guide_season_list()` | 每日/每周/成就/活动任务列表、任务领奖、指南任务赛季 | 基本完成 |
| 战斗通行证 | `client.battle_pass.get_info(battle_pass_id)` / `mission_list(battle_pass_id)` / `check(battle_pass_id)` | 通行证赛季总览、任务页和领取状态 | 已完成封装；`battle_pass_id` 需来自当前赛季或登录链路 |
| 邮件 | `client.mail.check()` / `list()` / `receive()` / `list_semi_permanent()` | 邮箱红点、普通邮件、半永久邮件、领取邮件 | 已完成 |
| 充值与购买状态 | `client.billing.status()` / `info()` | 充值页里的购买状态快照、月卡奖励邮件、可重复购买商品、购买次数 | 已完成封装；已用代理重登验证一次，当前账号未带出快照 |
| 课程表 | `client.academy.get_info()` / `attend_schedule()` | 课程表区域、学生日程、普通课程表执行 | 已完成 |
| 好友和名片 | `client.friend.list()` / `search()` / `detailed_info()` / `id_card()` / `send_request(confirm=True)` 等 | 好友列表、好友搜索、玩家详情、名片、好友申请处理 | 查询已完成；申请类操作需 `confirm=True` |
| 成长与外观奖励 | `client.account.check_level_reward()` / `client.account.receive_level_reward(confirm=True)` / `client.attachment.emblem_list()` / `client.attachment.emblem_acquire(confirm=True)` / `client.attachment.emblem_attach(confirm=True)` | 账号等级奖励页、头像框、Emblem 获取与装配 | 已封装；领取类操作需 `confirm=True` |
| 社团页面 | `client.clan.lobby()` / `search()` / `member_list()` / `all_assist_list()` | 社团大厅、社团搜索、成员列表、社团助战 | 已完成 |
| 活动和活动商店状态 | `client.event.list()` / `event_content.*` / `conquest.*` | 当前活动、永久化活动、活动关卡、活动商店、箱式商店、活动小游戏入口 | 已封装；部分需要当前开放活动才能 live 成功 |
| Raid、大决战和 WorldRaid | `client.raid.*` / `client.eliminate_raid.*` / `client.permanent_raid.lobby()` / `client.world_raid.*` | 总力战大厅、排名、最佳队伍、常驻 Raid、WorldRaid | Raid 类大部分 live 通过；WorldRaid 需要开放赛季参数 |
| 活动小游戏 | `client.mini_game.*` | Shooting、TableBoard、DreamMaker、Defense、RoadPuzzle、CCG 等小游戏大厅状态 | 已封装；部分需要当前开放小游戏活动 |
| 商店和招募状态 | `client.shop.list()` / `buy_ap(confirm=True)` / `gacha_recruit_list()` / `beforehand_gacha_get()` / `pickup_selection_gacha_get()` | 商店列表、AP 补充、招募列表、预抽卡/自选 Pickup 状态 | 已完成；花资源操作需 `confirm=True` |
| 制造和关卡确认 | `client.craft.list()` / `complete_process_all(confirm=True)` / `client.campaign.confirm_main_stage(confirm=True)` / `client.scenario.*(confirm=True)` | 制造列表、完成制造、主线/剧情关卡确认或跳过 | 已封装；状态变更操作需 `confirm=True` 和前置条件 |

### 需显式确认的状态变更（`confirm=True`）

**全部强制 `confirm=True`**，不传则抛 `UnsafeOperationError` 且不发请求。按风险分档：

| 档位 | 覆盖 | 示例入口 | 说明 |
| --- | --- | --- | --- |
| 领取奖励 | 总力战系 / 通行证 / 每日记录 / 小游戏任务 / 占领结算 / 活动关卡 等 | `client.raid.reward_all(confirm=True)`、`client.battle_pass.receive_reward(id, confirm=True)` | 把已完成奖励领进来；部分带"可领状态"前置校验 |
| 设置 / 偏好 | 账号资料·称呼、编队与咖啡厅预设、剧情展示、记忆大厅、选项、扫荡预设 等 | `client.account.call_name(call_name=..., confirm=True)`、`client.echelon.save(...)` | 改展示/预设/历史，**不消耗资源** |
| 养成 / 消耗 | 角色突破·技能·武器、装备、道具、制造、配方、商店购买、通行证等级、咖啡厅升级 等 | `client.character.transcendence(...)`、`client.equipment.level_up(...)`、`client.shop.buy_merchandise(...)` | **消耗青辉石/材料/货币/次数**，调用前自行确认 |
| 破坏性 / 社团 | 删好友·拉黑、退团·解散·踢人·任命 等 | `client.clan.dismiss(confirm=True)`、`client.friend.remove(...)` | **不可逆**，请格外谨慎 |

完整方法清单见 [显式确认变更页面](docs/wiki/player/state-changing.md)；逐协议状态见 `docs/protocols.md`（当前 **287/397** 协议已接入）。

**不接入**（保持纯调用 + 公平边界）：战斗进入/结算/成绩提交、竞技场、小游戏对局/结算、抽卡购买/保存、支付、风控上报、账号危险操作。

## 基础使用
- 我认为任何一个python开发者且脑子正常的人都知道你需要 `pip install -r requirements.txt` 下载依赖后这样子在你的项目中belike:
- region 可填：tw、asia、na、global、kr 默认 tw 如果你是傻逼连自己的号是什么区都不知道可以去死了。 

```python
import asyncio

from HLBA import Client

async def main():
    client = Client(region="tw", debug=True)
    result = await client.login("email@example.com", "password")

    print(result.account_id)
    print(result.nickname)
    print(result.friend_code)

asyncio.run(main())
```

`profile` 是设备和运行态信息，`session` 是后续游戏内发包需要的会话信息。里面有登录凭证，别打印到日志里。SDK 不会帮你写文件，想持久化就自己保存：

```python
import asyncio
import json
from pathlib import Path

from HLBA import Client

async def main():
    client = Client(region="tw")
    result = await client.login("email@example.com", "password")

    runtime = Path("runtime")
    runtime.mkdir(exist_ok=True)
    runtime.joinpath("profile.json").write_text(json.dumps(result.profile, ensure_ascii=False, indent=2), encoding="utf-8")
    runtime.joinpath("session.json").write_text(json.dumps(result.session, ensure_ascii=False, indent=2), encoding="utf-8")

asyncio.run(main())
```

## 更多支持
- 本项目还在早期开发阶段，百分之90的项目整理工作由claude+codex协助开发，有任何使用上的问题/bug请及时开issues反馈（请先阅读docs尝试解决问题，再开issues）。

## 致谢

- 原始项目：**[BlueArchive](https://bluearchive.nexon.com/)**。
- 引用：[Schaledb](https://schaledb.com/)
- 反混淆、符号还原与工程脚手架：**Claude** 在人工监督下完成
- 重命名函数，恢复可读性：**Claude Sonnet**自主完成
- 仓库源代码分析，敏感信息审计：**Claude Opus**在人工监督下完成
- 仓库素材来源于网络，感谢特异人士，**这位面善又友善的朋友**

## 奇异搞笑
<p align="center">
    <img src="funny/openXiangbin.jpg" alt="openXiangbin" width="170">
    <img src="funny/deobf.jpg" alt="deobf" width="180">
    <img src="funny/protection.png" alt="protection" width="180">
    <img src="funny/hacker.jpg" alt="hacker" width="180">
    <img src="funny/hacker2.jpg" alt="hacker2" width="220">
    <img src="funny/deobf-claude.png" alt="deobf2" width="250">
</p>
