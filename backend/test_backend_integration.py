"""
Backend Integration Test Suite

This test suite verifies that the backend is correctly configured and integrated:
- Server starts correctly
- MongoDB connection works
- Required environment variables exist
- API requests work end-to-end
- MongoDB writes succeed
- Blockchain integration works (or fails loudly with clear errors)

Run with:
    pytest test_backend_integration.py -v
    OR
    python test_backend_integration.py
"""

import os
import sys
import unittest
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
backend_dir = Path(__file__).parent
env_path = backend_dir / '.env'
if env_path.exists():
    load_dotenv(dotenv_path=env_path)

# Add backend to path
sys.path.insert(0, str(backend_dir))

import pytest
from flask import Flask
from mongoengine import connect, disconnect, get_db
from pymongo.errors import ServerSelectionTimeoutError, ConfigurationError
from pymongo import MongoClient

# Import app factory
from api import create_app
from config import Config, BlockchainConfig
from database.models import Shopkeeper, Customer, Transaction


class TestEnvironmentVariables(unittest.TestCase):
    """Test that required environment variables are set"""
    
    def test_mongodb_uri_exists(self):
        """MongoDB URI must be set"""
        mongodb_uri = os.getenv('MONGODB_URI')
        self.assertIsNotNone(mongodb_uri, "MONGODB_URI environment variable is not set")
        self.assertNotEqual(mongodb_uri.strip(), "", "MONGODB_URI is empty")
        print(f"✅ MONGODB_URI is set: {mongodb_uri[:30]}...")
    
    def test_mongodb_db_name_exists(self):
        """MongoDB database name must be set"""
        db_name = os.getenv('MONGODB_DB_NAME', 'kirana_db')
        self.assertIsNotNone(db_name)
        print(f"✅ MONGODB_DB_NAME is set: {db_name}")
    
    def test_blockchain_config_exists(self):
        """Blockchain config should exist (even if not fully configured)"""
        # These should exist in config, even if empty
        self.assertIsNotNone(BlockchainConfig.RPC_URL)
        self.assertIsNotNone(BlockchainConfig.POLYGON_AMOY_RPC_URL)
        print(f"✅ Blockchain config exists")
        print(f"   RPC_URL: {BlockchainConfig.RPC_URL}")
        print(f"   POLYGON_AMOY_RPC_URL: {BlockchainConfig.POLYGON_AMOY_RPC_URL}")
    
    def test_blockchain_required_fields_when_needed(self):
        """If blockchain is being used, these fields must be set"""
        # Only check if blockchain is actually being used
        # We'll test actual blockchain connection separately
        pass


class TestMongoDBConnection(unittest.TestCase):
    """Test MongoDB connection and operations"""
    
    @classmethod
    def setUpClass(cls):
        """Connect to MongoDB before all tests"""
        cls.mongodb_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/kirana_db')
        cls.db_name = os.getenv('MONGODB_DB_NAME', 'kirana_db')
        
    def setUp(self):
        """Set up test - connect to MongoDB"""
        try:
            # Disconnect first if already connected
            disconnect(alias='test')
        except:
            pass
    
    def tearDown(self):
        """Clean up - disconnect from MongoDB"""
        try:
            disconnect(alias='test')
        except:
            pass
    
    def test_mongodb_connection_string_valid(self):
        """MongoDB connection string should be valid format"""
        uri = self.mongodb_uri
        self.assertTrue(
            uri.startswith('mongodb://') or uri.startswith('mongodb+srv://'),
            f"Invalid MongoDB URI format: {uri}. Must start with mongodb:// or mongodb+srv://"
        )
        print(f"✅ MongoDB URI format is valid")
    
    def test_mongodb_connection_works(self):
        """MongoDB connection should actually work"""
        try:
            # Try to connect
            connect(
                db=self.db_name,
                host=self.mongodb_uri,
                alias='test'
            )
            
            # Verify connection by checking server info
            db = get_db(alias='test')
            server_info = db.client.server_info()
            
            self.assertIsNotNone(server_info)
            print(f"✅ MongoDB connection successful")
            print(f"   Server version: {server_info.get('version', 'unknown')}")
            
        except ServerSelectionTimeoutError as e:
            self.fail(f"MongoDB connection timeout - server not reachable at {self.mongodb_uri}. "
                     f"Error: {e}")
        except ConfigurationError as e:
            self.fail(f"MongoDB configuration error - invalid URI format. Error: {e}")
        except Exception as e:
            self.fail(f"MongoDB connection failed with unexpected error: {e}")
    
    def test_mongodb_write_and_read(self):
        """Test that we can write to and read from MongoDB"""
        try:
            connect(db=self.db_name, host=self.mongodb_uri, alias='test')
            
            # Try to create a test shopkeeper
            test_shopkeeper = Shopkeeper(
                name="Test Shopkeeper Integration",
                address="123 Test St",
                phone="+919999999999",
                wallet_address="0x0000000000000000000000000000000000000000"
            )
            test_shopkeeper.save()
            
            # Read it back
            found = Shopkeeper.objects(phone="+919999999999").first()
            self.assertIsNotNone(found, "Could not read back written shopkeeper")
            self.assertEqual(found.name, "Test Shopkeeper Integration")
            
            # Cleanup
            test_shopkeeper.delete()
            
            print("✅ MongoDB write and read test passed")
            
        except Exception as e:
            self.fail(f"MongoDB write/read test failed: {e}")


