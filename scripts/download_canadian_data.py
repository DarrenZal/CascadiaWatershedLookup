#!/usr/bin/env python3
"""
Download Canadian hydrographic data for Cascadia Watershed Lookup project.
Based on research.md technical blueprint.
"""

import os
import sys
import requests
import zipfile
from pathlib import Path
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Canadian data URLs from research.md
CANADIAN_DATA_URLS = {
    'chn_bc': 'https://ftp.geogratis.gc.ca/pub/nrcan_rncan/vector/chn_rhc/chn_british_columbia/chn_british_columbia_gpkg.zip',
    'bc_freshwater_atlas': 'https://www.data.gov.bc.ca/dataset/3ee497c4-57d7-47f8-b030-2e0c03f8462a/resource/c2e8d084-0c7b-4e0c-8c4c-d3a8b7d6b65b/download/freshwater_atlas_watersheds.gdb.zip',
    'sdac_boundaries': 'https://ftp.geogratis.gc.ca/pub/nrcan_rncan/vector/hydro/boundaries_standard_drainage_area_classification/boundaries_standard_drainage_area_classification_gdb.zip'
}

def download_file(url, destination):
    """Download a file from URL to destination."""
    logger.info(f"Downloading {url} to {destination}")
    
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        with open(destination, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        logger.info(f"Successfully downloaded {destination}")
        return True
    except Exception as e:
        logger.error(f"Failed to download {url}: {e}")
        return False

def extract_zip(zip_path, extract_to):
    """Extract a zip file to a directory."""
    logger.info(f"Extracting {zip_path} to {extract_to}")
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        
        logger.info(f"Successfully extracted {zip_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to extract {zip_path}: {e}")
        return False

def download_cascadia_boundary():
    """Download Cascadia boundary from WWU ArcGIS Feature Service."""
    logger.info("Attempting to download Cascadia boundary from WWU...")
    
    # ArcGIS Feature Service REST endpoint
    service_url = "https://services9.arcgis.com/RHVPKKiFTONKtxq3/arcgis/rest/services/cascadia_bioregion_boundaries/FeatureServer/0/query"
    
    params = {
        'where': '1=1',  # Get all features
        'outFields': '*',  # Get all attributes
        'f': 'geojson'  # Return as GeoJSON
    }
    
    try:
        response = requests.get(service_url, params=params)
        response.raise_for_status()
        
        # Save as GeoJSON
        data_dir = Path(__file__).parent.parent / 'data' / 'raw' / 'cascadia_boundary'
        data_dir.mkdir(parents=True, exist_ok=True)
        
        boundary_file = data_dir / 'cascadia_boundary.geojson'
        with open(boundary_file, 'w') as f:
            f.write(response.text)
        
        logger.info(f"Successfully downloaded Cascadia boundary to {boundary_file}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to download Cascadia boundary: {e}")
        logger.info("Alternative: Download manually from https://www.arcgis.com/home/item.html?id=c6497941559d433da98e286fb3f63551")
        return False

def main():
    """Main function to download Canadian datasets."""
    
    # Create data directories
    data_dir = Path(__file__).parent.parent / 'data'
    raw_data_dir = data_dir / 'raw'
    canadian_data_dir = raw_data_dir / 'canadian_hydro'
    canadian_data_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info("Starting Canadian data download...")
    
    # Download Cascadia boundary first
    download_cascadia_boundary()
    
    # Download Canadian Hydrospatial Network data for BC
    logger.info("Downloading Canadian Hydrospatial Network (CHN) data for BC...")
    # Note: The actual CHN download URLs may need to be updated based on current availability
    logger.info("CHN data must be downloaded manually from:")
    logger.info("https://open.canada.ca/data/en/dataset/ae385105-e48c-4b54-bd0f-dfb7303301cb")
    
    # Download BC Freshwater Atlas (priority data source per research.md)
    logger.info("BC Freshwater Atlas is priority data source for BC portion of Cascadia")
    logger.info("Manual download required from:")
    logger.info("https://www.data.gov.bc.ca/dataset/freshwater-atlas-watersheds")
    logger.info("Direct link: https://pub.data.gov.bc.ca/datasets/177864/fwa_watersheds_poly.gdb.zip")
    
    # Attempt to download BC Freshwater Atlas
    bc_atlas_url = "https://pub.data.gov.bc.ca/datasets/177864/fwa_watersheds_poly.gdb.zip"
    bc_atlas_zip = canadian_data_dir / 'bc_freshwater_atlas.gdb.zip'
    
    if download_file(bc_atlas_url, bc_atlas_zip):
        extract_zip(bc_atlas_zip, canadian_data_dir / 'bc_freshwater_atlas')
    
    # Download SDAC boundaries
    logger.info("Downloading Standard Drainage Area Classification (SDAC) boundaries...")
    sdac_url = "https://ftp.maps.canada.ca/pub/nrcan_rncan/vector/standard_drainage_area_classification/standard_drainage_area_classification_shp.zip"
    sdac_zip = canadian_data_dir / 'sdac_boundaries.zip'
    
    if download_file(sdac_url, sdac_zip):
        extract_zip(sdac_zip, canadian_data_dir / 'sdac_boundaries')
    
    logger.info("Canadian data download script completed!")
    logger.info("Note: Some datasets may require manual download due to access restrictions.")

if __name__ == '__main__':
    main()