from typing import Union, Literal

LikeType = Union[Literal[-1], Literal[1]]

def is_valid_like_type(like_type: str) -> bool:
    return like_type == "-1" or like_type == "1"