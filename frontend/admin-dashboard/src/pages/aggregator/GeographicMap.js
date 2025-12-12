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
  const [members, setMembers] = useState([]);
  const [serviceArea, setServiceArea] = useState({
    center: [28.6139, 77.2090], // Default: Delhi
    radius: 5000, // 5km radius
  });
  const [filters, setFilters] = useState({
    scoreRange: 'all',
    showServiceArea: true,
  });
  const [selectedMember, setSelectedMember] = useState(null);
  const [loading, setLoading] = useState(true);

  const cooperativeId = 'coop-001';

  useEffect(() => {
    loadMapData();
  }, []);

  const loadMapData = async () => {
    try {
      setLoading(true);
      
      const mapData = await apiService.getCooperativeMapData(cooperativeId);
      
      if (mapData.members && mapData.members.length > 0) {
        setMembers(mapData.members);
        
        // Calculate center based on members
        const avgLat = mapData.members.reduce((sum, m) => sum + (m.latitude || 0), 0) / mapData.members.length;
        const avgLng = mapData.members.reduce((sum, m) => sum + (m.longitude || 0), 0) / mapData.members.length;
        
        if (avgLat && avgLng) {
          setServiceArea({
            center: [avgLat, avgLng],
            radius: mapData.service_radius || 5000,
          });
        }
      }
    } catch (error) {
      console.error('Error loading map data:', error);
      // Set mock data for demonstration
      const mockMembers = [
        { id: 1, name: 'Krishna General Store', latitude: 28.6280, longitude: 77.2190, credit_score: 845, address: 'Connaught Place, Delhi' },
        { id: 2, name: 'Gupta Provisions', latitude: 28.6150, longitude: 77.2300, credit_score: 720, address: 'Karol Bagh, Delhi' },
        { id: 3, name: 'Sharma Kirana', latitude: 28.6350, longitude: 77.2050, credit_score: 680, address: 'Rajouri Garden, Delhi' },
        { id: 4, name: 'Verma Mart', latitude: 28.6050, longitude: 77.2150, credit_score: 590, address: 'Saket, Delhi' },
        { id: 5, name: 'Singh Store', latitude: 28.6200, longitude: 77.1950, credit_score: 420, address: 'Dwarka, Delhi' },
        { id: 6, name: 'Patel Groceries', latitude: 28.6400, longitude: 77.2250, credit_score: 780, address: 'Rohini, Delhi' },
        { id: 7, name: 'Mehta Supermart', latitude: 28.5950, longitude: 77.2350, credit_score: 650, address: 'Greater Kailash, Delhi' },
        { id: 8, name: 'Kumar Store', latitude: 28.6100, longitude: 77.2000, credit_score: 810, address: 'Janakpuri, Delhi' },
      ];
      setMembers(mockMembers);
    } finally {
      setLoading(false);
    }
  };

  const getFilteredMembers = () => {
    if (filters.scoreRange === 'all') return members;
    
    return members.filter(member => {
      const score = member.credit_score || 0;
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

  const filteredMembers = getFilteredMembers();

  const scoreSummary = {
    high: members.filter(m => (m.credit_score || 0) >= 700).length,
    medium: members.filter(m => (m.credit_score || 0) >= 500 && (m.credit_score || 0) < 700).length,
    low: members.filter(m => (m.credit_score || 0) < 500).length,
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
          <p className="page-subtitle">Cooperative service area and member locations</p>
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
                <span>Show Service Area</span>
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

          {/* Member List */}
          <div className="members-section">
            <h3 className="section-title">
              Members ({filteredMembers.length})
            </h3>
            <div className="member-list">
              {filteredMembers.map((member) => (
                <div
                  key={member.id}
                  className={`member-item ${selectedMember?.id === member.id ? 'selected' : ''}`}
                  onClick={() => setSelectedMember(member)}
                >
                  <div className="member-info">
                    <span className="member-name">{member.name}</span>
                    <span className="member-address">{member.address}</span>
                  </div>
                  <div
                    className="member-score"
                    style={{ 
                      color: getScoreColor(member.credit_score),
                      background: `${getScoreColor(member.credit_score)}15`
                    }}
                  >
                    {member.credit_score}
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

            {/* Service Area Circle */}
            {filters.showServiceArea && (
              <Circle
                center={serviceArea.center}
                radius={serviceArea.radius}
                pathOptions={{
                  color: '#10b981',
                  fillColor: '#10b981',
                  fillOpacity: 0.1,
                  weight: 2,
                  dashArray: '10, 10',
                }}
              />
            )}

            {/* Member Markers */}
            {filteredMembers.map((member) => (
              member.latitude && member.longitude && (
                <Marker
                  key={member.id}
                  position={[member.latitude, member.longitude]}
                  icon={createScoreIcon(member.credit_score || 0)}
                  eventHandlers={{
                    click: () => setSelectedMember(member),
                  }}
                >
                  <Popup>
                    <div className="marker-popup">
                      <h4 className="popup-title">{member.name}</h4>
                      <p className="popup-address">{member.address}</p>
                      <div className="popup-score">
                        <span className="popup-score-label">Vishwas Score:</span>
                        <span 
                          className="popup-score-value"
                          style={{ color: getScoreColor(member.credit_score) }}
                        >
                          {member.credit_score} ({getScoreLabel(member.credit_score)})
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

      {/* Selected Member Detail */}
      {selectedMember && (
        <div className="member-detail-panel">
          <div className="detail-header">
            <h3>{selectedMember.name}</h3>
            <button className="close-btn" onClick={() => setSelectedMember(null)}>×</button>
          </div>
          <div className="detail-content">
            <div className="detail-row">
              <span className="detail-label">Address</span>
              <span className="detail-value">{selectedMember.address}</span>
            </div>
            <div className="detail-row">
              <span className="detail-label">Vishwas Score</span>
              <span 
                className="detail-value score"
                style={{ color: getScoreColor(selectedMember.credit_score) }}
              >
                {selectedMember.credit_score} ({getScoreLabel(selectedMember.credit_score)})
              </span>
            </div>
            <div className="detail-row">
              <span className="detail-label">Coordinates</span>
              <span className="detail-value coords">
                {selectedMember.latitude?.toFixed(4)}, {selectedMember.longitude?.toFixed(4)}
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default GeographicMap;

