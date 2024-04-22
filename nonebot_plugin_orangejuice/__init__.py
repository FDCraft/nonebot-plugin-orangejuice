from nonebot.plugin import PluginMetadata

from .Config import Config

__plugin_meta__ = PluginMetadata(
    name='100orangejuice',
    description='100orangejuice',
    usage= r'See Sorabot Docs.',
    type="application",
    supported_adapters={"~onebot.v11"},
    homepage="https://github.com/FDCraft/nonebot-plugin-orangejuice",
    config=Config,
    extra={
        'author': 'Polaris_Light',
        'version': '0.11.0',
        'priority': 10
    }
)

import re

from nonebot import on_command, on_regex
from nonebot.matcher import Matcher

from .Ess import ess

from .Card import card
from .Deck import deck
from .Emote import emote
from .Le import le
from .Mixer import mixer
from .Stats import stats

@on_command('#help', aliases={'#帮助'}, priority=10, block=True).handle()
async def help(matcher: Matcher):
    help_msg = '''100OrangeJuice
    #ess help 基础管理模块帮助
    #card help 查卡帮助
    #icon help 查图标帮助
    #stat help 统计帮助
    #deck <code> 卡组查看
    #lulu 幸运蛋
    #mw [num] 奇迹漫步
    #7 浮游炮
    #zb <something> 占卜'''
    await matcher.finish(help_msg)

on_command(
    '#ess',
    aliases={'#Ess', '#Essential', '#essentilasx'},
    priority=10,
    block=True,
    handlers=[ess.ess]
)

on_command(
    '#card',
    priority=10,
    block=True,
    handlers=[card.card]
)

on_command(
    '#icon',
    priority=10,
    block=True,
    handlers=[card.icon]
)

on_command(
    '#stat',
    aliases={'#stats', '#sd'},
    priority=10,
    block=True,
    handlers=[stats.stats]
)

on_command(
    '#m',
    priority=10,
    block=True,
    handlers=[mixer.mixer]
)

on_command(
    '#deck',
    priority=10,
    block=True,
    handlers=[deck.deck]
)

on_command(
    '#lulu',
    aliases={'#幸运蛋'},
    priority=10,
    block=True,
    handlers=[le.lulu]
)

on_command(
    '#mw',
    aliases={'#奇迹漫步', '#喵呜'},
    priority=10,
    block=True,
    handlers=[le.nico]
)

on_command(
    '#7',
    aliases={'#浮游炮'},
    priority=10,
    block=True,
    handlers=[le.nanako]
)

on_command(
    '#zb',
    aliases={'#占卜'},
    priority=10,
    block=True,
    handlers=[le.divination]
)


on_regex(
    r"^\:[a-z0-9_]+\:$",
    flags=re.IGNORECASE,
    handlers=[emote.emote])


