import json
import os
from typing import Dict, Union

from nonebot.adapters.onebot.v11 import GroupMessageEvent, PrivateMessageEvent, Message, MessageSegment
from nonebot.matcher import Matcher
from nonebot.params import CommandArg

class Stats:
    def __init__(self) -> None:
        if not os.path.exists('data/steam_id.json'):
            if not os.path.exists('data'):
                os.mkdir('data')
                                
            with open('data/steam_id.json', 'w+') as f:
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
    #stat [steam64id] [limit]
    用于直接生成。limit为行数，可以不填，默认为5。
    使用非初始样式时，不会生成PVP各角色出场次数和胜场的行。
    #stat bind [steam64id]
    用于将当前账号绑定到对应steam账户。重复使用会更新绑定。
    #stat unbind
    删除自己的绑定。
    #stat me [limit]
    绑定steam64id后，使用本命令来快速生成自己的资料。'''
        await matcher.finish(help_msg)

    async def bind(self, uid: str, steam64id: str, matcher: Matcher) -> None:
        try:
            with open('data/steam_id.json', 'r', encoding='utf-8') as f:
                data: Dict[str, str] = json.load(f)
            data[uid] = steam64id
            json_data = json.dumps(data, indent=4)
            with open('data/steam_id.json', 'w', encoding='utf-8') as f:
                f.write(json_data)
            await matcher.send('绑定成功~')
        except:
            await matcher.finish('诶鸭出错啦~绑定失败~')

    async def unbind(self, uid: str, matcher: Matcher) -> None:
        try:
            with open('data/steam_id.json', 'r', encoding='utf-8') as f:
                data: Dict[str, str] = json.load(f)
            flag: bool = bool(data.pop(uid, False))
            if flag:
                with open('data/steam_id.json', 'w', encoding='utf-8') as f:
                    json_data = json.dumps(data, indent=4)
                    f.write(json_data)
                await matcher.send('解除绑定成功~')
            else:
                await matcher.finish('你还没有绑定过steam哦~')
        except:
            await matcher.finish('诶鸭出错啦~解绑失败~')

    async def me(self, uid: str, limit: str, matcher: Matcher) -> None:
        try:
            with open('data/steam_id.json', 'r', encoding='utf-8') as f:
                data: Dict[str, str] = json.load(f)
                steam64id: Union[str, None] = data.get(uid, None)
            if steam64id == None:
                await matcher.send('你还没有绑定过steam哦~')
            else:
                img = f'https://interface.100oj.com/stat/render.php?steamid={steam64id}&limit={limit}'
                await matcher.send(MessageSegment.image(img))
        except:
            await matcher.finish('诶鸭出错啦~')

    async def get_img(self, steam64id: str, limit: str, matcher: Matcher) -> None:
        try:
            img = f'https://interface.100oj.com/stat/render.php?steamid={steam64id}&limit={limit}'
            await matcher.send(MessageSegment.image(img))
        except:
            await matcher.finish('诶鸭出错啦~')

    async def main(self, matcher: Matcher, event: Union[GroupMessageEvent, PrivateMessageEvent], arg: Message = CommandArg()) -> None:
        args = arg.extract_plain_text().split(' ')

        if args == [] or args is None or args[0] == 'help':
            await self.help(matcher)

        elif args[0] == 'bind':
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
        
        else:
            await self.help(matcher)


stats = Stats()
            