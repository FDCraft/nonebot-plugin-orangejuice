import json
import os
import re
import requests
from typing import Dict, Union

from nonebot.adapters.onebot.v11 import GroupMessageEvent, PrivateMessageEvent, Message, MessageSegment
from nonebot.matcher import Matcher
from nonebot.params import CommandArg

from .Config import plugin_config
from .Ess import ess

steam_id_file_path: str = os.path.join(plugin_config.oj_data_path, 'steam_id.json')

class Stats:
    def __init__(self) -> None:
        if not os.path.exists(steam_id_file_path):
            if not os.path.exists(plugin_config.oj_data_path):
                os.makedirs(plugin_config.oj_data_path)
                                
            with open(steam_id_file_path, 'w+') as f:
                """
                steam_id.json
                {
                    "user_id": "steam_id"
                }
                """

                init_json = {}
                f.write(json.dumps(init_json, indent=4))

    async def help(self, matcher: Matcher) -> None:
        help_msg: str = '''橙汁个人统计图片生成
    #stat <steam64id> [limit]
    用于直接生成。limit为行数，可以不填，默认为5。
    使用非初始样式时，不会生成PVP各角色出场次数和胜场的行。
    #stat bind <steam64id>
    用于将当前账号绑定到对应steam账户。重复使用会更新绑定。
    #stat unbind
    删除自己的绑定。
    #stat me [limit]
    绑定steam64id后，使用本命令来快速生成自己的资料。'''
        await matcher.finish(help_msg)

    async def bind(self, uid: str, steam64id: str, matcher: Matcher) -> None:
        try:
            with open(steam_id_file_path, 'r', encoding='utf-8') as f:
                data: Dict[str, str] = json.load(f)
            data[uid] = steam64id
            json_data = json.dumps(data, indent=4)
            with open(steam_id_file_path, 'w', encoding='utf-8') as f:
                f.write(json_data)
            await matcher.send('绑定成功~')
        except:
            await matcher.finish('诶鸭出错啦~绑定失败~')

    async def unbind(self, uid: str, matcher: Matcher) -> None:
        try:
            with open(steam_id_file_path, 'r', encoding='utf-8') as f:
                data: Dict[str, str] = json.load(f)
            flag: bool = bool(data.pop(uid, False))
            if flag:
                with open(steam_id_file_path, 'w', encoding='utf-8') as f:
                    json_data = json.dumps(data, indent=4)
                    f.write(json_data)
                await matcher.send('解除绑定成功~')
            else:
                await matcher.finish('你还没有绑定过steam哦~')
        except:
            await matcher.finish('诶鸭出错啦~解绑失败~')

    async def me(self, uid: str, limit: str, matcher: Matcher) -> None:
        try:
            with open(steam_id_file_path, 'r', encoding='utf-8') as f:
                data: Dict[str, str] = json.load(f)
                steam64id: Union[str, None] = data.get(uid, None)
            if steam64id == None:
                await matcher.send('你还没有绑定过steam哦~')
                return None
            else:
                img = f'https://interface.100oj.com/stat/render.php?steamid={steam64id}&limit={limit}'
                if requests.get(img).content == b'':
                    await matcher.send('唔~这个账号还没有设置Steam个人资料为公开呢~')
                else:
                    await matcher.send(MessageSegment.image(img))
        except:
            await matcher.finish('诶鸭出错啦~')

    async def get_img(self, steam64id: str, limit: str, matcher: Matcher) -> None:
        try:
            img = f'https://interface.100oj.com/stat/render.php?steamid={steam64id}&limit={limit}'
            if requests.get(img).content == b'':
                    await matcher.send('唔~Ta没有设置Steam个人资料为公开呢~')
            else:
                await matcher.send(MessageSegment.image(img))
        except:
            await matcher.finish('诶鸭出错啦~')

    async def stats(self, matcher: Matcher, event: Union[GroupMessageEvent, PrivateMessageEvent], arg: Message = CommandArg()) -> None:
        if isinstance(event, GroupMessageEvent) and event.group_id in ess.config['modules']['Stats']:
            return None

        args = arg.to_rich_text().split(' ')

        if args == [''] or args is None or args[0] == 'help':
            await self.help(matcher)

        if args[0] == 'bind':
            uid = str(event.user_id)

            if len(args) == 2:
                steam64id: str = args[1]
                if steam64id.isdigit() and len(steam64id) == 17:
                    await self.bind(uid, steam64id, matcher)
                else:
                    await self.help(matcher)
            else:
                await self.help(matcher)

        elif args[0] == 'unbind':
            uid = str(event.user_id)
            await self.unbind(uid, matcher)

        elif args[0] == 'me':
            uid = str(event.user_id)
            if len(args) == 2:
                if args[1].isdigit():
                    limit: str = str(min(int(args[1]), 10))
                    await self.me(uid, limit, matcher)
                else:
                    await self.help(matcher)
            else:
                limit: str = '5'
                await self.me(uid, limit, matcher)
        
        elif args[0].isdigit() and len(args[0]) == 17:
            steam64id = args[0]
            if len(args) == 2:
                if args[1].isdigit():
                    limit: str = str(min(int(args[1]), 10))
                    await self.get_img(steam64id, limit, matcher)
                else:
                    await self.help(matcher)
            else:
                limit: str = '5'
                await self.get_img(steam64id, limit, matcher)

        elif args[0].startswith('[at'):
            uid = re.sub(r'\[at:qq=(.*?)\]', r'\1', args[0])
            if len(args) == 2:
                if args[1].isdigit():
                    limit: str = str(min(int(args[1]), 10))
                    await self.me(uid, limit, matcher)
                else:
                    await self.help(matcher)
            else:
                limit: str = '5'
                await self.me(uid, limit, matcher)
        
        else:
            await self.help(matcher)


stats = Stats()
            