import construct
from .adapters import DecimalAdapter, FloatAdapter

# # Instruction Structs

# ## MANGO_INSTRUCTION_VARIANT_FINDER
#
# The 'variant' of the instruction is held in the first 4 bytes. The remainder of the data
# is per-instruction.
#
# This `struct` loads only the first 4 bytes, as an `int`, so we know which specific parser
# has to be used to load the rest of the data.


MANGO_INSTRUCTION_VARIANT_FINDER = construct.Struct("variant" / construct.BytesInteger(4, swapped=True))


# ## Variant 0: INIT_MANGO_GROUP
#
# Instruction variant 1. From the
# [Rust source](https://github.com/blockworks-foundation/mango/blob/master/program/src/instruction.rs):
#
# > Initialize a group of lending pools that can be cross margined
# ```
# InitMangoGroup {
#     signer_nonce: u64,
#     maint_coll_ratio: U64F64,
#     init_coll_ratio: U64F64,
#     borrow_limits: [u64; NUM_TOKENS]
# },
# ```


INIT_MANGO_GROUP = construct.Struct(
    "variant" / construct.Const(0x0, construct.BytesInteger(4, swapped=True)),
    "signer_nonce" / DecimalAdapter(),
    "maint_coll_ratio" / FloatAdapter(),
    "init_coll_ratio" / FloatAdapter(),
    #  "borrow_limits" / construct.Array(NUM_TOKENS, DecimalAdapter())  # This is inconsistently available
)


# ## Variant 1: INIT_MARGIN_ACCOUNT
#
# Instruction variant 1. From the
# [Rust source](https://github.com/blockworks-foundation/mango/blob/master/program/src/instruction.rs):
#
# > Initialize a margin account for a user
# ```
# InitMarginAccount,
# ```


INIT_MARGIN_ACCOUNT = construct.Struct(
    "variant" / construct.Const(0x1, construct.BytesInteger(4, swapped=True)),
)


# ## Variant 2: DEPOSIT
#
# Instruction variant 2. From the
# [Rust source](https://github.com/blockworks-foundation/mango/blob/master/program/src/instruction.rs):
#
# > Deposit funds into margin account to be used as collateral and earn interest.
# ```
# Deposit {
#     quantity: u64
# },
# ```


DEPOSIT = construct.Struct(
    "variant" / construct.Const(0x2, construct.BytesInteger(4, swapped=True)), "quantity" / DecimalAdapter()
)


# ## Variant 3: WITHDRAW
#
# Instruction variant 3. From the
# [Rust source](https://github.com/blockworks-foundation/mango/blob/master/program/src/instruction.rs):
#
# > Withdraw funds that were deposited earlier.
# ```
# Withdraw {
#     quantity: u64
# },
# ```


WITHDRAW = construct.Struct(
    "variant" / construct.Const(0x3, construct.BytesInteger(4, swapped=True)), "quantity" / DecimalAdapter()
)


# ## Variant 4: BORROW
#
# Instruction variant 4. From the
# [Rust source](https://github.com/blockworks-foundation/mango/blob/master/program/src/instruction.rs):
#
# > Borrow by incrementing MarginAccount.borrows given collateral ratio is below init_coll_rat
# ```
# Borrow {
#     token_index: usize,
#     quantity: u64
# },
# ```


BORROW = construct.Struct(
    "variant" / construct.Const(0x4, construct.BytesInteger(4, swapped=True)),
    "token_index" / DecimalAdapter(),
    "quantity" / DecimalAdapter(),
)


# ## Variant 5: SETTLE_BORROW
#
# Instruction variant 5. From the
# [Rust source](https://github.com/blockworks-foundation/mango/blob/master/program/src/instruction.rs):
#
# > Use this token's position and deposit to reduce borrows
# ```
# SettleBorrow {
#     token_index: usize,
#     quantity: u64
# },
# ```


SETTLE_BORROW = construct.Struct(
    "variant" / construct.Const(0x5, construct.BytesInteger(4, swapped=True)),
    "token_index" / DecimalAdapter(),
    "quantity" / DecimalAdapter(),
)


