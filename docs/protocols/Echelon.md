# Echelon 协议

Echelon 模块相关协议。

字段结构仅作为 SDK DTO 与发包实现参考；实际可用性以真实网关返回为准。

## 协议列表

| 协议名 | 协议号 | 作用 | RequestClass | ResponseClass |
| --- | ---: | --- | --- | --- |
| `Echelon_List` | `5000` | 编队：获取列表数据 | `EchelonListRequest` | `EchelonListResponse` |
| `Echelon_Save` | `5001` | 编队：保存状态 | `EchelonSaveRequest` | `EchelonSaveResponse` |
| `Echelon_PresetList` | `5002` | 编队：预设列表 | `EchelonPresetListRequest` | `EchelonPresetListResponse` |
| `Echelon_PresetSave` | `5003` | 编队：保存预设 | `EchelonPresetSaveRequest` | `EchelonPresetSaveResponse` |
| `Echelon_PresetGroupRename` | `5004` | 编队：预设Group重命名 | `EchelonPresetGroupRenameRequest` | `EchelonPresetGroupRenameResponse` |

## 字段结构参考

### Echelon_List

- 协议号：`5000`
- 作用：编队：获取列表数据
- RequestClass：`EchelonListRequest`
- ResponseClass：`EchelonListResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

无字段或未匹配到结构。

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `EchelonDBs` | `List<EchelonDB>?` | Echelon 数据列表。 |

### Echelon_Save

- 协议号：`5001`
- 作用：编队：保存状态
- RequestClass：`EchelonSaveRequest`
- ResponseClass：`EchelonSaveResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `EchelonDB` | `EchelonDB?` | 编队数据。 |
| `AssistUseInfos` | `List<ClanAssistUseInfo>?` | AssistUseInfos数据列表。 |
| `IsPractice` | `bool` | 布尔状态。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `EchelonDB` | `EchelonDB?` | 编队数据。 |

### Echelon_PresetList

- 协议号：`5002`
- 作用：编队：预设列表
- RequestClass：`EchelonPresetListRequest`
- ResponseClass：`EchelonPresetListResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `EchelonExtensionType` | `EchelonExtensionType` | 编队扩展类型。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `PresetGroupDBs` | `EchelonPresetGroupDB[]?` | PresetGroup 数据列表。 |

### Echelon_PresetSave

- 协议号：`5003`
- 作用：编队：保存预设
- RequestClass：`EchelonPresetSaveRequest`
- ResponseClass：`EchelonPresetSaveResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `PresetDB` | `EchelonPresetDB?` | 预设数据。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `PresetDB` | `EchelonPresetDB?` | 预设数据。 |

### Echelon_PresetGroupRename

- 协议号：`5004`
- 作用：编队：预设Group重命名
- RequestClass：`EchelonPresetGroupRenameRequest`
- ResponseClass：`EchelonPresetGroupRenameResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `PresetGroupIndex` | `int` | 预设Group索引索引。 |
| `ExtensionType` | `EchelonExtensionType` | 扩展类型。 |
| `PresetGroupLabel` | `string?` | 预设分组标签。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `PresetGroupDB` | `EchelonPresetGroupDB?` | 预设Group数据。 |
