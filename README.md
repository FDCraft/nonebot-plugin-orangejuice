<div align="center">
  <a href="https://v2.nonebot.dev/store"><img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/nbp_logo.png" width="180" height="180" alt="NoneBotPluginLogo"></a>
  <br>
  <p><img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/NoneBotPlugin.svg" width="240" alt="NoneBotPluginText"></p>
</div>

<div align="center">
# nonebot-plugin-orangejuice

_✨ [Sorabot](https://100oj.com/zh/%E5%B7%A5%E5%85%B7/SoraBot%E4%BD%BF%E7%94%A8%E6%8C%87%E5%8D%97)的Nonebot实现✨_

<a href="./LICENSE">
    <img src="https://img.shields.io/github/license/FDCraft/nonebot-plugin-orangejuice.svg" alt="license">
</a>
<a href="https://pypi.python.org/pypi/nonebot-plugin-orangejuice">
    <img src="https://img.shields.io/pypi/v/nonebot-plugin-orangejuice.svg" alt="pypi">
</a>
<img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="python">

</div>

##  ⚠ 警告

本项目尚处于快速开发阶段，配置文件可能会经常变动，在更新版本前请务必做好数据的备份！

## 📖 介绍

[Sorabot](https://100oj.com/zh/%E5%B7%A5%E5%85%B7/SoraBot%E4%BD%BF%E7%94%A8%E6%8C%87%E5%8D%97)的Nonebot实现，提供 100% Orange Juice 的卡面查询、组卡器查询、战绩统计、表情短码与相关的娱乐功能。

## 💿 安装

<details open>
<summary>使用 nb-cli 安装</summary>
在 nonebot2 项目的根目录下打开命令行, 输入以下指令即可安装

    nb plugin install nonebot-plugin-orangejuice

</details>

<details>
<summary>使用包管理器安装</summary>
在 nonebot2 项目的插件目录下, 打开命令行, 根据你使用的包管理器, 输入相应的安装命令

<details>
<summary>pip</summary>

    pip install nonebot-plugin-orangejuice
</details>
<details>
<summary>pdm</summary>

    pdm add nonebot-plugin-orangejuice
</details>
<details>
<summary>poetry</summary>

    poetry add nonebot-plugin-orangejuice
</details>
<details>
<summary>conda</summary>

    conda install nonebot-plugin-orangejuice
</details>

打开 nonebot2 项目根目录下的 `pyproject.toml` 文件, 在 `[tool.nonebot]` 部分追加写入

    plugins = ["nonebot_plugin_orangejuice"]

</details>

## 🎉 .env 配置

| 配置项       | 说明                             | 默认值       |
| ------------ | -------------------------------- | ------------ |
| OJ_DATA_PATH | 储存插件用户信息与配置文件的目录 | 'data/100oj' |

## 🎉 使用

请参考[Sorabot](https://100oj.com/zh/%E5%B7%A5%E5%85%B7/SoraBot%E4%BD%BF%E7%94%A8%E6%8C%87%E5%8D%97)的文档，或输入 #help 指令来查看。

## 特别感谢

- [nonebot/nonebot2](https://github.com/nonebot/nonebot2)
- [Fruitbat Factory](https://fruitbatfactory.com/)
- [Sorabot](https://100oj.com/zh/%E5%B7%A5%E5%85%B7/SoraBot%E4%BD%BF%E7%94%A8%E6%8C%87%E5%8D%97)