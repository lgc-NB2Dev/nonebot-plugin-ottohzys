# Original by: https://github.com/CwavGuy/HUOZI_aolianfeiallin.top/blob/main/huoZiYinShua.py

import asyncio
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import List, Tuple, cast

import anyio
import numpy as np
import psola
import soundfile as sf
from async_lru import alru_cache
from nonebot import logger
from numpy.typing import NDArray
from pypinyin import lazy_pinyin

from .resource import TOKENS_DIR, YSDD_TOKENS_DIR, get_chinglish_map, get_ysdd_token_map

SoundArrayType = NDArray[np.float64]

TARGET_SAMPLE_RATE = 44100
"""目标采样率"""


def normalize_audio(data: SoundArrayType):
    """标准化音频，统一音量"""
    rms = np.sqrt(np.mean(data**2))
    if rms == 0:
        return data
    return data / rms * 0.2


@alru_cache()
async def load_audio(file_path: Path, normalize: bool = True) -> SoundArrayType:
    """读取音频文件"""

    file = BytesIO(await anyio.Path(file_path).read_bytes())
    data, sample_rate = cast(Tuple[SoundArrayType, int], sf.read(file))

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


@alru_cache()
async def get_pinyin_audio(
    pinyin: str,
    is_ysdd: bool = False,
    normalize: bool = True,
    empty_length: float = 0.25,
) -> SoundArrayType:
    if pinyin != "_":
        file_dir = YSDD_TOKENS_DIR if is_ysdd else TOKENS_DIR
        suffix = ".mp3" if is_ysdd else ".wav"
        file_name = f"{pinyin}{suffix}"
        try:
            return await load_audio(file_dir / file_name, normalize)
        except FileNotFoundError:
            logger.warning(f"Audio {file_name} not found in {file_dir}")

    return np.zeros(int(empty_length * TARGET_SAMPLE_RATE))


def modify_pitch_and_speed(
    data: SoundArrayType,
    pitch_multiple: float,
    speed_multiple: float,
) -> SoundArrayType:
    """改变音高和速度"""

    if pitch_multiple == 1 and speed_multiple == 1:
        # 没有改动的必要，直接返回
        return data

    # 第一次拉伸
    original_len = len(data)
    if speed_multiple / pitch_multiple != 1:
        # 不改变音高的同时在时间上拉伸（PSOLA）
        # constant_stretch 过小会导致 bug，因此分两次拉伸
        data = psola.vocode(
            data,
            TARGET_SAMPLE_RATE,
            constant_stretch=1 / pitch_multiple,
        )
        data = psola.vocode(data, TARGET_SAMPLE_RATE, constant_stretch=speed_multiple)

    # 第二次拉伸，以改变音高的方式拉伸回来
    new_length = int(original_len / speed_multiple)
    return np.interp(
        np.array(range(new_length)),
        np.linspace(0, new_length - 1, len(data)),
        data,
    )


@dataclass
class PreProcPron:
    pron: str
    is_pinyin: bool = False
    is_ysdd: bool = False


async def parse_sentence(sentence: str, ysdd_mode: bool = True) -> List[PreProcPron]:
    pre_proc_pron: List[PreProcPron] = []
    pre_proc_pron.append(PreProcPron(sentence))

    def replace_pron(kw: str, *replace_to: PreProcPron) -> List[PreProcPron]:
        tmp: List[PreProcPron] = []

        for pron in pre_proc_pron:
            if (kw not in pron.pron) or pron.is_pinyin or pron.is_ysdd:
                tmp.append(pron)
            else:
                splitted = [
                    ([*replace_to, PreProcPron(s)] if n else [PreProcPron(s)])
                    for n, s in (enumerate(pron.pron.split(kw)))
                ]
                flattened = [y for x in splitted for y in x if y.pron]
                tmp.extend(flattened)

        return tmp

    # 替换原声大碟
    if ysdd_mode:
        ysdd_token_map = get_ysdd_token_map()
        for token, sentences in ysdd_token_map.items():
            for s in sentences:
                pre_proc_pron = replace_pron(s, PreProcPron(token, is_ysdd=True))

    # 替换字母
    chinglish_map = get_chinglish_map()
    for ch, pron in chinglish_map.items():
        pre_proc_pron = replace_pron(
            ch,
            *(PreProcPron(pron, is_pinyin=True) for pron in pron.split()),
        )

    # 拼音化
    ret = []
    for pron in pre_proc_pron:
        if pron.is_ysdd or pron.is_pinyin:
            ret.append(pron)
            continue

        for p in lazy_pinyin(pron.pron):
            if p.isalpha():
                ret.append(PreProcPron(p, is_pinyin=True))
            else:
                ret.extend(PreProcPron("_", is_pinyin=True) for _ in p)

    return ret


async def generate_data(
    sentence: str,
    reverse: bool = False,
    ysdd_mode: bool = True,
    normalize: bool = True,
    speed_multiple: float = 1,
    pitch_multiple: float = 1,
    pause_length: float = 0.25,
) -> SoundArrayType:
    """活字印刷"""

    sentence = sentence.lower()
    tokens_list = await parse_sentence(sentence, ysdd_mode)

    audios: List[SoundArrayType] = await asyncio.gather(
        *(
            get_pinyin_audio(token.pron, token.is_ysdd, normalize, pause_length)
            for token in tokens_list
        ),
    )
    processed_au: SoundArrayType = np.concatenate((np.array([]), *audios))

    # 音高偏移
    processed_au = modify_pitch_and_speed(processed_au, pitch_multiple, speed_multiple)

    # 倒放
    if reverse:
        processed_au = np.flip(processed_au)

    return processed_au


def save_to_bytes_io(data: SoundArrayType) -> BytesIO:
    file = BytesIO()
    sf.write(file, data, TARGET_SAMPLE_RATE, format="wav", subtype="PCM_16")
    return file


async def generate(
    sentence: str,
    reverse: bool = False,
    ysdd_mode: bool = True,
    normalize: bool = True,
    speed_multiple: float = 1,
    pitch_multiple: float = 1,
    pause_length: float = 0.25,
) -> BytesIO:
    data = await generate_data(
        sentence,
        reverse,
        ysdd_mode,
        normalize,
        speed_multiple,
        pitch_multiple,
        pause_length,
    )
    return save_to_bytes_io(data)
