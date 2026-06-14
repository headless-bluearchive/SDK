# WeekDungeon 协议

WeekDungeon 模块相关协议。

字段结构仅作为 SDK DTO 与发包实现参考；实际可用性以真实网关返回为准。

## 协议列表

| 协议名 | 协议号 | 作用 | RequestClass | ResponseClass |
| --- | ---: | --- | --- | --- |
| `WeekDungeon_List` | `23000` | 悬赏通缉/日常副本：获取列表数据 | `WeekDungeonListRequest` | `WeekDungeonListResponse` |

## 字段结构参考

### WeekDungeon_List

- 协议号：`23000`
- 作用：悬赏通缉/日常副本：获取列表数据
- RequestClass：`WeekDungeonListRequest`
- ResponseClass：`WeekDungeonListResponse`
- 状态：已封装为 `client.week_dungeon.list()`，live 验证通过。

#### Request 字段

无字段或未匹配到结构。

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `AdditionalStageIdList` | `List<long>?` | Additional关卡IdList数据列表。 |
| `WeekDungeonStageHistoryDBList` | `List<WeekDungeonStageHistoryDB>?` | WeekDungeon关卡历史DBList数据列表。 |
