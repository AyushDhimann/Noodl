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
        require(pathContentHashes[_pathId] == 0, "Path already registered");
        pathContentHashes[_pathId] = _contentHash;
        emit PathRegistered(_pathId, _contentHash);
    }
}