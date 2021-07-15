import json
import logging
import os
import typing
from decimal import Decimal

import requests
from solana.publickey import PublicKey

from .constants import DEFAULT_TOKEN_URL, SOL_DECIMALS, SOL_MINT_ADDRESS

# # 🥭 Token class
#
# `Token` defines aspects common to every token.
#


class Token:
    def __init__(self, symbol: str, name: str, mint: PublicKey, decimals: Decimal):
        self.logger: logging.Logger = logging.getLogger(self.__class__.__name__)
        self.symbol: str = symbol.upper()
        self.name: str = name
        self.mint: PublicKey = mint
        self.decimals: Decimal = decimals

    def round(self, value: Decimal) -> Decimal:
        return round(value, int(self.decimals))

    def shift_to_decimals(self, value: Decimal) -> Decimal:
        divisor = Decimal(10 ** self.decimals)
        shifted = value / divisor
        return round(shifted, int(self.decimals))

    def shift_to_native(self, value: Decimal) -> Decimal:
        divisor = Decimal(10 ** self.decimals)
        shifted = value * divisor
        return round(shifted, 0)

    def symbol_matches(self, symbol: str) -> bool:
        return self.symbol.upper() == symbol.upper()

    @staticmethod
    def find_by_symbol(values: typing.List["Token"], symbol: str) -> "Token":
        found = [value for value in values if value.symbol_matches(symbol)]
        if len(found) == 0:
            raise Exception(f"Token '{symbol}' not found in token values: {values}")

        if len(found) > 1:
            raise Exception(f"Token '{symbol}' matched multiple tokens in values: {values}")

        return found[0]

    @staticmethod
    def find_by_mint(values: typing.List["Token"], mint: PublicKey) -> "Token":
        found = [value for value in values if value.mint == mint]
        if len(found) == 0:
            raise Exception(f"Token '{mint}' not found in token values: {values}")

        if len(found) > 1:
            raise Exception(f"Token '{mint}' matched multiple tokens in values: {values}")

        return found[0]

    # TokenMetadatas are equal if they have the same mint address.
    def __eq__(self, other):
        if hasattr(other, "mint"):
            return self.mint == other.mint
        return False

    def __str__(self) -> str:
        return f"« Token '{self.name}' [{self.mint} ({self.decimals} decimals)] »"

    def __repr__(self) -> str:
        return f"{self}"


# # 🥭 SolToken object
#
# It's sometimes handy to have a `Token` for SOL,
# but SOL isn't actually a token and can't appear in baskets.
# This object defines a special case for SOL.
#


SolToken = Token("SOL", "Pure SOL", SOL_MINT_ADDRESS, SOL_DECIMALS)


# # 🥭 TokenLookup class
#
# This class allows us to look up token symbols, names, mint addresses and decimals, all from Solana data.
# by default, the json is downloaded from the DEFAULT_TOKEN_URL and saved for subsequent runs
#


class TokenLookup:
    @staticmethod
    def _find_data_by_symbol(symbol: str, token_data: typing.Dict) -> typing.Optional[typing.Dict]:
        for token in token_data["tokens"]:
            if token["symbol"] == symbol:
                return token
        return None

    def __init__(self, token_data: typing.Dict) -> None:
        self.logger: logging.Logger = logging.getLogger(self.__class__.__name__)
        self.token_data = token_data

    def find_by_symbol(self, symbol: str) -> typing.Optional[Token]:
        found = TokenLookup._find_data_by_symbol(symbol, self.token_data)
        if found is not None:
            return Token(found["symbol"], found["name"], PublicKey(found["address"]), Decimal(found["decimals"]))

        return None

    def find_by_mint(self, mint: PublicKey) -> typing.Optional[Token]:
        mint_string: str = str(mint)
        for token in self.token_data["tokens"]:
            if token["address"] == mint_string:
                return Token(token["symbol"], token["name"], PublicKey(token["address"]), Decimal(token["decimals"]))

        return None

    def find_by_symbol_or_raise(self, symbol: str) -> Token:
        token = self.find_by_symbol(symbol)
        if token is None:
            raise Exception(f"Could not find token with symbol '{symbol}'.")

        return token

    def find_by_mint_or_raise(self, mint: PublicKey) -> Token:
        token = self.find_by_mint(mint)
        if token is None:
            raise Exception(f"Could not find token with mint {mint}.")

        return token

    @staticmethod
    def load(filename: str, get_if_not_exists=True) -> "TokenLookup":
        if not os.path.exists(filename) or os.path.getsize(filename) == 0:
            if get_if_not_exists:
                response = json.loads(requests.get(DEFAULT_TOKEN_URL).text)
                with open(filename, "w") as file_handle:
                    json.dump(response, file_handle)
            else:
                raise FileNotFoundError
        with open(filename) as json_file:
            token_data = json.load(json_file)
            return TokenLookup(token_data)
