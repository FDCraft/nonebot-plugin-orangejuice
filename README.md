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

## 📖 介绍

[Sorabot](https://100oj.com/zh/%E5%B7%A5%E5%85%B7/SoraBot%E4%BD%BF%E7%94%A8%E6%8C%87%E5%8D%97)的 Nonebot 实现，提供 100% Orange Juice 的卡面查询、组卡器查询、数据统计、表情短码与相关的娱乐功能。

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
| MATCH_SCORE | 查卡与查图标时模糊匹配的最低分数 | 80 |

## 🎉 使用

与 [Sorabot](https://100oj.com/zh/%E5%B7%A5%E5%85%B7/SoraBot%E4%BD%BF%E7%94%A8%E6%8C%87%E5%8D%97) 的功能大致相似，指令头均为 \#。

<details open>
<summary>单独的命令</summary>

| 命令             | 说明                               |
| --------------  | --------------------------------- |
| #help           | 查看帮助信息。                     |
| #card \<name\>  | 查询橙汁卡牌信息，支持模糊搜索。 部分别名（如泥头车 -> 亚里希安罗妮）会使用插件内置的正则匹配表强制匹配。  |
| #icon \<name\>  | 查询橙汁卡牌图标，支持模糊搜索。 部分别名（如泥头车 -> 亚里希安罗妮）会使用插件内置的正则匹配表强制匹配。  |
| #deck \<code\>  | 获取卡组图片。后跟 12 位卡组代码。  |
| #m \<count\>    | 查询当前混合器与未来混合器。        |
| #lulu           | 模拟露露的幸运蛋。                 |
| #7              | 模拟浮游炮展开。                   |
| #mw             | 模拟奇迹漫步。                     |
| :\<emote\>:     | 发送橙汁表情。                     |

</details>

<detials open>
<summary>橙汁数据查询</summary>

| 命令                                   | 说明                                                                                    |
| -------------------------------------  | --------------------------------------------------------------------------------------- |
| #stat                                  | 查看数据查询模块的帮助。                                                                   |
| #stat bind \<steam64id\>               | 用于将 steam 绑定到 qq。重复使用会更新绑定。                                                |
| #stat unbind                           | 删除自己的绑定。                                                                           |
| #stat me \[limit\]                     | 在绑定 steam 后，使用本命令来快速查询自己的数据。limit为显示的最高胜率角色数，可以不填，默认为5。|
| #stat \<steam64id\> \[limit\]          | 使用 steam64id 快速查询对应玩家的数据。                                                     |
| #stat \<@qq\> \[limit\]                | 通过 At 来查询对应玩家的统计数据。                                                          |
| #stat type \<id\>                      | 切换生成的统计图片样式。id目前可取0~7，其中0为初始样式。                                      |
| #stat pin \<id\>                       | 切换个人 pin 样式。                                                                        |
| #stats modify \<qq\> \<key\> \<value\> | 直接修改数据库中某个玩家的数据，用于给予 pin。仅 Bot 的所有者可用使用本命令。                   |

</detials>

<details open>
<summary>管理模块</summary>

此模块命令仅群管理与 Bot 的所有者可以使用。带 groupid 参数的命令都需要合适的权限。

| 命令                                                      | 说明                                                                           |
| -------------------------------------------------------  | ------------------------------------------------------------------------------ |
| #ess module\|-m enable\|-on \<modulename\> \[groupid\]   | 在群聊\[groupid\]开启名为\[modulename\]的模块。不填写\[groupid\]时默认使用本群id。 |
| #ess module\|-m disable\|-off \<modulename\> \[groupid\] | 在群聊\[groupid\]关闭名为\[modulename\]的模块。不填写\[groupid\]时默认使用本群id。 |
| #ess module\|-m list\|-l \[groupid\]                     | 列出群聊\[groupid]的模块列表。不填写\[groupid\]时默认使用本群id。                  |
| #ess mute \<qq\|@qq\> \[time\] \[reason\]                | 禁言\[qq\]。time 如为纯数字，则单位为s；接受 `数字 + s m h d`。                    |
| #ess save\|-s                                            | 将当前所有配置保存到本地文件。                                                    |
| #ess load\|-l                                            | 从本地文件重新载入全部配置。                                                      |

</details>

## 特别感谢

- [nonebot/nonebot2](https://github.com/nonebot/nonebot2)
- [Fruitbat Factory](https://fruitbatfactory.com/)
- [Sorabot](https://100oj.com/zh/%E5%B7%A5%E5%85%B7/SoraBot%E4%BD%BF%E7%94%A8%E6%8C%87%E5%8D%97)