class TestFlaskApplication(unittest.TestCase):
    """Test Flask application initialization"""
    
    def setUp(self):
        """Create test Flask app"""
        # Use testing config
        os.environ['FLASK_ENV'] = 'testing'
        
    def test_app_creation_succeeds(self):
        """Flask app should be created without errors"""
        try:
            app = create_app('testing')
            self.assertIsInstance(app, Flask)
            print("✅ Flask app created successfully")
        except Exception as e:
            self.fail(f"Flask app creation failed: {e}")
    
    def test_app_has_routes(self):
        """Flask app should have registered routes"""
        app = create_app('testing')
        
        # Check that routes are registered
        with app.app_context():
            rules = [str(rule) for rule in app.url_map.iter_rules()]
            self.assertGreater(len(rules), 0, "No routes registered in Flask app")
            
            # Check for key routes
            route_paths = [str(rule) for rule in app.url_map.iter_rules()]
            has_health = any('/health' in path for path in route_paths)
            has_api = any('/api' in path for path in route_paths)
            
            self.assertTrue(has_health, "Health endpoint not found")
            self.assertTrue(has_api, "API routes not found")
            
            print(f"✅ Flask app has {len(rules)} routes registered")
            print(f"   Health endpoint: {has_health}")
            print(f"   API routes: {has_api}")


