#!/usr/bin/env python3
"""
Create unified dataset manually to ensure correct schema.
"""

import geopandas as gpd
import pandas as pd
from pathlib import Path

def create_unified_dataset():
    """Create a simplified unified dataset for testing."""
    
    print("Creating unified Cascadia watershed dataset...")
    
    # Load US data
    us_gdf = gpd.read_file('data/cascadia_watersheds_backup.gpkg')
    print(f"Loaded {len(us_gdf)} US watersheds")
    
    # Load Canadian data
    can_gdf = gpd.read_file('data/raw/canadian_hydro/bc_watersheds_unified_schema.gpkg')
    print(f"Loaded {len(can_gdf)} Canadian watersheds")
    
    # Ensure both are in same CRS
    if us_gdf.crs != can_gdf.crs:
        can_gdf = can_gdf.to_crs(us_gdf.crs)
    
    # Update US data to add Canadian-style fields
    us_gdf['datasource'] = 'WBD'
    us_gdf['fwa_watershed_code'] = None
    us_gdf['fwa_assessment_id'] = None
    us_gdf['fwa_principal_drainage'] = None
    
    # Update Canadian data to add US-style fields
    can_gdf['datasource'] = 'BC-FWA'
    
    # Select and rename columns for consistency
    us_columns = {
        'unique_id': 'casc_id',
        'watershed_name': 'watershed_name', 
        'country': 'country',
        'area_sqkm': 'area_sqkm',
        'huc12_code': 'huc12_code',
        'huc10_code': 'huc10_code', 
        'huc8_code': 'huc8_code',
        'datasource': 'datasource',
        'fwa_watershed_code': 'fwa_watershed_code',
        'fwa_assessment_id': 'fwa_assessment_id',
        'fwa_principal_drainage': 'fwa_principal_drainage',
        'geometry': 'geometry'
    }
    
    can_columns = {
        'unique_id': 'casc_id',
        'watershed_name': 'watershed_name',
        'country': 'country', 
        'area_sqkm': 'area_sqkm',
        'huc12_code': 'huc12_code',
        'huc10_code': 'huc10_code',
        'huc8_code': 'huc8_code', 
        'datasource': 'datasource',
        'fwa_watershed_code': 'fwa_watershed_code',
        'fwa_assessment_id': 'fwa_assessment_id',
        'fwa_principal_drainage': 'fwa_principal_drainage',
        'geometry': 'geometry'
    }
    
    # Select and rename columns
    us_selected = us_gdf[list(us_columns.keys())].rename(columns=us_columns)
    can_selected = can_gdf[list(can_columns.keys())].rename(columns=can_columns)
    
    # Combine datasets
    unified_gdf = pd.concat([us_selected, can_selected], ignore_index=True)
    unified_gdf = gpd.GeoDataFrame(unified_gdf, crs=us_gdf.crs)
    
    print(f"Created unified dataset with {len(unified_gdf)} watersheds")
    print(f"Columns: {list(unified_gdf.columns)}")
    
    # Print summary
    print(f"\nSummary by country:")
    if 'country' in unified_gdf.columns:
        for country, count in unified_gdf['country'].value_counts().items():
            print(f"  {country}: {count:,} watersheds")
    
    print(f"\nSummary by data source:")
    if 'datasource' in unified_gdf.columns:
        for source, count in unified_gdf['datasource'].value_counts().items():
            print(f"  {source}: {count:,} watersheds")
    
    # Save unified dataset
    output_path = Path('data/cascadia_watersheds.gpkg')
    unified_gdf.to_file(output_path, driver='GPKG')
    print(f"\nSaved to {output_path}")
    
    # Verify the save worked
    verification_gdf = gpd.read_file(output_path)
    print(f"Verification: Loaded {len(verification_gdf)} watersheds")
    print(f"Verification columns: {list(verification_gdf.columns)}")
    
    if 'country' in verification_gdf.columns:
        country_counts = verification_gdf['country'].value_counts()
        print(f"Verification countries: {dict(country_counts)}")
    
    return unified_gdf

if __name__ == '__main__':
    unified_gdf = create_unified_dataset()