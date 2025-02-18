# Copyright (c) Aptos
# SPDX-License-Identifier: Apache-2.0
# based on:
# > https://github.com/aptos-labs/aptos-core/tree/main/ecosystem/python/sdk

import json

import click

from aptos_sdk.account import Account
from aptos_sdk.account_address import AccountAddress
from aptos_sdk.client import FaucetClient, RestClient
from common import FAUCET_URL, NODE_URL


@click.command()
@click.option("--gen_acct", flag_value=True, help="generate Aptos Account")
@click.option("--get_faucet", help="--get faucet [acct]")
@click.option("--priv", help="privkey in hex format")
@click.option(
    "--create_collection",
    help='collection informations. Example: \'["test", "hello", "www.google.com", 18446744073709551615]\'',
)
@click.option("--create_token", help='token informations: Example: \'["test_cc", "Alice simple token", "Alice simple token", 1, "https://aptos.dev/img/nyan.jpeg"]\''
)
@click.option("--create_tokens", help="token informations: \'[collection_name, mainifest_url, number, suffix, token_name_prefix]\'")
@click.option("--get_collection", help="get collection: ")
@click.option("--get_token", help="get token: ")
@click.option("--transfer_to", help="transfer token to someone")
@click.option("--get_balance", help="get balance: ")
def main(
    gen_acct,
    get_faucet,
    priv,
    create_collection,
    create_token,
    create_tokens,
    get_collection,
    get_token,
    transfer_to,
    get_balance,
):
    rest_client = RestClient(NODE_URL)
    faucet_client = FaucetClient(FAUCET_URL, rest_client)

    if gen_acct == True:
        #:!:>section gen acct
        user = Account.generate()
        print("\n=== Addresses ===")
        print(f"User Addr: {user.address()}")
        print(f"User Priv: {user.private_key.hex()}")
        # <:!:section gen acct
    if get_faucet != None:
        #:!:>section get faucet
        faucet_client.fund_account(get_faucet, 100_000_000)

        print("\n=== Initial Coin Balances ===")
        print(f"User: {rest_client.account_balance(get_faucet)}")
        # <:!:section get faucet

    if create_collection != None:
        #:!:>section create collection
        payload = json.loads(create_collection)
        acct = Account.load_key(priv)
        txn_hash = rest_client.create_collection(
            acct, payload[0], payload[1], payload[2], payload[3]
        )
        #  acct, collection_name, description, url
        rest_client.wait_for_transaction(txn_hash)
        print("\n=== Creating Collection and Token ===")

        collection_data = rest_client.get_collection(acct.address(), payload[0])
        print(
            f"User's collection: {json.dumps(collection_data, indent=4, sort_keys=True)}"
        )
        # <:!:section create collection

    if create_token != None:
        #:!:>section create token
        acct = Account.load_key(priv)
        payload = json.loads(create_token)
        #     # see in:
        # > https://github.com/aptos-labs/aptos-core/blob/main/aptos-move/framework/aptos-token/sources/token.move
        collection_name = payload[0]
        token_name =  payload[1]
        token_description =  payload[2]
        balance = payload[3]
        uri =  payload[4]
        txn_hash = rest_client.create_token(
        acct,
        collection_name,
        token_name,
        token_description,
        balance,
        uri,
        0,
        )  # <:!:section_5
        rest_client.wait_for_transaction(txn_hash)

        # public entry fun create_token_script(
        #     account: &signer,
        #     collection: String,
        #     name: String,
        #     description: String,
        #     balance: u64,
        #     maximum: u64,
        #     uri: String,
        #     royalty_payee_address: address,
        #     royalty_points_denominator: u64,
        #     royalty_points_numerator: u64,
        #     mutate_setting: vector<bool>,
        #     property_keys: vector<String>,
        #     property_values: vector<vector<u8>>,
        #     property_types: vector<String>
        # )
        # Example:
        # {acct, collection_name,  "Alice's simple token", 1, "https://aptos.dev/img/nyan.jpeg", 0}
        rest_client.wait_for_transaction(txn_hash)

        token_data = rest_client.get_token_data(
            acct.address(), collection_name, token_name, 0
        )
        print(f"User's token data: {json.dumps(token_data, indent=4, sort_keys=True)}")
        #:!:>section create token
   
    if get_collection != None:
        acct = Account.load_key(priv)
        collection_name = get_collection
        collection_data = rest_client.get_collection(acct.address(), collection_name)
        print(
            f"Your collection: {json.dumps(collection_data, indent=4, sort_keys=True)}"
        )
    if get_token != None:
        acct = Account.load_key(priv)
        collection_name = get_collection
        token_name = get_token
        property_version = 0
        token_data = rest_client.get_token_data(
            acct.address(), collection_name, token_name, property_version
        )
        print(f"User's token data: {json.dumps(token_data, indent=4, sort_keys=True)}")
    if transfer_to != None:
        acct = Account.load_key(priv)
        collection_name = get_collection
        token_name = get_token
        property_version = 0
        amount = 1
        txn_hash = rest_client.offer_token(
            acct,
            AccountAddress.from_hex(transfer_to),
            acct.address(),
            collection_name,
            token_name,
            property_version,
            amount,
        )
        rest_client.wait_for_transaction(txn_hash)
        print(f"txn_hash: {txn_hash}")
    if get_balance != None:
        addr = AccountAddress.from_hex(get_balance)
        collection_name = get_collection
        token_name = get_token
        property_version = 0
        balance = rest_client.get_token_balance(
            addr, addr, collection_name, token_name, property_version
        )
        print(f"User's token balance: {balance}")

    # ↑bounty price => $ 200↑

    # ↓bounty price => $ 200↓
    
    # requirement: Add the car link of Arweave/IPFS
    # mint Tokens
    # Example:
    # '[collection_name, "https://arweave.net/dexHfE8kFm0cdFEXiCNCRsdeROPfm9vlbKX91_j05l4/", 5, ".jpeg", "leeduckgo avatar"]'
    if create_tokens != None:
        # Token standard: https://aptos.dev/concepts/coin-and-token/aptos-token/#storing-metadata-off-chain
        # {
        #   "image": "https://www.arweave.net/abcd5678?ext=png",
        #   "animation_url": "https://www.arweave.net/efgh1234?ext=mp4",
        #   "external_url": "https://solflare.com"
        # }
        acct = Account.load_key(priv)
        payload = json.loads(create_tokens)
        # '[collection_name, mainifest_url, number, suffix, token_name_prefix]\'
        collection_name = payload[0]
        mainifest_url = payload[1]
        number = payload[2]
        suffix = payload[3]
        token_name_prefix= payload[4]
        for i in range(0, number):
            uri = mainifest_url + str(i) + suffix
            # uri = json.dumps({"image": image_url})
            token_name = token_name_prefix + " # " + str(i)

             # {acct, collection_name,  "Alice's simple token", 1, "https://aptos.dev/img/nyan.jpeg", 0}
            txn_hash = rest_client.create_token(
                acct,
                collection_name,
                token_name,
                token_name,
                1,
                uri,
                0
            )
            rest_client.wait_for_transaction(txn_hash)
            token_data = rest_client.get_token_data(
            acct.address(), collection_name, token_name, 0
            )
            print(f"User's token data: {json.dumps(token_data, indent=4, sort_keys=True)}")


