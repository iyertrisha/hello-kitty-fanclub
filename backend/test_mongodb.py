"""
MongoDB Connection Test Script

This script verifies that MongoDB is accessible and the connection string is correct.
Run this before starting the backend to ensure database connectivity.

Usage:
    python test_mongodb.py
"""
from pymongo import MongoClient
from config import Config
import sys

def test_mongodb_connection():
    """Test MongoDB connection using the same configuration as the app"""
    try:
        print("Testing MongoDB connection...")
        print(f"URI: {Config.MONGODB_URI}")
        print(f"Database: {Config.MONGODB_DB_NAME}")
        print()
        
        # Connect to MongoDB
        client = MongoClient(Config.MONGODB_URI, serverSelectionTimeoutMS=5000)
        
        # Test connection with ping
        db = client[Config.MONGODB_DB_NAME]
        result = db.command('ping')
        
        # Get server info
        server_info = client.server_info()
        
        # List databases to verify access
        db_list = client.list_database_names()
        
        print("[SUCCESS] MongoDB connected successfully!")
        print(f"   Database: {Config.MONGODB_DB_NAME}")
        print(f"   Server version: {server_info.get('version', 'unknown')}")
        print(f"   Ping result: {result}")
        print(f"   Available databases: {', '.join(db_list[:5])}{'...' if len(db_list) > 5 else ''}")
        
        # Verify target database exists or can be created
        if Config.MONGODB_DB_NAME in db_list:
            print(f"   [OK] Target database '{Config.MONGODB_DB_NAME}' exists")
        else:
            print(f"   [WARNING] Target database '{Config.MONGODB_DB_NAME}' does not exist (will be created on first use)")
        
        client.close()
        return True
        
    except Exception as e:
        print("[ERROR] MongoDB connection failed!")
        print(f"   Error: {e}")
        print()
        print("Troubleshooting steps:")
        print("   1. Check if MongoDB is running:")
        print("      PowerShell: Get-Service -Name MongoDB")
        print("      Or: Test-NetConnection -ComputerName localhost -Port 27017")
        print("   2. Start MongoDB if needed:")
        print("      PowerShell: Start-Service MongoDB")
        print("   3. Verify MONGODB_URI in .env file matches your MongoDB instance")
        print("   4. Check MongoDB logs for errors")
        return False

if __name__ == '__main__':
    success = test_mongodb_connection()
    sys.exit(0 if success else 1)

