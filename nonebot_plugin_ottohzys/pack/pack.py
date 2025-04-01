from pathlib import Path
from typing import Optional
from typing_extensions import TypeAlias

from cachetools import TTLCache
from cookit.pyd import type_validate_json

from ..audio import SoundArrayType
from ..config import SOURCE_RES_DIR

WordMapType: TypeAlias = dict[str, str]

CHINGLISH_FILENAME = "chinglish.json"
YSDD_TOKENS_FILENAME = "ysdd.json"
TOKENS_DIRNAME = "tokens"
YSDD_TOKENS_DIRNAME = "ysddTokens"

_default_chinglish_map: Optional[WordMapType] = None


def load_default_chinglish_map() -> WordMapType:
    global _default_chinglish_map
    if _default_chinglish_map is None:
        _default_chinglish_map = type_validate_json(
            WordMapType,
            (SOURCE_RES_DIR / CHINGLISH_FILENAME).read_text("u8"),
        )
    return _default_chinglish_map


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

    def get(self, token: str) -> Optional[SoundArrayType]:
        pass


class VoicePack:
    def __init__(self, base_path: Path) -> None:
        self.base_path = base_path
        self.token_manager = TokenManager(base_path)
        self.ysdd_token_manager = TokenManager(base_path, 0)

        self._chinglish_map: Optional[WordMapType] = None
        self._ysdd_tokens_map: Optional[WordMapType] = None

    @property
    def chinglish_map(self) -> WordMapType:
        if not (self.base_path / CHINGLISH_FILENAME).exists():
            return load_default_chinglish_map()
        if self._chinglish_map is None:
            self._chinglish_map = type_validate_json(
                WordMapType,
                (self.base_path / CHINGLISH_FILENAME).read_text("u8"),
            )
        return self._chinglish_map

    @property
    def ysdd_tokens_map(self) -> WordMapType:
        if not (self.base_path / YSDD_TOKENS_FILENAME).exists():
            return {}
        if self._ysdd_tokens_map is None:
            self._ysdd_tokens_map = type_validate_json(
                WordMapType,
                (self.base_path / YSDD_TOKENS_FILENAME).read_text("u8"),
            )
        return self._ysdd_tokens_map

    def get_token(self, token: str, is_ysdd: bool = False) -> Optional[SoundArrayType]:
        if is_ysdd:
            return self.ysdd_token_manager.get(token)
        return self.token_manager.get(token)
