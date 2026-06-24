# Billing 协议

这一组协议对应游戏里“充值与购买状态页”以及与购买记录相关的底层数据。SDK 目前只把登录后能读到的购买状态快照整理出来，作为 `client.billing.status()` / `info()` 的数据来源。

这里不包含支付实现，也不包含购买完成、收尾、验证回调或风控相关流程。

## 游戏里对应什么

- 充值页里的购买状态提示
- 月卡奖励邮件是否存在
- 哪些月卡商品已经买过、还能不能重复买
- 商品购买次数和重置时间

## SDK 入口

```python
billing = client.billing.status()
```

返回的重点不是“怎么付钱”，而是“账号现在在充值页里显示什么状态”。

## 协议说明

| 协议名 | 协议号 | 游戏里的意思 | 状态 |
| --- | ---: | --- | --- |
| `Billing_TransactionStartByYostar` | `29000` | 支付流程起点 | 暂不接入 |
| `Billing_TransactionEndByYostar` | `29001` | 支付流程终点 | 暂不接入 |
| `Billing_PurchaseListByYostar` | `29002` | Yostar 购买状态列表 | 只作为登录态快照来源 |
| `Billing_PurchaseCashShopVerifyByNexon` | `29003` | Nexon 购买校验 | 暂不接入 |
| `Billing_CheckConditionCashShopGoods` | `29004` | 条件商品检查 | 暂不接入 |
| `Billing_PurchaseListByNexon` | `29005` | Nexon 购买状态列表 | 只作为登录态快照来源 |
| `Billing_ValidateByNexon` | `29006` | 支付校验 | 暂不接入 |
| `Billing_FinishByNexon` | `29007` | 支付收尾 | 暂不接入 |
| `Billing_PurchaseFreeProduct` | `29008` | 免费商品发放 | 暂不接入 |

## 关键字段（真实来源）

购买状态快照来自 `Account_Auth`(1002) 响应包**顶层、与 `AccountDB` 同级**的这组 wire 字段（已由逆向反编译类定义 + 抓包证据双重确认）。注意：游戏客户端里那个 `AccountBillingInfo` 对象（含 `Birth` / `NeedCheckPurchaseState` / `MonthlyProductRewards` 等）是**客户端 `MXAccount` 的派生组件，服务器并不下发**，SDK 不去读它。

| 字段 | 元素类型 | 游戏里的意思 |
| --- | --- | --- |
| `RepurchasableMonthlyProductCountDBs` | `PurchaseCountDB` | 可重复购买月卡类商品的购买计数与重置时间。 |
| `MonthlyProductParcel` / `MonthlyProductMail` | `ParcelInfo` | 月卡本次发放 / 以邮件发放的奖励包裹。 |
| `BiweeklyProductParcel` / `BiweeklyProductMail` | `ParcelInfo` | 双周卡本次发放 / 邮件发放的奖励包裹。 |
| `WeeklyProductParcel` / `WeeklyProductMail` | `ParcelInfo` | 周卡本次发放 / 邮件发放的奖励包裹。 |

`PurchaseCountDB` = `{ ShopCashId(long), PurchaseCount(int), ResetDate, PurchaseDate?, ManualResetDate? }`；
`ParcelInfo` = `{ Key{ Type, Id }, Amount, Multiplier, Probability }`。

> 完整的月卡购买历史 / `ProductMonthlyIdInMailList` 等只出现在 `Billing_PurchaseListByNexon`(29005) 这类充值协议响应里，属于支付链路，SDK 不接入。

## 返回字段

`client.billing.status()` / `info()` 返回：

| 字段 | 含义 |
| --- | --- |
| `available` | 是否拿到了登录态购买状态快照（拿到即 `True`，即使各列表为空）。 |
| `source` | 快照来自 `Account_Auth` 还是恢复后的 `session.billing`。 |
| `repurchasable_monthly_product_counts` | `PurchaseCountDB` 列表，整理为 `{shop_cash_id, purchase_count, reset_date, purchase_date, manual_reset_date}`。 |
| `repurchasable_count` | 上面列表的条数。 |
| `monthly_product` / `biweekly_product` / `weekly_product` | 每档 `{parcel, mail, parcel_count, mail_count}`，`parcel`/`mail` 元素为整理后的 `ParcelInfo`。 |
| `monthly_product_reward_mail_exist` | 月卡邮件包裹是否非空（由 `MonthlyProductMail` 推导）。 |
| `subscription_reward_mail_exist` | 月/双周/周卡任一邮件包裹非空。 |

## 说明

- 这些内容是登录态快照，不是支付入口。
- 不会主动发起交易，也不会保存包或 dump。
- 如果当前 session 没带出这组字段，`available` 会是 `False`，重新登录一次通常能拿到。
