// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

/**
 * @title AIAgentRegistry
 * @dev Smart contract for registering and managing AI agents in the AetherFlow ecosystem
 * Implements on-chain component of the HCS-10 OpenConvAI standard
 */
contract AIAgentRegistry is AccessControl, Pausable {
    bytes32 public constant ADMIN_ROLE = keccak256("ADMIN_ROLE");
    bytes32 public constant PAUSER_ROLE = keccak256("PAUSER_ROLE");
    bytes32 public constant AGENT_MANAGER_ROLE = keccak256("AGENT_MANAGER_ROLE");
    
    IERC20 public aetherToken;
    
    // Agent status
    enum AgentStatus { Active, Suspended, Retired }
    
    // Agent type
    enum AgentType { 
        TrafficOptimizer,     // Optimizes traffic flow
        DataValidator,        // Validates vehicle data
        PredictionModel,      // Makes traffic predictions
        FederatedLearning     // Participates in federated learning
    }
    
    // Structure for an AI agent
    struct Agent {
        bytes32 agentId;              // Unique identifier
        address owner;                // Owner of the agent
        string name;                  // Human-readable name
        string metadataURI;           // URI to agent metadata
        AgentStatus status;           // Current status
        AgentType agentType;          // Type of agent
        string hcsTopicId;            // HCS topic ID for this agent
        uint256 registrationTime;     // When the agent was registered
        uint256 performanceScore;     // Performance score (0-100)
        uint256 reputationScore;      // Reputation score (0-100)
        mapping(address => bool) authorizedCallers; // Addresses authorized to call this agent
    }
    
    // Mapping from agent ID to Agent struct
    mapping(bytes32 => Agent) public agents;
    
    // Mapping from agent type to count of active agents
    mapping(AgentType => uint256) public agentCounts;
    
    // Array of all agent IDs for enumeration
    bytes32[] public allAgentIds;
    
    // Registration fee in AETHER tokens
    uint256 public registrationFee = 100 * 10**18; // 100 AETHER
    
    // Events
    event AgentRegistered(bytes32 indexed agentId, address indexed owner, string name, AgentType agentType, string hcsTopicId);
    event AgentStatusChanged(bytes32 indexed agentId, AgentStatus newStatus);
    event AgentMetadataUpdated(bytes32 indexed agentId, string newMetadataURI);
    event AgentScoreUpdated(bytes32 indexed agentId, uint256 performanceScore, uint256 reputationScore);
    event CallerAuthorized(bytes32 indexed agentId, address indexed caller, bool authorized);
    event RegistrationFeeChanged(uint256 newFee);
    
    /**
     * @dev Constructor sets up roles and token address
     * @param _aetherToken Address of the AETHER token contract
     */
    constructor(address _aetherToken) {
        require(_aetherToken != address(0), "AIAgentRegistry: Invalid token address");
        
        aetherToken = IERC20(_aetherToken);
        
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(PAUSER_ROLE, msg.sender);
        _grantRole(ADMIN_ROLE, msg.sender);
        _grantRole(AGENT_MANAGER_ROLE, msg.sender);
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
     * @dev Registers a new AI agent
     * @param name Human-readable name for the agent
     * @param metadataURI URI to agent metadata
     * @param agentType Type of the agent
     * @param hcsTopicId HCS topic ID for this agent
     * @return agentId The ID of the registered agent
     */
    function registerAgent(
        string memory name,
        string memory metadataURI,
        AgentType agentType,
        string memory hcsTopicId
    ) public whenNotPaused returns (bytes32) {
        // Collect registration fee
        require(
            aetherToken.transferFrom(msg.sender, address(this), registrationFee),
            "AIAgentRegistry: Registration fee transfer failed"
        );
        
        // Generate unique agent ID
        bytes32 agentId = keccak256(abi.encodePacked(msg.sender, name, block.timestamp));
        
        // Ensure agent ID is unique
        require(agents[agentId].registrationTime == 0, "AIAgentRegistry: Agent ID collision");
        
        // Create agent
        Agent storage newAgent = agents[agentId];
        newAgent.agentId = agentId;
        newAgent.owner = msg.sender;
        newAgent.name = name;
        newAgent.metadataURI = metadataURI;
        newAgent.status = AgentStatus.Active;
        newAgent.agentType = agentType;
        newAgent.hcsTopicId = hcsTopicId;
        newAgent.registrationTime = block.timestamp;
        newAgent.performanceScore = 50; // Default middle score
        newAgent.reputationScore = 50;  // Default middle score
        
        // Add to enumeration
        allAgentIds.push(agentId);
        
        // Increment agent count for this type
        agentCounts[agentType]++;
        
        emit AgentRegistered(agentId, msg.sender, name, agentType, hcsTopicId);
        
        return agentId;
    }
    
    /**
     * @dev Updates the status of an agent
     * @param agentId ID of the agent
     * @param newStatus New status to set
     */
    function updateAgentStatus(bytes32 agentId, AgentStatus newStatus) public whenNotPaused {
        Agent storage agent = agents[agentId];
        
        require(agent.registrationTime > 0, "AIAgentRegistry: Agent does not exist");
        require(
            msg.sender == agent.owner || hasRole(AGENT_MANAGER_ROLE, msg.sender),
            "AIAgentRegistry: Not authorized"
        );
        
        // Update agent counts if status changes between active and non-active
        if (agent.status == AgentStatus.Active && newStatus != AgentStatus.Active) {
            agentCounts[agent.agentType]--;
        } else if (agent.status != AgentStatus.Active && newStatus == AgentStatus.Active) {
            agentCounts[agent.agentType]++;
        }
        
        agent.status = newStatus;
        
        emit AgentStatusChanged(agentId, newStatus);
    }
    
    /**
     * @dev Updates the metadata URI for an agent
     * @param agentId ID of the agent
     * @param newMetadataURI New metadata URI
     */
    function updateMetadataURI(bytes32 agentId, string memory newMetadataURI) public whenNotPaused {
        Agent storage agent = agents[agentId];
        
        require(agent.registrationTime > 0, "AIAgentRegistry: Agent does not exist");
        require(msg.sender == agent.owner, "AIAgentRegistry: Not the owner");
        
        agent.metadataURI = newMetadataURI;
        
        emit AgentMetadataUpdated(agentId, newMetadataURI);
    }
    
    /**
     * @dev Updates performance and reputation scores for an agent
     * @param agentId ID of the agent
     * @param performanceScore New performance score (0-100)
     * @param reputationScore New reputation score (0-100)
     */
    function updateAgentScores(
        bytes32 agentId, 
        uint256 performanceScore, 
        uint256 reputationScore
    ) public onlyRole(AGENT_MANAGER_ROLE) whenNotPaused {
        require(performanceScore <= 100, "AIAgentRegistry: Invalid performance score");
        require(reputationScore <= 100, "AIAgentRegistry: Invalid reputation score");
        
        Agent storage agent = agents[agentId];
        require(agent.registrationTime > 0, "AIAgentRegistry: Agent does not exist");
        
        agent.performanceScore = performanceScore;
        agent.reputationScore = reputationScore;
        
        emit AgentScoreUpdated(agentId, performanceScore, reputationScore);
    }
    
    /**
     * @dev Authorizes or deauthorizes a caller for an agent
     * @param agentId ID of the agent
     * @param caller Address to authorize/deauthorize
     * @param authorized Whether the caller is authorized
     */
    function setCallerAuthorization(bytes32 agentId, address caller, bool authorized) public whenNotPaused {
        Agent storage agent = agents[agentId];
        
        require(agent.registrationTime > 0, "AIAgentRegistry: Agent does not exist");
        require(msg.sender == agent.owner, "AIAgentRegistry: Not the owner");
        
        agent.authorizedCallers[caller] = authorized;
        
        emit CallerAuthorized(agentId, caller, authorized);
    }
    
    /**
     * @dev Checks if a caller is authorized for an agent
     * @param agentId ID of the agent
     * @param caller Address to check
     * @return Whether the caller is authorized
     */
    function isCallerAuthorized(bytes32 agentId, address caller) public view returns (bool) {
        Agent storage agent = agents[agentId];
        
        if (agent.registrationTime == 0) return false;
        if (caller == agent.owner) return true;
        
        return agent.authorizedCallers[caller];
    }
    
    /**
     * @dev Gets the total number of registered agents
     * @return Total number of agents
     */
    function getTotalAgentCount() public view returns (uint256) {
        return allAgentIds.length;
    }
    
    /**
     * @dev Gets an agent by index (for enumeration)
     * @param index Index in the allAgentIds array
     * @return agentId ID of the agent at the specified index
     */
    function getAgentIdByIndex(uint256 index) public view returns (bytes32) {
        require(index < allAgentIds.length, "AIAgentRegistry: Index out of bounds");
        return allAgentIds[index];
    }
    
    /**
     * @dev Sets the registration fee
     * @param newFee New registration fee in AETHER tokens
     */
    function setRegistrationFee(uint256 newFee) public onlyRole(ADMIN_ROLE) {
        registrationFee = newFee;
        emit RegistrationFeeChanged(newFee);
    }
    
    /**
     * @dev Withdraws collected fees
     * @param amount Amount to withdraw
     * @param recipient Address to send fees to
     */
    function withdrawFees(uint256 amount, address recipient) public onlyRole(ADMIN_ROLE) {
        require(recipient != address(0), "AIAgentRegistry: Invalid recipient");
        
        require(
            aetherToken.transfer(recipient, amount),
            "AIAgentRegistry: Fee transfer failed"
        );
    }
}
