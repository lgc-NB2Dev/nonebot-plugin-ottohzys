import asyncio as aio
import json
import zipfile
from pathlib import Path
from typing import Any, Awaitable, Dict, List, Optional
from zipfile import ZipFile

import anyio
from httpx import AsyncClient
from nonebot import get_driver, logger

RESOURCE_DIR = Path.cwd() / "data" / "ottohzys"
if not RESOURCE_DIR.exists():
    RESOURCE_DIR.mkdir(parents=True)

TOKENS_DIR = RESOURCE_DIR / "tokens"
YSDD_TOKENS_DIR = RESOURCE_DIR / "ysddTokens"
YSDD_TOKEN_MAP_PATH = RESOURCE_DIR / "ysdd.json"

BUILTIN_RES_DIR = Path(__file__).parent / "res"
CHINGLISH_MAP_PATH = BUILTIN_RES_DIR / "chinglish.json"

RESOURCE_REPO_URL = "https://mirror.ghproxy.com/https://github.com/HanaYabuki/otto-hzys/archive/refs/heads/master.zip"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"


async def create_extract_tasks(
    file: ZipFile,
    zip_path: Optional[zipfile.Path] = None,
) -> List[Awaitable[Any]]:
    if not zip_path:
        zip_path = zipfile.Path(file)

    tasks_ready: List[Awaitable[Any]] = []

    async def inner(zf: ZipFile, zp: zipfile.Path, real_path: anyio.Path):
        for p in zp.iterdir():
            now_real_path = real_path / p.name
            if p.is_dir():
                await now_real_path.mkdir(parents=True, exist_ok=True)
                await inner(zf, p, now_real_path)
            else:
                task = aio.create_task(now_real_path.write_bytes(p.read_bytes()))
                tasks_ready.append(task)

    await inner(file, zip_path, anyio.Path(RESOURCE_DIR))
    return tasks_ready


async def download_resource():
    cache_path = anyio.Path(RESOURCE_DIR) / "cache.zip"
    if await cache_path.exists():
        await cache_path.unlink()

    async with await cache_path.open("wb") as df:
        async with AsyncClient() as cli:
            async with cli.stream(
                "GET",
                RESOURCE_REPO_URL,
                headers={"User-Agent": USER_AGENT},
                follow_redirects=True,
            ) as resp:
                resp.raise_for_status()
                async for chunk in resp.aiter_bytes():
                    await df.write(chunk)

    with ZipFile(cache_path) as f:
        tasks = await create_extract_tasks(
            f,
            zipfile.Path(f) / "otto-hzys-master" / "public" / "static",
        )
        await aio.gather(*tasks)

    await cache_path.unlink()


def check_resource_sync():
    return all(p.exists() for p in (TOKENS_DIR, YSDD_TOKENS_DIR, YSDD_TOKEN_MAP_PATH))


async def check_and_download():
    if check_resource_sync():
        return

    logger.info("Resource not found, trying to download, please wait...")
    try:
        await download_resource()
    except Exception:
        logger.error("Failed to download resources, please download manually")
        raise

    if not check_resource_sync():
        raise RuntimeError("Failed to download resources, please download manually")

    logger.success("Successfully downloaded resources")


def get_chinglish_map() -> Dict[str, str]:
    return json.loads(CHINGLISH_MAP_PATH.read_text(encoding="u8"))


def get_ysdd_token_map() -> Dict[str, List[str]]:
    return json.loads(YSDD_TOKEN_MAP_PATH.read_text(encoding="u8"))


driver = get_driver()


@driver.on_startup
async def _():
    await check_and_download()