# ## Variant 6: LIQUIDATE
#
# Instruction variant 6. From the
# [Rust source](https://github.com/blockworks-foundation/mango/blob/master/program/src/instruction.rs):
#
# > Take over a MarginAccount that is below init_coll_ratio by depositing funds
# ```
# Liquidate {
#     /// Quantity of each token liquidator is depositing in order to bring account above maint
#     deposit_quantities: [u64; NUM_TOKENS]
# },
# ```


_LIQUIDATE_NUM_TOKENS = 3  # Liquidate is deprecated and was only used with 3 tokens.
LIQUIDATE = construct.Struct(
    "variant" / construct.Const(0x6, construct.BytesInteger(4, swapped=True)),
    "deposit_quantities" / construct.Array(_LIQUIDATE_NUM_TOKENS, DecimalAdapter()),
)


# ## Variant 7: DEPOSIT_SRM
#
# Instruction variant 7. From the
# [Rust source](https://github.com/blockworks-foundation/mango/blob/master/program/src/instruction.rs):
#
# > Deposit SRM into the SRM vault for MangoGroup
# >
# > These SRM are not at risk and are not counted towards collateral or any margin calculations
# >
# > Depositing SRM is a strictly altruistic act with no upside and no downside
# ```
# DepositSrm {
#     quantity: u64
# },
# ```


DEPOSIT_SRM = construct.Struct(
    "variant" / construct.Const(0x7, construct.BytesInteger(4, swapped=True)), "quantity" / DecimalAdapter()
)


# ## Variant 8: WITHDRAW_SRM
#
# Instruction variant 8. From the
# [Rust source](https://github.com/blockworks-foundation/mango/blob/master/program/src/instruction.rs):
#
# > Withdraw SRM owed to this MarginAccount
# ```
# WithdrawSrm {
#     quantity: u64
# },
# ```


WITHDRAW_SRM = construct.Struct(
    "variant" / construct.Const(0x8, construct.BytesInteger(4, swapped=True)), "quantity" / DecimalAdapter()
)


# ## Variant 9: PLACE_ORDER
#
# Instruction variant 9. From the
# [Rust source](https://github.com/blockworks-foundation/mango/blob/master/program/src/instruction.rs):
#
# > Place an order on the Serum Dex using Mango margin facilities
# ```
# PlaceOrder {
#     order: serum_dex::instruction::NewOrderInstructionV3
# },
# ```


PLACE_ORDER = construct.Struct(
    "variant" / construct.Const(0x9, construct.BytesInteger(4, swapped=True)),
    "order" / construct.Padding(1),  # Actual type is: serum_dex::instruction::NewOrderInstructionV3
)


# ## Variant 10: SETTLE_FUNDS
#
# Instruction variant 10. From the
# [Rust source](https://github.com/blockworks-foundation/mango/blob/master/program/src/instruction.rs):
#
# > Settle all funds from serum dex open orders into MarginAccount positions
# ```
# SettleFunds,
# ```


SETTLE_FUNDS = construct.Struct(
    "variant" / construct.Const(0xA, construct.BytesInteger(4, swapped=True)),
)


# ## Variant 11: CANCEL_ORDER
#
# Instruction variant 11. From the
# [Rust source](https://github.com/blockworks-foundation/mango/blob/master/program/src/instruction.rs):
#
# > Cancel an order using dex instruction
# ```
# CancelOrder {
#     order: serum_dex::instruction::CancelOrderInstructionV2
# },
# ```


CANCEL_ORDER = construct.Struct(
    "variant" / construct.Const(0xB, construct.BytesInteger(4, swapped=True)),
    "order" / construct.Padding(1),  # Actual type is: serum_dex::instruction::CancelOrderInstructionV2
)


# ## Variant 12: CANCEL_ORDER_BY_CLIENT_ID
#
# Instruction variant 12. From the
# [Rust source](https://github.com/blockworks-foundation/mango/blob/master/program/src/instruction.rs):
#
# > Cancel an order using client_id
# ```
# CancelOrderByClientId {
#     client_id: u64
# },
# ```


