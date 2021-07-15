import logging

from decimal import Decimal

from solana.rpc.api import Client
from solana.publickey import PublicKey

from ..market import Market as PySerumMarket

from .basket_token import BasketToken

from .mango_market import Market
from .mango_spot_market import SpotMarket

# # 🥭 MarketMetadata class
#


class MarketMetadata:
    def __init__(
        self,
        name: str,
        address: PublicKey,
        base: BasketToken,
        quote: BasketToken,
        spot: Market,
        oracle: PublicKey,
        decimals: Decimal,
    ):
        self.logger: logging.Logger = logging.getLogger(self.__class__.__name__)
        self.name: str = name
        self.address: PublicKey = address
        self.base: BasketToken = base
        self.quote: BasketToken = quote

        if not isinstance(spot, SpotMarket):
            raise Exception(f"Spot '{spot}' is not a spot market.")
        self.spot: SpotMarket = spot
        self.oracle: PublicKey = oracle
        self.decimals: Decimal = decimals
        self.symbol: str = f"{base.token.symbol}/{quote.token.symbol}"
        self._market = None

    def fetch_market(self, conn: Client) -> PySerumMarket:
        if self._market is None:
            self._market = PySerumMarket.load(conn, self.spot.address)

        return self._market

    def __str__(self) -> str:
        base = f"{self.base}".replace("\n", "\n    ")
        quote = f"{self.quote}".replace("\n", "\n    ")
        return f"""« MarketMetadata '{self.name}' [{self.address}/{self.spot.address}]:
    Base: {base}
    Quote: {quote}
    Oracle: {self.oracle} ({self.decimals} decimals)
»"""

    def __repr__(self) -> str:
        return f"{self}"
