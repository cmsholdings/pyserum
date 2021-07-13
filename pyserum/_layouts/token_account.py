from construct import Bytes, Int64ul, Padding  # type: ignore
from construct import Struct as cStruct  # type: ignore


TOKEN_ACCOUNT = cStruct(
    "mint" / Bytes(32),
    "owner" / Bytes(32),
    "amount" / Int64ul,
    "padding" / Padding(93),
)