CANCEL_ORDER_BY_CLIENT_ID = construct.Struct(
    "variant" / construct.Const(0xC, construct.BytesInteger(4, swapped=True)), "client_id" / DecimalAdapter()
)


# ## Variant 13: CHANGE_BORROW_LIMIT
#
# Instruction variant 13. From the
# [Rust source](https://github.com/blockworks-foundation/mango/blob/master/program/src/instruction.rs).
#
# > Change the borrow limit using admin key. This will not affect any open positions on any MarginAccount
# >
# > This is intended to be an instruction only in alpha stage while liquidity is slowly improved"_
# ```
# ChangeBorrowLimit {
#     token_index: usize,
#     borrow_limit: u64
# },
# ```


CHANGE_BORROW_LIMIT = construct.Struct(
    "variant" / construct.Const(0xD, construct.BytesInteger(4, swapped=True)),
    "token_index" / DecimalAdapter(),
    "borrow_limit" / DecimalAdapter(),
)


# ## Variant 14: PLACE_AND_SETTLE
#
# Instruction variant 14. From the
# [Rust source](https://github.com/blockworks-foundation/mango/blob/master/program/src/instruction.rs).
#
# > Place an order on the Serum Dex and settle funds from the open orders account
# ```
# PlaceAndSettle {
#     order: serum_dex::instruction::NewOrderInstructionV3
# },
# ```


PLACE_AND_SETTLE = construct.Struct(
    "variant" / construct.Const(0xE, construct.BytesInteger(4, swapped=True)),
    "order" / construct.Padding(1),  # Actual type is: serum_dex::instruction::NewOrderInstructionV3
)


# ## Variant 15: FORCE_CANCEL_ORDERS
#
# Instruction variant 15. From the
# [Rust source](https://github.com/blockworks-foundation/mango/blob/master/program/src/instruction.rs):
#
# > Allow a liquidator to cancel open orders and settle to recoup funds for partial liquidation
#
# ```
# ForceCancelOrders {
#     /// Max orders to cancel -- could be useful to lower this if running into compute limits
#     /// Recommended: 5
#     limit: u8
# },
# ```


FORCE_CANCEL_ORDERS = construct.Struct(
    "variant" / construct.Const(0xF, construct.BytesInteger(4, swapped=True)), "limit" / DecimalAdapter(1)
)


# ## Variant 16: PARTIAL_LIQUIDATE
#
# Instruction variant 16. From the
# [Rust source](https://github.com/blockworks-foundation/mango/blob/master/program/src/instruction.rs):
#
# > Take over a MarginAccount that is below init_coll_ratio by depositing funds
#
# ```
# PartialLiquidate {
#     /// Quantity of the token being deposited to repay borrows
#     max_deposit: u64
# },
# ```


PARTIAL_LIQUIDATE = construct.Struct(
    "variant" / construct.Const(0x10, construct.BytesInteger(4, swapped=True)), "max_deposit" / DecimalAdapter()
)


# ## InstructionParsersByVariant dictionary
#
# This dictionary provides an easy way for us to access the specific parser for a given variant.


InstructionParsersByVariant = {
    0: INIT_MANGO_GROUP,
    1: INIT_MARGIN_ACCOUNT,
    2: DEPOSIT,
    3: WITHDRAW,
    4: BORROW,
    5: SETTLE_BORROW,
    6: LIQUIDATE,
    7: DEPOSIT_SRM,
    8: WITHDRAW_SRM,
    9: PLACE_ORDER,
    10: SETTLE_FUNDS,
    11: CANCEL_ORDER,
    12: CANCEL_ORDER_BY_CLIENT_ID,
    13: CHANGE_BORROW_LIMIT,
    14: PLACE_AND_SETTLE,
    15: FORCE_CANCEL_ORDERS,
    16: PARTIAL_LIQUIDATE,
}
