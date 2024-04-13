from typing import Union

from nonebot.adapters.onebot.v11 import Message, MessageSegment, GroupMessageEvent, PrivateMessageEvent
from nonebot.matcher import Matcher
from nonebot.params import CommandArg

from .Ess import ess

class Deck:
    def __init__(self) -> None:
        pass

    async def deck(self, matcher: Matcher, event: Union[GroupMessageEvent, PrivateMessageEvent], arg: Message = CommandArg()) -> None:
        if not ess.check(event, 'Deck'):
            return None

        deck = arg.extract_plain_text()

        if deck == '' or deck is None or len(deck) != 12:
            await matcher.finish('请输入正确的卡组编码~')

        img = f'https://interface.100oj.com/deck/render.php?deck={deck}'
        await matcher.send(MessageSegment.image(img))

deck = Deck()