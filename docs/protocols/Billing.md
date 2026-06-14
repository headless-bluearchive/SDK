# Billing 协议

充值与购买记录模块相关协议。

字段结构仅作为 SDK DTO 与发包实现参考；实际可用性以真实网关返回为准。

## 协议列表

| 协议名 | 协议号 | 作用 | RequestClass | ResponseClass |
| --- | ---: | --- | --- | --- |
| `Billing_TransactionStartByYostar` | `29000` | 充值与购买记录：执行 TransactionStartByYostar 流程 | `BillingTransactionStartByYostarRequest` | `BillingTransactionStartByYostarResponse` |
| `Billing_TransactionEndByYostar` | `29001` | 充值与购买记录：执行 TransactionEndByYostar 流程 | `BillingTransactionEndByYostarRequest` | `BillingTransactionEndByYostarResponse` |
| `Billing_PurchaseListByYostar` | `29002` | 充值与购买记录：Purchase列表ByYostar | `BillingPurchaseListByYostarRequest` | `BillingPurchaseListByYostarResponse` |
| `Billing_PurchaseCashShopVerifyByNexon` | `29003` | 充值与购买记录：PurchaseCash商店VerifyByNexon | `BillingPurchaseCashShopVerifyByNexonRequest` | `BillingPurchaseCashShopVerifyByNexonResponse` |
| `Billing_CheckConditionCashShopGoods` | `29004` | 充值与购买记录：检查ConditionCash商店Goods | `BillingCheckConditionCashGoodsRequest` | `BillingCheckConditionCashGoodsResponse` |
| `Billing_PurchaseListByNexon` | `29005` | 充值与购买记录：Purchase列表ByNexon | `BillingPurchaseListByNexonRequest` | `BillingPurchaseListByNexonResponse` |
| `Billing_ValidateByNexon` | `29006` | 充值与购买记录：执行 ValidateByNexon 流程 | `` | `` |
| `Billing_FinishByNexon` | `29007` | 充值与购买记录：执行 FinishByNexon 流程 | `` | `` |
| `Billing_PurchaseFreeProduct` | `29008` | 充值与购买记录：执行 PurchaseFreeProduct 流程 | `BillingPurchaseFreeProductRequest` | `BillingPurchaseFreeProductResponse` |

## 字段结构参考

### Billing_TransactionStartByYostar

- 协议号：`29000`
- 作用：充值与购买记录：执行 TransactionStartByYostar 流程
- RequestClass：`BillingTransactionStartByYostarRequest`
- ResponseClass：`BillingTransactionStartByYostarResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ShopCashId` | `long` | 商店Cash ID。 |
| `VirtualPayment` | `bool` | 是否为虚拟支付。 |
| `ShopCashProductSelectionDBs` | `List<ShopCashProductSelectionDB>?` | ShopCashProductSelection 数据列表。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `PurchaseCount` | `long` | 数量。 |
| `PurchaseResetDate` | `DateTime` | PurchaseResetDate时间。 |
| `PurchaseOrderId` | `long` | PurchaseOrder ID。 |
| `MXSeedKey` | `string?` | MX seed key。 |
| `PurchaseServerTag` | `PurchaseServerTag` | 购买服务器标签。 |
| `PurchaseServerCallbackUrl` | `string?` | 购买服务器回调 URL。 |

### Billing_TransactionEndByYostar

- 协议号：`29001`
- 作用：充值与购买记录：执行 TransactionEndByYostar 流程
- RequestClass：`BillingTransactionEndByYostarRequest`
- ResponseClass：`BillingTransactionEndByYostarResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `PurchaseOrderId` | `long` | PurchaseOrder ID。 |
| `EndType` | `BillingTransactionEndType` | 交易结束类型。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ParcelResult` | `ParcelResultDB?` | 奖励或道具变更结果。 |
| `MailDB` | `MailDB?` | 邮件数据。 |
| `CountList` | `List<PurchaseCountDB>?` | 数量List数据列表。 |
| `PurchaseCount` | `int` | 数量。 |
| `MonthlyProductList` | `List<MonthlyProductPurchaseDB>?` | Monthly商品List数据列表。 |
| `BattlePassInfo` | `BattlePassInfoDB?` | 战斗Pass信息数据。 |
| `BattlePassProductList` | `List<BattlePassProductPurchaseDB>?` | 战斗Pass商品List数据列表。 |

### Billing_PurchaseListByYostar

