from brownie import DappToken, TokenFarm, network, config
from scripts.helpful_scripts import get_account, get_contract
from web3 import Web3

# Use to_wei directly from the Web3 module
from web3.main import to_wei

# Define your constant using to_wei
KEPT_BALANCE = to_wei(100, "ether")


def deploy_token_farm_and_dapp_token():
    account = get_account()
    dapp_token = DappToken.deploy({"from": account})
    token_farm = TokenFarm.deploy(
        dapp_token.address,
        {"from": account},
        publish_source=config["networks"][network.show_active()]["verify"],
    )
    tx = dapp_token.transfer(
        token_farm.address,
        dapp_token.totalSupply() - KEPT_BALANCE,
        {"from": account},
    )
    tx.wait(1)
    fau_token = get_contract("fau_token")
    weth_token = get_contract("weth_token")
    dict_of_allowed_token={
        dapp_token:get_contract("dai_usd_price_feed"),
        fau_token:get_contract("dai_usd_price_feed"),
        weth_token:get_contract("eth_usd_price_feed"),

    }

    add_allowed_tokens(
        token_farm,
        dict_of_allowed_token,
        account,
    )
    
    return token_farm, dapp_token


def add_allowed_tokens(token_farm, dict_of_allowed_token, account):
    for token in dict_of_allowed_token:
        add_tx=token_farm.addAllowedTokens(token.address, {"from": account})
        add_tx.wait(1)
        set_tx = token_farm.setPriceFeedContract(
            token.address, dict_of_allowed_token[token], {"from": account}
        )
        set_tx.wait(1)
    return token_farm




def main():
    deploy_token_farm_and_dapp_token()