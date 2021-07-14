import json
import pytest
from solana.account import Account
from solana.publickey import PublicKey
from solana.rpc.api import Client

from pyserum.connection import conn


@pytest.mark.integration
@pytest.fixture(scope="session")
def stubbed_dex_program_pk() -> PublicKey:
    """Bootstrapped dex program id."""
    with open("data-vol/dex_program_id") as dex_program_id_file:
        return PublicKey(dex_program_id_file.read())


@pytest.mark.integration
@pytest.fixture(scope="session")
def stubbed_payer() -> Account:
    """Bootstrapped payer account."""
    with open("data-vol/user_account.json") as user_account_file:
        return Account(json.load(user_account_file)[:32])


@pytest.mark.integration
@pytest.fixture(scope="session")
def stubbed_base_mint() -> Account:
    """Bootstrapped base mint account."""
    with open("data-vol/coin_mint.json") as coin_mint_file:
        return Account(json.load(coin_mint_file)[:32])


@pytest.mark.integration
@pytest.fixture(scope="session")
def stubbed_quote_mint() -> Account:
    """Bootstrapped quote mint account."""
    with open("data-vol/pc_mint.json") as pc_mint_file:
        return Account(json.load(pc_mint_file)[:32])


@pytest.mark.integration
@pytest.fixture(scope="session")
def stubbed_market_pk() -> PublicKey:
    """Public key of the bootstrapped market."""
    with open("data-vol/market_addr") as market_addr_file:
        return PublicKey(market_addr_file.read())


@pytest.mark.integration
@pytest.fixture(scope="session")
def stubbed_req_q_pk() -> PublicKey:
    """Public key of the bootstrapped request queue."""
    with open("data-vol/req_q_addr") as read_q_addr_file:
        return PublicKey(read_q_addr_file.read())


@pytest.mark.integration
@pytest.fixture(scope="session")
def stubbed_event_q_pk() -> PublicKey:
    """Public key of the bootstrapped request queue."""
    with open("data-vol/event_q_addr") as event_q_addr_file:
        return PublicKey(event_q_addr_file.read())


@pytest.mark.integration
@pytest.fixture(scope="session")
def stubbed_bids_pk() -> PublicKey:
    """Public key of the bootstrapped bids book."""
    with open("data-vol/bids_addr") as bids_addr_file:
        return PublicKey(bids_addr_file.read())


@pytest.mark.integration
@pytest.fixture(scope="session")
def stubbed_asks_pk() -> PublicKey:
    """Public key of the bootstrapped asks book."""
    with open("data-vol/asks_addr") as asks_addr_file:
        return PublicKey(asks_addr_file.read())


@pytest.mark.integration
@pytest.fixture(scope="session")
def stubbed_base_vault_pk() -> PublicKey:
    """Public key of the base vault account."""
    with open("data-vol/coin_vault_addr") as coin_vault_addr_file:
        return PublicKey(coin_vault_addr_file.read())


@pytest.mark.integration
@pytest.fixture(scope="session")
def stubbed_quote_vault_pk() -> PublicKey:
    """Public key of the quote vault account."""
    with open("data-vol/pc_vault_addr") as pc_vault_addr_file:
        return PublicKey(pc_vault_addr_file.read())


@pytest.mark.integration
@pytest.fixture(scope="session")
def stubbed_vault_signer_pk() -> PublicKey:
    """Public key of the bootstrapped vault signer."""
    with open("data-vol/vault_signer_key_addr") as vault_signer_key_addr_file:
        return PublicKey(vault_signer_key_addr_file.read())


@pytest.mark.integration
@pytest.fixture(scope="session")
def stubbed_vault_signer_pk() -> PublicKey:
    """Public key of the bootstrapped vault signer."""
    with open("data-vol/vault_signer_key_addr") as vault_signer_key_addr_file:
        return PublicKey(vault_signer_key_addr_file.read())


@pytest.mark.integration
@pytest.fixture(scope="session")
def http_client() -> Client:
    """Solana http client."""
    cc = conn("http://localhost:8899")  # pylint: disable=invalid-name
    if not cc.is_connected():
        raise Exception("Could not connect to local node. Please run `make int-tests` to run integration tests.")
    return cc
