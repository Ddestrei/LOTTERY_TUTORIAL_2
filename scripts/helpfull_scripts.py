from brownie import (
    network,
    accounts,
    config,
    MockV3Aggregator,
    VRFCoordinatorMock,
    LinkToken,
    Contract,
    interface,
)
from brownie.network import gas_price
from brownie.network.gas.strategies import LinearScalingStrategy

FORKED_LOCAL_ENVIROMWNTS = ["mainnet_fork"]
LOCAL_BLOCKCHAIN_ENVIROMENTS = ["development"]

gas_strategy = LinearScalingStrategy("1 gwei", "200 gwei", 1.125)
gas_price(gas_strategy)


def get_account(index=None, id=None):
    if index:
        return accounts[index]
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIROMENTS:
        return accounts[0]
    if id:
        return accounts.load(id)
    if network.show_active() in config["networks"]:
        return accounts.add(config["wallets"]["from_key"])
    


contract_to_mock = {
    "eth_usd_price_feed": MockV3Aggregator,
    "vrf_coordinator": VRFCoordinatorMock,
    "link_token": LinkToken,
}


def get_contract(contract_name):
    contract_type = contract_to_mock[contract_name]
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIROMENTS:
        if len(contract_type) <= 0:
            deploy_mocks()
        contract = contract_type[-1]
    else:
        contract_address = config["networks"][network.show_active()][contract_name]
        contract = Contract.from_abi(
            contract_type._name, contract_address, contract_type.abi
        )
    return contract


DECIMALS = 8
INITIAL_VALUE = 200000000000


def deploy_mocks():
    """
    Use this script if you want to deploy mocks to a testnet
    """
    print(f"The active network is {network.show_active()}")
    print("Deploying Mocks...")
    account = get_account()
    MockV3Aggregator.deploy(
        DECIMALS, INITIAL_VALUE, {"from": account, "gas_price": gas_strategy}
    )
    link_token = LinkToken.deploy({"from": account, "gas_price": gas_strategy})
    VRFCoordinatorMock.deploy(
        link_token.address, {"from": account, "gas_price": gas_strategy}
    )
    print("Mocks Deployed!")


def fund_with_link(
    contract_address, account=None, link_token=None, amount=100000000000000000
):
    account = account if account else get_account()
    link_token = link_token if link_token else get_contract("link_token")
    link_token_contracts = interface.LinkTokenInterface(link_token.address)
    tx = link_token_contracts.transfer(contract_address, amount, {"from": account})
    tx.wait(1)
    print("Fund contract!!!")
    return tx
