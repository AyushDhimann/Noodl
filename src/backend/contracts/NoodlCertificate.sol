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

    // FIX: Store the tokenId for a given user and path. 0 means not minted.
    mapping(address => mapping(uint256 => uint256)) public userPathToTokenId;

    constructor(address initialOwner)
        ERC721("Noodl Certificate", "NOODL")
        Ownable(initialOwner)
    {
        // FIX: Start token counter at 1, so we can use 0 as a "not minted" sentinel value.
        _tokenIdCounter.increment();
        console.log("NoodlCertificate deployed! Owner:", initialOwner);
        console.log("Contract address:", address(this));
    }

    function safeMint(address to, uint256 pathId, string memory uri) public onlyOwner {
        console.log("=== MINT START ===");
        console.log("Recipient:", to);
        console.log("Path ID:", pathId);
        console.log("URI:", uri);

        uint256 existingTokenId = userPathToTokenId[to][pathId];

        // If a token ID is already stored for this user/path, just update the metadata.
        // This prevents errors in development if the database is reset but the chain is not.
        if (existingTokenId != 0) {
            console.log("Token already exists (ID: %s), updating URI.", existingTokenId);
            _setTokenURI(existingTokenId, uri);
            console.log("URI updated: SUCCESS");
            console.log("=== MINT COMPLETE (URI Update) ===");
        } else {
            // Otherwise, mint a new token.
            uint256 tokenId = _tokenIdCounter.current();
            console.log("Token ID to mint:", tokenId);

            _tokenIdCounter.increment();
            console.log("Counter after increment:", _tokenIdCounter.current());

            _safeMint(to, tokenId);
            console.log("Token minted: SUCCESS");

            _setTokenURI(tokenId, uri);
            console.log("URI set: SUCCESS");

            // Record the newly minted token ID for this user and path.
            userPathToTokenId[to][pathId] = tokenId;
            console.log("Tracking updated: SUCCESS");
            console.log("=== MINT COMPLETE (New Mint) ===");
        }
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
        uint256 current = _tokenIdCounter.current();
        console.log("Current token counter:", current);
        return current;
    }

    function hasUserMinted(address user, uint256 pathId) public view returns (bool) {
        bool minted = userPathToTokenId[user][pathId] != 0;
        console.log("Mint check - User:", user);
        console.log("Path:", pathId);
        console.log("Has minted:", minted);
        return minted;
    }

    function getTotalSupply() public view returns (uint256) {
        uint256 supply = _tokenIdCounter.current();
        console.log("Total supply:", supply);
        return supply;
    }
}