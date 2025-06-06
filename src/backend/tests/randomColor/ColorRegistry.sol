// SPDX-License-Identifier: MIT
pragma solidity ^0.8.9;

contract ColorRegistry {
    struct ColorInfo {
        string hexCode;
        string description;
        address submitter;
        uint256 timestamp;
    }

    // To keep track of all colors and allow fetching by index
    ColorInfo[] public allColors;
    // Mapping for quick lookup if hex code is already stored (optional, adds gas)
    mapping(string => bool) public isHexCodeStored;

    event ColorAdded(
        uint256 indexed id,
        string hexCode,
        string description,
        address submitter
    );

    // Only contract owner (deployer) can add colors initially,
    // or you can make it public if anyone can add.
    // For this app, your backend will be the one adding.
    address public owner;

    modifier onlyOwner() {
        require(msg.sender == owner, "Not the contract owner");
        _;
    }

    constructor() {
        owner = msg.sender; // The deployer is the owner
    }

    function addColor(string memory _hexCode, string memory _description) public onlyOwner {
        // Optional: check if hex code already exists to prevent duplicates
        // require(!isHexCodeStored[_hexCode], "Hex code already stored");

        allColors.push(ColorInfo({
            hexCode: _hexCode,
            description: _description,
            submitter: msg.sender, // This will be your backend's wallet address
            timestamp: block.timestamp
        }));
        isHexCodeStored[_hexCode] = true;

        emit ColorAdded(allColors.length - 1, _hexCode, _description, msg.sender);
    }

    function getColorCount() public view returns (uint256) {
        return allColors.length;
    }

    function getColorById(uint256 _id) public view returns (string memory hexCode, string memory description, address submitter, uint256 timestamp) {
        require(_id < allColors.length, "Invalid ID");
        ColorInfo storage color = allColors[_id];
        return (color.hexCode, color.description, color.submitter, color.timestamp);
    }

    // Function to allow owner to withdraw any accidental ETH sent to the contract
    function withdraw() public onlyOwner {
        payable(owner).transfer(address(this).balance);
    }
}