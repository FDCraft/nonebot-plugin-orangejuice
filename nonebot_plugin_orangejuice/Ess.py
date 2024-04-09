import datetime
import json
import os
import re
from typing import Any, Dict, List, Union

from nonebot import logger
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import Bot, Message, GroupMessageEvent, PrivateMessageEvent

from .Config import plugin_config

ess_file_path: str = os.path.join(plugin_config.oj_data_path, 'essentialx.json')
init_json: Dict[str, Union[Dict[str, List[str]], int]] = {"modules":{"Card":[],"Deck":[],"Emote":[],"Le":[],"Stats":[],"Mixer":[]},"version":2}

class Args:
    def __init__(self, bot: Bot, event: Union[GroupMessageEvent, PrivateMessageEvent], arg: Message) -> None:
        global init_json

        self.bot: Bot = bot
        self.event: Union[GroupMessageEvent, PrivateMessageEvent] = event

        self.invaild: bool = False
        self.handle: str = None
        self.operate: str = None
        self.target_module: str = None
        self.target_uid: int = None
        self.target_gid: int = None
        self.send_uid: int = event.user_id
        self.send_gid: int = event.group_id if isinstance(event, GroupMessageEvent) else None
        self.is_admin: bool = event.sender.role in ["admin", "owner"] if isinstance(event, GroupMessageEvent) else False
        self.is_superuser: bool = str(event.user_id) in bot.config.superusers

        self.extra_data: Dict[str, Any] = {}

        list_args = arg.to_rich_text().split(' ')

        while len(list_args) < 5:
            list_args.append('')
        logger.debug(f'参数解析结果：{list_args}')

        for i in range(0,5):
            list_args[i] = re.sub(r'\[at:qq=(.*?)\]', r'\1', list_args[i])

        match list_args[0]:
            case 'module' | '-m':
                self.handle = 'module'

                match list_args[1]:
                    case 'list' | '-l' | 'ls':
                        self.operate = 'list'

                        self.invaild = True # #ess module list [gid]
                        logger.trace('ess module list [gid] trigger.')
                        self.target_gid = int(list_args[2]) if list_args[2].isdigit() else self.send_gid

                    case 'enable' | '-on':
                        self.operate = 'enable'
                        if list_args[2] in list(init_json['modules'].keys()):
                            self.invaild = True # #ess module enable <modulename> [gid]
                            logger.trace(f'ess module enable <modulename> [gid] trigger.')
                            self.target_module = list_args[2]
                            self.target_gid = int(list_args[3]) if list_args[3].isdigit() else self.send_gid


                    case 'disable' | '-off':
                        self.operate = 'disable'
                        if list_args[2] in list(init_json['modules'].keys()):
                            self.invaild = True # #ess module disable <modulename> [gid]
                            self.target_module = list_args[2]
                            self.target_gid = int(list_args[3]) if list_args[3].isdigit() else self.send_gid
            
            case 'mute':
                self.handle = 'mute'
                if list_args[1].isdigit():
                    self.invaild = True # #ess mute <id> [time] [reason]
                    logger.trace(f'ess mute <id> [time] [reason] trigger.')
                    self.target_uid = int(list_args[1])
                    self.extra_data['mute_reason'] = list_args[3]
                    if list_args[2] != '':
                        if list_args[2].endswith('m'):
                            self.extra_data['mute_time'] = int(list_args[2][:-1]) * 60
                        elif list_args[2].endswith('h'):
                            self.extra_data['mute_time'] = int(list_args[2][:-1]) * 3600
                        elif list_args[2].endswith('d'):
                            self.extra_data['mute_time'] = int(list_args[2][:-1]) * 3600 * 24
                        elif list_args[2].endswith('s'):
                            self.extra_data['mute_time'] = int(list_args[2][:-1])
                        elif list_args[2].isdigit():
                            self.extra_data['mute_time'] = int(list_args[2])
                        else:
                            self.invaild = False
                    else:
                        self.extra_data['mute_time'] = 30

            case 'save' | '-s':
                self.invaild = True # #ess save
                logger.trace(f'ess save trigger.')
                self.handle = 'save'
            case 'load' | '-l':
                self.invaild = True # #ess load
                logger.trace(f'ess load trigger.')
                self.handle = 'load'
            case _:
                pass



class Ess:
    def __init__(self) -> None:
        if not os.path.exists(ess_file_path):
            if not os.path.exists(plugin_config.oj_data_path):
                os.makedirs(plugin_config.oj_data_path)
            self.init_json()  

        self.load_json()

        if self.config["version"] == 1:
            self.config["modules"]["Mixer"] = []
            self.config["version"] = 2
            self.save_json()

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
                    "Stats": [],
                    "Mixer": []
                },
                "version": 2
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

    def check(self, event: Union[GroupMessageEvent, PrivateMessageEvent]) -> bool:
        if event.user_id in self.config['blacklist']:
            return False
        else:
            return True
    

    async def help(self, matcher: Matcher) -> None:
        help_msg: str = '''Ess模块，需要是超级管理员/群管理/群主
    #ess module enable <modulename> [groupid]
    #ess module disable <modulename> [groupid]
    #ess module list [groupid]'''
        await matcher.finish(help_msg)

    async def module(self, matcher: Matcher, args: Args) -> None:

        if args.target_gid == None:
            await matcher.finish('呜，请指定群号！')

        if args.target_gid != args.send_gid and not args.is_superuser:
            await matcher.finish('诶鸭你没有权限这样做啦！')

        if args.operate == 'enable':
            if args.target_gid in self.config['modules'][args.target_module]:
                self.config['modules'][args.target_module].remove(args.target_gid)
            self.save_json()
            await matcher.finish(f'已在{args.target_gid}成功启用{args.target_module}模块！')

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

    async def save(self, matcher: Matcher, args: Args):
        if not args.is_superuser:
            await matcher.finish('诶鸭你没有权限这样做啦！')
        
        self.save_json()
        await matcher.finish('已保存配置~')

    async def load(self, matcher: Matcher, args: Args):
        if not args.is_superuser:
            await matcher.finish('诶鸭你没有权限这样做啦！')
        
        self.load_json()
        await matcher.finish('已载入配置~')

    async def mute(self, matcher: Matcher, args: Args):
        ban_time = args.extra_data['mute_time']

        now_time = datetime.datetime.now()
        unban_time = now_time + datetime.timedelta(seconds=ban_time)
        unban_time_str = unban_time.strftime("解禁时间:%Y年%m月%d日%H时%M分%S秒")
        try:
            info = await args.bot.get_group_member_info(group_id=args.event.group_id, user_id=args.target_uid)
            name = info['card'] if info['card'] is not None and info['card'] != '' else info['nickname']
            await args.bot.set_group_ban(group_id=args.event.group_id, user_id=args.target_uid, duration=ban_time)
        except Exception as e:
            await matcher.send('禁言失败(')

        await matcher.send(f'被禁者:{name}\n禁言原因:{args.extra_data["mute_reason"]}\n被禁时间:{str(ban_time)}秒\n{unban_time_str}')

    async def ess(self, bot: Bot, matcher: Matcher, event: Union[GroupMessageEvent, PrivateMessageEvent], arg: Message = CommandArg()) -> None:
        args = Args(bot, event, arg)

        if not args.is_admin and not args.is_superuser:
            return None
        
        if not args.invaild:
            await self.help(matcher)

        if hasattr(args, "handle"):
            await getattr(self, args.handle)(matcher, args)
            
        
ess = Ess()
