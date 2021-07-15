
# ## INDEX
#
# Here's the [Mango Rust structure](https://github.com/blockworks-foundation/mango/blob/master/program/src/state.rs):
# ```
# #[derive(Copy, Clone)]
# #[repr(C)]
# pub struct MangoIndex {
#     pub last_update: u64,
#     pub borrow: U64F64,
#     pub deposit: U64F64
# }
# ```
import construct

from pyserum._layouts.adapters import DatetimeAdapter, FloatAdapter

INDEX = construct.Struct(
    "last_update" / DatetimeAdapter(),
    "borrow" / FloatAdapter(),
    "deposit" / FloatAdapter()
)



