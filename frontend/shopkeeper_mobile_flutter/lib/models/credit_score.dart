class CreditScore {
  final String userId;
  final double score;
  final String level; // 'excellent', 'good', 'fair', 'poor'
  final bool isVerified;
  final String? verificationHash;
  final DateTime lastUpdated;
  final List<CreditHistory> history;

  CreditScore({
    required this.userId,
    required this.score,
    required this.level,
    this.isVerified = false,
    this.verificationHash,
    required this.lastUpdated,
    this.history = const [],
  });

  Map<String, dynamic> toJson() {
    return {
      'userId': userId,
      'score': score,
      'level': level,
      'isVerified': isVerified,
      'verificationHash': verificationHash,
      'lastUpdated': lastUpdated.toIso8601String(),
      'history': history.map((h) => h.toJson()).toList(),
    };
  }

  factory CreditScore.fromJson(Map<String, dynamic> json) {
    return CreditScore(
      userId: json['userId'] ?? '',
      score: (json['score'] ?? 0).toDouble(),
      level: json['level'] ?? 'fair',
      isVerified: json['isVerified'] ?? false,
      verificationHash: json['verificationHash'],
      lastUpdated: DateTime.parse(json['lastUpdated']),
      history: (json['history'] as List<dynamic>?)
          ?.map((h) => CreditHistory.fromJson(h))
          .toList() ?? [],
    );
  }
}

class CreditHistory {
  final DateTime date;
  final double previousScore;
  final double newScore;
  final String reason;

  CreditHistory({
    required this.date,
    required this.previousScore,
    required this.newScore,
    required this.reason,
  });

  Map<String, dynamic> toJson() {
    return {
      'date': date.toIso8601String(),
      'previousScore': previousScore,
      'newScore': newScore,
      'reason': reason,
    };
  }

  factory CreditHistory.fromJson(Map<String, dynamic> json) {
    return CreditHistory(
      date: DateTime.parse(json['date']),
      previousScore: (json['previousScore'] ?? 0).toDouble(),
      newScore: (json['newScore'] ?? 0).toDouble(),
      reason: json['reason'] ?? '',
    );
  }
}

