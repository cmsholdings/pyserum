import construct
from .adapters import PublicKeyAdapter, DecimalAdapter, DatetimeAdapter

AGGREGATOR_CONFIG = construct.Struct(
    "description" / construct.PaddedString(32, "utf8"),
    "decimals" / DecimalAdapter(1),
    "restart_delay" / DecimalAdapter(1),
    "max_submissions" / DecimalAdapter(1),
    "min_submissions" / DecimalAdapter(1),
    "reward_amount" / DecimalAdapter(),
    "reward_token_account" / PublicKeyAdapter(),
)

# ## ROUND
#
# Here's the [Flux Rust structure]
# (https://github.com/blockworks-foundation/solana-flux-aggregator/blob/master/program/src/state.rs):
# ```
# #[derive(Clone, Debug, BorshSerialize, BorshDeserialize, BorshSchema, Default, PartialEq)]
# pub struct Round {
#     pub id: u64,
#     pub created_at: u64,
#     pub updated_at: u64,
# }
# ```


ROUND = construct.Struct(
    "entity_id" / DecimalAdapter(), "created_at" / DecimalAdapter(), "updated_at" / DecimalAdapter()
)


# ## ANSWER
#
# Here's the [Flux Rust structure]
# (https://github.com/blockworks-foundation/solana-flux-aggregator/blob/master/program/src/state.rs):
# ```
# #[derive(Clone, Debug, BorshSerialize, BorshDeserialize, BorshSchema, Default, PartialEq)]
# pub struct Answer {
#     pub round_id: u64,
#     pub median: u64,
#     pub created_at: u64,
#     pub updated_at: u64,
# }
# ```


ANSWER = construct.Struct(
    "round_id" / DecimalAdapter(),
    "median" / DecimalAdapter(),
    "created_at" / DatetimeAdapter(),
    "updated_at" / DatetimeAdapter(),
)

# ## AGGREGATOR
#
# Here's the [Flux Rust structure]
# (https://github.com/blockworks-foundation/solana-flux-aggregator/blob/master/program/src/state.rs):
# ```
# #[derive(Clone, Debug, BorshSerialize, BorshDeserialize, BorshSchema, Default, PartialEq)]
# pub struct Aggregator {
#     pub config: AggregatorConfig,
#     /// is initialized
#     pub is_initialized: bool,
#     /// authority
#     pub owner: PublicKey,
#     /// current round accepting oracle submissions
#     pub round: Round,
#     pub round_submissions: PublicKey, // has_one: Submissions
#     /// the latest answer resolved
#     pub answer: Answer,
#     pub answer_submissions: PublicKey, // has_one: Submissions
# }
# ```


AGGREGATOR = construct.Struct(
    "config" / AGGREGATOR_CONFIG,
    "initialized" / DecimalAdapter(1),
    "owner" / PublicKeyAdapter(),
    "round" / ROUND,
    "round_submissions" / PublicKeyAdapter(),
    "answer" / ANSWER,
    "answer_submissions" / PublicKeyAdapter(),
)
