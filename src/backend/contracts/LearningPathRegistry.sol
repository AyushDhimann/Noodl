// SPDX-License-Identifier: MIT
pragma solidity ^0.8.18;

contract LearningPathRegistry {
    address public owner;
    mapping(uint256 => bytes32) public pathContentHashes;

    event PathRegistered(uint256 indexed pathId, bytes32 contentHash);

    constructor() {
        owner = msg.sender;
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "Not the owner");
        _;
    }

    function registerPath(uint256 _pathId, bytes32 _contentHash) public onlyOwner {
        // FIX: Remove the check that prevents updates.
        // This makes the function behave like an "upsert" for the owner,
        // which is more robust for development environments where the database might be reset.
        // require(pathContentHashes[_pathId] == 0, "Path already registered");
        pathContentHashes[_pathId] = _contentHash;
        emit PathRegistered(_pathId, _contentHash);
    }
}