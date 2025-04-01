from pathlib import Path

from nonebot import logger

from .pack import VoicePack


class VoicePackManager:
    def __init__(self, base_path: Path) -> None:
        self.base_path = base_path
        self.packs: list[VoicePack] = []

    def reload(self):
        self.packs.clear()
        for pack_path in (
            x
            for x in self.base_path.iterdir()
            if (x.is_dir() and (not x.name.startswith("_")) and VoicePack.valid(x))
        ):
            self.packs.append(pack := VoicePack(pack_path))
            logger.debug(f"Loaded pack `{pack.name}`")
        logger.success(f"Successfully loaded {len(self.packs)} packs")
