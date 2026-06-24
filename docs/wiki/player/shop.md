# 商店、AP 补充和招募状态

对应游戏里的普通/活动商店、AP 旁加号对应的购买弹窗，以及招募页面的状态展示。

- 能看：商店商品与库存/价格、神名精髓购买历史、当前卡池与免费招募历史、预抽卡活动状态、自选 Pickup 招募状态。
- 能做：补充 AP、购买/刷新商店商品（均需 `confirm=True`，会消耗资源）。

招募相关方法仅读取页面状态，不含抽卡购买、抽取与结果选择；完整公平边界见[总览](../README.md#公平边界)。

## SDK 入口

`client.shop.*`：

| 方法 | 用途 | 需 confirm |
| --- | --- | :--: |
| `list(category_list=None)` | 读取商店商品列表，可传分类列表筛选；为空让服务端返回默认分类 | 否 |
| `gacha_recruit_list()` | 读取当前可见卡池与免费招募历史 | 否 |
| `beforehand_gacha_get()` | 读取预抽卡活动状态 | 否 |
| `pickup_selection_gacha_get(shop_recruit_id)` | 读取指定卡池的自选 Pickup 招募状态 | 否 |
| `buy_ap(shop_unique_id, purchase_count=1, confirm=True)` | 补充 AP，消耗青辉石或相关资源 | 是 |
| `buy_merchandise(goods_id=, is_refresh_goods=, purchase_count=, shop_unique_id=, confirm=True)` | 购买商店商品 | 是 |
| `refresh(shop_category_type=, confirm=True)` | 刷新商店商品 | 是 |
| `buy_refresh_merchandise(shop_unique_ids=, confirm=True)` | 购买刷新后的商品 | 是 |

> `buy_merchandise` / `refresh` / `buy_refresh_merchandise` 是会消耗资源的养成/消耗类写操作，同时收录在[显式确认变更页面](state-changing.md)的 C3 总清单里。

## 返回说明

- `list` / `gacha_recruit_list` / `beforehand_gacha_get` / `pickup_selection_gacha_get` / `buy_ap`：返回整理后的 `dict`，包含对应业务字段（商品列表、招募/卡池、货币与购买结果等），部分带 `count`，并统一附带 `extra`（未被识别的服务端字段）。
- `buy_merchandise` / `refresh` / `buy_refresh_merchandise`：直接返回服务端原始负载。

## 示例

只读商店与招募状态：

```python
shop = await client.shop.list()
for info in shop["shop_infos"]:
    print(info.get("ShopCategory"), info.get("Products"))

recruits = await client.shop.gacha_recruit_list()
print(recruits["count"], recruits["free_history_count"])
```

补充 AP（商品 ID 来自当前商店/游戏状态）：

```python
result = await client.shop.buy_ap(shop_unique_id, purchase_count=1, confirm=True)
```

## 注意

- 需 confirm 的写操作（`buy_ap` / `buy_merchandise` / `refresh` / `buy_refresh_merchandise`）必须显式传 `confirm=True`，否则抛 `UnsafeOperationError` 且不发包。
- `shop_unique_id` / `goods_id` / `shop_recruit_id` 等 ID 一律来自 `list()`、`gacha_recruit_list()` 等当前账号可见数据，不要手填。
- 逐协议接入状态见仓库根 [`docs/protocols.md`](../../protocols.md)。
