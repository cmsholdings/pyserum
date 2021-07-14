#!/usr/bin/env bash

# script to install SOL and Serum Crank for Centos/Fedora/RHEL
# this aims to be cross-compatible with baremetal, WSL, and docker/podman

# version of sol bins to download
SOLANA_VERSION=${SOLANA_VERSION:-"v1.6.16"}

# version of serum to build
# issue: release has a bug, pull from master instead. ignoring for now..
#SERUM_VERSION=${SERUM_VERSION:-"v0.3.1"}

INSTALL_LOCATION=${INSTALL_LOCATION:-"/opt/src"}

dnf install -y epel-release
dnf update -y
dnf install -y \
    git \
    openssl-devel \
    llvm \
    net-tools \
    procps-ng \
    zlib-devel \
    clang \
    make \
    systemd-devel \
    curl \
    wget \
    jq \
    bzip2
dnf upgrade -y

curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
source "${HOME}"/.cargo/env

mkdir -p "${INSTALL_LOCATION}"

# we want to fail if for some reason this isnt a location
# shellcheck disable=SC2164
cd "${INSTALL_LOCATION}"
wget https://github.com/solana-labs/solana/releases/download/"${SOLANA_VERSION}"/solana-install-init-x86_64-unknown-linux-gnu

chmod +x solana-install-init-x86_64-unknown-linux-gnu
./solana-install-init-x86_64-unknown-linux-gnu stable

git clone https://github.com/project-serum/serum-dex.git
# grab path for sdk and solana
PATH=$PATH:${HOME}/.local/share/solana/install/active_release/bin/

# swap out the ancient version of bpf-rust to use up-to-date one
sed -ibak 's/version=v1.5/version=v1.13/g' "${HOME}/.local/share/solana/install/active_release/bin/sdk/bpf/scripts/install.sh"

# build the dex with the bpf-rust toolchain
cd "${INSTALL_LOCATION}/serum-dex/dex"
cargo-build-bpf

# build crank with the default non-bpf keychain
cd "${INSTALL_LOCATION}/serum-dex/dex/crank"
cargo build --release

cp -a "${INSTALL_LOCATION}/serum-dex/target/release/crank" /usr/local/bin
cp -a "${INSTALL_LOCATION}/serum-dex/dex/target/deploy/serum_dex.so" "${INSTALL_LOCATION}"

solana config set --url "http://127.0.0.1:8899"
