from __future__ import annotations

from decimal import Decimal
from typing import List, NamedTuple

from solana.publickey import PublicKey
from solana.rpc.api import Client
from solana.rpc.commitment import Recent
from solana.rpc.types import Commitment, MemcmpOpts
from solana.system_program import CreateAccountParams, create_account
from solana.transaction import TransactionInstruction

from ._layouts.account_flags import SERUM_ACCOUNT_FLAGS_LAYOUT
from ._layouts.open_orders import OPEN_ORDERS_LAYOUT
from .account_info import AccountInfo
from .enums import Version
from .instructions import SERUM_V3_DEX_PROGRAM_ID
from .market.state import MarketState
from .serum_account_flags import SerumAccountFlags


class ProgramAccount(NamedTuple):
    public_key: PublicKey
    data: bytes
    is_executablable: bool
    lamports: int
    owner: PublicKey


class OpenOrdersAccount:
    # pylint: disable=too-many-arguments
    # pylint: disable=too-many-instance-attributes
    # pylint: disable=too-many-locals
    def __init__(
        self,
        account_info: AccountInfo,
        version: Version,
        program_id: PublicKey,
        account_flags: SerumAccountFlags,
        market: PublicKey,
        owner: PublicKey,
        base_token_free: Decimal,
        base_token_total: Decimal,
        quote_token_free: Decimal,
        quote_token_total: Decimal,
        free_slot_bits: Decimal,
        is_bid_bits: Decimal,
        orders: List[Decimal],
        client_ids: List[Decimal],
        referrer_rebate_accrued: Decimal,
    ):
        self.account_info = account_info
        self.version: Version = version
        self.program_id: PublicKey = program_id
        self.account_flags: SerumAccountFlags = account_flags
        self.market: PublicKey = market
        self.owner: PublicKey = owner
        self.base_token_free: Decimal = base_token_free
        self.base_token_total: Decimal = base_token_total
        self.quote_token_free: Decimal = quote_token_free
        self.quote_token_total: Decimal = quote_token_total
        self.free_slot_bits: Decimal = free_slot_bits
        self.is_bid_bits: Decimal = is_bid_bits
        self.orders: List[Decimal] = orders
        self.client_ids: List[Decimal] = client_ids
        self.referrer_rebate_accrued: Decimal = referrer_rebate_accrued

    @staticmethod
    def parse_account(account_info: AccountInfo, base_decimals: Decimal, quote_decimals: Decimal) -> OpenOrdersAccount:
        """Given an AccountInfo object, base_decimal and quote_decimal, construct an OpenOrdersAccounts object."""
        open_order_decoded = OPEN_ORDERS_LAYOUT.parse(account_info.data)
        if not open_order_decoded.account_flags.open_orders or not open_order_decoded.account_flags.initialized:
            raise Exception("Not an open order account or not initialized.")

        base_divisor = 10 ** base_decimals
        quote_divisor = 10 ** quote_decimals

        return OpenOrdersAccount(
            account_flags=open_order_decoded.account_flags,
            account_info=account_info,
            version=Version.UNSPECIFIED,
            program_id=account_info.owner,
            market=PublicKey(open_order_decoded.market),
            owner=PublicKey(open_order_decoded.owner),
            base_token_free=open_order_decoded.base_token_free / base_divisor,
            base_token_total=open_order_decoded.base_token_total / base_divisor,
            quote_token_free=open_order_decoded.quote_token_free / quote_divisor,
            quote_token_total=open_order_decoded.quote_token_total / quote_divisor,
            free_slot_bits=int.from_bytes(open_order_decoded.free_slot_bits, "little"),
            is_bid_bits=int.from_bytes(open_order_decoded.is_bid_bits, "little"),
            orders=[int.from_bytes(order, "little") for order in open_order_decoded.orders],
            client_ids=open_order_decoded.client_ids,
            referrer_rebate_accrued=open_order_decoded.referrer_rebate_accrued,
        )

    @staticmethod
    def find_for_market_and_owner(
        conn: Client, market: PublicKey, owner: PublicKey, program_id: PublicKey, commitment: Commitment = Recent
    ) -> List[OpenOrdersAccount]:
        """Returns the OpenOrderAccount if it exists for a market and owner."""
        filters = [
            MemcmpOpts(
                offset=SERUM_ACCOUNT_FLAGS_LAYOUT.sizeof() + 5,  # 5 padding bytes and the account flags
                bytes=str(market),
            ),
            MemcmpOpts(
                offset=SERUM_ACCOUNT_FLAGS_LAYOUT.sizeof()
                + 37,  # 5 bytes of padding, 8 bytes of account flag, 32 bytes of market public key
                bytes=str(owner),
            ),
        ]
        response = conn.get_program_accounts(
            program_id,
            data_size=OPEN_ORDERS_LAYOUT.sizeof(),
            memcmp_opts=filters,
            commitment=commitment,
            encoding="base64",
        )

        accounts = list(
            map(
                lambda pair: AccountInfo.from_response_values(pair[0], pair[1]),
                [(result["account"], PublicKey(result["pubkey"])) for result in response["result"]],
            )
        )
        market_state = MarketState.load(conn, market, program_id)
        return list(
            map(
                lambda acc: OpenOrdersAccount.parse_account(
                    account_info=acc,
                    base_decimals=market_state.base_spl_token_decimals(),
                    quote_decimals=market_state.quote_spl_token_decimals(),
                ),
                accounts,
            )
        )

    @staticmethod
    def load(conn: Client, address: PublicKey, base_decimals: Decimal, quote_decimals: Decimal) -> OpenOrdersAccount:
        """Get an OpenOrdersAccount from an address and base/quote decimals."""
        acct_info = AccountInfo.load(conn, address)
        return OpenOrdersAccount.parse_account(
            account_info=acct_info, base_decimals=base_decimals, quote_decimals=quote_decimals
        )


def make_create_account_instruction(
    owner_address: PublicKey,
    new_account_address: PublicKey,
    lamports: int,
    program_id: PublicKey = SERUM_V3_DEX_PROGRAM_ID,
) -> TransactionInstruction:
    return create_account(
        CreateAccountParams(
            from_pubkey=owner_address,
            new_account_pubkey=new_account_address,
            lamports=lamports,
            space=OPEN_ORDERS_LAYOUT.sizeof(),
            program_id=program_id,
        )
    )
