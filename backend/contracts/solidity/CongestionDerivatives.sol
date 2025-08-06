// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

/**
 * @title CongestionDerivatives
 * @dev Smart contract for creating and settling financial derivatives based on traffic congestion
 * Allows users to create and trade prediction markets for traffic conditions
 */
contract CongestionDerivatives is AccessControl, Pausable, ReentrancyGuard {
    bytes32 public constant ORACLE_ROLE = keccak256("ORACLE_ROLE");
    bytes32 public constant PAUSER_ROLE = keccak256("PAUSER_ROLE");
    bytes32 public constant ADMIN_ROLE = keccak256("ADMIN_ROLE");
    
    IERC20 public aetherToken;
    
    uint256 public derivativeCounter;
    
    // Status of a derivative contract
    enum Status { Active, Settled, Cancelled }
    
    // Types of congestion derivatives
    enum DerivativeType { 
        BinaryCongestion,     // Will congestion exceed threshold? (yes/no)
        CongestionLevel,      // Predict exact congestion level
        TravelTime            // Predict travel time between points
    }
    
    // Structure for a congestion derivative
    struct Derivative {
        uint256 id;
        string geolocation;   // Area or corridor the derivative covers
        uint256 expiryTime;   // When the derivative expires and can be settled
        DerivativeType derivativeType;
        Status status;
        uint256 totalStaked;  // Total amount staked on this derivative
        mapping(address => uint256) stakes; // User stakes
        mapping(address => uint256) predictions; // User predictions
        uint256 actualValue;  // Actual value reported by oracle
        uint256 createdAt;    // Creation timestamp
    }
    
    // Mapping from derivative ID to Derivative struct
    mapping(uint256 => Derivative) public derivatives;
    
    // Events
    event DerivativeCreated(uint256 indexed id, string geolocation, uint256 expiryTime, DerivativeType derivativeType);
    event StakePlaced(uint256 indexed derivativeId, address indexed user, uint256 amount, uint256 prediction);
    event DerivativeSettled(uint256 indexed id, uint256 actualValue);
    event RewardClaimed(uint256 indexed derivativeId, address indexed user, uint256 amount);
    
    /**
     * @dev Constructor sets up roles and token address
     * @param _aetherToken Address of the AETHER token contract
     */
    constructor(address _aetherToken) {
        require(_aetherToken != address(0), "CongestionDerivatives: Invalid token address");
        
        aetherToken = IERC20(_aetherToken);
        
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(ORACLE_ROLE, msg.sender);
        _grantRole(PAUSER_ROLE, msg.sender);
        _grantRole(ADMIN_ROLE, msg.sender);
        
        derivativeCounter = 0;
    }
    
    /**
     * @dev Pauses the contract
     * Requirements: Caller must have PAUSER_ROLE
     */
    function pause() public onlyRole(PAUSER_ROLE) {
        _pause();
    }
    
    /**
     * @dev Unpauses the contract
     * Requirements: Caller must have PAUSER_ROLE
     */
    function unpause() public onlyRole(PAUSER_ROLE) {
        _unpause();
    }
    
    /**
     * @dev Creates a new congestion derivative
     * @param geolocation Area or corridor the derivative covers
     * @param expiryTimeFromNow Time until expiry in seconds from now
     * @param derivativeType Type of derivative
     * @return id The ID of the created derivative
     */
    function createDerivative(
        string memory geolocation,
        uint256 expiryTimeFromNow,
        DerivativeType derivativeType
    ) public onlyRole(ADMIN_ROLE) whenNotPaused returns (uint256) {
        require(expiryTimeFromNow > 1 hours, "CongestionDerivatives: Expiry too soon");
        require(expiryTimeFromNow < 30 days, "CongestionDerivatives: Expiry too far");
        
        uint256 id = derivativeCounter++;
        uint256 expiryTime = block.timestamp + expiryTimeFromNow;
        
        Derivative storage newDerivative = derivatives[id];
        newDerivative.id = id;
        newDerivative.geolocation = geolocation;
        newDerivative.expiryTime = expiryTime;
        newDerivative.derivativeType = derivativeType;
        newDerivative.status = Status.Active;
        newDerivative.totalStaked = 0;
        newDerivative.createdAt = block.timestamp;
        
        emit DerivativeCreated(id, geolocation, expiryTime, derivativeType);
        
        return id;
    }
    
    /**
     * @dev Places a stake on a prediction for a derivative
     * @param derivativeId ID of the derivative
     * @param amount Amount of AETHER tokens to stake
     * @param prediction The predicted value
     */
    function placeStake(
        uint256 derivativeId,
        uint256 amount,
        uint256 prediction
    ) public whenNotPaused nonReentrant {
        Derivative storage derivative = derivatives[derivativeId];
        
        require(derivative.id == derivativeId, "CongestionDerivatives: Derivative does not exist");
        require(derivative.status == Status.Active, "CongestionDerivatives: Derivative not active");
        require(block.timestamp < derivative.expiryTime, "CongestionDerivatives: Derivative expired");
        require(amount > 0, "CongestionDerivatives: Stake amount must be positive");
        
        // Validate prediction based on derivative type
        if (derivative.derivativeType == DerivativeType.BinaryCongestion) {
            require(prediction == 0 || prediction == 1, "CongestionDerivatives: Invalid binary prediction");
        }
        
        // Transfer tokens from user to contract
        require(
            aetherToken.transferFrom(msg.sender, address(this), amount),
            "CongestionDerivatives: Token transfer failed"
        );
        
        // Update stake and prediction
        derivative.stakes[msg.sender] += amount;
        derivative.predictions[msg.sender] = prediction;
        derivative.totalStaked += amount;
        
        emit StakePlaced(derivativeId, msg.sender, amount, prediction);
    }
    
    /**
     * @dev Settles a derivative with the actual value
     * @param derivativeId ID of the derivative to settle
     * @param actualValue The actual value reported by the oracle
     */
    function settleDerivative(uint256 derivativeId, uint256 actualValue) 
        public 
        onlyRole(ORACLE_ROLE) 
        whenNotPaused 
    {
        Derivative storage derivative = derivatives[derivativeId];
        
        require(derivative.id == derivativeId, "CongestionDerivatives: Derivative does not exist");
        require(derivative.status == Status.Active, "CongestionDerivatives: Derivative already settled");
        require(block.timestamp >= derivative.expiryTime, "CongestionDerivatives: Derivative not expired");
        
        derivative.status = Status.Settled;
        derivative.actualValue = actualValue;
        
        emit DerivativeSettled(derivativeId, actualValue);
    }
    
    /**
     * @dev Claims rewards for a settled derivative
     * @param derivativeId ID of the settled derivative
     */
    function claimReward(uint256 derivativeId) public whenNotPaused nonReentrant {
        Derivative storage derivative = derivatives[derivativeId];
        
        require(derivative.id == derivativeId, "CongestionDerivatives: Derivative does not exist");
        require(derivative.status == Status.Settled, "CongestionDerivatives: Derivative not settled");
        require(derivative.stakes[msg.sender] > 0, "CongestionDerivatives: No stake to claim");
        
        uint256 userStake = derivative.stakes[msg.sender];
        uint256 userPrediction = derivative.predictions[msg.sender];
        uint256 reward = 0;
        
        // Calculate reward based on derivative type and accuracy
        if (derivative.derivativeType == DerivativeType.BinaryCongestion) {
            // Binary prediction - winner takes all with 5% fee
            if (userPrediction == derivative.actualValue) {
                // User predicted correctly
                uint256 totalCorrectStakes = calculateTotalCorrectStakes(derivativeId, derivative.actualValue);
                reward = (derivative.totalStaked * 95 / 100) * userStake / totalCorrectStakes;
            }
        } else {
            // For other types, reward based on how close the prediction was
            uint256 accuracy = calculateAccuracy(userPrediction, derivative.actualValue);
            reward = (userStake * accuracy) / 100;
        }
        
        // Reset user stake to prevent double claiming
        derivative.stakes[msg.sender] = 0;
        
        // Transfer reward to user
        require(
            aetherToken.transfer(msg.sender, reward),
            "CongestionDerivatives: Reward transfer failed"
        );
        
        emit RewardClaimed(derivativeId, msg.sender, reward);
    }
    
    /**
     * @dev Calculates the total stakes that correctly predicted the outcome
     * @param derivativeId ID of the derivative
     * @param actualValue The actual value that was reported
     * @return Total amount staked on the correct prediction
     */
    function calculateTotalCorrectStakes(uint256 derivativeId, uint256 actualValue) 
        internal 
        view 
        returns (uint256) 
    {
        // This is a simplified implementation
        // In production, you would need to iterate through all stakers
        // This would likely be done off-chain and verified on-chain
        return derivative.totalStaked / 2; // Simplified assumption
    }
    
    /**
     * @dev Calculates accuracy of a prediction as a percentage
     * @param prediction User's prediction
     * @param actualValue Actual value reported
     * @return Accuracy percentage (0-100)
     */
    function calculateAccuracy(uint256 prediction, uint256 actualValue) 
        internal 
        pure 
        returns (uint256) 
    {
        // Simplified accuracy calculation
        if (prediction > actualValue) {
            uint256 diff = prediction - actualValue;
            if (diff > actualValue) return 0;
            return 100 - (diff * 100 / actualValue);
        } else {
            uint256 diff = actualValue - prediction;
            if (diff > prediction) return 0;
            return 100 - (diff * 100 / prediction);
        }
    }
    
    /**
     * @dev Cancels a derivative before it expires (emergency function)
     * @param derivativeId ID of the derivative to cancel
     */
    function cancelDerivative(uint256 derivativeId) public onlyRole(ADMIN_ROLE) {
        Derivative storage derivative = derivatives[derivativeId];
        
        require(derivative.id == derivativeId, "CongestionDerivatives: Derivative does not exist");
        require(derivative.status == Status.Active, "CongestionDerivatives: Derivative not active");
        
        derivative.status = Status.Cancelled;
        
        // Logic for refunding stakes would be implemented here
    }
    
    /**
     * @dev Withdraws fees collected from derivatives
     * @param amount Amount to withdraw
     * @param recipient Address to send fees to
     */
    function withdrawFees(uint256 amount, address recipient) 
        public 
        onlyRole(ADMIN_ROLE) 
        nonReentrant 
    {
        require(recipient != address(0), "CongestionDerivatives: Invalid recipient");
        require(amount > 0, "CongestionDerivatives: Amount must be positive");
        
        require(
            aetherToken.transfer(recipient, amount),
            "CongestionDerivatives: Fee transfer failed"
        );
    }
}
