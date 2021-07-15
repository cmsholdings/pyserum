import logging
import typing
from decimal import Decimal

from solana.publickey import PublicKey
from solana.rpc.api import Client
from solana.rpc.commitment import Commitment
from solana.rpc.types import TokenAccountOpts

from .token import Token

# # 🥭 TokenValue class
#
# The `TokenValue` class is a simple way of keeping a token and value together, and
# displaying them nicely consistently.
#


class TokenValue:
    def __init__(self, token: Token, value: Decimal):
        self.logger: logging.Logger = logging.getLogger(self.__class__.__name__)
        self.token = token
        self.value = value

    @staticmethod
    def fetch_total_value_or_none(
        conn: Client, commitment: Commitment, account_public_key: PublicKey, token: Token
    ) -> typing.Optional["TokenValue"]:
        opts = TokenAccountOpts(mint=token.mint)

        token_accounts_response = conn.get_token_accounts_by_owner(account_public_key, opts, commitment=commitment)
        token_accounts = token_accounts_response["result"]["value"]
        if len(token_accounts) == 0:
            return None

        total_value = Decimal(0)
        for token_account in token_accounts:
            result = conn.get_token_account_balance(token_account["pubkey"], commitment=commitment)
            value = Decimal(result["result"]["value"]["amount"])
            decimal_places = result["result"]["value"]["decimals"]
            divisor = Decimal(10 ** decimal_places)
            total_value += value / divisor

        return TokenValue(token, total_value)

    @staticmethod
    def fetch_total_value(
        conn: Client, commitment: Commitment, account_public_key: PublicKey, token: Token
    ) -> "TokenValue":
        value = TokenValue.fetch_total_value_or_none(
            conn=conn, commitment=commitment, account_public_key=account_public_key, token=token
        )
        if value is None:
            return TokenValue(token, Decimal(0))
        return value

    @staticmethod
    def report(values: typing.List["TokenValue"], reporter: typing.Callable[[str], None] = print) -> None:
        for value in values:
            reporter(f"{value.value:>18,.8f} {value.token.name}")

    @staticmethod
    def find_by_symbol(values: typing.List["TokenValue"], symbol: str) -> "TokenValue":
        found = [value for value in values if value.token.symbol_matches(symbol)]
        if len(found) == 0:
            raise Exception(f"Token '{symbol}' not found in token values: {values}")

        if len(found) > 1:
            raise Exception(f"Token '{symbol}' matched multiple tokens in values: {values}")

        return found[0]

    @staticmethod
    def find_by_mint(values: typing.List["TokenValue"], mint: PublicKey) -> "TokenValue":
        found = [value for value in values if value.token.mint == mint]
        if len(found) == 0:
            raise Exception(f"Token '{mint}' not found in token values: {values}")

        if len(found) > 1:
            raise Exception(f"Token '{mint}' matched multiple tokens in values: {values}")

        return found[0]

    @staticmethod
    def find_by_token(values: typing.List["TokenValue"], token: Token) -> "TokenValue":
        return TokenValue.find_by_mint(values, token.mint)

    @staticmethod
    def changes(before: typing.List["TokenValue"], after: typing.List["TokenValue"]) -> typing.List["TokenValue"]:
        changes: typing.List[TokenValue] = []
        for before_balance in before:
            after_balance = TokenValue.find_by_token(after, before_balance.token)
            result = TokenValue(before_balance.token, after_balance.value - before_balance.value)
            changes += [result]

        return changes

    def __str__(self) -> str:
        return f"« TokenValue: {self.value:>18,.8f} {self.token.name} »"

    def __repr__(self) -> str:
        return f"{self}"
