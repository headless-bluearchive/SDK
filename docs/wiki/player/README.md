# 游戏功能调用

这里按游戏里看到的页面整理 SDK 用法。每个页面先说明它对应游戏里的什么功能，再给出常用 SDK 入口、必要参数和状态变更边界。

## 基础页面

- [账号资源](game-account.md)：账号当前资源，像青辉石、AP、信用点这类货币和材料摘要（`client.account.currency()`）。
- [学生、主线、日常副本和扫荡](game-readonly.md)：学生列表、主线进度、悬赏通缉/日常副本、多扫荡预设（`client.character.list()`、`client.campaign.list()`、`client.week_dungeon.list()`、`client.sweep.preset_list()`）。
- [扫荡预设](sweep.md)：多扫荡预设读取和显式确认扫荡入口（`client.sweep.preset_list()`、`client.sweep.multi_sweep(confirm=True)`）。

## 日常功能

- [签到](attendance.md)：普通签到、活动签到、签到领奖（`client.attendance.status()`、`claim()`）。
- [咖啡厅](cafe.md)：咖啡厅状态、摸头、收益领取、奖杯历史（`client.cafe.get()`、`interact()`、`receive_currency()`、`trophy_history()`）。
- [任务](mission.md)：每日/每周/成就/活动任务列表、任务领奖、指南任务赛季（`client.mission.list()`、`reward()`、`guide_season_list()`）。
- [邮件](mail.md)：邮箱检查、普通邮件、半永久邮件、邮件领取（`client.mail.check()`、`list()`、`receive()`）。
- [课程表](academy.md)：课程表区域、学生日程、普通课程表执行（`client.academy.get_info()`、`attend_schedule()`）。
- [MomoTalk](momotalk.md)：未读消息、对话查看、对话推进、羁绊剧情（`client.momotalk.status()`、`messages()`、`read()`、`advance_dialog()`）。

## 社交、活动和玩法

- [好友、社团、活动、Raid、小游戏等查询](readonly-extended.md)：好友列表/搜索、社团大厅/成员/助战、当前活动、活动商店状态、Raid 排名、制约解除决战、WorldRaid、活动小游戏状态、装备/物品/编队等（`client.friend.*`、`client.clan.*`、`client.event_content.*`、`client.raid.*`、`client.mini_game.*`）。
- [商店、AP 补充和招募状态](shop.md)：普通商店列表、AP 补充、招募列表、预抽卡/自选 Pickup 状态（`client.shop.list()`、`buy_ap(confirm=True)`、`gacha_recruit_list()`）。
- [好友申请、制造完成、关卡确认和剧情跳过](state-changing.md)：对应游戏里真正点下按钮并改变账号状态的操作，必须显式确认（`client.friend.send_request(confirm=True)`、`client.craft.complete_process_all(confirm=True)`、`client.campaign.confirm_main_stage(confirm=True)`、`client.scenario.skip_main_stage(confirm=True)`）。

## 调用原则

- 打开页面查看列表、状态和同步数据的方法默认可以直接调用。
- 会领奖、花资源、改变好友关系、推进关卡或剧情的方法必须传 `confirm=True`。
- 需要活动 ID、赛季 ID、社团 ID、好友账号 ID 的方法，优先从前置查询结果里取，不要随便硬填。
