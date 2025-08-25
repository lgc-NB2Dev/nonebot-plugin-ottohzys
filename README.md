<!-- markdownlint-disable MD031 MD033 MD036 MD041 -->

<div align="center">

<a href="https://v2.nonebot.dev/store">
  <img src="https://raw.githubusercontent.com/A-kirami/nonebot-plugin-template/resources/nbp_logo.png" width="180" height="180" alt="NoneBotPluginLogo">
</a>

<p>
  <img src="https://raw.githubusercontent.com/lgc-NB2Dev/readme/main/template/plugin.svg" alt="NoneBotPluginText">
</p>

# NoneBot-Plugin-ottoHzys

_♿ 大电老师活字印刷 ♿_

<img src="https://img.shields.io/badge/python-3.10+-blue.svg" alt="python">
<a href="https://github.com/astral-sh/uv">
  <img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json" alt="uv">
</a>
<a href="https://wakatime.com/badge/user/b61b0f9a-f40b-4c82-bc51-0a75c67bfccf/project/897d1918-c2d7-4e7c-b84c-b33ba640cbf2">
  <img src="https://wakatime.com/badge/user/b61b0f9a-f40b-4c82-bc51-0a75c67bfccf/project/897d1918-c2d7-4e7c-b84c-b33ba640cbf2.svg" alt="wakatime">
</a>

<br />

<a href="https://pydantic.dev">
  <img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/lgc-NB2Dev/readme/main/template/pyd-v1-or-v2.json" alt="Pydantic Version 1 Or 2" >
</a>
<a href="./LICENSE">
  <img src="https://img.shields.io/github/license/lgc-NB2Dev/nonebot-plugin-ottohzys.svg" alt="license">
</a>
<a href="https://pypi.python.org/pypi/nonebot-plugin-ottohzys">
  <img src="https://img.shields.io/pypi/v/nonebot-plugin-ottohzys.svg" alt="pypi">
</a>
<a href="https://pypi.python.org/pypi/nonebot-plugin-ottohzys">
  <img src="https://img.shields.io/pypi/dm/nonebot-plugin-ottohzys" alt="pypi download">
</a>

<br />

<a href="https://registry.nonebot.dev/plugin/nonebot-plugin-ottohzys:nonebot_plugin_ottohzys">
  <img src="https://img.shields.io/endpoint?url=https%3A%2F%2Fnbbdg.lgc2333.top%2Fplugin%2Fnonebot-plugin-ottohzys" alt="NoneBot Registry">
</a>
<a href="https://registry.nonebot.dev/plugin/nonebot-plugin-ottohzys:nonebot_plugin_ottohzys">
  <img src="https://img.shields.io/endpoint?url=https%3A%2F%2Fnbbdg.lgc2333.top%2Fplugin-adapters%2Fnonebot-plugin-ottohzys" alt="Supported Adapters">
</a>

</div>

## 📖 介绍

### 前言

由于我不是很了解抽象文化，所以本插件纯度可能不是很够，有什么问题或者建议可以 [联系我](#-联系)，或者直接 发 Issue！

由于原项目没有放 License，所以我也把本仓库的 License 删掉了，如果原作者有相关意见可以直接联系我。

## 💿 安装

以下提到的方法 任选**其一** 即可

<details open>
<summary>[推荐] 使用 nb-cli 安装</summary>
在 nonebot2 项目的根目录下打开命令行, 输入以下指令即可安装

```bash
nb plugin install nonebot-plugin-ottohzys
```

</details>

<details>
<summary>使用包管理器安装</summary>
在 nonebot2 项目的插件目录下, 打开命令行, 根据你使用的包管理器, 输入相应的安装命令

<details>
<summary>pip</summary>

```bash
pip install nonebot-plugin-ottohzys
```

</details>
<details>
<summary>pdm</summary>

```bash
pdm add nonebot-plugin-ottohzys
```

</details>
<details>
<summary>poetry</summary>

```bash
poetry add nonebot-plugin-ottohzys
```

</details>
<details>
<summary>conda</summary>

```bash
conda install nonebot-plugin-ottohzys
```

</details>

打开 nonebot2 项目根目录下的 `pyproject.toml` 文件, 在 `[tool.nonebot]` 部分的 `plugins` 项里追加写入

```toml
[tool.nonebot]
plugins = [
    # ...
    "nonebot_plugin_ottohzys"
]
```

</details>

## ⚙️ 配置

在 NoneBot2 项目的 `.env` 文件中添加下表中的必填配置

|              配置项               | 必填 |                                                      默认值                                                      |              说明              |
| :-------------------------------: | :--: | :--------------------------------------------------------------------------------------------------------------: | :----------------------------: |
|              `PROXY`              |  否  |                                                        无                                                        |       请求使用的代理地址       |
|     `OTTOHZYS_PACK_LIST_URL`      |  否  | [`...`](https://github.com/lgc-NB2Dev/nonebot-plugin-ottohzys/blob/master/nonebot_plugin_ottohzys/config.py#L19) | 获取在线语音包列表时使用的地址 |
| `OTTOHZYS_PACK_DOWNLOAD_BASE_URL` |  否  | [`...`](https://github.com/lgc-NB2Dev/nonebot-plugin-ottohzys/blob/master/nonebot_plugin_ottohzys/config.py#L24) |     下载语音包时使用的地址     |
|      `OTTOHZYS_DEFAULT_PACK`      |  否  |                                                      `otto`                                                      | 默认语音包，如不存在会自动下载 |

## 🎉 使用

直接使用指令 `hzys -h` 查看帮助

## 📞 联系

QQ：3076823485  
Telegram：[@lgc2333](https://t.me/lgc2333)  
吹水群：[168603371](https://qm.qq.com/q/EikuZ5sP4G)  
邮箱：<lgc2333@126.com>

## 💡 鸣谢

### [sakaneko117/HUOZI](https://github.com/sakaneko117/HUOZI) & [CwavGuy/HUOZI_aolianfeiallin.top](https://github.com/CwavGuy/HUOZI_aolianfeiallin.top) & [HanaYabuki/otto-hzys](https://github.com/HanaYabuki/otto-hzys)

- 造好的轮子

### [Rouphy](https://github.com/Rouphy)

- 插件点子

## 💰 赞助

**[赞助我](https://blog.lgc2333.top/donate)**

感谢大家的赞助！你们的赞助将是我继续创作的动力！

## 📝 更新日志

### 1.0.2

- 修复在新版 Alconna 中的参数默认值问题

### 1.0.1

- 修复小问题

### 1.0.0

- 重构项目，加入语音包支持

### 0.2.1

- 优化资源下载

### 0.2.0

- 适配 Pydantic V1 & V2
- 支持多平台

### 0.1.2

- 添加参数 `-N` (`--normalize`)，改名部分参数
- 修复一系列粗心大意导致的 Bug，我是废物

### 0.1.1

- 重构部分代码
