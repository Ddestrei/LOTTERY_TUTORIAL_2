// SPDX-License-Identifier: MIT 
// SPDX-Licence-Identifier: GPL-3.0

pragma solidity ^0.8.18;

import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@chainlink/contracts/src/v0.8/VRFConsumerBase.sol";

contract Lottery is Ownable, VRFConsumerBase {

    bytes32 public keyHash;
    uint256 public fee;

    enum LOTTERY_STATE {
        OPEN,
        CLOSED,
        CALCULATING_WINNER
    }

    LOTTERY_STATE public lottery_state;

    address payable[] public players;
    uint256 public usdEntryFee;
    AggregatorV3Interface internal _ethUsdPriceFeed;
    address public recentWinner;

    event RequestedRandomness(bytes32 requestedId);

    constructor(
        address _priceFeedAddress, 
        address _vrfCondinator, 
        address _link,
        uint256 _fee,
        bytes32 _keyHash) 
        public VRFConsumerBase(_vrfCondinator,_link){
        lottery_state = LOTTERY_STATE.CLOSED;
        usdEntryFee = 50 * (10**18);
        _ethUsdPriceFeed = AggregatorV3Interface(_priceFeedAddress);
        fee = _fee;
        keyHash = _keyHash;

    }

    function enter() public payable returns(uint256){
        require(lottery_state == LOTTERY_STATE.OPEN, "Lottery is not open!!!");
        require(msg.value >= getEntranceFee(), "Not enought ETH!!!");
        players.push(payable(msg.sender));
    }

    function getEntranceFee()public view returns(uint256){
        // min 50$
        (,int price,,,) = _ethUsdPriceFeed.latestRoundData();
        uint256 adjustPrice = uint256(price) * (10**10);
        uint256 costToEnter = (usdEntryFee * (10**18))/adjustPrice;
        return costToEnter;
    }

    function startLottery() public onlyOwner{
        require(lottery_state == LOTTERY_STATE.CLOSED, "You can not start this lottery again!!!");
        lottery_state = LOTTERY_STATE.OPEN;
    }

    function endLottery()public onlyOwner{
        // uint256(
        //     keccak256(
        //         abi.encodePacked(
        //             nonce,
        //             msg.sender,
        //             block.difficulty,
        //             block.timestamp)
        //         )
        //     ) % players.length;
        lottery_state = LOTTERY_STATE.CALCULATING_WINNER;
        bytes32 requestedId = requestRandomness(keyHash, fee);
        emit RequestedRandomness(requestedId);
    }

    function fulfillRandomness(bytes32 _requestId, uint256 _randomness) internal override{
        require(lottery_state == LOTTERY_STATE.CALCULATING_WINNER, "You aren`t there yet!!!");
        require(_randomness > 0 , "random-not-found!!!");
        uint256 indexOfWinner = _randomness % players.length;
        recentWinner = players[indexOfWinner];
        payable(recentWinner).transfer(address(this).balance);
        players = new address payable[](0);
        lottery_state = LOTTERY_STATE.CLOSED;
    }
}