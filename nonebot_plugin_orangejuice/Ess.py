import json
import os
from typing import Annotated, Dict, List, Literal, Union

from nonebot import logger
from nonebot.exception import ParserExit
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Bot, Message, GroupMessageEvent, PrivateMessageEvent

from .Config import plugin_config

ess_file_path: str = os.path.join(plugin_config.oj_data_path, 'essentialx.json')
init_json: Dict[str, Union[Dict[str, List[str]], int]] = {"modules":{"Card":[],"Deck":[],"Emote":[],"Le":[],"Stats":[]},"version":1}

class Args:
    def __init__(self, bot: Bot, event: Union[GroupMessageEvent, PrivateMessageEvent], arg: Message) -> None:
        global init_json

        self.invaild: bool = False
        self.handle: str = None
        self.operate: str = None
        self.target_module: str = None
        self.target_uid: int = None
        self.target_gid: int = None
        self.send_uid: int = event.user_id
        self.send_gid: int = event.group_id if isinstance(event, GroupMessageEvent) else None
        if isinstance(self.send_gid, tuple): #IDK :(
            self.send_gid = self.send_gid[0]
        self.is_admin: bool = event.sender.role in ["admin", "owner"] if isinstance(event, GroupMessageEvent) else False
        self.is_superuser: bool = str(event.user_id) in bot.config.superusers

        list_args = arg.extract_plain_text().split(' ')

        while len(list_args) < 5:
            list_args.append('')
        logger.debug(f'参数解析结果：{list_args}')

        match list_args[0]:
            case 'module' | '-m':
                self.handle = 'module'

                match list_args[1]:
                    case 'list' | '-l' | 'ls':
                        self.operate = 'list'

                        self.invaild = True # ##ess module list [gid]
                        self.target_gid = int(list_args[2]) if list_args[2].isdigit() else self.send_gid

                    case 'enable' | '-on':
                        self.operate = 'enable'
                        logger.error('?')
                        if list_args[2] in list(init_json['modules'].keys()):
                            self.invaild = True # ##ess module enable [modulename] [gid]
                            self.target_module = list_args[2]
                            self.target_gid = int(list_args[3]) if list_args[3].isdigit() else self.send_gid


                    case 'disable' | '-off':
                        self.operate = 'disable'
                        logger.error('?')
                        if list_args[2] in list(init_json['modules'].keys()):
                            self.invaild = True # ##ess module disable [modulename] [gid]
                            self.target_module = list_args[2]
                            self.target_gid = int(list_args[3]) if list_args[3].isdigit() else self.send_gid
            case _:
                pass


class Ess:
    def __init__(self) -> None:
        if not os.path.exists(ess_file_path):
            if not os.path.exists(plugin_config.oj_data_path):
                os.makedirs(plugin_config.oj_data_path)
            self.init_json()  

        self.load_json()

    def init_json(self):
        with open(ess_file_path, 'w+') as f:
            '''
            essential.json
            {
                "modules": {
                    "Card": [], 
                    "Deck": [], 
                    "Emote": [], 
                    "Le": [],
                    "Stats": []
                },
                "version": 1
            }
            '''
            f.write(json.dumps(init_json, indent=4))

    def load_json(self):
        with open(ess_file_path, 'r', encoding='utf-8') as f:
            data: Dict[str, Union[Dict[str, List[str]], int]] = json.load(f)
            self.config = data

    def save_json(self):
        with open(ess_file_path, 'w', encoding='utf-8') as f:
            json_data = json.dumps(self.config, indent=4)
            f.write(json_data)
    

    async def help(self, matcher: Matcher) -> None:
        help_msg: str = '''Ess模块，需要是超级管理员/群管理/群主
    #ess module enable <modulename> [groupid]
    #ess module disable <modulename> [groupid]
    #ess module list [groupid]'''
        await matcher.finish(help_msg)

    async def module(self, matcher: Matcher, args: Args) -> None:

        if args.operate == 'enable':
            if args.target_gid in self.config['modules'][args.target_module]:
                self.config['modules'][args.target_module].remove(args.target_gid)
            self.save_json()
            await matcher.send(f'已在{args.target_gid}成功启用{args.target_module}模块！')

        elif args.operate == 'disable':
            if args.target_gid not in self.config['modules'][args.target_module]:
                self.config['modules'][args.target_module].append(args.target_gid)
            self.save_json()
            await matcher.finish(f'已在{args.target_gid}成功禁用{args.target_module}模块！')

        elif args.operate == 'list':
            enable_modules = []
            avaliable_modules = []
            for module in self.config['modules'].keys():
                if args.target_gid not in self.config['modules'][module]:
                    enable_modules.append(module)
                else:
                    avaliable_modules.append(module)
            msg1 = "\n- " + "\n- ".join(enable_modules) if enable_modules != [] else ""
            msg2 = "\n- " + "\n- ".join(avaliable_modules) if avaliable_modules != [] else ""
            await matcher.finish(f'群{args.target_gid}\n启用的模块: {msg1}\n可用模块: {msg2}')

        else:
            await self.help(matcher)

    async def ess(self, bot: Bot, matcher: Matcher, event: Union[GroupMessageEvent, PrivateMessageEvent], arg: Message = CommandArg()) -> None:
        args = Args(bot, event, arg)

        if not args.is_admin and not args.is_superuser:
            return None
        
        if not args.invaild:
            await self.help(matcher)
        
        if args.target_gid == None:
            await matcher.finish('呜，请指定群号！')

        if args.target_gid != args.send_gid and not args.is_superuser:
            await matcher.finish('诶鸭你没有权限这样做啦！')

        if hasattr(args, "handle"):
            await getattr(self, args.handle)(matcher, args)
            
        
ess = Ess()
