"""
Store clustering service - Geographic clustering algorithms
"""
from database.models import Shopkeeper
from services.order_routing.order_routing import calculate_distance
import logging

logger = logging.getLogger(__name__)


def calculate_cluster_center(stores):
    """
    Calculate cluster center (centroid) from store locations
    
    Args:
        stores: List of shopkeeper objects with location
    
    Returns:
        dict: Center location with 'latitude' and 'longitude'
    """
    if not stores:
        return None
    
    valid_stores = [s for s in stores if s.location]
    if not valid_stores:
        return None
    
    total_lat = sum(s.location.latitude for s in valid_stores)
    total_lon = sum(s.location.longitude for s in valid_stores)
    
    return {
        'latitude': total_lat / len(valid_stores),
        'longitude': total_lon / len(valid_stores)
    }


def get_nearby_stores(store_id, radius_km=5):
    """
    Get nearby stores within radius
    
    Args:
        store_id: Shopkeeper ID (reference store)
        radius_km: Radius in kilometers (default: 5)
    
    Returns:
        list: List of nearby shopkeeper dictionaries with distance
    """
    try:
        reference_store = Shopkeeper.objects.get(id=store_id)
    except Shopkeeper.DoesNotExist:
        return []
    
    if not reference_store.location:
        return []
    
    reference_location = {
        'latitude': reference_store.location.latitude,
        'longitude': reference_store.location.longitude
    }
    
    all_stores = Shopkeeper.objects(is_active=True, location__exists=True)
    
    nearby_stores = []
    for store in all_stores:
        if str(store.id) == str(store_id):
            continue
        
        store_location = {
            'latitude': store.location.latitude,
            'longitude': store.location.longitude
        }
        
        distance = calculate_distance(reference_location, store_location)
        
        if distance <= radius_km:
            nearby_stores.append({
                'shopkeeper_id': str(store.id),
                'name': store.name,
                'address': store.address,
                'phone': store.phone,
                'distance_km': round(distance, 2)
            })
    
    # Sort by distance
    nearby_stores.sort(key=lambda x: x['distance_km'])
    
    return nearby_stores


def cluster_stores_by_location(stores, max_distance_km=5):
    """
    Cluster stores geographically
    
    Args:
        stores: List of shopkeeper objects
        max_distance_km: Maximum distance within cluster (default: 5)
    
    Returns:
        list: List of clusters, each containing list of shopkeeper IDs
    """
    valid_stores = [s for s in stores if s.location]
    if not valid_stores:
        return []
    
    clusters = []
    assigned = set()
    
    for store in valid_stores:
        if str(store.id) in assigned:
            continue
        
        # Start new cluster
        cluster = [store]
        assigned.add(str(store.id))
        
        # Find nearby stores
        store_location = {
            'latitude': store.location.latitude,
            'longitude': store.location.longitude
        }
        
        for other_store in valid_stores:
            if str(other_store.id) in assigned:
                continue
            
            other_location = {
                'latitude': other_store.location.latitude,
                'longitude': other_store.location.longitude
            }
            
            distance = calculate_distance(store_location, other_location)
            
            if distance <= max_distance_km:
                cluster.append(other_store)
                assigned.add(str(other_store.id))
        
        clusters.append([str(s.id) for s in cluster])
    
    return clusters


def suggest_cooperative_members(store_id, radius_km=5):
    """
    Suggest stores for cooperative formation
    
    Args:
        store_id: Shopkeeper ID (reference store)
        radius_km: Radius in kilometers (default: 5)
    
    Returns:
        list: List of suggested shopkeeper dictionaries
    """
    nearby_stores = get_nearby_stores(store_id, radius_km)
    
    # Filter out stores already in cooperatives (optional enhancement)
    # For now, return all nearby stores
    
    return nearby_stores

