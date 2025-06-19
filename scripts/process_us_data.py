#!/usr/bin/env python3
"""
Process US Watershed Boundary Dataset for Cascadia region.
"""

import os
import sys
import geopandas as gpd
import pandas as pd
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_us_watersheds():
    """Load US watershed boundary data."""
    data_dir = Path(__file__).parent.parent / 'data' / 'raw' / 'us_wbd' / 'Shape'
    
    logger.info("Loading US watershed data...")
    
    # Load HUC12 watersheds (most detailed level)
    huc12_path = data_dir / 'WBDHU12.shp'
    huc10_path = data_dir / 'WBDHU10.shp'
    huc8_path = data_dir / 'WBDHU8.shp'
    
    if not huc12_path.exists():
        logger.error(f"HUC12 file not found: {huc12_path}")
        return None
    
    try:
        # Load HUC12 data (most detailed watersheds)
        huc12_gdf = gpd.read_file(huc12_path)
        logger.info(f"Loaded {len(huc12_gdf)} HUC12 watersheds")
        logger.info(f"HUC12 columns: {list(huc12_gdf.columns)}")
        
        # Load HUC10 and HUC8 for hierarchical info
        huc10_gdf = gpd.read_file(huc10_path)
        huc8_gdf = gpd.read_file(huc8_path)
        
        logger.info(f"Loaded {len(huc10_gdf)} HUC10 watersheds")
        logger.info(f"Loaded {len(huc8_gdf)} HUC8 watersheds")
        
        return huc12_gdf, huc10_gdf, huc8_gdf
        
    except Exception as e:
        logger.error(f"Error loading US watershed data: {e}")
        return None

def filter_cascadia_watersheds(huc12_gdf, huc10_gdf, huc8_gdf):
    """Filter watersheds to Cascadia region using boundary file."""
    
    logger.info("Loading Cascadia boundary and filtering watersheds...")
    
    try:
        # Load Cascadia boundary
        boundary_path = Path(__file__).parent.parent / 'data' / 'raw' / 'cascadia_boundary' / 'cascadia_boundary_simple.gpkg'
        cascadia_boundary = gpd.read_file(boundary_path)
        
        # Ensure both datasets use the same CRS
        if huc12_gdf.crs != cascadia_boundary.crs:
            cascadia_boundary = cascadia_boundary.to_crs(huc12_gdf.crs)
        
        logger.info(f"Loaded Cascadia boundary with CRS: {cascadia_boundary.crs}")
        
        # Spatial intersection - keep watersheds that overlap with Cascadia boundary
        cascadia_huc12 = gpd.overlay(huc12_gdf, cascadia_boundary, how='intersection')
        
        logger.info(f"Filtered to {len(cascadia_huc12)} HUC12 watersheds in Cascadia region")
        
        return cascadia_huc12
        
    except Exception as e:
        logger.error(f"Error filtering watersheds: {e}")
        return None

def create_unified_schema(cascadia_huc12):
    """Create unified schema for watershed data."""
    
    logger.info("Creating unified schema...")
    
    try:
        # Create unified dataset with standardized columns
        unified_data = []
        
        for idx, row in cascadia_huc12.iterrows():
            # Extract hierarchical HUC codes (use lowercase as seen in data)
            huc12_code = row.get('huc12', row.get('HUC12', ''))
            huc10_code = huc12_code[:10] if len(huc12_code) >= 10 else ''
            huc8_code = huc12_code[:8] if len(huc12_code) >= 8 else ''
            
            # Calculate area in square kilometers (convert from projected units to km²)
            # First reproject to equal-area projection for accurate area calculation
            temp_gdf = gpd.GeoDataFrame([row], crs=cascadia_huc12.crs)
            temp_gdf_proj = temp_gdf.to_crs('EPSG:3310')  # California Albers (good for Pacific Northwest)
            area_sqkm = temp_gdf_proj.geometry.area.iloc[0] / 1000000  # Convert m² to km²
            
            unified_record = {
                'unique_id': f"US_HUC12_{huc12_code}",
                'watershed_name': row.get('name', row.get('NAME', '')),
                'country': 'United States',
                'huc12_code': huc12_code,
                'huc10_code': huc10_code,
                'huc8_code': huc8_code,
                'sdac_ssda_code': '',  # Canadian only
                'sdac_sda_code': '',   # Canadian only
                'sdac_mda_code': '',   # Canadian only
                'area_sqkm': area_sqkm,
                'geometry': row.geometry
            }
            
            unified_data.append(unified_record)
        
        # Create GeoDataFrame
        unified_gdf = gpd.GeoDataFrame(unified_data, crs=cascadia_huc12.crs)
        logger.info(f"Created unified dataset with {len(unified_gdf)} records")
        
        return unified_gdf
        
    except Exception as e:
        logger.error(f"Error creating unified schema: {e}")
        return None

def save_processed_data(unified_gdf):
    """Save processed data to GeoPackage format."""
    
    output_dir = Path(__file__).parent.parent / 'data' / 'processed'
    output_dir.mkdir(exist_ok=True)
    
    output_path = output_dir / 'us_watersheds_cascadia.gpkg'
    
    logger.info(f"Saving processed data to {output_path}")
    
    try:
        unified_gdf.to_file(output_path, driver='GPKG')
        logger.info(f"Successfully saved {len(unified_gdf)} watersheds to {output_path}")
        
        # Print summary statistics
        logger.info("Summary statistics:")
        logger.info(f"  Total watersheds: {len(unified_gdf)}")
        logger.info(f"  Total area: {unified_gdf['area_sqkm'].sum():.2f} sq km")
        logger.info(f"  Average area: {unified_gdf['area_sqkm'].mean():.2f} sq km")
        
        return output_path
        
    except Exception as e:
        logger.error(f"Error saving processed data: {e}")
        return None

def main():
    """Main processing function."""
    
    logger.info("Starting US watershed data processing...")
    
    # Load US watershed data
    us_data = load_us_watersheds()
    if us_data is None:
        logger.error("Failed to load US watershed data")
        return
    
    huc12_gdf, huc10_gdf, huc8_gdf = us_data
    
    # Filter to Cascadia region
    cascadia_watersheds = filter_cascadia_watersheds(huc12_gdf, huc10_gdf, huc8_gdf)
    if cascadia_watersheds is None:
        logger.error("Failed to filter watersheds")
        return
    
    # Create unified schema
    unified_data = create_unified_schema(cascadia_watersheds)
    if unified_data is None:
        logger.error("Failed to create unified schema")
        return
    
    # Save processed data
    output_path = save_processed_data(unified_data)
    if output_path:
        logger.info(f"US watershed processing completed successfully!")
        logger.info(f"Output saved to: {output_path}")
    else:
        logger.error("Failed to save processed data")

if __name__ == '__main__':
    main()