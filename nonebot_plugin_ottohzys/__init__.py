# ruff: noqa: E402

from nonebot import get_driver
from nonebot.plugin import PluginMetadata, inherit_supported_adapters, require

require("nonebot_plugin_localstore")
require("nonebot_plugin_alconna")

from . import __main__ as __main__
from .config import ConfigModel
from .migrate import v0_migrate
from .pack import pack_manager

__version__ = "1.0.0"
__plugin_meta__ = PluginMetadata(
    name="活字印刷",
    description="大家好啊，今天来点大家想看的东西",
    usage="",
    type="application",
    homepage="https://github.com/lgc-NB2Dev/nonebot-plugin-ottohzys",
    config=ConfigModel,
    supported_adapters=inherit_supported_adapters("nonebot_plugin_alconna"),
    extra={"License": "MIT", "Author": "LgCookie"},
)


driver = get_driver()


@driver.on_startup
async def _():
    v0_migrate()
    pack_manager.reload()
