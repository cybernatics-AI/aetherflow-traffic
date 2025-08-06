// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "./AetherToken.sol";
import "./TrafficNFT.sol";
import "./CongestionDerivatives.sol";
import "./AIAgentRegistry.sol";

/**
 * @title AetherFlowContractFactory
 * @dev Factory contract to deploy and manage AetherFlow ecosystem contracts
 */
contract AetherFlowContractFactory is AccessControl, Pausable {
    bytes32 public constant ADMIN_ROLE = keccak256("ADMIN_ROLE");
    bytes32 public constant PAUSER_ROLE = keccak256("PAUSER_ROLE");
    bytes32 public constant DEPLOYER_ROLE = keccak256("DEPLOYER_ROLE");
    
    // Contract addresses
    address public aetherTokenAddress;
    address public trafficNFTAddress;
    address public congestionDerivativesAddress;
    address public aiAgentRegistryAddress;
    
    // Events
    event AetherTokenDeployed(address indexed contractAddress);
    event TrafficNFTDeployed(address indexed contractAddress);
    event CongestionDerivativesDeployed(address indexed contractAddress);
    event AIAgentRegistryDeployed(address indexed contractAddress);
    
    constructor() {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(PAUSER_ROLE, msg.sender);
        _grantRole(DEPLOYER_ROLE, msg.sender);
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
     * @dev Deploys the AetherToken contract
     * @return The address of the deployed contract
     */
    function deployAetherToken() public onlyRole(DEPLOYER_ROLE) whenNotPaused returns (address) {
        require(aetherTokenAddress == address(0), "AetherFlowContractFactory: AetherToken already deployed");
        
        AetherToken token = new AetherToken();
        aetherTokenAddress = address(token);
        
        // Grant roles to the factory
        token.grantRole(token.DEFAULT_ADMIN_ROLE(), address(this));
        token.grantRole(token.MINTER_ROLE(), address(this));
        token.grantRole(token.PAUSER_ROLE(), address(this));
        
        emit AetherTokenDeployed(aetherTokenAddress);
        
        return aetherTokenAddress;
    }
    
    /**
     * @dev Deploys the TrafficNFT contract
     * @return The address of the deployed contract
     */
    function deployTrafficNFT() public onlyRole(DEPLOYER_ROLE) whenNotPaused returns (address) {
        require(trafficNFTAddress == address(0), "AetherFlowContractFactory: TrafficNFT already deployed");
        
        TrafficNFT nft = new TrafficNFT();
        trafficNFTAddress = address(nft);
        
        // Grant roles to the factory
        nft.grantRole(nft.DEFAULT_ADMIN_ROLE(), address(this));
        nft.grantRole(nft.MINTER_ROLE(), address(this));
        nft.grantRole(nft.PAUSER_ROLE(), address(this));
        nft.grantRole(nft.DATA_VALIDATOR_ROLE(), address(this));
        
        emit TrafficNFTDeployed(trafficNFTAddress);
        
        return trafficNFTAddress;
    }
    
    /**
     * @dev Deploys the CongestionDerivatives contract
     * @return The address of the deployed contract
     */
    function deployCongestionDerivatives() public onlyRole(DEPLOYER_ROLE) whenNotPaused returns (address) {
        require(congestionDerivativesAddress == address(0), "AetherFlowContractFactory: CongestionDerivatives already deployed");
        require(aetherTokenAddress != address(0), "AetherFlowContractFactory: AetherToken not deployed");
        
        CongestionDerivatives derivatives = new CongestionDerivatives(aetherTokenAddress);
        congestionDerivativesAddress = address(derivatives);
        
        // Grant roles to the factory
        derivatives.grantRole(derivatives.DEFAULT_ADMIN_ROLE(), address(this));
        derivatives.grantRole(derivatives.ORACLE_ROLE(), address(this));
        derivatives.grantRole(derivatives.PAUSER_ROLE(), address(this));
        derivatives.grantRole(derivatives.ADMIN_ROLE(), address(this));
        
        emit CongestionDerivativesDeployed(congestionDerivativesAddress);
        
        return congestionDerivativesAddress;
    }
    
    /**
     * @dev Deploys the AIAgentRegistry contract
     * @return The address of the deployed contract
     */
    function deployAIAgentRegistry() public onlyRole(DEPLOYER_ROLE) whenNotPaused returns (address) {
        require(aiAgentRegistryAddress == address(0), "AetherFlowContractFactory: AIAgentRegistry already deployed");
        require(aetherTokenAddress != address(0), "AetherFlowContractFactory: AetherToken not deployed");
        
        AIAgentRegistry registry = new AIAgentRegistry(aetherTokenAddress);
        aiAgentRegistryAddress = address(registry);
        
        // Grant roles to the factory
        registry.grantRole(registry.DEFAULT_ADMIN_ROLE(), address(this));
        registry.grantRole(registry.PAUSER_ROLE(), address(this));
        registry.grantRole(registry.ADMIN_ROLE(), address(this));
        registry.grantRole(registry.AGENT_MANAGER_ROLE(), address(this));
        
        emit AIAgentRegistryDeployed(aiAgentRegistryAddress);
        
        return aiAgentRegistryAddress;
    }
    
    /**
     * @dev Deploys all contracts in the correct order
     * @return A tuple of all deployed contract addresses
     */
    function deployAllContracts() public onlyRole(DEPLOYER_ROLE) whenNotPaused returns (
        address, address, address, address
    ) {
        address token = deployAetherToken();
        address nft = deployTrafficNFT();
        address derivatives = deployCongestionDerivatives();
        address registry = deployAIAgentRegistry();
        
        return (token, nft, derivatives, registry);
    }
    
    /**
     * @dev Transfers admin roles from factory to a new admin
     * @param newAdmin Address of the new admin
     */
    function transferAdminRoles(address newAdmin) public onlyRole(DEFAULT_ADMIN_ROLE) {
        require(newAdmin != address(0), "AetherFlowContractFactory: Invalid admin address");
        
        // Transfer roles for AetherToken
        if (aetherTokenAddress != address(0)) {
            AetherToken token = AetherToken(aetherTokenAddress);
            token.grantRole(token.DEFAULT_ADMIN_ROLE(), newAdmin);
            token.grantRole(token.MINTER_ROLE(), newAdmin);
            token.grantRole(token.PAUSER_ROLE(), newAdmin);
        }
        
        // Transfer roles for TrafficNFT
        if (trafficNFTAddress != address(0)) {
            TrafficNFT nft = TrafficNFT(trafficNFTAddress);
            nft.grantRole(nft.DEFAULT_ADMIN_ROLE(), newAdmin);
            nft.grantRole(nft.MINTER_ROLE(), newAdmin);
            nft.grantRole(nft.PAUSER_ROLE(), newAdmin);
            nft.grantRole(nft.DATA_VALIDATOR_ROLE(), newAdmin);
        }
        
        // Transfer roles for CongestionDerivatives
        if (congestionDerivativesAddress != address(0)) {
            CongestionDerivatives derivatives = CongestionDerivatives(congestionDerivativesAddress);
            derivatives.grantRole(derivatives.DEFAULT_ADMIN_ROLE(), newAdmin);
            derivatives.grantRole(derivatives.ORACLE_ROLE(), newAdmin);
            derivatives.grantRole(derivatives.PAUSER_ROLE(), newAdmin);
            derivatives.grantRole(derivatives.ADMIN_ROLE(), newAdmin);
        }
        
        // Transfer roles for AIAgentRegistry
        if (aiAgentRegistryAddress != address(0)) {
            AIAgentRegistry registry = AIAgentRegistry(aiAgentRegistryAddress);
            registry.grantRole(registry.DEFAULT_ADMIN_ROLE(), newAdmin);
            registry.grantRole(registry.PAUSER_ROLE(), newAdmin);
            registry.grantRole(registry.ADMIN_ROLE(), newAdmin);
            registry.grantRole(registry.AGENT_MANAGER_ROLE(), newAdmin);
        }
        
        // Transfer roles for the factory itself
        _grantRole(DEFAULT_ADMIN_ROLE, newAdmin);
        _grantRole(PAUSER_ROLE, newAdmin);
        _grantRole(DEPLOYER_ROLE, newAdmin);
    }
}
