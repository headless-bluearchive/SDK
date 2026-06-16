# 官方资源数据

SDK 可以从游戏客户端使用的官方资源链路拉取 TableBundles。这个能力用于同步主数据，不依赖 SchaleDB、逆向调试目录或本地游戏目录。别再把反编译目录当运行依赖塞进 SDK 里了，库就该像个库。

## 准备数据

游戏功能方法不会在调用时偷偷下载几百 MB 的资源。外部程序可以在启动或设置页先检查，别让用户点个 MomoTalk 结果突然开始下 300MB：

```python
from HLBA import Client

client = Client()

status = client.data_status()
if not status["ready"]:
    result = await client.prepare_data()
```

`ExcelDB.db` 的 SQLCipher key/license 来自客户端 SQLCipher DLL 的固定 material，SDK 默认从 `config.official_data` 读取。调用方通常不需要先登录再准备官方数据。

`prepare_data()` 会按以下顺序解析版本：

1. 调用方显式传入的 `client_version` / `build_number`。
2. 当前 `profile` 里的 `client_version` / `app_version_code`。
3. Galaxy Store `com.nexon.bluearchivegalaxy` 的 `contentBinaryVersion`。

拿到版本后，SDK 会请求 Nexon patch version-check，再从返回的 `resource-data.json` 里定位并下载：

```text
Preload/TableBundles/ExcelDB.db
Preload/TableBundles/Excel.zip
```

默认下载到项目根目录的临时目录：

```text
temp/official_data/global/<client_version>/
```

可以通过环境变量覆盖：

```text
HEADLESS_BLUEARCHIVE_OFFICIAL_DATA_DIR
```

下载器会优先使用 HTTP Range 分片并发下载；如果官方 CDN 不支持 Range，会自动退回单连接流式下载。`workers` 可以按网络情况调整，常用值是 `4`、`8`、`16`。

```python
result = await client.prepare_data(
    download_large=True,
    workers=8,
)
```

只想先检查链路或只下载小文件时：

```python
await client.prepare_data(download_large=False)
```

这只会下载 `Excel.zip`，不会下载约 300MB 的 `ExcelDB.db`。

## 解析与清理

主数据解析完成后，精简 JSON 会写入：

```text
core/data/academy_messanger.json
core/data/academy_favor_schedule.json
core/data/official_data_manifest.json
```

`prepare_data()` 会在下载完成后尝试解析 `ExcelDB.db`。解析成功并通过检查后，SDK 会删除 `temp/official_data/global/<client_version>/` 下的下载文件，避免长期占用磁盘空间。

清理逻辑带路径保护，只允许删除 `temp/official_data` 内部的缓存目录。

## SQLCipher 解密

`ExcelDB.db` 是 SQLCipher 加密 SQLite，不是裸 SQLite 文件。SDK 不再使用 `CreatePassword("ExcelDB.db")` 作为数据库 key。当前使用客户端 SQLCipher DLL 中固定的 key/license，配置入口在：

```text
config/official_data.py
```

调用者一般不需要手动传 key/license：

```python
client = Client()
await client.prepare_data()
```

如果需要临时覆盖，可显式传入 `sqlcipher_key` / `sqlcipher_license`。

## SQLCipher 后端

`ExcelDB.db` 是 SQLCipher 加密 SQLite，不是裸 SQLite 文件。SDK 解析器会优先使用 Python SQLCipher 绑定：

```text
sqlcipher3.dbapi2
pysqlcipher3.dbapi2
```

如果本机没有 Python 绑定，也可以通过环境变量指定兼容的 `sqlcipher.dll`：

```text
HEADLESS_BLUEARCHIVE_SQLCIPHER_DLL
```

SQLCipher key/license 来自配置。SDK 不内置 DLL，也不会把 SQLCipher key/license 写入日志或测试输出。

如果没有可用后端，`prepare_data()` 不会伪造成功状态，返回值里会带上 `parser_error` 和下一步提示。

## 当前边界

当前 SDK 已完成官方源定位、版本检测、并发下载、SQLCipher 读取入口和 MomoTalk 相关 FlatBuffer 行解析，可从真实 `ExcelDB.db` 导出精简主数据。

MomoTalk 精确红点和可领取羁绊剧情会基于上述精简 JSON 计算。
