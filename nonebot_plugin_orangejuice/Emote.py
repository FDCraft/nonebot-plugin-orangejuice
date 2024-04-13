import os
from pathlib import Path
from typing import Union

from nonebot.adapters.onebot.v11 import MessageSegment, GroupMessageEvent, PrivateMessageEvent
from nonebot.params import RegexStr
from nonebot.matcher import Matcher

from .Ess import ess

class Emote: 
    def __init__(self) -> None:
        pass

    async def emote(self, matcher: Matcher, event: Union[GroupMessageEvent, PrivateMessageEvent], key: str = RegexStr()) -> None:
        if not ess.check(event, 'Emote'):
            return None

        key = key.replace(':', '').lower()
        folder_path = os.path.join(os.path.dirname(__file__), 'resources', 'emotes')
        img_name = f'{key}.png'
        img = Path(folder_path) / img_name
        poppo = Path(folder_path) / 'poppo.png'
        try:
            await matcher.send(MessageSegment.image(img))
        except:
            await matcher.send(MessageSegment.image(poppo))

emote = Emote()