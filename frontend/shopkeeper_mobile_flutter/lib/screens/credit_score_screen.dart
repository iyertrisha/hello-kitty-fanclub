import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/credit_score_provider.dart';
import '../widgets/verified_badge.dart';
import '../utils/helpers.dart';

class CreditScoreScreen extends StatefulWidget {
  const CreditScoreScreen({super.key});

  @override
  State<CreditScoreScreen> createState() => _CreditScoreScreenState();
}

class _CreditScoreScreenState extends State<CreditScoreScreen> {
  final String _userId = 'user_123'; // Replace with actual user ID

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<CreditScoreProvider>().loadCreditScore(_userId);
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Credit Score'),
      ),
      body: Consumer<CreditScoreProvider>(
        builder: (context, creditScoreProvider, child) {
          if (creditScoreProvider.isLoading) {
            return const Center(child: CircularProgressIndicator());
          }

          final creditScore = creditScoreProvider.creditScore;
          if (creditScore == null) {
            return const Center(child: Text('No credit score data'));
          }

          return SingleChildScrollView(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                // Score Card
                Card(
                  elevation: 4,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(16),
                  ),
                  child: Container(
                    padding: const EdgeInsets.all(24),
                    decoration: BoxDecoration(
                      gradient: LinearGradient(
                        colors: [
                          getCreditScoreColor(creditScore.score).withOpacity(0.8),
                          getCreditScoreColor(creditScore.score),
                        ],
                        begin: Alignment.topLeft,
                        end: Alignment.bottomRight,
                      ),
                      borderRadius: BorderRadius.circular(16),
                    ),
                    child: Column(
                      children: [
                        const Text(
                          'Your Credit Score',
                          style: TextStyle(
                            color: Colors.white,
                            fontSize: 18,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                        const SizedBox(height: 16),
                        Text(
                          creditScore.score.toStringAsFixed(0),
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: 64,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        const SizedBox(height: 8),
                        Container(
                          padding: const EdgeInsets.symmetric(
                            horizontal: 16,
                            vertical: 8,
                          ),
                          decoration: BoxDecoration(
                            color: Colors.white.withOpacity(0.2),
                            borderRadius: BorderRadius.circular(20),
                          ),
                          child: Text(
                            creditScore.level.toUpperCase(),
                            style: const TextStyle(
                              color: Colors.white,
                              fontWeight: FontWeight.bold,
                              fontSize: 14,
                            ),
                          ),
                        ),
                        const SizedBox(height: 16),
                        VerifiedBadge(
                          isVerified: creditScore.isVerified,
                          verificationHash: creditScore.verificationHash,
                        ),
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: 24),
                // Verification Info
                if (creditScore.isVerified && creditScore.verificationHash != null)
                  Card(
                    child: Padding(
                      padding: const EdgeInsets.all(16),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              Icon(Icons.verified, color: Colors.blue[700]),
                              const SizedBox(width: 8),
                              const Text(
                                'Blockchain Verified',
                                style: TextStyle(
                                  fontSize: 18,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 12),
                          const Text(
                            'Verification Hash:',
                            style: TextStyle(
                              fontSize: 12,
                              color: Colors.grey,
                            ),
                          ),
                          const SizedBox(height: 4),
                          Container(
                            padding: const EdgeInsets.all(12),
                            decoration: BoxDecoration(
                              color: Colors.grey[100],
                              borderRadius: BorderRadius.circular(8),
                            ),
                            child: SelectableText(
                              creditScore.verificationHash!,
                              style: const TextStyle(
                                fontFamily: 'monospace',
                                fontSize: 12,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                const SizedBox(height: 24),
                // Score Range Info
                Card(
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text(
                          'Score Range',
                          style: TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        const SizedBox(height: 16),
                        _buildScoreRangeItem('Excellent', 800, 850, Colors.green),
                        _buildScoreRangeItem('Good', 700, 799, Colors.blue),
                        _buildScoreRangeItem('Fair', 600, 699, Colors.orange),
                        _buildScoreRangeItem('Poor', 300, 599, Colors.red),
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: 24),
                // History
                if (creditScore.history.isNotEmpty) ...[
                  const Text(
                    'History',
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 8),
                  ...creditScore.history.map((history) {
                    return Card(
                      margin: const EdgeInsets.only(bottom: 8),
                      child: ListTile(
                        leading: CircleAvatar(
                          backgroundColor: history.newScore > history.previousScore
                              ? Colors.green
                              : Colors.red,
                          child: Icon(
                            history.newScore > history.previousScore
                                ? Icons.arrow_upward
                                : Icons.arrow_downward,
                            color: Colors.white,
                          ),
                        ),
                        title: Text(history.reason),
                        subtitle: Text(formatDate(history.date)),
                        trailing: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          crossAxisAlignment: CrossAxisAlignment.end,
                          children: [
                            Text(
                              history.previousScore.toStringAsFixed(0),
                              style: TextStyle(
                                color: Colors.grey[600],
                                decoration: TextDecoration.lineThrough,
                              ),
                            ),
                            Text(
                              history.newScore.toStringAsFixed(0),
                              style: TextStyle(
                                fontWeight: FontWeight.bold,
                                color: history.newScore > history.previousScore
                                    ? Colors.green
                                    : Colors.red,
                              ),
                            ),
                          ],
                        ),
                      ),
                    );
                  }),
                ],
              ],
            ),
          );
        },
      ),
    );
  }

  Widget _buildScoreRangeItem(String label, int min, int max, Color color) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Row(
        children: [
          Container(
            width: 12,
            height: 12,
            decoration: BoxDecoration(
              color: color,
              shape: BoxShape.circle,
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              label,
              style: const TextStyle(fontWeight: FontWeight.w500),
            ),
          ),
          Text(
            '$min - $max',
            style: TextStyle(color: Colors.grey[600]),
          ),
        ],
      ),
    );
  }
}

