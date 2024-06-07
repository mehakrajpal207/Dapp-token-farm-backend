// SPDX-License-Identifier: MIT
pragma solidity ^0.8.7;

import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

contract TokenFarm is Ownable, ReentrancyGuard {
    string public name = "Dapp Token Farm";
    IERC20 public dappToken;

    address[] public stakers;
    mapping(address => mapping(address => uint256)) public stakingBalance;
    mapping(address => uint256) public uniqueTokensStaked;
    mapping(address => address) public tokenPriceFeedMapping;
    address[] public allowedTokens;

    constructor(address _dappTokenAddress) {
        dappToken = IERC20(_dappTokenAddress);
    }

    function addAllowedTokens(address token) public onlyOwner {
        allowedTokens.push(token);
    }

    function setPriceFeedContract(address token, address priceFeed) public onlyOwner {
        tokenPriceFeedMapping[token] = priceFeed;
    }

    function stakeTokens(uint256 _amount, address token) public nonReentrant {
        require(_amount > 0, "Amount cannot be 0");
        require(tokenIsAllowed(token), "Token currently isn't allowed");

        updateUniqueTokensStaked(msg.sender, token);
        IERC20(token).transferFrom(msg.sender, address(this), _amount);
        stakingBalance[token][msg.sender] += _amount;

        if (uniqueTokensStaked[msg.sender] == 1) {
            stakers.push(msg.sender);
        }
    }

    function unstakeTokens(address token) public nonReentrant {
        uint256 balance = stakingBalance[token][msg.sender];
        require(balance > 0, "Staking balance cannot be 0");

        stakingBalance[token][msg.sender] = 0;
        uniqueTokensStaked[msg.sender] -= 1;
        IERC20(token).transfer(msg.sender, balance);
    }

    function getUserTotalValue(address user) public view returns (uint256) {
        uint256 totalValue = 0;
        if (uniqueTokensStaked[user] > 0) {
            for (uint256 i = 0; i < allowedTokens.length; i++) {
                totalValue += getUserTokenStakingBalanceEthValue(user, allowedTokens[i]);
            }
        }
        return totalValue;
    }

    function tokenIsAllowed(address token) public view returns (bool) {
        for (uint256 i = 0; i < allowedTokens.length; i++) {
            if (allowedTokens[i] == token) {
                return true;
            }
        }
        return false;
    }

    function updateUniqueTokensStaked(address user, address token) internal {
        if (stakingBalance[token][user] == 0) {
            uniqueTokensStaked[user] += 1;
        }
    }

    function getUserTokenStakingBalanceEthValue(address user, address token) public view returns (uint256) {
        if (uniqueTokensStaked[user] <= 0) {
            return 0;
        }
        (uint256 price, uint8 decimals) = getTokenEthPrice(token);
        return (stakingBalance[token][user] * price) / (10 ** decimals);
    }

    function issueTokens() public onlyOwner {
        for (uint256 i = 0; i < stakers.length; i++) {
            address recipient = stakers[i];
            dappToken.transfer(recipient, getUserTotalValue(recipient));
        }
    }

    function getTokenEthPrice(address token) public view returns (uint256, uint8) {
        address priceFeedAddress = tokenPriceFeedMapping[token];
        AggregatorV3Interface priceFeed = AggregatorV3Interface(priceFeedAddress);
        (, int256 price, , , ) = priceFeed.latestRoundData();
        return (uint256(price), priceFeed.decimals());
    }
}
