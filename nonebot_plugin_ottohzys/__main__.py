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
from nonebot import logger
from nonebot_plugin_alconna import AlconnaMatcher, Query, on_alconna
from nonebot_plugin_alconna.uniseg import UniMessage

from .config import DEFAULT_PACK_NAME, debug
from .pack import pack_manager
from .pack.audio import save_data
from .pack.hzys import generate_data

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
    meta=CommandMeta("活字印刷"),
)
m_cls = on_alconna(
    alc,
    aliases={"活字印刷"},
    skip_for_unmatch=False,
    auto_send_output=True,
    use_cmd_start=True,
)

TIP_TOO_EXTREME = "过于极端的音调和速度参数可能导致输出结果与预期不符"


@m_cls.handle()
async def _(
    m: AlconnaMatcher,
    q_sentence: Query[Optional[str]] = Query("sentence"),
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

    debug.write(voice, "{time}.wav")

    await UniMessage.voice(raw=voice).send()
