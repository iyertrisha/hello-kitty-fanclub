import React, { useEffect, useRef } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Circle } from 'react-leaflet';
import L from 'leaflet';
import './StoreMap.css';

// Fix for default marker icons in React Leaflet
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
});

const StoreMap = ({ stores, serviceAreaCenter, serviceAreaRadius, onStoreClick }) => {
  const mapRef = useRef(null);

  useEffect(() => {
    if (mapRef.current && stores.length > 0) {
      const map = mapRef.current;
      const bounds = L.latLngBounds(stores.map(s => [s.location.latitude, s.location.longitude]));
      
      if (serviceAreaCenter) {
        bounds.extend([serviceAreaCenter.latitude, serviceAreaCenter.longitude]);
      }
      
      map.fitBounds(bounds, { padding: [50, 50] });
    }
  }, [stores, serviceAreaCenter]);

  const getScoreColor = (score) => {
    if (score >= 700) return '#34d399';
    if (score >= 500) return '#fbbf24';
    return '#f87171';
  };

  const center = serviceAreaCenter 
    ? [serviceAreaCenter.latitude, serviceAreaCenter.longitude]
    : stores.length > 0
    ? [stores[0].location.latitude, stores[0].location.longitude]
    : [28.6139, 77.2090]; // Default: Delhi

  return (
    <div className="store-map-container">
      <MapContainer
        center={center}
        zoom={12}
        style={{ height: '600px', width: '100%' }}
        ref={mapRef}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        
        {serviceAreaCenter && serviceAreaRadius && (
          <Circle
            center={[serviceAreaCenter.latitude, serviceAreaCenter.longitude]}
            radius={serviceAreaRadius * 1000}
            pathOptions={{ color: '#667eea', fillColor: '#667eea', fillOpacity: 0.1 }}
          />
        )}

        {stores.map(store => (
          <Marker
            key={store.id}
            position={[store.location.latitude, store.location.longitude]}
            eventHandlers={{
              click: () => onStoreClick(store),
            }}
          >
            <Popup>
              <div className="map-popup">
                <h4>{store.name}</h4>
                <p>{store.address}</p>
                <p>
                  <strong>Credit Score:</strong>{' '}
                  <span style={{ color: getScoreColor(store.credit_score) }}>
                    {store.credit_score}
                  </span>
                </p>
                <p>
                  <strong>30-Day Sales:</strong> ₹{store.performance?.total_sales_30d?.toLocaleString() || 0}
                </p>
                {store.performance?.low_stock_count > 0 && (
                  <p className="low-stock-indicator">
                    ⚠️ {store.performance.low_stock_count} items low stock
                  </p>
                )}
                <button
                  onClick={() => onStoreClick(store)}
                  className="map-order-btn"
                >
                  Create Order
                </button>
              </div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  );
};

export default StoreMap;

