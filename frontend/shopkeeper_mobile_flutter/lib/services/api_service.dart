import 'package:dio/dio.dart';
import 'package:path/path.dart' as path;
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
  
  // Change this to your backend URL
  static const String baseUrl = 'http://localhost:5000/api';
  static const bool useMockApi = true; // Set to false when backend is ready

  ApiService._internal() {
    _dio.options.baseUrl = baseUrl;
    _dio.options.connectTimeout = const Duration(seconds: 30);
    _dio.options.receiveTimeout = const Duration(seconds: 30);
    
    // Add interceptors for logging
    _dio.interceptors.add(LogInterceptor(
      requestBody: true,
      responseBody: true,
    ));
  }

  // Audio upload and transcription
  Future<String> uploadAudioAndTranscribe(String audioPath) async {
    if (useMockApi) {
      await Future.delayed(const Duration(seconds: 2));
      return 'Mock transcription: This is a sample transaction recording.';
    }

    try {
      String fileName = path.basename(audioPath);
      FormData formData = FormData.fromMap({
        'audio': await MultipartFile.fromFile(audioPath, filename: fileName),
      });

      Response response = await _dio.post('/transcribe', data: formData);
      return response.data['transcription'] ?? '';
    } catch (e) {
      throw Exception('Failed to transcribe audio: $e');
    }
  }

  // Transaction APIs
  Future<List<Transaction>> getTransactions() async {
    if (useMockApi) {
      return await _storage.getTransactions();
    }

    try {
      Response response = await _dio.get('/transactions');
      List<dynamic> data = response.data['data'] ?? [];
      return data.map((json) => Transaction.fromJson(json as Map<String, dynamic>)).toList();
    } catch (e) {
      // Return local data if API fails
      return await _storage.getTransactions();
    }
  }

  Future<Transaction> createTransaction(Transaction transaction) async {
    if (useMockApi) {
      await _storage.saveTransaction(transaction);
      return transaction;
    }

    try {
      Response response = await _dio.post('/transactions', data: transaction.toJson());
      final savedTransaction = Transaction.fromJson(response.data['data']);
      await _storage.saveTransaction(savedTransaction.copyWith(synced: true));
      return savedTransaction;
    } catch (e) {
      // Save locally for sync later
      await _storage.saveTransaction(transaction);
      throw Exception('Failed to create transaction: $e');
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

