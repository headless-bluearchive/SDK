# 商店

商店先只封装读列表和 AP 购买。能花资源的接口必须显式确认，不搞“我只是运行了一下怎么石头没了”的惊喜。

## 列表

```python
shop = await client.shop.list()
```

也可以指定分类：

```python
shop = await client.shop.list(category_list=[1, 2])
```

返回：

| 字段 | 说明 |
| --- | --- |
| `shop_infos` | 商店商品信息。 |
| `eligma_history` | 神名精髓相关历史。 |
| `extra` | 其它顶层字段。 |

## 购买 AP

```python
result = await client.shop.buy_ap(
    shop_unique_id=shop_unique_id,
    purchase_count=1,
    confirm=True,
)
```

`confirm=True` 是故意设计的。AP 补充是资源消耗操作，外部程序必须显式确认。没有确认就会抛 `UnsafeOperationError`。
