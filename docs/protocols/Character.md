# Character 协议

角色模块相关协议。

字段结构仅作为 SDK DTO 与发包实现参考；实际可用性以真实网关返回为准。

## 协议列表

| 协议名 | 协议号 | 作用 | RequestClass | ResponseClass |
| --- | ---: | --- | --- | --- |
| `Character_List` | `2000` | 学生角色：获取列表数据 | `CharacterListRequest` | `CharacterListResponse` |
| `Character_Transcendence` | `2001` | 学生角色：突破/升星 | `CharacterTranscendenceRequest` | `CharacterTranscendenceResponse` |
| `Character_ExpGrowth` | `2002` | 学生角色：执行 ExpGrowth 流程 | `CharacterExpGrowthRequest` | `CharacterExpGrowthResponse` |
| `Character_FavorGrowth` | `2003` | 学生角色：执行 FavorGrowth 流程 | `CharacterFavorGrowthRequest` | `CharacterFavorGrowthResponse` |
| `Character_UpdateSkillLevel` | `2004` | 学生角色：更新SkillLevel | `CharacterSkillLevelUpdateRequest` | `CharacterSkillLevelUpdateResponse` |
| `Character_UnlockWeapon` | `2005` | 学生角色：执行 UnlockWeapon 流程 | `CharacterUnlockWeaponRequest` | `CharacterUnlockWeaponResponse` |
| `Character_WeaponExpGrowth` | `2006` | 学生角色：执行 WeaponExpGrowth 流程 | `CharacterWeaponExpGrowthRequest` | `CharacterWeaponExpGrowthResponse` |
| `Character_WeaponTranscendence` | `2007` | 学生角色：执行 WeaponTranscendence 流程 | `CharacterWeaponTranscendenceRequest` | `CharacterWeaponTranscendenceResponse` |
| `Character_SetFavorites` | `2008` | 学生角色：设置Favorites | `CharacterSetFavoritesRequest` | `CharacterSetFavoritesResponse` |
| `Character_SetCostume` | `2009` | 学生角色：设置Costume | `CharacterSetCostumeRequest` | `CharacterSetCostumeResponse` |
| `Character_BatchSkillLevelUpdate` | `2010` | 学生角色：BatchSkillLevel更新 | `CharacterBatchSkillLevelUpdateRequest` | `CharacterBatchSkillLevelUpdateResponse` |
| `Character_PotentialGrowth` | `2011` | 学生角色：执行 PotentialGrowth 流程 | `CharacterPotentialGrowthRequest` | `CharacterPotentialGrowthResponse` |

## 字段结构参考

### Character_List

- 协议号：`2000`
- 作用：学生角色：获取列表数据
- RequestClass：`CharacterListRequest`
- ResponseClass：`CharacterListResponse`
- 状态：已封装为 `client.character.list()`，live 验证通过。

#### Request 字段

无字段或未匹配到结构。

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `CharacterDBs` | `List<CharacterDB>?` | 角色数据列表。 |
| `TSSCharacterDBs` | `List<CharacterDB>?` | TSSCharacter 数据列表。 |
| `WeaponDBs` | `List<WeaponDB>?` | Weapon 数据列表。 |
| `CostumeDBs` | `List<CostumeDB>?` | Costume 数据列表。 |

### Character_Transcendence

- 协议号：`2001`
- 作用：学生角色：突破/升星
- RequestClass：`CharacterTranscendenceRequest`
- ResponseClass：`CharacterTranscendenceResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `TargetCharacterServerId` | `long` | 目标角色服务器 ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `CharacterDB` | `CharacterDB?` | 角色数据。 |
| `ParcelResultDB` | `ParcelResultDB?` | 奖励或道具变更结果。 |

### Character_ExpGrowth

- 协议号：`2002`
- 作用：学生角色：执行 ExpGrowth 流程
- RequestClass：`CharacterExpGrowthRequest`
- ResponseClass：`CharacterExpGrowthResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `TargetCharacterServerId` | `long` | 目标角色服务器 ID。 |
| `ConsumeRequestDB` | `ConsumeRequestDB?` | 消耗请求。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `CharacterDB` | `CharacterDB?` | 角色数据。 |
| `AccountCurrencyDB` | `AccountCurrencyDB?` | 账号货币数据。 |
| `ConsumeResultDB` | `ConsumeResultDB?` | 消耗结果。 |

### Character_FavorGrowth

