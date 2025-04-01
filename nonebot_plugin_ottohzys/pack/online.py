import shutil
import tempfile
import zipfile
from pathlib import Path

from cookit.pyd import type_validate_json
from httpx import AsyncClient
from pydantic import BaseModel

from ..config import config
from .pack import CONFIG_FILENAME

PACK_EXT = ".zip"


class OnlinePackInfo(BaseModel):
    name: str
    description: str


async def download_pack(pack_name: str, target_dir: Path):
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        temp_pack_path = temp_path / pack_name

        async with AsyncClient(base_url=config.pack_download_base_url, proxy=config.proxy, follow_redirects=True) as cli, cli.stream("GET", f"{pack_name}{PACK_EXT}") as resp:  # fmt: skip
            resp.raise_for_status()
            zip_path = temp_path / f"{pack_name}{PACK_EXT}"
            with zip_path.open("wb") as f:
                async for chunk in resp.aiter_bytes():
                    f.write(chunk)

        with zipfile.ZipFile(zip_path, "r") as z:
            z.extractall(temp_pack_path)

        if (cfg := (target_dir / CONFIG_FILENAME)).exists():
            shutil.copy(cfg, temp_pack_path)

        if target_dir.exists():
            shutil.rmtree(target_dir)

        shutil.move(temp_pack_path, target_dir)


async def get_online_packs():
    async with AsyncClient(proxy=config.proxy, follow_redirects=True) as cli:
        resp = await cli.get(config.pack_list_url)
        resp.raise_for_status()
        return type_validate_json(list[OnlinePackInfo], resp.content)
