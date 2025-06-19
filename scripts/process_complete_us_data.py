#!/usr/bin/env python3
"""
Process complete US Watershed Boundary Dataset (HUC 17 + 18) for Cascadia region.
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

def load_complete_us_watersheds():
    """Load US watershed boundary data from both HUC 17 and 18."""
    data_dir = Path(__file__).parent.parent / 'data' / 'raw' / 'us_wbd_complete'
    
    logger.info("Loading complete US watershed data (HUC 17 + 18)...")
    
    # Paths to HUC12 data in both regions
    huc17_path = data_dir / 'huc_17' / 'Shape' / 'WBDHU12.shp'
    huc18_path = data_dir / 'huc_18' / 'Shape' / 'WBDHU12.shp'
    
    gdfs = []
    
    # Load HUC 17 (Pacific Northwest)
    if huc17_path.exists():
        try:
            huc17_gdf = gpd.read_file(huc17_path)
            logger.info(f"Loaded {len(huc17_gdf)} HUC12 watersheds from region 17")
            gdfs.append(huc17_gdf)
        except Exception as e:
            logger.error(f"Error loading HUC 17: {e}")
    
    # Load HUC 18 (California)
    if huc18_path.exists():
        try:
            huc18_gdf = gpd.read_file(huc18_path)
            logger.info(f"Loaded {len(huc18_gdf)} HUC12 watersheds from region 18")
            gdfs.append(huc18_gdf)
        except Exception as e:
            logger.error(f"Error loading HUC 18: {e}")
    
    if not gdfs:
        logger.error("No watershed data loaded")
        return None
    
    # Combine all regions
    if len(gdfs) > 1:
        combined_gdf = pd.concat(gdfs, ignore_index=True)
        combined_gdf = gpd.GeoDataFrame(combined_gdf, crs=gdfs[0].crs)
    else:
        combined_gdf = gdfs[0]
    
    logger.info(f"Combined total: {len(combined_gdf)} HUC12 watersheds")
    logger.info(f"Columns: {list(combined_gdf.columns)}")
    
    return combined_gdf

def filter_cascadia_watersheds(watersheds_gdf):
    """Filter watersheds to Cascadia region using boundary file."""
    
    logger.info("Loading Cascadia boundary and filtering watersheds...")
    
    try:
        # Load Cascadia boundary
        boundary_path = Path(__file__).parent.parent / 'data' / 'raw' / 'cascadia_boundary' / 'cascadia_boundary_simple.gpkg'
        cascadia_boundary = gpd.read_file(boundary_path)
        
        # Ensure both datasets use the same CRS
        if watersheds_gdf.crs != cascadia_boundary.crs:
            cascadia_boundary = cascadia_boundary.to_crs(watersheds_gdf.crs)
        
        logger.info(f"Loaded Cascadia boundary with CRS: {cascadia_boundary.crs}")
        
        # Spatial intersection - keep watersheds that overlap with Cascadia boundary
        cascadia_watersheds = gpd.overlay(watersheds_gdf, cascadia_boundary, how='intersection')
        
        logger.info(f"Filtered to {len(cascadia_watersheds)} HUC12 watersheds in Cascadia region")
        
        # Check coverage bounds
        bounds = cascadia_watersheds.to_crs('EPSG:4326').total_bounds
        logger.info(f"Coverage bounds (WGS84): {bounds[1]:.2f}°N to {bounds[3]:.2f}°N, {bounds[0]:.2f}°W to {bounds[2]:.2f}°W")
        
        return cascadia_watersheds
        
    except Exception as e:
        logger.error(f"Error filtering watersheds: {e}")
        return None

def create_unified_schema(cascadia_watersheds):
    """Create unified schema for watershed data."""
    
    logger.info("Creating unified schema...")
    
    try:
        # Reproject entire dataset once for area calculations
        logger.info("Reprojecting to equal-area projection for area calculations...")
        cascadia_proj = cascadia_watersheds.to_crs('EPSG:3310')  # California Albers
        
        # Extract hierarchical HUC codes (vectorized)
        huc12_codes = cascadia_watersheds['huc12'].fillna('')
        huc10_codes = huc12_codes.str[:10]
        huc8_codes = huc12_codes.str[:8]
        
        # Calculate areas in square kilometers (vectorized)
        areas_sqkm = cascadia_proj.geometry.area / 1000000
        
        # Create unified dataset
        unified_gdf = cascadia_watersheds.copy()
        
        # Add standardized columns
        unified_gdf['unique_id'] = 'US_HUC12_' + huc12_codes
        # Use 'name' column from original data, fallback to empty string
        name_col = cascadia_watersheds.get('name', pd.Series([''] * len(cascadia_watersheds)))
        unified_gdf['watershed_name'] = name_col.fillna('')
        unified_gdf['country'] = 'United States'
        unified_gdf['huc12_code'] = huc12_codes
        unified_gdf['huc10_code'] = huc10_codes
        unified_gdf['huc8_code'] = huc8_codes
        unified_gdf['sdac_ssda_code'] = ''
        unified_gdf['sdac_sda_code'] = ''
        unified_gdf['sdac_mda_code'] = ''
        unified_gdf['area_sqkm'] = areas_sqkm
        
        # Keep only needed columns
        keep_columns = ['unique_id', 'watershed_name', 'country', 'huc12_code', 'huc10_code', 
                       'huc8_code', 'sdac_ssda_code', 'sdac_sda_code', 'sdac_mda_code', 'area_sqkm', 'geometry']
        unified_gdf = unified_gdf[keep_columns]
        
        logger.info(f"Created unified dataset with {len(unified_gdf)} records")
        
        return unified_gdf
        
    except Exception as e:
        logger.error(f"Error creating unified schema: {e}")
        return None

def save_processed_data(unified_gdf):
    """Save processed data to GeoPackage format."""
    
    output_dir = Path(__file__).parent.parent / 'data'
    
    # Save both as processed file and as main dataset
    processed_path = output_dir / 'processed' / 'us_watersheds_cascadia_complete.gpkg'
    main_path = output_dir / 'cascadia_watersheds.gpkg'
    
    # Ensure processed directory exists
    processed_path.parent.mkdir(exist_ok=True)
    
    logger.info(f"Saving processed data...")
    
    try:
        # Save processed version
        unified_gdf.to_file(processed_path, driver='GPKG')
        logger.info(f"Saved processed data to {processed_path}")
        
        # Save as main dataset (overwrite previous)
        unified_gdf.to_file(main_path, driver='GPKG')
        logger.info(f"Saved main dataset to {main_path}")
        
        # Print summary statistics
        logger.info("Summary statistics:")
        logger.info(f"  Total watersheds: {len(unified_gdf)}")
        logger.info(f"  Total area: {unified_gdf['area_sqkm'].sum():.2f} sq km")
        logger.info(f"  Average area: {unified_gdf['area_sqkm'].mean():.2f} sq km")
        
        # Coverage bounds
        bounds = unified_gdf.to_crs('EPSG:4326').total_bounds
        logger.info(f"  Coverage: {bounds[1]:.2f}°N to {bounds[3]:.2f}°N, {bounds[0]:.2f}°W to {bounds[2]:.2f}°W")
        
        return main_path
        
    except Exception as e:
        logger.error(f"Error saving processed data: {e}")
        return None

def main():
    """Main processing function."""
    
    logger.info("Starting complete US watershed data processing...")
    
    # Load complete US watershed data (HUC 17 + 18)
    watersheds_gdf = load_complete_us_watersheds()
    if watersheds_gdf is None:
        logger.error("Failed to load watershed data")
        return
    
    # Filter to Cascadia region
    cascadia_watersheds = filter_cascadia_watersheds(watersheds_gdf)
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
        logger.info(f"Complete US watershed processing finished successfully!")
        logger.info(f"Main dataset available at: {output_path}")
    else:
        logger.error("Failed to save processed data")

if __name__ == '__main__':
    main()