if __name__ == "__main__":
    main()
#     #:!:>section_1
#     rest_client = RestClient(NODE_URL)
#     faucet_client = FaucetClient(FAUCET_URL, rest_client)  # <:!:section_1

#     #:!:>section_2
#     alice = Account.generate()
#     bob = Account.generate()  # <:!:section_2

#     collection_name = "Alice's"
#     token_name = "Alice's first token"
#     property_version = 0

#     print("\n=== Addresses ===")
#     print(f"Alice: {alice.address()}")
#     print(f"Bob: {bob.address()}")

#     #:!:>section_3
#     faucet_client.fund_account(alice.address(), 100_000_000)
#     faucet_client.fund_account(bob.address(), 100_000_000)  # <:!:section_3

#     print("\n=== Initial Coin Balances ===")
#     print(f"Alice: {rest_client.account_balance(alice.address())}")
#     print(f"Bob: {rest_client.account_balance(bob.address())}")

#     print("\n=== Creating Collection and Token ===")

#     #:!:>section_4
#     txn_hash = rest_client.create_collection(
#         alice, collection_name, "Alice's simple collection", "https://aptos.dev"
#     )  # <:!:section_4
#     rest_client.wait_for_transaction(txn_hash)

#     #:!:>section_5
#     # see in:
#     # > https://github.com/aptos-labs/aptos-core/blob/main/aptos-move/framework/aptos-token/sources/token.move
#     txn_hash = rest_client.create_token(
#         alice,
#         collection_name,
#         token_name,
#         "Alice's simple token",
#         1,
#         "https://aptos.dev/img/nyan.jpeg",
#         0,
#     )  # <:!:section_5
#     rest_client.wait_for_transaction(txn_hash)

