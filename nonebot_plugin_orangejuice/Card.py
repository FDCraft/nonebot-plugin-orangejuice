from typing import Tuple, Union

import pymysql

from nonebot.adapters.onebot.v11 import Message, MessageSegment, GroupMessageEvent, PrivateMessageEvent 
from nonebot.matcher import Matcher
from nonebot.params import CommandArg

from .Ess import ess

BaseClass = Tuple[Tuple[str]]

tables = ['cardDeck', 'cardHyper', 'cardOther', 'unitCharacter', 'unitNPC']
groups = {'原版': 'ordinary', '合作': 'coop', '赏金': 'bounty', '其他': 'other'}

class Card:
    def __init__(self) -> None:
        self.db = pymysql.connect(
            host='47.242.108.196',
            port=3306,
            user='guest',
            password='Sumika!System2',
            database='data_oj'
        )

        cursor = self.db.cursor()

        for table in tables:
            cursor.execute(f"SELECT name_, i18nkey, groupData FROM {table}")
            setattr(self, table, cursor.fetchall())
        
        self.db.close()

    async def help(self, matcher: Matcher):
        help_msg: str = '''橙汁查卡
    #card [name] [group]
    查卡
    #icon [name] [group]
    查图标
    name为中文卡名
    group为 原版/合作/赏金/其他 或不填'''
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

            if len(args) == 2 and args[1] in groups.keys():
                group = groups[args[1]]
            else:
                group = None
            
            id = ''
            for table in tables:
                table_attr: BaseClass = getattr(self, table)
                for tuple in table_attr:
                    if group != None:
                        if tuple[0] == name and tuple[2] == group:
                            id = tuple[1]
                            now_table = table
                            break                            
                    else:
                        if tuple[0] == name:
                            id = tuple[1]
                            now_table = table
                            if tuple[2] == 'ordinary':
                                break
                if id != '':
                    break
            
            if id == '':
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

            if len(args) == 2 and args[1] in groups.keys():
                group = groups[args[1]]
            else:
                group = None
            
            id = ''
            for table in tables:
                table_attr: BaseClass = getattr(self, table)
                for tuple in table_attr:
                    if group != None:
                        if tuple[0] == name and tuple[2] == group:
                            id = tuple[1]
                            break                            
                    else:
                        if tuple[0] == name:
                            id = tuple[1]
                            if tuple[2] == 'ordinary':
                                break
                if id != '':
                    break
            
            if id == '':
                await matcher.send('没有这张卡啦~')
                return None

            img = f'http://interface.100oj.com/interface/util/icon.php?key={id}&size=256&lossless=true'
            await matcher.send(MessageSegment.image(img))
            return None                     
        except:
            await matcher.finish('诶鸭出错啦~')

card = Card()