// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721Enumerable.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/utils/Counters.sol";
import "@openzeppelin/contracts/security/Pausable.sol";

/**
 * @title TrafficNFT
 * @dev ERC721 contract for traffic data contributions in the AetherFlow ecosystem
 * Each NFT represents validated traffic data from a vehicle or intersection
 */
contract TrafficNFT is ERC721, ERC721URIStorage, ERC721Enumerable, AccessControl, Pausable {
    using Counters for Counters.Counter;

    bytes32 public constant MINTER_ROLE = keccak256("MINTER_ROLE");
    bytes32 public constant PAUSER_ROLE = keccak256("PAUSER_ROLE");
    bytes32 public constant DATA_VALIDATOR_ROLE = keccak256("DATA_VALIDATOR_ROLE");
    
    Counters.Counter private _tokenIdCounter;
    
    // Mapping from token ID to data hash (for verification)
    mapping(uint256 => bytes32) private _dataHashes;
    
    // Mapping from token ID to data type
    mapping(uint256 => string) private _dataTypes;
    
    // Mapping from token ID to geolocation data
    mapping(uint256 => string) private _geolocations;
    
    // Mapping from token ID to timestamp
    mapping(uint256 => uint256) private _timestamps;
    
    // Events
    event TrafficDataMinted(uint256 indexed tokenId, address contributor, bytes32 dataHash, string dataType);
    event DataValidated(uint256 indexed tokenId, address validator, bool isValid);

    constructor() ERC721("AetherFlow Traffic Data", "TRAFFIC") {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(MINTER_ROLE, msg.sender);
        _grantRole(PAUSER_ROLE, msg.sender);
        _grantRole(DATA_VALIDATOR_ROLE, msg.sender);
    }

    /**
     * @dev Pauses all token transfers and minting.
     * Requirements: Caller must have PAUSER_ROLE
     */
    function pause() public onlyRole(PAUSER_ROLE) {
        _pause();
    }

    /**
     * @dev Unpauses all token transfers and minting.
     * Requirements: Caller must have PAUSER_ROLE
     */
    function unpause() public onlyRole(PAUSER_ROLE) {
        _unpause();
    }

    /**
     * @dev Mints a new Traffic NFT representing traffic data
     * @param to Address receiving the NFT
     * @param uri Token URI with metadata
     * @param dataHash Hash of the traffic data for verification
     * @param dataType Type of traffic data (e.g., "vehicle", "intersection", "corridor")
     * @param geolocation String representation of geolocation data
     */
    function safeMint(
        address to, 
        string memory uri, 
        bytes32 dataHash, 
        string memory dataType,
        string memory geolocation
    ) public onlyRole(MINTER_ROLE) whenNotPaused {
        uint256 tokenId = _tokenIdCounter.current();
        _tokenIdCounter.increment();
        
        _safeMint(to, tokenId);
        _setTokenURI(tokenId, uri);
        
        _dataHashes[tokenId] = dataHash;
        _dataTypes[tokenId] = dataType;
        _geolocations[tokenId] = geolocation;
        _timestamps[tokenId] = block.timestamp;
        
        emit TrafficDataMinted(tokenId, to, dataHash, dataType);
    }
    
    /**
     * @dev Validates traffic data associated with an NFT
     * @param tokenId ID of the token to validate
     * @param isValid Whether the data is valid
     */
    function validateData(uint256 tokenId, bool isValid) 
        public 
        onlyRole(DATA_VALIDATOR_ROLE) 
    {
        require(_exists(tokenId), "TrafficNFT: Token does not exist");
        
        // Additional validation logic could be implemented here
        
        emit DataValidated(tokenId, msg.sender, isValid);
    }
    
    /**
     * @dev Returns the data hash associated with a token
     */
    function getDataHash(uint256 tokenId) public view returns (bytes32) {
        require(_exists(tokenId), "TrafficNFT: Token does not exist");
        return _dataHashes[tokenId];
    }
    
    /**
     * @dev Returns the data type associated with a token
     */
    function getDataType(uint256 tokenId) public view returns (string memory) {
        require(_exists(tokenId), "TrafficNFT: Token does not exist");
        return _dataTypes[tokenId];
    }
    
    /**
     * @dev Returns the geolocation associated with a token
     */
    function getGeolocation(uint256 tokenId) public view returns (string memory) {
        require(_exists(tokenId), "TrafficNFT: Token does not exist");
        return _geolocations[tokenId];
    }
    
    /**
     * @dev Returns the timestamp when the token was minted
     */
    function getTimestamp(uint256 tokenId) public view returns (uint256) {
        require(_exists(tokenId), "TrafficNFT: Token does not exist");
        return _timestamps[tokenId];
    }

    // The following functions are overrides required by Solidity

    function _beforeTokenTransfer(address from, address to, uint256 tokenId, uint256 batchSize)
        internal
        whenNotPaused
        override(ERC721, ERC721Enumerable)
    {
        super._beforeTokenTransfer(from, to, tokenId, batchSize);
    }

    function _burn(uint256 tokenId) 
        internal 
        override(ERC721, ERC721URIStorage) 
    {
        super._burn(tokenId);
    }

    function tokenURI(uint256 tokenId)
        public
        view
        override(ERC721, ERC721URIStorage)
        returns (string memory)
    {
        return super.tokenURI(tokenId);
    }
    
    function supportsInterface(bytes4 interfaceId)
        public
        view
        override(ERC721, ERC721Enumerable, AccessControl)
        returns (bool)
    {
        return super.supportsInterface(interfaceId);
    }
}
