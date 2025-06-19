#!/usr/bin/env python3
"""
Data download script for Cascadia Watershed Lookup project.
Downloads US Watershed Boundary Dataset and Canadian hydrographic data.
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

# Data URLs
US_WBD_URLS = {
    'washington': 'https://prd-tnm.s3.amazonaws.com/StagedProducts/Hydrography/WBD/HU2/Shape/WBD_17_HU2_Shape.zip',
    'oregon': 'https://prd-tnm.s3.amazonaws.com/StagedProducts/Hydrography/WBD/HU2/Shape/WBD_17_HU2_Shape.zip',
    'california': 'https://prd-tnm.s3.amazonaws.com/StagedProducts/Hydrography/WBD/HU2/Shape/WBD_18_HU2_Shape.zip',
    'idaho': 'https://prd-tnm.s3.amazonaws.com/StagedProducts/Hydrography/WBD/HU2/Shape/WBD_17_HU2_Shape.zip'
}

CASCADIA_BOUNDARY_URL = 'https://huxley.wwu.edu/spatial/cascadia/cascadia_boundary.zip'

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

def main():
    """Main function to download all required datasets."""
    
    # Create data directories
    data_dir = Path(__file__).parent.parent / 'data'
    raw_data_dir = data_dir / 'raw'
    raw_data_dir.mkdir(parents=True, exist_ok=True)
    
    # Download US Watershed Boundary Dataset
    logger.info("Starting US WBD download...")
    us_wbd_dir = raw_data_dir / 'us_wbd'
    us_wbd_dir.mkdir(exist_ok=True)
    
    # Download HUC data for Pacific Northwest (Region 17 covers most of PNW)
    wbd_zip = us_wbd_dir / 'WBD_17_HU2_Shape.zip'
    if download_file(US_WBD_URLS['washington'], wbd_zip):
        extract_zip(wbd_zip, us_wbd_dir)
    
    # Download California data (Region 18 for Northern California)
    wbd_ca_zip = us_wbd_dir / 'WBD_18_HU2_Shape.zip'
    if download_file(US_WBD_URLS['california'], wbd_ca_zip):
        extract_zip(wbd_ca_zip, us_wbd_dir)
    
    # Download Cascadia boundary
    logger.info("Starting Cascadia boundary download...")
    cascadia_dir = raw_data_dir / 'cascadia_boundary'
    cascadia_dir.mkdir(exist_ok=True)
    
    cascadia_zip = cascadia_dir / 'cascadia_boundary.zip'
    if download_file(CASCADIA_BOUNDARY_URL, cascadia_zip):
        extract_zip(cascadia_zip, cascadia_dir)
    
    # Note: Canadian data requires manual download from government sources
    logger.info("Canadian data download requires manual steps:")
    logger.info("1. Visit: https://open.canada.ca/data/en/dataset/a4b190fe-e090-4e6d-881e-b87956c07977")
    logger.info("2. Download Standard Drainage Area Classification (SDAC) data")
    logger.info("3. Place in data/raw/canadian_hydro/ directory")
    
    logger.info("Data download script completed!")

if __name__ == '__main__':
    main()