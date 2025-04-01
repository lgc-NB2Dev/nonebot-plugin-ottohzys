import json
from pathlib import Path
from typing import Optional
from typing_extensions import TypeAlias

from cachetools import TTLCache
from cookit.pyd import type_validate_json
from cookit.pyd.compat import type_dump_python
from pydantic import BaseModel

from ..config import SOURCE_RES_DIR
from .audio import SoundArrayType, find_sound_file, load_audio

TokenMapType: TypeAlias = dict[str, str]
YsddTokenMapType: TypeAlias = dict[str, list[str]]

CONFIG_FILENAME = "config.json"
CHINGLISH_FILENAME = "chinglish.json"
YSDD_TOKENS_FILENAME = "ysdd.json"
TOKENS_DIRNAME = "tokens"
YSDD_TOKENS_DIRNAME = "ysdd_tokens"

_default_chinglish_map: Optional[TokenMapType] = None


def load_default_chinglish_map() -> TokenMapType:
    global _default_chinglish_map
    if _default_chinglish_map is None:
        _default_chinglish_map = type_validate_json(
            TokenMapType,
            (SOURCE_RES_DIR / CHINGLISH_FILENAME).read_text("u8"),
        )
    return _default_chinglish_map


class PackConfig(BaseModel):
    commands: list[str] = []


class TokenManager:
    def __init__(
        self,
        base_path: Path,
        max_size: Optional[int] = 32,
        ttl: int = 300,
    ) -> None:
        self.base_path = base_path
        self._cache = (
            TTLCache[str, SoundArrayType](maxsize=max_size, ttl=ttl)
            if max_size
            else None
        )

    def get(self, token: str, normalize: bool = True) -> Optional[SoundArrayType]:
        if path := find_sound_file(self.base_path, token):
            data = load_audio(path, normalize)
            if self._cache is not None:
                self._cache[token] = data
            return data
        return None


class VoicePack:
    def __init__(self, base_path: Path) -> None:
        self.base_path = base_path
        self.config = self.read_config()
        self.token_manager = TokenManager(base_path / TOKENS_DIRNAME)
        self.ysdd_token_manager = TokenManager(base_path / YSDD_TOKENS_DIRNAME, 0)

        self._chinglish_map: Optional[TokenMapType] = None
        self._ysdd_tokens_map: Optional[YsddTokenMapType] = None

    @staticmethod
    def valid(base_path: Path):
        return (base_path / TOKENS_DIRNAME).exists()

    @property
    def name(self) -> str:
        return self.base_path.name

    @property
    def chinglish_map(self) -> TokenMapType:
        if not (self.base_path / CHINGLISH_FILENAME).exists():
            return load_default_chinglish_map()
        if self._chinglish_map is None:
            self._chinglish_map = type_validate_json(
                TokenMapType,
                (self.base_path / CHINGLISH_FILENAME).read_text("u8"),
            )
        return self._chinglish_map

    @property
    def ysdd_tokens_map(self) -> YsddTokenMapType:
        if not (self.base_path / YSDD_TOKENS_FILENAME).exists():
            return {}
        if self._ysdd_tokens_map is None:
            self._ysdd_tokens_map = type_validate_json(
                YsddTokenMapType,
                (self.base_path / YSDD_TOKENS_FILENAME).read_text("u8"),
            )
        return self._ysdd_tokens_map

    def read_config(self) -> PackConfig:
        if not (self.base_path / CONFIG_FILENAME).exists():
            p = PackConfig()
            (self.base_path / CONFIG_FILENAME).write_text(
                json.dumps(type_dump_python(p), ensure_ascii=False, indent=2),
                "u8",
            )
            return p
        return type_validate_json(
            PackConfig,
            (self.base_path / CONFIG_FILENAME).read_text("u8"),
        )

    def get_token(
        self,
        token: str,
        is_ysdd: bool = False,
        normalize: bool = True,
    ) -> Optional[SoundArrayType]:
        if is_ysdd:
            return self.ysdd_token_manager.get(token, normalize)
        return self.token_manager.get(token, normalize)
