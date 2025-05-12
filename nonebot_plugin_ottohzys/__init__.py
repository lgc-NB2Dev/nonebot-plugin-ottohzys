# ruff: noqa: E402

import asyncio

from nonebot import get_driver, logger
from nonebot.plugin import PluginMetadata, inherit_supported_adapters, require

require("nonebot_plugin_localstore")
require("nonebot_plugin_alconna")

from . import __main__ as __main__
from .config import DATA_DIR, ConfigModel, config
from .migrate import v0_migrate
from .pack import pack_manager
from .pack.online import download_pack

__version__ = "1.0.1"
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
    async def task():
        v0_migrate()
        pack_manager.reload()

        if not pack_manager.get_pack(config.default_pack):
            logger.info(f"Downloading default voice pack (`{config.default_pack}`)")
            try:
                await download_pack(config.default_pack, DATA_DIR / config.default_pack)
            except Exception:
                logger.exception(
                    f"Failed to download voice pack `{config.default_pack}`",
                )
            else:
                logger.success("Downloaded voice pack `{config.default_pack}`")
                pack_manager.reload()

    asyncio.create_task(task())
