import base64
import typing

import base58
from solana.publickey import PublicKey
from solana.rpc.api import Client
from spl.token.constants import WRAPPED_SOL_MINT  # type: ignore # TODO: Remove ignore.

from pyserum._layouts.market import MINT_LAYOUT


def decode_binary(encoded: typing.List) -> bytes:
    if isinstance(encoded, str):
        return base58.b58decode(encoded)
    if encoded[1] == "base64":
        return base64.b64decode(encoded[0])
    return base58.b58decode(encoded[0])


def encode_binary(decoded: bytes) -> typing.List:
    return [base64.b64encode(decoded), "base64"]


def load_bytes_data(conn: Client, addr: PublicKey):
    res = conn.get_account_info(addr)
    if ("result" not in res) or ("value" not in res["result"]) or ("data" not in res["result"]["value"]):
        raise Exception("Cannot load byte data.")
    data = res["result"]["value"]["data"][0]
    return base64.decodebytes(data.encode("ascii"))


def get_mint_decimals(conn: Client, mint_pub_key: PublicKey) -> int:
    """Get the mint decimals for a token mint"""
    if mint_pub_key == WRAPPED_SOL_MINT:
        return 9

    bytes_data = load_bytes_data(conn, mint_pub_key)
    return MINT_LAYOUT.parse(bytes_data).decimals
