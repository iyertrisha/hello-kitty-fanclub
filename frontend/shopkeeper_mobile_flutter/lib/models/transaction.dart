class Transaction {
  final String id;
  final String type; // 'credit' or 'debit'
  final double amount;
  final String description;
  final DateTime date;
  final String? audioPath;
  final String? transcription;
  final bool synced;
  final String? cooperativeId;

  Transaction({
    required this.id,
    required this.type,
    required this.amount,
    required this.description,
    required this.date,
    this.audioPath,
    this.transcription,
    this.synced = false,
    this.cooperativeId,
  });

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'type': type,
      'amount': amount,
      'description': description,
      'date': date.toIso8601String(),
      'audioPath': audioPath,
      'transcription': transcription,
      'synced': synced,
      'cooperativeId': cooperativeId,
    };
  }

  factory Transaction.fromJson(Map<String, dynamic> json) {
    return Transaction(
      id: json['id'] ?? '',
      type: json['type'] ?? 'debit',
      amount: (json['amount'] ?? 0).toDouble(),
      description: json['description'] ?? '',
      date: DateTime.parse(json['date']),
      audioPath: json['audioPath'],
      transcription: json['transcription'],
      synced: json['synced'] ?? false,
      cooperativeId: json['cooperativeId'],
    );
  }

  Transaction copyWith({
    String? id,
    String? type,
    double? amount,
    String? description,
    DateTime? date,
    String? audioPath,
    String? transcription,
    bool? synced,
    String? cooperativeId,
  }) {
    return Transaction(
      id: id ?? this.id,
      type: type ?? this.type,
      amount: amount ?? this.amount,
      description: description ?? this.description,
      date: date ?? this.date,
      audioPath: audioPath ?? this.audioPath,
      transcription: transcription ?? this.transcription,
      synced: synced ?? this.synced,
      cooperativeId: cooperativeId ?? this.cooperativeId,
    );
  }
}

