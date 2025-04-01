from pathlib import Path

from .pack import VoicePack


class VoicePackManager:
    def __init__(self, base_path: Path) -> None:
        self.base_path = base_path
        self.packs: list[VoicePack] = []

    def reload(self):
        pass
