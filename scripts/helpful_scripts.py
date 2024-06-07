from brownie import (
    accounts,
    network,
    config,
    Contract,
    MockV3Aggregator,
    MockDAI,
    MockWETH,
)
import eth_utils

LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["hardhat", "development", "ganache"]
INITIAL_PRICE_FEED_VALUE = 2000000000000000000000
DECIMALS = 18

contract_to_mock = {
    "eth_usd_price_feed": MockV3Aggregator,
    "dai_usd_price_feed": MockV3Aggregator,
    "fau_token": MockDAI,
    "weth_token": MockWETH,
    # Add other mocks here if necessary
}

def get_account(index=None, id=None):
    if index:
        return accounts[index]
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        return accounts[0]
    if id:
        return accounts.load(id)
    return accounts.add(config["wallets"]["from_key"])

def encode_function_data(initializer=None, *args):
    if len(args) == 0 or not initializer:
        return eth_utils.to_bytes(hexstr="0x")
    return initializer.encode_input(*args)

def upgrade(account, proxy, new_implementation_address, proxy_admin_contract=None, initializer=None, *args):
    transaction = None
    if proxy_admin_contract:
        if initializer:
            encoded_function_call = encode_function_data(initializer, *args)
            transaction = proxy_admin_contract.upgradeAndCall(
                proxy.address,
                new_implementation_address,
                encoded_function_call,
                {"from": account},
            )
        else:
            transaction = proxy_admin_contract.upgrade(
                proxy.address, new_implementation_address, {"from": account}
            )
    else:
        if initializer:
            encoded_function_call = encode_function_data(initializer, *args)
            transaction = proxy.upgradeToAndCall(
                new_implementation_address, encoded_function_call, {"from": account}
            )
        else:
            transaction = proxy.upgradeTo(new_implementation_address, {"from": account})
    return transaction

def get_contract(contract_name):
    contract_type = contract_to_mock[contract_name]
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        if len(contract_type) <= 0:
            deploy_mocks()
        contract = contract_type[-1]
    else:
        try:
            contract_address = config["networks"][network.show_active()][contract_name]
            contract = Contract.from_abi(
                contract_type._name, contract_address, contract_type.abi
            )
        except KeyError:
            print(f"{network.show_active()} address not found, perhaps you should add it to the config or deploy mocks?")
            print(f"brownie run scripts/deploy_mocks.py --network {network.show_active()}")
    return contract

def deploy_mocks(decimals=DECIMALS, initial_value=INITIAL_PRICE_FEED_VALUE):
    print(f"The active network is {network.show_active()}")
    print("Deploying Mocks...")
    account = get_account()
    print("Deploying Mock Price Feed...")
    mock_price_feed = MockV3Aggregator.deploy(
        decimals, initial_value, {"from": account}
    )
    print(f"Deployed to {mock_price_feed.address}")
    print("Deploying Mock DAI...")
    mock_dai = MockDAI.deploy({"from": account})
    print(f"Deployed to {mock_dai.address}")
    print("Deploying Mock WETH...")
    mock_weth = MockWETH.deploy({"from": account})
    print(f"Deployed to {mock_weth.address}")
    print("Mocks Deployed!")
