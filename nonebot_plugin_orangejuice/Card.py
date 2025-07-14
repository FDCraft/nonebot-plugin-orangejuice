import json
import os
import re
import shlex
from typing import List, Union, Literal

import aiosqlite
from fuzzywuzzy import fuzz  # noqa

from nonebot import get_driver
from nonebot.adapters.onebot.v11 import (
    Bot,
    Message,
    MessageSegment,
    GroupMessageEvent,
    PrivateMessageEvent,
)
from nonebot.matcher import Matcher
from nonebot.params import CommandArg

from .Config import plugin_config
from .Ess import ess

BaseClass = tuple[tuple[str, str, str, str]]

card_database_path = os.path.join(
    os.path.dirname(__file__), "resources", "card", "oj_data-2025-07-14.db"
)
regex_path = os.path.join(
    os.path.dirname(__file__), "resources", "card", "regex.json"
)
name_list_path = os.path.join(
    os.path.dirname(__file__), "resources", "card", "namelist.json"
)
img_root_path = (
    os.path.join(os.path.dirname(__file__), "resources", "card", "images")
)
# tables = ['cardDeck', 'cardHyper', 'cardOther', 'unitCharacter', 'unitNPC'] # cardBossSkill is special so not in here.
# groups = {'原版': 'ordinary', '合作': 'coop', '赏金': 'bounty', '其他': 'other'}
type_replace = {'旗帜卡': 'BANNER', '战斗卡': 'BATTLE', '事件卡': 'EVENT', '礼物卡': 'GIFT', '增益卡': 'BOOST', '陷阱卡': 'TRAP'}
# BANNER BOOST EVENT GIFT BATTLE

