import typing
import itertools
import construct
from .account_flags import MANGO_ACCOUNT_FLAGS
from .adapters import DecimalAdapter, FloatAdapter, PublicKeyAdapter

# ## MARGIN_ACCOUNT_V1
#
# Here's the V1 [Mango Rust structure](https://github.com/blockworks-foundation/mango/blob/master/program/src/state.rs):
# ```
# #[derive(Copy, Clone)]
# #[repr(C)]
# pub struct MarginAccount {
#     pub account_flags: u64,
#     pub mango_group: Pubkey,
#     pub owner: Pubkey,  // solana pubkey of owner
#
#     // assets and borrows are denominated in Mango adjusted terms
#     pub deposits: [U64F64; NUM_TOKENS],  // assets being lent out and gaining interest, including collateral
#
#     // this will be incremented every time an order is opened and decremented when order is closed
#     pub borrows: [U64F64; NUM_TOKENS],  // multiply by current index to get actual value
#
#     pub open_orders: [Pubkey; NUM_MARKETS],  // owned by Mango
#
#     pub being_liquidated: bool,
#     pub padding: [u8; 7] // padding to make compatible with previous MarginAccount size
#     // TODO add has_borrows field for easy memcmp fetching
# }
# ```


MARGIN_ACCOUNT_V1_NUM_TOKENS = 3
MARGIN_ACCOUNT_V1_NUM_MARKETS = MARGIN_ACCOUNT_V1_NUM_TOKENS - 1
MARGIN_ACCOUNT_V1 = construct.Struct(
    "account_flags" / MANGO_ACCOUNT_FLAGS,
    "mango_group" / PublicKeyAdapter(),
    "owner" / PublicKeyAdapter(),
    "deposits" / construct.Array(MARGIN_ACCOUNT_V1_NUM_TOKENS, FloatAdapter()),
    "borrows" / construct.Array(MARGIN_ACCOUNT_V1_NUM_TOKENS, FloatAdapter()),
    "open_orders" / construct.Array(MARGIN_ACCOUNT_V1_NUM_MARKETS, PublicKeyAdapter()),
    "being_liquidated" / DecimalAdapter(1),
    "padding" / construct.Padding(7),
)


# ## MARGIN_ACCOUNT_V2
#
# Here's the V2 [Mango Rust structure](https://github.com/blockworks-foundation/mango/blob/master/program/src/state.rs):
# ```
# #[derive(Copy, Clone)]
# #[repr(C)]
# pub struct MarginAccount {
#     pub account_flags: u64,
#     pub mango_group: Pubkey,
#     pub owner: Pubkey,  // solana pubkey of owner
#
#     // assets and borrows are denominated in Mango adjusted terms
#     pub deposits: [U64F64; NUM_TOKENS],  // assets being lent out and gaining interest, including collateral
#
#     // this will be incremented every time an order is opened and decremented when order is closed
#     pub borrows: [U64F64; NUM_TOKENS],  // multiply by current index to get actual value
#
#     pub open_orders: [Pubkey; NUM_MARKETS],  // owned by Mango
#
#     pub being_liquidated: bool,
#     pub has_borrows: bool, // does the account have any open borrows? set by checked_add_borrow and checked_sub_borrow
#     pub padding: [u8; 64] // padding
# }
# ```


MARGIN_ACCOUNT_V2_NUM_TOKENS = 5
MARGIN_ACCOUNT_V2_NUM_MARKETS = MARGIN_ACCOUNT_V2_NUM_TOKENS - 1
MARGIN_ACCOUNT_V2 = construct.Struct(
    "account_flags" / MANGO_ACCOUNT_FLAGS,
    "mango_group" / PublicKeyAdapter(),
    "owner" / PublicKeyAdapter(),
    "deposits" / construct.Array(MARGIN_ACCOUNT_V2_NUM_TOKENS, FloatAdapter()),
    "borrows" / construct.Array(MARGIN_ACCOUNT_V2_NUM_TOKENS, FloatAdapter()),
    "open_orders" / construct.Array(MARGIN_ACCOUNT_V2_NUM_MARKETS, PublicKeyAdapter()),
    "being_liquidated" / DecimalAdapter(1),
    "has_borrows" / DecimalAdapter(1),
    "padding" / construct.Padding(70),
)

# ## build_margin_account_parser_for_num_tokens() function
#
# This function builds a `construct.Struct` that can load a `MarginAccount` with a
# specific number of tokens. The number of markets and size of padding are derived
# from the number of tokens.


def build_margin_account_parser_for_num_tokens(num_tokens: int) -> construct.Struct:
    num_markets = num_tokens - 1

    return construct.Struct(
        "account_flags" / MANGO_ACCOUNT_FLAGS,
        "mango_group" / PublicKeyAdapter(),
        "owner" / PublicKeyAdapter(),
        "deposits" / construct.Array(num_tokens, FloatAdapter()),
        "borrows" / construct.Array(num_tokens, FloatAdapter()),
        "open_orders" / construct.Array(num_markets, PublicKeyAdapter()),
        "padding" / construct.Padding(8),
    )


# ## build_margin_account_parser_for_length() function
#
# This function takes a data length (presumably the size of the structure returned from
# the `AccountInfo`) and returns a `MarginAccount` structure that can parse it.
#
# If the size doesn't _exactly_ match the size of the `Struct`, and Exception is raised.


def build_margin_account_parser_for_length(length: int) -> construct.Struct:
    tried_sizes: typing.List[int] = []
    for num_tokens in itertools.count(start=2):
        parser = build_margin_account_parser_for_num_tokens(num_tokens)
        if parser.sizeof() == length:
            return parser

        tried_sizes += [parser.sizeof()]
        if parser.sizeof() > length:
            raise Exception(
                f"Could not create MarginAccount parser for length ({length}) - tried sizes ({tried_sizes})"
            )
