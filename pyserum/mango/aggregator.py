import datetime
import logging
from decimal import Decimal

import mango_helpers
from solana.publickey import PublicKey
from solana.rpc.api import Client

from .._layouts.aggregator import AGGREGATOR, AGGREGATOR_CONFIG, ANSWER, ROUND
from ..account_info import AccountInfo
from ..addressable_account import AddressableAccount
from ..enums import Version


class AggregatorConfig:
    def __init__(
        self,
        version: Version,
        description: str,
        decimals: Decimal,
        restart_delay: Decimal,
        max_submissions: Decimal,
        min_submissions: Decimal,
        reward_amount: Decimal,
        reward_token_account: PublicKey,
    ):
        self.logger: logging.Logger = logging.getLogger(self.__class__.__name__)
        self.version: Version = version
        self.description: str = description
        self.decimals: Decimal = decimals
        self.restart_delay: Decimal = restart_delay
        self.max_submissions: Decimal = max_submissions
        self.min_submissions: Decimal = min_submissions
        self.reward_amount: Decimal = reward_amount
        self.reward_token_account: PublicKey = reward_token_account

    @staticmethod
    def from_layout(layout: AGGREGATOR_CONFIG) -> "AggregatorConfig":
        return AggregatorConfig(
            Version.UNSPECIFIED,
            layout.description,
            layout.decimals,
            layout.restart_delay,
            layout.max_submissions,
            layout.min_submissions,
            layout.reward_amount,
            layout.reward_token_account,
        )

    def __str__(self) -> str:
        return (
            f"« AggregatorConfig: '{self.description}', "
            f"Decimals: {self.decimals} [restart delay: {self.restart_delay}], "
            f"Max: {self.max_submissions}, Min: {self.min_submissions}, "
            f"Reward: {self.reward_amount}, Reward Account: {self.reward_token_account} »"
        )

    def __repr__(self) -> str:
        return f"{self}"


# # 🥭 Round class
#


class Round:
    def __init__(
        self, version: Version, entity_id: Decimal, created_at: datetime.datetime, updated_at: datetime.datetime
    ):
        self.logger: logging.Logger = logging.getLogger(self.__class__.__name__)
        self.version: Version = version
        self.entity_id: Decimal = entity_id
        self.created_at: datetime.datetime = created_at
        self.updated_at: datetime.datetime = updated_at

    @staticmethod
    def from_layout(layout: ROUND) -> "Round":
        return Round(Version.UNSPECIFIED, layout.entity_id, layout.created_at, layout.updated_at)

    def __str__(self) -> str:
        return f"« Round[{self.entity_id}], Created: {self.updated_at}, Updated: {self.updated_at} »"

    def __repr__(self) -> str:
        return f"{self}"


# # 🥭 Answer class
#


class Answer:
    def __init__(
        self,
        version: Version,
        round_id: Decimal,
        median: Decimal,
        created_at: datetime.datetime,
        updated_at: datetime.datetime,
    ):
        self.logger: logging.Logger = logging.getLogger(self.__class__.__name__)
        self.version: Version = version
        self.round_id: Decimal = round_id
        self.median: Decimal = median
        self.created_at: datetime.datetime = created_at
        self.updated_at: datetime.datetime = updated_at

    @staticmethod
    def from_layout(layout: ANSWER) -> "Answer":
        return Answer(Version.UNSPECIFIED, layout.round_id, layout.median, layout.created_at, layout.updated_at)

    def __str__(self) -> str:
        return (
            f"« Answer: Round[{self.round_id}], "
            f"Median: {self.median:,.8f}, "
            f"Created: {self.updated_at}, Updated: {self.updated_at} »"
        )

    def __repr__(self) -> str:
        return f"{self}"


# # 🥭 Aggregator class
#


class Aggregator(AddressableAccount):
    def __init__(
        self,
        conn: Client,
        account_info: AccountInfo,
        version: Version,
        config: AggregatorConfig,
        initialized: bool,
        name: str,
        owner: PublicKey,
        round_: Round,
        round_submissions: PublicKey,
        answer: Answer,
        answer_submissions: PublicKey,
    ):
        super().__init__(account_info)
        self.conn: Client = conn
        self.version: Version = version
        self.config: AggregatorConfig = config
        self.initialized: bool = initialized
        self.name: str = name
        self.owner: PublicKey = owner
        self.round: Round = round_
        self.round_submissions: PublicKey = round_submissions
        self.answer: Answer = answer
        self.answer_submissions: PublicKey = answer_submissions

    @property
    def price(self) -> Decimal:
        return self.answer.median / (10 ** self.config.decimals)

    @staticmethod
    def from_layout(conn: Client, layout: AGGREGATOR, account_info: AccountInfo, name: str) -> "Aggregator":
        config = AggregatorConfig.from_layout(layout.config)
        initialized = bool(layout.initialized)
        round_ = Round.from_layout(layout.round)
        answer = Answer.from_layout(layout.answer)

        return Aggregator(
            conn=conn,
            account_info=account_info,
            version=Version.UNSPECIFIED,
            config=config,
            initialized=initialized,
            name=name,
            owner=layout.owner,
            round_=round_,
            round_submissions=layout.round_submissions,
            answer=answer,
            answer_submissions=layout.answer_submissions,
        )

    @staticmethod
    def parse(conn: Client, account_info: AccountInfo) -> "Aggregator":
        data = account_info.data
        if len(data) != AGGREGATOR.sizeof():
            raise Exception(f"Data length ({len(data)}) does not match expected size ({AGGREGATOR.sizeof()})")

        name = mango_helpers.lookup_oracle_name(account_info.address)
        layout = AGGREGATOR.parse(data)
        return Aggregator.from_layout(conn=conn, layout=layout, account_info=account_info, name=name)

    @staticmethod
    def load(conn: Client, account_address: PublicKey):
        account_info = AccountInfo.load(conn, account_address)
        if account_info is None:
            raise Exception(f"Aggregator account not found at address '{account_address}'")
        return Aggregator.parse(conn=conn, account_info=account_info)

    def __str__(self) -> str:
        return f"""
« Aggregator '{self.name}' [{self.version}]:
    Config: {self.config}
    Initialized: {self.initialized}
    Owner: {self.owner}
    Round: {self.round}
    Round Submissions: {self.round_submissions}
    Answer: {self.answer}
    Answer Submissions: {self.answer_submissions}
»
"""
