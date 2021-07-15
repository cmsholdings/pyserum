import abc
import logging

from solana.publickey import PublicKey

from .account_info import AccountInfo


# # 🥭 AddressableAccount class
#
# Some of our most-used objects (like `Group` or `MarginAccount`) are accounts on Solana
# with packed data. When these are loaded, they're typically loaded by loading the
# `AccountInfo` and parsing it in an object-specific way.
#
# It's sometimes useful to be able to treat these in a common fashion so we use
# `AddressableAccount` as a way of sharing common features and providing a common base.


class AddressableAccount(metaclass=abc.ABCMeta):
    def __init__(self, account_info: AccountInfo):
        self.logger: logging.Logger = logging.getLogger(self.__class__.__name__)
        self.account_info = account_info

    @property
    def address(self) -> PublicKey:
        return self.account_info.address

    def __repr__(self) -> str:
        return f"{self}"
