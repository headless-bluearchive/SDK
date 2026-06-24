# 功能完成度

SDK 目前已封装的游戏功能/场景一览，以及需要显式 `confirm=True` 的状态变更分档。逐模块调用方法见 [调用教程](README.md)，逐协议接入状态见 [`docs/protocols.md`](../protocols.md)。

## 已完成的部分

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

## 需显式确认的状态变更（`confirm=True`）

**全部强制 `confirm=True`**，不传则抛 `UnsafeOperationError` 且不发请求。按风险分档：

| 档位 | 覆盖 | 示例入口 | 说明 |
| --- | --- | --- | --- |
| 领取奖励 | 总力战系 / 通行证 / 每日记录 / 小游戏任务 / 占领结算 / 活动关卡 等 | `client.raid.reward_all(confirm=True)`、`client.battle_pass.receive_reward(id, confirm=True)` | 把已完成奖励领进来；部分带"可领状态"前置校验 |
| 设置 / 偏好 | 账号资料·称呼、编队与咖啡厅预设、剧情展示、记忆大厅、选项、扫荡预设 等 | `client.account.call_name(call_name=..., confirm=True)`、`client.echelon.save(...)` | 改展示/预设/历史，**不消耗资源** |
| 养成 / 消耗 | 角色突破·技能·武器、装备、道具、制造、配方、商店购买、通行证等级、咖啡厅升级 等 | `client.character.transcendence(...)`、`client.equipment.level_up(...)`、`client.shop.buy_merchandise(...)` | **消耗青辉石/材料/货币/次数**，调用前自行确认 |
| 破坏性 / 社团 | 删好友·拉黑、退团·解散·踢人·任命 等 | `client.clan.dismiss(confirm=True)`、`client.friend.remove(...)` | **不可逆**，请格外谨慎 |

完整方法清单见 [显式确认变更页面](player/state-changing.md)；逐协议状态见 [`docs/protocols.md`](../protocols.md)。

## 不接入（保持纯调用 + 公平边界）

战斗进入/结算/成绩提交、竞技场、小游戏对局/结算、抽卡购买/保存、支付、风控上报、账号危险操作。
