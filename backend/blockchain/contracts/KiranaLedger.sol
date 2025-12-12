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
        TransactionType txType;
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

    // State Variables
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
        bytes32 voiceHash,
        uint256 amount,
        uint8 txType
    );
    event BatchTransactionRecorded(
        uint256 indexed id,
        address indexed shopAddress,
        bytes32 batchHash,
        uint256 totalAmount
    );
    event CreditScoreUpdated(
        address indexed shopAddress,
        uint256 totalSales,
        uint256 creditGiven
    );
    event CooperativeCreated(uint256 indexed id, string name);
    event ShopkeeperJoinedCooperative(
        uint256 indexed coopId,
        address indexed shopAddress
    );

    // Modifiers
    modifier onlyRegistered() {
        require(
            registeredShopkeepers[msg.sender],
            "Shopkeeper not registered"
        );
        _;
    }

    modifier onlyAdmin() {
        require(msg.sender == admin, "Only admin can perform this action");
        _;
    }

    // Constructor
    constructor() {
        admin = msg.sender;
        nextTransactionId = 1;
    }

    // Functions
    function registerShopkeeper() external {
        require(
            !registeredShopkeepers[msg.sender],
            "Shopkeeper already registered"
        );
        registeredShopkeepers[msg.sender] = true;
        
        // Initialize credit score data
        shopkeeperCreditScores[msg.sender] = CreditScoreData({
            shopAddress: msg.sender,
            totalSales: 0,
            creditGiven: 0,
            creditRepaid: 0,
            txFrequency: 0,
            lastUpdated: block.timestamp
        });

        emit ShopkeeperRegistered(msg.sender);
    }

    function recordTransaction(
        bytes32 voiceHash,
        address shopAddress,
        uint256 amount,
        uint8 txType
    ) external returns (uint256) {
        require(
            registeredShopkeepers[shopAddress],
            "Shopkeeper not registered"
        );
        require(txType <= uint8(TransactionType.REPAY), "Invalid transaction type");

        uint256 txId = nextTransactionId;
        transactions[txId] = Transaction({
            id: txId,
            shopAddress: shopAddress,
            amount: amount,
            timestamp: block.timestamp,
            txType: TransactionType(txType),
            voiceHash: voiceHash
        });

        nextTransactionId++;

        emit TransactionRecorded(txId, shopAddress, voiceHash, amount, txType);
        return txId;
    }

    function recordBatchTransactions(
        bytes32 batchHash,
        address shopAddress,
        uint256 totalAmount
    ) external returns (uint256) {
        require(
            registeredShopkeepers[shopAddress],
            "Shopkeeper not registered"
        );

        uint256 txId = nextTransactionId;
        transactions[txId] = Transaction({
            id: txId,
            shopAddress: shopAddress,
            amount: totalAmount,
            timestamp: block.timestamp,
            txType: TransactionType.SALE,
            voiceHash: batchHash
        });

        nextTransactionId++;

        emit BatchTransactionRecorded(txId, shopAddress, batchHash, totalAmount);
        return txId;
    }

    function getTransaction(uint256 txId)
        external
        view
        returns (Transaction memory)
    {
        require(transactions[txId].id != 0, "Transaction does not exist");
        return transactions[txId];
    }

    function updateCreditScoreData(
        address shopAddress,
        CreditScoreData memory data
    ) external {
        require(
            registeredShopkeepers[shopAddress],
            "Shopkeeper not registered"
        );

        data.lastUpdated = block.timestamp;
        shopkeeperCreditScores[shopAddress] = data;

        emit CreditScoreUpdated(shopAddress, data.totalSales, data.creditGiven);
    }

    function getCreditScore(address shopAddress)
        external
        view
        returns (CreditScoreData memory)
    {
        require(
            registeredShopkeepers[shopAddress],
            "Shopkeeper not registered"
        );
        return shopkeeperCreditScores[shopAddress];
    }

    function createCooperative(
        uint256 coopId,
        string memory name,
        bytes32 termsHash,
        uint256 splitPercent
    ) external onlyAdmin {
        require(cooperatives[coopId].id == 0, "Cooperative already exists");
        require(splitPercent <= 100, "Split percent must be <= 100");

        cooperatives[coopId] = Cooperative({
            id: coopId,
            name: name,
            termsHash: termsHash,
            revenueSplitPercent: splitPercent
        });

        emit CooperativeCreated(coopId, name);
    }

    function joinCooperative(uint256 coopId, address shopAddress) external {
        require(cooperatives[coopId].id != 0, "Cooperative does not exist");
        require(
            registeredShopkeepers[shopAddress],
            "Shopkeeper not registered"
        );
        require(
            !cooperativeMembers[coopId][shopAddress],
            "Already a member"
        );

        cooperativeMembers[coopId][shopAddress] = true;

        emit ShopkeeperJoinedCooperative(coopId, shopAddress);
    }

    function getCooperative(uint256 coopId)
        external
        view
        returns (Cooperative memory)
    {
        require(cooperatives[coopId].id != 0, "Cooperative does not exist");
        return cooperatives[coopId];
    }

    function isCooperativeMember(uint256 coopId, address shopAddress)
        external
        view
        returns (bool)
    {
        return cooperativeMembers[coopId][shopAddress];
    }

    function isShopkeeperRegistered(address shopAddress)
        external
        view
        returns (bool)
    {
        return registeredShopkeepers[shopAddress];
    }
}



