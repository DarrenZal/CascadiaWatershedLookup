#!/usr/bin/env python3
"""
Integrate Canadian watershed data with existing US data to create unified Cascadia dataset.

This script implements the integration strategy from the research report:
1. Load existing US WBD data
2. Load Canadian FWA data 
3. Harmonize schemas and coordinate systems
4. Create spatial stitching at the border
5. Build unified dataset with CASC_ID system
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

def load_existing_us_data():
    """Load the existing US watershed data."""
    
    us_data_path = Path('data/cascadia_watersheds.gpkg')
    
    if not us_data_path.exists():
        raise FileNotFoundError(f"US data not found at {us_data_path}")
    
    logger.info(f"Loading US watershed data from {us_data_path}")
    us_gdf = gpd.read_file(us_data_path)
    
    logger.info(f"Loaded {len(us_gdf)} US watersheds")
    logger.info(f"US data CRS: {us_gdf.crs}")
    logger.info(f"US data columns: {list(us_gdf.columns)}")
    
    return us_gdf

def load_canadian_data():
    """Load the Canadian watershed data."""
    
    can_data_path = Path('data/raw/canadian_hydro/bc_watersheds_unified_schema.gpkg')
    
    if not can_data_path.exists():
        raise FileNotFoundError(f"Canadian data not found at {can_data_path}")
    
    logger.info(f"Loading Canadian watershed data from {can_data_path}")
    can_gdf = gpd.read_file(can_data_path)
    
    logger.info(f"Loaded {len(can_gdf)} Canadian watersheds")
    logger.info(f"Canadian data CRS: {can_gdf.crs}")
    logger.info(f"Canadian data columns: {list(can_gdf.columns)}")
    
    return can_gdf

def harmonize_schemas(us_gdf, can_gdf):
    """
    Harmonize the schemas between US and Canadian data following research blueprint.
    Creates unified schema with CASC_ID system.
    """
    
    logger.info("Harmonizing US and Canadian schemas...")
    
    # Ensure both datasets are in the same CRS (WGS84)
    if us_gdf.crs != 'EPSG:4326':
        us_gdf = us_gdf.to_crs('EPSG:4326')
    if can_gdf.crs != 'EPSG:4326':
        can_gdf = can_gdf.to_crs('EPSG:4326')
    
    # Process US data to unified schema
    us_unified = []
    for idx, row in us_gdf.iterrows():
        # Generate CASC_ID for US watersheds
        if pd.notna(row.get('huc12_code')):
            casc_id = f"US-{row['huc12_code']}"
        else:
            casc_id = f"US-{row['unique_id']}"
        
        unified_row = {
            'CASC_ID': casc_id,
            'Native_ID': row.get('unique_id', row.get('huc12_code')),
            'Watershed_Name': row.get('watershed_name', ''),
            'Area_SqKm': row.get('area_sqkm', 0),
            'DataSource': 'WBD',
            'HUC_Code': row.get('huc12_code'),
            'FWA_Code': None,
            'Province_State': 'US',
            'Country': 'USA',
            
            # Hierarchical codes
            'HUC12': row.get('huc12_code'),
            'HUC10': row.get('huc10_code'),
            'HUC8': row.get('huc8_code'),
            
            # Canadian codes (null for US)
            'FWA_Assessment_ID': None,
            'FWA_Watershed_Code': None,
            'FWA_Principal_Drainage': None,
            
            'geometry': row['geometry']
        }
        us_unified.append(unified_row)
    
    # Process Canadian data to unified schema
    can_unified = []
    for idx, row in can_gdf.iterrows():
        casc_id = row.get('unique_id', f"BC-{idx+1:04d}")
        
        unified_row = {
            'CASC_ID': casc_id,
            'Native_ID': row.get('fwa_assessment_id', casc_id),
            'Watershed_Name': row.get('watershed_name', ''),
            'Area_SqKm': row.get('area_sqkm', 0),
            'DataSource': 'BC-FWA',
            'HUC_Code': None,
            'FWA_Code': row.get('fwa_watershed_code'),
            'Province_State': 'BC',
            'Country': 'CAN',
            
            # US codes (null for Canadian)
            'HUC12': None,
            'HUC10': None,
            'HUC8': None,
            
            # Canadian codes
            'FWA_Assessment_ID': row.get('fwa_assessment_id'),
            'FWA_Watershed_Code': row.get('fwa_watershed_code'),
            'FWA_Principal_Drainage': row.get('fwa_principal_drainage'),
            
            'geometry': row['geometry']
        }
        can_unified.append(unified_row)
    
    # Combine into single GeoDataFrame
    all_unified = us_unified + can_unified
    unified_gdf = gpd.GeoDataFrame(all_unified, crs='EPSG:4326')
    
    logger.info(f"Created unified dataset with {len(unified_gdf)} watersheds")
    logger.info(f"- US watersheds: {len(us_unified)}")
    logger.info(f"- Canadian watersheds: {len(can_unified)}")
    
    return unified_gdf

def identify_border_watersheds(unified_gdf):
    """
    Identify watersheds that are near the Canada-US border for potential cross-border connectivity.
    Following research recommendation for IJC harmonized data approach.
    """
    
    logger.info("Identifying border watersheds for cross-border connectivity...")
    
    # Define approximate border latitude (49th parallel)
    border_lat = 49.0
    border_buffer = 0.5  # degrees (roughly 55km)
    
    # Identify US watersheds near border
    us_border_mask = (
        (unified_gdf['Country'] == 'USA') & 
        (unified_gdf.geometry.bounds['maxy'] > border_lat - border_buffer)
    )
    us_border_watersheds = unified_gdf[us_border_mask].copy()
    
    # Identify Canadian watersheds near border
    can_border_mask = (
        (unified_gdf['Country'] == 'CAN') & 
        (unified_gdf.geometry.bounds['miny'] < border_lat + border_buffer)
    )
    can_border_watersheds = unified_gdf[can_border_mask].copy()
    
    logger.info(f"Found {len(us_border_watersheds)} US border watersheds")
    logger.info(f"Found {len(can_border_watersheds)} Canadian border watersheds")
    
    return us_border_watersheds, can_border_watersheds

def create_cross_border_topology(unified_gdf, us_border, can_border):
    """
    Create simplified cross-border topological links.
    In production, this would use the IJC harmonized data as described in research.
    """
    
    logger.info("Creating cross-border topological connections...")
    
    # Add downstream connectivity field
    unified_gdf['Downstream_CASC_ID'] = None
    
    # For this demonstration, create simplified connections based on proximity
    # In production, would use actual hydrological flow analysis and IJC data
    
    connections_made = 0
    
    for idx, can_ws in can_border.iterrows():
        # Find nearest US watershed (simplified approach)
        can_centroid = can_ws.geometry.centroid
        
        # Calculate distances to US border watersheds
        distances = us_border.geometry.centroid.distance(can_centroid)
        
        if len(distances) > 0:
            nearest_us_idx = distances.idxmin()
            nearest_us_casc_id = us_border.loc[nearest_us_idx, 'CASC_ID']
            
            # Create connection if within reasonable distance (0.2 degrees ~ 22km)
            min_distance = distances.min()
            if min_distance < 0.2:
                unified_gdf.loc[unified_gdf['CASC_ID'] == can_ws['CASC_ID'], 'Downstream_CASC_ID'] = nearest_us_casc_id
                connections_made += 1
                logger.debug(f"Connected {can_ws['CASC_ID']} -> {nearest_us_casc_id} (distance: {min_distance:.3f}°)")
    
    logger.info(f"Created {connections_made} cross-border connections")
    
    return unified_gdf

def save_unified_dataset(unified_gdf, output_path):
    """Save the unified dataset to the main data file."""
    
    logger.info(f"Saving unified dataset to {output_path}")
    logger.info(f"Unified dataset columns: {list(unified_gdf.columns)}")
    logger.info(f"Unified dataset shape: {unified_gdf.shape}")
    
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Save to GeoPackage
    unified_gdf.to_file(output_path, driver='GPKG')
    
    logger.info(f"Saved {len(unified_gdf)} watersheds to {output_path}")
    
    # Verify the save worked correctly
    test_gdf = gpd.read_file(output_path)
    logger.info(f"Verification: Loaded {len(test_gdf)} rows with columns: {list(test_gdf.columns)}")
    
    if 'Country' in test_gdf.columns:
        country_counts = test_gdf['Country'].value_counts()
        logger.info(f"Country verification: {dict(country_counts)}")
    else:
        logger.warning("Country column not found in saved file!")
    
    # Print summary statistics
    print("\n" + "="*60)
    print("UNIFIED CASCADIA WATERSHED DATASET SUMMARY")
    print("="*60)
    
    total_area = unified_gdf['Area_SqKm'].sum()
    
    print(f"Total watersheds: {len(unified_gdf):,}")
    print(f"Total area: {total_area:,.0f} km²")
    print()
    
    # By country
    country_stats = unified_gdf.groupby('Country').agg({
        'CASC_ID': 'count',
        'Area_SqKm': 'sum'
    }).round(0)
    print("By Country:")
    for country, stats in country_stats.iterrows():
        print(f"  {country}: {stats['CASC_ID']:,} watersheds, {stats['Area_SqKm']:,.0f} km²")
    print()
    
    # By data source
    source_stats = unified_gdf.groupby('DataSource').agg({
        'CASC_ID': 'count',
        'Area_SqKm': 'sum'
    }).round(0)
    print("By Data Source:")
    for source, stats in source_stats.iterrows():
        print(f"  {source}: {stats['CASC_ID']:,} watersheds, {stats['Area_SqKm']:,.0f} km²")
    print()
    
    # Cross-border connections
    cross_border_connections = unified_gdf['Downstream_CASC_ID'].notna().sum()
    print(f"Cross-border connections: {cross_border_connections}")
    print()
    
    print("Integration completed successfully!")
    print("The unified dataset is now ready for cross-border watershed lookup.")

def main():
    """Main integration workflow."""
    
    print("Starting Canadian-US watershed data integration...")
    print("Following research report recommendations for hybrid data architecture.")
    print()
    
    try:
        # Step 1: Load existing data
        us_gdf = load_existing_us_data()
        can_gdf = load_canadian_data()
        
        # Step 2: Harmonize schemas
        unified_gdf = harmonize_schemas(us_gdf, can_gdf)
        
        # Step 3: Identify border watersheds
        us_border, can_border = identify_border_watersheds(unified_gdf)
        
        # Step 4: Create cross-border topology
        unified_gdf = create_cross_border_topology(unified_gdf, us_border, can_border)
        
        # Step 5: Save unified dataset
        output_path = Path('data/cascadia_watersheds.gpkg')
        save_unified_dataset(unified_gdf, output_path)
        
    except Exception as e:
        logger.error(f"Integration failed: {e}")
        raise

if __name__ == '__main__':
    main()