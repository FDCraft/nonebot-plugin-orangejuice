import json
import os
import re
from typing import Dict, List, Tuple, Union

import aiomysql
from fuzzywuzzy import fuzz

from nonebot import get_driver
from nonebot.adapters.onebot.v11 import Bot, Message, MessageSegment, GroupMessageEvent, PrivateMessageEvent 
from nonebot.matcher import Matcher
from nonebot.params import CommandArg

from .Config import plugin_config
from .Ess import ess

BaseClass = Tuple[Tuple[str, str, str, str]]

tables = ['cardDeck', 'cardHyper', 'cardOther', 'unitCharacter', 'unitNPC'] # cardBossSkill is special so not in here.
groups = {'原版': 'ordinary', '合作': 'coop', '赏金': 'bounty', '其他': 'other'}

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
            
        await cursor.execute(f"SELECT i18nkey, name_, nameEn, descr, cost, level_, type_, isHyper, isHyperOnly FROM cardBossSkill")
        self.cardBossSkill = await cursor.fetchall()
        
        self.db.close()
        
        regex_path = os.path.join(os.path.dirname(__file__), 'resources', 'card', 'regex.json')
        self.regex: Dict[str, str] = json.load(open(regex_path, 'r', encoding='utf-8'))
        
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
        
    def match(self, name: str, target_group: str = None, target_table: str = None, search_boss: bool = False) -> List[Tuple[str, str, str, str, str, int]]:
        
        def B2Q(string: str):
            return string.replace('~', '～').replace('&', '＆').replace('(', '（').replace(')', '）').replace('!', '！')
        
        result = [] # [(id, name, name_En, group, table, score), (id, name, name_En, group, table, score, descr, cost, level, type, isHyper)]
        force_flag = False

        for regex, key in self.regex.items():
           if re.match(regex, name, re.I):
               name = key
               force_flag = True
               
        
        for table in tables:
            if target_table and target_table != table:
                continue
            table_attr: BaseClass = getattr(self, table)
            for tuple in table_attr:
                if target_group:
                    if tuple[3] != target_group:
                        continue
                    score = max(fuzz.ratio(B2Q(name), tuple[1]), fuzz.ratio(name.lower(), tuple[2].lower()))
                    if (not force_flag and score >= plugin_config.match_score and score > 0) or (force_flag and score == 100):
                        result.append((tuple[0], tuple[1], tuple[2], tuple[3], table, score))
                else:
                    score = max(fuzz.ratio(B2Q(name), tuple[1]), fuzz.ratio(name, tuple[2]))
                    if (not force_flag and score >= plugin_config.match_score and score > 0) or (force_flag and score == 100):
                        result.append((tuple[0], tuple[1], tuple[2], tuple[3], table, score))
                        
        if search_boss and (not target_table or target_table == 'cardBossSkill'):
            for tuple in self.cardBossSkill:
                score = max(fuzz.ratio(B2Q(name), tuple[1]), fuzz.ratio(name.lower(), tuple[2].lower()))
                if (not force_flag and score >= plugin_config.match_score and score > 0) or (force_flag and score == 100):
                    result.append((tuple[0], tuple[1], tuple[2], 'coop', 'cardBossSkill', score, tuple[3], tuple[4], tuple[5], tuple[6], tuple[7]))
        
        result.sort(key=lambda tuple: (tuple[5], (tables + ['cardBossSkill'])[::-1].index(tuple[4]), list(groups.values())[::-1].index(tuple[3])), reverse=True)
        return result
    
    async def forward_send(self, bot: Bot, event: Union[GroupMessageEvent, PrivateMessageEvent], messages: List[MessageSegment]) -> None:
        if isinstance(event, GroupMessageEvent):
            await bot.send_group_forward_msg(
                group_id=event.group_id,
                    messages=[
                        {
                            "type": "node",
                            "data": {
                                "name": "花花",
                                "uin": bot.self_id,
                                "content": msg,
                            },
                        }
                        for msg in messages
                    ],
                )
        else:
            await bot.send_private_forward_msg(
                user_id=event.user_id,
                messages=[
                    {
                        "type": "node",
                        "data": {
                            "name": "花花",
                            "uin": bot.self_id,
                            "content": msg,
                        },
                    }
                    for msg in messages
                ],
            )

    async def card(self, bot: Bot, matcher: Matcher, event: Union[GroupMessageEvent, PrivateMessageEvent], arg: Message = CommandArg()) -> None:
        try:
            if not ess.check(event, 'Card'):
                return None
            args = arg.extract_plain_text().split(' ')

            if args == [''] or args is None or args[0] == 'help':
                await self.help(matcher)
                return None
            
            # input
            name = args[0]
            target_group = None
            target_table = None
            
            # input parse
            for arg in args:
                if arg in groups.keys():
                    target_group = groups[arg]
                elif arg in groups.values():
                    target_group = arg
                elif arg in tables:
                    target_table = arg
                    
            result = self.match(name, target_group, target_table, True)
            
            if result == []:
                await matcher.send('没有这张卡啦！')
                return None
            
            messages: List[MessageSegment] = []
            count = 0
            for tuple in result:
                count += 1
                if count > 20:
                    messages = [MessageSegment.text(f'匹配结果过多，仅显示前20张卡。')] + messages
                    break
                messages.append(MessageSegment.text(f'{count}.\n内部ID：{tuple[0]}\n中文名：{tuple[1]}\n英文名：{tuple[2]}\n组别：{tuple[3]}\n所在表：{tuple[4]}\n匹配分数：{tuple[5]}'))
                if tuple[4].startswith('unit'):
                    img = f'https://interface.100oj.com/interface/render/cardunit.php?key={tuple[0]}'
                    messages.append(MessageSegment.image(img))
                elif tuple[4] in tables:
                    img = f'https://interface.100oj.com/interface/render/{tuple[4].lower()}.php?key={tuple[0]}'
                    messages.append(MessageSegment.image(img))
                else:
                    messages.append(MessageSegment.text(f'「{tuple[1]}」({"[H] " if tuple[10] else ""}{tuple[9].upper()} {tuple[8]}/{tuple[7]})\n{tuple[6]}'))
                    
            await self.forward_send(bot, event, messages)
                          
        except Exception as e:
            await matcher.send('诶鸭出错啦~')
            raise e

    async def icon(self, bot: Bot, matcher: Matcher, event: Union[GroupMessageEvent, PrivateMessageEvent], arg: Message = CommandArg()) -> None:
        try:
            if not ess.check(event, 'Card'):
                return None
            args = arg.extract_plain_text().split(' ')

            if args == [''] or args is None or args[0] == 'help':
                await self.help(matcher)
                return None

            # input
            name = args[0]
            target_group = None
            target_table = None
            
            # input parse
            for arg in args:
                if arg in list(groups.keys()):
                    target_group = groups[arg]
                elif arg in list(groups.values()):
                    target_group = arg
                elif arg in tables:
                    target_table = arg
                    
            result = self.match(name, target_group, target_table, False)
            
            messages: List[MessageSegment] = []
            count = 0
            for tuple in result:
                count += 1
                messages.append(MessageSegment.text(f'{count}.\n内部ID：{tuple[0]}\n中文名：{tuple[1]}\n英文名：{tuple[2]}\n组别：{tuple[3]}\n所在表：{tuple[4]}\n匹配分数：{tuple[5]}'))
                img = f'https://interface.100oj.com/interface/util/icon.php?key={tuple[0]}&size=256&lossless=true'
                messages.append(MessageSegment.image(img))
                
            await self.forward_send(bot, event, messages)
                    
        except Exception as e:
            await matcher.send('诶鸭出错啦~')
            raise e

card: Card = Card()
driver = get_driver()

@driver.on_startup
async def init_card() -> None:
    await card.get_data()