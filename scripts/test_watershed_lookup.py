#!/usr/bin/env python3
"""
Test watershed lookup functionality with the processed data.
"""

import geopandas as gpd
from shapely.geometry import Point
from pathlib import Path
import logging
import time

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_watershed_data():
    """Load the unified watershed dataset."""
    data_path = Path(__file__).parent.parent / 'data' / 'cascadia_watersheds.gpkg'
    
    logger.info(f"Loading watershed data from {data_path}")
    
    try:
        watersheds_gdf = gpd.read_file(data_path)
        logger.info(f"Loaded {len(watersheds_gdf)} watersheds")
        logger.info(f"Dataset CRS: {watersheds_gdf.crs}")
        logger.info(f"Columns: {list(watersheds_gdf.columns)}")
        
        return watersheds_gdf
    except Exception as e:
        logger.error(f"Error loading watershed data: {e}")
        return None

def find_watershed(lat, lon, watersheds_data):
    """
    Find the watershed containing the given latitude and longitude.
    Based on the implementation from research.md.
    """
    logger.info(f"Finding watershed for coordinates: {lat}, {lon}")
    
    try:
        # Create a GeoDataFrame for the input point
        point_geom = Point(lon, lat)
        # Ensure the point uses the same CRS as the watershed data
        point_gdf = gpd.GeoDataFrame(
            {'query_id': [1]}, 
            geometry=[point_geom], 
            crs='EPSG:4326'  # Input coordinates are in WGS84
        )
        
        # Convert point to same CRS as watershed data if needed
        if point_gdf.crs != watersheds_data.crs:
            point_gdf = point_gdf.to_crs(watersheds_data.crs)
        
        # Perform the spatial join (point-in-polygon)
        # This is highly optimized and uses the spatial index
        start_time = time.time()
        result_gdf = gpd.sjoin(point_gdf, watersheds_data, how="inner", predicate="within")
        query_time = time.time() - start_time
        
        logger.info(f"Query completed in {query_time:.4f} seconds")
        
        return result_gdf, query_time
        
    except Exception as e:
        logger.error(f"Error during spatial join: {e}")
        return gpd.GeoDataFrame(), 0

def test_sample_locations():
    """Test watershed lookup with sample locations."""
    
    # Load watershed data once
    watersheds_gdf = load_watershed_data()
    if watersheds_gdf is None:
        logger.error("Failed to load watershed data")
        return
    
    # Test locations (lat, lon, description)
    test_locations = [
        (47.6062, -122.3321, "Seattle, WA"),
        (45.5152, -122.6784, "Portland, OR"),
        (49.2827, -123.1207, "Vancouver, BC (should be outside current dataset)"),
        (37.7749, -122.4194, "San Francisco, CA"),
        (43.0642, -87.9073, "Milwaukee, WI (outside Cascadia)"),
    ]
    
    logger.info("Testing watershed lookup with sample locations...")
    
    total_time = 0
    successful_queries = 0
    
    for lat, lon, description in test_locations:
        logger.info(f"\n--- Testing: {description} ---")
        
        result_gdf, query_time = find_watershed(lat, lon, watersheds_gdf)
        total_time += query_time
        
        if not result_gdf.empty:
            successful_queries += 1
            # Get the watershed information
            watershed_info = result_gdf.iloc[0]
            
            print(f"✅ Watershed found for {description}")
            print(f"   Watershed Name: {watershed_info.get('watershed_name', 'Unknown')}")
            print(f"   Unique ID: {watershed_info.get('unique_id', 'Unknown')}")
            print(f"   HUC12 Code: {watershed_info.get('huc12_code', 'N/A')}")
            print(f"   HUC10 Code: {watershed_info.get('huc10_code', 'N/A')}")
            print(f"   HUC8 Code: {watershed_info.get('huc8_code', 'N/A')}")
            print(f"   Area: {watershed_info.get('area_sqkm', 0):.2f} sq km")
            print(f"   Query time: {query_time:.4f} seconds")
        else:
            print(f"❌ No watershed found for {description}")
            print(f"   This location may be outside the current dataset coverage")
            print(f"   Query time: {query_time:.4f} seconds")
    
    # Performance summary
    logger.info(f"\n--- Performance Summary ---")
    logger.info(f"Total test locations: {len(test_locations)}")
    logger.info(f"Successful queries: {successful_queries}")
    logger.info(f"Total query time: {total_time:.4f} seconds")
    logger.info(f"Average query time: {total_time/len(test_locations):.4f} seconds")

def main():
    """Main test function."""
    logger.info("Starting watershed lookup tests...")
    test_sample_locations()
    logger.info("Watershed lookup tests completed!")

if __name__ == '__main__':
    main()