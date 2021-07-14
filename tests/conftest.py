from typing import Dict
import json
import pytest
from solana.account import Account
from solana.publickey import PublicKey
from solana.rpc.api import Client

from pyserum.connection import conn


@pytest.mark.integration
@pytest.fixture(scope="session")
def __bs_params() -> Dict[str, str]:
    params = {}
    with open("tests/crank.log") as crank_log:
        for line in crank_log.readlines():
            if ":" not in line:
                continue
            key, val = line.strip().replace(",", "").split(": ")
            assert key, "key must not be None"
            assert val, "val must not be None"
            params[key] = val
    return params


def __bootstrap_account(pubkey: str, secretkey: str) -> Account:
    secret = [int(b) for b in secretkey[1:-1].split(" ")]
    account = Account(secret)
    assert str(account.public_key()) == pubkey, "account must map to provided public key"
    return account


@pytest.mark.integration
@pytest.fixture(scope="session")
def stubbed_dex_program_pk(__bs_params) -> PublicKey:
    """Bootstrapped dex program id."""
    with open("data-vol/dex_program_id") as dex_program_id_file:
        return PublicKey(dex_program_id_file.read())


@pytest.mark.integration
@pytest.fixture(scope="session")
def stubbed_payer(__bs_params) -> Account:
    """Bootstrapped payer account."""
    return Account(json.load(open("data-vol/user_account.json").read())[:32])


@pytest.mark.integration
@pytest.fixture(scope="session")
def stubbed_base_mint(__bs_params) -> Account:
    """Bootstrapped base mint account."""
    return Account(json.load(open("data-vol/coin_mint.json").read())[:32])


@pytest.mark.integration
@pytest.fixture(scope="session")
def stubbed_quote_mint(__bs_params) -> Account:
    """Bootstrapped quote mint account."""
    return Account(json.load(open("data-vol/pc_mint.json").read())[:32])


@pytest.mark.integration
@pytest.fixture(scope="session")
def stubbed_base_wallet(__bs_params) -> Account:
    """Bootstrapped base mint account."""
    return __bootstrap_account(__bs_params["coin_wallet"], __bs_params["coin_wallet_secret"])


@pytest.mark.integration
@pytest.fixture(scope="session")
def stubbed_quote_wallet(__bs_params) -> Account:
    """Bootstrapped quote mint account."""
    return __bootstrap_account(__bs_params["pc_wallet"], __bs_params["pc_wallet_secret"])


@pytest.mark.integration
@pytest.fixture(scope="session")
def stubbed_market_pk(__bs_params) -> PublicKey:
    """Public key of the bootstrapped market."""
    return PublicKey(open("data-vol/market_addr").read())


@pytest.mark.integration
@pytest.fixture(scope="session")
def stubbed_req_q_pk(__bs_params) -> PublicKey:
    """Public key of the bootstrapped request queue."""
    return Account(open("data-vol/req_q_addr").read())


@pytest.mark.integration
@pytest.fixture(scope="session")
def stubbed_event_q_pk(__bs_params) -> PublicKey:
    """Public key of the bootstrapped request queue."""
    return PublicKey(open("data-vol/event_q_addr").read())


@pytest.mark.integration
@pytest.fixture(scope="session")
def stubbed_bids_pk(__bs_params) -> PublicKey:
    """Public key of the bootstrapped bids book."""
    return PublicKey(open("data-vol/bids_addr").read())


@pytest.mark.integration
@pytest.fixture(scope="session")
def stubbed_asks_pk(__bs_params) -> PublicKey:
    """Public key of the bootstrapped asks book."""
    return PublicKey(open("data-vol/asks_addr").read())


@pytest.mark.integration
@pytest.fixture(scope="session")
def stubbed_base_vault_pk(__bs_params) -> PublicKey:
    """Public key of the base vault account."""
    return PublicKey(open("data-vol/coin_vault_addr").read())


@pytest.mark.integration
@pytest.fixture(scope="session")
def stubbed_quote_vault_pk(__bs_params) -> PublicKey:
    """Public key of the quote vault account."""
    return PublicKey(open("data-vol/pc_vault_addr").read())


@pytest.mark.integration
@pytest.fixture(scope="session")
def stubbed_vault_signer_pk(__bs_params) -> PublicKey:
    """Public key of the bootstrapped vault signer."""
    return PublicKey(open("data-vol/vault_signer_key_addr").read())


@pytest.mark.integration
@pytest.fixture(scope="session")
def stubbed_bid_account_pk(__bs_params) -> PublicKey:
    """Public key of the initial bid order account."""
    return PublicKey(__bs_params["bid_account"])


@pytest.mark.integration
@pytest.fixture(scope="session")
def stubbed_ask_account_pk(__bs_params) -> PublicKey:
    """Public key of the initial ask order account."""
    return PublicKey(__bs_params["ask_account"])


@pytest.mark.integration
@pytest.fixture(scope="session")
def http_client() -> Client:
    """Solana http client."""
    cc = conn("http://localhost:8899")  # pylint: disable=invalid-name
    if not cc.is_connected():
        raise Exception("Could not connect to local node. Please run `make int-tests` to run integration tests.")
    return cc
