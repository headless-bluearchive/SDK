# 路线图

## 当前阶段

- 完成旧 `ba_replay` 到 `headlessBA` 的模块化迁移。
- 保留 Android/mobile 登录 replay 的可用性。
- 建立 `core/modules/utils/config/log/database` 基础边界。

## 下一阶段

- 把 CLI 中的长流程逐步收敛为 service 类。
- 为账号、任务、执行结果建立数据库模型。
- 建立游戏内 API registry 和统一 request runner。
- 增加 RESTful API 入口。
- 增加 GUI 可视化入口。
