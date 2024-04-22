from typing import Optional
from pydantic import BaseModel

try:
    # pydantic v2
    from nonebot import get_plugin_config
except ImportError:
    # pydantic v1
    from nonebot import get_driver

class Config(BaseModel):
    oj_data_path: Optional[str] = 'data/100oj'
    match_score: Optional[int] = 75

plugin_config = None

try:
    # pydantic v2
    plugin_config = get_plugin_config(Config)
except:
    # pydantic v1
    plugin_config = Config.parse_obj(get_driver().config)