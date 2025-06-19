#!/usr/bin/env python3
"""
Inspect the watershed data to understand coverage.
"""

import geopandas as gpd
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def inspect_watershed_data():
    """Inspect the watershed data to understand coverage."""
    
    data_path = Path(__file__).parent.parent / 'data' / 'cascadia_watersheds.gpkg'
    
    try:
        watersheds_gdf = gpd.read_file(data_path)
        
        print("=== Watershed Data Inspection ===")
        print(f"Total watersheds: {len(watersheds_gdf)}")
        print(f"CRS: {watersheds_gdf.crs}")
        
        # Convert to WGS84 for bounds inspection
        watersheds_wgs84 = watersheds_gdf.to_crs('EPSG:4326')
        bounds = watersheds_wgs84.total_bounds
        
        print(f"\nBounds (WGS84):")
        print(f"  Min Longitude: {bounds[0]:.4f}")
        print(f"  Min Latitude: {bounds[1]:.4f}")
        print(f"  Max Longitude: {bounds[2]:.4f}")
        print(f"  Max Latitude: {bounds[3]:.4f}")
        
        # Sample a few watersheds
        print(f"\n=== Sample Watersheds ===")
        for i in range(min(5, len(watersheds_gdf))):
            row = watersheds_gdf.iloc[i]
            print(f"Watershed {i+1}:")
            print(f"  Name: {row.get('watershed_name', 'Unknown')}")
            print(f"  HUC12: {row.get('huc12_code', 'N/A')}")
            print(f"  Area: {row.get('area_sqkm', 0):.2f} sq km")
            
            # Get centroid
            centroid = row.geometry.centroid
            centroid_wgs84 = gpd.GeoSeries([centroid], crs=watersheds_gdf.crs).to_crs('EPSG:4326')
            print(f"  Centroid (WGS84): {centroid_wgs84.y.iloc[0]:.4f}, {centroid_wgs84.x.iloc[0]:.4f}")
            print()
        
        # Check if major cities should be covered
        print("=== Coverage Check for Major Cities ===")
        test_points = [
            (47.6062, -122.3321, "Seattle, WA"),
            (45.5152, -122.6784, "Portland, OR"),
        ]
        
        for lat, lon, city in test_points:
            within_bounds = (bounds[0] <= lon <= bounds[2] and bounds[1] <= lat <= bounds[3])
            print(f"{city}: {'✅ Within bounds' if within_bounds else '❌ Outside bounds'}")
            print(f"  Coordinates: {lat}, {lon}")
            print(f"  Bounds check: lon {bounds[0]:.4f} <= {lon} <= {bounds[2]:.4f}: {bounds[0] <= lon <= bounds[2]}")
            print(f"  Bounds check: lat {bounds[1]:.4f} <= {lat} <= {bounds[3]:.4f}: {bounds[1] <= lat <= bounds[3]}")
            print()
        
    except Exception as e:
        logger.error(f"Error inspecting data: {e}")

def main():
    inspect_watershed_data()

if __name__ == '__main__':
    main()