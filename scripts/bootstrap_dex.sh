#!/bin/bash
set -e
INSTALL_LOCATION=${INSTALL_LOCATION:-"/opt/src"}
DATA_LOCATION=${DATA_LOCATION:-"/data"}

# shellcheck disable=SC1091
source "${HOME}/.bash_profile"

# helper func to parse output from market listing
parse_market_list_result() {
    cat "${DATA_LOCATION}/list_market_result" | grep "$1" | sed s/"    $1: "//g | sed s/,//g >"${DATA_LOCATION}"/"${1}"_addr
}

solana-test-validator --ledger "${DATA_LOCATION}/ledger" &

if [ ! -f "${DATA_LOCATION}/.bootstrapped" ]; then
    # make the keys on the shared volume if it doesnt exist. since its dev print the seeds in a separate file
    for acct_name in user_account market_owner coin_mint pc_mint; do
        if [ ! -f "${DATA_LOCATION}/$acct_name.json" ]; then
            solana-keygen new --no-bip39-passphrase -o "${DATA_LOCATION}"/${acct_name}.json >"${DATA_LOCATION}"/${acct_name}.txt
        fi
    done

    solana config set --url "http://127.0.0.1:8899"
    solana config set -k "${DATA_LOCATION}/user_account.json"

    # give the test validator time to start
    sleep 2

    solana airdrop 10000

    solana deploy "${INSTALL_LOCATION}"/serum_dex.so --output json-compact | jq .programId -r >"${DATA_LOCATION}/dex_program_id"

    DEX_PROGRAM_ID=$(cat "${DATA_LOCATION}"/dex_program_id)
    echo DEX_PROGRAM_ID: "${DEX_PROGRAM_ID}"

    echo "Crank Genesis for coin mint.."
    crank localnet genesis --payer "${DATA_LOCATION}/user_account.json" --mint "${DATA_LOCATION}/coin_mint.json" --owner-pubkey "$(solana address -k "${DATA_LOCATION}"/user_account.json)" --decimals 6

    echo "Crank Genesis for pc mint.."
    crank localnet genesis --payer "${DATA_LOCATION}/user_account.json" --mint "${DATA_LOCATION}/pc_mint.json" --owner-pubkey "$(solana address -k "${DATA_LOCATION}"/user_account.json)" --decimals 6

    echo "Crank listing market.."
    crank localnet list-market "${DATA_LOCATION}"/user_account.json "${DEX_PROGRAM_ID}" --coin-mint "$(solana address -k "${DATA_LOCATION}"/coin_mint.json)" --pc-mint "$(solana address -k "${DATA_LOCATION}"/pc_mint.json)" >"${DATA_LOCATION}/list_market_result"

    echo "Crank mint coin wallet.."
    crank localnet mint --payer "${DATA_LOCATION}"/user_account.json --signer "${DATA_LOCATION}"/user_account.json --mint-pubkey "$(solana address -k "${DATA_LOCATION}/coin_mint.json")" --quantity 1000000000000000 >"${DATA_LOCATION}"/coin_wallet_output.txt

    echo "Crank mint pc wallet.."
    crank localnet mint --payer "${DATA_LOCATION}"/user_account.json --signer "${DATA_LOCATION}"/user_account.json --mint-pubkey "$(solana address -k "${DATA_LOCATION}/pc_mint.json")" --quantity 1000000000000000 >"${DATA_LOCATION}"/pc_wallet_output.txt

    for addr_name in market req_q event_q bids asks coin_vault pc_vault vault_signer_key; do
        parse_market_list_result ${addr_name}
    done

    echo "dex_program_id: ${DEX_PROGRAM_ID}" >>crank.log

    touch "${DATA_LOCATION}"/.bootstrapped
fi

tail -f "${DATA_LOCATION}"/crank.log
