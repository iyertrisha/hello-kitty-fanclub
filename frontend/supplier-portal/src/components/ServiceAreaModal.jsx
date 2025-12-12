import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Circle, useMapEvents } from 'react-leaflet';
import L from 'leaflet';
import './ServiceAreaModal.css';

delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
});

function MapClickHandler({ onMapClick }) {
  useMapEvents({
    click: (e) => {
      onMapClick(e.latlng);
    },
  });
  return null;
}

const ServiceAreaModal = ({ currentServiceArea, currentRadius, onClose, onSave }) => {
  const [center, setCenter] = useState(
    currentServiceArea
      ? [currentServiceArea.latitude, currentServiceArea.longitude]
      : [28.6139, 77.2090] // Default: Delhi
  );
  const [radius, setRadius] = useState(currentRadius || 10);
  const [address, setAddress] = useState(currentServiceArea?.address || '');

  const handleMapClick = (latlng) => {
    setCenter([latlng.lat, latlng.lng]);
    // In a real app, you'd reverse geocode to get address
    setAddress(`${latlng.lat.toFixed(4)}, ${latlng.lng.toFixed(4)}`);
  };

  const handleSave = () => {
    onSave({
      center: {
        latitude: center[0],
        longitude: center[1],
        address: address
      },
      radius_km: radius
    });
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Set Service Area</h2>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>

        <div className="modal-body">
          <div className="map-container">
            <MapContainer
              center={center}
              zoom={12}
              style={{ height: '400px', width: '100%' }}
            >
              <TileLayer
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              />
              <MapClickHandler onMapClick={handleMapClick} />
              <Marker position={center} />
              <Circle
                center={center}
                radius={radius * 1000}
                pathOptions={{ color: '#667eea', fillColor: '#667eea', fillOpacity: 0.2 }}
              />
            </MapContainer>
          </div>

          <div className="form-controls">
            <div className="form-group">
              <label>Service Area Address</label>
              <input
                type="text"
                value={address}
                onChange={(e) => setAddress(e.target.value)}
                placeholder="Enter address or click on map"
              />
            </div>
            <div className="form-group">
              <label>Radius (km): {radius}</label>
              <input
                type="range"
                min="1"
                max="50"
                value={radius}
                onChange={(e) => setRadius(parseFloat(e.target.value))}
              />
            </div>
            <p className="help-text">Click on the map to set the center of your service area</p>
          </div>
        </div>

        <div className="modal-footer">
          <button className="btn-cancel" onClick={onClose}>Cancel</button>
          <button className="btn-save" onClick={handleSave}>Save Service Area</button>
        </div>
      </div>
    </div>
  );
};

export default ServiceAreaModal;

