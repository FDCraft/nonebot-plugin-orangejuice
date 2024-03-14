import random
from typing import Union

from nonebot.adapters.onebot.v11 import Message, GroupMessageEvent, PrivateMessageEvent
from nonebot.matcher import Matcher
from nonebot.params import CommandArg

from .Ess import ess
from .Card import card

class Le:
    def __init__(self) -> None:
        pass

    async def lulu(self, matcher: Matcher, event: Union[GroupMessageEvent, PrivateMessageEvent]) -> None:
        if isinstance(event, GroupMessageEvent) and event.group_id in ess.config['modules']['Le']:
            return None
        
        effect = random.randint(0, 2)
        if effect == 0:
            await matcher.finish(f'露露的幸运蛋结果：\n获得{random.randint(1, 6)*20}Stars')
        elif effect == 1:
            await matcher.finish('露露的幸运蛋结果：\n抽取五张卡')
        else:
            await matcher.finish('露露的幸运蛋结果：\n恢复所有HP，获得永久ATK/DEF/EVD+1')

    async def nanako(self, matcher: Matcher, event: Union[GroupMessageEvent, PrivateMessageEvent]) -> None:
        if isinstance(event, GroupMessageEvent) and event.group_id in ess.config['modules']['Le']:
            return None

        list1 = []
        for i in range(0, 2):
            a = random.randint(0, 7)
            list1.append(a)
        list1.sort()
        list1.append(7)

        points = []
        for i in range(len(list1)):
            b = list1[i] if i == 0 else list1[i] - list1[i-1]
            points.append(b)
        await matcher.finish(f'浮游炮展开结果：\nATK+{points[0]} DEF+{points[1]} EVD+{points[2]}')
    
    async def nico(self, matcher: Matcher, event: Union[GroupMessageEvent, PrivateMessageEvent], arg: Message = CommandArg()) -> None:
        if isinstance(event, GroupMessageEvent) and event.group_id in ess.config['modules']['Le']:
            return None

        text = arg.extract_plain_text()
        num = min(int(text), 8) if (text := text[:1]).isdigit() and int(text) else 4
    
        ordinary_list = []
        for tuple in card.cardHyper:
            if tuple[2] == 'ordinary':
                ordinary_list.append(tuple)
    
        result = []
        for i in range(0, num):
            result.append(random.choice(ordinary_list)[0])
        await matcher.finish(f'奇迹漫步结果：\n{", ".join(result)}')

    async def divination(self, matcher: Matcher, event: Union[GroupMessageEvent, PrivateMessageEvent], arg: Message = CommandArg()) -> None:
        if isinstance(event, GroupMessageEvent) and event.group_id in ess.config['modules']['Le']:
            return None


le = Le()