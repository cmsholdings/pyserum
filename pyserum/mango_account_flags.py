import logging
import typing
from ._layouts import account_flags as layouts
from .enums import Version


class MangoAccountFlags:
    def __init__(self, version: Version, initialized: bool, group: bool, margin_account: bool, srm_account: bool):
        self.logger: logging.Logger = logging.getLogger(self.__class__.__name__)
        self.version: Version = version
        self.initialized = initialized
        self.group = group
        self.margin_account = margin_account
        self.srm_account = srm_account

    @staticmethod
    def from_layout(layout: layouts.MANGO_ACCOUNT_FLAGS) -> "MangoAccountFlags":
        return MangoAccountFlags(
            Version.UNSPECIFIED, layout.initialized, layout.group, layout.margin_account, layout.srm_account
        )

    def __str__(self) -> str:
        flags: typing.List[typing.Optional[str]] = []
        flags += ["initialized" if self.initialized else None]
        flags += ["group" if self.group else None]
        flags += ["margin_account" if self.margin_account else None]
        flags += ["srm_account" if self.srm_account else None]
        flag_text = " | ".join(flag for flag in flags if flag is not None) or "None"
        return f"« MangoAccountFlags: {flag_text} »"

    def __repr__(self) -> str:
        return f"{self}"
