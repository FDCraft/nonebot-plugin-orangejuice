from typing import Union

from nonebot.adapters.onebot.v11 import GroupMessageEvent, PrivateMessageEvent, Message, MessageSegment
from nonebot.matcher import Matcher
from nonebot.params import CommandArg

async def deck(matcher: Matcher, event: Union[GroupMessageEvent, PrivateMessageEvent], arg: Message = CommandArg()) -> None:
    deck = arg.extract_plain_text()
    img = f'https://interface.100oj.com/deck/render.php?deck={deck}'
    await matcher.send(MessageSegment.image(img))