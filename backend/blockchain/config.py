import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class BlockchainConfig:
    """Configuration for blockchain service"""

    # Network RPC URLs
    RPC_URL = os.getenv("RPC_URL", "http://localhost:8545")
    POLYGON_AMOY_RPC_URL = os.getenv(
        "POLYGON_AMOY_RPC_URL", "https://rpc-amoy.polygon.technology"
    )

    # Private key for transactions (should be in .env file)
    PRIVATE_KEY = os.getenv("PRIVATE_KEY", "")

    # Contract address (deployed contract address)
    CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS", "")

    # Admin wallet address
    ADMIN_ADDRESS = os.getenv("ADMIN_ADDRESS", "")

    # Chain ID
    CHAIN_ID = int(os.getenv("CHAIN_ID", "1337"))

    # Gas settings
    GAS_LIMIT = int(os.getenv("GAS_LIMIT", "3000000"))

    @classmethod
    def validate(cls, require_contract: bool = True):
        """
        Validate that required configuration is present
        
        Args:
            require_contract: If True, CONTRACT_ADDRESS is required (default: True)
                             Set to False for initial setup before deployment
        """
        errors = []

        if not cls.PRIVATE_KEY:
            errors.append("PRIVATE_KEY is not set in environment variables")
        elif len(cls.PRIVATE_KEY) < 64:
            errors.append("PRIVATE_KEY appears to be invalid (too short, expected 64 hex characters)")

        if require_contract and not cls.CONTRACT_ADDRESS:
            errors.append("CONTRACT_ADDRESS is not set in environment variables (deploy contract first)")

        # ADMIN_ADDRESS is optional - can be derived from PRIVATE_KEY if needed
        # Only warn if both are missing
        if not cls.ADMIN_ADDRESS and not cls.PRIVATE_KEY:
            errors.append("Either ADMIN_ADDRESS or PRIVATE_KEY must be set")

        if errors:
            raise ValueError(
                "Configuration validation failed:\n" + "\n".join(f"  - {e}" for e in errors)
            )

        return True


# Export configuration instance
config = BlockchainConfig()



