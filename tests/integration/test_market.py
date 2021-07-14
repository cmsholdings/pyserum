# pylint: disable=redefined-outer-name

import pytest
from solana.account import Account
from solana.publickey import PublicKey
from solana.rpc.api import Client
from solana.rpc.types import TxOpts
from spl.token.client import TokenAccountOpts
from solana.rpc.commitment import Commitment

from pyserum.enums import OrderType, Side
from pyserum.market import Market


@pytest.mark.integration
@pytest.fixture(scope="module")
def bootstrapped_market(http_client: Client, stubbed_market_pk: PublicKey, stubbed_dex_program_pk: PublicKey) -> Market:
    # request queue is deprecated and to-be removed
    return Market.load(http_client, stubbed_market_pk, stubbed_dex_program_pk, force_use_request_queue=False)


@pytest.mark.integration
@pytest.fixture(scope="module")
def base_owner_token(http_client: Client, stubbed_payer: Account, bootstrapped_market: Market) -> PublicKey:
    return PublicKey(
        http_client.get_token_accounts_by_owner(
            owner=stubbed_payer.public_key(), opts=TokenAccountOpts(mint=bootstrapped_market.state.base_mint())
        )["result"]["value"][0]["pubkey"]
    )


@pytest.mark.integration
@pytest.fixture(scope="module")
def quote_owner_token(http_client: Client, stubbed_payer: Account, bootstrapped_market: Market) -> PublicKey:

    return PublicKey(
        http_client.get_token_accounts_by_owner(
            owner=stubbed_payer.public_key(), opts=TokenAccountOpts(mint=bootstrapped_market.state.quote_mint())
        )["result"]["value"][0]["pubkey"]
    )


@pytest.mark.integration
def test_bootstrapped_market(
    bootstrapped_market: Market,
    stubbed_market_pk: PublicKey,
    stubbed_dex_program_pk: PublicKey,
    stubbed_base_mint: PublicKey,
    stubbed_quote_mint: PublicKey,
    stubbed_event_q_pk: PublicKey,
):
    assert isinstance(bootstrapped_market, Market)
    assert bootstrapped_market.state.public_key() == stubbed_market_pk
    assert bootstrapped_market.state.program_id() == stubbed_dex_program_pk
    assert bootstrapped_market.state.base_mint() == stubbed_base_mint.public_key()
    assert bootstrapped_market.state.quote_mint() == stubbed_quote_mint.public_key()
    assert bootstrapped_market.state.event_queue() == stubbed_event_q_pk


@pytest.mark.integration
def test_market_load_bid(bootstrapped_market: Market):
    # TODO: test for non-zero order case.
    bids = bootstrapped_market.load_bids()
    assert sum(1 for _ in bids) == 0


@pytest.mark.integration
def test_market_load_asks(bootstrapped_market: Market):
    # TODO: test for non-zero order case.
    asks = bootstrapped_market.load_asks()
    assert sum(1 for _ in asks) == 0


@pytest.mark.integration
def test_market_load_events(bootstrapped_market: Market):
    event_queue = bootstrapped_market.load_event_queue()
    assert len(event_queue) == 0


@pytest.mark.integration
def test_market_load_requests(bootstrapped_market: Market):
    request_queue = bootstrapped_market.load_request_queue()
    # 0 requests. this is no longer used.
    assert len(request_queue) == 0


@pytest.mark.integration
def test_match_order(
    http_client: Client,
    bootstrapped_market: Market,
    stubbed_payer: Account,
    base_owner_token: PublicKey,
    quote_owner_token: PublicKey,
):
    start_event_queue_size = len(bootstrapped_market.load_event_queue())
    print(base_owner_token)
    print(quote_owner_token)
    base_size = bootstrapped_market.state.base_size_number_to_lots(1)
    base_price = bootstrapped_market.state.price_number_to_lots(1)
    bootstrapped_market.place_order(
        payer=quote_owner_token,
        owner=stubbed_payer,
        order_type=OrderType.LIMIT,
        side=Side.BUY,
        limit_price=base_price,
        max_quantity=base_size,
        client_id=1,
        opts=TxOpts(preflight_commitment=Commitment("recent")),
    )
    bootstrapped_market.place_order(
        payer=base_owner_token,
        owner=stubbed_payer,
        order_type=OrderType.LIMIT,
        side=Side.SELL,
        limit_price=base_price,
        max_quantity=base_size,
        client_id=2,
        opts=TxOpts(preflight_commitment=Commitment("recent")),
    )

    bootstrapped_market.match_orders(stubbed_payer, 2, TxOpts(skip_confirmation=False))

    event_queue = bootstrapped_market.load_event_queue()

    # 3 events are added to queue; 2 fills, 1 out
    assert len(event_queue) == start_event_queue_size + 3

    # There should be no bid order.
    bids = bootstrapped_market.load_bids()
    assert sum(1 for _ in bids) == 0

    # There should be no ask order.
    asks = bootstrapped_market.load_asks()
    assert sum(1 for _ in asks) == 0


