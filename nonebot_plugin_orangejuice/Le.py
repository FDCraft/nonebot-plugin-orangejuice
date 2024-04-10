import os
import random
import time
from typing import Union, List, Tuple

from nonebot import require, logger
from nonebot.adapters.onebot.v11 import Bot, Message, MessageSegment, GroupMessageEvent, PrivateMessageEvent
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
        
        deckList = ["冲刺！","纱季的曲奇","迁怒于人","远距离射击","美妙的叮铃铃","美妙的礼物","坚固的结晶","布丁","残机奖励","大小姐的特权",
            "孤独的暴走车","偷袭","探究心","学生会长的权益","模仿","成功报酬","绅士的决斗","宝物小偷","拦路者","幕后交易","加班","我的野生朋友们","传送操控",
            "燃起来吧！","兔子浮游炮","虹色之环","大麦格农炮","护盾","最终决战","性格反转力场","临阵脱逃","护盾反转","极速超能",
            "部件扩张","瞬间再生","阴谋的资金筹集","自暴自弃的改造","赌命一搏","殊死对决","便携布丁","虚假除械","可爱大对决",
            "糟糕的布丁","米缪冲击锤","危险布丁","存钱罐","袭来","飞一边去","热度300%","突击","深夜的惨剧","互相交换","喷射火焰","空中餐厅「纯洁」",
            "为了玩具店的未来","小鸡小鸡大游行","记忆封印","无情的恶作剧","礼物小偷","通缉令","啵噗化","想要见到你","安可","香蕉奈奈子","啵噗银行",
            "这里那里","大群的海鸥","神圣之夜","弹药用尽","礼物交换","我们是阴谋组","晚餐","超绝认真模式",
            "强制复活","小小的战争","我的朋友呀","被封印的守护者","混成化现象","恐怖的推销","众神的嬉戏","大争夺·圣诞夜","烧毁星球之光","派对时间",
            "加速空域","宁静","劳而无薪","无差别火力支援","宠物零食","家居翻修","甜点的破坏者","宠物零食","反抗",
            "不幸护符","疾风附魔","迷路的孩子","力量的代价","掠夺者啵噗","鲜血渴望","幸运护符","全金属单体结构","幸运7","奈奈子的浮游炮",
            "露露的幸运蛋","露露的幸运蛋","露露的幸运蛋","露露的幸运蛋","露露的幸运蛋","露露的幸运蛋","露露的幸运蛋","露露的幸运蛋","露露的幸运蛋","露露的幸运蛋",
            "露露的幸运蛋","露露的幸运蛋","露露的幸运蛋","露露的幸运蛋","露露的幸运蛋","露露的幸运蛋","露露的幸运蛋"]
        
        image_path = os.path.join(os.path.dirname(__file__), 'resources', 'lulu')
        
        effect = random.randint(0, 2)
        if random.random() <= 0.99:
            if effect == 0:
                dice = random.randint(1, 6)
                await matcher.finish(MessageSegment.image(os.path.join(image_path, 'le0.png')) + f'露露的幸运蛋结果：\n投掷骰子，获得 {dice*20} Stars')
            elif effect == 1:
                deck = []
                for i in range(0, 5):
                    deck.append('「' + random.choice(deckList) + '」')
                await matcher.finish(MessageSegment.image(os.path.join(image_path, 'le1.png')) + f'露露的幸运蛋结果：\n抽取 5 张卡\n{", ".join(deck)}')
            else:
                await matcher.finish(MessageSegment.image(os.path.join(image_path, 'le2.png')) + '露露的幸运蛋结果：\n恢复所有HP，获得永久ATK、DEF、EVD+1')
        else:
            if effect == 0:
                await matcher.finish(MessageSegment.image(os.path.join(image_path, 'le0b.png')) + '『脸伸过来！』')
            if effect == 1:
                await matcher.finish(MessageSegment.image(os.path.join(image_path, 'le1b.png')) + '『蓝碟！』')
            else:
                await matcher.finish(MessageSegment.image(os.path.join(image_path, 'le2b.png')) + '『露露的幸运蛋壳！』')

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
        seed = round(abs(hash("Polaris_Light" + str(now.tm_yday)+ str(now.tm_year) + "XYZ") / 3.0 + hash("QWERTY" + arg + str(event.user_id) + "0*8&6" + str(now.tm_mday) + "96485.3329") / 3.0))
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
        await matcher.finish(f'今天是{now.tm_year}年{now.tm_mon}月{now.tm_mday}日\n{user_name}所求事项：【{arg}】\n\n结果: 【{result}】')

check = Check()
le = Le()