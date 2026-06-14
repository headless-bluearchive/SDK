# 调用教程

这里是给外部调用方看的，不是协议考古笔记。你只要知道 `Client` 怎么登录、session 怎么保存、每个模块怎么调用、哪些地方别硬来，就够了。

## 基础

- [登录鉴权](base/auth.md)
- [官方资源数据](base/official-data.md)
- [错误对照](../error.md)

## 玩家接口

- [玩家接口总览](player/README.md)
- [账号资源](player/game-account.md)
- [签到](player/attendance.md)
- [咖啡厅](player/cafe.md)
- [任务](player/mission.md)
- [邮件](player/mail.md)
- [课程表](player/academy.md)
- [MomoTalk](player/momotalk.md)
- [基础只读](player/game-readonly.md)
- [商店](player/shop.md)
- [扫荡](player/sweep.md)

再强调一次：SDK 是库，不是脚本集合。状态变更接口会尽量给你挡一下错误，但外部程序自己也要知道自己在点什么。
