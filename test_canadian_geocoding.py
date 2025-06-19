#!/usr/bin/env python3
"""
Test Canadian geocoding and watershed lookup.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from watershed_lookup import CascadiaWatershedLookup

def test_canadian_geocoding():
    """Test geocoding for various Canadian addresses."""
    
    print("🍁 Testing Canadian Address Geocoding")
    print("=" * 50)
    
    lookup = CascadiaWatershedLookup('data/cascadia_watersheds.gpkg')
    
    canadian_addresses = [
        "1620 Belmont Ave, Victoria, BC, Canada",
        "789 West Pender Street, Vancouver, BC, Canada", 
        "100 Queen Street West, Toronto, ON, Canada",
        "1055 Dunsmuir Street, Vancouver, BC, Canada",
        "Parliament Hill, Ottawa, ON, Canada"
    ]
    
    print(f"Testing {len(canadian_addresses)} Canadian addresses...\n")
    
    for i, address in enumerate(canadian_addresses, 1):
        print(f"{i}. Testing: {address}")
        
        # Test geocoding
        coordinates = lookup.geocode_address(address)
        
        if coordinates:
            lat, lon = coordinates
            print(f"   ✅ Geocoded to: {lat:.6f}, {lon:.6f}")
            
            # Check if it's in BC (Cascadia region)
            if -130 <= lon <= -114 and 48 <= lat <= 55:
                print(f"   🌲 Location is within BC/Cascadia region")
                
                # Test watershed lookup
                result = lookup.find_watershed_by_point(lat, lon)
                if result:
                    country = result.get('country', 'Unknown')
                    name = result.get('watershed_name', 'Unnamed')
                    source = result.get('datasource', 'Unknown')
                    
                    if country == 'CAN':
                        print(f"   🇨🇦 Found Canadian watershed: {name}")
                        print(f"      Data source: {source}")
                    else:
                        print(f"   🇺🇸 Found US watershed: {name}")
                        print(f"      Note: Location may be covered by US data or outside sample CA data")
                else:
                    print(f"   ❌ No watershed found (outside Cascadia region)")
            else:
                print(f"   ℹ️  Location outside BC/Cascadia region")
                
        else:
            print(f"   ❌ Geocoding failed")
        
        print()  # Empty line for readability

def show_canadian_coverage():
    """Show current Canadian watershed coverage."""
    
    print("🗺️  Current Canadian Watershed Coverage")
    print("=" * 50)
    
    lookup = CascadiaWatershedLookup('data/cascadia_watersheds.gpkg')
    
    if lookup.watersheds_gdf is not None:
        gdf = lookup.watersheds_gdf
        can_watersheds = gdf[gdf['country'] == 'CAN']
        
        print(f"Canadian watersheds in dataset: {len(can_watersheds)}")
        
        if len(can_watersheds) > 0:
            print("\nCanadian watershed coverage:")
            bounds = can_watersheds.bounds
            print(f"  Longitude: {bounds['minx'].min():.3f}° to {bounds['maxx'].max():.3f}°")
            print(f"  Latitude: {bounds['miny'].min():.3f}° to {bounds['maxy'].max():.3f}°")
            
            print(f"\nCanadian watersheds by drainage system:")
            if 'fwa_principal_drainage' in can_watersheds.columns:
                drainage_counts = can_watersheds['fwa_principal_drainage'].value_counts()
                drainage_names = {
                    '100': 'Fraser River',
                    '300': 'Columbia River', 
                    '900': 'South Coast Rivers',
                    '920': 'Vancouver Island East'
                }
                
                for drainage, count in drainage_counts.items():
                    name = drainage_names.get(str(drainage), f"Drainage {drainage}")
                    print(f"  {name}: {count} watersheds")
        
        print(f"\n📍 Victoria, BC Location Analysis:")
        print(f"  Victoria coordinates: ~48.428°N, -123.339°W")
        print(f"  Expected drainage: Vancouver Island East (920)")
        print(f"  Current coverage: Sample data may not include Victoria area")
        
        print(f"\n💡 To improve Canadian coverage:")
        print(f"  1. Download full BC FWA Assessment Watersheds (19,469 total)")
        print(f"  2. Include Vancouver Island watersheds specifically")
        print(f"  3. Add coastal and island watershed coverage")

if __name__ == '__main__':
    test_canadian_geocoding()
    print()
    show_canadian_coverage()