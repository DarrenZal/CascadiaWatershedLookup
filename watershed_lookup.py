"""
Cascadia Watershed Lookup Service

This module implements a cross-border watershed identification service for the 
Cascadia bioregion. It accepts full street addresses from both the US and 
Canada and returns detailed hierarchical watershed information.

Based on the technical blueprint from research.md, this follows an offline-first 
architecture using a pre-processed, unified geospatial dataset.
"""

import geopandas as gpd
import requests
from shapely.geometry import Point
from typing import Dict, Optional, Tuple
import os


class CascadiaWatershedLookup:
    """
    Main class for watershed identification in the Cascadia bioregion.
    
    Uses offline-first architecture with pre-processed unified dataset
    covering both US (WBD/HUC) and Canadian (SDAC/CHN) watershed systems.
    """
    
    def __init__(self, watershed_data_path: str = "cascadia_watersheds.gpkg"):
        """
        Initialize the watershed lookup service.
        
        Args:
            watershed_data_path: Path to the unified Cascadia watershed dataset
        """
        self.watershed_data_path = watershed_data_path
        self.watersheds_gdf = None
        self._load_watershed_data()
    
    def _load_watershed_data(self):
        """Load the unified watershed dataset into memory."""
        try:
            if os.path.exists(self.watershed_data_path):
                self.watersheds_gdf = gpd.read_file(self.watershed_data_path)
                print(f"Loaded {len(self.watersheds_gdf)} watershed polygons")
            else:
                print(f"Warning: Watershed data file not found: {self.watershed_data_path}")
                print("You'll need to create the unified dataset following the research.md blueprint")
                self.watersheds_gdf = None
        except Exception as e:
            print(f"Error loading watershed data: {e}")
            self.watersheds_gdf = None
    
    def geocode_address(self, street_address: str, api_key: Optional[str] = None) -> Optional[Tuple[float, float]]:
        """
        Convert full street address to latitude/longitude coordinates.
        
        Uses geocode.maps.co API (generous free tier) as recommended in research.md.
        Requires full street address to get precise location, avoiding issues
        where postal codes might cross watershed boundaries.
        
        Args:
            street_address: Full street address (e.g., "123 Main St, Seattle, WA")
            api_key: Optional API key for higher rate limits
            
        Returns:
            Tuple of (latitude, longitude) or None if geocoding fails
        """
        base_url = "https://geocode.maps.co/search"
        
        params = {
            "q": street_address,
            "format": "json",
            "limit": 1
        }
        
        if api_key:
            params["api_key"] = api_key
        
        try:
            response = requests.get(base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if data and len(data) > 0:
                lat = float(data[0]["lat"])
                lon = float(data[0]["lon"])
                return (lat, lon)
            else:
                print(f"No geocoding results found for: {street_address}")
                return None
                
        except requests.RequestException as e:
            print(f"Geocoding API error: {e}")
            return None
        except (KeyError, ValueError, IndexError) as e:
            print(f"Error parsing geocoding response: {e}")
            return None
    
    def find_watershed_by_point(self, lat: float, lon: float) -> Optional[Dict]:
        """
        Find watershed containing the given coordinates using spatial join.
        
        Implements the core point-in-polygon query using GeoPandas sjoin
        with spatial indexing for performance.
        
        Args:
            lat: Latitude coordinate
            lon: Longitude coordinate
            
        Returns:
            Dictionary containing watershed information or None if not found
        """
        if self.watersheds_gdf is None:
            print("Error: Watershed data not loaded")
            return None
        
        try:
            # Create point geometry
            point_geom = Point(lon, lat)
            
            # Create single-row GeoDataFrame with same CRS as watershed data
            point_gdf = gpd.GeoDataFrame(
                [{"id": 1}], 
                geometry=[point_geom], 
                crs=self.watersheds_gdf.crs
            )
            
            # Perform spatial join (point-in-polygon)
            # Uses spatial index for performance optimization
            result_gdf = gpd.sjoin(
                point_gdf, 
                self.watersheds_gdf, 
                how="inner", 
                predicate="within"
            )
            
            if not result_gdf.empty:
                # Return the first (and should be only) match as dictionary
                watershed_row = result_gdf.iloc[0]
                return watershed_row.to_dict()
            else:
                print(f"No watershed found for coordinates ({lat}, {lon}) within Cascadia")
                return None
                
        except Exception as e:
            print(f"Error during spatial join: {e}")
            return None
    
    def extract_watershed_lineage(self, watershed_data: Dict) -> Dict:
        """
        Extract hierarchical watershed lineage from codes.
        
        Derives parent watershed codes from hierarchical coding systems:
        - US: HUC12 -> HUC10 -> HUC8 -> HUC6 -> HUC4 -> HUC2
        - Canada: SDAC SSDA -> SDA -> MDA
        
        Args:
            watershed_data: Dictionary containing watershed information
            
        Returns:
            Dictionary with hierarchical lineage information
        """
        lineage = {
            "immediate_watershed": {
                "name": watershed_data.get("watershed_name", "Unknown"),
                "country": watershed_data.get("country", "Unknown"),
                "area_sqkm": watershed_data.get("area_sqkm", 0)
            },
            "hierarchy": {}
        }
        
        # US Watershed Hierarchy (HUC system)
        if watershed_data.get("country") == "USA" and watershed_data.get("huc12_code"):
            huc12 = watershed_data["huc12_code"]
            lineage["hierarchy"]["us"] = {
                "huc12": huc12,
                "huc10": huc12[:10] if len(huc12) >= 10 else None,
                "huc8": huc12[:8] if len(huc12) >= 8 else None,
                "huc6": huc12[:6] if len(huc12) >= 6 else None,
                "huc4": huc12[:4] if len(huc12) >= 4 else None,
                "huc2": huc12[:2] if len(huc12) >= 2 else None
            }
        
        # Canadian Watershed Hierarchy (SDAC system)
        elif watershed_data.get("country") == "CAN" and watershed_data.get("sdac_ssda_code"):
            sdac_ssda = watershed_data["sdac_ssda_code"]
            lineage["hierarchy"]["canada"] = {
                "ssda": sdac_ssda,
                "sda": sdac_ssda[:3] if len(sdac_ssda) >= 3 else None,
                "mda": sdac_ssda[:2] if len(sdac_ssda) >= 2 else None
            }
        
        return lineage
    
    def lookup_watershed(self, street_address: str, api_key: Optional[str] = None) -> Optional[Dict]:
        """
        Main function to lookup watershed information for a full street address.
        
        This is the primary interface that combines geocoding and spatial lookup
        to return complete watershed information including hierarchical lineage.
        Requires full street address for precise location to avoid issues where
        postal codes might cross watershed boundaries.
        
        Args:
            street_address: Full street address (e.g., "123 Main St, Seattle, WA")
            api_key: Optional geocoding API key
            
        Returns:
            Dictionary containing complete watershed information or None if not found
        """
        # Step 1: Geocode the address to get coordinates
        coordinates = self.geocode_address(street_address, api_key)
        if not coordinates:
            return None
        
        lat, lon = coordinates
        print(f"Geocoded '{street_address}' to ({lat}, {lon})")
        
        # Step 2: Find watershed containing the point
        watershed_data = self.find_watershed_by_point(lat, lon)
        if not watershed_data:
            return None
        
        # Step 3: Extract hierarchical lineage
        lineage = self.extract_watershed_lineage(watershed_data)
        
        # Step 4: Compile complete result
        result = {
            "input_address": street_address,
            "coordinates": {"latitude": lat, "longitude": lon},
            "watershed_info": lineage,
            "raw_data": watershed_data
        }
        
        return result


def main():
    """
    Example usage of the CascadiaWatershedLookup service.
    
    Demonstrates how to lookup watershed information for various full street
    addresses across the Cascadia bioregion.
    """
    # Initialize the service
    lookup = CascadiaWatershedLookup()
    
    # Test full street addresses from different parts of Cascadia
    test_addresses = [
        "1600 Amphitheatre Parkway, Mountain View, CA",
        "123 Main Street, Seattle, WA",
        "456 Oak Avenue, Portland, OR", 
        "789 Maple Drive, Vancouver, BC",
        "321 Pine Street, Bellingham, WA"
    ]
    
    for address in test_addresses:
        print(f"\n{'='*50}")
        print(f"Looking up watershed for: {address}")
        print('='*50)
        
        result = lookup.lookup_watershed(address)
        
        if result:
            print(f"✓ Found watershed information:")
            print(f"  Coordinates: {result['coordinates']}")
            print(f"  Watershed: {result['watershed_info']['immediate_watershed']['name']}")
            print(f"  Country: {result['watershed_info']['immediate_watershed']['country']}")
            print(f"  Area: {result['watershed_info']['immediate_watershed']['area_sqkm']} km²")
            
            if 'us' in result['watershed_info']['hierarchy']:
                huc_info = result['watershed_info']['hierarchy']['us']
                print(f"  HUC Codes: HUC12={huc_info['huc12']}, HUC8={huc_info['huc8']}")
            
            if 'canada' in result['watershed_info']['hierarchy']:
                sdac_info = result['watershed_info']['hierarchy']['canada']
                print(f"  SDAC Codes: SSDA={sdac_info['ssda']}, MDA={sdac_info['mda']}")
        else:
            print("✗ No watershed information found")


if __name__ == "__main__":
    main()