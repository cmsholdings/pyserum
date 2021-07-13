"""Serum specific enums."""

from enum import IntEnum


class Side(IntEnum):
    """Side of the orderbook to trade."""

    BUY = 0
    """"""
    SELL = 1
    """"""


class OrderType(IntEnum):
    """Type of order."""

    LIMIT = 0
    """"""
    IOC = 1
    """"""
    POST_ONLY = 2
    """"""


class SelfTradeBehavior(IntEnum):
    DECREMENT_TAKE = 0
    CANCEL_PROVIDE = 1
    ABORT_TRANSACTION = 2


class Version(IntEnum):
    UNSPECIFIED = 0
    V1 = 1
    V2 = 2
    V3 = 3
    V4 = 4
    V5 = 5
