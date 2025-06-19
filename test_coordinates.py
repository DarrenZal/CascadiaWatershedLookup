#!/usr/bin/env python3
"""
Test watershed lookup using direct coordinates to verify Canadian integration.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from watershed_lookup import CascadiaWatershedLookup

def test_coordinates():
    """Test watershed lookup using direct coordinates."""
    
    print("Testing Watershed Lookup with Direct Coordinates")
    print("=" * 50)
    
    # Initialize the service with correct data path
    lookup = CascadiaWatershedLookup('data/cascadia_watersheds.gpkg')
    
    if lookup.watersheds_gdf is None:
        print("Failed to load watershed data!")
        return
    
    print(f"Loaded {len(lookup.watersheds_gdf)} watersheds")
    
    # Test coordinates in different regions
    test_points = [
        # Vancouver, BC (should find Canadian watershed)
        {"name": "Vancouver, BC", "lat": 49.2827, "lon": -123.1207},
        
        # Seattle, WA (should find US watershed) 
        {"name": "Seattle, WA", "lat": 47.6062, "lon": -122.3321},
        
        # Portland, OR (should find US watershed)
        {"name": "Portland, OR", "lat": 45.5152, "lon": -122.6784},
        
        # Victoria, BC (should find Canadian watershed or be outside region)
        {"name": "Victoria, BC", "lat": 48.4284, "lon": -123.3656},
        
        # Border area point (interesting for cross-border testing)
        {"name": "Border area", "lat": 49.0, "lon": -122.0},
    ]
    
    print("\nTesting coordinates:")
    print("-" * 30)
    
    for point in test_points:
        print(f"\n{point['name']} ({point['lat']:.4f}, {point['lon']:.4f})")
        
        result = lookup.find_watershed_by_point(point['lat'], point['lon'])
        
        if result:
            print(f"✓ Found watershed: {result.get('Watershed_Name', result.get('watershed_name', 'Unknown'))}")
            print(f"  Country: {result.get('Country', result.get('country', 'Unknown'))}")
            print(f"  Data source: {result.get('DataSource', 'Unknown')}")
            print(f"  Area: {result.get('Area_SqKm', result.get('area_sqkm', 0)):.1f} km²")
            
            # Check for hierarchical codes
            if result.get('HUC_Code'):
                print(f"  HUC12: {result['HUC_Code']}")
            if result.get('FWA_Code'):
                print(f"  FWA Code: {result['FWA_Code'][:50]}...")  # Truncate long FWA codes
            
            # Check for cross-border connectivity
            if result.get('Downstream_CASC_ID'):
                print(f"  Downstream connection: {result['Downstream_CASC_ID']}")
        else:
            print("✗ No watershed found (may be outside Cascadia region)")

def check_dataset_structure():
    """Check the structure of the integrated dataset."""
    
    print(f"\n\nDataset Structure Analysis:")
    print("=" * 40)
    
    lookup = CascadiaWatershedLookup('data/cascadia_watersheds.gpkg')
    
    if lookup.watersheds_gdf is None:
        print("Failed to load data!")
        return
    
    gdf = lookup.watersheds_gdf
    
    print(f"Total records: {len(gdf):,}")
    print(f"CRS: {gdf.crs}")
    print(f"Columns: {list(gdf.columns)}")
    
    # Check data sources
    if 'DataSource' in gdf.columns:
        print(f"\nData Sources:")
        for source, count in gdf['DataSource'].value_counts().items():
            print(f"  {source}: {count:,} watersheds")
    
    # Check countries
    if 'Country' in gdf.columns:
        print(f"\nCountries:")
        for country, count in gdf['Country'].value_counts().items():
            print(f"  {country}: {count:,} watersheds")
    
    # Check Canadian watersheds specifically
    canadian_watersheds = gdf[gdf['Country'] == 'CAN'] if 'Country' in gdf.columns else None
    if canadian_watersheds is not None and len(canadian_watersheds) > 0:
        print(f"\nCanadian Watersheds Details:")
        print(f"  Count: {len(canadian_watersheds)}")
        if 'FWA_Principal_Drainage' in canadian_watersheds.columns:
            drainage_counts = canadian_watersheds['FWA_Principal_Drainage'].value_counts()
            print(f"  Principal Drainages:")
            for drainage, count in drainage_counts.items():
                print(f"    {drainage}: {count} watersheds")
    
    # Check cross-border connections
    if 'Downstream_CASC_ID' in gdf.columns:
        connections = gdf['Downstream_CASC_ID'].notna().sum()
        print(f"\nCross-border connections: {connections}")
        
        # Show some examples
        connected = gdf[gdf['Downstream_CASC_ID'].notna()]
        if len(connected) > 0:
            print("Example connections:")
            for i, row in connected.head(3).iterrows():
                print(f"  {row.get('CASC_ID', 'Unknown')} -> {row['Downstream_CASC_ID']}")

if __name__ == '__main__':
    check_dataset_structure()
    test_coordinates()