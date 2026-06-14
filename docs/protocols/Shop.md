# Shop 协议

商店模块相关协议。

字段结构仅作为 SDK DTO 与发包实现参考；实际可用性以真实网关返回为准。

## 接入边界

已删除招募购买、抽取招募、Beforehand 招募执行、保存招募结果、选择招募结果、Pickup Selection 设置与购买、抽卡结果、抽卡统计等会影响游戏公平性的部分。

本文件只保留招募列表、招募状态读取，以及普通商店查询/资源操作类协议。

## 协议列表

| 协议名 | 协议号 | 作用 | RequestClass | ResponseClass |
| --- | ---: | --- | --- | --- |
| `Shop_BuyMerchandise` | `10000` | 商店/招募：购买商店商品 | `ShopBuyMerchandiseRequest` | `ShopBuyMerchandiseResponse` |
| `Shop_List` | `10002` | 商店/招募：获取列表数据 | `ShopListRequest` | `ShopListResponse` |
| `Shop_Refresh` | `10003` | 商店/招募：刷新数据或商店内容 | `ShopRefreshRequest` | `ShopRefreshResponse` |
| `Shop_BuyEligma` | `10004` | 商店/招募：购买神名精髓相关商品 | `ShopBuyEligmaRequest` | `ShopBuyEligmaResponse` |
| `Shop_GachaRecruitList` | `10006` | 商店/招募：获取招募列表 | `ShopGachaRecruitListRequest` | `ShopGachaRecruitListResponse` |
| `Shop_BuyRefreshMerchandise` | `10007` | 商店/招募：购买刷新商品 | `ShopBuyRefreshMerchandiseRequest` | `ShopBuyRefreshMerchandiseResponse` |
| `Shop_BuyAP` | `10009` | 商店/招募：购买 AP | `ShopBuyAPRequest` | `ShopBuyAPResponse` |
| `Shop_BeforehandGachaGet` | `10010` | 商店/招募：Beforehand招募获取 | `ShopBeforehandGachaGetRequest` | `ShopBeforehandGachaGetResponse` |
| `Shop_PickupSelectionGachaGet` | `10014` | 商店/招募：获取自选 Pickup 招募状态 | `ShopPickupSelectionGachaGetRequest` | `ShopPickupSelectionGachaGetResponse` |

## 字段结构参考

### Shop_BuyMerchandise

- 协议号：`10000`
- 作用：商店/招募：购买商店商品
- RequestClass：`ShopBuyMerchandiseRequest`
- ResponseClass：`ShopBuyMerchandiseResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `IsRefreshGoods` | `bool` | 布尔状态。 |
| `ShopUniqueId` | `long` | 商店唯一 ID。 |
| `GoodsId` | `long` | Goods ID。 |
| `PurchaseCount` | `long` | 数量。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `AccountCurrencyDB` | `AccountCurrencyDB?` | 账号货币数据。 |
| `ConsumeResultDB` | `ConsumeResultDB?` | 消耗结果。 |
| `ParcelResultDB` | `ParcelResultDB?` | 奖励或道具变更结果。 |
| `MailDB` | `MailDB?` | 邮件数据。 |
| `ShopProductDB` | `ShopProductDB?` | 商店商品数据。 |

### Shop_List

- 协议号：`10002`
- 作用：商店/招募：获取列表数据
- RequestClass：`ShopListRequest`
- ResponseClass：`ShopListResponse`
- 状态：SDK 已封装并通过 live 只读验证。默认发送 `CategoryList=[]`。

#### SDK 方法

```python
shops = await client.shop.list()
```

返回结构：

| 字段 | 说明 |
| --- | --- |
| `shop_infos` | 商店信息列表。 |
| `eligma_history` | 神名精髓相关历史列表。 |
| `extra` | 服务端返回中的其他顶层字段。 |

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `CategoryList` | `List<ShopCategoryType>?` | CategoryList数据列表。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ShopInfos` | `List<ShopInfoDB>?` | 商店Infos数据列表。 |
| `ShopEligmaHistoryDBs` | `List<ShopEligmaHistoryDB>?` | ShopEligmaHistory 数据列表。 |

### Shop_Refresh

