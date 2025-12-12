import 'package:flutter/foundation.dart';
import '../models/cooperative.dart';
import '../services/api_service.dart';

class CooperativeProvider with ChangeNotifier {
  final ApiService _apiService = ApiService();

  List<Cooperative> _cooperatives = [];
  bool _isLoading = false;
  String? _error;

  List<Cooperative> get cooperatives => _cooperatives;
  bool get isLoading => _isLoading;
  String? get error => _error;

  Future<void> loadCooperatives() async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      _cooperatives = await _apiService.getCooperatives();
      _error = null;
    } catch (e) {
      _error = e.toString();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> joinCooperative(String cooperativeId) async {
    try {
      await _apiService.joinCooperative(cooperativeId);
      final index = _cooperatives.indexWhere((c) => c.id == cooperativeId);
      if (index != -1) {
        _cooperatives[index] = _cooperatives[index].copyWith(
          joinRequestStatus: 'pending',
        );
        notifyListeners();
      }
    } catch (e) {
      _error = e.toString();
      notifyListeners();
      rethrow;
    }
  }
}

extension CooperativeExtension on Cooperative {
  Cooperative copyWith({
    String? id,
    String? name,
    String? description,
    int? memberCount,
    String? logoUrl,
    List<String>? memberIds,
    DateTime? createdAt,
    bool? isMember,
    String? joinRequestStatus,
  }) {
    return Cooperative(
      id: id ?? this.id,
      name: name ?? this.name,
      description: description ?? this.description,
      memberCount: memberCount ?? this.memberCount,
      logoUrl: logoUrl ?? this.logoUrl,
      memberIds: memberIds ?? this.memberIds,
      createdAt: createdAt ?? this.createdAt,
      isMember: isMember ?? this.isMember,
      joinRequestStatus: joinRequestStatus ?? this.joinRequestStatus,
    );
  }
}

