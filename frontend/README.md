# Frontend Applications

This directory contains two frontend applications:

1. **Shopkeeper Mobile App** - React Native mobile application
2. **Admin Dashboard** - React.js web dashboard

## Quick Start Guide

### Prerequisites

- Node.js (v16 or higher)
- npm or yarn
- Backend API running on `http://localhost:5000`

### Shopkeeper Mobile App

```bash
cd shopkeeper-mobile
npm install
npm start
```

See [shopkeeper-mobile/README.md](./shopkeeper-mobile/README.md) for detailed instructions.

### Admin Dashboard

```bash
cd admin-dashboard
npm install
npm start
```

See [admin-dashboard/README.md](./admin-dashboard/README.md) for detailed instructions.

## Architecture

Both applications connect to the Flask API backend:

```
┌─────────────────────┐
│  Flask API Backend  │
│   localhost:5000    │
└──────────┬──────────┘
           │
     ┌─────┴─────┐
     │           │
┌────▼────┐ ┌───▼────────┐
│ Mobile  │ │   Admin    │
│   App   │ │  Dashboard │
└─────────┘ └────────────┘
```

## API Base URL

Both applications use the same API base URL:
- Development: `http://localhost:5000/api`
- Production: Update in respective `src/services/api.js` files

## Development Workflow

1. **Start Backend API** (in `../backend/`)
2. **Start Mobile App** (for mobile testing)
3. **Start Admin Dashboard** (for web testing)

## Common Issues

### CORS Errors
Ensure backend has CORS enabled for:
- Mobile app origin
- Admin dashboard origin (`http://localhost:3000`)

### API Connection
- Verify backend is running
- Check API_BASE_URL in both apps
- For mobile device, use computer's IP instead of localhost

## Project Structure

```
frontend/
├── shopkeeper-mobile/     # React Native app
│   ├── src/
│   │   ├── screens/
│   │   ├── components/
│   │   ├── services/
│   │   └── navigation/
│   └── package.json
│
├── admin-dashboard/       # React.js dashboard
│   ├── src/
│   │   ├── pages/
│   │   ├── components/
│   │   └── services/
│   └── package.json
│
└── README.md              # This file
```

## Next Steps

1. Set up authentication (if required)
2. Configure environment variables
3. Test API integration
4. Deploy to production

For detailed setup instructions, see individual README files in each application directory.



