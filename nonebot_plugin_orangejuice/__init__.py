from nonebot.plugin import PluginMetadata

__plugin_meta = PluginMetadata(
    name='100orangejuice',
    description='100orangejuice',
    usage= r'See Sorabot Docs.',
    type="application",
    supported_adapters={"~onebot.v11"},
    extra={
        'author': 'Polaris_Light',
        'version': '0.1.0',
        'priority': 10
    }
)

from nonebot import on_command

from .Card import card
from .Deck import deck
from .Le import lulu, nanako, nico
from .Stats import stats

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
    handlers=[stats.main]
)

on_command(
    '#deck=',
    priority=10,
    block=True,
    handlers=[deck]
)

on_command(
    '#lulu',
    aliases={'#幸运蛋'},
    priority=10,
    block=True,
    handlers=[lulu]
)

on_command(
    '#mw',
    aliases={'#奇迹漫步'},
    priority=10,
    block=True,
    handlers=[nico]
)

on_command(
    '#7',
    aliases={'#浮游炮'},
    priority=10,
    block=True,
    handlers=[nanako]
)



