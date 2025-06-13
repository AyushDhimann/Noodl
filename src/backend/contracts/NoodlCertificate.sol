// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/Counters.sol";
import "hardhat/console.sol";

contract NoodlCertificate is ERC721, ERC721URIStorage, Ownable {
    using Counters for Counters.Counter;
    Counters.Counter private _tokenIdCounter;

    uint256 private constant TOKEN_ID_OFFSET = 74418500;

    mapping(address => mapping(uint256 => uint256)) public userPathToTokenId;

    constructor(address initialOwner)
        ERC721("Noodl Certificate", "NOODL")
        Ownable(initialOwner)
    {
        console.log("NoodlCertificate deployed! Owner:", initialOwner);
        console.log("Contract address:", address(this));
        console.log("Token ID offset:", TOKEN_ID_OFFSET);
        console.log("First token will have ID:", TOKEN_ID_OFFSET);
    }

    function setTokenURI(uint256 tokenId, string memory uri) public onlyOwner {
        console.log("Setting URI for token:", tokenId);
        _setTokenURI(tokenId, uri);
        console.log("URI set successfully");
    }

    function safeMint(address to, uint256 pathId) public onlyOwner {
        console.log("=== MINT START ===");
        console.log("Recipient:", to);
        console.log("Path ID:", pathId);

        uint256 existingTokenId = userPathToTokenId[to][pathId];
        require(existingTokenId == 0, "Certificate already minted for this user/path.");

        uint256 tokenId = _tokenIdCounter.current() + TOKEN_ID_OFFSET;
        console.log("Token ID to mint:", tokenId);
        console.log("Counter value before increment:", _tokenIdCounter.current());

        _tokenIdCounter.increment();
        console.log("Counter value after increment:", _tokenIdCounter.current());

        _safeMint(to, tokenId);
        console.log("Token minted: SUCCESS");

        userPathToTokenId[to][pathId] = tokenId;
        console.log("Tracking updated: SUCCESS");
        console.log("=== MINT COMPLETE (New Mint) ===");
    }

    function burn(uint256 tokenId) public {
        console.log("=== BURN START ===");
        console.log("Token ID:", tokenId);
        console.log("Caller:", msg.sender);

        address tokenOwner = ownerOf(tokenId);
        console.log("Token owner:", tokenOwner);

        bool isOwner = msg.sender == tokenOwner;
        bool isApproved = getApproved(tokenId) == msg.sender;
        bool isApprovedForAll = isApprovedForAll(tokenOwner, msg.sender);

        console.log("Is owner:", isOwner);
        console.log("Is approved:", isApproved);
        console.log("Is approved for all:", isApprovedForAll);

        require(isOwner || isApproved || isApprovedForAll, "Not authorized to burn");
        console.log("Authorization: PASSED");

        _burn(tokenId);
        console.log("=== BURN COMPLETE ===");
    }

    function tokenURI(uint256 tokenId)
        public
        view
        override(ERC721, ERC721URIStorage)
        returns (string memory)
    {
        console.log("Getting URI for token:", tokenId);
        return super.tokenURI(tokenId);
    }

    function supportsInterface(bytes4 interfaceId)
        public
        view
        override(ERC721, ERC721URIStorage)
        returns (bool)
    {
        return super.supportsInterface(interfaceId);
    }

    function getCurrentTokenId() public view returns (uint256) {
        uint256 current = _tokenIdCounter.current() + TOKEN_ID_OFFSET;
        console.log("Current counter value:", _tokenIdCounter.current());
        console.log("Current token ID (with offset):", current);
        return current;
    }

    function hasUserMinted(address user, uint256 pathId) public view returns (bool) {
        uint256 tokenId = userPathToTokenId[user][pathId];
        bool minted = tokenId != 0;
        console.log("Mint check - User:", user);
        console.log("Path:", pathId);
        console.log("Stored token ID:", tokenId);
        console.log("Has minted:", minted);
        return minted;
    }

    function getTotalSupply() public view returns (uint256) {
        uint256 supply = _tokenIdCounter.current();
        console.log("Total minted (counter value):", supply);
        console.log("Actual token IDs range from:", TOKEN_ID_OFFSET, "to:", supply > 0 ? supply + TOKEN_ID_OFFSET - 1 : 0);
        return supply;
    }
}