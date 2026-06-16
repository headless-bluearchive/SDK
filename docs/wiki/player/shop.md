# 商店、AP 补充和招募状态

这一页对应游戏里的商店页面、AP 购买弹窗，以及招募页面上的状态展示。读取商店和招募状态不会购买东西；AP 补充会消耗资源，必须显式确认。

## 商店商品列表

对应游戏里的普通商店、活动商店等商品列表。SDK 只读取商品状态，不自动购买。

```python
shop = await client.shop.list()
```

也可以只看指定分类：

```python
shop = await client.shop.list(category_list=[1, 2])
```

参数说明：

| 参数 | 游戏含义 |
| --- | --- |
| `category_list` | 商店分类列表。为空时让服务端返回默认分类集合。 |

返回结构：

```python
{
    "shop_infos": [...],      # 商品列表和库存/价格等信息
    "eligma_history": [...],  # 神名精髓相关购买历史
    "extra": {},
}
```

常见用法：

```python
shop = await client.shop.list()
for info in shop["shop_infos"]:
    print(info.get("ShopCategory"), info.get("Products"))
```

## AP 补充

对应游戏里点击 AP 旁边的加号并确认购买 AP。这个动作会消耗青辉石或相关资源。

```python
result = await client.shop.buy_ap(
    shop_unique_id=shop_unique_id,
    purchase_count=1,
    confirm=True,
)
```

参数说明：

| 参数 | 游戏含义 |
| --- | --- |
| `shop_unique_id` | AP 补充商品 ID，应该从商店列表或当前游戏状态中取得。 |
| `purchase_count` | 购买次数。 |
| `confirm=True` | 明确允许 SDK 执行资源消耗操作。 |

返回结构：

```python
{
    "account_currency": {...},  # 购买后的货币状态
    "consume_result": {...},    # 消耗结果
    "parcel_result": {...},     # 获得的 AP/物品结果
    "mail": {...},              # 如果服务端通过邮件发放，会出现在这里
    "shop_product": {...},      # 商品状态更新
    "extra": {},
}
```

没有 `confirm=True` 会抛 `UnsafeOperationError`。

## 招募页面状态

对应游戏里的招募页面，用于展示当前卡池、免费招募历史、预抽卡状态和自选 Pickup 状态。这里只读状态，不抽卡、不购买招募券、不保存招募结果。

当前卡池和免费招募历史：

```python
recruits = await client.shop.gacha_recruit_list()
```

返回结构：

```python
{
    "shop_recruits": [...],       # 当前可见招募/卡池
    "free_recruit_history": [...],
    "account_currency": {...},
    "count": 0,
    "free_history_count": 0,
    "extra": {},
}
```

预抽卡活动状态：

```python
beforehand = await client.shop.beforehand_gacha_get()
```

返回结构：

```python
{
    "beforehand_gacha": {...},
    "beforehand_gacha_history": {...},
    "extra": {},
}
```

自选 Pickup 招募状态：

```python
pickup = await client.shop.pickup_selection_gacha_get(shop_recruit_id)
```

参数 `shop_recruit_id` 来自招募列表里的卡池 ID。

返回结构：

```python
{
    "pickup_selection_gacha": {...},
    "shop_recruit": {...},
    "extra": {},
}
```
