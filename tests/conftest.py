import pytest
from brownie import network, accounts, MockERC20
from web3 import Web3

LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["development", "ganache"]
INITIAL_SUPPLY = Web3.to_wei(1000, "ether")

@pytest.fixture
def amount_staked():
    return Web3.to_wei(1, "ether")

@pytest.fixture
def get_account():
    return accounts[0]

@pytest.fixture
def deploy_mock_erc20():
    account = get_account()
    mock_erc20 = MockERC20.deploy(INITIAL_SUPPLY, {"from": account})
    return mock_erc20
