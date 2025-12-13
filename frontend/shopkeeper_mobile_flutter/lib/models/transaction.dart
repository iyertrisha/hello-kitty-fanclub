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
  final String? shopkeeperId;
  final String? customerId;
  final String? customerName;

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
    this.shopkeeperId,
    this.customerId,
    this.customerName,
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
      'shopkeeper_id': shopkeeperId,
      'customer_id': customerId,
      'customer_name': customerName,
    };
  }

  factory Transaction.fromJson(Map<String, dynamic> json) {
    // Handle both 'date' and 'timestamp' fields
    DateTime dateTime;
    if (json['date'] != null) {
      dateTime = DateTime.parse(json['date']);
    } else if (json['timestamp'] != null) {
      dateTime = DateTime.parse(json['timestamp']);
    } else {
      dateTime = DateTime.now(); // Fallback to current time
    }
    
    return Transaction(
      id: json['id'] ?? '',
      type: json['type'] ?? 'debit',
      amount: (json['amount'] ?? 0).toDouble(),
      description: json['description'] ?? '',
      date: dateTime,
      audioPath: json['audioPath'],
      transcription: json['transcription'],
      synced: json['synced'] is bool ? json['synced'] : (json['synced'] == 1 || json['synced'] == true),
      cooperativeId: json['cooperativeId'],
      shopkeeperId: json['shopkeeper_id'] ?? json['shopkeeperId'],
      customerId: json['customer_id'] ?? json['customerId'],
      customerName: json['customer_name'] ?? json['customerName'],
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
    String? shopkeeperId,
    String? customerId,
    String? customerName,
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
      shopkeeperId: shopkeeperId ?? this.shopkeeperId,
      customerId: customerId ?? this.customerId,
      customerName: customerName ?? this.customerName,
    );
  }
}
