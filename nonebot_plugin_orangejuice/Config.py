from typing import Optional, List, Literal
from pydantic import Extra, BaseModel

from nonebot import get_driver

class Config(BaseModel, extra=Extra.ignore):
    oj_data_path: Optional[str] = 'data/100oj'

plugin_config = Config.parse_obj(get_driver().config)