- 协议号：`29002`
- 作用：充值与购买记录：Purchase列表ByYostar
- RequestClass：`BillingPurchaseListByYostarRequest`
- ResponseClass：`BillingPurchaseListByYostarResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

无字段或未匹配到结构。

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `CountList` | `List<PurchaseCountDB>?` | 数量List数据列表。 |
| `OrderList` | `List<PurchaseOrderDB>?` | OrderList数据列表。 |
| `MonthlyProductList` | `List<MonthlyProductPurchaseDB>?` | Monthly商品List数据列表。 |
| `BlockedProductDBs` | `List<BlockedProductDB>?` | BlockedProduct 数据列表。 |
| `BattlePassProductList` | `List<BattlePassProductPurchaseDB>?` | 战斗Pass商品List数据列表。 |

### Billing_PurchaseCashShopVerifyByNexon

- 协议号：`29003`
- 作用：充值与购买记录：PurchaseCash商店VerifyByNexon
- RequestClass：`BillingPurchaseCashShopVerifyByNexonRequest`
- ResponseClass：`BillingPurchaseCashShopVerifyByNexonResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `NpSN` | `long` | Nexon publisher account id / guid。 |
| `StampToken` | `string?` | 支付 stamp token。 |
| `ShopCashId` | `long` | 商店Cash ID。 |
| `VirtualPayment` | `bool` | 是否为虚拟支付。 |
| `CurrencyCode` | `string?` | 货币代码。 |
| `CurrencyValue` | `long` | 货币金额。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ParcelResult` | `ParcelResultDB?` | 奖励或道具变更结果。 |
| `MailDB` | `MailDB?` | 邮件数据。 |
| `CountList` | `List<PurchaseCountDB>?` | 数量List数据列表。 |
| `PurchaseCount` | `int` | 数量。 |
| `MonthlyProductList` | `List<MonthlyProductPurchaseDB>?` | Monthly商品List数据列表。 |
| `ProductMonthlyIdInMailList` | `List<long>?` | 商品MonthlyIdIn邮件List数据列表。 |
| `GachaTicketItemIdList` | `List<long>?` | 招募票券道具IdList数据列表。 |
| `shopId` | `string?` | shop ID。 |
| `itemPrice` | `double` | 商品价格。 |
| `currency` | `string?` | 货币代码。 |
| `stampId` | `string?` | stamp ID。 |
| `BattlePassIdInMailList` | `List<long>?` | 战斗PassIdIn邮件List数据列表。 |

### Billing_CheckConditionCashShopGoods

- 协议号：`29004`
- 作用：充值与购买记录：检查ConditionCash商店Goods
- RequestClass：`BillingCheckConditionCashGoodsRequest`
- ResponseClass：`BillingCheckConditionCashGoodsResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `user_id` | `string?` | 用户 ID。 |
| `product_id` | `long` | 商品 ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `result` | `bool` | 处理结果。 |

### Billing_PurchaseListByNexon

- 协议号：`29005`
- 作用：充值与购买记录：Purchase列表ByNexon
- RequestClass：`BillingPurchaseListByNexonRequest`
- ResponseClass：`BillingPurchaseListByNexonResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `IsTeenage` | `bool` | 布尔状态。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `CountList` | `List<PurchaseCountDB>?` | 数量List数据列表。 |
| `OrderList` | `List<PurchaseOrderDB>?` | OrderList数据列表。 |
| `MonthlyProductList` | `List<MonthlyProductPurchaseDB>?` | Monthly商品List数据列表。 |
| `ProductMonthlyIdInMailList` | `List<long>?` | 商品MonthlyIdIn邮件List数据列表。 |
| `GachaTicketItemIdList` | `List<long>?` | 招募票券道具IdList数据列表。 |
| `BlockedProductDBs` | `List<BlockedProductDB>?` | BlockedProduct 数据列表。 |
| `BattlePassProductList` | `List<BattlePassProductPurchaseDB>?` | 战斗Pass商品List数据列表。 |
| `BattlePassIdInMailList` | `List<long>?` | 战斗PassIdIn邮件List数据列表。 |
| `IsTeenage` | `bool` | 布尔状态。 |

### Billing_ValidateByNexon

- 协议号：`29006`
- 作用：充值与购买记录：执行 ValidateByNexon 流程
- RequestClass：``
- ResponseClass：``
- 状态：待补结构。

#### Request 字段

无字段或未匹配到结构。

#### Response 字段

无字段或未匹配到结构。

### Billing_FinishByNexon

- 协议号：`29007`
- 作用：充值与购买记录：执行 FinishByNexon 流程
- RequestClass：``
- ResponseClass：``
- 状态：待补结构。

#### Request 字段

无字段或未匹配到结构。

#### Response 字段

无字段或未匹配到结构。

### Billing_PurchaseFreeProduct

- 协议号：`29008`
- 作用：充值与购买记录：执行 PurchaseFreeProduct 流程
- RequestClass：`BillingPurchaseFreeProductRequest`
- ResponseClass：`BillingPurchaseFreeProductResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ShopCashId` | `long` | 商店Cash ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ParcelResult` | `ParcelResultDB?` | 奖励或道具变更结果。 |
| `MailDB` | `MailDB?` | 邮件数据。 |
| `PurchaseProduct` | `PurchaseCountDB?` | Purchase商品数据。 |
