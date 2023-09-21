from nonebot import logger, on_shell_command
from nonebot.adapters.onebot.v11 import MessageSegment
from nonebot.matcher import Matcher
from nonebot.params import ShellCommandArgs
from nonebot.rule import ArgumentParser, Namespace

from .hzys import generate

COMMANDS = ("ottohzys", "otto活字印刷", "otto鬼叫", "电棍hzys", "电棍活字印刷", "电棍鬼叫")
CMD_PRIMARY, *CMD_ALIAS = COMMANDS


cmd_otto_parser = ArgumentParser(CMD_PRIMARY)
cmd_otto_parser.add_argument("sentence", nargs="+", help="要转换的文本")

cmd_otto = on_shell_command(CMD_PRIMARY, aliases=set(CMD_ALIAS), parser=cmd_otto_parser)


@cmd_otto.handle()
async def _(matcher: Matcher, args: Namespace = ShellCommandArgs()):
    sentence = " ".join(str(x) for x in args.sentence)

    try:
        voice = await generate(sentence)
    except Exception:
        logger.exception("Failed to generate voice")
        await matcher.finish("生成语音失败")

    await matcher.finish(MessageSegment.record(voice))
