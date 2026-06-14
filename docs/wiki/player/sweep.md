# 扫荡

扫荡模块目前只读多扫荡预设列表，不接战斗结果提交，也不伪造通关记录。

## 多扫荡预设

```python
presets = await client.sweep.preset_list()
```

返回：

| 字段 | 说明 |
| --- | --- |
| `presets` | `MultiSweepPresetDBs`。 |
| `extra` | 其它顶层字段。 |

后续如果接扫荡执行，也只会接官方已有通关记录后的入口，不接战斗结算、不接成绩提交。边界就摆在这里，别把 SDK 往奇怪方向拧。
