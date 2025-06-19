"""
Unit tests for the watershed lookup functionality.
"""

import pytest
import os
import sys
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from watershed_lookup import CascadiaWatershedLookup


class TestCascadiaWatershedLookup:
    """Test cases for the CascadiaWatershedLookup class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_gdf = MagicMock()
        self.mock_gdf.crs = 'EPSG:4326'
        
    @patch('watershed_lookup.gpd.read_file')
    @patch('watershed_lookup.os.path.exists')
    def test_init_with_existing_file(self, mock_exists, mock_read_file):
        """Test initialization with existing watershed data file."""
        mock_exists.return_value = True
        mock_read_file.return_value = self.mock_gdf
        
        lookup = CascadiaWatershedLookup('test_data.gpkg')
        
        assert lookup.watersheds_gdf is not None
        mock_read_file.assert_called_once_with('test_data.gpkg')
    
    @patch('watershed_lookup.os.path.exists')
    def test_init_with_missing_file(self, mock_exists):
        """Test initialization with missing watershed data file."""
        mock_exists.return_value = False
        
        lookup = CascadiaWatershedLookup('missing_data.gpkg')
        
        assert lookup.watersheds_gdf is None
    
    @patch('watershed_lookup.requests.get')
    def test_geocode_address_success(self, mock_get):
        """Test successful geocoding of an address."""
        # Mock successful API response
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = [{
            'lat': '47.6062',
            'lon': '-122.3321'
        }]
        mock_get.return_value = mock_response
        
        lookup = CascadiaWatershedLookup()
        result = lookup.geocode_address('Seattle, WA')
        
        assert result == (47.6062, -122.3321)
    
    @patch('watershed_lookup.requests.get')
    def test_geocode_address_no_results(self, mock_get):
        """Test geocoding with no results."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = []
        mock_get.return_value = mock_response
        
        lookup = CascadiaWatershedLookup()
        result = lookup.geocode_address('Invalid Address')
        
        assert result is None
    
    @patch('watershed_lookup.requests.get')
    def test_geocode_address_api_error(self, mock_get):
        """Test geocoding with API error."""
        mock_get.side_effect = Exception('API Error')
        
        lookup = CascadiaWatershedLookup()
        result = lookup.geocode_address('Seattle, WA')
        
        assert result is None
    
    @patch('watershed_lookup.gpd.sjoin')
    @patch('watershed_lookup.gpd.GeoDataFrame')
    @patch('watershed_lookup.Point')
    def test_find_watershed_by_point_success(self, mock_point, mock_gdf_constructor, mock_sjoin):
        """Test successful watershed lookup by coordinates."""
        # Setup mocks
        lookup = CascadiaWatershedLookup()
        lookup.watersheds_gdf = self.mock_gdf
        
        mock_point_instance = Mock()
        mock_point.return_value = mock_point_instance
        
        mock_point_gdf = Mock()
        mock_gdf_constructor.return_value = mock_point_gdf
        
        mock_result_gdf = Mock()
        mock_result_gdf.empty = False
        mock_result_row = Mock()
        mock_result_row.to_dict.return_value = {
            'watershed_name': 'Test Watershed',
            'country': 'USA',
            'area_sqkm': 100.0
        }
        mock_result_gdf.iloc = [mock_result_row]
        mock_sjoin.return_value = mock_result_gdf
        
        result = lookup.find_watershed_by_point(47.6062, -122.3321)
        
        assert result is not None
        assert result['watershed_name'] == 'Test Watershed'
    
    def test_find_watershed_by_point_no_data(self):
        """Test watershed lookup with no loaded data."""
        lookup = CascadiaWatershedLookup()
        lookup.watersheds_gdf = None
        
        result = lookup.find_watershed_by_point(47.6062, -122.3321)
        
        assert result is None
    
    def test_extract_watershed_lineage_us(self):
        """Test watershed lineage extraction for US watersheds."""
        lookup = CascadiaWatershedLookup()
        
        watershed_data = {
            'watershed_name': 'Test Watershed',
            'country': 'USA',
            'area_sqkm': 100.0,
            'huc12_code': '171100130501'
        }
        
        lineage = lookup.extract_watershed_lineage(watershed_data)
        
        assert lineage['immediate_watershed']['name'] == 'Test Watershed'
        assert lineage['immediate_watershed']['country'] == 'USA'
        assert 'us' in lineage['hierarchy']
        assert lineage['hierarchy']['us']['huc12'] == '171100130501'
        assert lineage['hierarchy']['us']['huc10'] == '1711001305'
        assert lineage['hierarchy']['us']['huc8'] == '17110013'
    
    def test_extract_watershed_lineage_canada(self):
        """Test watershed lineage extraction for Canadian watersheds."""
        lookup = CascadiaWatershedLookup()
        
        watershed_data = {
            'watershed_name': 'Test Watershed',
            'country': 'CAN',
            'area_sqkm': 100.0,
            'sdac_ssda_code': '08GA'
        }
        
        lineage = lookup.extract_watershed_lineage(watershed_data)
        
        assert lineage['immediate_watershed']['name'] == 'Test Watershed'
        assert lineage['immediate_watershed']['country'] == 'CAN'
        assert 'canada' in lineage['hierarchy']
        assert lineage['hierarchy']['canada']['ssda'] == '08GA'
        assert lineage['hierarchy']['canada']['sda'] == '08G'
        assert lineage['hierarchy']['canada']['mda'] == '08'
    
    @patch.object(CascadiaWatershedLookup, 'geocode_address')
    @patch.object(CascadiaWatershedLookup, 'find_watershed_by_point')
    @patch.object(CascadiaWatershedLookup, 'extract_watershed_lineage')
    def test_lookup_watershed_success(self, mock_extract, mock_find, mock_geocode):
        """Test complete watershed lookup workflow."""
        # Setup mocks
        mock_geocode.return_value = (47.6062, -122.3321)
        mock_find.return_value = {
            'watershed_name': 'Test Watershed',
            'country': 'USA',
            'area_sqkm': 100.0
        }
        mock_extract.return_value = {
            'immediate_watershed': {
                'name': 'Test Watershed',
                'country': 'USA',
                'area_sqkm': 100.0
            },
            'hierarchy': {}
        }
        
        lookup = CascadiaWatershedLookup()
        result = lookup.lookup_watershed('Seattle, WA')
        
        assert result is not None
        assert result['input_address'] == 'Seattle, WA'
        assert result['coordinates']['latitude'] == 47.6062
        assert result['coordinates']['longitude'] == -122.3321
        assert 'watershed_info' in result
        assert 'raw_data' in result
    
    @patch.object(CascadiaWatershedLookup, 'geocode_address')
    def test_lookup_watershed_geocoding_failure(self, mock_geocode):
        """Test watershed lookup with geocoding failure."""
        mock_geocode.return_value = None
        
        lookup = CascadiaWatershedLookup()
        result = lookup.lookup_watershed('Invalid Address')
        
        assert result is None


if __name__ == '__main__':
    pytest.main([__file__])