class Card:
    def __init__(self) -> None:
        global regex_path, name_list_path
        self.regex: dict[str, str] = json.load(open(regex_path, "r", encoding="utf-8"))
        self.name_list: dict[str, list[str]] = json.load(
            open(name_list_path, "r", encoding="utf-8")
        )
        # {'card': [(id, name, name_En), ()]}

    async def help(self, matcher: Matcher):
        help_msg: str = """橙汁查卡
    #card <name> <table> <-i>
    name 为中文卡名或者使用下划线的英文卡名
    table 为 card/unit/achievement/field"""
        await matcher.send(help_msg)

    def match(
        self, name: str, target_table: str = None
    ) -> list[tuple[Literal["card", "unit", "achievement", "field"], str, int]]:

        def B2Q(string: str):
            return (
                string.replace("~", "～")
                .replace("&", "＆")
                .replace("(", "（")
                .replace(")", "）")
                .replace("!", "！")
            )

        result = []
        force_flag = False

        for regex, key in self.regex.items():
            if re.match(regex, name, re.I):
                name = key
                force_flag = True

        for table in ["card", "unit", "achievement", "field"]:
            if target_table and target_table != table:
                continue
            name_list = self.name_list[table]
            for card in name_list:

                if force_flag:
                    if card[1] == name or card[2].lower() == name.lower():
                        result.append((table, card[0], 100))
                        continue
                    else:
                        continue

                score = max(
                    fuzz.ratio(B2Q(name), card[1]), fuzz.ratio(name.lower(), card[2].lower())
                )
                
                if score >= plugin_config.match_score and score > 0:
                    result.append((table, card[0], score))

        result.sort(
            key=lambda tuple: (
                tuple[2],
                ("field", "achievement", "unit", "card").index(tuple[0]),
            ),
            reverse=True,
        )
        return result

    async def search_db(self, match_result, count, icon: bool = False, detail: bool = False) -> list[MessageSegment]:
        messages: list[MessageSegment] = []
        table, id, score = match_result

        async with aiosqlite.connect(card_database_path) as db:
            db.row_factory = aiosqlite.Row  # 设置 row_factory
            async with db.cursor() as cursor:
                match table:
                    case "card":
                        await cursor.execute(
                            "SELECT * FROM Card WHERE 标识码 = ?", (id,)
                        )
                        row = await cursor.fetchone()
                        if row:
                            row_dict = dict(row)
                            
                        # 消息构建
                        card_type: str = row_dict['类型']
                        for key, value in type_replace.items():
                            card_type = card_type.replace(key, value)
                            
                        messages.append(
                            MessageSegment.text(
                                f"{count}.\n内部ID：{id}\n中文名：{row_dict['名称']}\n英文名：{row_dict['英文名称']}\n匹配分数：{score:.2f}"
                            )
                        )
                        messages.append(
                            MessageSegment.text(
                                f"来源：{row_dict['来源']} 稀有度：{row_dict['稀有度']} 画师：{row_dict['画师']}\n"
                                f"等级 {row_dict['等级']} 费用 {row_dict['费用'] if row_dict['费用'] != -1 else '可变'} "
                                f"（{card_type}）{('（Max ' + str(row_dict['携带限制']) + '）') if row_dict['携带限制'] != 0 else ''}\n"
                                f"{row_dict['卡牌描述']}\n"
                                f"{row_dict['背景文字']}"
                            )
                        )
                        
                        images = []
                        images.append(row_dict['图片']) if row_dict['图片'] != '' else None
                        if icon:
                            for key in ['图标', '礼物图标', '礼物图标2', '标记图标']:
                                images.append(row_dict[key]) if row_dict[key] != '' else None
                    
                        for filename in images:
                            if os.path.exists(os.path.join(img_root_path, filename)):
                                messages.append(
                                    MessageSegment.image(os.path.join(img_root_path, filename))
                                )
                        # 构建结束
                        
                    case "unit":
                        await cursor.execute(
                            "SELECT * FROM Unit WHERE 标识码 = ?", (id,)
                        )
                        row = await cursor.fetchone()
                        if row:
                            row_dict = dict(row)

                        # 消息构建
                        messages.append(
                            MessageSegment.text(
                                f"{count}.\n内部ID：{id}\n中文名：{row_dict['名称']}\n英文名：{row_dict['英文名称']}\n匹配分数：{score:.2f}"
                            )
                        )
                        messages.append(
                            MessageSegment.text(
                                f"原作：{row_dict['原作']} 声优：{row_dict['声优']} 画师：{row_dict['画师']}\n"
                                f"HP {row_dict['生命值']} ATK {row_dict['攻击力']} DEF {row_dict['防御力']} EVD {row_dict['闪避力']} REC {row_dict['复活值']}\n"
                                f"{row_dict['卡牌描述']}"
                            )
                        )
                        
                        images = []
                        images.append(row_dict['图片']) if row_dict['图片'] != '' else None
                        if icon:
                            for key in ['图标']:
                                images.append(row_dict[key]) if row_dict[key] != '' else None
                    
                        for filename in images:
                            if os.path.exists(os.path.join(img_root_path, filename)):
                                messages.append(
                                    MessageSegment.image(os.path.join(img_root_path, filename))
                                )
                        # UNIT 加餐
                        hyper = row_dict['Hyper']
                        hyper_result = self.match(hyper, target_table='card')
                        if len(hyper_result) != 0:
                            messages += await self.search_db(hyper_result[0], 'HYPER')
                        # 消息构建结束
                        
                    case "achievement":
                        await cursor.execute(
                            "SELECT * FROM Achievement WHERE 成就ID = ?", (id,)
                        )
                        row = await cursor.fetchone()
                        if row:
                            row_dict = dict(row)

                        # 消息构建
                        messages.append(
                            MessageSegment.text(
                                f"{count}.\n内部ID：{id}\n中文名：{row_dict['名称']}\n英文名：{row_dict['英文名称']}\n匹配分数：{score:.2f}"
                            )
                        )
                        messages.append(
                            MessageSegment.text(
                                f"描述：{row_dict['描述']}\n"
                                f"解锁条件：{row_dict['解锁条件']}"
                            )
                        )
                        
                        images = []
                        images.append(row_dict['图片']) if row_dict['图片'] != '' else None
                        for filename in images:
                            if os.path.exists(os.path.join(img_root_path, filename)):
                                messages.append(
                                    MessageSegment.image(os.path.join(img_root_path, filename))
                                )
                        # 消息构建结束

                    case "field":
                        await cursor.execute(
                            "SELECT * FROM Field WHERE 英文名称 = ?", (id,)
                        )
                        row = await cursor.fetchone()
                        if row:
                            row_dict = dict(row)

                        messages.append(
                            MessageSegment.text(
                                f"{count}.\n中文名：{row_dict['名称']}\n英文名：{row_dict['英文名称']}\n匹配分数：{score:.2f}"
                            )
                        )
                        messages.append(
                            MessageSegment.text(
                                f"默认事件：{row_dict['默认事件']}\n"
                                f"默认BOSS：{row_dict['默认Boss']}\n"
                                f"解锁条件：{row_dict['解锁条件']}"
                            )
                        )
                        
                        images = []
                        images.append(row_dict['图片']) if row_dict['图片'] != '' else None
                        for filename in images:
                            if os.path.exists(os.path.join(img_root_path, filename)):
                                messages.append(
                                    MessageSegment.image(os.path.join(img_root_path, filename))
                                )

        return messages

    async def forward_send(
        self,
        bot: Bot,
        event: Union[GroupMessageEvent, PrivateMessageEvent],
        messages: list[MessageSegment],
    ) -> None:
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

    async def card(
        self,
        bot: Bot,
        matcher: Matcher,
        event: Union[GroupMessageEvent, PrivateMessageEvent],
        arg: Message = CommandArg(),
    ) -> None:
        try:
            if not ess.check(event, "Card"):
                return None
            args = shlex.split(arg.extract_plain_text())

            if len(args) == 0 or "help" in args:
                await self.help(matcher)
                return None

            # input
            name = args[0]
            target_table = None
            icon = False
            detail = False

            # input parse
            for arg in args:
                if arg in ["card", "unit", "achievement", "field"]:
                    target_table = arg
                if arg in ["-i", "icon"]:
                    icon = True
                if arg in ["-t", "detail"]:
                    detail = True

            result = self.match(name, target_table)

            if len(result) == 0:
                await matcher.send("没有这张卡啦！")
                return None

            messages: List[MessageSegment] = []
            count = 0
            for tuple in result:
                count += 1
                if count > 10:
                    messages = [
                        MessageSegment.text(f"匹配结果过多，仅显示前10个结果。")
                    ] + messages
                    break
                messages += await self.search_db(tuple, count, icon)
                """
                messages.append(MessageSegment.text(f'{count}.\n内部ID：{tuple[0]}\n中文名：{tuple[1]}\n英文名：{tuple[2]}\n组别：{tuple[3]}\n所在表：{tuple[4]}\n匹配分数：{tuple[5]}'))
                if tuple[4].startswith('unit'):
                    img = f'https://interface.100oj.com/interface/render/cardunit.php?key={tuple[0]}'
                    messages.append(MessageSegment.image(img))
                elif tuple[4] in tables:
                    img = f'https://interface.100oj.com/interface/render/{tuple[4].lower()}.php?key={tuple[0]}'
                    messages.append(MessageSegment.image(img))
                else:
                    messages.append(MessageSegment.text(f'「{tuple[1]}」({"[H] " if tuple[10] else ""}{tuple[9].upper()} {tuple[8]}/{tuple[7]})\n{tuple[6]}'))
                """

            await self.forward_send(bot, event, messages)

        except Exception as e:
            await matcher.send("诶鸭出错啦~")
            raise e

card: Card = Card()
