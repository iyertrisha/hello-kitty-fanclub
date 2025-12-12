import json
import os
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from web3 import Web3
from web3.exceptions import ContractLogicError
from eth_account import Account

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BlockchainService:
    """Service class to interact with KiranaLedger smart contract"""

    def __init__(self, rpc_url: str, private_key: str, contract_address: str):
        """
        Initialize blockchain service

        Args:
            rpc_url: RPC URL for the blockchain network
            private_key: Private key for signing transactions
            contract_address: Deployed contract address
        """
        try:
            # Initialize Web3
            self.w3 = Web3(Web3.HTTPProvider(rpc_url))

            if not self.w3.is_connected():
                raise ConnectionError(f"Failed to connect to blockchain at {rpc_url}")

            logger.info(f"✅ Connected to blockchain at {rpc_url}")

            # Load account from private key
            if private_key.startswith("0x"):
                private_key = private_key[2:]

            self.account = Account.from_key(private_key)
            self.address = self.account.address
            logger.info(f"📝 Using account: {self.address}")

            # Load contract ABI
            abi_path = Path(__file__).parent.parent / "abis" / "KiranaLedger.json"
            if not abi_path.exists():
                raise FileNotFoundError(
                    f"ABI file not found at {abi_path}. Run 'npm run compile' first."
                )

            with open(abi_path, "r") as f:
                contract_json = json.load(f)
                self.contract_abi = contract_json.get("abi", contract_json)

            # Initialize contract
            self.contract_address = Web3.to_checksum_address(contract_address)
            self.contract = self.w3.eth.contract(
                address=self.contract_address, abi=self.contract_abi
            )

            logger.info(f"📄 Contract loaded at: {self.contract_address}")

        except Exception as e:
            logger.error(f"❌ Failed to initialize BlockchainService: {str(e)}")
            raise

    def _validate_address(self, address: str) -> str:
        """Validate and return checksummed Ethereum address"""
        if not Web3.is_address(address):
            raise ValueError(f"Invalid Ethereum address: {address}")
        return Web3.to_checksum_address(address)

    def _handle_transaction(
        self, tx_function, *args, gas_limit: int = 300000
    ) -> Dict[str, Any]:
        """
        Generic transaction handler

        Args:
            tx_function: Contract function to call
            *args: Arguments for the function
            gas_limit: Gas limit for transaction

        Returns:
            Transaction receipt
        """
        try:
            # Build transaction
            nonce = self.w3.eth.get_transaction_count(self.address)

            # Get gas price
            gas_price = self.w3.eth.gas_price

            # Build transaction
            transaction = tx_function(*args).build_transaction(
                {
                    "from": self.address,
                    "nonce": nonce,
                    "gas": gas_limit,
                    "gasPrice": gas_price,
                }
            )

            # Sign transaction
            signed_txn = self.w3.eth.account.sign_transaction(
                transaction, private_key=self.account.key
            )

            # Send transaction
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.raw_transaction)
            logger.info(f"⏳ Transaction sent: {tx_hash.hex()}")

            # Wait for receipt
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
            logger.info(f"✅ Transaction confirmed in block {tx_receipt['blockNumber']}")

            return {
                "success": True,
                "tx_hash": tx_hash.hex(),
                "block_number": tx_receipt["blockNumber"],
                "gas_used": tx_receipt["gasUsed"],
            }

        except ContractLogicError as e:
            logger.error(f"❌ Contract error: {str(e)}")
            return {"success": False, "error": str(e)}
        except Exception as e:
            logger.error(f"❌ Transaction failed: {str(e)}")
            return {"success": False, "error": str(e)}

    # Write Methods

    def register_shopkeeper(self, address: Optional[str] = None) -> Dict[str, Any]:
        """Register a shopkeeper"""
        shop_address = self._validate_address(address or self.address)
        logger.info(f"Registering shopkeeper: {shop_address}")
        return self._handle_transaction(self.contract.functions.registerShopkeeper)

    def record_transaction(
        self,
        voice_hash: str,
        shop_address: str,
        amount: int,
        tx_type: int,
    ) -> Dict[str, Any]:
        """
        Record a single transaction

        Args:
            voice_hash: Hash of the voice recording (hex string or bytes32)
            shop_address: Shopkeeper's Ethereum address
            amount: Transaction amount in wei
            tx_type: Transaction type (0=SALE, 1=CREDIT, 2=REPAY)
        """
        shop_address = self._validate_address(shop_address)

        # Convert voice_hash to bytes32 if it's a string
        if isinstance(voice_hash, str):
            if voice_hash.startswith("0x"):
                voice_hash_bytes = bytes.fromhex(voice_hash[2:])
            else:
                voice_hash_bytes = bytes.fromhex(voice_hash)
        else:
            voice_hash_bytes = voice_hash

        logger.info(f"Recording transaction for {shop_address}: {amount} wei, type {tx_type}")
        return self._handle_transaction(
            self.contract.functions.recordTransaction,
            voice_hash_bytes,
            shop_address,
            amount,
            tx_type,
        )

    def record_batch_transactions(
        self, batch_hash: str, shop_address: str, total_amount: int
    ) -> Dict[str, Any]:
        """
        Record batch transactions

        Args:
            batch_hash: Hash of the batch data
            shop_address: Shopkeeper's Ethereum address
            total_amount: Total amount in wei
        """
        shop_address = self._validate_address(shop_address)

        # Convert batch_hash to bytes32
        if isinstance(batch_hash, str):
            if batch_hash.startswith("0x"):
                batch_hash_bytes = bytes.fromhex(batch_hash[2:])
            else:
                batch_hash_bytes = bytes.fromhex(batch_hash)
        else:
            batch_hash_bytes = batch_hash

        logger.info(f"Recording batch for {shop_address}: {total_amount} wei")
        return self._handle_transaction(
            self.contract.functions.recordBatchTransactions,
            batch_hash_bytes,
            shop_address,
            total_amount,
        )

    def update_credit_score(
        self, shop_address: str, credit_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update credit score data for a shopkeeper

        Args:
            shop_address: Shopkeeper's Ethereum address
            credit_data: Dictionary with keys: totalSales, creditGiven, creditRepaid, txFrequency
        """
        shop_address = self._validate_address(shop_address)

        # Build credit score tuple
        credit_score_tuple = (
            shop_address,
            credit_data.get("totalSales", 0),
            credit_data.get("creditGiven", 0),
            credit_data.get("creditRepaid", 0),
            credit_data.get("txFrequency", 0),
            0,  # lastUpdated will be set by contract
        )

        logger.info(f"Updating credit score for {shop_address}")
        return self._handle_transaction(
            self.contract.functions.updateCreditScoreData, shop_address, credit_score_tuple
        )

    def create_cooperative(
        self, coop_id: int, name: str, terms_hash: str, split_percent: int
    ) -> Dict[str, Any]:
        """
        Create a cooperative (admin only)

        Args:
            coop_id: Unique cooperative ID
            name: Cooperative name
            terms_hash: Hash of terms and conditions
            split_percent: Revenue split percentage (0-100)
        """
        # Convert terms_hash to bytes32
        if isinstance(terms_hash, str):
            if terms_hash.startswith("0x"):
                terms_hash_bytes = bytes.fromhex(terms_hash[2:])
            else:
                terms_hash_bytes = bytes.fromhex(terms_hash)
        else:
            terms_hash_bytes = terms_hash

        logger.info(f"Creating cooperative: {name} (ID: {coop_id})")
        return self._handle_transaction(
            self.contract.functions.createCooperative,
            coop_id,
            name,
            terms_hash_bytes,
            split_percent,
        )

    def join_cooperative(self, coop_id: int, shop_address: str) -> Dict[str, Any]:
        """
        Join a cooperative

        Args:
            coop_id: Cooperative ID
            shop_address: Shopkeeper's Ethereum address
        """
        shop_address = self._validate_address(shop_address)

        logger.info(f"Shopkeeper {shop_address} joining cooperative {coop_id}")
        return self._handle_transaction(
            self.contract.functions.joinCooperative, coop_id, shop_address
        )

    # Read Methods

    def get_transaction(self, tx_id: int) -> Optional[Dict[str, Any]]:
        """Get transaction by ID"""
        try:
            tx = self.contract.functions.getTransaction(tx_id).call()
            return {
                "id": tx[0],
                "shopAddress": tx[1],
                "amount": tx[2],
                "timestamp": tx[3],
                "txType": tx[4],
                "voiceHash": tx[5].hex(),
            }
        except Exception as e:
            logger.error(f"Failed to get transaction {tx_id}: {str(e)}")
            return None

    def get_credit_score(self, shop_address: str) -> Optional[Dict[str, Any]]:
        """Get credit score data for a shopkeeper"""
        try:
            shop_address = self._validate_address(shop_address)
            score = self.contract.functions.getCreditScore(shop_address).call()
            return {
                "shopAddress": score[0],
                "totalSales": score[1],
                "creditGiven": score[2],
                "creditRepaid": score[3],
                "txFrequency": score[4],
                "lastUpdated": score[5],
            }
        except Exception as e:
            logger.error(f"Failed to get credit score for {shop_address}: {str(e)}")
            return None

    def is_shopkeeper_registered(self, shop_address: str) -> bool:
        """Check if shopkeeper is registered"""
        try:
            shop_address = self._validate_address(shop_address)
            return self.contract.functions.isShopkeeperRegistered(shop_address).call()
        except Exception as e:
            logger.error(f"Failed to check registration for {shop_address}: {str(e)}")
            return False

    def get_cooperative(self, coop_id: int) -> Optional[Dict[str, Any]]:
        """Get cooperative details"""
        try:
            coop = self.contract.functions.getCooperative(coop_id).call()
            return {
                "id": coop[0],
                "name": coop[1],
                "termsHash": coop[2].hex(),
                "revenueSplitPercent": coop[3],
            }
        except Exception as e:
            logger.error(f"Failed to get cooperative {coop_id}: {str(e)}")
            return None

    def is_cooperative_member(self, coop_id: int, shop_address: str) -> bool:
        """Check if address is a cooperative member"""
        try:
            shop_address = self._validate_address(shop_address)
            return self.contract.functions.isCooperativeMember(coop_id, shop_address).call()
        except Exception as e:
            logger.error(f"Failed to check membership: {str(e)}")
            return False

    def get_next_transaction_id(self) -> int:
        """Get the next transaction ID"""
        try:
            return self.contract.functions.nextTransactionId().call()
        except Exception as e:
            logger.error(f"Failed to get next transaction ID: {str(e)}")
            return 0

    def get_account_balance(self, address: Optional[str] = None) -> int:
        """Get account balance in wei"""
        address = self._validate_address(address or self.address)
        return self.w3.eth.get_balance(address)

    def get_account_balance_eth(self, address: Optional[str] = None) -> float:
        """Get account balance in ETH"""
        balance_wei = self.get_account_balance(address)
        return self.w3.from_wei(balance_wei, "ether")



