from brownie import Lottery, accounts, config, network, exceptions
from web3 import Web3
from scripts.deploy_lottery import deploy_lottery
from scripts.helpfull_scripts import (
    LOCAL_BLOCKCHAIN_ENVIROMENTS,
    get_account,
    fund_with_link,
    get_contract,
)
import pytest



@pytest.fixture
def lottery():
    lottery = deploy_lottery()
    return lottery


def test_get_entrance_fee(lottery):
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIROMENTS:
        pytest.skip()
    assert lottery.getEntranceFee() > Web3.toWei(0.024, "ether")
    assert lottery.getEntranceFee() < Web3.toWei(0.028, "ether")


def test_cant_enter_unless_starter(lottery):
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIROMENTS:
        pytest.skip()
    with pytest.raises(exceptions.VirtualMachineError):
        lottery.enter({"from": get_account(), "value": lottery.getEntranceFee()})


def test_can_start_and_enter_lottery(lottery):
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIROMENTS:
        pytest.skip()
    account = get_account()
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    assert lottery.players(0) == account


def test_can_end_lottery(lottery):
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIROMENTS:
        pytest.skip()
    account = get_account()
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    fund_with_link(lottery)
    lottery.endLottery({"from": account})
    assert lottery.lottery_state() == 2


def test_can_pick_winner_correctly(lottery):
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIROMENTS:
        pytest.skip()
    account = get_account()
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    lottery.enter({"from": get_account(), "value": lottery.getEntranceFee()})
    lottery.enter({"from": get_account(), "value": lottery.getEntranceFee()})
    fund_with_link(lottery)
    tx = lottery.endLottery({"from": account})
    requestedId = tx.events["RequestedRandomness"]["requestedId"]
    STATIC_RNG = 777
    get_contract("vrf_coordinator").callBackWithRandomness(
        requestedId, STATIC_RNG, lottery.address, {"from": account}
    )
    starting_balance = account.balance()
    balance_of_lottery = lottery.balance()
    assert lottery.recentWinner() == account
    assert lottery.balance() == 0
    assert account.balance() == starting_balance + balance_of_lottery
