import time
import typing
from decimal import Decimal

import construct
from solana.publickey import PublicKey
from solana.rpc.api import Client
from solana.rpc.commitment import Commitment

from .._layouts.group import GROUP_V1, GROUP_V2
from ..account_info import AccountInfo
from ..addressable_account import AddressableAccount
from ..enums import Version
from .aggregator import Aggregator
from .basket_token import BasketToken
from .constants import DEFAULT_TOKENFILE_NAME
from .index import Index
from .mango_account_flags import MangoAccountFlags
from .mango_market import CompoundMarketLookup, MarketLookup
from .mango_spot_market import SpotMarketLookup
from .market_metadata import MarketMetadata
from .token import SolToken, Token, TokenLookup
from .token_value import TokenValue


class Group(AddressableAccount):
    def __init__(
        self,
        conn: Client,
        account_info: AccountInfo,
        version: Version,
        name: str,
        account_flags: MangoAccountFlags,
        basket_tokens: typing.List[BasketToken],
        markets: typing.List[MarketMetadata],
        signer_nonce: Decimal,
        signer_key: PublicKey,
        dex_program_id: PublicKey,
        total_deposits: typing.List[TokenValue],
        total_borrows: typing.List[TokenValue],
        maint_coll_ratio: Decimal,
        init_coll_ratio: Decimal,
        srm_vault: PublicKey,
        admin: PublicKey,
        borrow_limits: typing.List[TokenValue],
    ):
        super().__init__(account_info)
        self.conn: Client = conn
        self.version: Version = version
        self.name: str = name
        self.account_flags: MangoAccountFlags = account_flags
        self.basket_tokens: typing.List[BasketToken] = basket_tokens
        self.markets: typing.List[MarketMetadata] = markets
        self.signer_nonce: Decimal = signer_nonce
        self.signer_key: PublicKey = signer_key
        self.dex_program_id: PublicKey = dex_program_id
        self.total_deposits: typing.List[TokenValue] = total_deposits
        self.total_borrows: typing.List[TokenValue] = total_borrows
        self.maint_coll_ratio: Decimal = maint_coll_ratio
        self.init_coll_ratio: Decimal = init_coll_ratio
        self.srm_vault: PublicKey = srm_vault
        self.admin: PublicKey = admin
        self.borrow_limits: typing.List[TokenValue] = borrow_limits

    @property
    def shared_quote_token(self) -> BasketToken:
        return self.basket_tokens[-1]

    @property
    def base_tokens(self) -> typing.List[BasketToken]:
        return self.basket_tokens[:-1]

    # When loading from a layout, we ignore mint_decimals. In this Discord from Daffy:
    #   https://discord.com/channels/791995070613159966/818978757648842782/851481660049850388
    # he says it's:
    # > same as what is stored on on chain Mint
    # > Cached on the group so we don't have to pass in the mint every time
    #
    # Since we already have that value from our `Token` we don't need to use it and we can
    # stick with passing around `Token` objects.
    #
    @staticmethod
    def from_layout(
        conn: Client,
        layout: construct.Struct,
        name: str,
        account_info: AccountInfo,
        version: Version,
        token_lookup: TokenLookup,
        market_lookup: MarketLookup,
    ) -> "Group":
        account_flags: MangoAccountFlags = MangoAccountFlags.from_layout(layout.account_flags)

        basket_tokens: typing.List[BasketToken] = []
        total_deposits: typing.List[TokenValue] = []
        total_borrows: typing.List[TokenValue] = []
        borrow_limits: typing.List[TokenValue] = []
        for index, token_address in enumerate(layout.tokens):
            static_token_data = token_lookup.find_by_mint(token_address)
            if static_token_data is None:
                raise Exception(f"Could not find token with mint '{token_address}'.")

            # We create a new Token object here specifically to force the use of our own decimals
            token = Token(static_token_data.symbol, static_token_data.name, token_address, layout.mint_decimals[index])
            token_index = Index.from_layout(layout.indexes[index], token)
            basket_token = BasketToken(token, layout.vaults[index], token_index)
            basket_tokens += [basket_token]
            total_deposits += [TokenValue(token, token.shift_to_decimals(layout.total_deposits[index]))]
            total_borrows += [TokenValue(token, token.shift_to_decimals(layout.total_borrows[index]))]
            borrow_limits += [TokenValue(token, token.shift_to_decimals(layout.borrow_limits[index]))]

        markets: typing.List[MarketMetadata] = []
        for index, market_address in enumerate(layout.spot_markets):
            spot_market = market_lookup.find_by_address(market_address)
            if spot_market is None:
                raise Exception(f"Could not find spot market with address '{market_address}'.")

            base_token = BasketToken.find_by_mint(basket_tokens, spot_market.base.mint)
            quote_token = BasketToken.find_by_mint(basket_tokens, spot_market.quote.mint)

            market = MarketMetadata(
                spot_market.symbol,
                market_address,
                base_token,
                quote_token,
                spot_market,
                layout.oracles[index],
                layout.oracle_decimals[index],
            )
            markets += [market]

        maint_coll_ratio = layout.maint_coll_ratio.quantize(Decimal(".01"))
        init_coll_ratio = layout.init_coll_ratio.quantize(Decimal(".01"))

        return Group(
            conn=conn,
            account_info=account_info,
            version=version,
            name=name,
            account_flags=account_flags,
            basket_tokens=basket_tokens,
            markets=markets,
            signer_nonce=layout.signer_nonce,
            signer_key=layout.signer_key,
            dex_program_id=layout.dex_program_id,
            total_deposits=total_deposits,
            total_borrows=total_borrows,
            maint_coll_ratio=maint_coll_ratio,
            init_coll_ratio=init_coll_ratio,
            srm_vault=layout.srm_vault,
            admin=layout.admin,
            borrow_limits=borrow_limits,
        )

    @staticmethod
    def parse(
        conn: Client, account_info: AccountInfo, group_name: str, token_lookup: TokenLookup, market_lookup: MarketLookup
    ) -> "Group":
        data = account_info.data
        if len(data) == GROUP_V1.sizeof():
            layout = GROUP_V1.parse(data)
            version: Version = Version.V1
        elif len(data) == GROUP_V2.sizeof():
            version = Version.V2
            layout = GROUP_V2.parse(data)
        else:
            raise Exception(
                f"Group data length ({len(data)}) does not match expected size \
                ({GROUP_V1.sizeof()} or {GROUP_V2.sizeof()})"
            )

        return Group.from_layout(conn, layout, group_name, account_info, version, token_lookup, market_lookup)

    @staticmethod
    def load(conn: Client, group_name: str, group_id: PublicKey, token_filename: str = DEFAULT_TOKENFILE_NAME):
        account_info = AccountInfo.load(conn, group_id)
        token_lookup = TokenLookup.load(token_filename)
        market_lookup: MarketLookup = CompoundMarketLookup([SpotMarketLookup.load(token_filename)])
        if account_info is None:
            raise Exception(f"Group account not found at address '{group_id}'")
        return Group.parse(
            conn=conn,
            account_info=account_info,
            group_name=group_name,
            token_lookup=token_lookup,
            market_lookup=market_lookup,
        )

    def price_index_of_token(self, token: Token) -> int:
        for index, existing in enumerate(self.basket_tokens):
            if existing.token == token:
                return index
        return -1

    def fetch_token_prices(self, conn: Client) -> typing.List[TokenValue]:
        started_at = time.time()

        # Note: we can just load the oracle data in a simpler way, with:
        #   oracles = map(lambda market: Aggregator.load(context, market.oracle), self.markets)
        # but that makes a network request for every oracle. We can reduce that to just one request
        # if we use AccountInfo.load_multiple() and parse the data ourselves.
        #
        # This seems to halve the time this function takes.
        oracle_addresses = list([market.oracle for market in self.markets])
        oracle_account_infos = AccountInfo.load_multiple(conn, oracle_addresses)
        oracles = map(lambda oracle_account_info: Aggregator.parse(oracle_account_info), oracle_account_infos)
        prices = list(map(lambda oracle: oracle.price, oracles)) + [Decimal(1)]
        token_prices = []
        for index, price in enumerate(prices):
            token_prices += [TokenValue(self.basket_tokens[index].token, price)]

        time_taken = time.time() - started_at
        self.logger.info(f"Fetching prices complete. Time taken: {time_taken:.2f} seconds.")
        return token_prices

    @staticmethod
    def load_with_prices(
        conn: Client, group_name: str, group_id: PublicKey, token_filename: str = DEFAULT_TOKENFILE_NAME
    ) -> typing.Tuple["Group", typing.List[TokenValue]]:
        group = Group.load(conn=conn, group_name=group_name, group_id=group_id, token_filename=token_filename)
        prices = group.fetch_token_prices(conn)
        return group, prices

    def fetch_balances(self, commitment: Commitment, root_address: PublicKey) -> typing.List[TokenValue]:
        balances: typing.List[TokenValue] = []
        sol_balance = self.conn.get_balance(root_address)["result"]["value"]
        balances += [TokenValue(SolToken, sol_balance)]

        for basket_token in self.basket_tokens:
            balance = TokenValue.fetch_total_value(
                conn=self.conn, commitment=commitment, account_public_key=root_address, token=basket_token.token
            )
            balances += [balance]
        return balances

    def __str__(self) -> str:
        total_deposits = "\n        ".join(map(str, self.total_deposits))
        total_borrows = "\n        ".join(map(str, self.total_borrows))
        borrow_limits = "\n        ".join(map(str, self.borrow_limits))
        shared_quote_token = str(self.shared_quote_token).replace("\n", "\n        ")
        base_tokens = "\n        ".join([f"{tok}".replace("\n", "\n        ") for tok in self.base_tokens])
        markets = "\n        ".join([f"{mkt}".replace("\n", "\n        ") for mkt in self.markets])
        return f"""
« Group [{self.version} - {self.name}] {self.address}:
    Flags: {self.account_flags}
    Base Tokens:
        {base_tokens}
    Quote Token:
        {shared_quote_token}
    Markets:
        {markets}
    DEX Program ID: « {self.dex_program_id} »
    SRM Vault: « {self.srm_vault} »
    Admin: « {self.admin} »
    Signer Nonce: {self.signer_nonce}
    Signer Key: « {self.signer_key} »
    Initial Collateral Ratio: {self.init_coll_ratio}
    Maintenance Collateral Ratio: {self.maint_coll_ratio}
    Total Deposits:
        {total_deposits}
    Total Borrows:
        {total_borrows}
    Borrow Limits:
        {borrow_limits}
»
"""
