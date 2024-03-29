from typing import Tuple, Union

import aiomysql
import asyncio
from fuzzywuzzy import fuzz

from nonebot import logger
from nonebot.adapters.onebot.v11 import Message, MessageSegment, GroupMessageEvent, PrivateMessageEvent 
from nonebot.matcher import Matcher
from nonebot.params import CommandArg

from .Config import plugin_config
from .Ess import ess

BaseClass = Tuple[Tuple[str, str, str, str]]

tables = ['cardDeck', 'cardHyper', 'cardOther', 'unitCharacter', 'unitNPC']
groups = {'原版': 'ordinary', '合作': 'coop', '赏金': 'bounty', '其他': 'other'}

def B2Q(string: str):
    return string.replace('~', '～').replace('&', '＆').replace('(', '（').replace(')', '）').replace('!', '！')

class Card:
    def __init__(self) -> None:
        pass
    async def get_data(self):
        self.db = await aiomysql.connect(
            host='47.242.108.196',
            port=3306,
            user='guest',
            password='Sumika!System2',
            db='data_oj'
        )

        cursor = await self.db.cursor()

        for table in tables:
            await cursor.execute(f"SELECT i18nkey, name_, nameEn, groupData FROM {table}")
            setattr(self, table, await cursor.fetchall())
        
        self.db.close()
        return self

    async def help(self, matcher: Matcher):
        help_msg: str = '''橙汁查卡
    #card <name> [group] [table]
    查卡
    #icon <name> [group] [table]
    查图标
    name为中文卡名或者使用下划线的英文卡名
    group为 原版/合作/赏金/其他 或不填
    table为卡表，具体见数据库'''
        await matcher.send(help_msg)

    async def card(self, matcher: Matcher, event: Union[GroupMessageEvent, PrivateMessageEvent], arg: Message = CommandArg()) -> None:
        try:
            if isinstance(event, GroupMessageEvent) and event.group_id in ess.config['modules']['Card']:
                return None
            args = arg.extract_plain_text().split(' ')

            if args == [''] or args is None or args[0] == 'help':
                await self.help(matcher)
                return None

            name = args[0]
            target_group = None
            target_table = None

            for arg in args:
                if arg in groups.keys():
                    target_group = groups[arg]
                elif arg in groups.values():
                    target_group = arg
                elif arg in tables:
                    target_table = arg   

            id = ''
            now_score = 0
            for table in tables:
                if target_table and target_table != table:
                    continue
                table_attr: BaseClass = getattr(self, table)
                for tuple in table_attr:
                    if target_group:
                        if tuple[3] != target_group:
                            continue
                        score = max(fuzz.ratio(B2Q(name), tuple[1]), fuzz.ratio(name, tuple[2]))
                        if score > now_score:
                            id = tuple[0]
                            now_table = table
                            now_score = score
                    else:
                        score = max(fuzz.ratio(B2Q(name), tuple[1]), fuzz.ratio(name, tuple[2])) + (1 if tuple[3] == 'ordinary' else 0)
                        if score > now_score:
                            id = tuple[0]
                            now_table = table
                            now_score = score
            
            if now_score < plugin_config.match_socre:
                await matcher.send('没有这张卡啦~')
                return None

            if now_table.startswith('unit'):
                img = f'http://interface.100oj.com/interface/render/cardunit.php?key={id}'
                await matcher.send(MessageSegment.image(img))
                return None
            else:
                img = f'http://interface.100oj.com/interface/render/{now_table.lower()}.php?key={id}'
                await matcher.send(MessageSegment.image(img))
                return None                               

        except:
            await matcher.finish('诶鸭出错啦~')

    async def icon(self, matcher: Matcher, event: Union[GroupMessageEvent, PrivateMessageEvent], arg: Message = CommandArg()) -> None:
        try:
            if isinstance(event, GroupMessageEvent) and event.group_id in ess.config['modules']['Card']:
                return None
            args = arg.extract_plain_text().split(' ')

            if args == [''] or args is None or args[0] == 'help':
                await self.help(matcher)
                return None


            name = args[0]
            target_group = None
            target_table = None

            for arg in args:
                if arg in groups.keys():
                    target_group = groups[arg]
                elif arg in groups.values():
                    target_group = arg
                elif arg in tables:
                    target_table = arg   

            id = ''
            now_score = 0
            for table in tables:
                if target_table and target_table != table:
                    continue
                table_attr: BaseClass = getattr(self, table)
                for tuple in table_attr:
                    if target_group:
                        if tuple[3] != target_group:
                            continue
                        score = max(fuzz.ratio(B2Q(name), tuple[1]), fuzz.ratio(name, tuple[2]))
                        if score > now_score:
                            id = tuple[0]
                            now_score = score
                    else:
                        score = max(fuzz.ratio(B2Q(name), tuple[1]), fuzz.ratio(name, tuple[2])) + (1 if tuple[3] == 'ordinary' else 0)
                        if score > now_score:
                            id = tuple[0]
                            now_score = score
            
            if now_score < plugin_config.match_socre:
                await matcher.send('没有这张卡啦~')
                return None

            img = f'http://interface.100oj.com/interface/util/icon.php?key={id}&size=256&lossless=true'
            await matcher.send(MessageSegment.image(img))
            return None                     
        except:
            await matcher.finish('诶鸭出错啦~')

card = asyncio.run(Card().get_data())