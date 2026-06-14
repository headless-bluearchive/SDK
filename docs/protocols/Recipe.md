# Recipe 协议

Recipe 模块相关协议。

字段结构仅作为 SDK DTO 与发包实现参考；实际可用性以真实网关返回为准。

## 协议列表

| 协议名 | 协议号 | 作用 | RequestClass | ResponseClass |
| --- | ---: | --- | --- | --- |
| `Recipe_Craft` | `11000` | 配方：执行 Craft 流程 | `RecipeCraftRequest` | `RecipeCraftResponse` |

## 字段结构参考

### Recipe_Craft

- 协议号：`11000`
- 作用：配方：执行 Craft 流程
- RequestClass：`RecipeCraftRequest`
- ResponseClass：`RecipeCraftResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `RecipeCraftUniqueId` | `long` | RecipeCraft唯一 ID。 |
| `RecipeIngredientUniqueId` | `long` | RecipeIngredient唯一 ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ParcelResultDB` | `ParcelResultDB?` | 奖励或道具变更结果。 |
| `EquipmentConsumeResultDB` | `ConsumeResultDB?` | 装备消耗结果数据。 |
| `ItemConsumeResultDB` | `ConsumeResultDB?` | 道具消耗结果数据。 |
