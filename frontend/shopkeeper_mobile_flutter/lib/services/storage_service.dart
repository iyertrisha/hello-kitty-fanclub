import 'package:shared_preferences/shared_preferences.dart';
import 'package:sqflite/sqflite.dart';
import 'package:path/path.dart' as path;
import '../models/transaction.dart' as models;
import '../models/product.dart';
import '../models/cooperative.dart';
import '../models/credit_score.dart';

class StorageService {
  static final StorageService _instance = StorageService._internal();
  factory StorageService() => _instance;
  StorageService._internal();

  Database? _database;

  Future<Database> get database async {
    if (_database != null) return _database!;
    _database = await _initDatabase();
    return _database!;
  }

  Future<Database> _initDatabase() async {
    String dbPath = path.join(await getDatabasesPath(), 'shopkeeper.db');
    return await openDatabase(
      dbPath,
      version: 2,
      onCreate: _onCreate,
      onUpgrade: _onUpgrade,
    );
  }

  Future<void> _onCreate(Database db, int version) async {
    // Transactions table
    await db.execute('''
      CREATE TABLE transactions(
        id TEXT PRIMARY KEY,
        type TEXT NOT NULL,
        amount REAL NOT NULL,
        description TEXT NOT NULL,
        date TEXT NOT NULL,
        audioPath TEXT,
        transcription TEXT,
        synced INTEGER NOT NULL DEFAULT 0,
        cooperativeId TEXT,
        shopkeeper_id TEXT,
        customer_id TEXT
      )
    ''');

    // Products table
    await db.execute('''
      CREATE TABLE products(
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT NOT NULL,
        price REAL NOT NULL,
        stock INTEGER NOT NULL,
        imageUrl TEXT,
        createdAt TEXT NOT NULL,
        updatedAt TEXT,
        synced INTEGER NOT NULL DEFAULT 0
      )
    ''');

    // Cooperatives table
    await db.execute('''
      CREATE TABLE cooperatives(
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT NOT NULL,
        memberCount INTEGER NOT NULL,
        logoUrl TEXT,
        createdAt TEXT NOT NULL,
        isMember INTEGER NOT NULL DEFAULT 0,
        joinRequestStatus TEXT
      )
    ''');

    // Credit score table
    await db.execute('''
      CREATE TABLE credit_score(
        userId TEXT PRIMARY KEY,
        score REAL NOT NULL,
        level TEXT NOT NULL,
        isVerified INTEGER NOT NULL DEFAULT 0,
        verificationHash TEXT,
        lastUpdated TEXT NOT NULL
      )
    ''');
  }

  Future<void> _onUpgrade(Database db, int oldVersion, int newVersion) async {
    if (oldVersion < 2) {
      // Add shopkeeper_id and customer_id columns to transactions table
      try {
        await db.execute('ALTER TABLE transactions ADD COLUMN shopkeeper_id TEXT');
      } catch (e) {
        // Column might already exist
      }
      try {
        await db.execute('ALTER TABLE transactions ADD COLUMN customer_id TEXT');
      } catch (e) {
        // Column might already exist
      }
    }
  }

  // Transaction methods
  Future<void> saveTransaction(models.Transaction transaction) async {
    final db = await database;
    await db.insert(
      'transactions',
      {
        ...transaction.toJson(),
        'synced': transaction.synced ? 1 : 0,  // Convert bool to int
      },
      conflictAlgorithm: ConflictAlgorithm.replace,
    );
  }

  Future<List<models.Transaction>> getTransactions() async {
    final db = await database;
    final List<Map<String, dynamic>> maps = await db.query('transactions', orderBy: 'date DESC');
    return List.generate(maps.length, (i) => models.Transaction.fromJson(maps[i]));
  }

  Future<models.Transaction?> getTransaction(String id) async {
    final db = await database;
    final List<Map<String, dynamic>> maps = await db.query(
      'transactions',
      where: 'id = ?',
      whereArgs: [id],
    );
    if (maps.isEmpty) return null;
    return models.Transaction.fromJson(maps.first);
  }

  Future<void> updateTransaction(models.Transaction transaction) async {
    final db = await database;
    await db.update(
      'transactions',
      transaction.toJson(),
      where: 'id = ?',
      whereArgs: [transaction.id],
    );
  }

