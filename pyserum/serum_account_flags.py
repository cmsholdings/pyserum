"""Serum-specific flags for a solana account."""
import logging
import typing

from ._layouts.account_flags import SERUM_ACCOUNT_FLAGS_LAYOUT
from .enums import Version


# pylint: disable=too-many-instance-attributes
class SerumAccountFlags:
    # pylint: disable=too-many-arguments
    def __init__(
        self,
        version: Version,
        initialized: bool,
        market: bool,
        open_orders: bool,
        request_queue: bool,
        event_queue: bool,
        bids: bool,
        asks: bool,
        disabled: bool,
    ):
        self.logger: logging.Logger = logging.getLogger(self.__class__.__name__)
        self.version: Version = version
        self.initialized: bool = initialized
        self.market: bool = market
        self.open_orders: bool = open_orders
        self.request_queue: bool = request_queue
        self.event_queue: bool = event_queue
        self.bids: bool = bids
        self.asks: bool = asks
        self.disabled: bool = disabled

    @staticmethod
    def from_layout(layout: SERUM_ACCOUNT_FLAGS_LAYOUT) -> "SerumAccountFlags":
        return SerumAccountFlags(
            Version.UNSPECIFIED,
            layout.initialized,
            layout.market,
            layout.open_orders,
            layout.request_queue,
            layout.event_queue,
            layout.bids,
            layout.asks,
            layout.disabled,
        )

    def __str__(self) -> str:
        flags: typing.List[typing.Optional[str]] = []
        flags += ["initialized" if self.initialized else None]
        flags += ["market" if self.market else None]
        flags += ["open_orders" if self.open_orders else None]
        flags += ["request_queue" if self.request_queue else None]
        flags += ["event_queue" if self.event_queue else None]
        flags += ["bids" if self.bids else None]
        flags += ["asks" if self.asks else None]
        flags += ["disabled" if self.disabled else None]
        flag_text = " | ".join(flag for flag in flags if flag is not None) or "None"
        return f"« SerumAccountFlags: {flag_text} »"

    def __repr__(self) -> str:
        return f"{self}"
