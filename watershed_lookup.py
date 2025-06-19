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
from typing import Dict, Optional, Tuple, List
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
    
    def validate_and_suggest_address(self, street_address: str, api_key: Optional[str] = None) -> Dict:
        """
        Validate an address and suggest corrections if needed.
        
        Args:
            street_address: Address to validate
            api_key: Optional geocoding API key
            
        Returns:
            Dictionary with validation results and suggestions
        """
        # Normalize the address
        normalized_address = self._normalize_address(street_address)
        
        # Try to geocode the original address
        result = {
            "original_address": street_address,
            "normalized_address": normalized_address,
            "is_valid": False,
            "coordinates": None,
            "suggestions": []
        }
        
        # Test geocoding with multiple address variations
        address_variations = [
            normalized_address,
            street_address,
            self._simplify_address(normalized_address),
            self._add_country_if_missing(normalized_address)
        ]
        
        for variation in address_variations:
            if not variation or variation in [addr for addr in address_variations[:address_variations.index(variation)]]:
                continue  # Skip duplicates
                
            coords = self._try_geocode_variation(variation, api_key)
            if coords:
                result["is_valid"] = True
                result["coordinates"] = coords
                result["validated_address"] = variation
                break
        
        # If no exact match, try to find similar addresses
        if not result["is_valid"]:
            suggestions = self._find_address_suggestions(normalized_address, api_key)
            result["suggestions"] = suggestions
            
        return result
    
    def _normalize_address(self, address: str) -> str:
        """Normalize address format for better geocoding success."""
        if not address:
            return ""
            
        # Remove extra whitespace
        normalized = " ".join(address.split())
        
        # Standardize common abbreviations
        abbreviations = {
            r'\bStreet\b': 'St',
            r'\bAvenue\b': 'Ave', 
            r'\bBoulevard\b': 'Blvd',
            r'\bRoad\b': 'Rd',
            r'\bDrive\b': 'Dr',
            r'\bLane\b': 'Ln',
            r'\bCourt\b': 'Ct',
            r'\bPlace\b': 'Pl',
            r'\bBritish Columbia\b': 'BC',
            r'\bWashington\b': 'WA',
            r'\bOregon\b': 'OR',
            r'\bCalifornia\b': 'CA',
            r'\bAlaska\b': 'AK',
            r'\bIdaho\b': 'ID'
        }
        
        import re
        for full_form, abbrev in abbreviations.items():
            normalized = re.sub(full_form, abbrev, normalized, flags=re.IGNORECASE)
            
        return normalized
    
    def _simplify_address(self, address: str) -> str:
        """Create a simplified version of the address for geocoding."""
        if not address:
            return ""
            
        # Remove apartment/unit numbers and extra details
        import re
        
        # Remove apartment/unit indicators
        patterns_to_remove = [
            r',\s*#?\d+[A-Za-z]?\s*,',  # , #123, or , 123A,
            r',\s*[Aa]pt\.?\s*\d+[A-Za-z]?\s*,',  # , Apt 123,
            r',\s*[Uu]nit\s*\d+[A-Za-z]?\s*,',  # , Unit 123,
            r'\s+#?\d+[A-Za-z]?\s*,',  # 123 Main St #5, -> 123 Main St,
        ]
        
        simplified = address
        for pattern in patterns_to_remove:
            simplified = re.sub(pattern, ',', simplified)
            
        # Clean up any double commas
        simplified = re.sub(r',\s*,', ',', simplified)
        
        return simplified.strip()
    
    def _add_country_if_missing(self, address: str) -> str:
        """Add country if it appears to be missing."""
        if not address:
            return ""
            
        # Check if address already has a country
        countries = ['Canada', 'United States', 'USA', 'US']
        for country in countries:
            if country.lower() in address.lower():
                return address
                
        # Detect likely country based on province/state
        if any(prov in address.upper() for prov in ['BC', 'AB', 'SK', 'MB', 'ON', 'QC', 'BRITISH COLUMBIA', 'ALBERTA']):
            return f"{address}, Canada"
        elif any(state in address.upper() for state in ['WA', 'OR', 'CA', 'AK', 'ID', 'WASHINGTON', 'OREGON', 'CALIFORNIA']):
            return f"{address}, USA"
            
        return address
    
    def _try_geocode_variation(self, address: str, api_key: Optional[str] = None) -> Optional[Tuple[float, float]]:
        """Try geocoding a specific address variation."""
        try:
            return self.geocode_address(address, api_key)
        except Exception:
            return None
    
    def _find_address_suggestions(self, address: str, api_key: Optional[str] = None, max_suggestions: int = 3) -> List[Dict]:
        """Find similar addresses that can be geocoded."""
        suggestions = []
        
        # Try Google Places autocomplete first (best results)
        if api_key:
            google_suggestions = self._get_google_places_suggestions(address, api_key, max_suggestions)
            suggestions.extend(google_suggestions)
        
        # If we still need more suggestions, try other methods
        if len(suggestions) < max_suggestions:
            variations = [
                self._remove_street_number(address),
                self._extract_city_state(address),
                self._try_phonetic_corrections(address)
            ]
            
            for variation in variations:
                if not variation or len(suggestions) >= max_suggestions:
                    break
                    
                coords = self._try_geocode_variation(variation, api_key)
                if coords:
                    suggestions.append({
                        "suggested_address": variation,
                        "coordinates": coords,
                        "confidence": "medium"
                    })
        
        return suggestions[:max_suggestions]
    
    def _remove_street_number(self, address: str) -> str:
        """Remove street number to find the street."""
        import re
        # Remove leading numbers
        no_number = re.sub(r'^(\d+[A-Za-z]?\s+)', '', address)
        return no_number if no_number != address else ""
    
    def _extract_city_state(self, address: str) -> str:
        """Extract just city, state/province, country."""
        parts = address.split(',')
        if len(parts) >= 2:
            # Take the last 2-3 parts (city, state/province, country)
            return ', '.join(parts[-3:]).strip() if len(parts) >= 3 else ', '.join(parts[-2:]).strip()
        return ""
    
    def _try_phonetic_corrections(self, address: str) -> str:
        """Try common phonetic corrections."""
        # This is a simplified version - in production you might use a phonetic matching library
        common_corrections = {
            'Viktor': 'Victoria',
            'Viktoria': 'Victoria', 
            'Vancuver': 'Vancouver',
            'Seatle': 'Seattle',
            'Seatel': 'Seattle'
        }
        
        corrected = address
        for wrong, correct in common_corrections.items():
            corrected = corrected.replace(wrong, correct)
            
        return corrected if corrected != address else ""

    def geocode_address(self, street_address: str, api_key: Optional[str] = None) -> Optional[Tuple[float, float]]:
        """
        Convert full street address to latitude/longitude coordinates.
        
        Uses multiple geocoding services with fallback for better Canadian coverage.
        
        Args:
            street_address: Full street address (e.g., "123 Main St, Seattle, WA")
            api_key: Optional API key for higher rate limits
            
        Returns:
            Tuple of (latitude, longitude) or None if geocoding fails
        """
        
        # Try multiple geocoding services for better coverage (Google Maps first)
        geocoding_services = [
            self._geocode_google_maps,
            self._geocode_nominatim,
            self._geocode_maps_co,
        ]
        
        for service in geocoding_services:
            try:
                result = service(street_address, api_key)
                if result:
                    return result
            except Exception as e:
                print(f"Geocoding service failed: {e}")
                continue
        
        print(f"All geocoding services failed for: {street_address}")
        return None
    
    def _geocode_google_maps(self, street_address: str, api_key: Optional[str] = None) -> Optional[Tuple[float, float]]:
        """
        Geocode using Google Maps Geocoding API (best accuracy, requires API key).
        """
        if not api_key:
            print("Google Maps geocoding skipped: No API key provided")
            return None
            
        base_url = "https://maps.googleapis.com/maps/api/geocode/json"
        
        params = {
            "address": street_address,
            "key": api_key,
            "region": "ca"  # Prefer Canadian results for ambiguous queries
        }
        
        try:
            response = requests.get(base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data["status"] == "OK" and data["results"]:
                location = data["results"][0]["geometry"]["location"]
                lat = location["lat"]
                lon = location["lng"]
                formatted_address = data["results"][0]["formatted_address"]
                print(f"Google Maps geocoded '{street_address}' to ({lat:.6f}, {lon:.6f}) - {formatted_address}")
                return (lat, lon)
            elif data["status"] == "ZERO_RESULTS":
                print(f"Google Maps: No results found for: {street_address}")
                return None
            else:
                print(f"Google Maps geocoding error: {data.get('status', 'Unknown error')}")
                return None
                
        except requests.RequestException as e:
            print(f"Google Maps geocoding request error: {e}")
            return None
        except (KeyError, ValueError) as e:
            print(f"Google Maps geocoding response parsing error: {e}")
            return None
    
    def _get_google_places_suggestions(self, address: str, api_key: str, max_suggestions: int = 3) -> List[Dict]:
        """
        Get address suggestions using Google Places Autocomplete API.
        """
        suggestions = []
        
        # Use Place Autocomplete to find similar addresses
        base_url = "https://maps.googleapis.com/maps/api/place/autocomplete/json"
        
        params = {
            "input": address,
            "key": api_key,
            "types": "address",
            "components": "country:ca|country:us",  # Restrict to North America
        }
        
        try:
            response = requests.get(base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data["status"] == "OK" and data.get("predictions"):
                for prediction in data["predictions"][:max_suggestions]:
                    description = prediction["description"]
                    place_id = prediction["place_id"]
                    
                    # Get coordinates for this place
                    coords = self._get_place_coordinates(place_id, api_key)
                    if coords:
                        suggestions.append({
                            "suggested_address": description,
                            "coordinates": coords,
                            "confidence": "high",
                            "place_id": place_id
                        })
            else:
                print(f"Google Places autocomplete: {data.get('status', 'No results')}")
                
        except requests.RequestException as e:
            print(f"Google Places autocomplete request error: {e}")
        except (KeyError, ValueError) as e:
            print(f"Google Places autocomplete response parsing error: {e}")
        
        return suggestions
    
    def _get_place_coordinates(self, place_id: str, api_key: str) -> Optional[Tuple[float, float]]:
        """
        Get coordinates for a Google Places place ID.
        """
        base_url = "https://maps.googleapis.com/maps/api/place/details/json"
        
        params = {
            "place_id": place_id,
            "key": api_key,
            "fields": "geometry"
        }
        
        try:
            response = requests.get(base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data["status"] == "OK" and data.get("result"):
                location = data["result"]["geometry"]["location"]
                return (location["lat"], location["lng"])
            else:
                print(f"Google Places details error: {data.get('status', 'Unknown')}")
                return None
                
        except requests.RequestException as e:
            print(f"Google Places details request error: {e}")
            return None
        except (KeyError, ValueError) as e:
            print(f"Google Places details response parsing error: {e}")
            return None
    
    def _geocode_nominatim(self, street_address: str, api_key: Optional[str] = None) -> Optional[Tuple[float, float]]:
        """
        Geocode using OpenStreetMap Nominatim (free, good Canadian coverage).
        """
        base_url = "https://nominatim.openstreetmap.org/search"
        
        params = {
            "q": street_address,
            "format": "json",
            "limit": 1,
            "addressdetails": 1
        }
        
        headers = {
            "User-Agent": "CascadiaWatershedLookup/1.0 (watershed-lookup-service)"
        }
        
        try:
            response = requests.get(base_url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if data and len(data) > 0:
                lat = float(data[0]["lat"])
                lon = float(data[0]["lon"])
                print(f"Nominatim geocoded '{street_address}' to ({lat:.6f}, {lon:.6f})")
                return (lat, lon)
            else:
                print(f"Nominatim: No results found for: {street_address}")
                return None
                
        except requests.RequestException as e:
            print(f"Nominatim geocoding error: {e}")
            return None
        except (KeyError, ValueError, IndexError) as e:
            print(f"Nominatim parsing error: {e}")
            return None
    
    def _geocode_maps_co(self, street_address: str, api_key: Optional[str] = None) -> Optional[Tuple[float, float]]:
        """
        Geocode using geocode.maps.co (original service).
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
                print(f"Maps.co geocoded '{street_address}' to ({lat:.6f}, {lon:.6f})")
                return (lat, lon)
            else:
                print(f"Maps.co: No results found for: {street_address}")
                return None
                
        except requests.RequestException as e:
            print(f"Maps.co geocoding error: {e}")
            return None
        except (KeyError, ValueError, IndexError) as e:
            print(f"Maps.co parsing error: {e}")
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
                # Handle multiple matches (overlapping watersheds)
                if len(result_gdf) > 1:
                    # Prefer Canadian watersheds when there are overlaps
                    canadian_matches = result_gdf[result_gdf['country'] == 'CAN']
                    if not canadian_matches.empty:
                        watershed_row = canadian_matches.iloc[0]
                    else:
                        # If no Canadian matches, take the first one
                        watershed_row = result_gdf.iloc[0]
                else:
                    # Single match - use it
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
        - Canada: FWA watershed codes and principal drainages
        
        Args:
            watershed_data: Dictionary containing watershed information
            
        Returns:
            Dictionary with hierarchical lineage information
        """
        # Generate watershed name from multiple possible fields
        watershed_name = (
            watershed_data.get("watershed_name", "").strip() or
            watershed_data.get("Watershed_Name", "").strip() or
            ""
        )
        
        if not watershed_name:
            # Use unique_id or casc_id as fallback name
            unique_id = (
                watershed_data.get("unique_id", "") or
                watershed_data.get("casc_id", "") or
                watershed_data.get("CASC_ID", "")
            )
            if unique_id:
                watershed_name = f"Watershed {unique_id}"
            else:
                watershed_name = "Unnamed Watershed"
        
        # Get country from multiple possible fields
        country = (
            watershed_data.get("country", "") or
            watershed_data.get("Country", "") or
            "Unknown"
        )
        
        # Get area from multiple possible fields
        area_sqkm = (
            watershed_data.get("area_sqkm", 0) or
            watershed_data.get("Area_SqKm", 0) or
            0
        )
        
        lineage = {
            "immediate_watershed": {
                "name": watershed_name,
                "country": country,
                "area_sqkm": area_sqkm
            },
            "hierarchy": {}
        }
        
        # US Watershed Hierarchy (HUC system)
        if country in ["USA", "United States"]:
            huc12 = watershed_data.get("huc12_code") or watershed_data.get("HUC12")
            if huc12:
                lineage["hierarchy"]["us"] = {
                    "huc12": huc12,
                    "huc10": huc12[:10] if len(str(huc12)) >= 10 else None,
                    "huc8": huc12[:8] if len(str(huc12)) >= 8 else None,
                    "huc6": huc12[:6] if len(str(huc12)) >= 6 else None,
                    "huc4": huc12[:4] if len(str(huc12)) >= 4 else None,
                    "huc2": huc12[:2] if len(str(huc12)) >= 2 else None
                }
        
        # Canadian Watershed Hierarchy (FWA system)
        elif country == "CAN":
            # Check for FWA codes
            fwa_code = (
                watershed_data.get("fwa_watershed_code") or
                watershed_data.get("FWA_Watershed_Code") or
                watershed_data.get("FWA_Code")
            )
            
            fwa_principal = (
                watershed_data.get("fwa_principal_drainage") or
                watershed_data.get("FWA_Principal_Drainage")
            )
            
            fwa_assessment_id = (
                watershed_data.get("fwa_assessment_id") or
                watershed_data.get("FWA_Assessment_ID")
            )
            
            if fwa_code or fwa_principal or fwa_assessment_id:
                lineage["hierarchy"]["canada"] = {
                    "fwa_watershed_code": fwa_code,
                    "fwa_principal_drainage": fwa_principal,
                    "fwa_assessment_id": fwa_assessment_id,
                    "principal_drainage_name": self._get_principal_drainage_name(fwa_principal)
                }
            
            # Legacy SDAC system support
            sdac_ssda = watershed_data.get("sdac_ssda_code")
            if sdac_ssda:
                if "canada" not in lineage["hierarchy"]:
                    lineage["hierarchy"]["canada"] = {}
                lineage["hierarchy"]["canada"].update({
                    "sdac_ssda": sdac_ssda,
                    "sdac_sda": sdac_ssda[:3] if len(str(sdac_ssda)) >= 3 else None,
                    "sdac_mda": sdac_ssda[:2] if len(str(sdac_ssda)) >= 2 else None
                })
        
        return lineage
    
    def _get_principal_drainage_name(self, principal_code):
        """Get the name of the principal drainage from the code."""
        drainage_names = {
            '100': 'Fraser River',
            '200': 'Mackenzie River', 
            '300': 'Columbia River',
            '400': 'Skeena River',
            '500': 'Nass River',
            '600': 'Stikine River',
            '700': 'Taku River',
            '800': 'Yukon River',
            '900': 'South Coast Rivers',
            '920': 'Vancouver Island East'
        }
        return drainage_names.get(str(principal_code), f"Drainage {principal_code}" if principal_code else None)
    
    def parse_address_input(self, address_input: str) -> str:
        """
        Parse address input that could be single-line or multi-line format.
        
        Args:
            address_input: Raw address input (single or multi-line)
            
        Returns:
            Properly formatted single-line address
        """
        if not address_input:
            return ""
        
        # If it's already a single line, just clean it up
        if '\n' not in address_input:
            return " ".join(address_input.split())
        
        # Parse multi-line address
        lines = [line.strip() for line in address_input.split('\n') if line.strip()]
        
        # Combine lines with commas, handling common patterns
        if len(lines) == 1:
            return lines[0]
        elif len(lines) == 2:
            # Typical: Street Address / City, State ZIP
            return f"{lines[0]}, {lines[1]}"
        elif len(lines) == 3:
            # Typical: Street Address / City, State / ZIP or Country
            return f"{lines[0]}, {lines[1]}, {lines[2]}"
        elif len(lines) == 4:
            # Typical: Street Address / City / State/Province / ZIP/Country
            return f"{lines[0]}, {lines[1]}, {lines[2]}, {lines[3]}"
        else:
            # Just join all lines with commas
            return ", ".join(lines)

    def lookup_watershed_with_validation(self, address_input: str, api_key: Optional[str] = None) -> Dict:
        """
        Main function to lookup watershed information with address validation and suggestions.
        
        Supports both single-line and multi-line address input formats.
        Includes address validation and provides suggestions for invalid addresses.
        
        Args:
            address_input: Address input (single or multi-line format)
            api_key: Optional geocoding API key
            
        Returns:
            Dictionary containing watershed information, validation results, and suggestions
        """
        # Parse the address input (handle single/multi-line)
        parsed_address = self.parse_address_input(address_input)
        
        # Validate the address and get suggestions
        validation_result = self.validate_and_suggest_address(parsed_address, api_key)
        
        # Prepare response structure
        response = {
            "input_address": address_input,
            "parsed_address": parsed_address,
            "validation": validation_result,
            "watershed_info": None,
            "success": False
        }
        
        # If address is valid, proceed with watershed lookup
        if validation_result["is_valid"]:
            coordinates = validation_result["coordinates"]
            lat, lon = coordinates
            
            # Find watershed containing the point
            watershed_data = self.find_watershed_by_point(lat, lon)
            if watershed_data:
                # Extract hierarchical lineage
                lineage = self.extract_watershed_lineage(watershed_data)
                
                # Remove geometry objects that can't be JSON serialized
                clean_watershed_data = {}
                for key, value in watershed_data.items():
                    if key != 'geometry' and not hasattr(value, 'geom_type'):
                        clean_watershed_data[key] = value
                
                response["watershed_info"] = {
                    "coordinates": {"latitude": lat, "longitude": lon},
                    "watershed_details": lineage,
                    "raw_data": clean_watershed_data
                }
                response["success"] = True
        
        return response

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
        # Remove geometry objects that can't be JSON serialized
        clean_watershed_data = {}
        for key, value in watershed_data.items():
            if key != 'geometry' and not hasattr(value, 'geom_type'):
                clean_watershed_data[key] = value
        
        result = {
            "input_address": street_address,
            "coordinates": {"latitude": lat, "longitude": lon},
            "watershed_info": lineage,
            "raw_data": clean_watershed_data
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