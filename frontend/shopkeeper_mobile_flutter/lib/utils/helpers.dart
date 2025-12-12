import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:uuid/uuid.dart';

const uuid = Uuid();

String formatCurrency(double amount) {
  return NumberFormat.currency(symbol: '₹', decimalDigits: 2).format(amount);
}

String formatDate(DateTime date) {
  return DateFormat('MMM dd, yyyy').format(date);
}

String formatDateTime(DateTime date) {
  return DateFormat('MMM dd, yyyy HH:mm').format(date);
}

String getCreditScoreLevel(double score) {
  if (score >= 800) return 'excellent';
  if (score >= 700) return 'good';
  if (score >= 600) return 'fair';
  return 'poor';
}

Color getCreditScoreColor(double score) {
  if (score >= 800) return Colors.green;
  if (score >= 700) return Colors.blue;
  if (score >= 600) return Colors.orange;
  return Colors.red;
}

