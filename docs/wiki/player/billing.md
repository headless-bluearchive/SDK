# 充值与购买状态

对应游戏里充值页 / 月卡页 / 购买记录页能看到的购买状态快照——不是支付页面，也不是购买按钮本身。能看的是：账号有没有月卡奖励邮件、哪些月卡商品可以重复购买、各档月卡 / 双周卡 / 周卡的奖励包。这里不发起支付、不补单、不领奖。

`status()` 只读登录态里 `Account_Auth` 带出来的购买状态字段（登录时缓存到 `result.billing` 与 `session["billing"]`），没有缓存时返回不可用状态。

## SDK 入口

`status()` / `info()` 是同步方法，不需要 `await`，也不发网络请求。

| 方法 | 用途 | 需 `confirm=True` |
| --- | --- | :--: |
| `status()` | 读登录态里的充值与购买状态快照 | 否 |
| `info()` | `status()` 的别名（与其他页面命名习惯保持一致） | 否 |

```python
billing = client.billing.status()
if billing["available"] and billing["monthly_product_reward_mail_exist"]:
    print("有月卡奖励邮件")
```

## 返回说明

`status()` / `info()` 不经网络，也不经 `format_*`；方法内部把 `Account_Auth` 顶层 wire 字段整理成一个稳定 dict。形状大致是：

- 一个可用性标志：`available` / `source`，不可用时附 `reason`。
- 可重复购买月卡商品的购买计数列表 + `repurchasable_count`。
- 月卡 / 双周卡 / 周卡三档奖励桶（`monthly_product` / `biweekly_product` / `weekly_product`），每桶含 `parcel`（本次发放）和 `mail`（以邮件发放）两类包裹及各自数量。
- 两个由包裹是否非空推导的布尔：有没有月卡奖励邮件、任意订阅（月 / 双周 / 周卡）有没有奖励邮件。

列表元素仍是整理后的轻量 dict（购买计数项、奖励包裹项）。此处仅描述结构，不逐一列出键名。

> 这些字段是 `Account_Auth` 顶层 wire 字段；游戏客户端那个 `AccountBillingInfo`（`Birth` / `NeedCheckPurchaseState` / `MonthlyProductRewards` 等）是客户端派生物，服务器不下发，SDK 不读它。完整购买历史属于充值协议 `Billing_PurchaseListByNexon`，不接入。

## 注意

- 这是购买状态快照，不是支付接口：不自动补单、不自动领奖、不完成任何购买流程。
- 依赖 `Account_Auth` 登录响应里的那组顶层购买字段。若当前 session 没有这份快照（或用旧 session 恢复时没带上 `session["billing"]`），`available` 会是 `False`，此时重新登录通常可重新获取。

---

逐协议接入状态见 [协议总表](../../protocols.md)。
