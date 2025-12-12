import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/transaction_provider.dart';
import '../widgets/stat_card.dart';
import '../utils/helpers.dart';
import 'transaction_list_screen.dart';
import 'record_transaction_screen.dart';
import 'credit_score_screen.dart';
import 'inventory_screen.dart';
import 'cooperatives_screen.dart';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<TransactionProvider>().loadTransactions();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Dashboard'),
        elevation: 0,
      ),
      body: RefreshIndicator(
        onRefresh: () async {
          await context.read<TransactionProvider>().loadTransactions();
        },
        child: SingleChildScrollView(
          physics: const AlwaysScrollableScrollPhysics(),
          padding: const EdgeInsets.all(16),
          child: Consumer<TransactionProvider>(
            builder: (context, transactionProvider, child) {
              return Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Stats Cards
                  GridView.count(
                    crossAxisCount: 2,
                    shrinkWrap: true,
                    physics: const NeverScrollableScrollPhysics(),
                    crossAxisSpacing: 16,
                    mainAxisSpacing: 16,
                    childAspectRatio: 1.5,
                    children: [
                      StatCard(
                        title: 'Total Credit',
                        value: formatCurrency(transactionProvider.totalCredit),
                        icon: Icons.arrow_downward,
                        color: Colors.green,
                      ),
                      StatCard(
                        title: 'Total Debit',
                        value: formatCurrency(transactionProvider.totalDebit),
                        icon: Icons.arrow_upward,
                        color: Colors.red,
                      ),
                      StatCard(
                        title: 'Balance',
                        value: formatCurrency(transactionProvider.balance),
                        icon: Icons.account_balance_wallet,
                        color: Colors.blue,
                      ),
                      StatCard(
                        title: 'Transactions',
                        value: '${transactionProvider.transactions.length}',
                        icon: Icons.receipt_long,
                        color: Colors.orange,
                      ),
                    ],
                  ),
                  const SizedBox(height: 24),
                  // Quick Actions
                  const Text(
                    'Quick Actions',
                    style: TextStyle(
                      fontSize: 20,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 16),
                  GridView.count(
                    crossAxisCount: 2,
                    shrinkWrap: true,
                    physics: const NeverScrollableScrollPhysics(),
                    crossAxisSpacing: 16,
                    mainAxisSpacing: 16,
                    childAspectRatio: 2.5,
                    children: [
                      _buildActionCard(
                        context,
                        'Record Transaction',
                        Icons.add_circle,
                        Colors.blue,
                        () {
                          Navigator.push(
                            context,
                            MaterialPageRoute(
                              builder: (_) => const RecordTransactionScreen(),
                            ),
                          );
                        },
                      ),
                      _buildActionCard(
                        context,
                        'View Transactions',
                        Icons.list,
                        Colors.green,
                        () {
                          Navigator.push(
                            context,
                            MaterialPageRoute(
                              builder: (_) => const TransactionListScreen(),
                            ),
                          );
                        },
                      ),
                      _buildActionCard(
                        context,
                        'Credit Score',
                        Icons.star,
                        Colors.orange,
                        () {
                          Navigator.push(
                            context,
                            MaterialPageRoute(
                              builder: (_) => const CreditScoreScreen(),
                            ),
                          );
                        },
                      ),
                      _buildActionCard(
                        context,
                        'Inventory',
                        Icons.inventory,
                        Colors.purple,
                        () {
                          Navigator.push(
                            context,
                            MaterialPageRoute(
                              builder: (_) => const InventoryScreen(),
                            ),
                          );
                        },
                      ),
                      _buildActionCard(
                        context,
                        'Cooperatives',
                        Icons.group,
                        Colors.teal,
                        () {
                          Navigator.push(
                            context,
                            MaterialPageRoute(
                              builder: (_) => const CooperativesScreen(),
                            ),
                          );
                        },
                      ),
                    ],
                  ),
                  const SizedBox(height: 24),
                  // Recent Transactions
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Text(
                        'Recent Transactions',
                        style: TextStyle(
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      TextButton(
                        onPressed: () {
                          Navigator.push(
                            context,
                            MaterialPageRoute(
                              builder: (_) => const TransactionListScreen(),
                            ),
                          );
                        },
                        child: const Text('View All'),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  if (transactionProvider.isLoading)
                    const Center(child: CircularProgressIndicator())
                  else if (transactionProvider.transactions.isEmpty)
                    const Card(
                      child: Padding(
                        padding: EdgeInsets.all(24),
                        child: Center(
                          child: Text('No transactions yet'),
                        ),
                      ),
                    )
                  else
                    ...transactionProvider.transactions.take(5).map((transaction) {
                      return Card(
                        margin: const EdgeInsets.only(bottom: 8),
                        child: ListTile(
                          leading: CircleAvatar(
                            backgroundColor: transaction.type == 'credit'
                                ? Colors.green
                                : Colors.red,
                            child: Icon(
                              transaction.type == 'credit'
                                  ? Icons.arrow_downward
                                  : Icons.arrow_upward,
                              color: Colors.white,
                            ),
                          ),
                          title: Text(transaction.description),
                          subtitle: Text(formatDate(transaction.date)),
                          trailing: Text(
                            '${transaction.type == 'credit' ? '+' : '-'}${formatCurrency(transaction.amount)}',
                            style: TextStyle(
                              fontWeight: FontWeight.bold,
                              color: transaction.type == 'credit'
                                  ? Colors.green
                                  : Colors.red,
                            ),
                          ),
                        ),
                      );
                    }),
                ],
              );
            },
          ),
        ),
      ),
    );
  }

  Widget _buildActionCard(
    BuildContext context,
    String title,
    IconData icon,
    Color color,
    VoidCallback onTap,
  ) {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(icon, color: color, size: 32),
              const SizedBox(height: 8),
              Text(
                title,
                textAlign: TextAlign.center,
                style: const TextStyle(
                  fontWeight: FontWeight.w600,
                  fontSize: 12,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

