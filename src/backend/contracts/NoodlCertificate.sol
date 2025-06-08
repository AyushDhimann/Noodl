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

    mapping(address => mapping(uint256 => bool)) public hasMinted;

    constructor(address initialOwner)
        ERC721("Noodl Certificate", "NOODL")
        Ownable(initialOwner)
    {
        console.log("NoodlCertificate deployed! Owner:", initialOwner);
        console.log("Contract address:", address(this));
    }

    function safeMint(address to, uint256 pathId, string memory uri) public onlyOwner {
        console.log("=== MINT START ===");
        console.log("Recipient:", to);
        console.log("Path ID:", pathId);
        console.log("URI:", uri);

        require(!hasMinted[to][pathId], "Certificate already minted for this user/path");
        console.log("Duplicate check: PASSED");

        uint256 tokenId = _tokenIdCounter.current();
        console.log("Token ID to mint:", tokenId);

        _tokenIdCounter.increment();
        console.log("Counter after increment:", _tokenIdCounter.current());

        _safeMint(to, tokenId);
        console.log("Token minted: SUCCESS");

        _setTokenURI(tokenId, uri);
        console.log("URI set: SUCCESS");

        hasMinted[to][pathId] = true;
        console.log("Tracking updated: SUCCESS");
        console.log("=== MINT COMPLETE ===");
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
        bool minted = hasMinted[user][pathId];
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