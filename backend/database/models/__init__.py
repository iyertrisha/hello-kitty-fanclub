"""
Database models module
Export all models for easy importing
"""
import importlib.util
from pathlib import Path

# Import from parent directory's models.py file directly
# We need to do this because we have both database/models.py and database/models/ directory
# Python treats 'models' as the package, so we import the file directly using importlib
_models_file = Path(__file__).parent.parent / 'models.py'
spec = importlib.util.spec_from_file_location('database_models', _models_file)
_models_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(_models_module)

# Import all models from the loaded module
Shopkeeper = _models_module.Shopkeeper
Transaction = _models_module.Transaction
Customer = _models_module.Customer
Cooperative = _models_module.Cooperative
Product = _models_module.Product
Location = _models_module.Location
BulkOrder = _models_module.BulkOrder
Supplier = _models_module.Supplier
SupplierOrder = _models_module.SupplierOrder
OTPVerification = _models_module.OTPVerification

__all__ = [
    'Shopkeeper',
    'Transaction',
    'Customer',
    'Cooperative',
    'Product',
    'Location',
    'BulkOrder',
    'Supplier',
    'SupplierOrder',
    'OTPVerification'
]

