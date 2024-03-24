import datetime
import json
import time
from typing import Union

import aiohttp

from nonebot.adapters.onebot.v11 import GroupMessageEvent, PrivateMessageEvent, Message
from nonebot.matcher import Matcher
from nonebot.params import CommandArg

from .Ess import ess

mixers_list = ["空袭","增幅","返回","炸弹","恩惠","混乱","冰冻","布雷","奇迹","随机传送","恢复","疾走","宝箱","BOSS HP+10","追星者","乞丐","玩家ATK+1","玩家DEF+1","玩家EVD+1","爆燃","翻转","BOSS ATK+1","BOSS DEF+1","BOSS EVD+1","鬼牌","破产","粘液","孢子",""]

class Mixer:
    def __init__(self) -> None:
        pass

    def get_today_time(self) -> int:
        return int(time.mktime(datetime.date.today().timetuple())) + 57600
    
    async def get_data(self) -> None:
        async with aiohttp.ClientSession() as session:
            req = await session.get('https://interface.100oj.com/mixer/js/content.min.js')
        if req.status != 200:
            return None
        else:
            json_data = await req.text()
            self.data: dict = json.loads(json_data.replace('var ms = ', ''))

    async def mixer(self, matcher: Matcher, event: Union[GroupMessageEvent, PrivateMessageEvent], arg: Message = CommandArg()) -> None:
        if isinstance(event, GroupMessageEvent) and event.group_id in ess.config['modules']['Mixer']:
            return None
        
        await self.get_data()

        if not self.data:
            await matcher.finish('诶鸭出错啦~')
            
        text: str = arg.extract_plain_text().replace(' ', '')
        day = min(int(text), 60) if (text := text[:2]).isdigit() else 2

        if day == 1:
            date = '昨日混合器：'
        elif day == 2:
            date = '今日混合器：'
        elif day == 0:
            date = f'2日前混合器：' 
        else:
            date = f'{day - 2}日后混合器：'
            

        query_time = self.get_today_time() + (day - 1) * 86400
        key = str(hex(query_time))

        today_mixer = self.data.get(key, None)
        if today_mixer:
            if len(today_mixer) == 3:
                await matcher.finish(date + f'\n[{mixers_list[today_mixer[0]]}], [{mixers_list[today_mixer[1]]}], [{mixers_list[today_mixer[2]]}]')
            else:
                await matcher.finish(date + f'\n[{mixers_list[today_mixer[0]]}], [{mixers_list[today_mixer[1]]}]')
        else:
            await matcher.finish('诶鸭出错啦~')

mixer: Mixer = Mixer()
