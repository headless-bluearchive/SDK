# TimeAttackDungeon 协议

合同火力演习模块相关协议。

字段结构仅作为 SDK DTO 与发包实现参考；实际可用性以真实网关返回为准。

## 协议列表

| 协议名 | 协议号 | 作用 | RequestClass | ResponseClass |
| --- | ---: | --- | --- | --- |
| `TimeAttackDungeon_Lobby` | `39000` | 综合战术考试：获取或进入模块大厅 | `TimeAttackDungeonLobbyRequest` | `TimeAttackDungeonLobbyResponse` |
| `TimeAttackDungeon_Sweep` | `39004` | 综合战术考试：执行扫荡 | `TimeAttackDungeonSweepRequest` | `TimeAttackDungeonSweepResponse` |
| `TimeAttackDungeon_Login` | `39006` | 综合战术考试：进入模块并同步基础数据 | `TimeAttackDungeonLoginRequest` | `TimeAttackDungeonLoginResponse` |

## 字段结构参考

### TimeAttackDungeon_Lobby

- 协议号：`39000`
- 作用：综合战术考试：获取或进入模块大厅
- RequestClass：`TimeAttackDungeonLobbyRequest`
- ResponseClass：`TimeAttackDungeonLobbyResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

无字段或未匹配到结构。

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `RoomDBs` | `Dictionary<long, TimeAttackDungeonRoomDB>?` | Room 数据列表。 |
| `PreviousRoomDB` | `TimeAttackDungeonRoomDB?` | PreviousRoom数据。 |
| `ParcelResultDB` | `ParcelResultDB?` | 奖励或道具变更结果。 |
| `AchieveSeasonBestRecord` | `bool` | 是否刷新赛季最佳记录。 |
| `SeasonBestRecord` | `long` | 赛季最佳记录。 |

### TimeAttackDungeon_Sweep

- 协议号：`39004`
- 作用：综合战术考试：执行扫荡
- RequestClass：`TimeAttackDungeonSweepRequest`
- ResponseClass：`TimeAttackDungeonSweepResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `SweepCount` | `long` | 数量。 |

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `Rewards` | `List<List<ParcelInfo>>?` | 奖励数据列表。 |
| `ParcelResultDB` | `ParcelResultDB?` | 奖励或道具变更结果。 |
| `RoomDB` | `TimeAttackDungeonRoomDB?` | Room数据。 |

### TimeAttackDungeon_Login

- 协议号：`39006`
- 作用：综合战术考试：进入模块并同步基础数据
- RequestClass：`TimeAttackDungeonLoginRequest`
- ResponseClass：`TimeAttackDungeonLoginResponse`
- 状态：结构参考，发包前需要用真实网关响应验证。

#### Request 字段

无字段或未匹配到结构。

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `PreviousRoomDB` | `TimeAttackDungeonRoomDB?` | PreviousRoom数据。 |
