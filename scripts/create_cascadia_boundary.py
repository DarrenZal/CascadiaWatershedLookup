#!/usr/bin/env python3
"""
Create a simple Cascadia boundary for initial testing.
Based on coordinates from research.md (40°N to 60°N, 130°W to 110°W).
"""

import geopandas as gpd
from shapely.geometry import Polygon
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_cascadia_boundary():
    """Create a simple rectangular boundary for Cascadia based on research coordinates."""
    
    logger.info("Creating simple Cascadia boundary...")
    
    # Cascadia bounding box from research.md
    # Latitude: 40°N to 60°N, Longitude: 130°W to 110°W
    min_lon, min_lat = -130.0, 40.0
    max_lon, max_lat = -110.0, 60.0
    
    # Create rectangular polygon
    boundary_coords = [
        (min_lon, min_lat),  # Southwest
        (max_lon, min_lat),  # Southeast
        (max_lon, max_lat),  # Northeast
        (min_lon, max_lat),  # Northwest
        (min_lon, min_lat)   # Close the polygon
    ]
    
    # Create polygon
    cascadia_polygon = Polygon(boundary_coords)
    
    # Create GeoDataFrame
    gdf = gpd.GeoDataFrame(
        {'name': ['Cascadia Bioregion'], 'source': ['Simplified boundary']},
        geometry=[cascadia_polygon],
        crs='EPSG:4326'  # WGS84
    )
    
    # Save to file
    data_dir = Path(__file__).parent.parent / 'data' / 'raw' / 'cascadia_boundary'
    data_dir.mkdir(parents=True, exist_ok=True)
    
    output_path = data_dir / 'cascadia_boundary_simple.gpkg'
    gdf.to_file(output_path, driver='GPKG')
    
    logger.info(f"Created simple Cascadia boundary: {output_path}")
    logger.info(f"Boundary covers: {min_lat}°N to {max_lat}°N, {min_lon}°W to {max_lon}°W")
    
    return output_path

def main():
    """Main function."""
    boundary_path = create_cascadia_boundary()
    print(f"Cascadia boundary created at: {boundary_path}")

if __name__ == '__main__':
    main()