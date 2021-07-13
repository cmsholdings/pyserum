from construct import BitsInteger, BitsSwapped, BitStruct, Const, Padding, Flag  # type: ignore

# We will use a bitstruct with 64 bits instead of the widebits implementation in serum-js.
SERUM_ACCOUNT_FLAGS_LAYOUT = BitsSwapped(  # Swap to little endian
    BitStruct(
        "initialized" / Flag,
        "market" / Flag,
        "open_orders" / Flag,
        "request_queue" / Flag,
        "event_queue" / Flag,
        "bids" / Flag,
        "asks" / Flag,
        "disabled" / Flag,
        Const(0, BitsInteger(56)),  # Padding
    )
)

MANGO_ACCOUNT_FLAGS = BitsSwapped(
    BitStruct("initialized" / Flag, "group" / Flag, "margin_account" / Flag, "srm_account" / Flag, Padding(4 + (7 * 8)))
)
