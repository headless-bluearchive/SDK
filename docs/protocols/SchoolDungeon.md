# SchoolDungeon 协议

学院交流会模块相关协议。

字段结构仅作为 SDK DTO 与发包实现参考；实际可用性以真实网关返回为准。

## 每日任务影响

当前只保留 `SchoolDungeon_List` 查询，用于读取学院交流会关卡历史与状态。

完成学院交流会每日任务通常需要进入战斗或提交结算结果，这类协议属于会影响游戏公平性的范围，SDK 文档不保留。因此该模块会影响“完成学园交流会”类每日任务的自动完成，只能用于状态读取。

## 协议列表

| 协议名 | 协议号 | 作用 | RequestClass | ResponseClass |
| --- | ---: | --- | --- | --- |
| `SchoolDungeon_List` | `38000` | 学院交流会：获取列表数据 | `SchoolDungeonListRequest` | `SchoolDungeonListResponse` |

## 字段结构参考

### SchoolDungeon_List

- 协议号：`38000`
- 作用：学院交流会：获取列表数据
- RequestClass：`SchoolDungeonListRequest`
- ResponseClass：`SchoolDungeonListResponse`
- 状态：SDK 已封装为游戏页面状态读取方法；实际可用性仍以真实账号当前开放内容和网关返回为准。

#### Request 字段

无字段或未匹配到结构。

#### Response 字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `SchoolDungeonStageHistoryDBList` | `List<SchoolDungeonStageHistoryDB>?` | SchoolDungeon关卡历史DBList数据列表。 |
