// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Burnable.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";

/**
 * @title AetherToken
 * @dev ERC20 token for the AetherFlow ecosystem
 * Implements role-based access control, pausable functionality, and burning capabilities
 */
contract AetherToken is ERC20, ERC20Burnable, Pausable, AccessControl {
    bytes32 public constant MINTER_ROLE = keccak256("MINTER_ROLE");
    bytes32 public constant PAUSER_ROLE = keccak256("PAUSER_ROLE");
    
    uint256 public constant MAX_SUPPLY = 1_000_000_000 * 10**18; // 1 billion tokens
    uint256 private _totalMinted = 0;

    // Events
    event RewardDistributed(address indexed recipient, uint256 amount, string reason);
    
    /**
     * @dev Constructor that gives the msg.sender all existing tokens.
     */
    constructor() ERC20("AetherFlow Token", "AETHER") {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(MINTER_ROLE, msg.sender);
        _grantRole(PAUSER_ROLE, msg.sender);
        
        // Initial supply for ecosystem development (10% of max supply)
        uint256 initialSupply = MAX_SUPPLY / 10;
        _mint(msg.sender, initialSupply);
        _totalMinted += initialSupply;
    }

    /**
     * @dev Pauses all token transfers.
     * Requirements: Caller must have PAUSER_ROLE
     */
    function pause() public onlyRole(PAUSER_ROLE) {
        _pause();
    }

    /**
     * @dev Unpauses all token transfers.
     * Requirements: Caller must have PAUSER_ROLE
     */
    function unpause() public onlyRole(PAUSER_ROLE) {
        _unpause();
    }

    /**
     * @dev Mints tokens to the specified address.
     * Requirements:
     * - Caller must have MINTER_ROLE
     * - Total minted tokens must not exceed MAX_SUPPLY
     */
    function mint(address to, uint256 amount) public onlyRole(MINTER_ROLE) {
        require(_totalMinted + amount <= MAX_SUPPLY, "AetherToken: Max supply exceeded");
        _mint(to, amount);
        _totalMinted += amount;
    }
    
    /**
     * @dev Distributes rewards to data contributors or validators
     * @param recipient Address receiving the reward
     * @param amount Amount of tokens to reward
     * @param reason String description of the reward reason
     */
    function distributeReward(address recipient, uint256 amount, string memory reason) 
        public 
        onlyRole(MINTER_ROLE) 
    {
        require(_totalMinted + amount <= MAX_SUPPLY, "AetherToken: Max supply exceeded");
        _mint(recipient, amount);
        _totalMinted += amount;
        
        emit RewardDistributed(recipient, amount, reason);
    }
    
    /**
     * @dev Returns the amount of tokens that can still be minted
     */
    function remainingSupply() public view returns (uint256) {
        return MAX_SUPPLY - _totalMinted;
    }

    /**
     * @dev Hook that is called before any transfer of tokens.
     */
    function _beforeTokenTransfer(address from, address to, uint256 amount)
        internal
        whenNotPaused
        override
    {
        super._beforeTokenTransfer(from, to, amount);
    }
}