- 协议号：`2003`
- 作用：学生角色：执行 FavorGrowth 流程
- RequestClass：`CharacterFavorGrowthRequest`
- ResponseClass：`CharacterFavorGrowthResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `TargetCharacterDBId` | `long` | 目标角色DB ID。 |
| `ConsumeItemDBIdsAndCounts` | `Dictionary<long, int>?` | 消耗道具 ID 与数量。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `CharacterDB` | `CharacterDB?` | 角色数据。 |
| `ConsumeStackableItemDBResult` | `List<ItemDB>?` | 可堆叠道具消耗结果。 |
| `ParcelResultDB` | `ParcelResultDB?` | 奖励或道具变更结果。 |

### Character_UpdateSkillLevel

- 协议号：`2004`
- 作用：学生角色：更新SkillLevel
- RequestClass：`CharacterSkillLevelUpdateRequest`
- ResponseClass：`CharacterSkillLevelUpdateResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `TargetCharacterDBId` | `long` | 目标角色DB ID。 |
| `SkillSlot` | `SkillSlot` | 技能槽位。 |
| `Level` | `int` | 等级。 |
| `ReplaceInfos` | `List<SelectTicketReplaceInfo>?` | 替换信息列表。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `CharacterDB` | `CharacterDB?` | 角色数据。 |
| `ParcelResultDB` | `ParcelResultDB?` | 奖励或道具变更结果。 |

### Character_UnlockWeapon

- 协议号：`2005`
- 作用：学生角色：执行 UnlockWeapon 流程
- RequestClass：`CharacterUnlockWeaponRequest`
- ResponseClass：`CharacterUnlockWeaponResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `TargetCharacterServerId` | `long` | 目标角色服务器 ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `WeaponDB` | `WeaponDB?` | 武器数据。 |

### Character_WeaponExpGrowth

- 协议号：`2006`
- 作用：学生角色：执行 WeaponExpGrowth 流程
- RequestClass：`CharacterWeaponExpGrowthRequest`
- ResponseClass：`CharacterWeaponExpGrowthResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `TargetCharacterServerId` | `long` | 目标角色服务器 ID。 |
| `ConsumeUniqueIdAndCounts` | `Dictionary<long, long>?` | 消耗对象唯一 ID 与数量。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ParcelResultDB` | `ParcelResultDB?` | 奖励或道具变更结果。 |

### Character_WeaponTranscendence

- 协议号：`2007`
- 作用：学生角色：执行 WeaponTranscendence 流程
- RequestClass：`CharacterWeaponTranscendenceRequest`
- ResponseClass：`CharacterWeaponTranscendenceResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `TargetCharacterServerId` | `long` | 目标角色服务器 ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ParcelResultDB` | `ParcelResultDB?` | 奖励或道具变更结果。 |

### Character_SetFavorites

- 协议号：`2008`
- 作用：学生角色：设置Favorites
- RequestClass：`CharacterSetFavoritesRequest`
- ResponseClass：`CharacterSetFavoritesResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ActivateByServerIds` | `Dictionary<long, bool>?` | ID 列表。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `CharacterDBs` | `List<CharacterDB>?` | 角色数据列表。 |

### Character_SetCostume

- 协议号：`2009`
- 作用：学生角色：设置Costume
- RequestClass：`CharacterSetCostumeRequest`
- ResponseClass：`CharacterSetCostumeResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `CharacterUniqueId` | `long` | 角色服务器唯一 ID。 |
| `CostumeIdToSet` | `Nullable<long>` | 要设置的服装 ID。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `SetCostumeDB` | `CostumeDB?` | 设置后的服装数据。 |
| `UnsetCostumeDB` | `CostumeDB?` | 解除后的服装数据。 |

### Character_BatchSkillLevelUpdate

- 协议号：`2010`
- 作用：学生角色：BatchSkillLevel更新
- RequestClass：`CharacterBatchSkillLevelUpdateRequest`
- ResponseClass：`CharacterBatchSkillLevelUpdateResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `TargetCharacterDBId` | `long` | 目标角色DB ID。 |
| `SkillLevelUpdateRequestDBs` | `List<SkillLevelBatchGrowthRequestDB>?` | SkillLevelUpdateRequest 数据列表。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `CharacterDB` | `CharacterDB?` | 角色数据。 |
| `ParcelResultDB` | `ParcelResultDB?` | 奖励或道具变更结果。 |

### Character_PotentialGrowth

- 协议号：`2011`
- 作用：学生角色：执行 PotentialGrowth 流程
- RequestClass：`CharacterPotentialGrowthRequest`
- ResponseClass：`CharacterPotentialGrowthResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `TargetCharacterDBId` | `long` | 目标角色DB ID。 |
| `PotentialGrowthRequestDBs` | `List<PotentialGrowthRequestDB>?` | PotentialGrowthRequest 数据列表。 |
| `ReplaceInfos` | `List<SelectTicketReplaceInfo>?` | 替换信息列表。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `CharacterDB` | `CharacterDB?` | 角色数据。 |
| `ParcelResultDB` | `ParcelResultDB?` | 奖励或道具变更结果。 |
