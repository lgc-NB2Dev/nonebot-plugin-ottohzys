from typing import Optional

from arclet.alconna import (
    Alconna,
    Arg,
    Args,
    CommandMeta,
    Field,
    Option,
    OptionResult,
    store_true,
)
from cookit.nonebot import exception_notify
from httpx import HTTPStatusError
from nonebot import logger
from nonebot.matcher import current_bot, current_event
from nonebot.permission import SUPERUSER
from nonebot_plugin_alconna import AlconnaMatcher, Query, on_alconna
from nonebot_plugin_alconna.uniseg import UniMessage

from .config import DEFAULT_PACK_NAME, config, debug
from .pack import pack_manager
from .pack.audio import save_data
from .pack.hzys import generate_data
from .pack.manager import VoicePackManager
from .pack.online import download_pack, get_online_packs

alc = Alconna(
    "hzys",
    Args(
        Arg("sentence", Optional[str], notice="要生成语音的文本"),
    ),
    Option(
        "-p|--pack",
        Args["pack", str, Field(default=DEFAULT_PACK_NAME)],
        help_text="语音包名称",
    ),
    Option(
        "-r|--reverse",
        action=store_true,
        default=OptionResult(value=False),
        help_text="是否倒放",
    ),
    Option(
        "-Y|--no-ysdd",
        action=store_true,
        default=OptionResult(value=False),
        help_text="特定语句是否 不使用 原声大碟",
    ),
    Option(
        "-N|--no-normalize",
        action=store_true,
        default=OptionResult(value=False),
        help_text="是否 不使用 自动音量归一化",
    ),
    Option(
        "-s|--speed",
        Args["speed", float, Field(default=1.0)],
        help_text="语音速度，范围 >= 0.5，默认 1.0，越小速度越慢",
    ),
    Option(
        "-p|--pitch",
        Args["pitch", float, Field(default=1.0)],
        help_text="语音音调，范围 0 < pitch <= 2，默认 1.0，越大音调越高",
    ),
    Option(
        "-P|--pause",
        Args["pause", float, Field(default=0.25)],
        help_text="空格等字符的停顿时间，单位秒，默认 0.25",
    ),
    Option(
        "-Lo|--list-online",
        action=store_true,
        default=OptionResult(value=False),
        help_text="列出在线语音包（仅超级用户可用）",
    ),
    Option(
        "-Ll|--list-local",
        action=store_true,
        default=OptionResult(value=False),
        help_text="列出本地语音包",
    ),
    Option(
        "-Ly|--list-ysdd",
        action=store_true,
        default=OptionResult(value=False),
        help_text="列出当前语音包可用的原声大碟",
    ),
    Option(
        "-R|--reload",
        action=store_true,
        default=OptionResult(value=False),
        help_text="重载本地语音包（仅超级用户可用）",
    ),
    Option(
        "-D|--download",
        Args["pack", str],
        help_text="下载在线语音包（仅超级用户可用）",
    ),
    meta=CommandMeta(
        "活字印刷",
        usage=(f'hzys -p {config.default_pack} "大家好啊 我是电棍"\nhzys -p -Ly'),
    ),
)
m_cls = on_alconna(
    alc,
    aliases={"活字印刷"},
    skip_for_unmatch=False,
    auto_send_output=True,
    use_cmd_start=True,
)

TIP_TOO_EXTREME = "过于极端的音调和速度参数可能导致输出结果与预期不符"


async def is_superuser():
    return await SUPERUSER(current_bot.get(), current_event.get())


@m_cls.assign("~list-online.value", value=True)
async def _(m: AlconnaMatcher):
    if not await is_superuser():
        await m.finish()
    async with exception_notify("获取在线语音包失败"):
        packs = await get_online_packs()
    lst = "\n".join(f"- {x.name}: {x.description}" for x in packs)
    await m.finish(f"目前可用的在线语音包：\n{lst}")


