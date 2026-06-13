
<p align="center">
  <img src="logo.png" alt="deobf" width="500">
</p>

<p align="center">
  <a href="./LICENSE">
    <img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="License: MIT">
  </a>
  <a href="https://www.python.org/">
    <img src="https://img.shields.io/badge/python-3.10%2B-blue.svg" alt="Python Version">
  </a>
</p>

## 前提概要
此项目**目前**仅制作了国际服碧蓝档案(港澳台, asia, na, global, kr)的协议层的登录部分。

Headless Bluearchive Backend 是 `headless-bluearchive` 的 backend 包。在**不影响游戏公平性**的前提将 bluearchive 的登录和主网关发包封装成一个 Python 库，供 CLI、API 服务、GUI 或其他自动化程序复用。

调用方只需要引用库入口，不需要再处理协议构包和会话加密这些底层细节，项目中**不包含**战斗、提交成绩、竞技场等影响游戏公平性的发包。

> ⚠️ 本仓库**仅供学习与研究目的发布** —— 基于BlueArchive的底层架构，一份由互联网爱好者学习研究而产生的产物，您应该遵守其官方使用协定，如产生任何法律后果责任自负⚠️

## 快速了解
- 文档：[架构](docs/architecture.md) | [开发规范](docs/development.md) | [调用教程](docs/api)

## 许可
原始字节码未授予任何许可。本仓库中的所有逆向结果仅供研究与学习使用。

## 开挂死妈
本项目的初衷只是为了更好的服务ba玩家，而不是被拿去利用拿去翻牌透视和竞技场透视，除非你是[本心先生](https://www.bilibili.com/opus/1053758758567542800)。

## 细节

经过 claude fable 5 配合 x64dbg、IDA 和 Recaf 长达 5 秒的分析，claude 认为 BA 的主网关请求并不是补几个字段就能跑通的简单 HTTP replay。除了基础协议字段和请求体外，还叠加了 PacketCryptManager 外层封包、CRC、压缩、异或、1014 后 O22 会话语义、SessionKey 注入和请求体 AES 加密的组合流程。

此外，部分关键返回值还依赖经过 Themida 虚拟化保护的 NGS-X 服务组件 grap-communicator64.aes。被 Themida 保护后的 blob 确实已经烂到不适合人类直接复用，因此我们顺手还原了游戏本体源码和调用链逻辑，并在完成 Themida 脱壳与 devirtualization 后接入 Codex，以较低的 Tokens 成本完成了这一份负责加密、封包、解包和发送请求的客户端封装。
## 目录结构

```text
backend/
  HLBA.py            # SDK 对外入口
  core/              # 协议、schema、packet、crypto、gateway client、异常定义
  modules/
    auth/            # 登录服务
    runtime/         # Android profile、区域配置、运行态配置
    game/
      player/
        cafe/        
        ....         # 游戏发包
  config/            # 项目默认配置
  utils/             # 通用工具
  tests/             # 轻量测试
  docs/              # 架构、开发规范和调用文档
```

## 基础使用
- 我认为任何一个python开发者且脑子正常的人都知道你需要 `pip install -r requirements.txt` 下载依赖后这样子在你的项目中belike:

```python
from HLBA import Client

# region 可填：tw、asia、na、global、kr 默认 tw 如果你是傻逼连自己的号是什么区都不知道可以去死。 
client = Client(region="tw", debug=True)
result = client.login("email@example.com", "password")

print(result.account_id)
print(result.nickname)
print(result.friend_code)
```

## 更多支持
- 本项目还在早期开发阶段，百分之90的项目整理工作由claude+codex协助开发，如果你认为你是**残疾人**有任何问题不带任何日志和细节，那我批准你开issue了。

## 致谢

- 原始项目：**[BlueArchive](https://bluearchive.nexon.com/)**。
- 反混淆、符号还原与工程脚手架：**Claude** 在人工监督下完成。
- 重命名函数，恢复可读性：**Claude Sonnet**自主完成
- 仓库源代码分析，敏感信息审计：**ChatGPT**自主完成
- 仓库素材来源于网络，感谢特异人士，**这位面善又友善的朋友**

## 奇异搞笑
<p align="center">
    <img src="funny/claude2.gif" alt="claude" width="180">
    <img src="funny/deobf.jpg" alt="deobf" width="180">
    <img src="funny/protection.png" alt="protection" width="180">
    <img src="funny/hacker.jpg" alt="hacker" width="180">
    <img src="funny/claude.gif" alt="claude" width="180">
</p>
