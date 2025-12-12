// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract KiranaLedger {
    // Enums
    enum TransactionType {
        SALE,
        CREDIT,
        REPAY
    }

    // Structs
    struct Transaction {
        uint256 id;
        address shopAddress;
        uint256 amount;
        uint256 timestamp;
        uint8 txType;
        bytes32 voiceHash;
    }

    struct CreditScoreData {
        address shopAddress;
        uint256 totalSales;
        uint256 creditGiven;
        uint256 creditRepaid;
        uint256 txFrequency;
        uint256 lastUpdated;
    }

    struct Cooperative {
        uint256 id;
        string name;
        bytes32 termsHash;
        uint256 revenueSplitPercent;
    }

    // State variables
    mapping(uint256 => Transaction) public transactions;
    mapping(address => bool) public registeredShopkeepers;
    mapping(address => CreditScoreData) public shopkeeperCreditScores;
    mapping(uint256 => Cooperative) public cooperatives;
    mapping(uint256 => mapping(address => bool)) public cooperativeMembers;
    
    uint256 public nextTransactionId;
    address public admin;

    // Events
    event ShopkeeperRegistered(address indexed shopAddress);
    event TransactionRecorded(
        uint256 indexed id,
        address indexed shopAddress,
        uint256 amount,
        uint8 txType,
        bytes32 voiceHash
    );
    event BatchTransactionsRecorded(
        bytes32 indexed batchHash,
        address indexed shopAddress,
        uint256 totalAmount
    );
    event CreditScoreUpdated(address indexed shopAddress, uint256 totalSales, uint256 creditGiven, uint256 creditRepaid);
    event CooperativeCreated(uint256 indexed coopId, string name);
    event CooperativeJoined(uint256 indexed coopId, address indexed shopAddress);

    constructor() {
        admin = msg.sender;
    }

    // Modifiers
    modifier onlyRegistered() {
        require(registeredShopkeepers[msg.sender], "Shopkeeper not registered");
        _;
    }

    modifier onlyAdmin() {
        require(msg.sender == admin, "Only admin can perform this action");
        _;
    }

    // Shopkeeper registration
    function registerShopkeeper() external {
        require(!registeredShopkeepers[msg.sender], "Shopkeeper already registered");
        registeredShopkeepers[msg.sender] = true;
        emit ShopkeeperRegistered(msg.sender);
    }

    // Transaction recording
    function recordTransaction(
        bytes32 voiceHash,
        address shopAddress,
        uint256 amount,
        uint8 txType
    ) external onlyRegistered {
        require(shopAddress == msg.sender, "Can only record transactions for yourself");
        require(amount > 0, "Amount must be greater than 0");
        require(txType <= 2, "Invalid transaction type");

        uint256 txId = nextTransactionId;
        transactions[txId] = Transaction({
            id: txId,
            shopAddress: shopAddress,
            amount: amount,
            timestamp: block.timestamp,
            txType: txType,
            voiceHash: voiceHash
        });

        nextTransactionId++;

        emit TransactionRecorded(txId, shopAddress, amount, txType, voiceHash);
    }

    // Batch transaction recording
    function recordBatchTransactions(
        bytes32 batchHash,
        address shopAddress,
        uint256 totalAmount
    ) external onlyRegistered {
        require(shopAddress == msg.sender, "Can only record batch transactions for yourself");
        require(totalAmount > 0, "Total amount must be greater than 0");

        emit BatchTransactionsRecorded(batchHash, shopAddress, totalAmount);
    }

    // Credit score management
    function updateCreditScoreData(
        address shopAddress,
        CreditScoreData memory creditData
    ) external onlyRegistered {
        require(shopAddress == msg.sender, "Can only update your own credit score");
        
        shopkeeperCreditScores[shopAddress] = CreditScoreData({
            shopAddress: shopAddress,
            totalSales: creditData.totalSales,
            creditGiven: creditData.creditGiven,
            creditRepaid: creditData.creditRepaid,
            txFrequency: creditData.txFrequency,
            lastUpdated: block.timestamp
        });

        emit CreditScoreUpdated(shopAddress, creditData.totalSales, creditData.creditGiven, creditData.creditRepaid);
    }

    // Cooperative management
    function createCooperative(
        uint256 coopId,
        string memory name,
        bytes32 termsHash,
        uint256 revenueSplitPercent
    ) external onlyAdmin {
        require(cooperatives[coopId].id == 0, "Cooperative already exists");
        require(revenueSplitPercent <= 100, "Revenue split cannot exceed 100%");

        cooperatives[coopId] = Cooperative({
            id: coopId,
            name: name,
            termsHash: termsHash,
            revenueSplitPercent: revenueSplitPercent
        });

        emit CooperativeCreated(coopId, name);
    }

    function joinCooperative(uint256 coopId) external onlyRegistered {
        require(cooperatives[coopId].id != 0, "Cooperative does not exist");
        require(!cooperativeMembers[coopId][msg.sender], "Already a member of this cooperative");

        cooperativeMembers[coopId][msg.sender] = true;
        emit CooperativeJoined(coopId, msg.sender);
    }

    // View functions
    function getTransaction(uint256 txId) external view returns (
        uint256 id,
        address shopAddress,
        uint256 amount,
        uint256 timestamp,
        uint8 txType,
        bytes32 voiceHash
    ) {
        Transaction memory transaction = transactions[txId];
        return (transaction.id, transaction.shopAddress, transaction.amount, transaction.timestamp, transaction.txType, transaction.voiceHash);
    }

    function getCreditScore(address shopAddress) external view returns (
        address,
        uint256 totalSales,
        uint256 creditGiven,
        uint256 creditRepaid,
        uint256 txFrequency,
        uint256 lastUpdated
    ) {
        CreditScoreData memory score = shopkeeperCreditScores[shopAddress];
        return (score.shopAddress, score.totalSales, score.creditGiven, score.creditRepaid, score.txFrequency, score.lastUpdated);
    }

    function getCooperative(uint256 coopId) external view returns (
        uint256 id,
        string memory name,
        bytes32 termsHash,
        uint256 revenueSplitPercent
    ) {
        Cooperative memory coop = cooperatives[coopId];
        return (coop.id, coop.name, coop.termsHash, coop.revenueSplitPercent);
    }

    function isShopkeeperRegistered(address shopAddress) external view returns (bool) {
        return registeredShopkeepers[shopAddress];
    }

    function isCooperativeMember(uint256 coopId, address shopAddress) external view returns (bool) {
        return cooperativeMembers[coopId][shopAddress];
    }
}
