class Cooperative {
  final String id;
  final String name;
  final String description;
  final int memberCount;
  final String? logoUrl;
  final List<String> memberIds;
  final DateTime createdAt;
  final bool isMember;
  final String? joinRequestStatus; // 'pending', 'approved', 'rejected'

  Cooperative({
    required this.id,
    required this.name,
    required this.description,
    required this.memberCount,
    this.logoUrl,
    required this.memberIds,
    required this.createdAt,
    this.isMember = false,
    this.joinRequestStatus,
  });

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'description': description,
      'memberCount': memberCount,
      'logoUrl': logoUrl,
      'memberIds': memberIds,
      'createdAt': createdAt.toIso8601String(),
      'isMember': isMember,
      'joinRequestStatus': joinRequestStatus,
    };
  }

  factory Cooperative.fromJson(Map<String, dynamic> json) {
    return Cooperative(
      id: json['id'] ?? '',
      name: json['name'] ?? '',
      description: json['description'] ?? '',
      memberCount: json['memberCount'] ?? 0,
      logoUrl: json['logoUrl'],
      memberIds: List<String>.from(json['memberIds'] ?? []),
      createdAt: DateTime.parse(json['createdAt']),
      isMember: json['isMember'] ?? false,
      joinRequestStatus: json['joinRequestStatus'],
    );
  }
}

class CooperativeMember {
  final String id;
  final String name;
  final String email;
  final String? avatarUrl;
  final DateTime joinedAt;
  final double creditScore;

  CooperativeMember({
    required this.id,
    required this.name,
    required this.email,
    this.avatarUrl,
    required this.joinedAt,
    required this.creditScore,
  });

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'email': email,
      'avatarUrl': avatarUrl,
      'joinedAt': joinedAt.toIso8601String(),
      'creditScore': creditScore,
    };
  }

  factory CooperativeMember.fromJson(Map<String, dynamic> json) {
    return CooperativeMember(
      id: json['id'] ?? '',
      name: json['name'] ?? '',
      email: json['email'] ?? '',
      avatarUrl: json['avatarUrl'],
      joinedAt: DateTime.parse(json['joinedAt']),
      creditScore: (json['creditScore'] ?? 0).toDouble(),
    );
  }
}

