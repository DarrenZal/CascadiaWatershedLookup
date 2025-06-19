#!/usr/bin/env python3
"""
Create sample Canadian watershed data for testing Cascadia integration.

Since the BC Freshwater Atlas Assessment Watersheds are not easily accessible
through automated downloads, this script creates sample data to demonstrate
the integration workflow described in the research report.
"""

import os
import sys
import geopandas as gpd
import pandas as pd
from shapely.geometry import Polygon, Point
import numpy as np
from pathlib import Path

# Add parent directory to path to import modules
sys.path.append(str(Path(__file__).parent.parent))

def create_sample_bc_watersheds():
    """
    Create sample BC Assessment Watersheds data following the research blueprint.
    
    Based on FWA Assessment Watersheds characteristics:
    - Target size: 2,000-10,000 hectares (20-100 km²)
    - FWA watershed codes (144-character topological strings)
    - BC Albers projection (EPSG:3005)
    """
    
    # Define Cascadia boundary approximate extent for BC portion
    # These coordinates roughly cover southern BC within Cascadia
    bc_bounds = {
        'min_lon': -125.0,
        'max_lon': -114.0,
        'min_lat': 49.0,
        'max_lat': 54.5
    }
    
    # Sample FWA codes representing different drainage basins
    sample_watersheds = []
    
    # Fraser River watersheds (code 100)
    fraser_watersheds = [
        {'code': '100-000000-000000-000000-000000-000000-0001', 'name': 'Lower Fraser', 'principal': 100},
        {'code': '100-000000-000000-000000-000000-000000-0002', 'name': 'Middle Fraser', 'principal': 100},
        {'code': '100-000000-000000-000000-000000-000000-0003', 'name': 'Upper Fraser', 'principal': 100},
        {'code': '100-000000-000000-000000-000000-000000-0004', 'name': 'Thompson River', 'principal': 100},
        {'code': '100-000000-000000-000000-000000-000000-0005', 'name': 'Chilcotin River', 'principal': 100},
    ]
    
    # Columbia River watersheds (code 300)
    columbia_watersheds = [
        {'code': '300-000000-000000-000000-000000-000000-0001', 'name': 'Kootenay River', 'principal': 300},
        {'code': '300-000000-000000-000000-000000-000000-0002', 'name': 'Columbia Upper', 'principal': 300},
        {'code': '300-000000-000000-000000-000000-000000-0003', 'name': 'Okanagan River', 'principal': 300},
        {'code': '300-000000-000000-000000-000000-000000-0004', 'name': 'Kettle River', 'principal': 300},
    ]
    
    # Coastal watersheds (code 900)
    coastal_watersheds = [
        {'code': '900-000000-000000-000000-000000-000000-0001', 'name': 'Squamish River', 'principal': 900},
        {'code': '900-000000-000000-000000-000000-000000-0002', 'name': 'Cheakamus River', 'principal': 900},
        {'code': '900-000000-000000-000000-000000-000000-0003', 'name': 'Capilano River', 'principal': 900},
        {'code': '920-000000-000000-000000-000000-000000-0001', 'name': 'Victoria Harbour', 'principal': 920},
        {'code': '920-000000-000000-000000-000000-000000-0002', 'name': 'Cowichan River', 'principal': 920},
    ]
    
    all_watersheds = fraser_watersheds + columbia_watersheds + coastal_watersheds
    
    # Create sample polygons distributed across BC
    geometries = []
    for i, watershed in enumerate(all_watersheds):
        # Special handling for Victoria Harbour watershed
        if watershed['name'] == 'Victoria Harbour':
            # Place Victoria watershed specifically around Victoria coordinates
            center_lon = -123.35  # Victoria area
            center_lat = 48.43
            size = 0.08  # Smaller watershed around Victoria
        else:
            # Distribute other watersheds across BC extent
            center_lon = bc_bounds['min_lon'] + (i % 5) * (bc_bounds['max_lon'] - bc_bounds['min_lon']) / 5
            center_lat = bc_bounds['min_lat'] + (i // 5) * (bc_bounds['max_lat'] - bc_bounds['min_lat']) / 3
            size = 0.15  # degrees
        
        # Create roughly square watershed polygon
        polygon = Polygon([
            (center_lon - size, center_lat - size),
            (center_lon + size, center_lat - size),
            (center_lon + size, center_lat + size),
            (center_lon - size, center_lat + size),
            (center_lon - size, center_lat - size)
        ])
        geometries.append(polygon)
    
    # Build GeoDataFrame with FWA schema
    gdf_data = []
    for i, (watershed, geom) in enumerate(zip(all_watersheds, geometries)):
        # Calculate area in square kilometers (rough approximation)
        area_sqkm = geom.area * 111.32 * 111.32  # Rough conversion from degrees to km²
        
        # Create assessment watershed ID (simplified)
        assessment_id = f"AW_{watershed['principal']:03d}_{i+1:04d}"
        
        row = {
            'ASSESSMENT_WATERSHED_ID': assessment_id,
            'WATERSHED_CODE': watershed['code'],
            'GNIS_NAME': watershed['name'],
            'FEATURE_AREA_SQM': area_sqkm * 1000000,  # Convert to square meters
            'WATERSHED_GROUP_CODE': f"{watershed['principal']:03d}",
            'LOCAL_WATERSHED_CODE': f"{i+1:04d}",
            'BLUE_LINE_KEY': f"BLK_{i+1:06d}",
            'WATERSHED_KEY': f"WK_{i+1:06d}",
            'FWA_WATERSHED_CODE': watershed['code'],
            'geometry': geom
        }
        gdf_data.append(row)
    
    # Create GeoDataFrame
    bc_gdf = gpd.GeoDataFrame(gdf_data, crs='EPSG:4326')
    
    # Transform to BC Albers (EPSG:3005) as per research recommendations
    bc_gdf = bc_gdf.to_crs('EPSG:3005')
    
    return bc_gdf

def create_unified_schema_sample(bc_gdf):
    """
    Convert BC FWA data to unified Cascadia schema following research blueprint.
    """
    
    unified_data = []
    
    for idx, row in bc_gdf.iterrows():
        # Generate CASC_ID following research recommendation
        casc_id = f"BC-{row['WATERSHED_GROUP_CODE']}-{row['ASSESSMENT_WATERSHED_ID']}"
        
        # Extract FWA codes for hierarchy
        fwa_code = row['WATERSHED_CODE']
        principal_code = row['WATERSHED_GROUP_CODE']
        
        # Simplified FWA hierarchy (research notes this is complex)
        # In real implementation, would need proper FWA code parsing
        fwa_hierarchy = {
            'principal_drainage': principal_code,
            'watershed_group': principal_code,
            'local_watershed': row['LOCAL_WATERSHED_CODE']
        }
        
        unified_row = {
            'unique_id': casc_id,
            'watershed_name': row['GNIS_NAME'],
            'country': 'CAN',
            'area_sqkm': row['FEATURE_AREA_SQM'] / 1000000,
            
            # US HUC codes (null for Canadian watersheds)
            'huc12_code': None,
            'huc10_code': None,
            'huc8_code': None,
            
            # Canadian FWA codes
            'fwa_watershed_code': fwa_code,
            'fwa_assessment_id': row['ASSESSMENT_WATERSHED_ID'],
            'fwa_principal_drainage': principal_code,
            
            # Additional Canadian fields following research schema
            'sdac_ssda_code': None,  # Would be populated with SDAC data
            'sdac_sda_code': None,
            'sdac_mda_code': None,
            
            'geometry': row['geometry']
        }
        
        unified_data.append(unified_row)
    
    return gpd.GeoDataFrame(unified_data, crs=bc_gdf.crs)

def main():
    """Main function to create sample Canadian data."""
    
    print("Creating sample BC Freshwater Atlas Assessment Watersheds data...")
    
    # Create output directory
    data_dir = Path(__file__).parent.parent / 'data' / 'raw' / 'canadian_hydro'
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Create sample BC watersheds
    bc_gdf = create_sample_bc_watersheds()
    print(f"Created {len(bc_gdf)} sample BC Assessment Watersheds")
    
    # Save original BC FWA format
    bc_output_path = data_dir / 'bc_fwa_assessment_watersheds_sample.gpkg'
    bc_gdf.to_file(bc_output_path, driver='GPKG')
    print(f"Saved BC FWA sample data to {bc_output_path}")
    
    # Create unified schema version
    unified_gdf = create_unified_schema_sample(bc_gdf)
    
    # Transform to WGS84 for consistency with US data
    unified_gdf = unified_gdf.to_crs('EPSG:4326')
    
    # Save unified format
    unified_output_path = data_dir / 'bc_watersheds_unified_schema.gpkg'
    unified_gdf.to_file(unified_output_path, driver='GPKG')
    print(f"Saved unified schema BC data to {unified_output_path}")
    
    # Print summary
    print("\nSample Data Summary:")
    print(f"- Total watersheds: {len(unified_gdf)}")
    print(f"- Fraser River basin: {len(unified_gdf[unified_gdf['fwa_principal_drainage'] == '100'])}")
    print(f"- Columbia River basin: {len(unified_gdf[unified_gdf['fwa_principal_drainage'] == '300'])}")
    print(f"- Coastal basins: {len(unified_gdf[unified_gdf['fwa_principal_drainage'].isin(['900', '920'])])}")
    print(f"- Average area: {unified_gdf['area_sqkm'].mean():.1f} km²")
    print(f"- Total area: {unified_gdf['area_sqkm'].sum():.0f} km²")
    
    print("\nNote: This is sample data for testing integration workflow.")
    print("For production, download actual BC FWA Assessment Watersheds from:")
    print("https://catalogue.data.gov.bc.ca/dataset/freshwater-atlas-assessment-watersheds")

if __name__ == '__main__':
    main()