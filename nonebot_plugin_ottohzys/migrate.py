import shutil
from pathlib import Path

from nonebot import logger

from .config import DATA_DIR
from .pack.pack import (
    TOKENS_DIRNAME,
    YSDD_TOKENS_DIRNAME,
    YSDD_TOKENS_FILENAME,
)

OLD_DATA_DIR = Path("data/ottohzys")


def v0_migrate():
    if not OLD_DATA_DIR.exists():
        return

    logger.info("Migrating data from old version")

    pack_dir = DATA_DIR / "otto"

    shutil.copytree(OLD_DATA_DIR / "tokens", pack_dir / TOKENS_DIRNAME)
    shutil.copytree(OLD_DATA_DIR / "ysddTokens", pack_dir / YSDD_TOKENS_DIRNAME)
    # shutil.copy(OLD_DATA_DIR / "chinglish.json", pack_dir / CHINGLISH_FILENAME)
    shutil.copy(OLD_DATA_DIR / "ysdd.json", pack_dir / YSDD_TOKENS_FILENAME)
    (pack_dir / "config.json").write_text(
        ('{\n  "commands": ["ottohzys", "电棍活字印刷", "大电老师活字印刷"]\n}\n'),
        "u8",
    )

    shutil.rmtree(OLD_DATA_DIR)

    logger.info("Successfully migrated data from old version")
