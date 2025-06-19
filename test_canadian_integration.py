#!/usr/bin/env python3
"""
Test script to verify Canadian watershed lookup functionality.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from watershed_lookup import CascadiaWatershedLookup

def test_canadian_watersheds():
    """Test Canadian watershed lookup functionality."""
    
    print("Testing Canadian Watershed Lookup Integration")
    print("=" * 50)
    
    # Initialize the service
    lookup = CascadiaWatershedLookup()
    
    # Test Canadian addresses
    canadian_test_addresses = [
        "1055 Dunsmuir Street, Vancouver, BC",
        "1 Wellington Street, Ottawa, ON",
        "789 Fort Street, Victoria, BC",
        "100 Queen Street West, Toronto, ON",
        "999 Canada Place, Vancouver, BC"
    ]
    
    # Test US addresses for comparison
    us_test_addresses = [
        "1600 Amphitheatre Parkway, Mountain View, CA",
        "123 Main Street, Seattle, WA",
        "456 Pine Street, Portland, OR"
    ]
    
    print("\nTesting Canadian addresses:")
    print("-" * 30)
    
    for address in canadian_test_addresses:
        print(f"\nTesting: {address}")
        result = lookup.lookup_watershed(address)
        
        if result:
            watershed_info = result['watershed_info']['immediate_watershed']
            print(f"✓ Found watershed: {watershed_info['name']}")
            print(f"  Country: {watershed_info['country']}")
            print(f"  Area: {watershed_info['area_sqkm']:.1f} km²")
            
            # Check for Canadian-specific hierarchy
            if 'canada' in result['watershed_info']['hierarchy']:
                can_info = result['watershed_info']['hierarchy']['canada']
                print(f"  Canadian hierarchy found")
            elif 'us' in result['watershed_info']['hierarchy']:
                us_info = result['watershed_info']['hierarchy']['us']
                print(f"  US HUC codes: {us_info.get('huc8', 'N/A')}")
            
            raw_data = result.get('raw_data', {})
            if raw_data.get('DataSource'):
                print(f"  Data source: {raw_data['DataSource']}")
        else:
            print("✗ No watershed found")
    
    print(f"\n\nTesting US addresses for comparison:")
    print("-" * 40)
    
    for address in us_test_addresses:
        print(f"\nTesting: {address}")
        result = lookup.lookup_watershed(address)
        
        if result:
            watershed_info = result['watershed_info']['immediate_watershed']
            print(f"✓ Found watershed: {watershed_info['name']}")
            print(f"  Country: {watershed_info['country']}")
            print(f"  Area: {watershed_info['area_sqkm']:.1f} km²")
            
            raw_data = result.get('raw_data', {})
            if raw_data.get('DataSource'):
                print(f"  Data source: {raw_data['DataSource']}")
        else:
            print("✗ No watershed found")

def test_dataset_summary():
    """Test the unified dataset structure."""
    
    print(f"\n\nDataset Summary:")
    print("=" * 30)
    
    lookup = CascadiaWatershedLookup()
    
    if lookup.watersheds_gdf is not None:
        gdf = lookup.watersheds_gdf
        
        print(f"Total watersheds: {len(gdf):,}")
        print(f"Dataset CRS: {gdf.crs}")
        print(f"Columns: {list(gdf.columns)}")
        
        # Summary by data source
        if 'DataSource' in gdf.columns:
            source_counts = gdf['DataSource'].value_counts()
            print(f"\nBy Data Source:")
            for source, count in source_counts.items():
                print(f"  {source}: {count:,} watersheds")
        
        # Summary by country
        if 'Country' in gdf.columns:
            country_counts = gdf['Country'].value_counts()
            print(f"\nBy Country:")
            for country, count in country_counts.items():
                print(f"  {country}: {count:,} watersheds")
        
        # Check for cross-border connections
        if 'Downstream_CASC_ID' in gdf.columns:
            connections = gdf['Downstream_CASC_ID'].notna().sum()
            print(f"\nCross-border connections: {connections}")
    
    else:
        print("No watershed data loaded!")

if __name__ == '__main__':
    test_dataset_summary()
    test_canadian_watersheds()