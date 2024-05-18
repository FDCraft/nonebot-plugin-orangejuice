import os
import re
from pathlib import Path
from typing import Union, List

from nonebot import logger
from nonebot.adapters.onebot.v11 import MessageSegment, GroupMessageEvent, PrivateMessageEvent
from nonebot.params import EventPlainText
from nonebot.matcher import Matcher

from .Ess import ess

class Emote: 
    def __init__(self) -> None:
        pass

    async def emote(self, matcher: Matcher, event: Union[GroupMessageEvent, PrivateMessageEvent], msg: str = EventPlainText()) -> None:
        keys: List[str] = re.findall(r'\:([a-zA-Z0-9_]+)\:', msg)
        if len(keys) > 8 or keys == []:
            return None
        
        if not ess.check(event, 'Emote'):
            return None
        
        logger.info(f'Emote: {keys}')
        
        reply: List[MessageSegment] = []
        
        for key in keys:
            key = key.replace('\n', '').lower()
            folder_path = os.path.join(os.path.dirname(__file__), 'resources', 'emotes')
            img_name = f'{key}.png'
            img = Path(folder_path) / img_name
            poppo = Path(folder_path) / 'poppo.png'
            if os.path.exists(img):
                reply.append(MessageSegment.image(img))
            else:
                reply.append(MessageSegment.image(poppo))
                
        await matcher.send(reply)

emote = Emote()