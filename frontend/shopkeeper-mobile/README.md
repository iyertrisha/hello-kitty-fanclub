# Shopkeeper Mobile App

React Native mobile application for shopkeepers to manage transactions, inventory, credit scores, and cooperatives.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Node.js** (v16 or higher)
- **npm** or **yarn**
- **Expo CLI** (`npm install -g expo-cli`)
- **React Native development environment**:
  - For iOS: Xcode (Mac only)
  - For Android: Android Studio with Android SDK
- **Expo Go app** on your mobile device (for testing)

## Installation Steps

### 1. Navigate to the project directory

```bash
cd frontend/shopkeeper-mobile
```

### 2. Install dependencies

```bash
npm install
```

or

```bash
yarn install
```

### 3. Configure API endpoint

Open `src/services/api.js` and update the `API_BASE_URL`:

```javascript
const API_BASE_URL = 'http://localhost:5000/api'; // Update to your Flask API URL
```

For physical device testing, use your computer's IP address:
```javascript
const API_BASE_URL = 'http://192.168.1.XXX:5000/api'; // Replace XXX with your IP
```

### 4. Set up shopkeeper ID (for testing)

The app uses AsyncStorage to store the shopkeeper ID. For testing, you can set it manually:

1. Open `src/screens/DashboardScreen.js` (or any screen)
2. The app defaults to shopkeeper ID '1' if not set
3. Or modify the `loadShopkeeperId` function to use your shopkeeper ID

## Running the App

### Development Mode

Start the Expo development server:

```bash
npm start
```

or

```bash
expo start
```

This will:
- Start the Metro bundler
- Open Expo DevTools in your browser
- Display a QR code in the terminal

### Running on iOS Simulator (Mac only)

```bash
npm run ios
```

or

```bash
expo start --ios
```

### Running on Android Emulator

```bash
npm run android
```

or

```bash
expo start --android
```

### Running on Physical Device

1. Install **Expo Go** app on your device:
   - iOS: [App Store](https://apps.apple.com/app/expo-go/id982107779)
   - Android: [Google Play](https://play.google.com/store/apps/details?id=host.exp.exponent)

2. Scan the QR code displayed in the terminal with:
   - iOS: Camera app
   - Android: Expo Go app

3. The app will load on your device

## Project Structure

```
shopkeeper-mobile/
├── src/
│   ├── screens/          # Screen components
│   │   ├── DashboardScreen.js
│   │   ├── RecordTransactionScreen.js
│   │   ├── CreditScoreScreen.js
│   │   ├── InventoryScreen.js
│   │   └── CooperativeScreen.js
│   ├── components/       # Reusable components
│   │   ├── VoiceRecorder.js
│   │   ├── TransactionCard.js
│   │   ├── CreditScoreCard.js
│   │   └── ProductCard.js
│   ├── services/         # API services
│   │   └── api.js
│   ├── navigation/       # Navigation setup
│   │   └── AppNavigator.js
│   ├── utils/            # Utility functions
│   │   └── offlineStorage.js
│   └── App.js            # Main app component
├── package.json
├── app.json
└── babel.config.js
```

## Features

### 1. Dashboard
- Daily sales summary
- Recent transactions
- Quick actions
- Stats cards (sales, credits, inventory alerts)

### 2. Record Transaction
- Voice recording for transaction input
- Transaction type selection (Sale/Credit/Repay)
- Amount and customer input
- Offline support with sync

### 3. Credit Score
- Vishwas Score display (300-900)
- Blockchain verification badge
- Score breakdown and explanation
- Historical trends

### 4. Inventory Management
- Product list with search
- Add/edit/delete products
- Stock quantity management
- Low stock alerts
- Category filtering

### 5. Cooperatives
- List available cooperatives
- Join/leave cooperatives
- View members
- Bulk order history
- Revenue split information

## API Integration

The app connects to the Flask API at `http://localhost:5000/api`. Ensure:

1. **Backend API is running** on port 5000
2. **CORS is enabled** for mobile app origins
3. **API endpoints** match the expected format

### Required API Endpoints

- `GET /api/transactions` - Get transactions
- `POST /api/transactions` - Create transaction
- `GET /api/shopkeeper/:id/credit-score` - Get credit score
- `GET /api/shopkeeper/:id/inventory` - Get inventory
- `PUT /api/shopkeeper/:id/inventory/:product_id` - Update inventory
- `GET /api/cooperative` - Get cooperatives
- `POST /api/cooperative/:id/join` - Join cooperative
- `POST /api/transactions/transcribe` - Upload audio for transcription

## Offline Support

The app includes offline storage using AsyncStorage:

- Transactions saved locally when offline
- Automatic sync when connection is restored
- Sync queue for failed API calls
- Conflict resolution

## Troubleshooting

### Common Issues

1. **Metro bundler won't start**
   ```bash
   npm start -- --reset-cache
   ```

2. **App won't connect to API**
   - Check API_BASE_URL in `src/services/api.js`
   - Ensure backend is running
   - For physical device, use computer's IP address instead of localhost

3. **Voice recording not working**
   - Check microphone permissions
   - Ensure `expo-av` is properly installed
   - Test on physical device (simulator may not support audio)

4. **Navigation errors**
   - Clear cache: `npm start -- --reset-cache`
   - Reinstall dependencies: `rm -rf node_modules && npm install`

5. **Build errors**
   - Clear Expo cache: `expo start -c`
   - Update Expo CLI: `npm install -g expo-cli@latest`

## Building for Production

### iOS

```bash
expo build:ios
```

### Android

```bash
expo build:android
```

## Testing

### Manual Testing Checklist

- [ ] Dashboard loads and displays stats
- [ ] Voice recording works
- [ ] Transaction creation works
- [ ] Credit score displays correctly
- [ ] Inventory CRUD operations work
- [ ] Cooperative join/leave works
- [ ] Offline mode saves transactions
- [ ] Sync works when back online

## Environment Variables

Create a `.env` file (optional):

```env
EXPO_PUBLIC_API_URL=http://localhost:5000/api
```

## Support

For issues or questions, refer to:
- [Expo Documentation](https://docs.expo.dev/)
- [React Native Documentation](https://reactnative.dev/)
- Project documentation in `/docs`

## License

This project is part of the Shopkeeper Management System.

