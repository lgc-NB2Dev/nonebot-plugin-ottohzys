# Original by: https://github.com/CwavGuy/HUOZI_aolianfeiallin.top/blob/main/huoZiYinShua.py

from dataclasses import dataclass
from typing import Optional

import numpy as np
from pypinyin import lazy_pinyin

from .audio import SoundArrayType, empty_sound_array, modify_pitch_and_speed
from .pack import VoicePack


@dataclass
class PreProcPron:
    pron: Optional[str]
    is_pinyin: bool = False
    is_ysdd: bool = False


def parse_sentence(
    pack: VoicePack,
    sentence: str,
    ysdd_mode: bool = True,
) -> list[PreProcPron]:
    pre_proc_pron: list[PreProcPron] = []
    pre_proc_pron.append(PreProcPron(sentence))

    def replace_pron(kw: str, *replace_to: PreProcPron) -> list[PreProcPron]:
        tmp: list[PreProcPron] = []

        for pron in pre_proc_pron:
            if (
                (not pron.pron)
                or (kw not in pron.pron)
                or pron.is_pinyin
                or pron.is_ysdd
            ):
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
        ysdd_token_map = pack.ysdd_tokens_map
        for token, sentences in ysdd_token_map.items():
            for s in sentences:
                pre_proc_pron = replace_pron(s, PreProcPron(token, is_ysdd=True))

    # 替换字母
    chinglish_map = pack.chinglish_map
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

        none_pron = PreProcPron(None)
        if pron.pron:
            for p in lazy_pinyin(pron.pron):
                if p.isalpha():
                    ret.append(PreProcPron(p, is_pinyin=True))
                else:
                    ret.extend(none_pron for _ in p)
        else:
            ret.append(none_pron)

    return ret


def generate_data(
    pack: VoicePack,
    sentence: str,
    reverse: bool = False,
    ysdd_mode: bool = True,
    normalize: bool = True,
    speed_multiple: float = 1,
    pitch_multiple: float = 1,
    pause_length: float = 0.25,
) -> SoundArrayType:
    sentence = sentence.lower()
    tokens_list = parse_sentence(pack, sentence, ysdd_mode)

    empty_arr: Optional[SoundArrayType] = None

    def get_token_audio(token: PreProcPron) -> SoundArrayType:
        nonlocal empty_arr
        if token.pron and (
            (audio := pack.get_token(token.pron, token.is_ysdd, normalize)) is not None
        ):
            return audio
        if empty_arr is None:
            empty_arr = empty_sound_array(pause_length)
        return empty_arr

    audios: list[SoundArrayType] = [get_token_audio(token) for token in tokens_list]
    processed_au: SoundArrayType = np.concatenate((np.array([]), *audios))

    # 音高偏移
    processed_au = modify_pitch_and_speed(processed_au, pitch_multiple, speed_multiple)

    # 倒放
    if reverse:
        processed_au = np.flip(processed_au)

    return processed_au
