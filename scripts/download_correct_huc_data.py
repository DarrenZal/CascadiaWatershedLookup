#!/usr/bin/env python3
"""
Download the correct HUC regions for full Cascadia coverage.
Based on inspection, we need more HUC regions to cover the full area.
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

# Correct HUC regions for Cascadia coverage
# HUC 17 = Pacific Northwest (includes Columbia River basin)
# HUC 18 = California (includes northern California)
# We need both to get full coverage
HUC_REGIONS = {
    'huc_17': 'https://prd-tnm.s3.amazonaws.com/StagedProducts/Hydrography/WBD/HU2/Shape/WBD_17_HU2_Shape.zip',
    'huc_18': 'https://prd-tnm.s3.amazonaws.com/StagedProducts/Hydrography/WBD/HU2/Shape/WBD_18_HU2_Shape.zip'
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

def main():
    """Download all necessary HUC regions for Cascadia."""
    
    # Create fresh data directory
    data_dir = Path(__file__).parent.parent / 'data'
    raw_data_dir = data_dir / 'raw'
    us_wbd_dir = raw_data_dir / 'us_wbd_complete'
    us_wbd_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info("Downloading complete HUC regions for Cascadia coverage...")
    
    # Download both HUC 17 and 18
    for region, url in HUC_REGIONS.items():
        zip_file = us_wbd_dir / f'{region}.zip'
        
        if not zip_file.exists():
            if download_file(url, zip_file):
                extract_zip(zip_file, us_wbd_dir / region)
        else:
            logger.info(f"{region} already exists, skipping download")
            extract_zip(zip_file, us_wbd_dir / region)
    
    logger.info("HUC data download completed!")
    logger.info("Next: Run process_complete_us_data.py to process all regions")

if __name__ == '__main__':
    main()