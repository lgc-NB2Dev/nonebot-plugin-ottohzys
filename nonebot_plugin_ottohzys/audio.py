# Original by: https://github.com/CwavGuy/HUOZI_aolianfeiallin.top/blob/main/huoZiYinShua.py

from io import BytesIO
from pathlib import Path
from typing import cast

import anyio
import numpy as np
import soundfile as sf
from numpy.typing import NDArray

SoundArrayType = NDArray[np.float64]

TARGET_SAMPLE_RATE = 44100
"""目标采样率"""

SUPPORTED_EXTS = (".wav", ".mp3")


def find_sound_file(base_dir: Path, base_name: str):
    for ext in SUPPORTED_EXTS:
        file_path = base_dir / f"{base_name}{ext}"
        if file_path.exists():
            return file_path
    return None


def empty_sound_array(length: int) -> SoundArrayType:
    return np.zeros(int(length * TARGET_SAMPLE_RATE))


def normalize_audio(data: SoundArrayType):
    """标准化音频，统一音量"""
    rms = np.sqrt(np.mean(data**2))
    if rms == 0:
        return data
    return data / rms * 0.2


async def load_audio(file_path: Path, normalize: bool = True) -> SoundArrayType:
    """读取音频文件"""

    file = BytesIO(await anyio.Path(file_path).read_bytes())
    data, sample_rate = cast(tuple[SoundArrayType, int], sf.read(file))

    # 双声道转单声道
    if len(data.shape) == 2:
        # 左右声道相加除以2
        data = (data[:, 0] + data[:, 1]) / 2

    # 统一采样率
    if sample_rate != TARGET_SAMPLE_RATE:
        # 计算转换后的长度
        new_length = int((TARGET_SAMPLE_RATE / sample_rate) * len(data))
        # 转换
        data = np.interp(
            np.array(range(new_length)),
            np.linspace(0, new_length - 1, len(data)),
            data,
        )

    # 标准化
    if normalize:
        data = normalize_audio(data)

    return data
