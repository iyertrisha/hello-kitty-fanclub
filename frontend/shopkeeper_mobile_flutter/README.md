# Shopkeeper Mobile Flutter App

A Flutter mobile application for shopkeepers with voice recording, transaction management, credit scoring, inventory management, and cooperative membership features.

## Features

- ✅ **Voice Recording & Transcription**: Record audio and get transcriptions via backend API
- ✅ **Transaction Management**: Add, view, edit, and delete transactions (credit/debit)
- ✅ **Credit Score**: View credit score with blockchain verification badge
- ✅ **Inventory Management**: Manage products with stock tracking
- ✅ **Cooperative Membership**: Browse and join cooperatives
- ✅ **Offline Support**: Data stored locally and synced when online
- ✅ **Modern UI**: Material Design 3 with beautiful, responsive interface

## Project Structure

```
lib/
├── main.dart                 # App entry point
├── models/                   # Data models
│   ├── transaction.dart
│   ├── product.dart
│   ├── cooperative.dart
│   └── credit_score.dart
├── services/                 # Business logic services
│   ├── api_service.dart      # Backend API integration
│   ├── storage_service.dart  # Local storage (SQLite + SharedPreferences)
│   ├── audio_service.dart    # Audio recording & playback
│   └── network_service.dart  # Network connectivity
├── providers/                # State management (Provider)
│   ├── transaction_provider.dart
│   ├── product_provider.dart
│   ├── cooperative_provider.dart
│   ├── credit_score_provider.dart
│   └── audio_provider.dart
├── screens/                  # UI screens
│   ├── dashboard_screen.dart
│   ├── transaction_list_screen.dart
│   ├── record_transaction_screen.dart
│   ├── credit_score_screen.dart
│   ├── inventory_screen.dart
│   ├── add_product_screen.dart
│   └── cooperatives_screen.dart
├── widgets/                  # Reusable widgets
│   ├── stat_card.dart
│   ├── voice_recorder.dart
│   └── verified_badge.dart
└── utils/                    # Utilities
    ├── constants.dart
    └── helpers.dart
```

## Setup Instructions

### Prerequisites

- Flutter SDK (3.0.0 or higher)
- Dart SDK (3.0.0 or higher)
- Android Studio / Xcode (for mobile development)
- Physical device or emulator

### Installation

1. **Install dependencies:**
   ```bash
   cd frontend/shopkeeper_mobile_flutter
   flutter pub get
   ```

2. **Configure backend URL:**
   - Open `lib/services/api_service.dart`
   - Update `baseUrl` to your backend API URL
   - Set `useMockApi = false` when backend is ready

3. **Run the app:**
   ```bash
   flutter run
   ```

### Android Setup

The app requires the following permissions (already configured in `AndroidManifest.xml`):
- Internet access
- Microphone (for voice recording)
- Network state (for connectivity checks)
- External storage (for audio files)

### Testing on Physical Device

1. **Enable USB Debugging** on your Android device
2. **Connect device** via USB
3. **Run:**
   ```bash
   flutter devices  # List available devices
   flutter run -d <device-id>
   ```

## Backend Integration

### API Endpoints Expected

The app expects the following backend endpoints:

- `POST /api/transcribe` - Upload audio and get transcription
- `GET /api/transactions` - Get all transactions
- `POST /api/transactions` - Create transaction
- `PUT /api/transactions/:id` - Update transaction
- `DELETE /api/transactions/:id` - Delete transaction
- `GET /api/products` - Get all products
- `POST /api/products` - Create product
- `PUT /api/products/:id` - Update product
- `DELETE /api/products/:id` - Delete product
- `GET /api/cooperatives` - Get all cooperatives
- `POST /api/cooperatives/:id/join` - Join cooperative
- `GET /api/credit-score/:userId` - Get credit score

### Mock API Mode

By default, the app runs in mock API mode (`useMockApi = true`). This allows you to:
- Test the UI without a backend
- Develop features independently
- Store data locally only

To switch to real backend:
1. Set `useMockApi = false` in `api_service.dart`
2. Update `baseUrl` to your backend URL
3. Ensure backend is running and accessible

## Offline Sync

The app automatically:
- Stores all data locally using SQLite
- Marks items as `synced: false` when created offline
- Syncs unsynced items when network is available
- Shows sync status indicators in the UI

## State Management

The app uses **Provider** for state management:
- `TransactionProvider` - Manages transactions
- `ProductProvider` - Manages products
- `CooperativeProvider` - Manages cooperatives
- `CreditScoreProvider` - Manages credit score
- `AudioProvider` - Manages audio recording

## Dependencies

Key dependencies:
- `provider` - State management
- `dio` - HTTP client
- `sqflite` - Local database
- `shared_preferences` - Key-value storage
- `record` - Audio recording
- `audioplayers` - Audio playback
- `permission_handler` - Permission management
- `connectivity_plus` - Network status

## Development Notes

- All screens are fully functional with mock data
- Voice recording requires microphone permission
- Offline-first architecture for better UX
- Material Design 3 components throughout
- Responsive layout for different screen sizes

## Troubleshooting

**Build errors:**
```bash
flutter clean
flutter pub get
flutter run
```

**Permission issues:**
- Ensure AndroidManifest.xml has required permissions
- Grant microphone permission when prompted

**Network issues:**
- Check backend URL in `api_service.dart`
- Verify device can reach backend (use device IP, not localhost)

## Next Steps

1. Connect to your backend API
2. Implement authentication if needed
3. Add push notifications
4. Add more analytics and reporting
5. Customize UI/UX as needed
