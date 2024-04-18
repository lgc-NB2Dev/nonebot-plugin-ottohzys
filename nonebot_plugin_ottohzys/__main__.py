from nonebot import logger, on_shell_command
from nonebot.exception import ParserExit
from nonebot.matcher import Matcher
from nonebot.params import ShellCommandArgs
from nonebot.rule import ArgumentParser, Namespace
from nonebot_plugin_alconna.uniseg import UniMessage

from .hzys import generate

CMD_PREFIXES = ("otto", "电棍", "大电老师")
CMD_SUFFIXES = ("活字印刷", "鬼叫", "hzys")
COMMANDS = [f"{prefix}{suffix}" for prefix in CMD_PREFIXES for suffix in CMD_SUFFIXES]
CMD_PRIMARY, *CMD_ALIAS = COMMANDS


cmd_otto_parser = ArgumentParser(CMD_PRIMARY, add_help=False)
cmd_otto_parser.add_argument(
    "-r",
    "--reverse",
    action="store_true",
    help="是否倒放",
    default=False,
)
cmd_otto_parser.add_argument(
    "-Y",
    "--no-ysdd",
    action="store_true",
    help="特定语句是否 不使用 原声大碟",
    default=False,
)
cmd_otto_parser.add_argument(
    "-N",
    "--no-normalize",
    action="store_true",
    help="是否 不使用 自动音量归一化",
    default=False,
)
cmd_otto_parser.add_argument(
    "-s",
    "--speed",
    type=float,
    help="语音速度，范围 >= 0.5，默认 1.0，越小速度越慢",
    default=1.0,
)
cmd_otto_parser.add_argument(
    "-p",
    "--pitch",
    type=float,
    help="语音音调，范围 0 < pitch <= 2，默认 1.0，越大音调越高",
    default=1.0,
)
cmd_otto_parser.add_argument(
    "-P",
    "--pause",
    type=float,
    help="空格等字符的停顿时间，单位秒，默认 0.25",
    default=0.25,
)
cmd_otto_parser.add_argument("sentence", nargs="*", help="要生成语音的文本")

HELP = cmd_otto_parser.format_help()
TIP_TOO_EXTREME = "过于极端的音调和速度参数可能导致输出结果与预期不符"

cmd_otto = on_shell_command(CMD_PRIMARY, aliases=set(CMD_ALIAS), parser=cmd_otto_parser)


@cmd_otto.handle()
async def _(matcher: Matcher, err: ParserExit = ShellCommandArgs()):
    await matcher.finish(f"解析指令参数出错：{err.message}")


@cmd_otto.handle()
async def _(matcher: Matcher, args: Namespace = ShellCommandArgs()):
    # if not check_resource_sync():
    #     await matcher.finish("未找到需要的资源文件，请检查")

    sentence = " ".join(str(x) for x in args.sentence).strip()
    reverse: bool = args.reverse
    ysdd: bool = not args.no_ysdd
    normalize: bool = not args.no_normalize
    speed: float = args.speed
    pitch: float = args.pitch
    pause: float = args.pause

    if speed < 0.5:
        await matcher.finish(TIP_TOO_EXTREME)
    if not 0 < pitch <= 2:
        await matcher.finish(TIP_TOO_EXTREME)
    if not sentence:
        await matcher.finish(HELP)

    try:
        voice = await generate(
            sentence=sentence,
            reverse=reverse,
            ysdd_mode=ysdd,
            normalize=normalize,
            speed_multiple=speed,
            pitch_multiple=pitch,
            pause_length=pause,
        )
    except Exception:
        logger.exception("Failed to generate voice")
        await matcher.finish("生成语音失败")

    await UniMessage.voice(raw=voice).send()
