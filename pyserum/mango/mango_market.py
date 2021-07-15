import abc
import logging
import typing

from solana.publickey import PublicKey

from .token import Token

# # 🥭 Market class
#
# This class describes a crypto market. It *must* have a base token and a quote token.
#


class Market(metaclass=abc.ABCMeta):
    def __init__(self, base: Token, quote: Token):
        self.logger: logging.Logger = logging.getLogger(self.__class__.__name__)
        self.base: Token = base
        self.quote: Token = quote

    @property
    def symbol(self) -> str:
        return f"{self.base.symbol}/{self.quote.symbol}"

    def __str__(self) -> str:
        return f"« Market {self.symbol} »"

    def __repr__(self) -> str:
        return f"{self}"


class MarketLookup(metaclass=abc.ABCMeta):
    def __init__(self) -> None:
        self.logger: logging.Logger = logging.getLogger(self.__class__.__name__)

    @abc.abstractmethod
    def find_by_symbol(self, symbol: str) -> typing.Optional[Market]:
        raise NotImplementedError("MarketLookup.find_by_symbol() is not implemented on the base type.")

    @abc.abstractmethod
    def find_by_address(self, address: PublicKey) -> typing.Optional[Market]:
        raise NotImplementedError("MarketLookup.find_by_address() is not implemented on the base type.")

    @abc.abstractmethod
    def all_markets(self) -> typing.Sequence[Market]:
        raise NotImplementedError("MarketLookup.all_markets() is not implemented on the base type.")


class CompoundMarketLookup(MarketLookup):
    def __init__(self, lookups: typing.Sequence[MarketLookup]) -> None:
        super().__init__()
        self.lookups: typing.Sequence[MarketLookup] = lookups

    def find_by_symbol(self, symbol: str) -> typing.Optional[Market]:
        for lookup in self.lookups:
            result = lookup.find_by_symbol(symbol)
            if result is not None:
                return result
        return None

    def find_by_address(self, address: PublicKey) -> typing.Optional[Market]:
        for lookup in self.lookups:
            result = lookup.find_by_address(address)
            if result is not None:
                return result
        return None

    def all_markets(self) -> typing.Sequence[Market]:
        return [market for sublist in map(lambda lookup: lookup.all_markets(), self.lookups) for market in sublist]
