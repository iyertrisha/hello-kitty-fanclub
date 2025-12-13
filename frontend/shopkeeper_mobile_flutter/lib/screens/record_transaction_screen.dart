import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:uuid/uuid.dart';
import '../models/transaction.dart';
import '../providers/transaction_provider.dart';
import '../widgets/voice_recorder.dart';
import '../services/api_service.dart';

class RecordTransactionScreen extends StatefulWidget {
  final Transaction? transaction;
  final String? language;

  const RecordTransactionScreen({super.key, this.transaction, this.language});

  @override
  State<RecordTransactionScreen> createState() => _RecordTransactionScreenState();
}

class _RecordTransactionScreenState extends State<RecordTransactionScreen> {
  final _formKey = GlobalKey<FormState>();
  final _amountController = TextEditingController();
  final _descriptionController = TextEditingController();
  final _customerNameController = TextEditingController();
  final _transactionTypeController = TextEditingController(
    text: 'Will be detected from speech...',
  );
  final ApiService _apiService = ApiService();
  
  String _selectedType = ''; // Empty initially, will be auto-populated from parsing
  String? _transcription;
  String? _customerId;
  String? _customerName;
  bool _isParsing = false;
  List<Map<String, dynamic>> _customers = [];
  bool _isLoadingCustomers = false;

  @override
  void initState() {
    super.initState();
    if (widget.transaction != null) {
      _amountController.text = widget.transaction!.amount.toString();
      _descriptionController.text = widget.transaction!.description;
      _selectedType = widget.transaction!.type;
      _transactionTypeController.text = _selectedType == 'credit' ? 'Credit' : 'Debit';
      _transcription = widget.transaction!.transcription;
      _customerName = widget.transaction!.customerName;
      _customerId = widget.transaction!.customerId;
      if (_customerName != null) {
        _customerNameController.text = _customerName!;
      }
    }
    _loadCustomers();
  }
  
  Future<void> _loadCustomers() async {
    setState(() {
      _isLoadingCustomers = true;
    });
    try {
      final customers = await _apiService.getCustomers();
      setState(() {
        _customers = customers;
        _isLoadingCustomers = false;
      });
    } catch (e) {
      setState(() {
        _isLoadingCustomers = false;
      });
      // Silently fail - user can still enter customer manually
    }
  }
  
