import json
import typing

from decimal import Decimal
from solana.publickey import PublicKey

from .mango_market import Market, MarketLookup
from .token import Token


# # 🥭 SpotMarket class
#
# This class encapsulates our knowledge of a Serum spot market.
#


class SpotMarket(Market):
    def __init__(self, base: Token, quote: Token, address: PublicKey):
        super().__init__(base, quote)
        self.address: PublicKey = address

    def __str__(self) -> str:
        return f"« SpotMarket {self.symbol}: {self.address} »"

    def __repr__(self) -> str:
        return f"{self}"


# # 🥭 SpotMarketLookup class
#
# This class allows us to look up Serum market addresses and tokens, all from our Solana
# static data.
#
# The static data is the [Solana token list]
# (https://raw.githubusercontent.com/solana-labs/token-list/main/src/tokens/solana.tokenlist.json) provided by Serum.
#
# You can load a `SpotMarketLookup` class by something like:
# ```
# with open("solana.tokenlist.json") as json_file:
#     token_data = json.load(json_file)
#     spot_market_lookup = SpotMarketLookup(token_data)
# ```
# This uses the same data file as `TokenLookup` but it looks a lot more complicated. The
# main reason for this is that tokens are described in a list, whereas markets are optional
# child attributes of tokens.
#
# To find a token, we can just go through the list.
#
# To find a market, we need to split the market symbol into the two token symbols, go through
# the list, check if the item has the optional `extensions` attribute, and in there see if
# there is a name-value pair for the particular market we're interested in. Also, the
# current file only lists USDC and USDT markets, so that's all we can support this way.


class SpotMarketLookup(MarketLookup):
    def __init__(self, token_data: typing.Dict) -> None:
        super().__init__()
        self.token_data: typing.Dict = token_data

    @staticmethod
    def load(token_data_filename: str) -> "SpotMarketLookup":
        with open(token_data_filename) as json_file:
            token_data = json.load(json_file)
            return SpotMarketLookup(token_data)

    @staticmethod
    def _find_data_by_symbol(symbol: str, token_data: typing.Dict) -> typing.Optional[typing.Dict]:
        for token in token_data["tokens"]:
            if token["symbol"] == symbol:
                return token
        return None

    @staticmethod
    def _find_token_by_symbol_or_error(symbol: str, token_data: typing.Dict) -> Token:
        found_token_data = SpotMarketLookup._find_data_by_symbol(symbol, token_data)
        if found_token_data is None:
            raise Exception(f"Could not find data for token symbol '{symbol}'.")

        return Token(symbol, found_token_data["name"], PublicKey(found_token_data["address"]), Decimal(found_token_data["decimals"]))

    def find_by_symbol(self, symbol: str) -> typing.Optional[Market]:
        base_symbol, quote_symbol = symbol.split("/")
        base_data = SpotMarketLookup._find_data_by_symbol(base_symbol, self.token_data)
        if base_data is None:
            self.logger.warning(f"Could not find data for base token '{base_symbol}'")
            return None
        base = Token(base_data["symbol"], base_data["name"], PublicKey(
            base_data["address"]), Decimal(base_data["decimals"]))

        quote_data = SpotMarketLookup._find_data_by_symbol(quote_symbol, self.token_data)
        if quote_data is None:
            self.logger.warning(f"Could not find data for quote token '{quote_symbol}'")
            return None
        quote = Token(quote_data["symbol"], quote_data["name"], PublicKey(
            quote_data["address"]), Decimal(quote_data["decimals"]))

        if "extensions" not in base_data:
            self.logger.warning(f"No markets found for base token '{base.symbol}'.")
            return None

        if quote.symbol == "USDC":
            if "serumV3Usdc" not in base_data["extensions"]:
                self.logger.warning(f"No USDC market found for base token '{base.symbol}'.")
                return None

            market_address_string = base_data["extensions"]["serumV3Usdc"]
            market_address = PublicKey(market_address_string)
        elif quote.symbol == "USDT":
            if "serumV3Usdt" not in base_data["extensions"]:
                self.logger.warning(f"No USDT market found for base token '{base.symbol}'.")
                return None

            market_address_string = base_data["extensions"]["serumV3Usdt"]
            market_address = PublicKey(market_address_string)
        else:
            self.logger.warning(
                f"Could not find market with quote token '{quote.symbol}'. Only markets based on USDC or USDT are supported.")
            return None

        return SpotMarket(base, quote, market_address)

    def find_by_address(self, address: PublicKey) -> typing.Optional[Market]:
        address_string: str = str(address)
        for token_data in self.token_data["tokens"]:
            if "extensions" in token_data:
                if "serumV3Usdc" in token_data["extensions"]:
                    if token_data["extensions"]["serumV3Usdc"] == address_string:
                        market_address_string = token_data["extensions"]["serumV3Usdc"]
                        market_address = PublicKey(market_address_string)
                        base = Token(token_data["symbol"], token_data["name"], PublicKey(
                            token_data["address"]), Decimal(token_data["decimals"]))
                        quote_data = SpotMarketLookup._find_data_by_symbol("USDC", self.token_data)
                        if quote_data is None:
                            raise Exception("Could not load token data for USDC (which should always be present).")
                        quote = Token(quote_data["symbol"], quote_data["name"], PublicKey(
                            quote_data["address"]), Decimal(quote_data["decimals"]))
                        return SpotMarket(base, quote, market_address)
                if "serumV3Usdt" in token_data["extensions"]:
                    if token_data["extensions"]["serumV3Usdt"] == address_string:
                        market_address_string = token_data["extensions"]["serumV3Usdt"]
                        market_address = PublicKey(market_address_string)
                        base = Token(token_data["symbol"], token_data["name"], PublicKey(
                            token_data["address"]), Decimal(token_data["decimals"]))
                        quote_data = SpotMarketLookup._find_data_by_symbol("USDT", self.token_data)
                        if quote_data is None:
                            raise Exception("Could not load token data for USDT (which should always be present).")
                        quote = Token(quote_data["symbol"], quote_data["name"], PublicKey(
                            quote_data["address"]), Decimal(quote_data["decimals"]))
                        return SpotMarket(base, quote, market_address)
        return None

    def all_markets(self) -> typing.Sequence[Market]:
        usdt = SpotMarketLookup._find_token_by_symbol_or_error("USDT", self.token_data)
        usdc = SpotMarketLookup._find_token_by_symbol_or_error("USDC", self.token_data)

        all_markets: typing.List[SpotMarket] = []
        for token_data in self.token_data["tokens"]:
            if "extensions" in token_data:
                if "serumV3Usdc" in token_data["extensions"]:
                    market_address_string = token_data["extensions"]["serumV3Usdc"]
                    market_address = PublicKey(market_address_string)
                    base = Token(token_data["symbol"], token_data["name"], PublicKey(
                        token_data["address"]), Decimal(token_data["decimals"]))
                    all_markets += [SpotMarket(base, usdc, market_address)]
                if "serumV3Usdt" in token_data["extensions"]:
                    market_address_string = token_data["extensions"]["serumV3Usdt"]
                    market_address = PublicKey(market_address_string)
                    base = Token(token_data["symbol"], token_data["name"], PublicKey(
                        token_data["address"]), Decimal(token_data["decimals"]))
                    all_markets += [SpotMarket(base, usdt, market_address)]

        return all_markets

