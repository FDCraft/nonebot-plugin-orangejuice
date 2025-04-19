import datetime
import json
import re
import time
from typing import Union

import asyncio
import aiohttp
from cachetools import TTLCache

from nonebot.adapters.onebot.v11 import GroupMessageEvent, PrivateMessageEvent, Message
from nonebot.matcher import Matcher
from nonebot.params import CommandArg

from .Ess import ess

mixers_dict = {
    "Air Raid": "空袭 +10%",
    "Amplify": "增幅 +10%",
    "Backtrack": "返回 +10%",
    "Bomber": "炸弹 +10%",
    "Charity": "恩惠 +0%",
    "Confusion": "混乱 +25%",
    "Freeze": "冰冻 +10%",
    "Minelayer": "布雷 +25%",
    "Miracle": "奇迹 +0%",
    "Random Warp": "随机传送 +25%",
    "Regeneration": "恢复 +0%",
    "Sprint": "疾走 +10%",
    "Treasure": "宝箱 +0%",
    "Healthy Boss": "BOSS HP+10 +25%",
    "Star-chaser": "追星者 +0%",
    "Beggar": "乞丐 +25%",
    "Aggressive Heroes": "玩家ATK+1 +0%",
    "Defensive Heroes": "玩家DEF+1 +0%",
    "Evasive Heroes": "玩家EVD+1 +0%",
    "Blazing": "爆燃 +10%",
    "Flipped": "翻转 +10%",
    "Menacing Boss": "BOSS ATK+1 +25%",
    "Hard-shelled Boss": "BOSS DEF+1 +25%",
    "Slippery Boss": "BOSS EVD+1 +25%",
    "Joker": "鬼牌 +0%",
    "Bankrupt": "破产 +25%",
    "Goo": "粘液 +25%",
    "Spores": "孢子 +10%",
    "": ""
}

class Mixer:
    def __init__(self):
        self.cache = TTLCache(maxsize=4, ttl=345600)

    @staticmethod
    def get_today_time() -> int:
        return int(time.mktime(datetime.date.today().timetuple()))
    
    @staticmethod
    def get_query_time() -> int:
        if int(time.time()) - (today_time := int(time.mktime(datetime.date.today().timetuple()))) >= 57600: # 5-18 17:00 -> 5-19 16:00 
            return today_time + 86400 + 57600
        else: # 5-18 15:00 -> 5.18 16:00
            return today_time + 57600
    
    async def get_data(self) -> Union[dict, None]:
        query_time = self.get_query_time()
        cache_key = str(query_time)
        last_cache_key = str(query_time - 86400)
        
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        async with aiohttp.ClientSession() as session:
            req = await session.get('https://orangejuice.wiki/w/api.php?format=json&action=query&prop=revisions&rvprop=content&rvslots=*&pageids=21473', timeout=300)
            if req.status == 200:
                json_data = await req.text()
                data = json.loads(json_data) # {{FrontMixer\n|mixer1=Flipped\n|mixer2=Amplify\n|mixer3=Slippery Boss\n}}<!--\n\n--><noinclude>[[Category:Main page templates]]</noinclude>
                raw = data['query']['pages']['21473']['revisions'][0]['slots']['main']['*']
                
                if self.cache.get(last_cache_key) and raw == self.cache[last_cache_key]: # Not Update
                    return None
                else:
                    self.cache[cache_key] = raw
                    return self.cache[cache_key]
            else:
                return None
    
    async def get_today_mixer(self) -> Union[dict, None]:
        PATTERN = re.compile(r'\{\{FrontMixer\n\|mixer1=(.*?)\n\|mixer2=(.*?)\n\|mixer3=(.*?)\n\}\}')
        
        raw = await self.get_data()
        
        if raw is None:
            return None
        else:
            searchObj = re.search(PATTERN, raw)
            return [searchObj.group(1), searchObj.group(2), searchObj.group(3)]

    async def mixer(self, matcher: Matcher, event: Union[GroupMessageEvent, PrivateMessageEvent], arg: Message = CommandArg()) -> None:
        if not ess.check(event, 'Mixer'):
            return None
        
        self.data = await self.get_data()

        if not self.data:
            await matcher.finish('诶鸭出错啦~')
            
        text: str = arg.extract_plain_text().replace(' ', '')

        prefix = f'当前混合器：' 

        today_mixer = await self.get_today_mixer()
        
        if today_mixer:
            if today_mixer[2] != '':
                await matcher.finish(prefix + f'\n「{mixers_dict[today_mixer[0]]}」, 「{mixers_dict[today_mixer[1]]}」, 「{mixers_dict[today_mixer[2]]}」')
            else:
                await matcher.finish(prefix + f'\n「{mixers_dict[today_mixer[0]]}」, 「{mixers_dict[today_mixer[1]]}」')
        else:
            await matcher.finish('这一天的混合器数据还没更新哦~')

mixer: Mixer = Mixer()

if __name__ == '__main__':
    result = asyncio.run(mixer.get_today_mixer())
    print(f'{mixers_dict[result[0]]}」, 「{mixers_dict[result[1]]}」, 「{mixers_dict[result[2]]}')