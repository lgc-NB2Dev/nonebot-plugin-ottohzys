from nonebot import get_plugin_config
from pydantic import BaseModel


class ConfigModel(BaseModel):
    pass


config: ConfigModel = get_plugin_config(ConfigModel)
