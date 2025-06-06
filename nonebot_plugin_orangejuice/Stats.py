import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Union

import aiohttp
import aiosqlite

from nonebot import logger, get_driver
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent, PrivateMessageEvent, Message, MessageSegment
from nonebot.matcher import Matcher
from nonebot.params import CommandArg

from .Config import plugin_config
from .Ess import ess

image_path = Path(os.path.join(os.path.dirname(__file__), 'resources', 'stats'))
steam_id_file_path: str = os.path.join(plugin_config.oj_data_path, 'steam_id.db')
db_keys: List[str] = ['steam64id', 'renderType', 'sp1', 'sp1_1', 'sp1_2', 'sp1_3', 'sp1_4', 'sp1_5', 'sp1_6', 'sp1_31', 'sp1_37']

class Stats:
    def __init__(seld) -> None:
        pass
    async def init_database(self) -> 'Stats':
        if not os.path.exists(steam_id_file_path):
            if not os.path.exists(plugin_config.oj_data_path):
                os.makedirs(plugin_config.oj_data_path)
                                
            self.db = await aiosqlite.connect(steam_id_file_path)
            self.cursor = await self.db.cursor()

            await self.cursor.execute('CREATE TABLE IF NOT EXISTS steamInfo(qq VARCHAR(11) PRIMARY KEY,steam64id CHARACTER(17),renderType INTERGER,sp1 TINYINT,\
                                sp1_1 TINYINT,sp1_2 TINYINT,sp1_3 TINYINT,sp1_4 TINYINT,sp1_5 TINYINT,sp1_6 TINYINT,sp1_31 TINYINT,sp1_37 TINYINT)')
            await self.cursor.execute('INSERT INTO steamInfo VALUES (?, ?, 0, 2, 1, 1, 1, 1, 1, 1, 1, 1)', ('995905922', '76561198857827726')) # Developer Sign
            await self.cursor.execute('INSERT INTO steamInfo VALUES (?, ?, 0, 31, 1, 0, 0, 1, 0, 0, 1, 1)', ('535369354', '76561198361135527')) # Developer Sign

            if os.path.exists(os.path.join(plugin_config.oj_data_path, 'steam_id.json')): # Change old json into database
                with open(os.path.join(plugin_config.oj_data_path, 'steam_id.json'), 'r', encoding='utf-8') as f:
                    data: Dict[str, str] = json.load(f)
                    for qq, steam64id in data.items():
                        await self.cursor.execute('INSERT INTO steamInfo VALUES (?, ?, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)', (qq, steam64id))

            await self.db.commit()
            await self.db.close()

        self.db = await aiosqlite.connect(steam_id_file_path)
        self.cursor = await self.db.cursor()

        return self
    
    @staticmethod
    def get_jrrp(string: str):
        now = datetime.now()
        num1 = round((abs((hash('Polaris_Light' + str(now.timetuple().tm_yday)+ str(now.year) + 'XYZ') / 3.0 + hash('QWERTY' + string + '0*8&6' + str(now.day) + '96485.3365') / 3.0) / 527.0) % 1000.0))
        num2 = round(num1 / 995.0 * 99.0) if num1 < 996 else 100
        return num2
    
    async def lucky_orb(self, matcher: Matcher, uid: str) -> None:
        jrrp = self.get_jrrp(uid)
        if jrrp == 100: # A way to test this function
            await self.cursor.execute('SELECT sp1, sp1_4 FROM steamInfo WHERE qq = ?', (uid,))
            data = await self.cursor.fetchall()
            logger.info(f'Lucky Orb!: {uid}, {data}')
            
            if data[0][1] == 0:
                await matcher.send(MessageSegment.image(image_path / 'sp1_4.png') + '『Lucky Orb！』')
                await self.cursor.execute('UPDATE steamInfo SET sp1_4 = ? WHERE qq = ?', ('1', uid))
                if data[0][0] == 0:
                    await self.cursor.execute('UPDATE steamInfo SET sp1 = ? WHERE qq = ?', ('4', uid))
                await self.db.commit()
        else:
            return None
    
    
    async def help(self, matcher: Matcher) -> None:
        help_msg: str = '''橙汁个人统计图片生成
    #stat <steam64id> [limit]
    用于直接生成。limit为行数，可以不填，默认为5。
    #stat bind <steam64id>
    用于将当前账号绑定到对应steam账户。重复使用会更新绑定。
    #stat unbind
    删除自己的绑定。
    #stat me [limit]
    绑定steam64id后，使用本命令来快速生成自己的资料。
    #stat type <type>
    更改出图类型。
    #stats modify <uid> <key> <value>
    直接操作数据库，需要有超级管理员权限。'''
        await matcher.finish(help_msg + MessageSegment.image(image_path / 'help.png') + MessageSegment.image(image_path / 'pin.png'))

    async def bind(self, uid: str, steam64id: str, matcher: Matcher) -> None:
        try:
            await self.cursor.execute('INSERT INTO steamInfo VALUES (?, ?, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0) ON CONFLICT(qq) DO UPDATE SET steam64id = ?', (uid, steam64id, steam64id))
            await self.db.commit()
            await matcher.send('绑定成功~')
            return None
        except Exception as e:
            await matcher.send('诶鸭出错啦~绑定失败~')
            raise e
        
    async def unbind(self, uid: str, matcher: Matcher) -> None:
        try:
            await self.cursor.execute('UPDATE steamInfo SET steam64id = 0 WHERE qq = ?', (uid,))
            await self.db.commit()
            await matcher.send('解绑成功~')
            return None
        except Exception as e:
            await matcher.send('诶鸭出错啦~解绑失败~')
            raise e
        
    async def type(self, uid: str, type: str, matcher: Matcher):
        try:
            await self.cursor.execute('SELECT * FROM steamInfo WHERE qq = ?', (uid,))
            data = await self.cursor.fetchall()
            if data == [] or data is None:
                await matcher.send('你还没有绑定过Steam哦~请使用 #stat bind <steam64id> 来进行绑定。')
                return None        
            
            await self.cursor.execute('UPDATE steamInfo SET renderType = ? WHERE qq = ?', (type, uid))
            await self.db.commit()
            await matcher.send('修改成功~')
        except Exception as e:
            await matcher.send('诶鸭出错啦~')
            raise e
        
    async def pin(self, uid: str, pin: str, matcher: Matcher):
        try:
            await self.cursor.execute('SELECT * FROM steamInfo WHERE qq = ?', (uid,))
            data = await self.cursor.fetchall()
            if data == [] or data is None:
                await matcher.send('你还没有绑定过Steam哦~请使用 #stat bind <steam64id> 来进行绑定。')
                return None
            
            if pin == '0':
                await self.cursor.execute('UPDATE steamInfo SET sp1 = ? WHERE qq = ?', (pin, uid))
                await self.db.commit()
                await matcher.send('修改成功~')
            else:
                match pin:
                    case '31':
                        index = 10
                    case '37':
                        index = 11
                    case _:
                        index = int(pin) + 3
                if data[0][index]:
                    await self.cursor.execute('UPDATE steamInfo SET sp1 = ? WHERE qq = ?', (pin, uid))
                    await self.db.commit()
                    await matcher.send('修改成功~')                    
                else:
                    await matcher.send('你无法使用这个pin。')
        except Exception as e:
            await matcher.send('诶鸭出错啦~')
            raise e
        
    async def get(self, matcher: Matcher, target_uid: str) -> None:
        try:
            await self.cursor.execute('SELECT * FROM steamInfo WHERE qq = ?', (target_uid, ))
            data = await self.cursor.fetchall()
            if data == [] or data is None:
                await matcher.send(f'{target_uid}还没有绑定Steam账号。')
                return None
            
            await self.db.commit()
            await matcher.send(f'{target_uid} 的数据为 {data[0]}。')
        except Exception as e:
            await matcher.send('诶鸭出错啦~')
            raise e 
        
    async def modify(self, matcher: Matcher, target_uid: str, key: str, value: str) -> None:
        try:
            if key == 'steam64id':
                await self.cursor.execute('INSERT INTO steamInfo VALUES (?, ?, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0) ON CONFLICT(qq) DO UPDATE SET steam64id = ?', (target_uid, value, value))
                await self.db.commit()
                await matcher.send(f'修改成功，绑定{value}到{target_uid}。')
            else:
                if key not in db_keys:
                    await matcher.send(f'有效的key应为:\n{", ".join(db_keys)}。')
                    return None
                
                await self.cursor.execute('SELECT * FROM steamInfo WHERE qq = ?', (target_uid,))
                data = await self.cursor.fetchall()
                if data == [] or data is None:
                    await matcher.send(f'{target_uid}还没有绑定Steam账号。')
                    return None

                
                await self.cursor.execute(f'UPDATE steamInfo SET {key} = {value} WHERE qq = {target_uid}')
                await self.db.commit()
                await matcher.send(f'修改成功，修改 {target_uid} 的 {key} 为 {value}。')
                
        except Exception as e:
            await matcher.send('诶鸭出错啦~')
            raise e                   

    async def send_stats(self, matcher: Matcher, uid: str = None, steam64id: str = None, at: str = None, limit: str = 5) -> None:
        try:
            if uid:
                await self.lucky_orb(matcher, uid)
                
                reply = '唔~你还没有设置Steam个人资料为公开呢~\n更改为公开后可以先在https://interface.100oj.com/stat/player.php来查看是否已经可以查询到数据，确认可查到后再次使用该功能。(该设置有一定的延迟。)'
                await self.cursor.execute('SELECT steam64id,renderType,sp1 FROM steamInfo WHERE qq = ?', (uid,))
                data = await self.cursor.fetchall()
                if data == [] or data is None or data[0][0] == 0:
                    await matcher.send('你还没有绑定过Steam哦~请使用 #stat bind <steam64id> 来进行绑定。')
                    return None
                
            if steam64id:
                reply = '唔~Ta还没有设置Steam个人资料为公开呢~'
                await self.cursor.execute('SELECT steam64id,renderType,sp1 FROM steamInfo WHERE steam64id = ?', (steam64id,))
                data = await self.cursor.fetchall()
                if data == [] or data is None or data[0][0] == 0:
                    data = ((steam64id, 0, 0),)

            if at:
                uid = re.sub(r'\[at:qq=(.*?)\]', r'\1', at)  
                reply = '唔~Ta还没有设置Steam个人资料为公开呢~'
                await self.cursor.execute('SELECT steam64id,renderType,sp1 FROM steamInfo WHERE qq = ?', (uid,))
                data = await self.cursor.fetchall()
                if data == [] or data is None or data[0][0] == 0:
                    await matcher.send('Ta还没有绑定过Steam哦~')
                    return None

            
            
            img = f'https://interface.100oj.com/stat/render.php?steamid={data[0][0]}&render={data[0][1]}&sp1={data[0][2]}&limit={limit}'
            
            timeout = aiohttp.ClientTimeout(total=60)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                req = await session.get(img)
                data = await req.read()
            
            if data == b'':
                await matcher.send(reply)
            else:
                await matcher.send(MessageSegment.image(img))
                
        except Exception as e:
            await matcher.send('诶鸭出错啦~')
            raise e


    async def stats(self, bot: Bot, matcher: Matcher, event: Union[GroupMessageEvent, PrivateMessageEvent], arg: Message = CommandArg()) -> None:
        if not ess.check(event, 'Stats'):
            return None

    
        rich_text: str = arg.to_rich_text()
        rich_text = re.sub(' +', ' ', rich_text)
        
        list_args = rich_text.split(' ')

        while len(list_args) < 3:
            list_args.append('')
            
        logger.info(f'参数解析结果：{list_args}')

        match list_args[0]:
            case 'help' | '':
                await self.help(matcher)
            case 'bind' | '-b':
                uid = str(event.user_id)
                match list_args[1]:
                    case '':
                        await matcher.finish('请输入steam64id。')
                    case steam64id if steam64id.isdigit() and steam64id.startswith('7656') and len(steam64id) == 17:
                        steam64id = list_args[1]
                        await self.bind(uid, steam64id, matcher)
                    case _:
                        await matcher.finish('这不是一个有效的steam64id。它应该是一个以7656开头、总长度为17位的纯数字。\n如果您不知道什么是steam64id，推荐在网络上了解更多的相关知识。')
            case 'unbind' | '-u':
                uid = str(event.user_id)
                await self.unbind(uid, matcher)
            case 'type' | '-t':
                uid = str(event.user_id)
                match list_args[1]:
                    case '':
                        await matcher.finish('请输入出图类型代码。')
                    case type if int(type) in range(0, 9):
                        type = list_args[1]
                        await self.type(uid, type, matcher)
                    case _:
                        await matcher.finish('这不是一个有效的出图类型代码。它应该介于0与8之间。')
            case 'pin' | '-p':
                uid = str(event.user_id)
                match list_args[1]:
                    case '':
                        await matcher.finish('请输入pin代码。')
                    case pin if int(pin) in range(0, 7) or pin == '31' or pin == '37':
                        pin = list_args[1]
                        await self.pin(uid, pin, matcher)
                    case _:
                        await matcher.finish('这不是一个有效的pin代码。请在 https://interface.100oj.com/stat/pininfo.html 查看所有类型。')
            case 'me':
                uid = str(event.user_id)
                match list_args[1]:
                    case limit if limit.isdigit():
                        limit: str = list_args[1]
                        await self.send_stats(matcher, uid=uid, limit=limit)
                    case _:
                        await self.send_stats(matcher, uid=uid)
            case at if at.startswith('[at'):
                at = list_args[0]
                match list_args[1]:
                    case limit if limit.isdigit():
                        limit: str = list_args[1]
                        await self.send_stats(matcher, at=at, limit=limit)
                    case _:
                        await self.send_stats(matcher, at=at)
            case steam64id if steam64id.isdigit() and steam64id.startswith('7656') and len(steam64id) == 17:
                steam64id = list_args[0]
                match list_args[1]:
                    case limit if limit.isdigit():
                        limit: str = list_args[1]
                        await self.send_stats(matcher, steam64id=steam64id, limit=limit)
                    case _:
                        await self.send_stats(matcher, steam64id=steam64id)
            case 'get':
                if str(event.user_id) not in bot.config.superusers:
                    return None
                target_uid = list_args[1]
                target_uid = re.sub(r'\[at:qq=(.*?)\]', r'\1', target_uid)
                logger.debug(f'Get Trigger: {target_uid}')
                await self.get(matcher, target_uid)
            case 'modify':
                if str(event.user_id) not in bot.config.superusers:
                    return None
                
                target_uid, key, value = list_args[1:4]
                target_uid = re.sub(r'\[at:qq=(.*?)\]', r'\1', target_uid)
                logger.debug(f'Modify Trigger: {target_uid} {key} {value}')
                await self.modify(matcher, target_uid, key, value)
            case _:
                await self.help(matcher)

stats: Stats = Stats()
driver = get_driver()

@driver.on_startup
async def init_card() -> None:
    await stats.init_database()