  Future<void> deleteTransaction(String id) async {
    final db = await database;
    await db.delete('transactions', where: 'id = ?', whereArgs: [id]);
  }

  Future<List<models.Transaction>> getUnsyncedTransactions() async {
    final db = await database;
    final List<Map<String, dynamic>> maps = await db.query(
      'transactions',
      where: 'synced = ?',
      whereArgs: [0],
    );
    return List.generate(maps.length, (i) => models.Transaction.fromJson(maps[i]));
  }

  // Product methods
  Future<void> saveProduct(Product product) async {
    final db = await database;
    // Convert boolean to int for SQLite compatibility
    final json = product.toJson();
    json['synced'] = (json['synced'] as bool) ? 1 : 0;
    await db.insert(
      'products',
      json,
      conflictAlgorithm: ConflictAlgorithm.replace,
    );
  }

  Future<List<Product>> getProducts() async {
    final db = await database;
    final List<Map<String, dynamic>> maps = await db.query('products', orderBy: 'createdAt DESC');
    // Convert synced from int (0/1) to bool for SQLite compatibility
    return List.generate(maps.length, (i) {
      final map = Map<String, dynamic>.from(maps[i]);
      map['synced'] = (map['synced'] as int) == 1;
      return Product.fromJson(map);
    });
  }

  Future<Product?> getProduct(String id) async {
    final db = await database;
    final List<Map<String, dynamic>> maps = await db.query(
      'products',
      where: 'id = ?',
      whereArgs: [id],
    );
    if (maps.isEmpty) return null;
    // Convert synced from int (0/1) to bool for SQLite compatibility
    final map = Map<String, dynamic>.from(maps.first);
    map['synced'] = (map['synced'] as int) == 1;
    return Product.fromJson(map);
  }

  Future<void> updateProduct(Product product) async {
    final db = await database;
    // Convert boolean to int for SQLite compatibility
    final json = product.toJson();
    json['synced'] = (json['synced'] as bool) ? 1 : 0;
    await db.update(
      'products',
      json,
      where: 'id = ?',
      whereArgs: [product.id],
    );
  }

  Future<void> deleteProduct(String id) async {
    final db = await database;
    await db.delete('products', where: 'id = ?', whereArgs: [id]);
  }

  Future<List<Product>> getUnsyncedProducts() async {
    final db = await database;
    final List<Map<String, dynamic>> maps = await db.query(
      'products',
      where: 'synced = ?',
      whereArgs: [0],
    );
    return List.generate(maps.length, (i) => Product.fromJson(maps[i]));
  }

  // Cooperative methods
  Future<void> saveCooperative(Cooperative cooperative) async {
    final db = await database;
    await db.insert(
      'cooperatives',
      {
        ...cooperative.toJson(),
        'isMember': cooperative.isMember ? 1 : 0,
      },
      conflictAlgorithm: ConflictAlgorithm.replace,
    );
  }

  Future<List<Cooperative>> getCooperatives() async {
    final db = await database;
    final List<Map<String, dynamic>> maps = await db.query('cooperatives', orderBy: 'createdAt DESC');
    return List.generate(maps.length, (i) {
      final json = maps[i];
      json['isMember'] = json['isMember'] == 1;
      return Cooperative.fromJson(json);
    });
  }

  // Credit score methods
  Future<void> saveCreditScore(CreditScore creditScore) async {
    final db = await database;
    await db.insert(
      'credit_score',
      {
        ...creditScore.toJson(),
        'isVerified': creditScore.isVerified ? 1 : 0,
      },
      conflictAlgorithm: ConflictAlgorithm.replace,
    );
  }

  Future<CreditScore?> getCreditScore(String userId) async {
    final db = await database;
    final List<Map<String, dynamic>> maps = await db.query(
      'credit_score',
      where: 'userId = ?',
      whereArgs: [userId],
    );
    if (maps.isEmpty) return null;
    final json = maps.first;
    json['isVerified'] = json['isVerified'] == 1;
    return CreditScore.fromJson(json);
  }

  // SharedPreferences for simple key-value storage
  Future<void> setString(String key, String value) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(key, value);
  }

  Future<String?> getString(String key) async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(key);
  }

  Future<void> setBool(String key, bool value) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool(key, value);
  }

  Future<bool?> getBool(String key) async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getBool(key);
  }
}

