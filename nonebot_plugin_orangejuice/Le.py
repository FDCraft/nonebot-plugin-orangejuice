import json
import os
import random
import time
from typing import Union, Dict, List, Tuple

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

le_file_path: str = os.path.join(plugin_config.oj_data_path, 'le.json')
init_json: Dict[str, Dict[str, Dict[str, int]]]
init_json = {
    "114514": {
        "1919810": {
            "count": 0,
            "last_time": 0
        }    
    }
}

class Check:
    def __init__(self) -> None:
        if not os.path.exists(le_file_path):
            if not os.path.exists(plugin_config.oj_data_path):
                os.makedirs(plugin_config.oj_data_path)
            self.init_json()  

        self.load_json()
        
        def reset_user_count():
            self.data = {}
            self.save_json()
            
        try:
            scheduler.add_job(reset_user_count, "cron", hour="0", id="clear_le")
        except ActionFailed as e:
            logger.warning(f"定时任务添加失败，{repr(e)}")
            
    def init_json(self):
        with open(le_file_path, 'w+') as f:
            f.write(json.dumps(init_json, indent=4))

    def load_json(self):
        with open(le_file_path, 'r', encoding='utf-8') as f:
            data: Dict[str, Dict[str, Dict[str, int]]]
            data = json.load(f)
            self.data = data

    def save_json(self):
        with open(le_file_path, 'w', encoding='utf-8') as f:
            json_data = json.dumps(self.data, indent=4)
            f.write(json_data)
            
    def check_uid(self, gid: Union[int, str], uid: Union[int, str]) -> None:
        if str(gid) not in self.data:
            self.data[str(gid)] = {}
        if str(uid) not in self.data[str(gid)]:
            self.data[str(gid)][str(uid)] = {
                "count": 0,
                "last_time": 0
            }
        self.save_json()

    def check_cd(self, event: Union[GroupMessageEvent, PrivateMessageEvent]) -> bool:
        if isinstance(event, PrivateMessageEvent):
            return False
        
        gid = event.group_id
        uid = event.user_id
        current_time = int(time.time())

        ess.check_gid(gid)
        
        if ess.config['group_config_list'][str(gid)]['le_cd'] == 0:
            return False
        
        self.check_uid(gid, uid)
        
        if str(uid) not in self.data[str(gid)]:
            self.data[str(gid)][str(uid)]['last_time'] = current_time
            return False
        
        delta_time = current_time - self.data[str(gid)][str(uid)]['last_time']
        
        if delta_time >= ess.config['group_config_list'][str(gid)]['le_cd']:
            self.data[str(gid)][str(uid)]['last_time'] = current_time
            self.save_json()
            return False
        else:
            return True
    
    def check_max(self, event: Union[GroupMessageEvent, PrivateMessageEvent]) -> bool:
        if isinstance(event, PrivateMessageEvent):
            return False
        
        gid = event.group_id
        uid = event.user_id
        
        ess.check_gid(gid)        
        
        if ess.config['group_config_list'][str(gid)]['le_max'] == 0:
            return False
        
        self.check_uid(gid, uid)
    
        if str(uid) not in self.data[str(gid)]:
            self.data[str(gid)][str(uid)]['count'] = 0
            return False

        if self.data[str(gid)][str(uid)]['count'] < ess.config['group_config_list'][str(gid)]['le_max']:
            self.data[str(gid)][str(uid)]['count'] += 1
            self.save_json()
            return False
        else:
            return True
        
    def check(self, event: Union[GroupMessageEvent, PrivateMessageEvent]) -> bool:
        return check.check_cd(event) or check.check_max(event)

class Le:
    def __init__(self) -> None:
        pass

    async def lulu(self, matcher: Matcher, event: Union[GroupMessageEvent, PrivateMessageEvent]) -> None:
        if not ess.check(event, 'Le'):
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
        if not ess.check(event, 'Le'):
            return None
        
        if check.check(event):
            return None

        points = [0, 0, 0]
        for i in range(0, 7):
            points[random.randint(0, 2)] += 1
        await matcher.finish(f'浮游炮展开结果：\nATK+{points[0]} DEF+{points[1]} EVD+{points[2]}')
    
    async def nico(self, matcher: Matcher, event: Union[GroupMessageEvent, PrivateMessageEvent], arg: Message = CommandArg()) -> None:
        if not ess.check(event, 'Le'):
            return None
        
        if check.check(event):
            return None

        text = arg.extract_plain_text()
        num = min(int(text), 9) if (text := text[:1]).isdigit() and int(text) else 4
    
        mw_list = ["平安的旅途","风信鸡的指引","烹饪时间","极速装置","束发魔女","主角的特权","甜点守护者","愤怒狂暴","湛蓝乌鸦·再临","给你的礼物",
            "反射外装","决杀手术","奇迹红豆冰淇淋","星之再生","金蛋","三角力场","变化无常的风车","亚空间通道","阴谋机器人出动！","恶魔之手",
            "阴谋的间谍行动～预备","坚实魔女","空间的跳跃(标记)","特别舞台","飞艇轰炸","束缚之锁","情报官","魔法狱火","记录重现","荒唐的性能",
            "阴谋的操纵者","兔子模玩店","扩散光子步枪","永恒的观测者","浮游炮展开","融化的记忆","圣诞小姐的工作","海贼在天上飞？","店铺扩张战略","天使之手",
            "超能模式！","永久流放","修罗场模式","玩偶使","白色圣诞大粉碎","赌博！","涡轮满载","×16大火箭","大爆炸铃","脱衣","隐身启动","劲敌","杀戮魔法",
            "神出鬼没","兽之魔女","不动之物体","艾莉的奇迹","爆燃！","自爆","火箭炮","大火箭炮","乔纳桑·速袭","另一个最终兵器","露露的幸运蛋","星球的导火线","才气觉醒",
            "水晶障壁","统治者","急速的亚莉希安罗妮","圣露眼","拜托了厨师长！","升档","炽热的商人之魂","月夜之舞","社交界亮相","黄昏色的梦","小麦格农炮","梦寐以求的世界",
            "星星收集者","甜点天堂","甜点制作者的魔法","甜点成堆大作战","假想越狱","露露是厄运之龙","母亲之力","艾莉的超能奇迹","前主角的光辉时刻", '抵抗之心', '全炮门开启']

        result = []
        for i in range(0, num):
            result.append('「' + random.choice(mw_list) + '」')
        await matcher.finish(f'奇迹漫步结果：\n{", ".join(result)}')

    async def divination(self, bot: Bot, matcher: Matcher, event: Union[GroupMessageEvent, PrivateMessageEvent], arg: Message = CommandArg()) -> None:
        if not ess.check(event, 'Le'):
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