@pytest.mark.integration
def test_settle_fund(
    bootstrapped_market: Market, stubbed_payer: Account, base_owner_token: PublicKey, quote_owner_token: PublicKey
):
    open_order_accounts = bootstrapped_market.find_open_orders_accounts_for_owner(stubbed_payer.public_key())
    print(f"OpenOrders: {open_order_accounts}")

    with pytest.raises(ValueError):
        # Should not allow base_wallet to be base_vault
        bootstrapped_market.settle_funds(
            stubbed_payer,
            open_order_accounts[0],
            bootstrapped_market.state.base_vault(),
            quote_owner_token,
        )

    with pytest.raises(ValueError):
        # Should not allow quote_wallet to be wallet_vault
        bootstrapped_market.settle_funds(
            stubbed_payer,
            open_order_accounts[0],
            base_owner_token,
            bootstrapped_market.state.quote_vault(),
        )

    for open_order_account in open_order_accounts:
        assert "error" not in bootstrapped_market.settle_funds(
            stubbed_payer,
            open_order_account,
            base_owner_token,
            quote_owner_token,
            opts=TxOpts(skip_confirmation=False),
        )

    # TODO: Check account states after settling funds


@pytest.mark.integration
def test_order_placement_cancellation_cycle(
    bootstrapped_market: Market, stubbed_payer: Account, base_owner_token: PublicKey, quote_owner_token: PublicKey
):
    bootstrapped_market.place_order(
        payer=quote_owner_token,
        owner=stubbed_payer,
        side=Side.BUY,
        order_type=OrderType.LIMIT,
        limit_price=1000,
        max_quantity=3000,
        opts=TxOpts(skip_confirmation=False),
    )

    # There should be no bid order.
    bids = bootstrapped_market.load_bids()
    assert sum(1 for _ in bids) == 0

    # There should be no ask order.
    asks = bootstrapped_market.load_asks()
    assert sum(1 for _ in asks) == 0

    bootstrapped_market.place_order(
        payer=base_owner_token,
        owner=stubbed_payer,
        side=Side.SELL,
        order_type=OrderType.LIMIT,
        limit_price=1500,
        max_quantity=3000,
        opts=TxOpts(skip_confirmation=False),
    )

    # The two order shouldn't get executed since there is a price difference of 1
    bootstrapped_market.match_orders(
        stubbed_payer,
        2,
        opts=TxOpts(skip_confirmation=False),
    )

    # There should be 1 bid order that we sent earlier.
    bids = bootstrapped_market.load_bids()
    assert sum(1 for _ in bids) == 1

    # There should be 1 ask order that we sent earlier.
    asks = bootstrapped_market.load_asks()
    assert sum(1 for _ in asks) == 1

    for bid in bids:
        bootstrapped_market.cancel_order(stubbed_payer, bid, opts=TxOpts(skip_confirmation=False))

    bootstrapped_market.match_orders(stubbed_payer, 1, opts=TxOpts(skip_confirmation=False))

    # All bid order should have been cancelled.
    bids = bootstrapped_market.load_bids()
    assert sum(1 for _ in bids) == 0

    for ask in asks:
        bootstrapped_market.cancel_order(stubbed_payer, ask, opts=TxOpts(skip_confirmation=False))

    bootstrapped_market.match_orders(stubbed_payer, 1, opts=TxOpts(skip_confirmation=False))

    # All ask order should have been cancelled.
    asks = bootstrapped_market.load_asks()
    assert sum(1 for _ in asks) == 0