@m_cls.assign("~list-local.value", value=True)
async def _(m: AlconnaMatcher):
    lst = "\n".join(
        f"- {x.name}\n  - 已注册指令：{', '.join(x.config.commands)}"
        for x in pack_manager.packs
    )
    await m.finish(f"目前已加载的语音包：\n{lst}")


@m_cls.assign("~list-ysdd.value", value=True)
async def _(
    m: AlconnaMatcher,
    q_pack: Query[str] = Query("~pack"),
):
    if not (pack := pack_manager.get_pack(q_pack.result)):
        await m.finish("找不到指定的贴纸包")
    lst = "\n".join(f"- {' / '.join(v)}" for v in pack.ysdd_tokens_map.values())
    await m.finish(f"当前语音包可用的原声大碟：\n{lst}")


@m_cls.assign("~reload.value", value=True)
async def _(m: AlconnaMatcher):
    if not await is_superuser():
        await m.finish()
    try:
        pack_manager.reload()
    except Exception:
        logger.exception("Failed to reload voice packs")
        await m.finish("重载语音包失败")
    await m.finish("重载完毕")


@m_cls.assign("~download")
async def _(
    m: AlconnaMatcher,
    q_pack: Query[str] = Query("~download.pack"),
):
    if not await is_superuser():
        await m.finish()

    await m.send("请稍等，正在下载")
    try:
        await download_pack(q_pack.result, pack_manager.base_path / q_pack.result)
    except Exception as e:
        if isinstance(e, HTTPStatusError) and e.response.status_code == 404:
            await m.finish("找不到指定的语音包")
        logger.exception("Failed to download voice pack")
        await m.finish("下载失败")

    try:
        pack_manager.reload()
    except Exception:
        logger.exception("Failed to reload voice packs")
        await m.finish("重载语音包失败")

    await m.finish("下载完毕")


@m_cls.handle()
async def _(
    m: AlconnaMatcher,
    q_sentence: Query[Optional[str]] = Query("sentence", None),
    q_pack: Query[str] = Query("~pack"),
    q_reverse: Query[bool] = Query("~reverse.value"),
    q_no_ysdd: Query[bool] = Query("~no-ysdd.value"),
    q_no_normalize: Query[bool] = Query("~no-normalize.value"),
    q_speed: Query[float] = Query("~speed.speed"),
    q_pitch: Query[float] = Query("~pitch.pitch"),
    q_pause: Query[float] = Query("~pause.pause"),
):
    if not q_sentence.result:
        await m.finish(alc.get_help())

    if not (pack := pack_manager.get_pack(q_pack.result)):
        await m.finish("找不到指定的贴纸包")
    if q_speed.result < 0.5:
        await m.finish(TIP_TOO_EXTREME)
    if not 0 < q_pitch.result <= 2:
        await m.finish(TIP_TOO_EXTREME)

    try:
        voice_arr = generate_data(
            pack,
            sentence=q_sentence.result,
            reverse=q_reverse.result,
            ysdd_mode=not q_no_ysdd.result,
            normalize=not q_no_normalize.result,
            speed_multiple=q_speed.result,
            pitch_multiple=q_pitch.result,
            pause_length=q_pause.result,
        )
        voice = save_data(voice_arr)
    except Exception:
        logger.exception("Failed to generate voice")
        await m.finish("生成语音失败")

    if debug.enabled:
        debug.write(voice, "{time}.wav")

    await UniMessage.voice(raw=voice).send()


registered_commands: list[str] = []


@pack_manager.register_before_reload_hook
def _(_: VoicePackManager):
    for x in registered_commands:
        msg = alc.shortcut(x, delete=True)
        logger.debug(msg)


@pack_manager.register_after_reload_hook
def _(m: VoicePackManager):
    for p in m.packs:
        for x in p.config.commands:
            msg = alc.shortcut(x, arguments=["-p", p.name], prefix=True)
            logger.debug(msg)
