# ## GROUP_V1
#
# Groups have a common quote currency, and it's always the last token in the tokens.
#
# That means the number of markets is number_of_tokens - 1.
#
# Here's the [Mango Rust structure](https://github.com/blockworks-foundation/mango/blob/master/program/src/state.rs):
# ```
# #[derive(Copy, Clone)]
# #[repr(C)]
# pub struct MangoGroup {
#     pub account_flags: u64,
#     pub tokens: [Pubkey; NUM_TOKENS],  // Last token is shared quote currency
#     pub vaults: [Pubkey; NUM_TOKENS],  // where funds are stored
#     pub indexes: [MangoIndex; NUM_TOKENS],  // to keep track of interest
#     pub spot_markets: [Pubkey; NUM_MARKETS],  // pubkeys to MarketState of serum dex
#     pub oracles: [Pubkey; NUM_MARKETS],  // oracles that give price of each base currency in quote currency
#     pub signer_nonce: u64,
#     pub signer_key: Pubkey,
#     pub dex_program_id: Pubkey,  // serum dex program id
#
#     // denominated in Mango index adjusted terms
#     pub total_deposits: [U64F64; NUM_TOKENS],
#     pub total_borrows: [U64F64; NUM_TOKENS],
#
#     pub maint_coll_ratio: U64F64,  // 1.10
#     pub init_coll_ratio: U64F64,  //  1.20
#
#     pub srm_vault: Pubkey,  // holds users SRM for fee reduction
#
#     /// This admin key is only for alpha release and the only power it has is to amend borrow limits
#     /// If users borrow too much too quickly before liquidators are able to handle the volume,
#     /// lender funds will be at risk. Hence these borrow limits will be raised slowly
#     pub admin: Pubkey,
#     pub borrow_limits: [u64; NUM_TOKENS],
#
#     pub mint_decimals: [u8; NUM_TOKENS],
#     pub oracle_decimals: [u8; NUM_MARKETS],
#     pub padding: [u8; MANGO_GROUP_PADDING]
# }
# impl_loadable!(MangoGroup);
# ```
import construct

from pyserum._layouts.account_flags import MANGO_ACCOUNT_FLAGS
from pyserum._layouts.adapters import DecimalAdapter, FloatAdapter, PublicKeyAdapter
from pyserum._layouts.mango_index import INDEX

GROUP_V1_NUM_TOKENS = 3
GROUP_V1_NUM_MARKETS = GROUP_V1_NUM_TOKENS - 1
GROUP_V1_PADDING = 8 - (GROUP_V1_NUM_TOKENS + GROUP_V1_NUM_MARKETS) % 8
GROUP_V1 = construct.Struct(
    "account_flags" / MANGO_ACCOUNT_FLAGS,
    "tokens" / construct.Array(GROUP_V1_NUM_TOKENS, PublicKeyAdapter()),
    "vaults" / construct.Array(GROUP_V1_NUM_TOKENS, PublicKeyAdapter()),
    "indexes" / construct.Array(GROUP_V1_NUM_TOKENS, INDEX),
    "spot_markets" / construct.Array(GROUP_V1_NUM_MARKETS, PublicKeyAdapter()),
    "oracles" / construct.Array(GROUP_V1_NUM_MARKETS, PublicKeyAdapter()),
    "signer_nonce" / DecimalAdapter(),
    "signer_key" / PublicKeyAdapter(),
    "dex_program_id" / PublicKeyAdapter(),
    "total_deposits" / construct.Array(GROUP_V1_NUM_TOKENS, FloatAdapter()),
    "total_borrows" / construct.Array(GROUP_V1_NUM_TOKENS, FloatAdapter()),
    "maint_coll_ratio" / FloatAdapter(),
    "init_coll_ratio" / FloatAdapter(),
    "srm_vault" / PublicKeyAdapter(),
    "admin" / PublicKeyAdapter(),
    "borrow_limits" / construct.Array(GROUP_V1_NUM_TOKENS, DecimalAdapter()),
    "mint_decimals" / construct.Array(GROUP_V1_NUM_TOKENS, DecimalAdapter(1)),
    "oracle_decimals" / construct.Array(GROUP_V1_NUM_MARKETS, DecimalAdapter(1)),
    "padding" / construct.Array(GROUP_V1_PADDING, construct.Padding(1)),
)