  Future<void> _parseTranscript() async {
    if (_transcription == null || _transcription!.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Please record and transcribe audio first'),
          backgroundColor: Colors.orange,
        ),
      );
      return;
    }
    
    setState(() {
      _isParsing = true;
    });
    
    try {
      final parsedData = await _apiService.parseTranscript(
        _transcription!,
        widget.language ?? 'en-IN',
      );
      
      setState(() {
        // Auto-populate fields from parser
        if (parsedData['type'] != null) {
          // Map parser types to UI types
          // 'sale' or 'buying' (with is_buying flag) -> 'debit'
          // 'credit' -> 'credit'
          String parserType = parsedData['type'] as String;
          bool isBuying = parsedData['is_buying'] == true;
          
          if (parserType == 'credit') {
            _selectedType = 'credit';
            _transactionTypeController.text = 'Credit';
          } else if (parserType == 'sale' || isBuying) {
            _selectedType = 'debit';
            _transactionTypeController.text = 'Debit';
          } else {
            // Default fallback
            _selectedType = 'debit';
            _transactionTypeController.text = 'Debit';
          }
        }
        if (parsedData['amount'] != null) {
          // Format amount: remove .0 if it's a whole number
          double amount = parsedData['amount'] is int 
              ? (parsedData['amount'] as int).toDouble()
              : (parsedData['amount'] as num).toDouble();
          if (amount == amount.truncateToDouble()) {
            _amountController.text = amount.toInt().toString();
          } else {
            _amountController.text = amount.toString();
          }
        }
        if (parsedData['customer_name'] != null) {
          _customerName = parsedData['customer_name'];
          _customerNameController.text = _customerName!;
        }
        if (parsedData['customer_id'] != null) {
          _customerId = parsedData['customer_id'];
        }
        _isParsing = false;
      });
      
      // Debug logging
      print('Parsed data: $parsedData');
      print('Amount extracted: ${parsedData['amount']}');
      print('Amount field value: ${_amountController.text}');
      
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Transaction parsed successfully'),
            backgroundColor: Colors.green,
          ),
        );
      }
    } catch (e) {
      setState(() {
        _isParsing = false;
      });
      // Log error for debugging
      print('Parse error details: $e');
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Failed to parse transcript: $e'),
            backgroundColor: Colors.red,
            duration: const Duration(seconds: 4),
          ),
        );
      }
    }
  }

  @override
  void dispose() {
    _amountController.dispose();
    _descriptionController.dispose();
    _customerNameController.dispose();
    _transactionTypeController.dispose();
    super.dispose();
  }

  Future<void> _saveTransaction() async {
    // Validate that transaction type is set
    if (_selectedType.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Please record and transcribe audio to detect transaction type'),
          backgroundColor: Colors.orange,
        ),
      );
      return;
    }
    if (!_formKey.currentState!.validate()) return;
    
    // Additional validation: Customer required for credit transactions
    if (_selectedType == 'credit' && 
        (_customerNameController.text.trim().isEmpty && _customerId == null)) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Customer is required for credit transactions'),
          backgroundColor: Colors.red,
        ),
      );
      return;
    }

    final transaction = Transaction(
      id: widget.transaction?.id ?? const Uuid().v4(),
      type: _selectedType,
      amount: double.parse(_amountController.text),
      description: _descriptionController.text,
      date: widget.transaction?.date ?? DateTime.now(),
      transcription: _transcription,
      synced: false,
      customerId: _customerId,
      customerName: _customerNameController.text.trim().isNotEmpty 
          ? _customerNameController.text.trim() 
          : null,
    );

    try {
      if (widget.transaction != null) {
        await context.read<TransactionProvider>().updateTransaction(transaction);
      } else {
        await context.read<TransactionProvider>().addTransaction(transaction);
      }

      if (mounted) {
        Navigator.pop(context, true); // Return true to indicate success
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Transaction saved successfully'),
            backgroundColor: Colors.green,
          ),
        );
      }
    } catch (e) {
      // This should rarely happen now, but handle gracefully
      if (mounted) {
        Navigator.pop(context);
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Transaction saved locally. Will sync when online.'),
            backgroundColor: Colors.orange,
          ),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(widget.transaction == null ? 'Record Transaction' : 'Edit Transaction'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // Voice Recorder
              const Text(
                'Voice Recording',
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 8),
              VoiceRecorder(
                language: widget.language ?? 'en-IN',
                onTranscriptionComplete: (transcription) async {
                  setState(() {
                    _transcription = transcription;
                    _descriptionController.text = transcription;
                  });
                  // Auto-parse after transcription (with a small delay to ensure state is updated)
                  await Future.delayed(const Duration(milliseconds: 100));
                  await _parseTranscript();
                },
              ),
              // Show parsing indicator if parsing is in progress
              if (_isParsing) ...[
                const SizedBox(height: 8),
                const Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    SizedBox(
                      width: 16,
                      height: 16,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    ),
                    SizedBox(width: 8),
                    Text('Parsing transcript...'),
                  ],
                ),
              ],
              const SizedBox(height: 24),
              // Transaction Type (Auto-populated from parsing)
              const Text(
                'Transaction Type',
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 8),
              TextFormField(
                readOnly: true,
                decoration: InputDecoration(
                  labelText: 'Transaction Type',
                  hintText: 'Will be detected from speech...',
                  prefixIcon: Icon(
                    _selectedType == 'credit' ? Icons.arrow_downward : Icons.arrow_upward,
                    color: _selectedType == 'credit' ? Colors.green : Colors.red,
                  ),
                  suffixIcon: _isParsing
                      ? const SizedBox(
                          width: 20,
                          height: 20,
                          child: Padding(
                            padding: EdgeInsets.all(12.0),
                            child: CircularProgressIndicator(strokeWidth: 2),
                          ),
                        )
                      : _selectedType.isNotEmpty
                          ? Icon(
                              _selectedType == 'credit' ? Icons.check_circle : Icons.check_circle,
                              color: _selectedType == 'credit' ? Colors.green : Colors.red,
                            )
                          : null,
                  filled: true,
                  fillColor: _selectedType == 'credit' 
                      ? Colors.green[50] 
                      : _selectedType == 'debit'
                          ? Colors.red[50]
                          : Colors.grey[100],
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
                controller: _transactionTypeController,
              ),
              const SizedBox(height: 24),
              // Customer Name
              Text(
                'Customer Name${_selectedType == 'credit' ? ' *' : ''}',
                style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 8),
              _isLoadingCustomers
                  ? const LinearProgressIndicator()
                  : _customers.isEmpty
                      ? TextFormField(
                          controller: _customerNameController,
                          decoration: const InputDecoration(
                            labelText: 'Customer Name',
                            hintText: 'Enter customer name',
                            prefixIcon: Icon(Icons.person),
                            border: OutlineInputBorder(),
                          ),
                          onChanged: (value) {
                            setState(() {
                              _customerName = value.trim().isNotEmpty ? value.trim() : null;
                              // Clear customer_id if manually typing
                              if (value.trim().isNotEmpty) {
                                _customerId = null;
                              }
                            });
                          },
                          validator: (value) {
                            if (_selectedType == 'credit' && 
                                (value == null || value.trim().isEmpty)) {
                              return 'Customer is required for credit transactions';
                            }
                            return null;
                          },
                        )
                      : Autocomplete<String>(
                          optionsBuilder: (TextEditingValue textEditingValue) {
                            if (textEditingValue.text.isEmpty) {
                              return _customers.map((c) => c['name'] as String);
                            }
                            return _customers
                                .map((c) => c['name'] as String)
                                .where((name) => name
                                    .toLowerCase()
                                    .contains(textEditingValue.text.toLowerCase()))
                                .toList();
                          },
                          onSelected: (String selection) {
                            _customerNameController.text = selection;
                            final customer = _customers.firstWhere(
                              (c) => c['name'] == selection,
                            );
                            setState(() {
                              _customerName = selection;
                              _customerId = customer['id'] as String?;
                            });
                          },
                          fieldViewBuilder: (
                            BuildContext context,
                            TextEditingController textEditingController,
                            FocusNode focusNode,
                            VoidCallback onFieldSubmitted,
                          ) {
                            textEditingController.text = _customerNameController.text;
                            return TextFormField(
                              controller: textEditingController,
                              focusNode: focusNode,
                              decoration: const InputDecoration(
                                labelText: 'Customer Name',
                                hintText: 'Select or type customer name',
                                prefixIcon: Icon(Icons.person),
                                border: OutlineInputBorder(),
                              ),
                              onChanged: (value) {
                                _customerNameController.text = value;
                                setState(() {
                                  _customerName = value.trim().isNotEmpty ? value.trim() : null;
                                  // Clear customer_id if manually typing
                                  if (value.trim().isNotEmpty) {
                                    _customerId = null;
                                  }
                                });
                              },
                              validator: (value) {
                                if (_selectedType == 'credit' && 
                                    (value == null || value.trim().isEmpty)) {
                                  return 'Customer is required for credit transactions';
                                }
                                return null;
                              },
                            );
                          },
                        ),
              const SizedBox(height: 24),
              // Amount
              const Text(
                'Amount *',
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 8),
              TextFormField(
                controller: _amountController,
                decoration: const InputDecoration(
                  labelText: 'Amount',
                  hintText: 'Enter amount in rupees',
                  prefixIcon: Icon(Icons.currency_rupee),
                  border: OutlineInputBorder(),
                ),
                keyboardType: TextInputType.number,
                validator: (value) {
                  if (value == null || value.isEmpty) {
                    return 'Please enter an amount *';
                  }
                  final amount = double.tryParse(value);
                  if (amount == null) {
                    return 'Please enter a valid number';
                  }
                  if (amount <= 0) {
                    return 'Amount must be greater than 0';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 16),
              // Description
              TextFormField(
                controller: _descriptionController,
                decoration: const InputDecoration(
                  labelText: 'Description',
                  prefixIcon: Icon(Icons.description),
                  border: OutlineInputBorder(),
                ),
                maxLines: 3,
                validator: (value) {
                  if (value == null || value.isEmpty) {
                    return 'Please enter a description';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 24),
              // Save Button
              ElevatedButton(
                onPressed: _saveTransaction,
                style: ElevatedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  backgroundColor: Colors.blue,
                  foregroundColor: Colors.white,
                ),
                child: const Text(
                  'Save Transaction',
                  style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

