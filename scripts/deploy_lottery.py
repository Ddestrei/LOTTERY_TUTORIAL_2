from brownie import Lottery, network, config
from brownie.network import gas_price
from brownie.network.gas.strategies import LinearScalingStrategy
from scripts.helpfull_scripts import get_account, get_contract, fund_with_link
import time

gas_strategy = LinearScalingStrategy("60 gwei", "90 gwei", 1.125)
gas_price = gas_strategy


def deploy_lottery():
    account = get_account()
    lottery = Lottery.deploy(
        get_contract("eth_usd_price_feed").address,
        get_contract("vrf_coordinator").address,
        get_contract("link_token").address,
        config["networks"][network.show_active()]["fee"],
        config["networks"][network.show_active()]["keyhash"],
        {"from": account, "price": gas_strategy},
        publish_source=config["networks"][network.show_active()].get("verify", False),
    )
    print("Deployed lottery!!!")
    return lottery


def start_lottery():
    account = get_account()
    lottery = Lottery[-1]
    starting_tx = lottery.startLottery({"from": account})
    starting_tx.wait(1)
    print("The lottery is started!!!")


def enter_lottery():
    account = get_account()
    lottery = Lottery[-1]
    value = lottery.getEntranceFee() + 100000000
    tx = lottery.enter({"from": account, "value": value})
    tx.wait(1)
    print("You enter the Lottery!!!")


def end_lottery():
    account = get_account()
    lottery = Lottery[-1]
    tx = fund_with_link(lottery.address)
    tx.wait(1)
    ending_transaction = lottery.endLottery({"from": account})
    ending_transaction.wait(1)
    time.sleep(60)
    print(f"{lottery.recentWinner()} is the new winner!!!")


def main():
    deploy_lottery()
    start_lottery()
    enter_lottery()
    end_lottery()
