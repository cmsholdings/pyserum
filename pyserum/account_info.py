"""Common format for responses involving accounts from solana."""
import logging
import time
import typing
from decimal import Decimal

from solana.publickey import PublicKey
from solana.rpc.api import Client
from solana.rpc.commitment import Recent
from solana.rpc.types import Commitment, RPCError, RPCMethod, RPCResponse

from .utils import decode_binary, encode_binary


class AccountInfo:
    """AccountInfo class."""

    def __init__(
        self,
        address: PublicKey,
        executable: bool,
        lamports: Decimal,
        owner: PublicKey,
        rent_epoch: Decimal,
        data: bytes,
    ):
        self.logger: logging.Logger = logging.getLogger(self.__class__.__name__)
        self.address: PublicKey = address
        self.executable: bool = executable
        self.lamports: Decimal = lamports
        self.owner: PublicKey = owner
        self.rent_epoch: Decimal = rent_epoch
        self.data: bytes = data

    def encoded_data(self) -> typing.List:
        return encode_binary(self.data)

    def __str__(self) -> str:
        return f"""« AccountInfo [{self.address}]:
    Owner: {self.owner}
    Executable: {self.executable}
    Lamports: {self.lamports}
    Rent Epoch: {self.rent_epoch}
»"""

    def __repr__(self) -> str:
        return f"{self}"

    @staticmethod
    def load(conn: Client, address: PublicKey, commitment: Commitment = Recent) -> typing.Optional["AccountInfo"]:
        response: RPCResponse = conn.get_account_info(address, commitment=commitment)
        if response.result["value"] is None:
            return None
        return AccountInfo.from_response(response=response, address=address)

    @staticmethod
    def load_multiple(
        conn: Client,
        addresses: typing.List[PublicKey],
        chunk_size: int = 100,
        sleep_between_calls: float = 0.0,
        commitment: Commitment = Recent,
    ) -> typing.List["AccountInfo"]:
        # This is a tricky one to get right.
        # Some errors this can generate:
        #  413 Client Error: Payload Too Large for url
        #  Error response from server: 'Too many inputs provided; max 100', code: -32602
        address_strings: typing.List[str] = list(map(PublicKey.__str__, addresses))
        multiple: typing.List[AccountInfo] = []
        chunks = AccountInfo._split_list_into_chunks(address_strings, chunk_size)
        for counter, chunk in enumerate(chunks):
            # pylint: disable=protected-access
            response = conn._provider.make_request(
                RPCMethod("getMultipleAccounts"), [*chunk], {"commitment": commitment, "encoding": "base64"}
            )
            if "error" in response:
                if response["error"] is str:
                    message: str = typing.cast(str, response["error"])
                    code: int = -1
                else:
                    error: RPCError = typing.cast(RPCError, response["error"])
                    message = error["message"]
                    code = error["code"]
                raise Exception(f"Error response from server for getMultipleAccounts: '{message}', code: {code}")

            response_value_list = zip(response["result"]["value"], addresses)
            multiple += list(map(lambda pair: AccountInfo.from_response_values(pair[0], pair[1]), response_value_list))
            if (sleep_between_calls > 0.0) and (counter < (len(chunks) - 1)):
                time.sleep(sleep_between_calls)

        return multiple

    @staticmethod
    def from_response_values(response_values: typing.Dict[str, typing.Any], address: PublicKey) -> "AccountInfo":
        """Parse the inner elements of a Solana RPC response into an AccountInfo object."""
        executable = bool(response_values["executable"])
        lamports = Decimal(response_values["lamports"])
        owner = PublicKey(response_values["owner"])
        rent_epoch = Decimal(response_values["rentEpoch"])
        data = decode_binary(response_values["data"])
        return AccountInfo(address, executable, lamports, owner, rent_epoch, data)

    @staticmethod
    def from_response(response: RPCResponse, address: PublicKey) -> "AccountInfo":
        """Parse a bare RPC response and map it into an AccountInfo object."""
        return AccountInfo.from_response_values(response["result"]["value"], address)

    @staticmethod
    def _split_list_into_chunks(to_chunk: typing.List, chunk_size: int = 100) -> typing.List[typing.List]:
        chunks = []
        start = 0
        while start < len(to_chunk):
            chunk = to_chunk[start : start + chunk_size]
            chunks += [chunk]
            start += chunk_size
        return chunks
