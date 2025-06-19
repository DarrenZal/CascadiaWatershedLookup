# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

The CascadiaWatershedLookup project implements a cross-border watershed identification service for the Cascadia bioregion. It accepts addresses or postal codes from both the US and Canada and returns detailed hierarchical watershed information suitable for mapping and community organization.

## Architecture

The project follows an **offline-first architecture** using a pre-processed, unified geospatial dataset covering the entire Cascadia bioregion. This approach harmonizes disparate national datasets:

- **US Data**: Watershed Boundary Dataset (WBD) with Hydrologic Unit Code (HUC) system
- **Canadian Data**: Standard Drainage Area Classification (SDAC) and Canadian Hydrospatial Network (CHN)

## Core Technical Approach

### Data Processing Pipeline
1. Define Cascadia operational boundary using WWU's authoritative boundary file
2. Acquire and clip national watershed datasets to Cascadia extent
3. Harmonize different schemas into unified data model
4. Implement high-performance point-in-polygon queries

### Key Implementation Details
- Uses GeoPandas for spatial operations with R-tree spatial indexing
- Geocoding via external APIs (Mapbox, geocode.maps.co, etc.)
- Single unified data file: `cascadia_watersheds.gpkg`
- Hierarchical watershed codes allow parent/child relationship derivation

## Data Schema

The unified dataset contains fields for both US and Canadian watershed systems:
- US: `huc12_code`, `huc10_code`, `huc8_code` (hierarchical)
- Canadian: `sdac_ssda_code`, `sdac_sda_code`, `sdac_mda_code` (alphanumeric)
- Common: `unique_id`, `watershed_name`, `country`, `geometry`, `area_sqkm`

## Core Query Operation

The main function performs a spatial join using `geopandas.sjoin()` with:
- Input: lat/lon point from geocoded address
- Dataset: Pre-loaded unified watershed polygons
- Operation: Point-in-polygon test with spatial index optimization
- Output: Complete watershed record with hierarchical lineage

## Development Notes

- No build system or package management currently configured
- Project is in early development with only research documentation
- Implementation will likely use Python with GeoPandas, Shapely libraries
- Data refresh process needed periodically to update source datasets
- Offline approach chosen for reliability and complete coverage across international borders