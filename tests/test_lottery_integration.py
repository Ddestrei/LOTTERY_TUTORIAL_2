from brownie import network
from scripts.helpfull_scripts import LOCAL_BLOCKCHAIN_ENVIROMENTS, get_account, fund_with_link
from scripts.deploy_lottery import deploy_lottery
import pytest, time

@pytest.fixture
def lottery():
    lottery = deploy_lottery()
    return lottery

@pytest.fixture
def account():
    account = get_account()
    return account


def test_can_pick_winner(lottery, account):
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIROMENTS:
        pytest.skip()
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    fund_with_link(lottery)
    lottery.endLottery({"from": account})
    time.sleep(60)
    assert lottery.recentWinner() == account
    assert lottery.balance() == 0 


