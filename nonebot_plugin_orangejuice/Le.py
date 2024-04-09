import random
import time
from typing import Union, List, Tuple

from nonebot import require, logger
from nonebot.adapters.onebot.v11 import Bot, Message, GroupMessageEvent, PrivateMessageEvent
from nonebot.exception import ActionFailed
from nonebot.matcher import Matcher
from nonebot.params import CommandArg

try:
    scheduler = require("nonebot_plugin_apscheduler").scheduler
except Exception:
    scheduler = None
    logger.warning("未安装定时插件依赖")

from .Config import plugin_config

from .Ess import ess
from .Card import card


class Check: 
    def __init__(self) -> None:
        self.cd = plugin_config.le_cd
        self.max_count = plugin_config.le_max
        self.user_cd = {}
        self.user_count = {}
        def reset_user_count():
            self.user_count = {}

        try:
            scheduler.add_job(reset_user_count, "cron", hour="0", id="clear_le_max_count")
        except ActionFailed as e:
            logger.warning(f"定时任务添加失败，{repr(e)}")
        
    def check_cd(self, event: Union[GroupMessageEvent, PrivateMessageEvent]) -> bool:
        if self.cd == 0:
            return False
        
        user_id = event.user_id
        current_time = int(time.time())
        
        if str(user_id) not in list(self.user_cd.keys()):
            self.user_cd[f"{user_id}"] = current_time
            return False
        
        delta_time = current_time - self.user_cd[f'{user_id}']
        
        if delta_time >= self.cd:
            self.user_cd[f'{user_id}'] = current_time
            return False
        else:
            return True
    
    def check_max(self, event: Union[GroupMessageEvent, PrivateMessageEvent]) -> bool:
        if self.max_count == 0:
            return False
        
        user_id = event.user_id
    
        if str(user_id) not in list(self.user_count.keys()):
            self.user_count[f"{user_id}"] = 0

        if self.user_count[f"{user_id}"] < self.max_count:
            self.user_count[f"{user_id}"] += 1
            return False
        else:
            return True
        
    def check(self, event: Union[GroupMessageEvent, PrivateMessageEvent]) -> bool:
        return check.check_cd(event) or check.check_max(event)

class Le:
    def __init__(self) -> None:
        pass

    async def lulu(self, matcher: Matcher, event: Union[GroupMessageEvent, PrivateMessageEvent]) -> None:
        if isinstance(event, GroupMessageEvent) and event.group_id in ess.config['modules']['Le']:
            return None
        
        if check.check(event):
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
        
        if check.check(event):
            return None

        points = [0, 0, 0]
        for i in range(0, 7):
            points[random.randint(0, 2)] += 1
        await matcher.finish(f'浮游炮展开结果：\nATK+{points[0]} DEF+{points[1]} EVD+{points[2]}')
    
    async def nico(self, matcher: Matcher, event: Union[GroupMessageEvent, PrivateMessageEvent], arg: Message = CommandArg()) -> None:
        if isinstance(event, GroupMessageEvent) and event.group_id in ess.config['modules']['Le']:
            return None
        
        if check.check(event):
            return None

        text = arg.extract_plain_text()
        num = min(int(text), 9) if (text := text[:1]).isdigit() and int(text) else 4
    
        ordinary_list = []
        for tuple in card.cardHyper:
            if tuple[3] == 'ordinary':
                ordinary_list.append(tuple)
    
        result = []
        for i in range(0, num):
            result.append('「' + random.choice(ordinary_list)[1] + '」')
        await matcher.finish(f'奇迹漫步结果：\n{", ".join(result)}')

    async def divination(self, bot: Bot, matcher: Matcher, event: Union[GroupMessageEvent, PrivateMessageEvent], arg: Message = CommandArg()) -> None:
        if isinstance(event, GroupMessageEvent) and event.group_id in ess.config['modules']['Le']:
            return None
        
        if check.check(event):
            return None
        
        arg = arg.extract_plain_text()
        now = time.localtime()
        seed = round(abs(hash("Polaris_Light" + str(now.tm_yday)+ str(now.tm_year) + "XYZ") / 3.0 + hash("QWERTY" + arg + str(event.user_id) + "0*8&6" + str(now.tm_mday) + "kjhg") / 3.0))
        random.seed(seed)

        divination_list: List[str] = ['大吉', '吉', '中吉', '小吉', '半吉', '末吉', '末小吉', '凶', '小凶', '半凶', '末凶', '大凶']
        result = random.choice(divination_list)

        if '女装' in arg:
            result = '必须大吉！建议马上开始'

        for name in bot.config.nickname:
            if name in arg:
                result = '你好像有那个大病'

        user_name = event.sender.card if event.sender.card != '' else event.sender.nickname
        now = time.localtime()
        await matcher.finish(f'今天是{now.tm_year}年{now.tm_mon}月{now.tm_mday}日\n{user_name}所求事项：【{arg}】\n\n结果：【{result}】')

check = Check()
le = Le()