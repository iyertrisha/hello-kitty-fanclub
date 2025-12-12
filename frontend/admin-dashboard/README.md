# KiranaChain Admin Dashboards

Two role-based admin dashboards for the KiranaChain platform.

## Dashboard Architecture

This application provides two distinct dashboards:

### 1. Platform Admin Dashboard (`/platform-admin`)
**Who:** Platform operators/maintainers  
**Access Level:** Read-only + Flagging only

#### Features:
- **Overview** - Platform health monitoring + Credit Score Summary
- **Store Management** - View stores, flag issues, credit score filtering
- **Blockchain Logs** - All transactions (read-only) with PolygonScan links
- **Analytics** - Platform insights + Credit Score Distribution

#### What Platform Admin CAN do:
- View all platform data (read-only)
- Flag stores for review
- Monitor platform health
- Generate reports

#### What Platform Admin CANNOT do:
- Add/edit/delete stores
- Modify transactions
- Change credit scores
- Manipulate cooperative data

---

### 2. Aggregator/Cooperative Dashboard (`/aggregator`)
**Who:** Cooperative managers/coordinators  
**Access Level:** Cooperative data only

#### Features:
- **Cooperative Overview** - Health + Member Credit Scores
- **Geographic Map** - Service area + Member locations with scores
- **Cooperative Orders** - Order management + Fulfillment
- **Blockchain Logs** - Cooperative transactions only

#### What Aggregator CAN do:
- View cooperative members (read-only)
- Manage cooperative orders
- View cooperative analytics
- Coordinate bulk orders
- View blockchain logs (cooperative only)

#### What Aggregator CANNOT do:
- View other cooperatives' data
- Modify individual store data
- Access platform admin functions

---

## Vishwas Score Integration

ML-based credit score (300-900 range) integrated across all pages:

**Score Ranges:**
- 🟢 **700-900 (Excellent)** - High creditworthiness
- 🟡 **500-700 (Good)** - Moderate creditworthiness
- 🔴 **300-500 (Needs Attention)** - Lower creditworthiness

**Calculated from 5 factors:**
1. Transaction consistency (25%)
2. Business growth (20%)
3. Product diversity (15%)
4. Cooperative participation (15%)
5. Repayment history (25%)

---

## URLs

| Dashboard | URL | Description |
|-----------|-----|-------------|
| Dashboard Selector | `/` | Choose between dashboards |
| Platform Admin | `/platform-admin` | Platform monitoring |
| Platform Stores | `/platform-admin/stores` | Store management |
| Platform Blockchain | `/platform-admin/blockchain` | All transactions |
| Platform Analytics | `/platform-admin/analytics` | Platform insights |
| Aggregator Overview | `/aggregator` | Cooperative health |
| Geographic Map | `/aggregator/map` | Service area visualization |
| Cooperative Orders | `/aggregator/orders` | Order management |
| Aggregator Blockchain | `/aggregator/blockchain` | Cooperative transactions |

---

## Getting Started

### Prerequisites
- Node.js 16+
- npm or yarn

### Installation

```bash
cd whackiest/frontend/admin-dashboard
npm install
```

### Running the Dashboard

```bash
npm start
```

The application will start at `http://localhost:3000`

### Environment Variables

Create a `.env.local` file:

```env
REACT_APP_API_URL=http://localhost:5000/api
```

---

## Tech Stack

- **React 18** - UI framework
- **React Router 6** - Routing
- **Recharts** - Data visualization
- **React-Leaflet** - Geographic mapping
- **Axios** - API client

---

## Project Structure

```
src/
├── pages/
│   ├── DashboardSelector.js    # Landing page
│   ├── platform-admin/         # Platform Admin pages
│   │   ├── Overview.js
│   │   ├── StoreManagement.js
│   │   ├── BlockchainLogs.js
│   │   └── Analytics.js
│   └── aggregator/             # Aggregator pages
│       ├── CooperativeOverview.js
│       ├── GeographicMap.js
│       ├── CooperativeOrders.js
│       └── BlockchainLogs.js
├── layouts/
│   ├── PlatformAdminLayout.js  # Platform sidebar
│   └── AggregatorLayout.js     # Aggregator sidebar
├── components/
│   ├── CreditScoreWidget.js    # Score summary widget
│   ├── StatsCard.js            # Statistics card
│   └── SalesChart.js           # Sales visualization
└── services/
    └── api.js                  # API methods
```

---

## API Endpoints

### Platform Admin Endpoints
- `GET /api/admin/overview` - Platform stats
- `GET /api/admin/stores` - All stores (read-only)
- `POST /api/admin/stores/{id}/flag` - Flag store
- `GET /api/admin/blockchain-logs` - All transactions
- `GET /api/admin/analytics` - Platform analytics

### Aggregator Endpoints
- `GET /api/cooperative/{id}/overview` - Cooperative stats
- `GET /api/cooperative/{id}/members` - Members (read-only)
- `GET /api/cooperative/{id}/orders` - Cooperative orders
- `GET /api/cooperative/{id}/blockchain-logs` - Cooperative transactions
- `GET /api/cooperative/{id}/map-data` - Geographic data

---

## Design Philosophy

1. **Read-only for admins** - Data ownership by creators
2. **Blockchain transparency** - All transactions verified
3. **Cooperative collaboration** - Geographic pooling
4. **Trust through scores** - Vishwas Score integration

---

## License

Part of the KiranaChain project.
