import 'package:dio/dio.dart';
import 'package:path/path.dart' as path;
import 'dart:io';
import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/transaction.dart';
import '../models/product.dart';
import '../models/cooperative.dart';
import '../models/credit_score.dart';
import 'storage_service.dart';

class ApiService {
  static final ApiService _instance = ApiService._internal();
  factory ApiService() => _instance;

  final Dio _dio = Dio();
  final StorageService _storage = StorageService();
  
  // Backend URL configuration
  // For Android emulator: use 10.0.2.2 (special IP to access host machine)
  // For iOS simulator: use localhost
  // For physical device: use your computer's IP address (e.g., http://192.168.1.XXX:5000/api)
  // Find your IP with: ipconfig (Windows) or ifconfig (Mac/Linux)
  // NOTE: Using actual network IP (10.20.43.13) instead of 10.0.2.2 due to network routing issues
  static const String baseUrl = 'http://10.20.43.13:5000/api';
  static const bool useMockApi = false; // Backend is ready

  ApiService._internal() {
    _dio.options.baseUrl = baseUrl;
    _dio.options.connectTimeout = const Duration(seconds: 10);
    _dio.options.receiveTimeout = const Duration(seconds: 10);
    
    // Add interceptors for logging
    _dio.interceptors.add(LogInterceptor(
      requestBody: true,
      responseBody: true,
    ));
  }

