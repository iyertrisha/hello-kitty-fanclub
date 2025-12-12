import 'package:flutter/foundation.dart';
import '../models/credit_score.dart';
import '../services/api_service.dart';

class CreditScoreProvider with ChangeNotifier {
  final ApiService _apiService = ApiService();

  CreditScore? _creditScore;
  bool _isLoading = false;
  String? _error;

  CreditScore? get creditScore => _creditScore;
  bool get isLoading => _isLoading;
  String? get error => _error;

  Future<void> loadCreditScore(String userId) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      _creditScore = await _apiService.getCreditScore(userId);
      _error = null;
    } catch (e) {
      _error = e.toString();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }
}

