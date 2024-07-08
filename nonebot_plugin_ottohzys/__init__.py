from nonebot.plugin import PluginMetadata, inherit_supported_adapters, require

require("nonebot_plugin_alconna")

from . import __main__ as __main__  # noqa: E402
from .config import ConfigModel  # noqa: E402

__version__ = "0.2.1.post1"
__plugin_meta__ = PluginMetadata(
    name="大电老师活字印刷",
    description="大家好啊，今天来点大家想看的东西",
    usage="直接使用指令【ottohzys】加上文本就行了，不带参数查看详细帮助，不会用我阐述你的梦",
    type="application",
    homepage="https://github.com/lgc-NB2Dev/nonebot-plugin-ottohzys",
    config=ConfigModel,
    supported_adapters=inherit_supported_adapters("nonebot_plugin_alconna"),
    extra={"License": "MIT", "Author": "student_2333"},
)
