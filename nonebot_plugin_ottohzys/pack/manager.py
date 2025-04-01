from pathlib import Path
from typing import Any, Callable, Optional
from typing_extensions import TypeAlias

from nonebot import logger

from .pack import VoicePack

BeforeReloadHook: TypeAlias = Callable[["VoicePackManager"], Any]
AfterReloadHook: TypeAlias = Callable[["VoicePackManager"], Any]


class VoicePackManager:
    def __init__(self, base_path: Path) -> None:
        self.base_path = base_path
        self.packs: list[VoicePack] = []
        self.before_reload_hooks: list[BeforeReloadHook] = []
        self.after_reload_hooks: list[AfterReloadHook] = []

    def register_before_reload_hook(self, hook: BeforeReloadHook):
        self.before_reload_hooks.append(hook)
        return hook

    def register_after_reload_hook(self, hook: AfterReloadHook):
        self.after_reload_hooks.append(hook)
        return hook

    def reload(self):
        for hook in self.before_reload_hooks:
            hook(self)
        self.packs.clear()

        for pack_path in (
            x
            for x in self.base_path.iterdir()
            if (x.is_dir() and (not x.name.startswith("_")) and VoicePack.valid(x))
        ):
            try:
                self.packs.append(pack := VoicePack(pack_path))
            except Exception:
                logger.exception(f"Failed to load pack `{pack_path.name}`")
            else:
                logger.debug(f"Loaded pack `{pack.name}`")

        for hook in self.after_reload_hooks:
            hook(self)
        logger.success(f"Successfully loaded {len(self.packs)} packs")

    def get_pack(self, name: str) -> Optional[VoicePack]:
        return next((x for x in self.packs if x.name == name), None)
