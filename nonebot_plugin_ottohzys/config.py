from pathlib import Path

from cookit.nonebot.localstore import ensure_localstore_path_config
from cookit.pyd import get_alias_model
from nonebot import get_plugin_config
from nonebot_plugin_localstore import get_plugin_data_dir

ensure_localstore_path_config()
DATA_DIR = get_plugin_data_dir()
SOURCE_DIR = Path(__file__).parent
SOURCE_RES_DIR = SOURCE_DIR / "res"

AliasConfigModel = get_alias_model(lambda _: "ottohzys_")


class ConfigModel(AliasConfigModel):
    default_sound_pack: str = "otto"


config: ConfigModel = get_plugin_config(ConfigModel)
