import datetime
import logging
from decimal import Decimal

from .._layouts.mango_index import INDEX
from ..enums import Version
from .token import Token
from .token_value import TokenValue

# # 🥭 Index class
#


class Index:
    def __init__(
        self, version: Version, token: Token, last_update: datetime.datetime, borrow: TokenValue, deposit: TokenValue
    ):
        self.logger: logging.Logger = logging.getLogger(self.__class__.__name__)
        self.version: Version = version
        self.token: Token = token
        self.last_update: datetime.datetime = last_update
        self.borrow: TokenValue = borrow
        self.deposit: TokenValue = deposit

    @staticmethod
    def from_layout(layout: INDEX, token: Token) -> "Index":
        borrow = TokenValue(token, layout.borrow / Decimal(10 ** token.decimals))
        deposit = TokenValue(token, layout.deposit / Decimal(10 ** token.decimals))
        return Index(Version.UNSPECIFIED, token, layout.last_update, borrow, deposit)

    def __str__(self) -> str:
        return f"""« Index [{self.token.symbol}] ({self.last_update}):
    Borrow: {self.borrow},
    Deposit: {self.deposit} »"""

    def __repr__(self) -> str:
        return f"{self}"
