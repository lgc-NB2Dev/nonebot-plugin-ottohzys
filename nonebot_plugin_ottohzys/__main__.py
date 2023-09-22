from nonebot import logger, on_shell_command
from nonebot.adapters.onebot.v11 import MessageSegment
from nonebot.exception import ParserExit
from nonebot.matcher import Matcher
from nonebot.params import ShellCommandArgs
from nonebot.rule import ArgumentParser, Namespace

from .hzys import generate

COMMANDS = ("ottohzys", "otto活字印刷", "otto鬼叫", "电棍hzys", "电棍活字印刷", "电棍鬼叫")
CMD_PRIMARY, *CMD_ALIAS = COMMANDS


cmd_otto_parser = ArgumentParser(CMD_PRIMARY, add_help=False)
cmd_otto_parser.add_argument(
    "--reverse",
    "-r",
    action="store_true",
    help="是否倒放",
    default=False,
)
cmd_otto_parser.add_argument(
    "--speed",
    "-s",
    type=float,
    help="语音速度，范围 >= 0.5，默认 1.0，越小速度越快",
    default=1.0,
)
cmd_otto_parser.add_argument(
    "--pitch",
    "-p",
    type=float,
    help="语音音调，范围 0 < pitch < 2，默认 1.0，越小音调越低",
    default=1.0,
)
cmd_otto_parser.add_argument(
    "--ysdd",
    "-y",
    action="store_false",
    help="特定语句是否 不使用 原声大碟",
    default=True,
)
cmd_otto_parser.add_argument(
    "--pause",
    "-P",
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
    reverse: bool = args.reverse
    speed: float = args.speed
    pitch: float = args.pitch
    ysdd: bool = args.ysdd
    sentence = " ".join(str(x) for x in args.sentence).strip()

    if speed < 0.5:
        await matcher.finish(TIP_TOO_EXTREME)
    if not 0 < pitch < 2:
        await matcher.finish(TIP_TOO_EXTREME)
    if not sentence:
        await matcher.finish(HELP)

    try:
        voice = await generate(sentence, ysdd, speed, pitch, reverse)
    except Exception:
        logger.exception("Failed to generate voice")
        await matcher.finish("生成语音失败")

    await matcher.finish(MessageSegment.record(voice))