#     txn_hash = rest_client.create_token(
#     alice,
#     collection_name,
#     "Alice's second token",
#     "Alice's simple token*2",
#     1,
#     "https://baidu.com",
#     0,
# )  # <:!:section_5
#     rest_client.wait_for_transaction(txn_hash)

#     #:!:>section_6
#     collection_data = rest_client.get_collection(alice.address(), collection_name)
#     print(
#         f"Alice's collection: {json.dumps(collection_data, indent=4, sort_keys=True)}"
#     )  # <:!:section_6
#     #:!:>section_7
#     balance = rest_client.get_token_balance(
#         alice.address(), alice.address(), collection_name, token_name, property_version
#     )
#     print(f"Alice's token balance: {balance}")  # <:!:section_7
#     #:!:>section_8
#     token_data = rest_client.get_token_data(
#         alice.address(), collection_name, token_name, property_version
#     )
#     print(
#         f"Alice's token data: {json.dumps(token_data, indent=4, sort_keys=True)}"
#     )  # <:!:section_8

#     print("\n=== Transferring the token to Bob ===")
#     #:!:>section_9
#     txn_hash = rest_client.offer_token(
#         alice,
#         bob.address(),
#         alice.address(),
#         collection_name,
#         token_name,
#         property_version,
#         1,
#     )  # <:!:section_9
#     rest_client.wait_for_transaction(txn_hash)

#     #:!:>section_10
#     txn_hash = rest_client.claim_token(
#         bob,
#         alice.address(),
#         alice.address(),
#         collection_name,
#         token_name,
#         property_version,
#     )  # <:!:section_10
#     rest_client.wait_for_transaction(txn_hash)

#     balance = rest_client.get_token_balance(
#         alice.address(), alice.address(), collection_name, token_name, property_version
#     )
#     print(f"Alice's token balance: {balance}")
#     balance = rest_client.get_token_balance(
#         bob.address(), alice.address(), collection_name, token_name, property_version
#     )
#     print(f"Bob's token balance: {balance}")

#     print("\n=== Transferring the token back to Alice using MultiAgent ===")
#     #:!:>section_11
#     txn_hash = rest_client.direct_transfer_token(
#         bob, alice, alice.address(), collection_name, token_name, 0, 1
#     )  # <:!:section_11
#     rest_client.wait_for_transaction(txn_hash)

#     balance = rest_client.get_token_balance(
#         alice.address(), alice.address(), collection_name, token_name, property_version
#     )
#     print(f"Alice's token balance: {balance}")
#     balance = rest_client.get_token_balance(
#         bob.address(), alice.address(), collection_name, token_name, property_version
#     )
#     print(f"Bob's token balance: {balance}")

#     rest_client.close()