- 协议号：`10003`
- 作用：商店/招募：刷新数据或商店内容
- RequestClass：`ShopRefreshRequest`
- ResponseClass：`ShopRefreshResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ShopCategoryType` | `ShopCategoryType` | 商店分类类型。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ParcelResultDB` | `ParcelResultDB?` | 奖励或道具变更结果。 |
| `ShopInfoDB` | `ShopInfoDB?` | 商店信息数据。 |

### Shop_BuyEligma

- 协议号：`10004`
- 作用：商店/招募：购买神名精髓相关商品
- RequestClass：`ShopBuyEligmaRequest`
- ResponseClass：`ShopBuyEligmaResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `GoodsUniqueId` | `long` | Goods唯一 ID。 |
| `ShopUniqueId` | `long` | 商店唯一 ID。 |
| `CharacterUniqueId` | `long` | 角色服务器唯一 ID。 |
| `PurchaseCount` | `long` | 数量。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ParcelResultDB` | `ParcelResultDB?` | 奖励或道具变更结果。 |
| `ConsumeResultDB` | `ConsumeResultDB?` | 消耗结果。 |
| `ShopProductDB` | `ShopProductDB?` | 商店商品数据。 |

### Shop_GachaRecruitList

- 协议号：`10006`
- 作用：商店/招募：获取招募列表
- RequestClass：`ShopGachaRecruitListRequest`
- ResponseClass：`ShopGachaRecruitListResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

无字段或未匹配到结构。

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ShopRecruits` | `List<ShopRecruitDB>?` | 商店Recruits数据列表。 |
| `ShopFreeRecruitHistoryDBs` | `List<ShopFreeRecruitHistoryDB>?` | ShopFreeRecruitHistory 数据列表。 |

### Shop_BuyRefreshMerchandise

- 协议号：`10007`
- 作用：商店/招募：购买刷新商品
- RequestClass：`ShopBuyRefreshMerchandiseRequest`
- ResponseClass：`ShopBuyRefreshMerchandiseResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ShopUniqueIds` | `List<long>?` | ID 列表。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `AccountCurrencyDB` | `AccountCurrencyDB?` | 账号货币数据。 |
| `ConsumeResultDB` | `ConsumeResultDB?` | 消耗结果。 |
| `ParcelResultDB` | `ParcelResultDB?` | 奖励或道具变更结果。 |
| `ShopProductDB` | `List<ShopProductDB>?` | 商店商品数据列表。 |
| `MailDB` | `MailDB?` | 邮件数据。 |

### Shop_BuyAP

- 协议号：`10009`
- 作用：商店/招募：购买 AP
- RequestClass：`ShopBuyAPRequest`
- ResponseClass：`ShopBuyAPResponse`
- 状态：SDK 已做安全封装并通过 live 资源消耗验证。调用必须显式传入 `confirm=True`；AP 商品可先通过 `Shop_List(category_list=[4])` 读取，实际购买字段使用列表里的 `ShopExcelId`。

#### SDK 方法

```python
result = await client.shop.buy_ap(shop_unique_id, purchase_count=1, confirm=True)
```

该接口会消耗资源，不会被 SDK 默认自动调用。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ShopUniqueId` | `long` | 商店唯一 ID。 |
| `PurchaseCount` | `long` | 数量。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `AccountCurrencyDB` | `AccountCurrencyDB?` | 账号货币数据。 |
| `ConsumeResultDB` | `ConsumeResultDB?` | 消耗结果。 |
| `ParcelResultDB` | `ParcelResultDB?` | 奖励或道具变更结果。 |
| `MailDB` | `MailDB?` | 邮件数据。 |
| `ShopProductDB` | `ShopProductDB?` | 商店商品数据。 |

### Shop_BeforehandGachaGet

- 协议号：`10010`
- 作用：商店/招募：Beforehand招募获取
- RequestClass：`ShopBeforehandGachaGetRequest`
- ResponseClass：`ShopBeforehandGachaGetResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

无字段或未匹配到结构。

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `AlreadyPicked` | `bool` | 是否已经选择。 |
| `BeforehandGachaSnapshot` | `BeforehandGachaSnapshotDB?` | Beforehand招募Snapshot数据。 |

### Shop_PickupSelectionGachaGet

- 协议号：`10014`
- 作用：商店/招募：获取自选 Pickup 招募状态
- RequestClass：`ShopPickupSelectionGachaGetRequest`
- ResponseClass：`ShopPickupSelectionGachaGetResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ShopRecruitId` | `long` | 商店Recruit ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `PickupCharacterSelection` | `Dictionary<long, long>?` | Pickup 角色选择映射。 |
