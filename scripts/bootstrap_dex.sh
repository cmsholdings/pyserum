#!/bin/bash
set -e
INSTALL_LOCATION=${INSTALL_LOCATION:-"/opt/src"}
DATA_LOCATION=${DATA_LOCATION:-"/data"}

# shellcheck disable=SC1091
source "${HOME}/.bash_profile"

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
    tail -F "${DATA_LOCATION}/ledger/validator.log"

    solana deploy "${INSTALL_LOCATION}"/serum_dex.so --output json-compact | jq .programId -r >"${DATA_LOCATION}/dex_program_id"

    DEX_PROGRAM_ID=$(cat "${DATA_LOCATION}"/dex_program_id)
    echo DEX_PROGRAM_ID: "${DEX_PROGRAM_ID}"

    crank localnet genesis --payer "${DATA_LOCATION}/user_account.json" --mint "${DATA_LOCATION}/coin_mint.json" --owner-pubkey "$(solana address -k "${DATA_LOCATION}"/user_account.json)" --decimals 6
    crank localnet genesis --payer "${DATA_LOCATION}/user_account.json" --mint "${DATA_LOCATION}/pc_mint.json" --owner-pubkey "$(solana address -k "${DATA_LOCATION}"/user_account.json)" --decimals 6

    crank localnet list-market "${DATA_LOCATION}"/user_account.json "${DEX_PROGRAM_ID}" --coin-mint "$(solana address -k "${DATA_LOCATION}"/coin_mint.json)" --pc-mint "$(solana address -k "${DATA_LOCATION}"/pc_mint.json)" >"${DATA_LOCATION}/list_market_result"

    crank localnet mint --payer "${DATA_LOCATION}"/user_account.json --signer "${DATA_LOCATION}"/user_account.json --mint-pubkey "$(solana address -k "${DATA_LOCATION}/coin_mint.json")" --quantity 1000000000000000 >"${DATA_LOCATION}"/coin_wallet_output.txt

    crank localnet mint --payer "${DATA_LOCATION}"/user_account.json --signer "${DATA_LOCATION}"/user_account.json --mint-pubkey "$(solana address -k "${DATA_LOCATION}/pc_mint.json")" --quantity 1000000000000000 >"${DATA_LOCATION}"/pc_wallet_output.txt

    # crank localnet print-event-queue "${DEX_PROGRAM_ID}" ""

    echo "dex_program_id: ${DEX_PROGRAM_ID}" >>crank.log
    mv crank.log tests/crank.log
    touch "${DATA_LOCATION}"/.bootstrapped
fi
tail -f tests/crank.log
