import json
import zipfile
from pathlib import Path
from typing import Dict, List, Optional
from zipfile import ZipFile

import httpx
from nonebot import logger

RESOURCE_DIR = Path.cwd() / "data" / "ottohzys"
if not RESOURCE_DIR.exists():
    RESOURCE_DIR.mkdir(parents=True)

TOKENS_DIR = RESOURCE_DIR / "tokens"
YSDD_TOKENS_DIR = RESOURCE_DIR / "ysddTokens"
YSDD_TOKEN_MAP_PATH = RESOURCE_DIR / "ysdd.json"

BUILTIN_RES_DIR = Path(__file__).parent / "res"
CHINGLISH_MAP_PATH = BUILTIN_RES_DIR / "chinglish.json"

RESOURCE_REPO_URL = "https://ghproxy.com/https://github.com/HanaYabuki/otto-hzys/archive/refs/heads/master.zip"


def download_resource_sync():
    cache_path = RESOURCE_DIR / "cache.zip"
    if cache_path.exists():
        cache_path.unlink()

    with cache_path.open("wb") as df:
        with httpx.stream("GET", RESOURCE_REPO_URL, follow_redirects=True) as response:
            for chunk in response.iter_bytes():
                df.write(chunk)

    def extract(
        zf: ZipFile,
        zp: Optional[zipfile.Path] = None,
        paths: Optional[List[str]] = None,
    ):
        if not zp:
            zp = zipfile.Path(zf)

        if not paths:
            paths = []
        else:
            zp = zp.joinpath(*paths)

        for p in zp.iterdir():
            real_path = RESOURCE_DIR.joinpath(*paths, p.name)
            if p.is_dir():
                real_path.mkdir(parents=True, exist_ok=True)
                extract(zf, zp, [*paths, p.name])
            else:
                real_path.write_bytes(p.read_bytes())

    with ZipFile(cache_path) as f:
        extract(f, zipfile.Path(f) / "otto-hzys-master" / "public" / "static")

    cache_path.unlink()


def check_resource_sync():
    return all(p.exists() for p in (TOKENS_DIR, YSDD_TOKENS_DIR, YSDD_TOKEN_MAP_PATH))


def check_and_download():
    if check_resource_sync():
        return

    logger.info("Resource not found, trying to download, please wait...")
    try:
        download_resource_sync()
    except Exception:
        logger.error("Failed to download resources, please download manually")
        raise

    if not check_resource_sync():
        raise RuntimeError("Failed to download resources, please download manually")

    logger.success("Successfully downloaded resources")


check_and_download()


CHINGLISH_MAP: Dict[str, str] = json.loads(
    CHINGLISH_MAP_PATH.read_text(encoding="u8"),
)
YSDD_TOKEN_MAP: Dict[str, List[str]] = json.loads(
    YSDD_TOKEN_MAP_PATH.read_text(encoding="u8"),
)
