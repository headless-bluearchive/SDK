# ContentSweep 协议

扫荡预设模块相关协议。

字段结构仅作为 SDK DTO 与发包实现参考；实际可用性以真实网关返回为准。

## 协议列表

| 协议名 | 协议号 | 作用 | RequestClass | ResponseClass |
| --- | ---: | --- | --- | --- |
| `ContentSweep_Request` | `27000` | 扫荡预设：请求 | `ContentSweepRequest` | `ContentSweepResponse` |
| `ContentSweep_MultiSweep` | `27001` | 扫荡预设：执行 MultiSweep 流程 | `ContentSweepMultiSweepRequest` | `ContentSweepMultiSweepResponse` |
| `ContentSweep_MultiSweepPresetList` | `27002` | 扫荡预设：MultiSweep预设列表 | `ContentSweepMultiSweepPresetListRequest` | `ContentSweepMultiSweepPresetListResponse` |
| `ContentSweep_SetMultiSweepPreset` | `27003` | 扫荡预设：设置MultiSweep预设 | `ContentSweepSetMultiSweepPresetRequest` | `ContentSweepSetMultiSweepPresetResponse` |
| `ContentSweep_SetMultiSweepPresetName` | `27004` | 扫荡预设：设置MultiSweep预设Name | `ContentSweepSetMultiSweepPresetNameRequest` | `ContentSweepSetMultiSweepPresetNameResponse` |

## 字段结构参考

### ContentSweep_Request

- 协议号：`27000`
- 作用：扫荡预设：请求
- RequestClass：`ContentSweepRequest`
- ResponseClass：`ContentSweepResponse`
- 状态：SDK 已封装为单关扫荡方法。调用方必须传 `confirm=True`，并自行确认 AP、次数、通关状态和用户授权。

#### SDK 方法

```python
result = await client.sweep.request(
    content=content_type,
    stage_id=stage_id,
    count=1,
    event_content_id=0,
    confirm=True,
)
```

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `Content` | `ContentType` | 内容类型。 |
| `StageId` | `long` | 关卡 ID。 |
| `EventContentId` | `long` | EventContent ID。 |
| `Count` | `long` | 数量。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ClearParcels` | `List<List<ParcelInfo>>?` | ClearParcels数据列表。 |
| `BonusParcels` | `List<ParcelInfo>?` | BonusParcels数据列表。 |
| `EventContentBonusParcels` | `List<List<ParcelInfo>>?` | EventContentBonusParcels数据列表。 |
| `ParcelResult` | `ParcelResultDB?` | 奖励或道具变更结果。 |
| `CampaignStageHistoryDB` | `CampaignStageHistoryDB?` | 战役关卡历史数据。 |

### ContentSweep_MultiSweep

- 协议号：`27001`
- 作用：扫荡预设：执行 MultiSweep 流程
- RequestClass：`ContentSweepMultiSweepRequest`
- ResponseClass：`ContentSweepMultiSweepResponse`
- 状态：SDK 已封装为多关扫荡方法。逆向可确认 `MultiSweepParameter` 包含 `EventContentId`、`ContentType`、`StageId`、`SweepCount`；调用方必须传 `confirm=True`，并自行确认 AP、次数、通关状态和用户授权。

#### SDK 方法

```python
result = await client.sweep.multi_sweep(
    [{"content_type": content_type, "stage_id": stage_id, "sweep_count": 1}],
    confirm=True,
)
```

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `MultiSweepParameters` | `IEnumerable<MultiSweepParameter>?` | 多次扫荡参数。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `ClearParcels` | `List<List<ParcelInfo>>?` | ClearParcels数据列表。 |
| `BonusParcels` | `List<ParcelInfo>?` | BonusParcels数据列表。 |
| `EventContentBonusParcels` | `List<List<ParcelInfo>>?` | EventContentBonusParcels数据列表。 |
| `ParcelResult` | `ParcelResultDB?` | 奖励或道具变更结果。 |
| `CampaignStageHistoryDBs` | `List<CampaignStageHistoryDB>?` | CampaignStageHistory 数据列表。 |

### ContentSweep_MultiSweepPresetList

- 协议号：`27002`
- 作用：扫荡预设：MultiSweep预设列表
- RequestClass：`ContentSweepMultiSweepPresetListRequest`
- ResponseClass：`ContentSweepMultiSweepPresetListResponse`
- 状态：SDK 已封装并通过 live 只读验证。

#### SDK 方法

```python
presets = await client.sweep.preset_list()
```

返回结构：

| 字段 | 说明 |
| --- | --- |
| `presets` | 多扫荡预设列表。 |
| `extra` | 服务端返回中的其他顶层字段。 |

#### Request 字段

无字段或未匹配到结构。

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `MultiSweepPresetDBs` | `IEnumerable<MultiSweepPresetDB>?` | MultiSweepPreset 数据列表。 |

### ContentSweep_SetMultiSweepPreset

- 协议号：`27003`
- 作用：扫荡预设：设置MultiSweep预设
- RequestClass：`ContentSweepSetMultiSweepPresetRequest`
- ResponseClass：`ContentSweepSetMultiSweepPresetResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `PresetId` | `long` | 预设 ID。 |
| `PresetName` | `string?` | 预设名称。 |
| `StageIds` | `IEnumerable<long>?` | ID 列表。 |
| `ParcelIds` | `IEnumerable<ParcelKeyPair>?` | ID 列表。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `MultiSweepPresetDBs` | `IEnumerable<MultiSweepPresetDB>?` | MultiSweepPreset 数据列表。 |

### ContentSweep_SetMultiSweepPresetName

- 协议号：`27004`
- 作用：扫荡预设：设置MultiSweep预设Name
- RequestClass：`ContentSweepSetMultiSweepPresetNameRequest`
- ResponseClass：`ContentSweepSetMultiSweepPresetNameResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `PresetId` | `long` | 预设 ID。 |
| `PresetName` | `string?` | 预设名称。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `MultiSweepPresetDBs` | `IEnumerable<MultiSweepPresetDB>?` | MultiSweepPreset 数据列表。 |
