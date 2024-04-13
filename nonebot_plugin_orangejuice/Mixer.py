import datetime
import json
import time
from typing import Union

import aiohttp
from cachetools import TTLCache

from nonebot.adapters.onebot.v11 import GroupMessageEvent, PrivateMessageEvent, Message
from nonebot.matcher import Matcher
from nonebot.params import CommandArg

from .Ess import ess

mixers_list = ["空袭 +10%","增幅 +10%","返回 +10%","炸弹 +10%","恩惠 +0%","混乱 +25%","冰冻 +10%","布雷 +25%","奇迹 +0%","随机传送 +25%","恢复 +0%","疾走 +10%","宝箱 +0%","BOSS HP+10 +25%","追星者 +0%","乞丐 +25%","玩家ATK+1 +0%","玩家DEF+1 +0%","玩家EVD+1 +0%","爆燃 +10%","翻转 +10%","BOSS ATK+1 +25%","BOSS DEF+1 +25%","BOSS EVD+1 +25%","鬼牌 +0%","破产 +25%","粘液 +25%","孢子 +10%",""]

class Mixer:
    def __init__(self):
        self.cache = TTLCache(maxsize=2, ttl=43200)

    def get_today_time(self) -> int:
        return int(time.mktime(datetime.date.today().timetuple())) + 57600
    
    async def get_data(self) -> dict:
        cache_key = "content_min_js"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        async with aiohttp.ClientSession() as session:
            req = await session.get('https://interface.100oj.com/mixer/js/content.min.js')
            if req.status == 200:
                json_data = await req.text()
                data = json.loads(json_data.replace('var ms = ', ''))
                self.cache[cache_key] = data
                return data
            else:
                return None

    async def mixer(self, matcher: Matcher, event: Union[GroupMessageEvent, PrivateMessageEvent], arg: Message = CommandArg()) -> None:
        if not ess.check(event, 'Mixer'):
            return None
        
        self.data = await self.get_data()

        if not self.data:
            await matcher.finish('诶鸭出错啦~')
            
        text: str = arg.extract_plain_text().replace(' ', '')
        day = min(int(text), 850) if (text := text[:3]).isdigit() else 2

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
                await matcher.finish(date + f'\n「{mixers_list[today_mixer[0]]}」, 「{mixers_list[today_mixer[1]]}」, 「{mixers_list[today_mixer[2]]}」')
            else:
                await matcher.finish(date + f'\n「{mixers_list[today_mixer[0]]}」, 「{mixers_list[today_mixer[1]]}」')
        else:
            await matcher.finish('数据库里还没有这一天的混合器数据哦~')

mixer: Mixer = Mixer()
