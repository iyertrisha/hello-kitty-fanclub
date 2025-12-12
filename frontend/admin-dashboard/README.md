# Admin Dashboard

React.js admin dashboard for managing shopkeepers, cooperatives, analytics, and blockchain logs.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Node.js** (v16 or higher)
- **npm** or **yarn**
- **Modern web browser** (Chrome, Firefox, Safari, Edge)

## Installation Steps

### 1. Navigate to the project directory

```bash
cd frontend/admin-dashboard
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

For production, update this to your production API URL.

### 4. Environment Variables (Optional)

Create a `.env` file in the root directory:

```env
REACT_APP_API_URL=http://localhost:5000/api
```

Then update `src/services/api.js` to use it:

```javascript
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';
```

## Running the Application

### Development Mode

Start the development server:

```bash
npm start
```

or

```bash
yarn start
```

The application will:
- Start on `http://localhost:3000`
- Automatically open in your default browser
- Hot-reload on file changes

### Production Build

Build the application for production:

```bash
npm run build
```

or

```bash
yarn build
```

This creates an optimized production build in the `build/` directory.

### Serve Production Build Locally

After building, you can serve it locally:

```bash
npm install -g serve
serve -s build
```

## Project Structure

```
admin-dashboard/
├── public/
│   └── index.html          # HTML template
├── src/
│   ├── pages/              # Page components
│   │   ├── Overview.js
│   │   ├── StoreManagement.js
│   │   ├── Cooperatives.js
│   │   ├── Analytics.js
│   │   └── BlockchainLogs.js
│   ├── components/         # Reusable components
│   │   ├── StatsCard.js
│   │   ├── SalesChart.js
│   │   ├── StoreTable.js
│   │   └── CooperativeCard.js
│   ├── services/          # API services
│   │   └── api.js
│   ├── App.js             # Main app component
│   ├── App.css            # App styles
│   ├── index.js           # Entry point
│   └── index.css          # Global styles
├── package.json
└── README.md
```

## Features

### 1. Overview Dashboard
- Total stores count
- Transaction statistics (today, week, month)
- Revenue statistics (today, week, month)
- Active cooperatives count
- Recent activity feed
- Sales trend chart

### 2. Store Management
- View all shopkeepers/stores
- Search and filter stores
- Sort by name, address, credit score, sales, status
- View, edit, delete stores
- Credit score display with color coding

### 3. Cooperative Management
- List all cooperatives
- Create new cooperatives
- View cooperative members
- Manage bulk orders
- Configure revenue split
- Add/remove members

### 4. Analytics
- Sales trends chart (area chart)
- Credit score distribution (bar chart)
- Revenue by cooperative (pie chart)
- Transaction volume over time (line chart)
- Date range filtering (week, month, quarter, year)

### 5. Blockchain Logs
- View all blockchain transactions
- Filter by shopkeeper, date range, type
- Display transaction hash, block number, timestamp
- Link to PolygonScan explorer
- Verification status indicators

## API Integration

The dashboard connects to the Flask API at `http://localhost:5000/api`. Ensure:

1. **Backend API is running** on port 5000
2. **CORS is enabled** for the dashboard origin (`http://localhost:3000`)
3. **API endpoints** match the expected format

### Required API Endpoints

- `GET /api/admin/overview` - Get overview statistics
- `GET /api/admin/stores` - Get all stores
- `PUT /api/admin/stores/:id` - Update store
- `DELETE /api/admin/stores/:id` - Delete store
- `GET /api/admin/cooperatives` - Get all cooperatives
- `POST /api/admin/cooperatives` - Create cooperative
- `PUT /api/admin/cooperatives/:id` - Update cooperative
- `DELETE /api/admin/cooperatives/:id` - Delete cooperative
- `GET /api/admin/analytics` - Get analytics data
- `GET /api/admin/blockchain-logs` - Get blockchain logs

## Authentication

Currently, the dashboard uses a simple token-based authentication stored in localStorage. For production:

1. Implement proper authentication flow
2. Add login page
3. Secure API endpoints with JWT tokens
4. Add role-based access control

To add authentication:

1. Create `src/pages/Login.js`
2. Update `src/App.js` to check for authentication
3. Add token to API requests in `src/services/api.js`

## Styling

The dashboard uses:
- **CSS Modules** for component-specific styles
- **Recharts** for data visualization
- **Responsive design** for mobile compatibility

## Troubleshooting

### Common Issues

1. **App won't start**
   ```bash
   # Clear cache and reinstall
   rm -rf node_modules package-lock.json
   npm install
   npm start
   ```

2. **API connection errors**
   - Check `API_BASE_URL` in `src/services/api.js`
   - Ensure backend API is running
   - Check CORS configuration on backend
   - Check browser console for errors

3. **Charts not rendering**
   - Ensure Recharts is installed: `npm install recharts`
   - Check browser console for errors
   - Verify data format matches chart expectations

4. **Build errors**
   ```bash
   # Clear build cache
   rm -rf build node_modules
   npm install
   npm run build
   ```

5. **Routing issues**
   - Ensure React Router is installed: `npm install react-router-dom`
   - Check browser console for route errors

## Testing

### Manual Testing Checklist

- [ ] Overview page loads and displays stats
- [ ] Store management table displays stores
- [ ] Search and filter work correctly
- [ ] Cooperative creation works
- [ ] Analytics charts render correctly
- [ ] Blockchain logs display correctly
- [ ] All API calls work
- [ ] Responsive design works on mobile

## Deployment

### Deploy to Netlify

1. Build the app: `npm run build`
2. Drag and drop the `build` folder to Netlify
3. Configure environment variables in Netlify dashboard

### Deploy to Vercel

1. Install Vercel CLI: `npm install -g vercel`
2. Run: `vercel`
3. Follow the prompts

### Deploy to AWS S3 + CloudFront

1. Build the app: `npm run build`
2. Upload `build` folder contents to S3 bucket
3. Configure CloudFront distribution
4. Set up custom domain (optional)

## Environment Variables

Create `.env` file for different environments:

```env
# Development
REACT_APP_API_URL=http://localhost:5000/api

# Production
REACT_APP_API_URL=https://api.yourdomain.com/api
```

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Performance Optimization

- Code splitting with React.lazy()
- Memoization for expensive components
- Optimized re-renders
- Lazy loading for charts
- Image optimization

## Security Considerations

- Never commit `.env` files
- Use HTTPS in production
- Implement proper authentication
- Validate all API responses
- Sanitize user inputs
- Use Content Security Policy headers

## Support

For issues or questions:
- Check browser console for errors
- Review API response format
- Refer to React documentation
- Check project documentation in `/docs`

## License

This project is part of the Shopkeeper Management System.