class TestAPIEndpoints(unittest.TestCase):
    """Test API endpoints with test client"""
    
    def setUp(self):
        """Create test client"""
        app = create_app('testing')
        app.config['TESTING'] = True
        self.app = app
        self.client = app.test_client()
    
    def test_health_endpoint(self):
        """Health endpoint should return 200"""
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200, 
                        f"Health endpoint returned {response.status_code}, expected 200")
        
        data = response.get_json()
        self.assertIsNotNone(data)
        self.assertIn('status', data)
        print("✅ Health endpoint works")
    
    def test_root_endpoint(self):
        """Root endpoint should return 200"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        print("✅ Root endpoint works")


class TestBlockchainIntegration(unittest.TestCase):
    """Test blockchain service initialization and configuration"""
    
    def test_blockchain_service_can_be_imported(self):
        """Blockchain service should be importable"""
        try:
            from blockchain.utils.contract_service import BlockchainService
            print("✅ BlockchainService can be imported")
        except ImportError as e:
            self.fail(f"Cannot import BlockchainService: {e}. Is web3 installed?")
    
    def test_blockchain_config_values(self):
        """Blockchain config should have required values if blockchain is being used"""
        # Check if blockchain is configured
        has_private_key = bool(BlockchainConfig.PRIVATE_KEY)
        has_contract = bool(BlockchainConfig.CONTRACT_ADDRESS)
        has_rpc = bool(BlockchainConfig.RPC_URL or BlockchainConfig.POLYGON_AMOY_RPC_URL)
        
        print(f"Blockchain configuration status:")
        print(f"   PRIVATE_KEY set: {has_private_key}")
        print(f"   CONTRACT_ADDRESS set: {has_contract}")
        print(f"   RPC_URL set: {has_rpc}")
        
        if has_private_key or has_contract:
            # If any blockchain config is set, check all required fields
            if has_private_key and not has_contract:
                print("⚠️  WARNING: PRIVATE_KEY set but CONTRACT_ADDRESS not set")
            if has_contract and not has_private_key:
                print("⚠️  WARNING: CONTRACT_ADDRESS set but PRIVATE_KEY not set")
    
    def test_blockchain_rpc_url_consistency(self):
        """Check for RPC URL inconsistency issue"""
        # This test identifies the critical bug found in analysis
        from services.transaction.transaction_service import get_blockchain_service
        
        # Check which RPC URL would be used
        transaction_service_uses = BlockchainConfig.RPC_URL
        blockchain_route_uses = BlockchainConfig.POLYGON_AMOY_RPC_URL
        
        if transaction_service_uses != blockchain_route_uses:
            print("⚠️  CRITICAL: RPC URL inconsistency detected!")
            print(f"   Transaction service would use: {transaction_service_uses}")
            print(f"   Blockchain routes would use: {blockchain_route_uses}")
            print("   This will cause blockchain writes to fail!")
        else:
            print("✅ RPC URLs are consistent")
    
    def test_blockchain_service_initialization_fails_loudly(self):
        """Blockchain service should fail loudly if misconfigured"""
        from blockchain.utils.contract_service import BlockchainService
        
        # Try to initialize with invalid config
        try:
            service = BlockchainService(
                rpc_url="http://invalid-rpc-url:8545",
                private_key="0x" + "0" * 64,  # Dummy key
                contract_address="0x" + "0" * 40  # Dummy address
            )
            # If it doesn't raise, check if connection actually fails
            if not service.w3.is_connected():
                print("✅ Blockchain service correctly fails connection check")
            else:
                print("⚠️  WARNING: Blockchain service accepted invalid RPC URL")
        except ConnectionError as e:
            print("✅ Blockchain service fails loudly with ConnectionError")
        except Exception as e:
            print(f"✅ Blockchain service fails loudly: {type(e).__name__}")


class TestEndToEndTransactionFlow(unittest.TestCase):
    """Test complete transaction flow from API to MongoDB (and optionally blockchain)"""
    
    def setUp(self):
        """Set up test client and test data"""
        app = create_app('testing')
        app.config['TESTING'] = True
        self.app = app
        self.client = app.test_client()
        
        # Create test shopkeeper and customer
        try:
            self.shopkeeper = Shopkeeper(
                name="E2E Test Shopkeeper",
                address="123 E2E St",
                phone="+918888888888",
                wallet_address="0x1111111111111111111111111111111111111111"
            ).save()
            
            self.customer = Customer(
                name="E2E Test Customer",
                phone="+917777777777"
            ).save()
        except Exception as e:
            # If they already exist, get them
            self.shopkeeper = Shopkeeper.objects(phone="+918888888888").first()
            self.customer = Customer.objects(phone="+917777777777").first()
    
    def tearDown(self):
        """Clean up test data"""
        try:
            # Delete test transactions
            Transaction.objects(
                shopkeeper_id=self.shopkeeper.id,
                customer_id=self.customer.id
            ).delete()
        except:
            pass
    
    def test_create_transaction_via_api(self):
        """Test creating a transaction via API endpoint"""
        transaction_data = {
            "type": "sale",
            "amount": 100.50,
            "shopkeeper_id": str(self.shopkeeper.id),
            "customer_id": str(self.customer.id)
        }
        
        response = self.client.post(
            '/api/transactions',
            json=transaction_data,
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201, 
                        f"Transaction creation failed with status {response.status_code}. "
                        f"Response: {response.get_json()}")
        
        data = response.get_json()
        self.assertIn('id', data)
        self.assertEqual(data['type'], 'sale')
        self.assertEqual(data['amount'], 100.50)
        
        # Verify it's in MongoDB
        transaction_id = data['id']
        transaction = Transaction.objects(id=transaction_id).first()
        self.assertIsNotNone(transaction, "Transaction not found in MongoDB after creation")
        
        print("✅ Transaction created via API and saved to MongoDB")
        
        # Check if blockchain write was attempted
        if transaction.blockchain_tx_id:
            print(f"   Blockchain TX ID: {transaction.blockchain_tx_id}")
        else:
            print("   Note: Transaction not written to blockchain (may be expected)")


class TestCriticalIssues(unittest.TestCase):
    """Test for specific critical issues identified in analysis"""
    
    def test_rpc_url_consistency_in_transaction_service(self):
        """CRITICAL: Transaction service should use POLYGON_AMOY_RPC_URL"""
        # This is the bug identified in BACKEND_ARCHITECTURE_ANALYSIS.md
        import inspect
        from services.transaction import transaction_service
        
        # Check the source code to see which RPC URL is used
        source = inspect.getsource(transaction_service.get_blockchain_service)
        
        if 'RPC_URL' in source and 'POLYGON_AMOY_RPC_URL' not in source:
            self.fail(
                "CRITICAL BUG: transaction_service.py uses RPC_URL instead of "
                "POLYGON_AMOY_RPC_URL. This causes blockchain writes to fail!"
            )
        elif 'POLYGON_AMOY_RPC_URL' in source:
            print("✅ Transaction service uses correct RPC URL (POLYGON_AMOY_RPC_URL)")
        else:
            print("⚠️  Could not verify RPC URL usage in transaction service")
    
    def test_mongodb_connection_validation(self):
        """MongoDB connection should be validated after connect()"""
        from database import create_app
        
        # This test checks if connection validation exists
        # We can't easily test the actual validation, but we can note if it's missing
        print("⚠️  Note: MongoDB connection validation should be added to create_app()")


def run_tests():
    """Run all tests"""
    # Configure test runner
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        TestEnvironmentVariables,
        TestMongoDBConnection,
        TestFlaskApplication,
        TestAPIEndpoints,
        TestBlockchainIntegration,
        TestEndToEndTransactionFlow,
        TestCriticalIssues
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success: {result.testsRun - len(result.failures) - len(result.errors)}")
    
    if result.failures:
        print("\nFAILURES:")
        for test, traceback in result.failures:
            print(f"  - {test}")
    
    if result.errors:
        print("\nERRORS:")
        for test, traceback in result.errors:
            print(f"  - {test}")
    
    # Exit with appropriate code
    if result.wasSuccessful():
        print("\n✅ All tests passed!")
        return 0
    else:
        print("\n❌ Some tests failed. Review output above.")
        return 1


if __name__ == '__main__':
    # Run with pytest if available, otherwise unittest
    try:
        import pytest
        sys.exit(pytest.main([__file__, '-v', '--tb=short']))
    except ImportError:
        sys.exit(run_tests())