# ## GROUP_V2
#
# Groups have a common quote currency, and it's always the last token in the tokens.
#
# That means the number of markets is number_of_tokens - 1.
#
# There is no difference between the V1 and V2 structures except for the number of tokens.
# We handle things this way to be consistent with how we handle V1 and V2 `MarginAccount`s.
#
# Here's the [Mango Rust structure](https://github.com/blockworks-foundation/mango/blob/master/program/src/state.rs):
# ```
# #[derive(Copy, Clone)]
# #[repr(C)]
# pub struct MangoGroup {
#     pub account_flags: u64,
#     pub tokens: [Pubkey; NUM_TOKENS],  // Last token is shared quote currency
#     pub vaults: [Pubkey; NUM_TOKENS],  // where funds are stored
#     pub indexes: [MangoIndex; NUM_TOKENS],  // to keep track of interest
#     pub spot_markets: [Pubkey; NUM_MARKETS],  // pubkeys to MarketState of serum dex
#     pub oracles: [Pubkey; NUM_MARKETS],  // oracles that give price of each base currency in quote currency
#     pub signer_nonce: u64,
#     pub signer_key: Pubkey,
#     pub dex_program_id: Pubkey,  // serum dex program id
#
#     // denominated in Mango index adjusted terms
#     pub total_deposits: [U64F64; NUM_TOKENS],
#     pub total_borrows: [U64F64; NUM_TOKENS],
#
#     pub maint_coll_ratio: U64F64,  // 1.10
#     pub init_coll_ratio: U64F64,  //  1.20
#
#     pub srm_vault: Pubkey,  // holds users SRM for fee reduction
#
#     /// This admin key is only for alpha release and the only power it has is to amend borrow limits
#     /// If users borrow too much too quickly before liquidators are able to handle the volume,
#     /// lender funds will be at risk. Hence these borrow limits will be raised slowly
#     /// UPDATE: 4/15/2021 - this admin key is now useless, borrow limits are removed
#     pub admin: Pubkey,
#     pub borrow_limits: [u64; NUM_TOKENS],
#
#     pub mint_decimals: [u8; NUM_TOKENS],
#     pub oracle_decimals: [u8; NUM_MARKETS],
#     pub padding: [u8; MANGO_GROUP_PADDING]
# }
#
# ```


GROUP_V2_NUM_TOKENS = 5
GROUP_V2_NUM_MARKETS = GROUP_V2_NUM_TOKENS - 1
GROUP_V2_PADDING = 8 - (GROUP_V2_NUM_TOKENS + GROUP_V2_NUM_MARKETS) % 8
GROUP_V2 = construct.Struct(
    "account_flags" / MANGO_ACCOUNT_FLAGS,
    "tokens" / construct.Array(GROUP_V2_NUM_TOKENS, PublicKeyAdapter()),
    "vaults" / construct.Array(GROUP_V2_NUM_TOKENS, PublicKeyAdapter()),
    "indexes" / construct.Array(GROUP_V2_NUM_TOKENS, INDEX),
    "spot_markets" / construct.Array(GROUP_V2_NUM_MARKETS, PublicKeyAdapter()),
    "oracles" / construct.Array(GROUP_V2_NUM_MARKETS, PublicKeyAdapter()),
    "signer_nonce" / DecimalAdapter(),
    "signer_key" / PublicKeyAdapter(),
    "dex_program_id" / PublicKeyAdapter(),
    "total_deposits" / construct.Array(GROUP_V2_NUM_TOKENS, FloatAdapter()),
    "total_borrows" / construct.Array(GROUP_V2_NUM_TOKENS, FloatAdapter()),
    "maint_coll_ratio" / FloatAdapter(),
    "init_coll_ratio" / FloatAdapter(),
    "srm_vault" / PublicKeyAdapter(),
    "admin" / PublicKeyAdapter(),
    "borrow_limits" / construct.Array(GROUP_V2_NUM_TOKENS, DecimalAdapter()),
    "mint_decimals" / construct.Array(GROUP_V2_NUM_TOKENS, DecimalAdapter(1)),
    "oracle_decimals" / construct.Array(GROUP_V2_NUM_MARKETS, DecimalAdapter(1)),
    "padding" / construct.Array(GROUP_V2_PADDING, construct.Padding(1)),
)
