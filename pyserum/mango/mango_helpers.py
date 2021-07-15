import json
import os
import typing

from solana.publickey import PublicKey

cluster = os.environ.get("CLUSTER") or "mainnet-beta"

with open("ids.json") as json_file:
    MangoConstants = json.load(json_file)


def _lookup_name_by_address(address: PublicKey, collection: typing.Dict[str, str]) -> typing.Optional[str]:
    address_string = str(address)
    for stored_name, stored_address in collection.items():
        if stored_address == address_string:
            return stored_name
    return None


def lookup_oracle_name(token_address: PublicKey) -> str:
    return _lookup_name_by_address(token_address, MangoConstants[cluster]["oracles"]) or "« Unknown Oracle »"
