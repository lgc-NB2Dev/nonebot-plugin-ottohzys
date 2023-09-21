# Original by: https://github.com/CwavGuy/HUOZI_aolianfeiallin.top/blob/main/huoZiYinShua.py

from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import Dict, List, Tuple, cast

import anyio
import numpy as np
import psola
import soundfile as sf
from nonebot import logger
from numpy.typing import NDArray
from pypinyin import lazy_pinyin

from .resource import CHINGLISH_MAP, TOKENS_DIR, YSDD_TOKEN_MAP, YSDD_TOKENS_DIR

SoundArrayType = NDArray[np.float64]

TARGET_SAMPLE_RATE = 44100
"""目标采样率"""

audio_cache: Dict[str, SoundArrayType] = {}
ysdd_audio_cache: Dict[str, SoundArrayType] = {}


def normalize_audio(data: SoundArrayType):
    """标准化音频，统一音量"""
    rms = np.sqrt(np.mean(data**2))
    if rms == 0:
        return data
    return data / rms * 0.2


async def load_audio(file_path: Path):
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
    return normalize_audio(data)


async def get_pinyin_audio(
    pinyin: str,
    is_ysdd: bool = False,
    empty_length: float = 0.25,
) -> SoundArrayType:
    cache_dict = ysdd_audio_cache if is_ysdd else audio_cache
    file_dir = YSDD_TOKENS_DIR if is_ysdd else TOKENS_DIR

    if pinyin in cache_dict:
        return cache_dict[pinyin]

    suffix = ".mp3" if is_ysdd else ".wav"
    file_name = f"{pinyin}{suffix}"
    try:
        audio = await load_audio(file_dir / file_name)
    except FileNotFoundError:
        logger.warning(f"Audio {file_name} not found in {file_dir}")
        return np.zeros(int(empty_length * TARGET_SAMPLE_RATE))

    cache_dict[pinyin] = audio
    return audio


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
    if speed_multiple / pitch_multiple != 1:
        # 不改变音高的同时在时间上拉伸（PSOLA）
        # constant_stretch过小会导致bug，因此分两次拉伸
        data = psola.vocode(
            data,
            TARGET_SAMPLE_RATE,
            constant_stretch=1 / pitch_multiple,
        )
        data = psola.vocode(
            data,
            TARGET_SAMPLE_RATE,
            constant_stretch=speed_multiple,
        )

    # 第二次拉伸，以改变音高的方式拉伸回来
    new_length = int(len(data) / speed_multiple)
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
        for token, sentences in YSDD_TOKEN_MAP.items():
            for s in sentences:
                pre_proc_pron = replace_pron(s, PreProcPron(token, is_ysdd=True))

    # 替换字母
    for ch, pron in CHINGLISH_MAP.items():
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
    ysdd_mode: bool = True,
    pitch_multiple: float = 1,
    speed_multiple: float = 1,
    reverse: bool = False,
    pause_length: float = 0.25,
) -> SoundArrayType:
    """活字印刷"""

    sentence = sentence.lower()
    tokens_list = await parse_sentence(sentence, ysdd_mode)

    processed_au: SoundArrayType = np.array([])
    for token in tokens_list:
        audio = await get_pinyin_audio(token.pron, token.is_ysdd, pause_length)
        processed_au = np.concatenate((processed_au, audio))

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
    raw_data: str,
    ysdd_mode: bool = True,
    pitch_multiple: float = 1,
    speed_multiple: float = 1,
    reverse: bool = False,
    pause_length: float = 0.25,
) -> BytesIO:
    data = await generate_data(
        raw_data,
        ysdd_mode,
        pitch_multiple,
        speed_multiple,
        reverse,
        pause_length,
    )
    return save_to_bytes_io(data)
