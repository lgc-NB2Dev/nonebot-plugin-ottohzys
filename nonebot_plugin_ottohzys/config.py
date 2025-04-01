from pathlib import Path
from typing import Optional

from cookit import DebugFileWriter
from cookit.nonebot.localstore import ensure_localstore_path_config
from cookit.pyd import get_alias_model
from nonebot import get_plugin_config
from nonebot_plugin_localstore import get_plugin_data_dir
from pydantic import Field

ensure_localstore_path_config()
DATA_DIR = get_plugin_data_dir()
SOURCE_DIR = Path(__file__).parent
SOURCE_RES_DIR = SOURCE_DIR / "res"

AliasConfigModel = get_alias_model(lambda k: f"ottohzys_{k}")

DEFAULT_PACK_LIST_URL = (
    "https://raw.githubusercontent.com/lgc-NB2Dev/nonebot-plugin-ottohzys"
    "/refs/heads/master"
    "/.github/voice_packs.json"
)
DEFAULT_PACK_DOWNLOAD_BASE_URL = (
    "https://github.com/lgc-NB2Dev/nonebot-plugin-ottohzys"
    "/releases/download/voice-packs/"
)

DEFAULT_PACK_NAME = "otto"


class ConfigModel(AliasConfigModel):
    proxy: Optional[str] = Field(None, alias="proxy")

    pack_list_url: str = DEFAULT_PACK_LIST_URL
    pack_download_base_url: str = DEFAULT_PACK_DOWNLOAD_BASE_URL

    default_pack: str = DEFAULT_PACK_NAME


config: ConfigModel = get_plugin_config(ConfigModel)

debug = DebugFileWriter(Path.cwd() / "debug", "ottohzys")