  // Helper function for safe logging (fire-and-forget)
  void _logDebug(String location, String message, Map<String, dynamic> data, String hypothesisId) {
    try {
      http.post(
        Uri.parse('http://127.0.0.1:7242/ingest/fc2dc567-e9a9-422f-8853-acf0d309dd42'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'location': location,
          'message': message,
          'data': data,
          'timestamp': DateTime.now().millisecondsSinceEpoch,
          'sessionId': 'debug-session',
          'runId': 'run1',
          'hypothesisId': hypothesisId,
        }),
      ).then((_) {}, onError: (_) {});
    } catch (_) {
      // Ignore logging errors
    }
  }

  // Test backend connectivity
  Future<bool> testBackendConnection() async {
    try {
      final response = await _dio.get('/test');
      return response.statusCode == 200;
    } catch (e) {
      return false;
    }
  }

  // Audio upload and transcription
  Future<String> uploadAudioAndTranscribe(String audioPath, {String? language}) async {
    if (useMockApi) {
      await Future.delayed(const Duration(seconds: 2));
      return 'Mock transcription: This is a sample transaction recording.';
    }

    try {
      // Verify file exists
      final file = File(audioPath);
      if (!await file.exists()) {
        throw Exception('Audio file does not exist at path: $audioPath');
      }

      String fileName = path.basename(audioPath);
      Map<String, dynamic> formDataMap = {
        'audio': await MultipartFile.fromFile(
          audioPath,
          filename: fileName,
        ),
      };
      
      // Add language parameter if provided
      if (language != null) {
        formDataMap['language'] = language;
      }
      
      FormData formData = FormData.fromMap(formDataMap);

      // IMPORTANT: Use /transactions/transcribe (not /transcribe)
      Response response = await _dio.post(
        '/transactions/transcribe',
        data: formData,
      );
      return response.data['transcription'] ?? '';
    } catch (e) {
      print('Upload error: $e'); // Debug logging
      throw Exception('Failed to transcribe audio: $e');
    }
  }

  // Parse transcript to extract transaction fields
  Future<Map<String, dynamic>> parseTranscript(
    String transcript,
    String language, {
    String? shopkeeperId,
  }) async {
    if (useMockApi) {
      await Future.delayed(const Duration(seconds: 1));
      return {
        'type': 'credit',
        'amount': 500.0,
        'customer_id': 'customer_123',
        'customer_name': 'Mock Customer',
      };
    }

    try {
      final response = await _dio.post(
        '/transactions/parse',
        data: {
          'transcript': transcript,
          'language': language,
          if (shopkeeperId != null) 'shopkeeper_id': shopkeeperId,
        },
      );

      if (response.data['success'] == true && response.data['data'] != null) {
        return response.data['data'] as Map<String, dynamic>;
      } else {
        throw Exception('Parser returned invalid response');
      }
    } catch (e) {
      print('Parse error: $e'); // Debug logging
      throw Exception('Failed to parse transcript: $e');
    }
  }

  // Get list of customers
  Future<List<Map<String, dynamic>>> getCustomers() async {
    if (useMockApi) {
      await Future.delayed(const Duration(milliseconds: 500));
      return [
        {'id': 'customer_1', 'name': 'John Doe'},
        {'id': 'customer_2', 'name': 'Jane Smith'},
        {'id': 'customer_3', 'name': 'Bob Johnson'},
      ];
    }

    try {
      final response = await _dio.get('/customers');
      List<dynamic> data = response.data['data'] ?? response.data['customers'] ?? [];
      return data.map((json) => json as Map<String, dynamic>).toList();
    } catch (e) {
      print('Get customers error: $e'); // Debug logging
      // Return empty list on error instead of throwing
      return [];
    }
  }

  // Transaction APIs
  Future<List<Transaction>> getTransactions() async {
    if (useMockApi) {
      final local = await _storage.getTransactions();
      return local;
    }

    try {
      Response response = await _dio.get('/transactions');
      // Handle both 'data' and 'transactions' keys for backward compatibility
      List<dynamic> data = response.data['data'] ?? response.data['transactions'] ?? [];
      final transactions = data.map((json) => Transaction.fromJson(json as Map<String, dynamic>)).toList();
      return transactions;
    } catch (e) {
      // Return local data if API fails
      final local = await _storage.getTransactions();
      return local;
    }
  }

  Future<Transaction> createTransaction(Transaction transaction) async {
    if (useMockApi) {
      await _storage.saveTransaction(transaction);
      return transaction;
    }

    // STEP 1: Always save locally first (offline-first)
    await _storage.saveTransaction(transaction);
    
    // STEP 2: Attempt backend sync in background (non-blocking)
    try {
      // #region agent log
      _logDebug('api_service.dart:120', 'createTransaction entry', {'transactionId': transaction.id, 'type': transaction.type, 'amount': transaction.amount}, 'A');
      // #endregion
      
      // Ensure required backend fields are present
      final transactionData = transaction.toJson();
      if (transactionData['shopkeeper_id'] == null) {
        transactionData['shopkeeper_id'] = 'default_shopkeeper_id';  // TODO: Get from user session
      }
      if (transactionData['customer_id'] == null) {
        transactionData['customer_id'] = 'default_customer_id';  // TODO: Get from user input
      }
      
      // #region agent log
      _logDebug('api_service.dart:135', 'Before POST request', {'url': '${_dio.options.baseUrl}/transactions', 'dataKeys': transactionData.keys.toList(), 'hasShopkeeperId': transactionData['shopkeeper_id'] != null, 'hasCustomerId': transactionData['customer_id'] != null}, 'B');
      // #endregion
      
      // Try sync with shorter timeout (timeout is set on Dio instance)
      Response response = await _dio.post(
        '/transactions',
        data: transactionData,
      );
      
      // #region agent log
      _logDebug('api_service.dart:148', 'POST request succeeded', {'statusCode': response.statusCode, 'hasData': response.data != null}, 'C');
      // #endregion
      
      // Sync succeeded - update local copy
      final savedTransaction = Transaction.fromJson(response.data['data']);
      await _storage.saveTransaction(savedTransaction.copyWith(synced: true));
      return savedTransaction;
    } catch (e) {
      // #region agent log
      _logDebug('api_service.dart:155', 'POST request failed', {'error': e.toString(), 'errorType': e.runtimeType.toString()}, 'D');
      // #endregion
      
      // Sync failed - transaction already saved locally with synced=false
      // Will be retried later via syncOfflineData()
      print('Warning: Failed to sync transaction to backend. Saved locally. Error: $e');
      return transaction; // Return local transaction
    }
  }

  Future<Transaction> updateTransaction(Transaction transaction) async {
    if (useMockApi) {
      await _storage.updateTransaction(transaction);
      return transaction;
    }

    try {
      Response response = await _dio.put('/transactions/${transaction.id}', data: transaction.toJson());
      final updatedTransaction = Transaction.fromJson(response.data['data']);
      await _storage.updateTransaction(updatedTransaction.copyWith(synced: true));
      return updatedTransaction;
    } catch (e) {
      await _storage.updateTransaction(transaction);
      throw Exception('Failed to update transaction: $e');
    }
  }

  Future<void> deleteTransaction(String id) async {
    if (useMockApi) {
      await _storage.deleteTransaction(id);
      return;
    }

    try {
      await _dio.delete('/transactions/$id');
      await _storage.deleteTransaction(id);
    } catch (e) {
      throw Exception('Failed to delete transaction: $e');
    }
  }

  // Product APIs
  Future<List<Product>> getProducts() async {
    if (useMockApi) {
      return await _storage.getProducts();
    }

    try {
      Response response = await _dio.get('/products');
      List<dynamic> data = response.data['data'] ?? [];
      return data.map((json) => Product.fromJson(json)).toList();
    } catch (e) {
      return await _storage.getProducts();
    }
  }

  Future<Product> createProduct(Product product) async {
    if (useMockApi) {
      await _storage.saveProduct(product);
      return product;
    }

    try {
      Response response = await _dio.post('/products', data: product.toJson());
      final savedProduct = Product.fromJson(response.data['data']);
      await _storage.saveProduct(savedProduct.copyWith(synced: true));
      return savedProduct;
    } catch (e) {
      await _storage.saveProduct(product);
      throw Exception('Failed to create product: $e');
    }
  }

  Future<Product> updateProduct(Product product) async {
    if (useMockApi) {
      await _storage.updateProduct(product);
      return product;
    }

    try {
      Response response = await _dio.put('/products/${product.id}', data: product.toJson());
      final updatedProduct = Product.fromJson(response.data['data']);
      await _storage.updateProduct(updatedProduct.copyWith(synced: true));
      return updatedProduct;
    } catch (e) {
      await _storage.updateProduct(product);
      throw Exception('Failed to update product: $e');
    }
  }

  Future<void> deleteProduct(String id) async {
    if (useMockApi) {
      await _storage.deleteProduct(id);
      return;
    }

    try {
      await _dio.delete('/products/$id');
      await _storage.deleteProduct(id);
    } catch (e) {
      throw Exception('Failed to delete product: $e');
    }
  }

  // Cooperative APIs
  Future<List<Cooperative>> getCooperatives() async {
    if (useMockApi) {
      return await _storage.getCooperatives();
    }

    try {
      Response response = await _dio.get('/cooperatives');
      List<dynamic> data = response.data['data'] ?? [];
      return data.map((json) => Cooperative.fromJson(json)).toList();
    } catch (e) {
      return await _storage.getCooperatives();
    }
  }

  Future<void> joinCooperative(String cooperativeId) async {
    if (useMockApi) {
      // Mock implementation
      return;
    }

    try {
      await _dio.post('/cooperatives/$cooperativeId/join');
    } catch (e) {
      throw Exception('Failed to join cooperative: $e');
    }
  }

  // Credit Score APIs
  Future<CreditScore> getCreditScore(String userId) async {
    if (useMockApi) {
      final stored = await _storage.getCreditScore(userId);
      if (stored != null) return stored;
      
      // Return mock credit score
      final mockScore = CreditScore(
        userId: userId,
        score: 750.0,
        level: 'good',
        isVerified: true,
        verificationHash: '0x1234567890abcdef',
        lastUpdated: DateTime.now(),
      );
      await _storage.saveCreditScore(mockScore);
      return mockScore;
    }

    try {
      Response response = await _dio.get('/credit-score/$userId');
      final creditScore = CreditScore.fromJson(response.data['data']);
      await _storage.saveCreditScore(creditScore);
      return creditScore;
    } catch (e) {
      final stored = await _storage.getCreditScore(userId);
      if (stored != null) return stored;
      throw Exception('Failed to get credit score: $e');
    }
  }

  // Sync offline data
  Future<void> syncOfflineData() async {
    if (useMockApi) return;

    try {
      // Sync transactions
      final unsyncedTransactions = await _storage.getUnsyncedTransactions();
      for (var transaction in unsyncedTransactions) {
        try {
          await createTransaction(transaction);
        } catch (e) {
          // Continue with next transaction
        }
      }

      // Sync products
      final unsyncedProducts = await _storage.getUnsyncedProducts();
      for (var product in unsyncedProducts) {
        try {
          await createProduct(product);
        } catch (e) {
          // Continue with next product
        }
      }
    } catch (e) {
      throw Exception('Failed to sync offline data: $e');
    }
  }
}
