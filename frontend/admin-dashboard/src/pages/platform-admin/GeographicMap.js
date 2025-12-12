import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Circle, useMap } from 'react-leaflet';
import L from 'leaflet';
import apiService from '../../services/api';
import 'leaflet/dist/leaflet.css';
import './GeographicMap.css';

// Fix for default marker icons in React-Leaflet
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
});

// Custom marker icon based on score
const createScoreIcon = (score) => {
  let color = '#f87171'; // Red for low
  if (score >= 700) color = '#34d399'; // Green for high
  else if (score >= 500) color = '#fbbf24'; // Yellow for medium

  return L.divIcon({
    className: 'custom-marker',
    html: `
      <div class="marker-container" style="background-color: ${color}20; border-color: ${color};">
        <div class="marker-dot" style="background-color: ${color};"></div>
        <span class="marker-score" style="color: ${color};">${score}</span>
      </div>
    `,
    iconSize: [50, 60],
    iconAnchor: [25, 60],
    popupAnchor: [0, -60],
  });
};

// Map center updater component
const MapCenterUpdater = ({ center }) => {
  const map = useMap();
  useEffect(() => {
    map.setView(center, map.getZoom());
  }, [center, map]);
  return null;
};

const GeographicMap = () => {
  const [stores, setStores] = useState([]);
  const [serviceArea, setServiceArea] = useState({
    center: [28.6139, 77.2090], // Default: Delhi
    radius: 5000, // 5km radius
  });
  const [filters, setFilters] = useState({
    scoreRange: 'all',
    showServiceArea: true,
  });
  const [selectedStore, setSelectedStore] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadMapData();
  }, []);

  const loadMapData = async () => {
    try {
      setLoading(true);
      
      const data = await apiService.getStores();
      const storesList = data.stores || data.data || data || [];
      
      // Map store data to include location info
      const mappedStores = storesList.map(store => ({
        id: store.id || store._id,
        name: store.name,
        address: store.address,
        credit_score: store.credit_score || 0,
        latitude: store.location?.latitude || store.latitude,
        longitude: store.location?.longitude || store.longitude,
        is_active: store.is_active,
        total_sales: store.total_sales_30d || 0,
      })).filter(store => store.latitude && store.longitude);
      
      setStores(mappedStores);
      
      // Calculate center based on stores with valid coordinates
      if (mappedStores.length > 0) {
        const avgLat = mappedStores.reduce((sum, s) => sum + (s.latitude || 0), 0) / mappedStores.length;
        const avgLng = mappedStores.reduce((sum, s) => sum + (s.longitude || 0), 0) / mappedStores.length;
        
        if (avgLat && avgLng) {
          setServiceArea({
            center: [avgLat, avgLng],
            radius: 5000,
          });
        }
      }
    } catch (error) {
      console.error('Error loading map data:', error);
      // Set mock data for demonstration
      const mockStores = [
        { id: 1, name: 'Krishna General Store', latitude: 28.6280, longitude: 77.2190, credit_score: 845, address: 'Connaught Place, Delhi' },
        { id: 2, name: 'Gupta Provisions', latitude: 28.6150, longitude: 77.2300, credit_score: 720, address: 'Karol Bagh, Delhi' },
        { id: 3, name: 'Sharma Kirana', latitude: 28.6350, longitude: 77.2050, credit_score: 680, address: 'Rajouri Garden, Delhi' },
        { id: 4, name: 'Verma Mart', latitude: 28.6050, longitude: 77.2150, credit_score: 590, address: 'Saket, Delhi' },
        { id: 5, name: 'Singh Store', latitude: 28.6200, longitude: 77.1950, credit_score: 420, address: 'Dwarka, Delhi' },
        { id: 6, name: 'Patel Groceries', latitude: 28.6400, longitude: 77.2250, credit_score: 780, address: 'Rohini, Delhi' },
        { id: 7, name: 'Mehta Supermart', latitude: 28.5950, longitude: 77.2350, credit_score: 650, address: 'Greater Kailash, Delhi' },
        { id: 8, name: 'Kumar Store', latitude: 28.6100, longitude: 77.2000, credit_score: 810, address: 'Janakpuri, Delhi' },
      ];
      setStores(mockStores);
    } finally {
      setLoading(false);
    }
  };

  const getFilteredStores = () => {
    if (filters.scoreRange === 'all') return stores;
    
    return stores.filter(store => {
      const score = store.credit_score || 0;
      if (filters.scoreRange === 'high') return score >= 700;
      if (filters.scoreRange === 'medium') return score >= 500 && score < 700;
      if (filters.scoreRange === 'low') return score < 500;
      return true;
    });
  };

  const getScoreColor = (score) => {
    if (score >= 700) return '#34d399';
    if (score >= 500) return '#fbbf24';
    return '#f87171';
  };

  const getScoreLabel = (score) => {
    if (score >= 700) return 'Excellent';
    if (score >= 500) return 'Good';
    return 'Needs Attention';
  };

  const filteredStores = getFilteredStores();

  const scoreSummary = {
    high: stores.filter(s => (s.credit_score || 0) >= 700).length,
    medium: stores.filter(s => (s.credit_score || 0) >= 500 && (s.credit_score || 0) < 700).length,
    low: stores.filter(s => (s.credit_score || 0) < 500).length,
  };

  if (loading) {
    return (
      <div className="geographic-map">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Loading map data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="geographic-map">
      <div className="page-header">
        <div className="header-content">
          <h1 className="page-title">Geographic Map</h1>
          <p className="page-subtitle">Platform stores and locations</p>
        </div>
        <div className="header-badge">
          <span className="read-only-badge">
            <span className="badge-icon">🔒</span>
            Read-Only
          </span>
        </div>
      </div>

      <div className="map-layout">
        {/* Sidebar */}
        <div className="map-sidebar">
          {/* Filters */}
          <div className="filter-section">
            <h3 className="section-title">Filters</h3>
            <div className="filter-group">
              <label className="filter-label">Vishwas Score Range</label>
              <select
                className="filter-select"
                value={filters.scoreRange}
                onChange={(e) => setFilters({ ...filters, scoreRange: e.target.value })}
              >
                <option value="all">All Scores</option>
                <option value="high">700+ (Excellent)</option>
                <option value="medium">500-699 (Good)</option>
                <option value="low">Below 500 (Needs Attention)</option>
              </select>
            </div>
            <div className="filter-group">
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={filters.showServiceArea}
                  onChange={(e) => setFilters({ ...filters, showServiceArea: e.target.checked })}
                />
                <span>Show Coverage Area</span>
              </label>
            </div>
          </div>

          {/* Score Summary */}
          <div className="summary-section">
            <h3 className="section-title">Score Summary</h3>
            <div className="score-summary">
              <div className="summary-item">
                <span className="summary-dot high"></span>
                <span className="summary-label">Excellent (700+)</span>
                <span className="summary-count">{scoreSummary.high}</span>
              </div>
              <div className="summary-item">
                <span className="summary-dot medium"></span>
                <span className="summary-label">Good (500-699)</span>
                <span className="summary-count">{scoreSummary.medium}</span>
              </div>
              <div className="summary-item">
                <span className="summary-dot low"></span>
                <span className="summary-label">Needs Attention</span>
                <span className="summary-count">{scoreSummary.low}</span>
              </div>
            </div>
          </div>

          {/* Store List */}
          <div className="stores-section">
            <h3 className="section-title">
              Stores ({filteredStores.length})
            </h3>
            <div className="store-list">
              {filteredStores.map((store) => (
                <div
                  key={store.id}
                  className={`store-item ${selectedStore?.id === store.id ? 'selected' : ''}`}
                  onClick={() => setSelectedStore(store)}
                >
                  <div className="store-info">
                    <span className="store-name">{store.name}</span>
                    <span className="store-address">{store.address}</span>
                  </div>
                  <div
                    className="store-score"
                    style={{ 
                      color: getScoreColor(store.credit_score),
                      background: `${getScoreColor(store.credit_score)}15`
                    }}
                  >
                    {store.credit_score}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Map Container */}
        <div className="map-container">
          <MapContainer
            center={serviceArea.center}
            zoom={12}
            style={{ height: '100%', width: '100%' }}
          >
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
              url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
            />
            
            <MapCenterUpdater center={serviceArea.center} />

            {/* Coverage Area Circle */}
            {filters.showServiceArea && (
              <Circle
                center={serviceArea.center}
                radius={serviceArea.radius}
                pathOptions={{
                  color: '#3b82f6',
                  fillColor: '#3b82f6',
                  fillOpacity: 0.1,
                  weight: 2,
                  dashArray: '10, 10',
                }}
              />
            )}

            {/* Store Markers */}
            {filteredStores.map((store) => (
              store.latitude && store.longitude && (
                <Marker
                  key={store.id}
                  position={[store.latitude, store.longitude]}
                  icon={createScoreIcon(store.credit_score || 0)}
                  eventHandlers={{
                    click: () => setSelectedStore(store),
                  }}
                >
                  <Popup>
                    <div className="marker-popup">
                      <h4 className="popup-title">{store.name}</h4>
                      <p className="popup-address">{store.address}</p>
                      <div className="popup-score">
                        <span className="popup-score-label">Vishwas Score:</span>
                        <span 
                          className="popup-score-value"
                          style={{ color: getScoreColor(store.credit_score) }}
                        >
                          {store.credit_score} ({getScoreLabel(store.credit_score)})
                        </span>
                      </div>
                    </div>
                  </Popup>
                </Marker>
              )
            ))}
          </MapContainer>
        </div>
      </div>

      {/* Selected Store Detail */}
      {selectedStore && (
        <div className="store-detail-panel">
          <div className="detail-header">
            <h3>{selectedStore.name}</h3>
            <button className="close-btn" onClick={() => setSelectedStore(null)}>×</button>
          </div>
          <div className="detail-content">
            <div className="detail-row">
              <span className="detail-label">Address</span>
              <span className="detail-value">{selectedStore.address}</span>
            </div>
            <div className="detail-row">
              <span className="detail-label">Vishwas Score</span>
              <span 
                className="detail-value score"
                style={{ color: getScoreColor(selectedStore.credit_score) }}
              >
                {selectedStore.credit_score} ({getScoreLabel(selectedStore.credit_score)})
              </span>
            </div>
            <div className="detail-row">
              <span className="detail-label">Coordinates</span>
              <span className="detail-value coords">
                {selectedStore.latitude?.toFixed(4)}, {selectedStore.longitude?.toFixed(4)}
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default GeographicMap;

